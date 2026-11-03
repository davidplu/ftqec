"""Independently replay and export all newly certified physical discoveries."""
import json,time,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.circuits.model import Circuit
from ftqec.circuits.identity import physical_identity
from ftqec.evaluation.resources import resources
from ftqec.execution.tasks import Task,batch
from ftqec.certification.eligibility import assess,verify
from ftqec.delivery.export import export_result
from ftqec.delivery.verify import verify_bundle
from ftqec.optimization.selection import pareto
source=source_identity();population=Path('results/non_graphlike')/source/'population_study';root=Path('results/exports')/source/'finalists';root.mkdir(parents=True,exist_ok=True)
while not (population/'complete.json').exists():time.sleep(2)
start=time.perf_counter();cpu=time.process_time();candidates={}
def add(data,certificate,genome,origin,parent=None,input_code=None):
 if certificate.get('status')!='CERTIFIED':return
 c=Circuit.from_dict(data);cid=physical_identity(c);key=(cid,certificate['target'])
 if key in candidates:candidates[key]['origins'].append(origin);return
 candidates[key]=dict(id=cid,circuit=data,certify=certificate,genome=genome,resources=resources(c),parent=parent,input_code=input_code or c.code.to_dict(),origins=[origin])
for p in sorted(population.glob('*/checkpoint.json')):
 s=json.loads(p.read_text())
 for row in s['rows']:add(row['circuit'],row.get('certify',{}),row['genome'],str(p),row.get('parent'),s['code'])
for p in (Path('results/pareto')/source/'deferred_frontier').glob('*.json'):
 d=json.loads(p.read_text())
 if 'answer' in d:add(d['origin']['circuit'],d['answer']['result'],d['origin']['genome'],str(p),d['origin'].get('parent'),d['origin']['input_code'])
for p in (Path('results/pareto')/source/'compaction_study').glob('*.json'):
 d=json.loads(p.read_text())
 if 'answer' in d:add(d['construction']['result']['circuit'],d['answer']['result'],d['genome'],str(p),d['parent']['id'],d['parent']['input_code'])
p=Path('results/pareto')/source/'allocation_study/rows.json'
for row in json.loads(p.read_text()):
 if 'certification' in row:add(row['circuit'],row['certification']['result'],row['genome'],str(p)+'#slot='+str(row['slot']),row['parent'])
p=Path('results/repair_trajectories')/source/'shor5_six_arm/rows.json'
for row in json.loads(p.read_text()):
 for method in ['decomposition','mitm']:
  if method in row:add(row['construction']['result']['circuit'],row[method]['result'],row['genome'],str(p)+'#seed='+str(row['seed']),row['parent'])
protocol=dict(source=source,selection='Every newly certified physical discovery, including dominated positives; family Pareto adoption only after separate replay and export reconstruction',candidates=[dict(id=k[0],target=k[1]) for k in sorted(candidates)],work=20000000,cpu=120,wall=240,memory_mb=384,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
index=[];frontiers={}
for (cid,target),row in sorted(candidates.items()):
 label=f'{target}_{cid}';c=Circuit.from_dict(row['circuit']);path=root/'replays'/(label+'.json')
 t=Task(dict(circuit=c.to_dict(),certificate=row['certify']),'verify',c.code.input_hash,{'p':.001},'auto',0,source,dict(work=20000000,memory_mb=384,cpu_seconds=120,wall_seconds=240))
 if path.exists():a=json.loads(path.read_text())['answer']
 else:a=batch([t],1)[0];save(path,dict(task=t.to_dict(),answer=a))
 if not a['result'].get('verified'):index.append(dict(id=cid,target=target,adopted=False,verification=a));continue
 e=assess(c);ev=verify(c,e);assert ev['verified'];save(root/'eligibility'/(label+'.json'),dict(assessment=e,independent=ev))
 run=root/'records'/label;save(run/'checkpoint.json',dict(source=source,code=row['input_code'],config=dict(target=target,decoder='auto',p=.001),rows=[row],tasks={}))
 bundle=root/'bundles'/label
 if not bundle.exists():export_result(run,cid,bundle)
 v=verify_bundle(bundle,20000000);save(root/'verification'/(label+'.json'),v)
 adopted=bool(v.get('positive_certificate_verified'));record=dict(id=cid,circuit=digest(c.to_dict()),target=target,code=c.code.to_dict(),source=source,bundle=str(bundle),run=str(run),resources=row['resources'],origins=row['origins'],parent=row['parent'],graph_eligible=e['eligible'],independent=v,adopted=adopted)
 index.append(record)
 if adopted:frontiers.setdefault(c.code.input_hash+':'+str(target),[]).append(row)
 print('DELIVERED',target,cid[:12],adopted,flush=True)
frontier={key:[dict(id=r['id'],resources=r['resources'],origins=r['origins']) for r in pareto(rows)] for key,rows in frontiers.items()}
save(root/'index.json',dict(source=source,records=index));save(Path('results/pareto')/source/'certified_frontiers.json',dict(source=source,frontiers=frontier,qualification='Finite independently verified frontier, not a global optimum. All dominated positives and unresolved records retained.'))
save(root/'complete.json',dict(source=source,controller_cpu=time.process_time()-cpu,wall=time.perf_counter()-start,records=len(index)))
