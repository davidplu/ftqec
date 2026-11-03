"""Frozen development cost study, independent family split and bounded proof work."""
import json,time,subprocess,statistics,math
from pathlib import Path
from dataclasses import asdict
import psutil
from ftqec.results.artifacts import save,digest,source_identity
from ftqec.codes.input import load
from ftqec.architectures.population import sample,compile
from ftqec.circuits.identity import physical_identity
from ftqec.screening.structural import check
from ftqec.evaluation.resources import resources
from ftqec.certification.exact import certify,screen
from ftqec.simulation.monte_carlo import evaluate
from ftqec.simulation.sequential import combine
from ftqec.optimization.costs import CostModel
from ftqec.optimization.adaptive import choose
from ftqec.optimization.selection import pareto,promising,reliability_pareto

ROOT=Path("results/cost_aware/study")

def record_call(tier,c,target,shots=64,seed=0):
    cpu=time.process_time();wall=time.perf_counter()
    if tier=="certify":
        result=certify(c,target,10000) if target in (2,3,4) else dict(status="UNKNOWN",reason="UNSUPPORTED_PROOF_METHOD",target=target)
    elif tier=="screen":result=screen(c,10000)
    else:result=evaluate(c,.001,shots,seed)
    return dict(tier=tier,target=target,operations=len(c.operations),cpu=time.process_time()-cpu,wall=time.perf_counter()-wall,rss=psutil.Process().memory_info().rss,
        supported=target in (2,3,4) if tier=="certify" else True,censored=result.get("status")=="UNKNOWN" and result.get("reason")!="UNSUPPORTED_PROOF_METHOD",status=result.get("status","SIMULATED"),result=result)

def pool(name,count):
    data=json.loads(Path("examples",name+".json").read_text());inp=load(data);rows=[];seen=set()
    for i in range(count):
        cpu=time.process_time();wall=time.perf_counter();g=sample(inp,100003+i);c=compile(inp,g);structural=check(c);metric=resources(c);identity=physical_identity(c)
        if identity in seen:continue
        seen.add(identity);rows.append(dict(id=identity,circuit=c,genome=g.to_dict(),resources=metric,structural=structural,generation_cpu=time.process_time()-cpu,generation_wall=time.perf_counter()-wall))
    return rows

def serializable(row):return dict(row,circuit=row["circuit"].to_dict())

def policy_run(name,rows,target,model):
    cpu=time.process_time();wall=time.perf_counter();records=[];out=[];checkpoints=[];spent=0
    for i,original in enumerate(rows):
        row=dict(original);actions=[];beg=time.process_time();tick=time.perf_counter()
        if name=="direct":action="certify"
        elif name=="fixed":action="screen"
        elif name=="random":action=("certify","screen","simulation")[int(row["id"][:8],16)%3]
        else:
            temp=dict(row,circuit=row["circuit"].to_dict());decision=choose(temp,target,model,i);action=decision["action"];row["decision"]=decision
        if action=="screen":
            result=record_call("screen",row["circuit"],target);actions.append(result);row["screen"]=result["result"]
            action="reject" if result["status"]=="FAULT_INVALID" else "simulation"
        if action=="simulation":
            b=record_call("simulation",row["circuit"],target,64,900000+i);actions.append(b);batches=[b["result"]]
            if name in ("costaware","hybrid"):
                summary=combine(batches)
                if summary["confidence"][1]-summary["confidence"][0]>.2:
                    b=record_call("simulation",row["circuit"],target,256,1900000+i);actions.append(b);batches.append(b["result"])
                row["simulation"]=combine(batches)
            else:
                b=record_call("simulation",row["circuit"],target,256,1900000+i);actions.append(b);batches.append(b["result"]);row["simulation"]=combine(batches)
            action="certify"
        if action=="certify":
            b=record_call("certify",row["circuit"],target);actions.append(b);row["certify"]=b["result"]
        row["actions"]=actions;row["cpu"]=time.process_time()-beg;row["wall"]=time.perf_counter()-tick;spent+=row["cpu"];out.append(row);records+=actions
        checkpoints.append(dict(cumulative_cpu=spent,cumulative_wall=time.perf_counter()-wall,certified=[r["id"] for r in out if r.get("certify",{}).get("status")=="CERTIFIED"],processed=len(out)))
    return dict(policy=name,target=target,rows=[serializable(r) for r in out],cpu=time.process_time()-cpu,wall=time.perf_counter()-wall,actions=records,checkpoints=checkpoints,
        generation_qualification="Hybrid uses same fixed pool: generation improvement is deliberately not attributed to allocation policy")

