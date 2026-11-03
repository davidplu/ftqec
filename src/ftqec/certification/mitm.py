"""Exact location-exclusive signature MITM, with disk partitions and independent joins.

A minimum harmful set has no zero effect and no repeated (detector, logical)
effect: removing either preserves harmful parity and decreases its weight.
Equal effects are grouped, but their physical locations are NOT identified.
A bipartite matching must assign every selected effect a distinct location.
"""
import hashlib
import json
import math
import sqlite3
import struct
import tempfile
from itertools import combinations
from pathlib import Path
from ..results.artifacts import digest, source_identity

VERSION = 'location-exclusive-effect-mitm-1'


class WorkLimit(Exception):
    pass


class Budget:
    def __init__(self, limit):
        self.limit = limit
        self.used = 0

    def tick(self, n=1):
        self.used += n
        if self.used > self.limit:
            raise WorkLimit('exact_mitm_work_limit')


def universe(inv):
    grouped = {}
    for op, label, det, logical, _ in inv.rows():
        if not (det or logical):
            continue
        locations = grouped.setdefault((det, logical), {})
        locations[op] = min(label, locations.get(op, label))
    return [(d, l, tuple(sorted(choices.items())))
            for (d, l), choices in sorted(grouped.items())]


def assignment(ids, groups, budget):
    """Find a system of distinct location representatives, not a relaxation."""
    owners = {}
    def augment(effect, visited):
        for location, label in groups[effect][2]:
            budget.tick()
            if location in visited:
                continue
            visited.add(location)
            old = owners.get(location)
            if old is None or augment(old, visited):
                owners[location] = effect
                return True
        return False
    for effect in ids:
        if not augment(effect, set()):
            return None
    by_effect = {effect: location for location, effect in owners.items()}
    return [(by_effect[e], dict(groups[e][2])[by_effect[e]]) for e in ids]


def _recursive_tuples(n, size, prefix=(), start=0):
    # Verifier enumeration is recursive, separate from producer combinations.
    if not size:
        yield prefix
    else:
        for i in range(start, n-size+1):
            yield from _recursive_tuples(n, size-1, prefix+(i,), i+1)


def _pack(ids):
    return struct.pack('>'+'I'*len(ids), *ids)


