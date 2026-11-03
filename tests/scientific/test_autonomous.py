import copy
import pytest
from ftqec.architectures.references import rotated_surface
from ftqec.architectures.population import compile, sample, Genome, mutate
from ftqec.architectures.synthesis import generate
from ftqec.codes.input import load
from ftqec.codes.distance import certify_code, verify_code
from ftqec.certification.exact import certify, verify, screen
from ftqec.screening.structural import check


@pytest.mark.parametrize("target",range(1,11))
def test_integer_distance_ladder_code_only(target):
    inp,_=rotated_surface(max(2,target),1)
    g,receipt=generate(inp,0,target)
    assert receipt["method"]=="code_only_greedy_hook_graph"
    c=compile(inp,g);check(c)
    proof=certify(c,target,20000000)
    assert proof["target"]==target and proof["status"]=="CERTIFIED"
    assert verify(c,proof,20000000)["verified"]
    assert proof["proof"]["inventory_count"]>0
    algebraic=certify_code(inp.code,max(2,target))
    assert algebraic["status"]=="CERTIFIED" and verify_code(inp.code,algebraic)["verified"]
    bad=copy.deepcopy(algebraic);bad["channels"][0]["potentials"][0][0]=99
    assert not verify_code(inp.code,bad)["verified"]


def test_target_one_never_single_fault_rejects_and_rounds_unbounded():
    inp=load(dict(generators=["ZZ"]))
    g=Genome("bare",((0,1),),(0,),11)
    c=compile(inp,g);check(c)
    assert screen(c,target=1)["status"]=="NO_WITNESS_FOUND"
    assert certify(c,1)["status"]=="CERTIFIED"
    assert certify(c,2)["status"]=="INVALID"


@pytest.mark.parametrize("family",["flagged","verified_cat"])
def test_expanded_flags_and_cat_semantics(family):
    inp=load(dict(generators=["XXXX","ZZZZ"]))
    g=Genome(family,((0,1,2,3),(3,2,1,0)),(0,1),2,False,False,(),"adjacent",3,"axis_grouped")
    c=compile(inp,g);check(c)
    assert len({mutate(inp,g,i,target=10).verification_rounds for i in range(100)})>1


def test_matching_and_lookup_same_physical_sampling():
    pytest.importorskip("pymatching")
    from ftqec.simulation.monte_carlo import evaluate
    inp,_=rotated_surface(3,1);g,_=generate(inp,0,3);c=compile(inp,g);check(c)
    out=evaluate(c,0,32,7,decoder="matching")
    assert out["decoder"]=="correlated_matching" and out["failures"]==0
    out=evaluate(c,.005,128,11,decoder="matching")
    assert out["shots"]==128 and out["decoder_unknown"]==0


def test_general_stabilizer_generation_unchanged():
    inp=load(dict(generators=["XZZXI","IXZZX","XIXZZ","ZXIXZ"]))
    for seed in range(4):
        c=compile(inp,sample(inp,seed,target=10));check(c)


def test_ler_frontiers_never_compare_different_decoders():
    from ftqec.optimization.selection import reliability_pareto
    a=dict(id="a",resources=dict(Q=2,D=2,QD=4,two_q_gates=2),simulation=dict(rate=.1,decoder="lookup",p=.01))
    b=dict(id="b",resources=dict(Q=3,D=3,QD=9,two_q_gates=3),simulation=dict(rate=.2,decoder="matching",p=.01))
    assert len(reliability_pareto([a,b]))==2


def test_partial_graph_proof_continues_without_repeating_roots(tmp_path):
    from ftqec.certification.structural import produce,check as verify_potentials
    graph=dict(vertices=4,edges=[(0,1,0,0,"X"),(1,2,0,1,"X"),(2,3,0,2,"X"),(0,3,1,3,"X")])
    first=produce(graph,4,checkpoint=tmp_path,work_limit=20)
    assert not first["complete"] and first["completed_roots"]>0
    for _ in range(4):
        result=produce(graph,4,checkpoint=tmp_path,work_limit=20)
        if result["complete"]:break
    assert result["complete"] and verify_potentials(graph,result,4)


def test_pending_population_resumes_after_admission_pause(tmp_path,monkeypatch):
    import ftqec.optimization.engine as engine
    data=dict(generators=["ZZ"])
    config=engine.Config(population=1,generations=1,target=1,workers=1,memory_mb=256,initial_shots=8,further_shots=8,decoder="one_mechanism_lookup")
    actual=engine.batch
    def pause(*args,**kwargs):raise MemoryError("controlled admission pause")
    monkeypatch.setattr(engine,"batch",pause)
    before=engine.optimize(data,tmp_path,config)
    assert before["status"]=="RESOURCE_SAFETY_INTERVENTION" and before["pending_generation"]["ids"]
    monkeypatch.setattr(engine,"batch",actual)
    after=engine.optimize(data,tmp_path,config)
    assert after["generation"]==1 and len(after["generation_compute"])==1
    assert after["rows"][0]["certify"]["status"]=="CERTIFIED"


def test_atomic_save_retries_transient_windows_sharing_failure(tmp_path,monkeypatch):
    import ftqec.results.artifacts as artifacts
    import json
    actual=artifacts.os.replace;calls=[]
    def replace(a,b):
        calls.append(1)
        if len(calls)<3:raise PermissionError("controlled sharing violation")
        return actual(a,b)
    monkeypatch.setattr(artifacts.os,"replace",replace)
    artifacts.save(tmp_path/"checkpoint.json",dict(value=7))
    assert len(calls)==3 and json.loads((tmp_path/"checkpoint.json").read_text())==dict(value=7)


@pytest.mark.parametrize("family",["bare","flagged","cat","verified_cat"])
def test_batched_signed_flows_agree_with_original_checker(family):
    from ftqec.screening.structural import legacy_check
    inp=load(dict(generators=["XXXX","ZZZZ"]))
    g=Genome(family,((0,1,2,3),(3,2,1,0)),(0,1),2,False,False,(),"nested",2)
    c=compile(inp,g);old=copy.deepcopy(c);new=copy.deepcopy(c)
    assert legacy_check(old)==check(new) and old.to_dict()==new.to_dict()
    # A wrong signed measurement is rejected by both checkers.
    first=next(i for i,o in enumerate(c.operations) if o.record and "_s" in o.record)
    from dataclasses import replace
    c.operations[first]=replace(c.operations[first],qubits=(c.syndrome_qubits[-1],))
    old=copy.deepcopy(c);new=copy.deepcopy(c)
    def accepts(fn,c):
        try:fn(c);return True
        except ValueError:return False
    assert accepts(legacy_check,old)==accepts(check,new)


def test_runtime_change_invalidates_cached_task():
    from ftqec.execution.tasks import Task
    from dataclasses import replace
    t=Task({},"screen","code",{},"lookup",1,"source",{})
    changed=replace(t,runtime=dict(t.runtime,python=[0,0,0]))
    assert t.identity!=changed.identity
