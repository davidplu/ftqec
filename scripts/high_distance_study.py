"""Prospective real-circuit high-distance study; references never enter optimizer seeds."""
import os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):os.environ[key]="1"
import json,time,subprocess,shutil,platform,collections
from pathlib import Path
import psutil
from ftqec.results.artifacts import save,digest,source_identity
from ftqec.codes.input import load
from ftqec.architectures.population import sample,compile
from ftqec.architectures.references import rotated_surface
from ftqec.circuits.identity import physical_identity
from ftqec.circuits.model import Circuit
from ftqec.screening.structural import check
from ftqec.evaluation.resources import resources
from ftqec.execution.tasks import Task,batch
from ftqec.certification.exact import verify
from ftqec.optimization.costs import CostModel
from ftqec.optimization.adaptive import choose
from ftqec.optimization.engine import Config,optimize
from ftqec.optimization.selection import pareto
from ftqec.simulation.sequential import combine

ROOT=Path("results/high_distance/study")
FROZEN=None

def task(c,tier,target,output,seed=0,shots=64):
    if FROZEN is not None and source_identity()!=FROZEN:raise ValueError("Frozen scientific source changed")
    return Task(c.to_dict(),tier,c.code.input_hash,dict(p=.001),"one_mechanism_lookup",seed,source_identity(),dict(target=target,work=20000000,shots=shots,memory_mb=512,cpu_seconds=900,wall_seconds=1200,proof_directory=str((output/"proofs").resolve())))

def evaluate(c,tier,target,output,seed=0,shots=64):
    output.mkdir(parents=True,exist_ok=True);t=task(c,tier,target,output,seed,shots);path=output/(t.identity+".json")
    if path.exists():
        saved=json.loads(path.read_text())
        if saved["task"]!=t.to_dict():raise ValueError("Cached scientific task mismatch")
        return saved["answer"]
    answer=batch([t],1,memory_mb=512)[0]
    save(path,dict(task=t.to_dict(),answer=answer));return answer

def make_pool(name,count):
    inp=load(json.loads(Path("examples",name+".json").read_text()));rows=[];seen=set()
    for seed in range(424243,424243+count):
        g=sample(inp,seed);c=compile(inp,g);check(c);cid=physical_identity(c)
        if cid not in seen:seen.add(cid);rows.append(dict(id=cid,circuit=c,genome=g.to_dict(),resources=resources(c),seed=seed))
    return rows