def _unpack(blob):
    return struct.unpack('>'+'I'*(len(blob)//4), blob)


def _effect(ids, groups):
    d = l = 0
    for i in ids:
        d ^= groups[i][0]
        l ^= groups[i][1]
    return d, l


def _open(path, context):
    db = sqlite3.connect(str(path))
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA synchronous=NORMAL')
    db.execute('PRAGMA cache_size=-8192')
    db.execute('PRAGMA temp_store=FILE')
    db.execute('CREATE TABLE IF NOT EXISTS meta(context TEXT NOT NULL)')
    existing = db.execute('SELECT context FROM meta').fetchall()
    if existing and existing != [(context,)]:
        db.close()
        raise ValueError('MITM checkpoint identity mismatch')
    if not existing:
        db.execute('INSERT INTO meta VALUES(?)', (context,))
    db.execute('CREATE TABLE IF NOT EXISTS halves(k INTEGER,lead INTEGER,tail INTEGER,d TEXT,l TEXT,ids BLOB,PRIMARY KEY(k,ids))')
    db.execute('CREATE INDEX IF NOT EXISTS effects ON halves(k,d,l)')
    db.execute('CREATE TABLE IF NOT EXISTS partitions(k INTEGER,lead INTEGER,n INTEGER,sha TEXT,PRIMARY KEY(k,lead))')
    db.execute("INSERT OR IGNORE INTO halves VALUES(0,-1,-1,'0x0','0x0',?)", (b'',))
    db.commit()
    return db


def _build(db, groups, size, budget, independent=False):
    n = len(groups)
    for lead in range(n-size+1):
        old = db.execute('SELECT n,sha FROM partitions WHERE k=? AND lead=?', (size,lead)).fetchone()
        if old:
            if old[0] != math.comb(n-lead-1,size-1):
                raise ValueError('Invalid partition coverage')
            continue
        sha = hashlib.sha256()
        count = 0
        tails = (_recursive_tuples(n,size-1,start=lead+1) if independent
                 else combinations(range(lead+1,n),size-1))
        try:
            for tail in tails:
                budget.tick()
                ids = (lead,)+tuple(tail)
                d,l = _effect(ids,groups)
                packed = _pack(ids)
                db.execute('INSERT INTO halves VALUES(?,?,?,?,?,?)',
                           (size,lead,ids[-1],hex(d),hex(l),packed))
                sha.update(json.dumps([list(ids),hex(d),hex(l)],separators=(',',':')).encode()+b'\n')
                count += 1
            assert count == math.comb(n-lead-1,size-1)
            db.execute('INSERT INTO partitions VALUES(?,?,?,?)',(size,lead,count,sha.hexdigest()))
            db.commit()
        except BaseException:
            db.rollback()
            raise
    actual = db.execute('SELECT COUNT(*) FROM halves WHERE k=?',(size,)).fetchone()[0]
    if actual != math.comb(n,size):
        raise ValueError('Incomplete or duplicate half-set coverage')


def _producer_join(db, groups, weight, budget):
    db.execute('CREATE INDEX IF NOT EXISTS lead_range ON halves(k,d,lead,l,ids)')
    left = weight//2
    right = weight-left
    examined = 0
    for d,l,ids,tail in db.execute('SELECT d,l,ids,tail FROM halves WHERE k=? ORDER BY ids',(left,)):
        budget.tick()
        for blob, in db.execute('SELECT ids FROM halves INDEXED BY lead_range WHERE k=? AND d=? AND l!=? AND lead>? ORDER BY ids',(right,d,l,tail)):
            budget.tick()
            examined += 1
            ids_all = _unpack(ids)+_unpack(blob)
            match = assignment(ids_all,groups,budget)
            if match is not None:
                return match, examined
    return None, examined


def _checker_join(db, groups, weight, budget):
    db.execute('CREATE INDEX IF NOT EXISTS tail_range ON halves(k,d,tail,l,ids)')
    # Reverse traversal of the right index, with the left boundary predicate.
    right = (weight+1)//2
    left = weight-right
    examined = 0
    for d,l,blob,lead in db.execute('SELECT d,l,ids,lead FROM halves WHERE k=? ORDER BY ids DESC',(right,)):
        budget.tick()
        for other, in db.execute('SELECT ids FROM halves INDEXED BY tail_range WHERE k=? AND d=? AND l!=? AND tail<? ORDER BY ids DESC',(left,d,l,lead)):
            budget.tick()
            examined += 1
            ids = _unpack(other)+_unpack(blob)
            # Independent location matching by recursive search with Hall pruning.
            supports = [tuple(op for op,label in groups[e][2]) for e in ids]
            supports.sort(key=len)
            def place(i, used):
                if i == len(supports):
                    return True
                if len(set().union(*(set(s) for s in supports[i:]))-used) < len(supports)-i:
                    return False
                for op in supports[i]:
                    budget.tick()
                    if op not in used and place(i+1,used|{op}):
                        return True
                return False
            if place(0,set()):
                return False, examined
    return True, examined


def prove(inv, target, work_limit=200000, directory=None, start_weight=1):
    if type(target) is not int or target<1 or not 1<=start_weight<=target:
        raise ValueError('Invalid exclusion range')
    groups = universe(inv)
    context = digest(dict(version=VERSION,source=source_identity(),inventory=inv.hash,
                          groups=digest(groups),target=target,start=start_weight))
    temporary = tempfile.TemporaryDirectory(prefix='ftqec-mitm-') if directory is None else None
    root = Path(temporary.name) if temporary else Path(directory)/context
    root.mkdir(parents=True,exist_ok=True)
    db = _open(root/'halves.sqlite',context)
    budget = Budget(work_limit)
    lower = start_weight
    counts = {}
    witness = None
    reason = None
    try:
        for weight in range(start_weight,target):
            for size in sorted({weight//2,(weight+1)//2}-{0}):
                _build(db,groups,size,budget)
            witness,examined = _producer_join(db,groups,weight,budget)
            counts[str(weight)] = examined
            if witness is not None:
                break
            lower = weight+1
    except WorkLimit as exc:
        reason = str(exc)
    partitions = [dict(size=k,first=lead,count=n,sha256=sha)
                  for k,lead,n,sha in db.execute('SELECT * FROM partitions ORDER BY k,lead')]
    db.close()
    if temporary:
        temporary.cleanup()
    return dict(method=VERSION,complete=lower>=target,witness=witness,lower_bound=lower,
                start_weight=start_weight,target=target,groups_hash=digest(groups),
                effects=len(groups),inventory_hash=inv.hash,inventory_count=inv.count,
                partitions=partitions,join_counts=counts,work=budget.used,reason=reason)


def verify(inv, proof, bound, work_limit=200000):
    """Reconstruct from independent forward effects; no producer DB is trusted."""
    if proof.get('method')!=VERSION or proof.get('target',0)<bound:
        return dict(verified=False,reason='MITM method/target identity')
    start = proof.get('start_weight')
    if type(start) is not int or not 1<=start<=bound:
        return dict(verified=False,reason='MITM exclusion range')
    groups = universe(inv)
    if proof.get('groups_hash')!=digest(groups) or proof.get('inventory_hash')!=inv.hash or proof.get('inventory_count')!=inv.count:
        return dict(verified=False,reason='MITM forward inventory identity')
    budget = Budget(work_limit)
    with tempfile.TemporaryDirectory(prefix='ftqec-mitm-check-') as directory:
        db = _open(Path(directory)/'verify.sqlite','independent')
        try:
            for weight in range(start,bound):
                for size in sorted({weight//2,(weight+1)//2}-{0}):
                    _build(db,groups,size,budget,independent=True)
                valid,count = _checker_join(db,groups,weight,budget)
                if not valid or proof.get('join_counts',{}).get(str(weight))!=count:
                    return dict(verified=False,reason='MITM harmful set or join coverage',work=budget.used)
            expected = [dict(size=k,first=lead,count=n,sha256=sha)
                        for k,lead,n,sha in db.execute('SELECT * FROM partitions ORDER BY k,lead')]
            supplied = {(p['size'],p['first']):p for p in proof.get('partitions',[])}
            if len(supplied)!=len(proof.get('partitions',[])) or any(supplied.get((p['size'],p['first']))!=p for p in expected):
                return dict(verified=False,reason='MITM partition coverage')
            return dict(verified=True,lower_bound=bound,method='forward inventory, recursive halves, reverse joins and independent location assignment',work=budget.used)
        except WorkLimit:
            return dict(verified=False,reason='independent_mitm_work_limit',work=budget.used)
        finally:
            db.close()
