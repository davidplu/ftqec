import copy,json
from pathlib import Path
import pytest
from ftqec.codes.input import load
from ftqec.architectures.population import compile,sample
from ftqec.architectures.references import rotated_surface
from ftqec.screening.structural import check
from ftqec.certification.inventory import backward,forward,fault_at
from ftqec.certification.high_distance import pairs,independent_pairs,certify,verify,independent_dp
from ftqec.certification.structural import produce,check as check_potentials,dp
from ftqec.faults.signatures import signatures

@pytest.mark.parametrize("name",["perfect5","steane","shor9","surface_small"])
def test_streaming_backward_forward_and_legacy_exact(name):
    inp=load(json.loads(Path("examples",name+".json").read_text()));c=compile(inp,sample(inp,5));check(c)
    a=backward(c);b=forward(c,17)
    try:
        assert a.hash==b.hash
        expected={(s.fault.operation,s.fault.label):(s.detectors,s.logical,s.data) for s in signatures(c)}
        assert {(op,label):(d,l,data) for op,label,d,l,data in a.rows()}==expected
        assert pairs(a)[0]==independent_pairs(b)
    finally:a.close();b.close()

def test_real_surface_positive_five_and_graph_tamper(tmp_path):
    inp,c=rotated_surface(5,5);check(c);proof=certify(c,5,10000000,tmp_path)
    assert proof["status"]=="CERTIFIED" and proof["independent"]["verified"]
    assert proof["proof"]["method"]=="graph_potentials"
    bad=copy.deepcopy(proof);bad["proof"]["channels"][0]["potentials"].pop()
    assert not verify(c,bad,10000000)["verified"]
    bad=copy.deepcopy(proof);bad["exact_distance"]=999
    assert not verify(c,bad,10000000)["verified"]
    bad=copy.deepcopy(proof);bad["target"]=9
    assert not verify(c,bad,10000000)["verified"]
    again=certify(c,5,10000000,tmp_path)
    assert again["status"]=="CERTIFIED"

def test_true_high_target_dispatch_retains_witness():
    inp,c=rotated_surface(3,3)
    for target in (5,7,9):
        proof=certify(c,target,1000000)
        assert proof["status"]=="INVALID" and proof["upper_bound"]<target
        assert proof["independent"]["verified"] and proof["target"]==target

def test_pairs_physical_exclusivity_and_correlated_alternatives():
    from ftqec.certification.inventory import Inventory
    from ftqec.faults.signatures import Fault
    a=Inventory()
    try:
        for label,l in (("IX",0),("XX",1)):a.add(Fault(0,(0,1),label,"cx","op:0"),1,l,0)
        a.finish();assert pairs(a)[0]==3 and independent_pairs(a)==3
    finally:a.close()

def test_graph_eligibility_not_edge_decomposition():
    from ftqec.certification.structural import graph
    class Inv:
        def rows(self):yield 0,"X",7,1,0
    assert graph(Inv(),[1,2,4],0) is None

def test_dp_exhaustive_independent_and_limits():
    inp=load(dict(generators=["ZZ"]));c=compile(inp,sample(inp,0));check(c);inv=backward(c)
    try:
        result=dp(inv,3,100000)
        assert result["complete"] and result["witness"]
        assert not independent_dp(inv,3,100000)
        assert not dp(inv,9,0)["complete"]
    finally:inv.close()

def test_unknown_is_not_requested_target_certificate():
    inp=load(json.loads(Path("examples/perfect5.json").read_text()));c=compile(inp,sample(inp,3));check(c)
    result=certify(c,9,0)
    assert result["status"] in ("UNKNOWN","INVALID")
    if result["status"]=="UNKNOWN":assert result["lower_bound"]<9 and result["unresolved"]


def test_basis_mutations_preserve_signed_group_and_logical_task():
    from ftqec.architectures.population import mutate
    from ftqec.simulation.monte_carlo import evaluate
    inp=load(json.loads(Path("examples/steane.json").read_text()));parent=sample(inp,1)
    children=[mutate(inp,parent,i) for i in range(30)]
    changed=[g for g in children if g.basis]
    assert changed
    c=compile(inp,changed[0]);check(c)
    assert c.experiment["reference_code"]==inp.code.to_dict()
    assert evaluate(c,0,16,3)["failures"]==0


def test_empty_or_missing_extraction_cannot_receive_high_certificate():
    from ftqec.circuits.model import Circuit
    inp=load(dict(generators=["ZZ"]))
    with pytest.raises(ValueError,match="coverage"):certify(Circuit(inp.code,(),()),9,10000)
    inp,c=rotated_surface(3,3);c.detectors=[d for d in c.detectors if d!=["r2_s0"]]
    with pytest.raises(ValueError,match="coverage"):certify(c,9,10000)
