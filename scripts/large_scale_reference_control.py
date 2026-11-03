"""Separately certify a documented reference; never pass it into optimization."""
import json,time,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.architectures.references import rotated_surface
from ftqec.codes.input import load
from ftqec.circuits.identity import physical_identity
from ftqec.execution.tasks import Task,batch
from ftqec.evaluation.resources import resources
from ftqec.delivery.export import export_result
from ftqec.delivery.verify import verify_bundle
from ftqec.screening.structural import check
s=source_identity();root=Path('results/large_scale/references')/s/'surface3_noiseless_normalized';root.mkdir(parents=True,exist_ok=True);inp,c=rotated_surface(3,rounds=1);structural=check(c);protocol_path=Path('results/large_scale/campaigns')/s/'protocol.json';study=load(json.loads(protocol_path.read_text())['codes']['surface3'])
def space(rows):
 basis={}
 for value in rows:
  for pivot in sorted(basis,reverse=True):
   if value>>pivot&1:value^=basis[pivot]
  if value:
   pivot=value.bit_length()-1
   for old in basis:
    if basis[old]>>pivot&1:basis[old]^=value
   basis[pivot]=value
 return tuple(basis[p] for p in sorted(basis))
assert inp.code.n==study.code.n and space(g.packed for g in inp.code.generators)==space(g.packed for g in study.code.generators)
protocol=dict(structural=structural,source=s,circuit=digest(c.to_dict()),reference_origin=c.experiment['reference_origin'],target=3,optimizer_protocol=str(protocol_path),same_data_wire_stabilizer_span=True,classification='documented reference, not autonomous discovery or optimizer seed',driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
task=Task(c.to_dict(),'certify',c.code.input_hash,dict(p=.001),'auto',0,s,dict(target=3,work=20000000,memory_mb=384,cpu_seconds=120,wall_seconds=240,proof_directory=str(root/'proofs')))
if (root/'task.json').exists():packet=json.loads((root/'task.json').read_text());assert packet['task']==task.to_dict()
else:packet=dict(task=task.to_dict(),answer=batch([task],1,memory_mb=384)[0]);save(root/'task.json',packet)
answer=packet['answer'];row=dict(id=physical_identity(c),circuit=c.to_dict(),resources=resources(c),certify=answer['result'],origin=protocol['classification'],parent=None);run=root/'record';save(run/'checkpoint.json',dict(source=s,code=inp.to_dict(),config=dict(target=3,decoder='auto',p=.001),rows=[row],tasks={answer['task']:answer}));save(run/'tasks'/(answer['task']+'.json'),packet)
bundle=root/'bundle'
if not bundle.exists():export_result(run,row['id'],bundle)
t=time.perf_counter();cpu=time.process_time();verification=verify_bundle(bundle,20000000);save(root/'verification.json',dict(result=verification,wall=time.perf_counter()-t,controller_cpu=time.process_time()-cpu));save(root/'summary.json',dict(source=s,circuit=digest(c.to_dict()),resources=row['resources'],status=answer['result']['status'],verification=verification,bundle=str(bundle),classification=protocol['classification'],same_data_wire_stabilizer_span=True));print('REFERENCE',row['resources'],answer['result']['status'],verification.get('positive_certificate_verified'),flush=True)