"""Frozen code-only discovery campaign. All reference schedules stay outside optimize."""
import os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):os.environ[key]="1"
import json,time,subprocess,hashlib,zipfile
from pathlib import Path
import psutil
from ftqec.results.artifacts import save,source_identity,digest,source_records
from ftqec.codes.input import load
from ftqec.codes.distance import certify_code
from ftqec.architectures.references import rotated_surface
from ftqec.optimization.engine import optimize,Config
from ftqec.optimization.selection import pareto

ROOT=Path("results/autonomous/campaign")


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    source=source_identity();protocol=ROOT/"protocol.json"
    if protocol.exists():
        frozen=json.loads(protocol.read_text());assert frozen["source"]==source
    else:
        frozen=dict(source=source,commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
                    driver_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    protocol_sha=hashlib.sha256(Path("docs/SCIENTIFIC_PROTOCOL.md").read_bytes()).hexdigest(),
                    seed=20261028,targets=list(range(1,11)),population=8,convergence_generations=3,
                    reference_seeding=False,global_time_cap=None,host=dict(cpu_count=os.cpu_count(),
                    memory_total=psutil.virtual_memory().total,memory_available=psutil.virtual_memory().available),
                    preparation="Benchmark exports stabilizers only; optimizer never receives reference circuits")
        save(protocol,frozen)
        with zipfile.ZipFile(ROOT/"scientific_source.zip","w",zipfile.ZIP_DEFLATED) as z:
            for name in source_records(Path("src/ftqec")):z.write(Path("src/ftqec")/name,"ftqec/"+name)
    ladder=[]
    for target in range(1,11):
        assert source_identity()==source
        name=f"surface_target{target}";dest=Path("results/discovery/autonomous")/name
        codepath=ROOT/"codes"/(name+".json")
        if not codepath.exists():
            inp,_=rotated_surface(max(2,target),1)
            save(codepath,inp.to_dict())
            algebraic=certify_code(inp.code,max(2,target))
            save(ROOT/"algebraic"/(name+".json"),algebraic)
        data=json.loads(codepath.read_text())
        cfg=Config(population=8,workers=2,seed=20261028,target=target,strategy="hybrid",
                   initial_shots=64,further_shots=256,finalists=3,proof_work=20000000,
                   decoder="auto",convergence_generations=3)
        statepath=dest/"checkpoint.json"
        if statepath.exists() and json.loads(statepath.read_text()).get("status")=="OPERATIONAL_FRONTIER_PLATEAU":
            state=json.loads(statepath.read_text())
        else:state=optimize(data,dest,cfg)
        rows=state["rows"];positive=[r for r in rows if r.get("certify",{}).get("status")=="CERTIFIED"]
        frontier=pareto(positive)
        entry=dict(target=target,name=name,experiment_class="AUTONOMOUS_DISCOVERY",source=source,
                   code=state["code"],generated=sum(g["generated"] for g in state["generation_compute"]),
                   compiled=sum(g["compiled"] for g in state["generation_compute"]),distinct=len(rows),
                   simulated=sum("shots" in r.get("simulation",{}) for r in rows),
                   certified=len(positive),fault_rejected=sum(r.get("screen",{}).get("status")=="FAULT_INVALID" or r.get("certify",{}).get("status")=="INVALID" for r in rows),
                   unknown=sum(r.get("certify",{}).get("status")=="UNKNOWN" for r in rows),
                   stop_reason=state["status"],frontier=[dict(id=r["id"],resources=r["resources"],family=r["genome"]["family"],construction=r["construction"]) for r in frontier],
                   compute=json.loads((dest/"compute.json").read_text()),frontier_history=state.get("frontier_history",[]))
        ladder.append(entry);save(Path("benchmarks/distance_ladder/autonomous")/(name+".json"),entry)
        save(Path("benchmarks/distance_ladder/autonomous/summary.json"),dict(source=source,rows=ladder))
        for r in frontier:
            save(Path("results/certificates/autonomous")/(name+"_"+r["id"][:16]+".json"),dict(circuit=r["circuit"],certificate=r["certify"],genome=r["genome"],construction=r["construction"],experiment_class="AUTONOMOUS_DISCOVERY"))
        save(Path("results/pareto/autonomous")/(name+".json"),dict(source=source,rows=frontier))
        print("LADDER",target,state["status"],len(rows),len(positive),"positives",flush=True)
        if state["status"]=="RESOURCE_SAFETY_INTERVENTION":return
    save(ROOT/"complete.json",dict(source=source,status="LADDER_COMPLETE"))
    print("LADDER_COMPLETE",flush=True)

if __name__=="__main__":main()
