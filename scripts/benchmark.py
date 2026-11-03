"""Prospective finite comparison; small controls do not establish superiority."""
import json,time
from pathlib import Path
from ftqec.optimization.engine import Config,optimize
from ftqec.codes.input import load
from ftqec.architectures.population import sample,compile
from ftqec.screening.structural import check
from ftqec.certification.exact import certify,screen
from ftqec.results.artifacts import save,source_identity,digest

def main():
    root=Path("benchmarks/results");root.mkdir(exist_ok=True)
    protocol=dict(source=source_identity(),codes=["surface_small","perfect5"],strategies=["random","witness","multifidelity","hybrid"],seed=104729,population=4,generations=2,target=2,initial_shots=16,further_shots=32,proof_work=10000)
    if (root/"protocol.json").exists() and json.loads((root/"protocol.json").read_text())!=protocol:raise ValueError("Frozen benchmark protocol changed")
    save(root/"protocol.json",protocol);rows=[]
    for name in protocol["codes"]:
        data=json.loads(Path("examples",name+".json").read_text())
        for strategy in protocol["strategies"]:
            state=optimize(data,root/name/strategy,Config(population=4,generations=2,seed=104729,initial_shots=16,further_shots=32,proof_work=10000,target=2,strategy=strategy))
            rows.append(dict(code=name,strategy=strategy,circuits=len(state["rows"]),certified=sum(r.get("certify",{}).get("status")=="CERTIFIED" for r in state["rows"]),compute=json.loads((root/name/strategy/"compute.json").read_text())))
    inp=load(json.loads(Path("examples/surface_small.json").read_text()));positive=[]
    for seed in range(8):
        c=compile(inp,sample(inp,seed));check(c);proof=certify(c,2,100000)
        if proof["status"]=="CERTIFIED":positive.append(dict(circuit=digest(c.to_dict()),proof=proof,screen=screen(c)))
    audit=dict(positive_count=len(positive),false_rejections=sum(x["screen"]["status"]=="FAULT_INVALID" for x in positive),controls=positive,scope="Target2 positive retention only; not target3 or family-generalization evidence; near-frontier loss and matched screening CPU savings remain unmeasured")
    save(root/"false_rejection.json",audit);save(root/"comparison.json",dict(protocol=protocol,rows=rows,superiority_claim=False))

if __name__=="__main__":main()
