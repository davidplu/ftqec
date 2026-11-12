"""Source-bound fixed-pool experiments with actual-compute event ledgers.

Finite experimental budgets stop dispatch, never truncate an active proof.
The ordinary optimizer remains unlimited. Interrupted CPU ledgers are censored,
not silently reset; durable tasks remain reusable within the same policy run.
"""
import argparse,json,time,os
from pathlib import Path
import psutil
from ..results.artifacts import digest,save,source_identity
from ..execution.tasks import Task,batch
from ..execution.runtime import runtime_identity
from ..execution.locking import RunLock
from ..optimization.store import PopulationStore,skyline
from ..optimization.phase3 import proposal
from ..codes.two_block import parse
from ..circuits.model import Circuit
from ..circuits.identity import physical_identity
from .policies import order,aggregate,hypervolume,checkpoint_frontier


def scalar_tiers(db):
    """Read measured scalars, never decompress scientific payloads for progress.

    Fine-grained queue/serialization/shot records remain in immutable task packets
    for separately accounted offline analysis. All of their CPU is already included
    in whole-process worker CPU and controller process_time.
    """
    return {tier:dict(tasks=count,cpu=cpu,summed_wall=wall,peak_rss=peak)
        for tier,count,cpu,wall,peak in db.db.execute('''SELECT t.tier,count(*),sum(e.cpu),sum(e.wall),max(e.peak)
        FROM execution e JOIN tasks t ON e.id=t.id GROUP BY t.tier''')}


class Ledger:
    def __init__(self,root,identity,source,settings,seed,shared_cpu=0.):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
        self.lock=RunLock(self.root/'run.lock');self.lock.__enter__()
        self.db=PopulationStore(self.root/'population.sqlite',identity)
        self.source=source;self.settings=settings;self.seed=seed;self.shared_cpu=shared_cpu;self.identity=identity
        self.started=time.perf_counter();self.proc=psutil.Process();self.peak=self.proc.memory_info().rss
        self.prior=self.db.get_meta('controller',dict(cpu=0.,wall=0.,clean=True,censored=False))
        self.censored=self.prior['censored'] or not self.prior['clean']
        # One ledger per process: process_time includes interpreter startup and imports.
        self.db.set_meta('controller',dict(self.prior,clean=False,censored=self.censored))

    def cpu(self):return self.shared_cpu+self.prior['cpu']+time.process_time()+self.db.worker_cpu()

    def persist(self):
        metadata=self.db.get_meta('state',{})
        metadata.update(source=self.source,config=self.settings)
        self.db.set_meta('state',metadata)
        save(self.root/'checkpoint.json',dict(schema='sqlite-population-1',population_db='population.sqlite',
             source=self.source,identity=self.identity,status=metadata.get('status','RUNNING')))
        self.peak=max(self.peak,self.proc.memory_info().rss)
        state=dict(cpu=self.prior['cpu']+time.process_time(),wall=self.prior['wall']+time.perf_counter()-self.started,
                   clean=False,censored=self.censored,peak_rss=max(self.peak,self.prior.get('peak_rss',0)))
        self.db.set_meta('controller',state)
        save(self.root/'progress.json',dict(pid=os.getpid(),source=self.source,worker_cpu=self.db.worker_cpu(),
             controller=state,shared_cpu=self.shared_cpu,total_cpu=self.cpu(),tiers=scalar_tiers(self.db),state=self.db.get_meta('state')))

    def evaluate(self,key,tier,payload):
        settings=self.settings
        task=Task(payload,tier,settings['code_identity'],dict(p=settings['noise']),'bposd',
                  self.seed+int(digest(key)[:8],16),self.source,
                  dict(target=settings['target'],shots=settings['shots'],work=settings['work'],proof_method='auto',
                       memory_mb=512,cpu_seconds=None,wall_seconds=None,max_decoder_faults=200000,
                       proof_directory=str((self.root/'proofs'/key/tier).resolve()),cancel_file=str((self.root/'cancel.json').resolve())))
        self.db.queue(task,key)
        answer=self.db.answer(task.identity)
        if answer is None:
            if (self.root/'cancel.json').exists():raise InterruptedError('Explicit cancellation')
            answers=batch([task],1,512,on_result=lambda t,a:self.db.complete(t.identity,a))
            answer=answers[0]
        self.persist()
        return answer['result']

    def close(self):
        self.persist()
        state=self.db.get_meta('controller');state.update(cpu=self.prior['cpu']+time.process_time(),clean=True)
        self.db.set_meta('controller',state)
        self.db.close();self.lock.__exit__(None,None,None)