def main():
    ROOT.mkdir(parents=True,exist_ok=False)
    protocol=dict(source=source_identity(),commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),train=["surface_small","perfect5"],final_families=["shor9","steane"],training_count=4,final_count=24,
        targets=[2,3,5,7,9],policies=["direct","fixed","costaware","random","hybrid"],seed=100003,proof_work=10000,p=.001,looks=[64,256],alpha=.05,stopping="width<=0.2 or two looks",scaling=[100,1000,10000],scaling_tiers="actual compile and noiseless validation only",comparison_checkpoints_cpu=[.5,1.,2.,4.,8.,16.],comparison_checkpoints_wall=[1.,2.,4.,8.,16.,32.],global_optimizer_cutoff=None)
    save(ROOT/"protocol.json",protocol);training=[];profiles=[]
    for name in protocol["train"]:
        for row in pool(name,4):
            for target in protocol["targets"]:
                result=record_call("certify",row["circuit"],target);profiles.append(dict(code=name,candidate=row["id"],**result))
                if result["supported"]:training.append(result)
            for tier in ("screen","simulation"):
                result=record_call(tier,row["circuit"],2);training.append(result)
    save(Path("benchmarks/certification_costs/profile.json"),dict(protocol=protocol,rows=profiles))
    model=CostModel(training);save(Path("results/cost_profiles/frozen.json"),dict(source=source_identity(),training=training,predictor="completed-only size-scaled median; censored lower bounds",frozen_before_final_families=True))
    comparisons=[];audit=[];calibration=[]
    for name in protocol["final_families"]:
        rows=pool(name,24);save(ROOT/(name+"_pool.json"),dict(source=source_identity(),rows=[serializable(r) for r in rows]))
        labels={}
        for row in rows:
            labels[row["id"]]=record_call("certify",row["circuit"],2)
            c=record_call("certify",row["circuit"],3);profiles.append(dict(code=name,candidate=row["id"],**c))
            estimate=model.estimate("certify",len(row["circuit"].operations),2)
            calibration.append(dict(code=name,candidate=row["id"],observed_cpu=labels[row["id"]]["cpu"],censored=labels[row["id"]]["censored"],rule_cpu=estimate.cpu,learned_cpu=model.learned_prediction("certify",len(row["circuit"].operations),2)))
        positives=[r for r in rows if labels[r["id"]]["status"]=="CERTIFIED"];frontier={r["id"] for r in pareto(positives)}
        references=[]
        for i,row in enumerate(rows):
            result=record_call("simulation",row["circuit"],2,256,70000000+i)
            references.append(dict(id=row["id"],resources=row["resources"],simulation=result["result"],cost=result,certification_status=labels[row["id"]]["status"]))
        save(Path("benchmarks/positive_retention")/(name+"_reference_ler.json"),dict(source=source_identity(),rows=references,scope="Common fixed-N benchmark reference, not an optimizer input; analysis compute charged separately"))
        for policy in protocol["policies"]:
            outcome=policy_run(policy,rows,2,model);outcome["code"]=name;path=Path("benchmarks/policy_comparison")/name/(policy+".json");save(path,outcome)
            retained={r["id"] for r in outcome["rows"] if r.get("certify",{}).get("status")=="CERTIFIED"}
            outcome["common_reference_ler_frontier"]=[r["id"] for r in reliability_pareto([r for r in references if r["id"] in retained])]
            save(path,outcome)
            audit.append(dict(code=name,policy=policy,positive_count=len(positives),retained_positive=len(retained & {r["id"] for r in positives}),false_hard_rejections=sum(r.get("screen",{}).get("status")=="FAULT_INVALID" and labels[r["id"]]["status"]=="CERTIFIED" for r in outcome["rows"]),lost_certified_pareto=len(frontier-retained)))
            comparisons.append(dict(code=name,policy=policy,cpu=outcome["cpu"],wall=outcome["wall"],certified=len(retained),compiled=len(rows),screened=sum(a["tier"]=="screen" for a in outcome["actions"]),simulation_batches=sum(a["tier"]=="simulation" for a in outcome["actions"]),shots=sum(a["result"].get("shots",0) for a in outcome["actions"]),certification_calls=sum(a["tier"]=="certify" for a in outcome["actions"]),checkpoints=outcome["checkpoints"]))
            print(name,policy,round(outcome["cpu"],3),len(retained),flush=True)
    save(Path("benchmarks/positive_retention/audit.json"),dict(source=source_identity(),rows=audit,qualification="Target2 held-out development families; unknown labels never converted to negative"))
    save(Path("results/cost_profiles/calibration.json"),dict(source=source_identity(),rows=calibration))
    save(Path("benchmarks/certification_costs/profile.json"),dict(protocol=protocol,rows=profiles))
    save(Path("benchmarks/policy_comparison/summary.json"),dict(protocol=protocol,rows=comparisons))
    # Actual equal-compute prefix checkpoints, excluding the unfinished candidate; no fractional credit.
    matched=[]
    for row in comparisons:
        for kind,budgets in (("cpu",protocol["comparison_checkpoints_cpu"]),("wall",protocol["comparison_checkpoints_wall"])):
            for budget in budgets:
                completed=[x for x in row["checkpoints"] if x["cumulative_"+kind]<=budget]
                matched.append(dict(code=row["code"],policy=row["policy"],metric=kind,budget=budget,completed=completed[-1] if completed else None,qualification="Comparison checkpoint, not optimizer stopping rule; complete-candidate prefixes only"))
    save(Path("benchmarks/policy_comparison/matched_compute.json"),dict(source=source_identity(),rows=matched))
    for count in protocol["scaling"]:
        inp=load(json.loads(Path("examples/steane.json").read_text()));cpu=time.process_time();wall=time.perf_counter();seen=set();families={}
        for i in range(count):
            g=sample(inp,982451653+i);c=compile(inp,g);check(c);identity=physical_identity(c);seen.add(identity);families[g.family]=families.get(g.family,0)+1
            if (i+1)%1000==0:print("scaling",count,i+1,flush=True)
        save(Path("benchmarks/population_scaling")/(str(count)+".json"),dict(source=source_identity(),generated=count,compiled=count,noiseless_checked=count,unique=len(seen),screened=0,simulated=0,certified=0,cpu=time.process_time()-cpu,wall=time.perf_counter()-wall,rss=psutil.Process().memory_info().rss,families=families,qualification="Only compile/noiseless tier; no evaluation throughput extrapolation"))
    print("STUDY_COMPLETE",flush=True)

if __name__=="__main__":main()
