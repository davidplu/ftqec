"""Bounded proof continuation; retain original UNKNOWN optimizer rows unchanged."""
import json,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.execution.tasks import Task,batch
from ftqec.certification.exact import verify
from ftqec.circuits.model import Circuit
from ftqec.codes.input import load
source=source_identity();base=Path('results/general_competitive/final')/source
state=json.loads((base/'optimizer/shor_product4/checkpoint.json').read_text())
rows=[r for r in state['rows'] if r.get('certify',{}).get('status')=='UNKNOWN']
root=Path('results/general_competitive/proof_continuation')/source;root.mkdir(parents=True,exist_ok=True)
protocol=dict(source=source,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),selection='All target-four UNKNOWN candidates from the completed prospective Shor-product population; original results remain unchanged',ids=[r['id'] for r in rows],work=10000000,cpu_seconds=300,memory_mb=512,workers=2,qualification='Separate bounded proof continuation, not retrospective success in the original budget')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
for row in rows:
 path=root/(row['id']+'.json')
 if path.exists():continue
 c=Circuit.from_dict(row['circuit']);task=Task(row['circuit'],'certify',load(state['code']).identity,dict(p=.001),'auto',0,source,dict(target=4,work=10000000,proof_method='mitm',memory_mb=512,cpu_seconds=300,wall_seconds=600,proof_directory=str((base/'optimizer/shor_product4/proofs'/row['id']).resolve())))
 answer=batch([task],workers=2,memory_mb=512)[0];cert=answer['result']
 replay=verify(c,cert,10000000) if 'proof' in cert else dict(verified=False,reason=cert.get('reason'))
 save(path,dict(source=source,prior_status='UNKNOWN',row_id=row['id'],circuit=c.to_dict(),resources=row['resources'],task=task.to_dict(),answer=answer,independent_replay=replay))
 print('CONTINUATION',row['id'],cert['status'],cert.get('lower_bound'),answer['cpu'],flush=True)
save(root/'complete.json',dict(source=source,protocol=digest(protocol)))
