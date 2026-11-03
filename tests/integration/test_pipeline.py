import json
from pathlib import Path
from ftqec.optimization.engine import Config,optimize
from ftqec.execution.tasks import Task,batch
from ftqec.results.artifacts import source_identity,digest
from ftqec.codes.input import load
from ftqec.architectures.population import sample,compile
from ftqec.screening.structural import check

def test_checkpoint_cache_resume(tmp_path):
    data=json.loads(Path("examples/surface_small.json").read_text());config=Config(population=4,generations=1,initial_shots=16,further_shots=32,target=2,finalists=1)
    a=optimize(data,tmp_path,config);b=optimize(data,tmp_path,config)
    assert a["tasks"]==b["tasks"] and a["seen"]==b["seen"]
    assert len(b["seen"])==len(set(b["seen"]))
    assert json.loads((tmp_path/"archives.json").read_text())["certified"]

def test_multicore_serialization_and_limits():
    inp=load(dict(generators=["ZZ"]));c=compile(inp,sample(inp,0));check(c)
    tasks=[Task(c.to_dict(),"simulation",inp.identity,{"p":0},"one_mechanism_lookup",seed,source_identity(),{"shots":16,"memory_mb":256}) for seed in (2,3)]
    assert Task(**json.loads(json.dumps(tasks[0].to_dict()))).identity==tasks[0].identity
    answers=batch(tasks,2);assert len({a["pid"] for a in answers})==2
    assert all(a["result"]["failures"]==0 for a in answers)
    assert all(a["pid"]==a["supervised_pid"] for a in answers)
    assert all(a["peak_rss"]>=a["rss"] for a in answers)
    assert all(a["cpu"]+.001>=a["body_cpu"] for a in answers)
    assert min(a["completion_monotonic"] for a in answers)>max(a["dispatch_monotonic"] for a in answers)
    tiny=Task(c.to_dict(),"simulation",inp.identity,{"p":0},"one_mechanism_lookup",0,source_identity(),{"shots":1000000,"memory_mb":1})
    assert batch([tiny])[0]["result"]["reason"]=="MEMORY_LIMIT"


def test_finished_resume_rejects_corrupt_cache(tmp_path):
    import pytest
    data=json.loads(Path("examples/surface_small.json").read_text())
    config=Config(population=2,generations=1,initial_shots=8,further_shots=8,target=2,finalists=1)
    state=optimize(data,tmp_path,config)
    tid=next(iter(state["tasks"]));path=tmp_path/"tasks"/(tid+".json")
    value=json.loads(path.read_text());value["answer"]["cpu"]+=1;path.write_text(json.dumps(value))
    with pytest.raises(ValueError,match="corruption"):optimize(data,tmp_path,config)
