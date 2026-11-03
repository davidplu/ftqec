import pytest
import json,random
from pathlib import Path
from ftqec.optimization.costs import CostModel
from ftqec.optimization.adaptive import choose
from ftqec.simulation.sequential import confidence
from ftqec.optimization.engine import Config,optimize
from ftqec.execution.tasks import Task

def test_censoring_not_zero_or_completion_label():
    m=CostModel([dict(tier="certify",target=3,operations=100,cpu=4.,censored=True,status="UNKNOWN")])
    e=m.estimate("certify",100,3)
    assert e.cpu>=4 and e.samples==0 and e.censored==1
    assert m.learned_prediction("certify",100,3) is None

def test_direct_shortcut_and_no_single_failure_rejection():
    row=dict(id="x",circuit=dict(operations=[{}]*100))
    assert choose(row,2,CostModel(),1)["reason"]=="direct_certification_cheaper_than_funnel"
    row["simulation"]=dict(failures=1,shots=10,confidence=[0,1])
    assert choose(row,3,CostModel(),1)["action"]!="reject_with_proof"

def test_sequential_empirical_any_look_coverage():
    rng=random.Random(841);misses=0
    for repeat in range(1000):
        failures=0;miss=False
        for look in range(1,6):
            failures+=sum(rng.random()<.2 for _ in range(40));lo,hi=confidence(failures,look*40,look)
            miss|=not lo<=.2<=hi
        misses+=miss
    assert misses<=50

@pytest.mark.parametrize("strategy",["costaware","costhybrid"])
def test_costaware_optimizer_bypasses_simulation_and_resumes(tmp_path,strategy):
    data=json.loads(Path("examples/surface_small.json").read_text());cfg=Config(population=3,generations=1,strategy=strategy,target=2)
    a=optimize(data,tmp_path,cfg);b=optimize(data,tmp_path,cfg)
    assert a["tasks"]==b["tasks"]
    assert any(d["reason"]=="direct_certification_cheaper_than_funnel" for d in a["action_decisions"])
    assert all("simulation" not in row for row in a["rows"])
    assert any(row.get("certify",{}).get("status")=="CERTIFIED" for row in a["rows"])

def test_task_identity_excludes_only_operational_cancel_path():
    args=dict(circuit={},tier="screen",code_identity="code",noise={},decoder="d",seed=1,source="s")
    assert Task(**args,limits=dict(work=10,cancel_file="a")).identity==Task(**args,limits=dict(work=10,cancel_file="b")).identity
    assert Task(**args,limits=dict(work=11)).identity!=Task(**args,limits=dict(work=10)).identity


def test_source_keys_are_platform_canonical(tmp_path):
    from ftqec.results.artifacts import source_records
    (tmp_path/"sub").mkdir();(tmp_path/"sub/module.py").write_bytes(b"value=1\n")
    assert list(source_records(tmp_path))==["sub/module.py"]

def test_unsupported_is_not_censored_completion_cost(tmp_path):
    data=json.loads(Path("examples/surface_small.json").read_text())
    state=optimize(data,tmp_path,Config(population=1,generations=1,strategy="costaware",target=5))
    observations=state["cost_observations"]
    assert observations and observations[0]["supported"]
    assert all(o.get("reason")!="UNSUPPORTED_PROOF_METHOD" for o in observations)
    assert any(row["certify"]["status"] in ("INVALID","UNKNOWN","CERTIFIED") for row in state["rows"])
