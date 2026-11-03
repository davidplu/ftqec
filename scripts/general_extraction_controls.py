"""Current-source independent control recertification and exact public export."""
import json,time,hashlib
from pathlib import Path
from ftqec.results.artifacts import save,source_identity,digest
from ftqec.circuits.model import Circuit
from ftqec.circuits.identity import physical_identity
from ftqec.evaluation.resources import resources
from ftqec.execution.tasks import Task,batch
from ftqec.delivery.export import export_result
from ftqec.delivery.verify import verify_bundle
source=source_identity();root=Path('results/general_extraction/controls')/source;root.mkdir(parents=True,exist_ok=True)
old='2c806077ca35e80028b6f49add2dbd46390d1d400bb8f7b28452d3f3f038ae58';base=Path('results/competitive_export/delivery')/old/'exports'
choices=[('surface10_seed24',10,'graph'),('allocation_certify_1',10,'graph'),('allocation_certify_25',10,'graph'),('allocation_certify_50',10,'graph'),('repair_compressed',4,'mitm')]
small=Path('results/competitive_export/method_validation')/old/'positive_surface2.json'
smallc=json.loads(small.read_text())['tasks'][0]['circuit']
inputs=[(name,json.loads((base/name/'circuit.json').read_text()),target,method) for name,target,method in choices]
inputs.append(('physical_separator2',smallc,2,'decomposition'))
protocol=dict(source=source,cases=[(n,digest(c),t,m) for n,c,t,m in inputs],work=20000000,memory_mb=384,cpu=120,wall=240,workers=1,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Preserved scientific controls and a physical low-distance proof; not new code-only discoveries')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
start=time.perf_counter();cpu=time.process_time();index=[]
for label,data,target,method in inputs:
 c=Circuit.from_dict(data);task=Task(data,'certify',c.code.input_hash,{'p':.001},'auto',0,source,dict(target=target,proof_method=method,work=20000000,memory_mb=384,cpu_seconds=120,wall_seconds=240,proof_directory=str(root/'proofs'/label)))
 path=root/'certification'/(label+'.json')
 if path.exists():answer=json.loads(path.read_text())['answer']
 else:answer=batch([task],1)[0];save(path,dict(task=task.to_dict(),answer=answer))
 row=dict(id=physical_identity(c),circuit=data,resources=resources(c),certify=answer['result'],origin='preserved control',parent=None)
 run=root/'records'/label;save(run/'checkpoint.json',dict(source=source,code=c.code.to_dict(),config=dict(target=target,decoder='auto',p=.001),rows=[row],tasks={answer['task']:answer}))
 save(run/'tasks'/(answer['task']+'.json'),dict(task=task.to_dict(),answer=answer))
 bundle=root/'exports'/label
 if not bundle.exists():export_result(run,row['id'],bundle)
 verification=verify_bundle(bundle,20000000);save(root/'verification'/(label+'.json'),verification)
 index.append(dict(label=label,bundle=str(bundle),resources=row['resources'],result=answer['result']['status'],verification=verification));print('CONTROL',label,answer['result']['status'],verification.get('positive_certificate_verified'),flush=True)
save(root/'index.json',dict(source=source,records=index));save(root/'complete.json',dict(source=source,controller_cpu=time.process_time()-cpu,wall=time.perf_counter()-start))
