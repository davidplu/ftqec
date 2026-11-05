import copy,itertools,random,json
from pathlib import Path
import pytest
from ftqec.certification import triples
from ftqec.results.artifacts import digest,source_identity

class Inventory:
    def __init__(self,rows):self.values=rows;self.hash=digest(rows);self.count=len(rows)
    def rows(self):return iter(self.values)

def harmful(rows,weight):
    for group in itertools.combinations(rows,weight):
        if len({r[0] for r in group})!=weight:continue
        d=l=0
        for _,_,dd,ll,_ in group:d^=dd;l^=ll
        if not d and l:return True
    return False

def test_streamed_triples_against_physical_exhaustion():
    checked=0
    for seed in range(500):
        rng=random.Random(seed);rows=[(op,str(j),rng.randrange(1,32),rng.randrange(4),0) for op in range(6) for j in range(2)]
        if harmful(rows,1) or harmful(rows,2):continue
        inv=Inventory(rows);proof=triples.prove(inv,100000);bad=harmful(rows,3)
        assert bool(proof['witness'])==bad and proof['complete']==(not bad)
        if not bad:
            assert triples.verify(inv,proof,4,100000)['verified']
            broken=copy.deepcopy(proof);broken['pairs_processed']+=1
            assert not triples.verify(inv,broken,4,100000)['verified']
        checked+=1
    assert checked==116

def test_streamed_location_domains_and_work_limits():
    rows=[(0,'a',1,0,0),(0,'b',2,0,0),(1,'c',3,1,0)]
    inv=Inventory(rows);proof=triples.prove(inv,1000)
    assert proof['complete'] and triples.verify(inv,proof,4)['verified']
    rows.append((2,'a',1,0,0));proof=triples.prove(Inventory(rows),1000)
    assert proof['witness'] and len({op for op,label in proof['witness']})==3
    short=triples.prove(inv,1)
    assert not short['complete'] and short['lower_bound']==3
    assert not triples.verify(inv,short,4)['verified']
    assert not triples.verify(inv,triples.prove(inv,1000),4,1)['verified']

@pytest.mark.parametrize('basis',['X','Z'])
def test_surface_memory_streamed_certificate(basis):
    from ftqec.architectures.references import rotated_surface
    from ftqec.circuits.repeated import memory
    from ftqec.certification.exact import certify,verify
    _,single=rotated_surface(4,1)
    c=memory(single,4,basis)
    cert=certify(c,4,50000000,method='triples')
    assert cert['status']=='CERTIFIED' and cert['proof']['method']==triples.VERSION
    assert verify(c,cert,50000000)['verified']

def test_worker_process_monitor_launch_race(monkeypatch):
    import psutil
    from ftqec.execution.tasks import Task,guarded
    from ftqec.codes.two_block import parse
    from ftqec.architectures.group_schedule import term_schedule
    from ftqec.circuits.repeated import memory
    data=json.loads(Path('examples/two_block_small.json').read_text());c=memory(term_schedule(parse(data),serial=True),2,'Z')
    task=Task(c.to_dict(),'screen',parse(data).input.identity,{'p':.001},'auto',0,source_identity(),dict(target=2,work=10000,memory_mb=512,cpu_seconds=None,wall_seconds=None))
    original=psutil.Process;calls=[]
    def race(pid=None):
        calls.append(pid)
        if len(calls)==1:raise psutil.NoSuchProcess(pid)
        return original(pid)
    monkeypatch.setattr(psutil,'Process',race)
    result=guarded(task)
    assert len(calls)>=2 and result['result']['status'] in ('NO_WITNESS_FOUND','FAULT_INVALID')

def test_unexpected_controller_error_is_durable(tmp_path,monkeypatch):
    import ftqec.optimization.repeated as engine
    def failed(*args,**kwargs):raise RuntimeError('injected process-monitor failure')
    monkeypatch.setattr(engine,'batch',failed)
    with pytest.raises(RuntimeError,match='process-monitor'):
        engine.optimize(json.loads(Path('examples/two_block_small.json').read_text()),tmp_path/'run',2,2,population=1,generations=1)
    state=json.loads((tmp_path/'run/checkpoint.json').read_text())
    assert state['status']=='INTERRUPTED_ERROR' and state['pending'] and state['generation']==0
