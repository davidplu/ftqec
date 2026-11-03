import json
from pathlib import Path
from dataclasses import replace
import pytest
from ftqec.codes.input import load
from ftqec.architectures.population import sample,compile,Genome
from ftqec.scheduling.dependencies import dependencies,reorder,commute
from ftqec.scheduling.scheduler import schedule
from ftqec.screening.structural import check
from ftqec.circuits.model import Operation


def test_commutation_rules_and_causal_dependencies():
    cx=Operation('CX',(0,1));cz=Operation('CZ',(1,2))
    assert not commute(cx,cz)
    assert commute(cx,Operation('CZ',(0,2)))
    assert not commute(cx,Operation('RESET',(0,)))
    inp=load(json.loads(Path('examples/steane.json').read_text()))
    c=compile(inp,replace(sample(inp,3),family='bare',shared=False,rounds=1))
    deps=dependencies(c)
    assert all(set(op.deps)<=deps[i] for i,op in enumerate(c.operations))
    for method in ('list','critical_path','conflict_color','resource'):
        out=reorder(c,method);check(out);s=schedule(out)
        busy=set()
        for op,t in zip(out.operations,s.starts):
            for q in op.qubits:
                assert (q,t) not in busy
                busy.add((q,t))
        assert sorted((o.gate,o.qubits,o.record) for o in out.operations)==sorted((o.gate,o.qubits,o.record) for o in c.operations)


def test_intermediate_ancilla_allocation_and_old_genomes():
    inp=load(json.loads(Path('examples/steane.json').read_text()))
    parent=replace(sample(inp,8),family='bare',rounds=2)
    old=parent.to_dict();old.pop('ancilla_slots')
    assert Genome.from_dict(old).ancilla_slots is None
    for slots in (1,2,3,6):
        c=compile(inp,replace(parent,ancilla_slots=slots,schedule='critical_path'))
        check(c)
        assert len(c.syndrome_qubits)==slots
    with pytest.raises(ValueError,match='allocation'):compile(inp,replace(parent,ancilla_slots=0))


def test_small_exact_schedule_and_colored_code_only():
    from ftqec.scheduling.dependencies import exact_small
    from ftqec.architectures.synthesis import generate
    from ftqec.architectures.references import rotated_surface
    inp=load(dict(generators=['ZZ']))
    c=compile(inp,Genome('bare',((0,1),),(0,)))
    out,receipt=exact_small(c)
    assert receipt['status']=='OPTIMAL_FOR_DECLARED_DAG'
    check(out)
    assert schedule(out).depth==6
    assert exact_small(c,node_limit=0)[1]['status']=='UNKNOWN'
    inp,_=rotated_surface(3,1)
    g,receipt=generate(inp,0,3,parallel=True)
    assert receipt['method']=='code_only_hook_guided_constraint_coloring'
    out=compile(inp,g);check(out)
    from ftqec.certification.exact import certify,verify
    proof=certify(out,3)
    assert proof['status']=='CERTIFIED' and verify(out,proof)['verified']


def test_witness_repair_uses_physical_hook_metadata():
    from ftqec.architectures.population import mutate
    inp=load(dict(generators=['XXXX','ZZZZ']))
    parent=Genome('bare',((0,1,2,3),(0,1,2,3)),(0,1))
    witness=dict(faults=[dict(role='data_interaction',qubits=[4,1],label='XI',check=0)])
    a=mutate(inp,parent,0,witness,target=4)
    b=mutate(inp,parent,1,witness,target=4)
    assert a.flag_style=='adjacent' and b.flag_style=='nested'
    assert a.schedule==b.schedule=='critical_path'
    check(compile(inp,a));check(compile(inp,b))


def test_construction_admission_resume_preserves_exact_candidate(tmp_path,monkeypatch):
    import ftqec.execution.tasks as tasks
    from ftqec.optimization.engine import Config,optimize
    data=dict(generators=['ZZ']);cfg=Config(population=2,generations=1,target=1,initial_shots=8,further_shots=8,finalists=2,decoder='one_mechanism_lookup')
    actual=tasks.batch
    def pause(*args,**kwargs):raise MemoryError('construction admission pause')
    monkeypatch.setattr(tasks,'batch',pause)
    before=optimize(data,tmp_path,cfg)
    assert before['status']=='RESOURCE_SAFETY_INTERVENTION'
    frozen=before['construction_pending']['genome']
    assert before['construction_pending']['index']==0
    monkeypatch.setattr(tasks,'batch',actual)
    after=optimize(data,tmp_path,cfg)
    assert after['generation']==1 and after['rows'][0]['genome']==frozen
    assert 'construction_pending' not in after
    assert after['rows'][0]['certify']['status']=='CERTIFIED'


def test_construction_memory_limit_is_unknown_not_invalid(tmp_path):
    from ftqec.optimization.engine import Config,optimize
    state=optimize(dict(generators=['ZZ']),tmp_path,Config(population=1,generations=1,target=1,memory_mb=1,initial_shots=8,further_shots=8))
    assert state['construction_unknown']
    assert state['construction_unknown'][0]['reason']=='MEMORY_LIMIT'
    assert not state['rows'] and not state.get('structural_rejections')
