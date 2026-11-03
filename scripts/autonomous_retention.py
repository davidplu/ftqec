"""Prospective positive-containing allocation study with labels withheld from policies."""
import os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):os.environ[key]="1"
import json,time,random,hashlib
from pathlib import Path
from dataclasses import replace
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.execution.tasks import Task,batch
from ftqec.circuits.model import Circuit
from ftqec.circuits.identity import physical_identity
from ftqec.codes.input import load
from ftqec.architectures.population import compile,Genome
from ftqec.screening.structural import check
from ftqec.evaluation.resources import resources
from ftqec.optimization.costs import CostModel
from ftqec.optimization.adaptive import choose
from ftqec.optimization.selection import pareto
root=Path("benchmarks/positive_retention/autonomous");root.mkdir(parents=True,exist_ok=True)
source=source_identity();poolpath=root/"pool.json"
if not poolpath.exists():
 pool=[]
 for target in (2,10):
  state=json.loads(Path(f"results/discovery/autonomous/surface_target{target}/checkpoint.json").read_text())
  positives=[r for r in state["rows"] if r.get("certify",{}).get("status")=="CERTIFIED"]
  for r in positives[:2]:pool.append(dict(id=r["id"],target=target,circuit=r["circuit"],resources=r["resources"],genome=r["genome"]))
  if target==10:
   others=[r for r in state["rows"] if r.get("certify",{}).get("status") in ("INVALID","UNKNOWN")]
   for r in others[:2]:pool.append(dict(id=r["id"],target=target,circuit=r["circuit"],resources=r["resources"],genome=r["genome"]))
   parent=positives[0];inp=load(state["code"]);g=replace(Genome.from_dict(parent["genome"]),rounds=10)
   c=compile(inp,g);check(c);pool.append(dict(id=physical_identity(c),target=10,circuit=c.to_dict(),resources=resources(c),genome=g.to_dict(),origin="derived repeated-round positive-control candidate; truth determined independently"))
 save(poolpath,pool)
