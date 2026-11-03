"""Incremental, source-bound population storage with content-checked payloads."""
import json,sqlite3,zlib,time
from pathlib import Path
from ..results.artifacts import digest


def pack(value):return zlib.compress(json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':')).encode(),3)
def unpack(value,expected):
    result=json.loads(zlib.decompress(value))
    if digest(result)!=expected:raise ValueError('Population payload corruption')
    return result


class PopulationStore:
    def __init__(self,path,identity=None,readonly=False):
        self.path=Path(path);self.cost=dict(cpu=0.,wall=0.,writes=0)
        if readonly:
            self.db=sqlite3.connect(self.path.resolve().as_uri()+'?mode=ro',uri=True)
        else:
            self.path.parent.mkdir(parents=True,exist_ok=True);self.db=sqlite3.connect(self.path)
            self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA synchronous=FULL')
            self.db.executescript('''
            CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,payload BLOB NOT NULL,hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS circuits(id TEXT PRIMARY KEY,payload BLOB NOT NULL,hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS candidates(id TEXT PRIMARY KEY,family TEXT NOT NULL,generation INTEGER NOT NULL,
              q INTEGER,d INTEGER,qd INTEGER,gates INTEGER,status TEXT,screen TEXT,near_id TEXT,
              payload BLOB NOT NULL,hash TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS candidate_rank ON candidates(family,qd,id);
            CREATE INDEX IF NOT EXISTS candidate_status ON candidates(status);
            CREATE TABLE IF NOT EXISTS structures(id TEXT PRIMARY KEY,timed_structure TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS timed_structures ON structures(timed_structure);
            CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,candidate TEXT,tier TEXT,status TEXT,
              payload BLOB NOT NULL,hash TEXT NOT NULL,answer BLOB,answer_hash TEXT);
            CREATE INDEX IF NOT EXISTS candidate_tasks ON tasks(candidate);
            CREATE TABLE IF NOT EXISTS execution(id TEXT PRIMARY KEY,cpu REAL,wall REAL,peak INTEGER,dispatch REAL,completed REAL,pid INTEGER);
            CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY,kind TEXT,payload BLOB NOT NULL,hash TEXT NOT NULL);
            ''')
        if identity is not None:
            old=self.get_meta('identity')
            if old is None:self.set_meta('identity',identity)
            elif old!=identity:raise ValueError('Resume identity mismatch')
    def close(self):self.db.close()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def write(self,sql,args):
        t=time.perf_counter();c=time.process_time()
        with self.db:self.db.execute(sql,args)
        self.cost['wall']+=time.perf_counter()-t;self.cost['cpu']+=time.process_time()-c;self.cost['writes']+=1
    def get_meta(self,key,default=None):
        r=self.db.execute('SELECT payload,hash FROM meta WHERE key=?',(key,)).fetchone()
        return unpack(*r) if r else default
    def set_meta(self,key,value):self.write('INSERT OR REPLACE INTO meta VALUES(?,?,?)',(key,pack(value),digest(value)))
    def event(self,kind,value):self.write('INSERT INTO events(kind,payload,hash) VALUES(?,?,?)',(kind,pack(value),digest(value)))
    def put(self,row):
        value=dict(row);circuit=value.pop('circuit');cid=value['id'];metric=value['resources'];family=value['genome']['family']
        old=self.db.execute('SELECT hash FROM circuits WHERE id=?',(cid,)).fetchone()
        ch=digest(circuit)
        if old and old[0]!=ch:raise ValueError('Physical identity already bound to another exact circuit')
        if not old:self.write('INSERT INTO circuits VALUES(?,?,?)',(cid,pack(circuit),ch))
        self.write('INSERT OR REPLACE INTO candidates VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
          (cid,family,value['generation'],metric['Q'],metric['D'],metric['QD'],metric['two_q_gates'],
           value.get('certify',{}).get('status'),value.get('screen',{}).get('status'),value.get('diversity',{}).get('near_id'),pack(value),digest(value)))
        self.write('INSERT OR REPLACE INTO structures VALUES(?,?)',(cid,value.get('diversity',{}).get('timed_structure',cid)))
    def meaningful_count(self):return self.db.execute('SELECT count(DISTINCT timed_structure) FROM structures').fetchone()[0]
    def contains(self,cid):return self.db.execute('SELECT 1 FROM candidates WHERE id=?',(cid,)).fetchone() is not None
    def get(self,cid):
        row=self.db.execute('SELECT payload,hash FROM candidates WHERE id=?',(cid,)).fetchone()
        if row is None:raise KeyError(cid)
        value=unpack(*row);value['circuit']=unpack(*self.db.execute('SELECT payload,hash FROM circuits WHERE id=?',(cid,)).fetchone())
        return value
    def summaries(self,certified=False):
        sql='SELECT id,family,q,d,qd,gates,status,screen,near_id FROM candidates'
        if certified:sql+=" WHERE status='CERTIFIED'"
        for r in self.db.execute(sql+' ORDER BY id'):
            yield dict(id=r[0],genome=dict(family=r[1]),resources=dict(Q=r[2],D=r[3],QD=r[4],two_q_gates=r[5]),certify=dict(status=r[6]),screen=dict(status=r[7]),near_id=r[8])
    def parent_ids(self,limit,seed):
        # Family-balanced resource elites plus deterministic exploration; no reference inputs.
        ids=[]
        for (family,) in self.db.execute('SELECT DISTINCT family FROM candidates ORDER BY family'):
            for (cid,) in self.db.execute("SELECT id FROM candidates WHERE family=? ORDER BY CASE WHEN status='CERTIFIED' THEN 0 ELSE 1 END,qd,id LIMIT ?",(family,max(1,limit//8))):ids.append(cid)
        n=self.count()
        if n:
            offset=seed%n
            ids.extend(r[0] for r in self.db.execute('SELECT id FROM candidates ORDER BY id LIMIT ? OFFSET ?',(limit,offset)))
            if len(ids)<limit:ids.extend(r[0] for r in self.db.execute('SELECT id FROM candidates ORDER BY id LIMIT ?',(limit-len(ids),)))
        return list(dict.fromkeys(ids))[:limit]
    def count(self):return self.db.execute('SELECT count(*) FROM candidates').fetchone()[0]
    def queue(self,task,candidate):
        old=self.db.execute('SELECT payload,hash FROM tasks WHERE id=?',(task.identity,)).fetchone()
        payload=task.to_dict()
        if old:
            from ..execution.tasks import Task
            if Task(**unpack(*old)).identity!=task.identity:raise ValueError('Cached task identity corruption')
            return
        self.write('INSERT INTO tasks VALUES(?,?,?,?,?,?,NULL,NULL)',(task.identity,candidate,task.tier,'QUEUED',pack(payload),digest(payload)))
    def answer(self,tid):
        row=self.db.execute('SELECT answer,answer_hash FROM tasks WHERE id=?',(tid,)).fetchone()
        return unpack(*row) if row and row[0] is not None else None
    def complete(self,tid,answer):
        if answer['task']!=tid:raise ValueError('Task result identity mismatch')
        with self.db:
            self.db.execute("UPDATE tasks SET status='COMPLETE',answer=?,answer_hash=? WHERE id=?",(pack(answer),digest(answer),tid))
            self.db.execute('INSERT OR REPLACE INTO execution VALUES(?,?,?,?,?,?,?)',(tid,answer['cpu'],answer['wall'],answer.get('peak_rss',answer.get('rss',0)),answer.get('dispatch_monotonic'),answer.get('completion_monotonic'),answer.get('pid')))
    def worker_cpu(self):return self.db.execute('SELECT coalesce(sum(cpu),0) FROM execution').fetchone()[0]
    def simulation_summaries(self):
        for blob,sha in self.db.execute("SELECT payload,hash FROM candidates WHERE coalesce(status,'')!='INVALID' AND coalesce(screen,'')!='FAULT_INVALID'"):
            row=unpack(blob,sha)
            if 'rate' in row.get('simulation',{}):yield {k:row[k] for k in ('id','resources','simulation','genome')}

    def packets(self,candidate=None):
        sql='SELECT payload,hash,answer,answer_hash FROM tasks WHERE answer IS NOT NULL';args=()
        if candidate is not None:sql+=' AND candidate=?';args=(candidate,)
        for p,h,a,ah in self.db.execute(sql,args):yield dict(task=unpack(p,h),answer=unpack(a,ah))
    def totals(self):
        tiers={}
        for r in self.db.execute('SELECT tier,answer,answer_hash FROM tasks WHERE answer IS NOT NULL'):
            a=unpack(r[1],r[2]);b=tiers.setdefault(r[0],dict(tasks=0,cpu=0.,summed_wall=0.,shots=0,queue_wall=0.,peak_rss=0,serialization_cpu=0.))
            b['tasks']+=1;b['cpu']+=a['cpu'];b['summed_wall']+=a['wall'];b['shots']+=a['result'].get('shots',0);b['queue_wall']+=a.get('queue_wall',0);b['peak_rss']=max(b['peak_rss'],a.get('peak_rss',a.get('rss',0)));b['serialization_cpu']+=a.get('task_serialization',{}).get('cpu',0)
        return tiers


def skyline(rows):
    """Exact skyline over distinct resource tuples, retaining all physical ties."""
    from .selection import dominates
    keys=('Q','D','QD','two_q_gates');groups={}
    for row in rows:groups.setdefault(tuple(row['resources'][k] for k in keys),[]).append(row)
    front=[]
    for point in groups:
        resource=dict(zip(keys,point))
        if any(dominates(dict(zip(keys,x)),resource,keys) for x in front):continue
        front=[x for x in front if not dominates(resource,dict(zip(keys,x)),keys)];front.append(point)
    return [row for point in front for row in groups[point]]
