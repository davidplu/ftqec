"""Post-study validation only; does not tune scheduler settings."""
import json,time,subprocess,hashlib
from pathlib import Path
from dataclasses import asdict
from ftqec.execution.tasks import Task,batch
from ftqec.codes.input import load
from ftqec.architectures.population import sample,compile
from ftqec.screening.structural import check
from ftqec.results.artifacts import save,source_identity

def main():
    root=Path("results/compute/portability");root.mkdir(parents=True,exist_ok=False)
    inp=load(json.loads(Path("examples/surface_small.json").read_text()));c=compile(inp,sample(inp,8));check(c)
    tasks=[Task(c.to_dict(),"simulation",inp.identity,dict(p=.001),"one_mechanism_lookup",seed,source_identity(),dict(shots=64,memory_mb=256,cpu_seconds=120,wall_seconds=180)) for seed in (981,982)]
    cpu=time.process_time();wall=time.perf_counter()
    for i in range(1000):Task(**json.loads(json.dumps(tasks[i%2].to_dict())))
    serialization=dict(repetitions=1000,cpu=time.process_time()-cpu,wall=time.perf_counter()-wall)
    local=batch(tasks,2)
    save(root/"task.json",tasks[0].to_dict())
    subprocess.run([str(Path(".venv/Scripts/ftqec.exe").resolve()),"worker",str(root/"task.json"),str(root/"worker.json")],check=True)
    remote_format=json.loads((root/"worker.json").read_text())
    keys=("p","shots","failures","decoder_unknown","seed","decoder","noise","stim_hash")
    equivalent=all(local[0]["result"][k]==remote_format["result"][k] for k in keys)
    overlap=max(0,min(r["completion_monotonic"] for r in local)-max(r["dispatch_monotonic"] for r in local))
    save(root/"result.json",dict(source=source_identity(),local=local,portable_worker=remote_format,equivalent=equivalent,process_overlap_seconds=overlap,serialization=serialization,cloud_status="NOT_RUN: no authorized remote infrastructure supplied",scope="Actual local processes and same serialized worker interface; not remote cloud deployment"))
    assert equivalent and overlap>0
    preserved=json.loads(Path("results/cost_aware/baseline/preservation.json").read_text());mismatches=[];checked=0
    for name,h in preserved["members"].items():
        if name.replace(chr(92),"/").startswith("benchmarks/"):
            checked+=1
            if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=h:mismatches.append(name)
    prior=json.loads(Path("dist/artifact_manifest.json").read_text())
    for row in prior["files"]:
        if row["path"].replace(chr(92),"/").startswith("dist/"):
            checked+=1
            if hashlib.sha256(Path(row["path"]).read_bytes()).hexdigest()!=row["sha256"]:mismatches.append(row["path"])
    old_commit=subprocess.check_output(["git","-c","safe.directory=C:/Users/david/qLDPC synthesizer","-C",r"C:\Users\david\qLDPC synthesizer","rev-parse","HEAD"],text=True).strip()
    save(Path("results/cost_aware/preservation_final.json"),dict(source=source_identity(),checked=checked,mismatches=mismatches,historical_commit_unchanged=old_commit==preserved["historical_repository_commit"],status="PASS" if checked>0 and not mismatches and old_commit==preserved["historical_repository_commit"] else "FAIL"))

if __name__=="__main__":main()
