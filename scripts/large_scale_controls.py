"""Re-certify preserved historical frontiers as controls, never optimizer seeds."""
import json,time,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.circuits.model import Circuit
from ftqec.circuits.identity import physical_identity
from ftqec.evaluation.resources import resources
from ftqec.execution.tasks import Task,batch
from ftqec.delivery.export import export_result
from ftqec.delivery.verify import verify_bundle
s=source_identity();old='d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306';root=Path('results/large_scale/controls')/s;root.mkdir(parents=True,exist_ok=True)
base=Path('results/general_extraction/controls')/old/'exports';cases=[]
for name,target,method in [('surface10_seed24',10,'graph'),('allocation_certify_1',10,'graph'),('allocation_certify_25',10,'graph'),('allocation_certify_50',10,'graph'),('repair_compressed',4,'mitm')]:
 path=base/name/'circuit.json';cases.append(dict(name=name,circuit=json.loads(path.read_text()),target=target,method=method,origin=str(path),classification='preserved historical control'))
index=json.loads((Path('results/exports')/old/'finalists/index.json').read_text())['records']
for prefix,name,target in [('db9bf9ac','shor5_low_qubit',5),('b1aad234','shor5_low_qd',5),('04c290a8','hgp3_previous',3)]:
 r=next(x for x in index if x['id'].startswith(prefix));path=Path(r['bundle'])/'circuit.json';cases.append(dict(name=name,circuit=json.loads(path.read_text()),target=target,method='mitm',origin=str(path),classification='preserved historical control'))
protocol=dict(source=s,cases=cases,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),work=20000000,scope='Historical positive controls are segregated from code-only optimizer inputs and are not new discoveries.')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
records=[]
for case in cases:
 name=case['name'];data=case['circuit'];c=Circuit.from_dict(data);p=root/'certification'/(name+'.json')
 task=Task(data,'certify',c.code.input_hash,dict(p=.001),'auto',0,s,dict(target=case['target'],proof_method=case['method'],work=20000000,memory_mb=384,cpu_seconds=120,wall_seconds=240,proof_directory=str(root/'proofs'/name)))
 if p.exists():packet=json.loads(p.read_text());assert packet['task']==task.to_dict()
 else:packet=dict(task=task.to_dict(),answer=batch([task],1,memory_mb=384)[0]);save(p,packet)
 answer=packet['answer'];row=dict(id=physical_identity(c),circuit=data,resources=resources(c),certify=answer['result'],origin=case['classification'],parent=None)
 run=root/'records'/name;save(run/'checkpoint.json',dict(source=s,code=c.code.to_dict(),config=dict(target=case['target'],decoder='auto',p=.001),rows=[row],tasks={answer['task']:answer}));save(run/'tasks'/(answer['task']+'.json'),packet)
 bundle=root/'exports'/name
 if not bundle.exists():export_result(run,row['id'],bundle)
 t=time.perf_counter();cpu=time.process_time();verification=verify_bundle(bundle,20000000);save(root/'verification'/(name+'.json'),dict(result=verification,wall=time.perf_counter()-t,controller_cpu=time.process_time()-cpu))
 records.append(dict(name=name,circuit=digest(data),source=s,origin=case['origin'],target=case['target'],classification=case['classification'],resources=row['resources'],status=answer['result']['status'],bundle=str(bundle),verification=verification));save(root/'index_partial.json',dict(source=s,records=records));print('CONTROL',name,answer['result']['status'],verification.get('positive_certificate_verified'),flush=True)
save(root/'index.json',dict(source=s,records=records));save(root/'complete.json',dict(source=s,all_verified=all(r['verification'].get('positive_certificate_verified') for r in records)))