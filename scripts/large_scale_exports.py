"""Export and independently verify deterministic adopted population representatives."""
import json,time,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.optimization.store import PopulationStore
from ftqec.circuits.model import Circuit
from ftqec.execution.tasks import Task,batch
from ftqec.delivery.export import export_result
from ftqec.delivery.verify import verify_bundle
s=source_identity();audit=Path('results/large_scale/audit')/s/'summary.json';summary=json.loads(audit.read_text());root=Path('results/exports/large_scale')/s;root.mkdir(parents=True,exist_ok=True)
protocol=dict(source=s,audit_sha256=hashlib.sha256(audit.read_bytes()).hexdigest(),representatives=summary['export_representatives'],driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),work=20000000,memory_mb=384,cpu_seconds=120,wall_seconds=240,scope='Independent fresh proof replay and full circuit/schedule reconstruction of every adopted resource tuple. Equal-resource physical alternatives remain in the population database.')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
records=[]
for point in protocol['representatives']:
 key=point['circuit'];done=root/'receipts'/(key+'.json')
 if done.exists():records.append(json.loads(done.read_text()));continue
 with PopulationStore(Path(point['run'])/'population.sqlite',readonly=True) as db:row=db.get(point['id'])
 c=Circuit.from_dict(row['circuit']);assert digest(c.to_dict())==key and row['certify']['status']=='CERTIFIED'
 task=Task(dict(circuit=c.to_dict(),certificate=row['certify']),'verify',c.code.input_hash,dict(p=.001),'auto',0,s,dict(work=20000000,memory_mb=384,cpu_seconds=120,wall_seconds=240))
 packet_path=root/'proof_replay'/(key+'.json')
 if packet_path.exists():packet=json.loads(packet_path.read_text());assert packet['task']==task.to_dict()
 else:
  answer=batch([task],1,memory_mb=384)[0];packet=dict(task=task.to_dict(),answer=answer);save(packet_path,packet)
 if not packet['answer']['result'].get('verified'):
  save(root/'blocked.json',dict(point=point,packet=str(packet_path),reason='Independent proof replay did not complete positively'));raise RuntimeError('Adopted proof replay not verified')
 bundle=root/'bundles'/key
 if not bundle.exists():export_result(point['run'],point['id'],bundle,'bundle')
 t=time.perf_counter();cpu=time.process_time();verification=verify_bundle(bundle,20000000)
 save(root/'bundle_replay'/(key+'.json'),dict(result=verification,wall=time.perf_counter()-t,controller_cpu=time.process_time()-cpu))
 assert all(verification.get(k) for k in ('positive_certificate_verified','reconstruction_verified','resource_recomputation_verified')),verification
 record=dict(point,bundle=str(bundle),independent_proof_replay=str(packet_path),verification=verification);save(done,record);records.append(record);print('EXPORTED_VERIFIED',point['family'],key,flush=True)
save(root/'index.json',dict(source=s,records=records));save(root/'complete.json',dict(source=s,count=len(records)))