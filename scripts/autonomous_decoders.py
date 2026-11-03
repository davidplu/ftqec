"""Matched physical-model decoder study and temporal-detector equivalence audit."""
import os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):os.environ[key]="1"
import json,time,hashlib
from pathlib import Path
import numpy as np
import psutil
from ftqec.results.artifacts import save,source_identity,digest
from ftqec.circuits.model import Circuit
from ftqec.simulation.monte_carlo import model,evaluate
from ftqec.simulation.sequential import combine
root=Path("results/ler/autonomous_decoder");root.mkdir(parents=True,exist_ok=True)
source=source_identity();selected=[]
for target in (3,10):
 s=json.loads(Path(f"results/discovery/autonomous/surface_target{target}/checkpoint.json").read_text())
 positive=[r for r in s["rows"] if r.get("certify",{}).get("status")=="CERTIFIED"]
 for r in positive[:2]:selected.append(dict(target=target,id=r["id"],circuit=r["circuit"],resources=r["resources"]))
protocol=dict(source=source,scientific_implementation_commit="3e50ef90cea15a778181fa8dc24d3056fdf6bb48",candidates=[r["id"] for r in selected],p=[.001,.01],decoders=["matching","one_mechanism_lookup"],looks=[4096,16384],seed=1618033,alpha=.05,driver_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
p=root/"protocol.json"
if p.exists():
 old=json.loads(p.read_text());assert old==protocol
else:save(p,protocol)
results=[];audits=[];start=time.perf_counter();cpu=time.process_time();peak=psutil.Process().memory_info().rss
for row in selected:
 c=Circuit.from_dict(row["circuit"])
 raw=model(c,.01,"raw");temporal=model(c,.01,"temporal")
 a,ao=raw.compile_detector_sampler(seed=31415).sample(256,separate_observables=True)
 b,bo=temporal.compile_detector_sampler(seed=31415).sample(256,separate_observables=True)
 expected=a.copy();previous={};records={o.record:o for o in c.operations if o.record}
 for i,det in enumerate(c.detectors):
  op=next((records[r] for r in det if "_s" in r),None)
  if op is not None:
   if op.check in previous:expected[:,i]^=a[:,previous[op.check]]
   previous[op.check]=i
 for i in range(len(c.code.generators)):
  if i in previous:expected[:,len(c.detectors)+i]^=a[:,previous[i]]
 audit=dict(id=row["id"],same_observables=bool(np.array_equal(ao,bo)),invertible_detector_transform=bool(np.array_equal(expected,b)),shots=256)
 assert audit["same_observables"] and audit["invertible_detector_transform"];audits.append(audit)
 for p in protocol["p"]:
  for decoder in protocol["decoders"]:
   folder=root/row["id"]/str(p)/decoder;folder.mkdir(parents=True,exist_ok=True)
   batches=[]
   for look,shots in enumerate(protocol["looks"]):
    path=folder/f"batch{look}.json"
    if path.exists():answer=json.loads(path.read_text())
    else:
     answer=evaluate(c,p,shots,1618033+look*10000019,100000,decoder=decoder);save(path,answer)
    if "shots" not in answer:
     results.append(dict(id=row["id"],target=row["target"],p=p,requested_decoder=decoder,unsupported=answer));break
    batches.append(answer);combined=combine(batches)
    if combined["confidence"][1]-combined["confidence"][0]<=.02:break
   if batches:results.append(dict(id=row["id"],target=row["target"],resources=row["resources"],p=p,requested_decoder=decoder,simulation=combine(batches),batches=batches))
   peak=max(peak,psutil.Process().memory_info().rss)
   save(root/"results.json",dict(source=source,rows=results,audits=audits,cpu=time.process_time()-cpu,wall=time.perf_counter()-start,observed_peak_rss=peak))
   print("DECODER",row["target"],p,decoder,results[-1].get("simulation",{}).get("failures"),flush=True)
save(root/"complete.json",dict(source=source,rows=len(results)))
