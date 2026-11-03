"""Matched fixed-pool audit with independently certified positive controls."""
import json,time,subprocess
from pathlib import Path
from ftqec.codes.input import load
from ftqec.architectures.population import sample,compile
from ftqec.screening.structural import check
from ftqec.certification.exact import certify,screen
from ftqec.simulation.monte_carlo import evaluate
from ftqec.optimization.selection import promising,pareto
from ftqec.evaluation.resources import resources
from ftqec.results.artifacts import save,source_identity,digest

def main():
    root=Path("benchmarks/retention");data=json.loads(Path("examples/surface_small.json").read_text());inp=load(data)
    protocol=dict(source=source_identity(),commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),code=data,seeds=list(range(8)),target=2,p=.001,shots=64,simulation_seed=32452843,work=100000)
    save(root/"protocol.json",protocol);pool=[]
    for seed in protocol["seeds"]:
        g=sample(inp,seed);c=compile(inp,g);check(c)
        pool.append(dict(circuit=c,id=digest(c.to_dict()),genome=g.to_dict(),resources=resources(c)))
    cpu=time.process_time();wall=time.perf_counter()
    for r in pool:r["baseline_proof"]=certify(r["circuit"],2,100000)
    baseline=dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-wall,calls=len(pool))
    cpu=time.process_time();wall=time.perf_counter();eligible=[]
    for i,r in enumerate(pool):
        r["screen"]=screen(r["circuit"])
        if r["screen"]["status"]!="FAULT_INVALID":
            r["simulation"]=evaluate(r["circuit"],.001,64,32452843+i);eligible.append(r)
    selected=promising(eligible)
    for r in selected:r["policy_proof"]=certify(r["circuit"],2,100000)
    policy=dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-wall,calls=len(selected))
    positive=[r for r in pool if r["baseline_proof"]["status"]=="CERTIFIED"];retained={r["id"] for r in selected};frontier=pareto(positive)
    save(root/"result.json",dict(protocol=protocol,baseline=baseline,policy=policy,positive_count=len(positive),positive_retention=sum(r["id"] in retained for r in positive),
        false_rejections=sum(r["id"] not in retained for r in positive),certified_resource_pareto_losses=sum(r["id"] not in retained for r in frontier),
        cpu_saving_seconds=baseline["cpu"]-policy["cpu"],certification_workload_reduction=1-policy["calls"]/baseline["calls"],
        rows=[dict(r,circuit=r["circuit"].to_dict()) for r in pool],qualification="One small target2 pool, including independently positive controls. End-to-end policy includes Monte Carlo, baseline certifies directly. CPU savings may be negative; no target3, family-generalization, true-LER-frontier or superiority claim."))

if __name__=="__main__":main()