def protocol(path):
    data=json.loads(Path(path).read_text());body={k:v for k,v in data.items() if k!='identity'}
    if digest(body)!=data.get('identity'):raise ValueError('Frozen protocol integrity failure')
    if data['source']!=source_identity():raise ValueError('Frozen scientific source mismatch')
    if 'runtime' in data and data['runtime']!=runtime_identity():raise ValueError('Frozen scientific runtime mismatch')
    return data


def build_pool(spec,root,seed,count):
    if count<1:raise ValueError('Positive proposal count required')
    frozen=Path(root)/'pool.json'
    if frozen.exists():
        old=json.loads(frozen.read_text())
        if old['protocol']!=spec['identity'] or old['seed']!=seed or old['proposals']!=count or digest({k:v for k,v in old.items() if k!='hash'})!=old['hash']:
            raise ValueError('Immutable pool mismatch')
        return old
    code=parse(spec['code']);settings=dict(spec['settings'],code_identity=code.input.identity,decoder='bposd',seed=seed,p=spec['settings']['noise'])
    identity=digest(dict(protocol=spec['identity'],kind='pool',seed=seed,count=count))
    run=Ledger(root,identity,spec['source'],settings,seed)
    db=run.db
    state=db.get_meta('state',dict(index=0,pairs=[],aliases=[],outcomes=[],status='RUNNING'))
    state.update(code=code.input.to_dict())
    db.set_meta('state',state)
    try:
        while state['index']<count:
            index=state['index'];p=proposal(code,index,seed,'structured')
            db.event('proposal',dict(index=index,**p))
            result=run.evaluate(p['key'],'construct_2bga',dict(code_input=spec['code'],rounds=settings['rounds'],genome=p['genome']))
            if result['status']=='STRUCTURALLY_VALID':
                physical=[physical_identity(Circuit.from_dict(c)) for c in result['circuits']]
                pair=digest(physical)
                existing=next((x for x in state['pairs'] if x['id']==pair),None)
                if existing:state['aliases'].append(dict(index=index,pair=pair,genome=p['key']))
                else:
                    rows=[]
                    for c,metric in zip(result['circuits'],result['resources']):
                        cid=digest(c)
                        row=dict(id=cid,circuit=c,resources=metric,genome=p['genome'],generation=index//10,pair=pair)
                        row['screen']=run.evaluate(cid,'screen',c);db.put(row);rows.append(row)
                    state['pairs'].append(dict(id=pair,index=index,resources=aggregate(rows),sectors=[r['id'] for r in rows],
                        eligible=not any(r['screen'].get('status')=='FAULT_INVALID' for r in rows)))
            else:state['outcomes'].append(dict(index=index,proposal=p['key'],result=result))
            state['index']+=1;db.set_meta('state',state);run.persist()
            print(json.dumps(dict(stage='pool',seed=seed,index=state['index'],pairs=len(state['pairs']),cpu=run.cpu())),flush=True)
        state['status']='COMPLETE';db.set_meta('state',state)
    except (MemoryError,InterruptedError) as exc:
        state['status']='BLOCKED';state['reason']=str(exc);db.set_meta('state',state)
        raise
    finally:run.close()
    with PopulationStore(Path(root)/'population.sqlite',readonly=True) as read:
        controller=read.get_meta('controller')
        manifest=dict(identity=identity,protocol=spec['identity'],source=spec['source'],seed=seed,proposals=count,
                      pairs=state['pairs'],aliases=state['aliases'],outcomes=state['outcomes'],
                      shared_cpu=controller['cpu']+read.worker_cpu(),controller=controller,tiers=scalar_tiers(read))
    manifest['hash']=digest(manifest)
    path=Path(root)/'pool.json'
    if path.exists():
        # An already frozen pool cannot be silently replaced by a resumed accounting snapshot.
        old=json.loads(path.read_text())
        if old['pairs']!=manifest['pairs']:raise ValueError('Immutable pool mismatch')
        return old
    save(path,manifest);return manifest


def compare(spec,pool_path,root,policy,seed):
    pool_path=Path(pool_path);pool=json.loads(pool_path.read_text())
    if digest({k:v for k,v in pool.items() if k!='hash'})!=pool['hash']:raise ValueError('Pool integrity failure')
    if pool['protocol']!=spec['identity']:raise ValueError('Pool protocol mismatch')
    code=parse(spec['code']);settings=dict(spec['settings'],code_identity=code.input.identity,decoder='bposd',seed=seed,
                                         generator_seed=pool['seed'],p=spec['settings']['noise'])
    identity=digest(dict(protocol=spec['identity'],pool=pool['hash'],policy=policy,seed=seed))
    run=Ledger(root,identity,spec['source'],settings,seed,pool['shared_cpu']);db=run.db
    state=db.get_meta('state',dict(index=0,positive=[],events=[],status='RUNNING'))
    state.update(code=code.input.to_dict())
    pairs=order([p for p in pool['pairs'] if p['eligible']],policy,seed,n=code.checks.n)
    checkpoints=[pool['shared_cpu']+v for v in spec['promotion_cpu_checkpoints']]
    try:
        with PopulationStore(pool_path.parent/'population.sqlite',readonly=True) as source:
            while state['index']<len(pairs):
                if run.cpu()>=max(checkpoints):state['status']='EXPERIMENT_CHECKPOINT_REACHED';break
                pair=pairs[state['index']];rows=[]
                # Once admitted, finish this paired evaluation; budget overshoot is retained
                # but excluded from earlier checkpoints using actual availability CPU.
                for cid in pair['sectors']:
                    row=db.get(cid) if db.contains(cid) else source.get(cid)
                    row['simulation']=run.evaluate(cid,'simulation',row['circuit'])
                    cert=run.evaluate(cid,'certify',row['circuit']);row['certify']=cert
                    if cert['status'] in ('CERTIFIED','INVALID'):
                        checked=run.evaluate(cid,'verify_exact',dict(circuit=row['circuit'],certificate=cert))
                        row['independent_verification']=checked
                        if checked['status']=='CONTRADICTION':
                            db.put(row);raise RuntimeError('Independent witness contradicts claimed lower bound')
                        row['certify']=checked.get('certificate',cert)
                        if checked['status'] not in ('CERTIFIED','INVALID'):row['certify']=dict(row['certify'],status='UNKNOWN')
                    db.put(row);rows.append(row)
                if all(r.get('independent_verification',{}).get('status')=='CERTIFIED' for r in rows):
                    if pair['id'] not in {p['id'] for p in state['positive']}:state['positive'].append(pair)
                frontier=skyline(state['positive'])
                db.set_meta('state',state);run.persist()
                available=run.cpu()
                state['events'].append(dict(pair=pair['id'],available_cpu=available,frontier=frontier,
                    hypervolume=hypervolume(frontier,spec['hypervolume_reference'])))
                state['index']+=1;db.set_meta('state',state);run.persist()
                print(json.dumps(dict(stage='promotion',policy=policy,index=state['index'],paired=len(state['positive']),cpu=available)),flush=True)
            else:state['status']='EXHAUSTED_POLICY_QUEUE'
    except (MemoryError,InterruptedError) as exc:
        state['status']='BLOCKED';state['reason']=str(exc);raise
    except Exception:
        state['status']='ERROR';raise
    finally:
        db.set_meta('state',state)
        save(Path(root)/'comparison.json',dict(protocol=spec['identity'],pool=pool['hash'],policy=policy,seed=seed,
            state=state,accounting_censored=run.censored or pool['controller']['censored'],
            checkpoints=[dict(cpu=c,coverage='OBSERVED' if run.cpu()>=c or state['status']=='EXHAUSTED_POLICY_QUEUE' else 'NOT_REACHED',frontier=checkpoint_frontier(state['events'],c),
                hypervolume=hypervolume(checkpoint_frontier(state['events'],c),spec['hypervolume_reference'])) for c in checkpoints]))
        run.close()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('pool','compare'));p.add_argument('--protocol',required=True)
    p.add_argument('--output',required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--count',type=int,default=100)
    p.add_argument('--pool');p.add_argument('--policy',choices=('direct','random','resource','legacy','frontier'))
    a=p.parse_args();spec=protocol(a.protocol)
    if a.mode=='pool':build_pool(spec,a.output,a.seed,a.count)
    else:compare(spec,a.pool,a.output,a.policy,a.seed)


if __name__=='__main__':main()
