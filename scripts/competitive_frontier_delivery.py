"""Additional public bundles for every nondominated family alternative."""
import json,time,hashlib
from pathlib import Path
import psutil
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.optimization.selection import pareto
from ftqec.circuits.model import Circuit
from ftqec.execution.tasks import Task,batch
from ftqec.delivery.export import export_result
from ftqec.delivery.verify import verify_bundle
source=source_identity();primary=Path('results/competitive_export/delivery')/source
while not (primary/'complete.json').exists():time.sleep(2)
old='29bb185a85b2bb0f36e73bb52fe8a08a5f384a7239fb8e8220886ced4ac73b41';root=Path('results/competitive_export/final')/old;out=Path('results/competitive_export/frontier_delivery')/source
existing={r['candidate_id'] for r in json.loads((primary/'index.json').read_text())['records']};families={}
for p in sorted((root/'optimizer').glob('*/checkpoint.json')):
 if p.parent.name.startswith('control_'):continue
 state=json.loads(p.read_text());family=p.parent.name.split('_seed')[0]
 for row in state['rows']:
  if row.get('certify',{}).get('status')=='CERTIFIED':families.setdefault(family,[]).append(dict(row,origin=str(p),input_code=state['code'],config=state['config']))
selected=[]
for family,rows in families.items():
 unique={r['id']:r for r in pareto(rows)}
 for row in unique.values():
  if row['id'] not in existing:selected.append((family+'_'+row['id'][:12],row))
protocol=dict(source=source,discovery_source=old,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),selection='All family-level certified nondominated physical candidates across frozen seeds, excluding already delivered identities',candidates=[r['id'] for _,r in selected])
if (out/'protocol.json').exists():assert json.loads((out/'protocol.json').read_text())==protocol
else:save(out/'protocol.json',protocol)
start=time.perf_counter();cpu=time.process_time();index=[]
for label,original in selected:
 cc=Circuit.from_dict(original['circuit']);cfg=original['config'];t=Task(cc.to_dict(),'certify',cc.code.input_hash,{'p':.001},cfg['decoder'],cfg['seed'],source,dict(target=cfg['target'],proof_method='auto',work=20000000,memory_mb=512,cpu_seconds=180,wall_seconds=360))
 path=out/'certification'/(label+'.json')
 if path.exists():packet=json.loads(path.read_text());assert packet['task']==t.to_dict();a=packet['answer']
 else:a=batch([t],1)[0];save(path,dict(task=t.to_dict(),answer=a))
 assert a['result'].get('status')=='CERTIFIED',(label,a)
 row=dict(id=original['id'],circuit=cc.to_dict(),resources=original['resources'],certify=a['result'],genome=original['genome'],parent=original.get('parent'),original_discovery=dict(source=old,record=original))
 run=out/'records'/label;save(run/'tasks'/(a['task']+'.json'),dict(task=t.to_dict(),answer=a));save(run/'checkpoint.json',dict(source=source,code=original['input_code'],config=cfg,rows=[row],tasks={a['task']:a}))
 bundle=out/'exports'/label
 if not bundle.exists():export_result(run,row['id'],bundle)
 v=verify_bundle(bundle);assert v['positive_certificate_verified'];save(out/'verification'/(label+'.json'),v)
 index.append(dict(label=label,run=str(run),bundle=str(bundle),candidate_id=row['id'],circuit=digest(cc.to_dict()),source=source,status='CERTIFIED',verification=v,resources=row['resources']));print('FRONTIER_DELIVERED',label,flush=True)
save(out/'index.json',dict(source=source,records=index));save(out/'complete.json',dict(source=source,controller_cpu=time.process_time()-cpu,wall=time.perf_counter()-start,peak_controller_working_set=psutil.Process().memory_info().peak_wset,records=len(index)))
print('FAMILY_FRONTIER_DELIVERY_COMPLETE',len(index),flush=True)