else:pool=json.loads(poolpath.read_text())
protocol=dict(source=source,scientific_implementation_commit="3e50ef90cea15a778181fa8dc24d3056fdf6bb48",pool_hash=digest(pool),policies=["direct","fixed","costaware","random"],seed=271828,
              decoder="matching",p=.001,shots=256,work=20000000,workers=2,memory_mb=512,
              truth_visibility="audit only; no labels passed to policy",global_time_cap=None,
              comparison="complete-pool total measured CPU plus common cumulative-CPU frontier intersections",
              driver_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
p=root/"protocol.json"
if p.exists():assert json.loads(p.read_text())==protocol
else:save(p,protocol)
def run(rows,tier,folder):
 tasks=[];todo=[];cached={}
 for row in rows:
  t=Task(row["circuit"],tier,Circuit.from_dict(row["circuit"]).code.input_hash,{"p":.001},"matching",271828+int(row["id"][:8],16),source,
         dict(target=row["target"],shots=256,work=20000000,memory_mb=512,cpu_seconds=300,wall_seconds=600,max_decoder_faults=100000))
  tasks.append(t);path=folder/(t.identity+".json")
  if path.exists():cached[t.identity]=json.loads(path.read_text())["answer"]
  else:todo.append(t)
 for t,a in zip(todo,batch(todo,2,512) if todo else []):save(folder/(t.identity+".json"),dict(task=t.to_dict(),answer=a));cached[t.identity]=a
 return [cached[t.identity] for t in tasks]
# Labels are computed by the same independent full physical checker, outside policy state.
truth=run(pool,"certify",root/"truth_tasks")
labels={r["id"]:a["result"] for r,a in zip(pool,truth)};save(root/"truth.json",labels)
truth_ler=run(pool,"simulation",root/"truth_ler_tasks")
ler_labels={r["id"]:a["result"] for r,a in zip(pool,truth_ler)};save(root/"truth_ler.json",ler_labels)
for policy in protocol["policies"]:
 folder=Path("benchmarks/policy_comparison/autonomous")/policy
 if (folder/"summary.json").exists():continue
 rows=[dict(r) for r in pool]
 if policy=="random":random.Random(271828).shuffle(rows)
 observations=[];decisions=[];history=[];spent=0.;shots=0;peak=0;certified=[];rejected=[]
 start=time.perf_counter();cpu=time.process_time()
 pending=list(rows)
 while pending:
  actions={}
  model=CostModel(observations)
  for i,r in enumerate(pending):
   if r.get("certify",{}).get("status") or r.get("screen",{}).get("status")=="FAULT_INVALID":continue
   if policy in ("direct","random"):action="certify"
   elif policy=="fixed":action="screen" if "screen" not in r else "simulation" if "simulation" not in r else "certify"
   else:decision=choose(r,r["target"],model,i);action=decision["action"]
   if policy!="costaware":decision=dict(action=action,reason="prospectively fixed policy")
   decisions.append(dict(id=r["id"],**decision))
   if action in ("retain","reject_with_proof"):continue
   actions.setdefault(action,[]).append(r)
  pending=[]
  for action,selected in actions.items():
   answers=run(selected,action,folder/"tasks")
   for row,a in zip(selected,answers):
    result=a["result"];row[action]=result;spent+=a["cpu"];shots+=result.get("shots",0);peak=max(peak,a.get("peak_rss",a.get("rss",0)))
    observations.append(dict(tier=action,target=row["target"],operations=len(row["circuit"]["operations"]),cpu=a["cpu"],censored=result.get("status")=="UNKNOWN",status=result.get("status","SIMULATED"),supported=result.get("status")!="UNSUPPORTED_DECODER"))
    if result.get("status")=="CERTIFIED":certified.append(row["id"])
    if result.get("status") in ("FAULT_INVALID","INVALID"):rejected.append(row["id"])
    if action!="certify" and result.get("status")!="FAULT_INVALID":pending.append(row)
  history.append(dict(worker_cpu=spent,coordinator_cpu=time.process_time()-cpu,certified=list(certified),rejected=list(rejected),checkpoint="completed parallel action wave"))
  if not actions:break
 positive={k for k,v in labels.items() if v.get("status")=="CERTIFIED"}
 truth_pareto=set()
 for target in (2,10):truth_pareto|={r["id"] for r in pareto([r for r in pool if r["target"]==target and r["id"] in positive])}
 from ftqec.optimization.selection import reliability_pareto
 ler_front=set()
 for target in (2,10):
  annotated=[dict(r,simulation=ler_labels[r["id"]]) for r in pool if r["target"]==target and r["id"] in positive]
  ler_front|={r["id"] for r in reliability_pareto(annotated)}
 eligible={r["id"] for r in pool}-set(rejected)
 summary=dict(source=source,policy=policy,known_architecture_families=sorted({r["genome"]["family"] for r in pool}),lost_architecture_families=sorted({r["genome"]["family"] for r in pool}-{r["genome"]["family"] for r in pool if r["id"] in eligible}),known_estimated_resource_ler_frontier=sorted(ler_front),
              retained_estimated_resource_ler_frontier=sorted(ler_front&eligible),
              retained_architecture_families=sorted({r["genome"]["family"] for r in pool if r["id"] in eligible}),worker_cpu=spent,coordinator_cpu=time.process_time()-cpu,wall=time.perf_counter()-start,
              peak_rss=peak,shots=shots,known_positives=sorted(positive),retained_positives=sorted(positive&set(certified)),
              false_hard_rejections=sorted(positive&set(rejected)),known_certified_pareto=sorted(truth_pareto),
              retained_certified_pareto=sorted(truth_pareto&set(certified)),history=history,decisions=decisions,
              unresolved=[r["id"] for r in rows if r.get("certify",{}).get("status")=="UNKNOWN"],
              resource_ler_retention="candidate retention against separate matching-decoder 256-shot point-estimate audit; broad uncertainty, not true LER frontier")
 save(folder/"summary.json",summary);print("POLICY",policy,spent,len(positive&set(certified)),"retained",flush=True)
save(root/"complete.json",dict(source=source,pool=len(pool)))
