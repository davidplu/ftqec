"""Storage integrity, exact selection and public disk-population integration."""
import json,random,sqlite3
from dataclasses import replace
from pathlib import Path
import pytest
from ftqec.optimization.store import PopulationStore,skyline
from ftqec.optimization.selection import pareto
from ftqec.optimization.engine import Config,optimize
from ftqec.architectures.population import sample,compile
from ftqec.codes.input import load
from ftqec.circuits.identity import physical_identity
from ftqec.evaluation.resources import resources
from ftqec.results.artifacts import digest,source_identity
from ftqec.execution.tasks import Task
from ftqec.delivery.export import export_result,list_results
from ftqec.delivery.verify import verify_bundle


def input_code():return json.loads((Path(__file__).resolve().parents[2]/'examples/surface_small.json').read_text())
def make_row():
    inp=load(input_code());g=sample(inp,23,2);c=compile(inp,g)
    return dict(id=physical_identity(c),circuit=c.to_dict(),genome=g.to_dict(),generation=0,resources=resources(c))


def test_incremental_storage_binding_and_corruption(tmp_path):
    path=tmp_path/'population.sqlite';row=make_row()
    with PopulationStore(path,'epoch') as db:
        db.put(row);assert db.get(row['id'])==row
        row['screen']=dict(status='NO_WITNESS_FOUND');db.put(row)
        assert db.count()==1
        task=Task(row['circuit'],'screen','code',{'p':.001},'auto',1,source_identity(),{})
        db.queue(task,row['id']);assert db.answer(task.identity) is None
    with pytest.raises(ValueError,match='Resume identity'):PopulationStore(path,'different')
    with PopulationStore(path,'epoch') as db:
        assert db.get(row['id'])==row
        answer=dict(task=task.identity,cpu=1.,wall=2.,result={'status':'UNKNOWN'},rss=1)
        db.complete(task.identity,answer);assert db.answer(task.identity)==answer
        assert len(list(db.packets(row['id'])))==1
        db.db.execute("UPDATE candidates SET hash='corrupt'");db.db.commit()
        with pytest.raises(ValueError,match='corruption'):db.get(row['id'])


def test_skyline_matches_exhaustive_and_retains_ties():
    rng=random.Random(301);rows=[]
    for i in range(500):
        q,d,g=[rng.randrange(1,15) for _ in range(3)]
        rows.append(dict(id=str(i),resources=dict(Q=q,D=d,QD=q*d,two_q_gates=g)))
    rows.append(dict(rows[0],id='physical_tie'))
    assert {r['id'] for r in skyline(iter(rows))}=={r['id'] for r in pareto(rows)}


def test_disk_population_resume_and_public_export(tmp_path,monkeypatch):
    from ftqec.optimization import disk_engine
    config=Config(storage='sqlite',population=4,generations=1,window=2,promotion=2,workers=2,target=2,proof_work=20000,initial_shots=8,further_shots=8,seed=24,strategy='hybrid',memory_mb=256)
    original=disk_engine.batch;tripped=[False]
    def interrupted(tasks,*args,**kwargs):
        if tasks[0].tier=='screen' and not tripped[0]:tripped[0]=True;raise MemoryError('test admission interruption')
        return original(tasks,*args,**kwargs)
    monkeypatch.setattr(disk_engine,'batch',interrupted)
    state=optimize(input_code(),tmp_path/'run',config);assert state['status']=='RESOURCE_SAFETY_INTERVENTION'
    monkeypatch.setattr(disk_engine,'batch',original)
    state=optimize(input_code(),tmp_path/'run',config);assert state['status']=='REQUESTED_GENERATIONS_COMPLETED'
    assert state['unique_circuits']>=2 and len(state['sessions'])==2
    with PopulationStore(tmp_path/'run/population.sqlite',readonly=True) as db:
        assert db.db.execute("SELECT count(*) FROM tasks WHERE tier='construct'").fetchone()[0]==4
    checkpoint=json.loads((tmp_path/'run/checkpoint.json').read_text());assert 'rows' not in checkpoint and 'tasks' not in checkpoint
    listed=list_results(tmp_path/'run',True);assert len(listed['results'])==state['unique_circuits']
    for r in listed['results']:
        out=tmp_path/r['circuit_id'];export_result(tmp_path/'run',r['circuit_id'],out)
        result=verify_bundle(out,20000);assert result['resource_recomputation_verified'] and result['reconstruction_verified']
    again=optimize(input_code(),tmp_path/'run',config);assert again['unique_circuits']==state['unique_circuits']


def test_cancel_and_changed_config_rejected(tmp_path):
    run=tmp_path/'run';run.mkdir();(run/'cancel.json').write_text('{}')
    config=Config(storage='sqlite',population=2,generations=1,target=2)
    assert optimize(input_code(),run,config)['status']=='CANCELLED'
    with pytest.raises(ValueError,match='identity'):optimize(input_code(),run,replace(config,seed=1))

def test_fused_cheap_stage_matches_separate_engines():
    from ftqec.execution.tasks import execute
    from ftqec.certification.exact import screen
    inp=load(input_code());g=sample(inp,29,3)
    task=Task(dict(code_input=inp.to_dict(),genome=g.to_dict()),'construct_screen',inp.identity,dict(p=.001),'auto',29,source_identity(),dict(work=20000,target=3))
    r=execute(task)['result'];assert r['status']=='STRUCTURALLY_VALID'
    from ftqec.circuits.model import Circuit
    assert r['screen']==screen(Circuit.from_dict(r['circuit']),20000,target=3)

def test_timed_diversity_ignores_parallel_text_order():
    from ftqec.optimization.diversity import timed_structure
    from ftqec.circuits.model import Circuit
    from ftqec.codes.stabilizer import StabilizerCode
    c=Circuit(StabilizerCode.from_dict(dict(n=2,generators=['ZZ'])),(),())
    c.add('X',[0]);c.add('Z',[1]);other=Circuit.from_dict(c.to_dict());other.operations.reverse()
    assert timed_structure(c)==timed_structure(other)
    other.add('X',[0]);assert timed_structure(c)!=timed_structure(other)


def test_goal_counts_structural_classes_not_hashes(tmp_path):
    row=make_row();row['diversity']=dict(timed_structure='same_physical_structure')
    with PopulationStore(tmp_path/'db','identity') as db:
        db.put(row);other=dict(row,id='distinct_exact_identity');db.put(other)
        assert db.count()==2 and db.meaningful_count()==1

def test_supervised_proposal_preserves_existing_generator():
    from ftqec.architectures.synthesis import generate
    from ftqec.execution.tasks import execute
    inp=load(input_code());g=sample(inp,24,2)
    policy=dict(guided=True,parallel=True,joint=True)
    task=Task(dict(code_input=inp.to_dict(),genome=g.to_dict(),synthesis=policy),'construct',inp.identity,dict(p=.001),'auto',24,source_identity(),dict(work=20000,target=2))
    result=execute(task)['result'];expected,receipt=generate(inp,24,2,**policy)
    assert result['status']=='STRUCTURALLY_VALID' and result['genome']==expected.to_dict()
    assert result['construction']==receipt and 'proposal' in result['phase_costs']
