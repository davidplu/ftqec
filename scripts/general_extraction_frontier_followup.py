"""Prospective certification of deferred verified-cat resource alternatives."""
import json,time,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.optimization.selection import pareto
from ftqec.execution.tasks import Task,batch
from ftqec.circuits.model import Circuit
from ftqec.certification.eligibility import assess,verify
source=source_identity();base=Path('results/non_graphlike')/source/'population_study';root=Path('results/pareto')/source/'deferred_frontier';root.mkdir(parents=True,exist_ok=True)
rows=[]
for seed in [101,211]:
 p=base/f'shor5_random_{seed}'/'checkpoint.json';s=json.loads(p.read_text());assert s['status']=='REQUESTED_GENERATIONS_COMPLETED'
 rows.extend(dict(r,origin=str(p),input_code=s['code']) for r in s['rows'] if r['genome']['family']=='verified_cat' and r.get('certify',{}).get('status') not in ('INVALID','UNKNOWN') and r.get('screen',{}).get('status')!='FAULT_INVALID')
# pareto() requires certified status; select on actual resources directly here,
# retaining all equal-resource physical identities, then certify before adoption.
def dominates(a,b):
 keys=('Q','D','QD','two_q_gates');return all(a['resources'][k]<=b['resources'][k] for k in keys) and any(a['resources'][k]<b['resources'][k] for k in keys)
selected={r['id']:r for r in rows if not any(dominates(q,r) for q in rows) and r.get('certify',{}).get('status')!='CERTIFIED'}
protocol=dict(source=source,selection='All deferred nondominated verified-cat alternatives from the two completed random populations; identical resource tuples retain independent physical identities; excludes already certified and verified invalid or guarded UNKNOWN rows',ids=sorted(selected),work=20000000,cpu=120,wall=240,memory_mb=384,workers=2,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
start=time.perf_counter();cpu=time.process_time();index=[]
for cid,row in selected.items():
 path=root/(cid+'.json')
 if path.exists():index.append(str(path));continue
 c=Circuit.from_dict(row['circuit']);e=assess(c);v=verify(c,e);assert v['verified']
 t=Task(c.to_dict(),'certify',c.code.input_hash,{'p':.001},'auto',0,source,dict(target=5,proof_method='auto',work=20000000,memory_mb=384,cpu_seconds=120,wall_seconds=240,proof_directory=str(root/'proofs'/cid)))
 a=batch([t],2)[0];save(path,dict(origin=row,task=t.to_dict(),answer=a,eligibility=e,eligibility_verification=v));index.append(str(path));print('DEFERRED_FRONTIER',cid[:12],a['result'].get('status'),flush=True)
save(root/'complete.json',dict(source=source,records=index,wall=time.perf_counter()-start,controller_cpu=time.process_time()-cpu))
