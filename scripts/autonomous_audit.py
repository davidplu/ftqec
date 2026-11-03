"""Read-only-source release audit: replay, concurrency and prior-epoch preservation."""
import json,time,hashlib
from pathlib import Path
from ftqec.results.artifacts import save,source_identity
from ftqec.circuits.model import Circuit
from ftqec.certification.exact import verify
from ftqec.faults.verification import verify_witness
from ftqec.codes.input import load
from ftqec.architectures.synthesis import generate
from ftqec.architectures.population import compile
from ftqec.screening.structural import check
from ftqec.certification.exact import certify
source=source_identity();rows=[];start=time.perf_counter();cpu=time.process_time()
for p in sorted(Path("results/discovery/autonomous").glob("*/checkpoint.json")):
 s=json.loads(p.read_text());positive=[r for r in s["rows"] if r.get("certify",{}).get("status")=="CERTIFIED"]
 if not positive:continue
 r=min(positive,key=lambda r:r["resources"]["QD"])
 result=verify(Circuit.from_dict(r["circuit"]),r["certify"],20000000)
 assert result["verified"]
 rows.append(dict(run=p.parent.name,id=r["id"],independent=result))
for p in Path("results/discovery/autonomous_comparison").glob("*/*/checkpoint.json"):
 s=json.loads(p.read_text());partial=[r for r in s['rows'] if r.get('certify',{}).get('status')=='UNKNOWN' and r['certify'].get('independent',{}).get('verified')]
 if partial:
  r=min(partial,key=lambda r:(-r['certify']['lower_bound'],r['resources']['QD']))
  result=verify(Circuit.from_dict(r['circuit']),r['certify'],2000000);assert result['verified']
  rows.append(dict(run=p.parent.as_posix(),id=r['id'],partial_bound=result,status='UNKNOWN'))
for p in list(Path("results/discovery/autonomous").glob("*/checkpoint.json"))+list(Path("results/discovery/autonomous_comparison").glob("*/*/checkpoint.json")):
 s=json.loads(p.read_text())
 for r in s["rows"]:
  w=r.get("screen",{}).get("witness") or r.get("certify",{}).get("witness")
  if w:
   result=verify_witness(Circuit.from_dict(r["circuit"]),w);assert result["verified"]
   rows.append(dict(run=p.parent.as_posix(),id=r["id"],witness=result))
posthoc=Path('results/autonomous/posthoc_shor_diagnosis')
if (posthoc/'result.json').exists():
 diagnostic=json.loads((posthoc/'result.json').read_text());candidate=json.loads((posthoc/'candidate.json').read_text())
 if diagnostic.get('witness'):
  replayed=verify_witness(Circuit.from_dict(candidate['circuit']),diagnostic['witness']);assert replayed['verified']
  rows.append(dict(run=str(posthoc),id=candidate['id'],posthoc_witness=replayed))
save(Path("results/autonomous/release/independent_audit.json"),dict(source=source,rows=rows,cpu=time.process_time()-cpu,wall=time.perf_counter()-start))
events=[];worker_cpu=0.;ids=set();intervals=[]
for p in Path("results/discovery/autonomous").glob("*/tasks/*.json"):
 a=json.loads(p.read_text())["answer"]
 for attempt in a.get("attempts",[a]):
  if "dispatch_monotonic" not in attempt:continue
  assert attempt["pid"]==attempt["supervised_pid"]
  events.extend([(attempt["dispatch_monotonic"],1),(attempt["completion_monotonic"],-1)])
  worker_cpu+=attempt["cpu"];ids.add(attempt["pid"]);intervals.append(dict(pid=attempt["pid"],start=attempt["dispatch_monotonic"],end=attempt["completion_monotonic"],cpu=attempt["cpu"]))
active=peak=0
for stamp,delta in sorted(events):active+=delta;peak=max(peak,active)
best=None
for i,a in enumerate(intervals):
 for b in intervals[i+1:]:
  if a['pid']==b['pid'] or max(a['start'],b['start'])>=min(a['end'],b['end']):continue
  elapsed=max(a['end'],b['end'])-min(a['start'],b['start']);ratio=(a['cpu']+b['cpu'])/elapsed
  if best is None or ratio>best['worker_cpu_per_elapsed_second']:best=dict(workers=[a,b],elapsed=elapsed,worker_cpu_per_elapsed_second=ratio)
save(Path("results/autonomous/release/concurrency.json"),dict(source=source,observed_peak_concurrent_evaluators=peak,distinct_pids=len(ids),completed_worker_cpu=worker_cpu,best_measured_overlap=best,qualification="actual evaluator lifetimes and measured CPU; CPU/elapsed above one demonstrates multicore use, not an isolated speedup comparison"))
old=json.loads(Path("results/autonomous/baseline/preservation.json").read_text())["evidence"]
bad=[];relocated=[]
for name,sha in old.items():
 p=Path(name)
 if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==sha:continue
 backup=Path("results/autonomous/baseline/prior_artifact_manifest.json")
 if name=="results/artifact_manifest.json" and backup.exists() and hashlib.sha256(backup.read_bytes()).hexdigest()==sha:relocated.append(dict(original=name,preserved=str(backup)));continue
 bad.append(name)
assert not bad,bad
save(Path("results/autonomous/release/preservation.json"),dict(prior_files=len(old),mismatches=bad,relocated_manifests=relocated,status="PASS"))
# Metamorphic code-only check: arbitrary data relabeling and generator reorder.
data=json.loads(Path("results/autonomous/campaign/codes/surface_target4.json").read_text())
import random
rng=random.Random(24681357);perm=list(range(data["n"]));rng.shuffle(perm)
data["generators"]=["".join(g[q] for q in perm) for g in reversed(data["generators"])];data.pop("metadata",None);data.pop("signs",None);data["name"]="anonymous_permuted_css"
inp=load(data);g,construction=generate(inp,0,4);c=compile(inp,g);check(c);cert=certify(c,4,20000000)
assert cert["status"]=="CERTIFIED" and verify(c,cert,20000000)["verified"]
save(Path("results/autonomous/release/permutation_validation.json"),dict(source=source,input=data,construction=construction,circuit=c.to_dict(),certificate=cert))
print("AUDIT_COMPLETE",len(rows),"records",peak,"concurrent evaluators",len(old),"preserved files",flush=True)