def main():
    global FROZEN
    ROOT.mkdir(parents=True,exist_ok=True);source=source_identity();FROZEN=source
    cpu_info=subprocess.run(["powershell.exe","-NoProfile","-Command","Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json -Compress"],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    protocol=dict(source=source,commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),driver_sha256=digest(Path(__file__).read_text()),protocol_sha256=digest(Path("docs/SCIENTIFIC_PROTOCOL.md").read_text()),distances=[3,5,7,9],round_variants="one and designed distance",target_work=20000000,worker_memory_mb=512,workers=2,per_action_cpu=900,per_action_wall=1200,global_time_cutoff=None,seed=424243,policies=["direct","fixed","costaware","random","hybrid_allocation"],final_families=["steane","shor9"],development_families=["perfect5","surface_small"],pool_count=16,simulation=dict(p=.001,looks=[64,256],alpha=.05,decoder="one_mechanism_lookup"),architecture_vocabulary=["bare","flagged","cat","verified_cat","phase_correct_basis_mutations"],success="fresh graph-potential target9 proof excludes0..8 under extraction-only contract; no claim of full physical memory")
    if (ROOT/"protocol.json").exists():
        frozen=json.loads((ROOT/"protocol.json").read_text())
        if frozen["source"]!=source:raise ValueError("Resume source mismatch")
        protocol=frozen
    else:save(ROOT/"protocol.json",protocol)
    save(Path("results/local_feasibility/host_resume.json" if Path("results/local_feasibility/host.json").exists() else "results/local_feasibility/host.json"),dict(source=source,cpu_model=cpu_info.stdout.strip(),cpu_query_stderr=cpu_info.stderr,physical_cores=psutil.cpu_count(logical=False),logical_cores=psutil.cpu_count(),ram_available=psutil.virtual_memory().available,ram_total=psutil.virtual_memory().total,disk=shutil.disk_usage('.')._asdict(),platform=platform.platform(),native_thread_environment=1))
    cases=[];tasks=[]
    for d in protocol["distances"]:
        for rounds in (1,d):
            inp,c=rotated_surface(d,rounds);check(c);name=f"surface_d{d}_r{rounds}_t{d}";out=ROOT/"controls"/name;out.mkdir(parents=True,exist_ok=True)
            save(out/"circuit.json",c.to_dict());save(out/"code.json",inp.to_dict());t=task(c,"certify",d,out);tasks.append(t);cases.append(dict(name=name,distance=d,rounds=rounds,target=d,output=str(out),resources=resources(c),circuit_hash=digest(c.to_dict())))
    # Actual parallel workers, not synthetic scheduling.
    answers=[]
    for case,t in zip(cases,tasks):
        result_path=Path(case["output"])/"result.json"
        if not result_path.exists():break
        saved=json.loads(result_path.read_text())
        if saved["task"]!=t.to_dict():raise ValueError("Reference resume identity")
        answers.append(saved["answer"])
    if len(answers)!=len(tasks):answers=batch(tasks,2,memory_mb=512)
    audit=[]
    for case,t,answer in zip(cases,tasks,answers):
        save(Path(case["output"])/"result.json",dict(task=t.to_dict(),answer=answer));case["answer"]=answer
        result=answer["result"]
        if result.get("status")=="CERTIFIED" and not Path("results/high_distance/independent_audit.json").exists():
            c=Circuit.from_dict(t.circuit);cpu=time.process_time();wall=time.perf_counter();checked=verify(c,result,20000000)
            audit.append(dict(name=case["name"],source=source,receipt=checked,cpu=time.process_time()-cpu,wall=time.perf_counter()-wall));assert checked["verified"]
        print(case["name"],result.get("status"),result.get("lower_bound"),result.get("exact_distance"),round(answer["cpu"],3),answer.get("peak_rss"),flush=True)
        save(Path("benchmarks/high_distance/ladder.json"),dict(protocol=protocol,rows=cases))
    if audit:save(Path("results/high_distance/independent_audit.json"),dict(source=source,rows=audit))
    for d in protocol["distances"]:
        inp,c=rotated_surface(d,d);check(c);answer=evaluate(c,"certify",d+2,ROOT/"negative_controls"/str(d));save(ROOT/"negative_controls"/(str(d)+".json"),answer)
    nine=next(c for c in cases if c["distance"]==9 and c["rounds"]==9)
    if nine["answer"]["result"].get("status")=="CERTIFIED" and not Path("results/local_feasibility/resume.json").exists():
        c=Circuit.from_dict(json.loads((Path(nine["output"])/"circuit.json").read_text()));again=evaluate(c,"certify",9,Path(nine["output"]));same=digest(again["result"]["proof"])==digest(nine["answer"]["result"]["proof"])
        save(Path("results/local_feasibility/resume.json"),dict(source=source,same_proof=same,answer=again,partition_files=len(list((Path(nine["output"])/"proofs").rglob('*.json')))));assert same
    # Training costs freeze before final-family allocation outcomes.
    training=[]
    for name in protocol["development_families"]:
        for row in make_pool(name,4):
            for tier in ("screen","simulation","certify"):
                a=evaluate(row["circuit"],tier,3,ROOT/"training"/name/row["id"],row["seed"])
                training.append(dict(tier=tier,target=3,operations=len(row["circuit"].operations),cpu=a["cpu"],wall=a["wall"],status=a["result"].get("status","SIMULATED"),censored=a["result"].get("status")=="UNKNOWN",supported=True))
    save(ROOT/"frozen_cost_model.json",dict(source=source,rows=training));model=CostModel(training);summaries=[]
    for name in ("perfect5","steane","shor9"):
        pool=make_pool(name,16);save(ROOT/"pools"/(name+".json"),dict(source=source,rows=[dict(r,circuit=r["circuit"].to_dict()) for r in pool]))
        labels={};frontier_rows=[]
        for policy in protocol["policies"]:
            completed=Path("benchmarks/cost_aware")/name/(policy+".json")
            if completed.exists():
                old=json.loads(completed.read_text())
                if old["source"]!=source:raise ValueError("Policy resume source")
                summaries.append(old["summary"])
                if policy=="direct":labels={r["id"]:r.get("certify",{}).get("status") for r in old["rows"]}
                print("REUSED",name,policy,flush=True);continue
            partial_before=(ROOT/"policies"/name/policy).exists()
            start=time.perf_counter();parent=time.process_time();rows=[];history=[];worker_cpu=0
            for i,original in enumerate(pool):
                row=dict(original,circuit=original["circuit"].to_dict());c=original["circuit"];out=ROOT/"policies"/name/policy/row["id"];actions=[]
                action="certify" if policy=="direct" else "screen" if policy=="fixed" else ("screen","simulation","certify")[i%3] if policy=="random" else choose(row,3,model,i)["action"]
                row["initial_action"]=action
                if action=="screen":
                    a=evaluate(c,"screen",3,out,original["seed"]);actions.append(a);row["screen"]=a["result"];action="done" if row["screen"].get("status")=="FAULT_INVALID" else "simulation"
                if action=="simulation":
                    a=evaluate(c,"simulation",3,out,original["seed"],64);actions.append(a);batches=[a["result"]] if "shots" in a["result"] else []
                    if batches and (policy in ("fixed","random") or combine(batches)["confidence"][1]-combine(batches)["confidence"][0]>.2):
                        a=evaluate(c,"simulation",3,out,original["seed"]+10**10,256);actions.append(a)
                        if "shots" in a["result"]:batches.append(a["result"])
                    if batches:row["simulation"]=combine(batches)
                    action="certify"
                if action=="certify":
                    a=evaluate(c,"certify",3,out,original["seed"]);actions.append(a);row["certify"]=a["result"]
                    if policy=="direct":labels[row["id"]]=a["result"].get("status")
                row["actions"]=actions;rows.append(row);worker_cpu+=sum(a["cpu"] for a in actions)
                valid=[r for r in rows if r.get("certify",{}).get("status")=="CERTIFIED"]
                history.append(dict(processed=len(rows),worker_cpu=worker_cpu,parent_cpu=time.process_time()-parent,wall=time.perf_counter()-start,certified=[r["id"] for r in valid],pareto=[r["id"] for r in pareto(valid)]))
            valid=[r for r in rows if r.get("certify",{}).get("status")=="CERTIFIED"];retained={r["id"] for r in valid}
            summary=dict(resumed_from_partial=partial_before,wall_scope="resumed session only; previous partial controller wall/CPU unmeasured" if partial_before else "complete measured policy session",code=name,policy=policy,cpu=worker_cpu,parent_cpu=time.process_time()-parent,wall=time.perf_counter()-start,compiled=len(pool),certified=len(valid),unknown=sum(r.get("certify",{}).get("status")=="UNKNOWN" for r in rows),shots=sum(r.get("simulation",{}).get("shots",0) for r in rows),false_rejection=sum(r.get("screen",{}).get("status")=="FAULT_INVALID" and labels.get(r["id"])=="CERTIFIED" for r in rows),retained=sorted(retained),history=history)
            save(Path("benchmarks/cost_aware")/name/(policy+".json"),dict(source=source,summary=summary,rows=rows));summaries.append(summary);print("policy",name,policy,len(valid),round(worker_cpu,3),flush=True)
        save(Path("benchmarks/positive_retention/high_distance")/(name+".json"),dict(source=source,labels=labels,summaries=[r for r in summaries if r["code"]==name]))
    save(Path("benchmarks/cost_aware/summary.json"),dict(source=source,rows=summaries,qualification="Same pools; exact completed Windows worker CPU and separate controller CPU. Hybrid-allocation arm is distinct from the actual hybrid population run below."))
    # Real population run, not a reference seeded into the optimizer.
    code=json.loads(Path("examples/steane.json").read_text());result=optimize(code,ROOT/"population",Config(population=24,generations=2,workers=2,seed=65537,target=3,proof_work=20000000,strategy="costhybrid",initial_shots=64,further_shots=256))
    save(Path("results/pareto/high_distance_population.json"),dict(source=source,status=result["status"],generated=len(result["rows"]),certified=sum(r.get("certify",{}).get("status")=="CERTIFIED" for r in result["rows"]),frontier=json.loads((ROOT/"population/archives.json").read_text()),frontier_history=result.get("frontier_history",[])))
    save(ROOT/"execution_complete.json",dict(source=source,complete=True,scientific_success_requires_independent_audit=True));print("STUDY_COMPLETE",flush=True)

if __name__=="__main__":main()
