import copy
import pytest
from ftqec.codes.two_block import parse
from ftqec.architectures.group_schedule import term_schedule
from ftqec.circuits.repeated import memory,repeat,validate_memory,stim_model
from ftqec.certification.inventory import backward,forward
from ftqec.certification.exact import certify,verify
from ftqec.faults.signatures import signatures_forward
from ftqec.faults.verification import replay


def small():
    return {'n':6,'generators':['XIXXIX','XXIXXI','ZZIZZI','IZZIZZ'],'metadata':{'multiplication_table':[[(i+j)%3 for j in range(3)] for i in range(3)],'a':[0,1],'b':[0,1],'k':2,'group_order':3,'abelian':True}}


def test_group_input_reconstructs_redundant_checks():
    code=parse(small());assert code.checks.rank==4 and len(code.checks.generators)==6
    broken=small();broken['metadata']['multiplication_table'][0][0]=1
    with pytest.raises(ValueError):parse(broken)
    broken=small();broken['metadata']['a']=[0,0]
    with pytest.raises(ValueError):parse(broken)


@pytest.mark.parametrize('basis',['X','Z'])
@pytest.mark.parametrize('rounds',[1,2,3])
def test_physical_memory_inventory_and_stim_agree(basis,rounds):
    single=term_schedule(parse(small()),serial=True);c=memory(single,rounds,basis)
    validate_memory(c);sc=stim_model(c,0);d,o=sc.compile_detector_sampler(seed=4).sample(20,separate_observables=True)
    assert not d.any() and not o.any()
    a,b=backward(c),forward(c)
    try:
        assert a.hash==b.hash
        rows=list(a.rows());slow=signatures_forward(c)
        indexed={(s.fault.operation,s.fault.label):(s.detectors,s.logical,s.data) for s in slow}
        assert all(indexed[(op,label)]==(ds,ls,data) for op,label,ds,ls,data in rows)
        for sig in slow[::37]:
            actual=replay(c,[sig.fault]);assert actual['detector_outcomes']==sig.detectors and actual['logical_coset']==sig.logical
    finally:a.close();b.close()
    result=certify(c,2,200000)
    assert result['status'] in ('CERTIFIED','INVALID') and verify(c,result,200000)['verified']


def test_memory_tampering_and_explicit_storage():
    c=memory(term_schedule(parse(small()),serial=True),2,'Z',True);validate_memory(c)
    assert any(o.gate=='IDLE' for o in c.operations)
    bad=copy.deepcopy(c);bad.detectors.pop()
    with pytest.raises(ValueError):validate_memory(bad)
    bad=copy.deepcopy(c);bad.observables[0]=[]
    with pytest.raises(ValueError):validate_memory(bad)
    bad=copy.deepcopy(c);bad.operations=[o for o in bad.operations if o.gate!='IDLE']
    with pytest.raises(ValueError):validate_memory(bad)


def test_repeat_actual_operations_and_names():
    c=term_schedule(parse(small()),serial=True);r=repeat(c,3)
    assert sum(o.gate=='CX' for o in r.operations)==3*sum(o.gate=='CX' for o in c.operations)
    assert len({o.record for o in r.operations if o.record})==3*len(c.detectors)

@pytest.mark.parametrize('family',['bare','flagged','cat','verified_cat'])
def test_generic_gadget_memory_and_reuse(family):
    from ftqec.architectures.group_schedule import architecture
    code=parse(small());order=[['X',j] for j in range(len(code.x_terms))]+[['Z',j] for j in range(len(code.z_terms))]
    c=architecture(code,dict(family=family,order=order,ancilla_slots=2,flag_style='adjacent'))
    for basis in ('X','Z'):
        mem=memory(c,2,basis);validate_memory(mem)
        a,b=backward(mem),forward(mem)
        try:assert a.hash==b.hash
        finally:a.close();b.close()


def test_late_single_fault_precedes_pair_witness():
    from ftqec.certification.high_distance import pairs
    class Inventory:
        def rows(self):return iter([(0,'X',1,0,0),(1,'X',1,1,0),(2,'X',0,1,0)])
    assert pairs(Inventory())==(1,[(2,'X')])


def test_memory_pending_construction_recovery(tmp_path,monkeypatch):
    import ftqec.optimization.repeated as engine
    original=engine.batch
    def interrupted(tasks,workers=1,memory_mb=256,on_result=None):
        def first(task,answer):
            on_result(task,answer)
            raise MemoryError('injected interruption after durable task receipt')
        return original(tasks,workers,memory_mb,on_result=first)
    config=dict(rounds=2,target=2,population=2,generations=1,workers=1,work=20000,shots=8,no_time_limits=True)
    monkeypatch.setattr(engine,'batch',interrupted)
    state=engine.optimize(small(),tmp_path/'run',**config)
    assert state['status']=='RESOURCE_SAFETY_INTERVENTION' and state['generation']==0 and state['pending']
    retained=set(state['tasks'])
    monkeypatch.setattr(engine,'batch',original)
    resumed=engine.optimize(small(),tmp_path/'run',**config)
    assert resumed['status']=='REQUESTED_GENERATIONS_COMPLETED' and retained<=set(resumed['tasks'])


def test_memory_population_resume_and_export(tmp_path):
    from ftqec.optimization.repeated import optimize
    from ftqec.delivery.export import export_result
    from ftqec.delivery.verify import verify_bundle
    path=tmp_path/'run'
    config=dict(rounds=2,target=2,population=2,generations=1,workers=2,work=20000,shots=16,no_time_limits=True)
    state=optimize(small(),path,**config)
    assert state['status']=='REQUESTED_GENERATIONS_COMPLETED' and len(state['rows'])>=2
    count=len(state['tasks']);again=optimize(small(),path,**config)
    assert len(again['tasks'])==count
    row=next(r for r in state['rows'] if 'certify' in r)
    out=tmp_path/'bundle';export_result(path,row['id'],out)
    result=verify_bundle(out)
    assert result['reconstruction_verified'] and result['stim_verified']
    assert result['certificate_binding_verified'] and result['proof_replay']['verified']
