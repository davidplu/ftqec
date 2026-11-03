"""Post-evaluation witness diagnosis; never promotes a positive certificate."""
import json,time,hashlib
from pathlib import Path
from collections import defaultdict
import psutil
from ftqec.results.artifacts import source_identity,save
from ftqec.circuits.model import Circuit
from ftqec.certification.exact import verify
from ftqec.certification.inventory import forward
from ftqec.certification.high_distance import negative
assert Path('benchmarks/policy_comparison/autonomous_generation/complete.json').exists()
root=Path('results/autonomous/posthoc_shor_diagnosis');root.mkdir(parents=True,exist_ok=True)
assert not (root/'result.json').exists(),'Preserve the prior diagnostic'
choices=[]
for p in Path('results/discovery/autonomous_comparison/shor_product4').glob('*/checkpoint.json'):
 for r in json.loads(p.read_text())['rows']:
  cert=r.get('certify',{})
  if cert.get('status')=='UNKNOWN' and cert.get('lower_bound')==3 and cert.get('independent',{}).get('verified'):choices.append((r['resources']['QD'],p.parent.name,r['id'],r))
_,strategy,cid,row=min(choices,key=lambda r:r[:3]);c=Circuit.from_dict(row['circuit']);source=source_identity()
protocol=dict(source=source,scientific_implementation_commit='3e50ef90cea15a778181fa8dc24d3056fdf6bb48',experiment_class='POSTHOC_FAILURE_DIAGNOSIS',selection='lowest QD independently bounded UNKNOWN in completed frozen Shor campaigns',strategy=strategy,id=cid,driver_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),maximum_inventory=10000,maximum_pairs=2000000,cpu_seconds=300,memory_mb=512,qualification='No optimizer tuning, no retrospective change to benchmark outcomes, no positive certification from this helper')
save(root/'protocol.json',protocol);save(root/'candidate.json',row)
start=time.perf_counter();cpu=time.process_time();checked=verify(c,row['certify'],2000000);assert checked['verified']
inv=forward(c)
try:
 assert inv.count<=10000
 items=list(inv.rows());groups=defaultdict(list)
 for k,(op,label,d,l,data) in enumerate(items):groups[d].append((k,op,label,l))
 pairs=triples=0;witness=None;stop=None
 for i,(oi,li,di,ei,_) in enumerate(items):
  if time.process_time()-cpu>=300 or psutil.Process().memory_info().rss>512*2**20 or psutil.virtual_memory().available<512*2**20:stop='RESOURCE_SAFETY_INTERVENTION';break
  for j in range(i+1,len(items)):
   pairs+=1
   if pairs>2000000:stop='PAIR_WORK_LIMIT';break
   oj,lj,dj,ej,_=items[j]
   if oi==oj:continue
   for k,ok,lk,ek in groups.get(di^dj,()):
    if k<=j or ok in (oi,oj):continue
    triples+=1
    if ei^ej^ek:
     witness=negative(c,[(oi,li),(oj,lj),(ok,lk)]);assert witness is not None
     break
   if witness:break
  if witness or stop:break
 status='VERIFIED_WEIGHT_THREE_WITNESS' if witness else stop or 'NO_WEIGHT_THREE_WITNESS_FOUND_DIAGNOSTIC_ONLY'
 save(root/'result.json',dict(source=source,status=status,id=cid,strategy=strategy,prior_independent_lower_bound=checked,inventory_count=inv.count,inventory_hash=inv.hash,pairs_examined=pairs,matching_location_exclusive_triples=triples,witness=witness,cpu=time.process_time()-cpu,wall=time.perf_counter()-start,rss=psutil.Process().memory_info().rss,qualification=protocol['qualification']))
 print(status,'pairs',pairs,'CPU',time.process_time()-cpu,flush=True)
finally:inv.close()
