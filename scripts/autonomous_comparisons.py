"""Frozen generation-policy comparisons on separate CSS construction families."""
import os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):os.environ[key]="1"
import json,hashlib
from pathlib import Path
from ftqec.results.artifacts import save,source_identity
from ftqec.optimization.engine import Config,optimize
from ftqec.codes.input import load
from ftqec.codes.distance import certify_code
root=Path("benchmarks/policy_comparison/autonomous_generation");root.mkdir(parents=True,exist_ok=True)
source=source_identity();cases={"steane":(json.loads(Path("examples/steane.json").read_text()),3)}
d=4;n=d*d;gens=[]
for row in range(d):
 for col in range(d-1):
  p=["I"]*n;p[row*d+col]=p[row*d+col+1]="Z";gens.append("".join(p))
for row in range(d-1):
 p=["I"]*n
 for q in range(row*d,(row+2)*d):p[q]="X"
 gens.append("".join(p))
cases["shor_product4"]=(dict(n=n,name="shor_product4",generators=gens),4)
protocol=dict(source=source,scientific_implementation_commit="3e50ef90cea15a778181fa8dc24d3056fdf6bb48",cases=cases,strategies=["random","witness","multifidelity","hybrid"],seed=57721,
              population=8,workers=2,initial_shots=64,further_shots=256,proof_work=2000000,
              convergence_generations=3,global_time_cap=None,
              split="surface development; Steane and Shor product final-family performance after freeze; historically exposed families, not a novelty holdout",
              comparison="actual cumulative compute intersection; equal generations not treated as matched compute",
              driver_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
p=root/"protocol.json"
if p.exists():assert json.loads(p.read_text())==json.loads(json.dumps(protocol))
else:save(p,protocol)
summary=[]
for name,(data,target) in cases.items():
 inp=load(data);save(root/name/"algebraic.json",certify_code(inp.code,target))
 for strategy in protocol["strategies"]:
  dest=Path("results/discovery/autonomous_comparison")/name/strategy
  cfg=Config(population=8,workers=2,seed=57721,target=target,strategy=strategy,initial_shots=64,further_shots=256,finalists=3,proof_work=2000000,decoder="auto",convergence_generations=3)
  statepath=dest/"checkpoint.json"
  if statepath.exists() and json.loads(statepath.read_text()).get("status")=="OPERATIONAL_FRONTIER_PLATEAU":state=json.loads(statepath.read_text())
  else:state=optimize(data,dest,cfg)
  compute=json.loads((dest/"compute.json").read_text());archives=json.loads((dest/"archives.json").read_text())
  summary.append(dict(name=name,target=target,strategy=strategy,source=source,stop_reason=state["status"],compute=compute,
                      archives=archives,frontier_history=state.get("frontier_history",[]),distinct=len(state["rows"]),
                      certified=sum(r.get("certify",{}).get("status")=="CERTIFIED" for r in state["rows"])))
  save(root/"summary.json",dict(protocol=protocol,rows=summary));print("GENERATION",name,strategy,summary[-1]["certified"],state["status"],flush=True)
  if state["status"]=="RESOURCE_SAFETY_INTERVENTION":raise SystemExit(2)
save(root/"complete.json",dict(source=source,rows=len(summary)))
