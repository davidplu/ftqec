import json,itertools
from pathlib import Path
import pytest,stim
from ftqec.codes.input import load
from ftqec.codes.pauli import Pauli
from ftqec.codes.logicals import logical_basis
from ftqec.architectures.population import Genome,sample,compile,FAMILIES
from ftqec.screening.structural import check
from ftqec.faults.signatures import signatures,signatures_forward
from ftqec.faults.verification import replay
from ftqec.certification.exact import certify,verify
from ftqec.simulation.monte_carlo import evaluate,interval
from ftqec.results.artifacts import digest

@pytest.mark.parametrize("name",["perfect5","steane","shor9","surface_small","color_small","noncss_local_clifford"])
@pytest.mark.parametrize("family",FAMILIES)
def test_migrated_engines_against_independent_oracles(name,family):
    inp=load(json.loads(Path("examples",name+".json").read_text()));base=sample(inp,7)
    c=compile(inp,Genome(family,base.orders,base.checks,1,True));check(c)
    a=signatures(c);b=signatures_forward(c)
    assert a==b
    for row in a[::max(1,len(a)//8)]:
        independent=replay(c,[row.fault])
        assert (row.detectors,row.logical,row.data)==(independent["detector_outcomes"],independent["logical_coset"],Pauli.parse(independent["final_data_pauli"]).packed)
    assert evaluate(c,0,16,9)["failures"]==0

def test_positive_and_tamper():
    inp=load(json.loads(Path("examples/surface_small.json").read_text()));c=compile(inp,sample(inp,4));check(c)
    proof=certify(c,2,100000)
    assert proof["status"]=="CERTIFIED" and proof["independent"]["verified"]
    proof["circuit"]="changed";assert not verify(c,proof)["verified"]

def test_signed_code_and_logical_validation():
    inp=load(dict(generators=["-ZZ"],logicals=[["XX","ZI"]]))
    c=compile(inp,sample(inp,0));check(c);assert evaluate(c,0,16,2)["failures"]==0
    with pytest.raises(ValueError):load(dict(generators=["XX","ZZ","YY"]))
    with pytest.raises(ValueError):load(dict(generators=["X","Z"]))
    with pytest.raises(ValueError):load(dict(generators=["ZZ"],logicals=[["XI","ZI"]]))

def test_confidence_not_single_error_rejection():
    lo,hi=interval(1,100);assert lo<.01<hi
    assert interval(0,100)[1]>0

def test_fault_address_rejected():
    inp=load(dict(generators=["ZZ"]));c=compile(inp,sample(inp,0));check(c)
    row=signatures(c)[0];f=row.fault.to_dict();f["location"]="forged"
    with pytest.raises(ValueError):replay(c,[f])


def test_invalid_finalist_witness_independent_replay():
    inp=load(dict(generators=["ZZ"]))
    c=compile(inp,sample(inp,2));check(c)
    proof=certify(c,3,10000)
    assert proof["status"]=="INVALID" and proof["independent"]["verified"]
    proof["target"]=1;assert not verify(c,proof)["verified"]


def test_physical_dedup_ignores_family_labels():
    from ftqec.circuits.identity import physical_identity
    inp=load(dict(generators=["ZZ"]))
    c=compile(inp,sample(inp,2));check(c);identity=physical_identity(c)
    c.experiment["family"]="renamed"
    assert physical_identity(c)==identity
    c.add("X",[0]);assert physical_identity(c)!=identity
