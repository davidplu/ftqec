"""Fresh replay of every distinct reported completed scientific proof body."""
import json,time
from pathlib import Path
from cost_study import pool
from ftqec.circuits.model import Circuit
from ftqec.certification.exact import verify
from ftqec.results.artifacts import digest,save,source_identity

def main():
    cpu=time.process_time();wall=time.perf_counter();circuits={};claims=[]
    for name in ("surface_small","perfect5"):
        for row in pool(name,4):circuits[(name,row["id"])]=row["circuit"]
    profile=json.loads(Path("benchmarks/certification_costs/profile.json").read_text())
    for name in ("shor9","steane"):
        p=json.loads(Path("results/cost_aware/study",name+"_pool.json").read_text())
        for row in p["rows"]:circuits[(name,row["id"])]=Circuit.from_dict(row["circuit"])
    for row in profile["rows"]:
        if row["supported"] and row["status"] in ("CERTIFIED","INVALID"):claims.append((row["code"],row["candidate"],row["result"]))
    for path in Path("benchmarks/policy_comparison").glob("*/*.json"):
        outcome=json.loads(path.read_text())
        for row in outcome["rows"]:
            cert=row.get("certify",{})
            if cert.get("status") in ("CERTIFIED","INVALID"):claims.append((outcome["code"],row["id"],cert))
    receipts={}
    for name,cid,cert in claims:
        body={k:v for k,v in cert.items() if k!="independent_cost"};key=digest(body)
        if key not in receipts:
            check=verify(circuits[(name,cid)],cert,10000)
            receipts[key]=dict(code=name,candidate=cid,target=cert["target"],status=cert["status"],receipt=check,instances=0)
            if not check["verified"]:raise ValueError("Fresh proof audit failed: "+key)
        receipts[key]["instances"]+=1
    save(Path("results/pareto/proof_audit.json"),dict(source=source_identity(),status="PASS",claims=len(claims),distinct_completed_proof_bodies=len(receipts),receipts=receipts,cpu=time.process_time()-cpu,wall=time.perf_counter()-wall,qualification="UNKNOWN/unsupported records remain unaccepted; duplicates require the same completed scientific proof body and fresh replay once per exact body"))
    print(len(claims),len(receipts),"proof bodies verified",flush=True)

if __name__=="__main__":main()
