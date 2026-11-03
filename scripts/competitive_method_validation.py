"""Physical low-distance validation of the separator backend, separately labelled."""
import json,time
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
from ftqec.circuits.model import Circuit
from ftqec.execution.tasks import Task,batch
from ftqec.certification.eligibility import assess,verify
source=source_identity();root=Path('results/competitive_export/method_validation')/source
state=json.loads((Path('results/competitive_export/release')/source/'cli_run/checkpoint.json').read_text())
row=next(r for r in state['rows'] if r.get('certify',{}).get('status')=='CERTIFIED');cc=Circuit.from_dict(row['circuit'])
save(root/'protocol.json',dict(source=source,target=2,selection='First positive actual surface_small circuit from installed CLI smoke',method='decomposition',scope='Low-distance physical backend validation; not graph-ineligible target5 milestone or matched timing comparison'))
e=assess(cc);v=verify(cc,e);assert v['verified'];save(root/'eligibility.json',dict(receipt=e,independent=v,circuit=cc.to_dict()))
task=Task(cc.to_dict(),'certify',cc.code.input_hash,{'p':.001},'matching',0,source,dict(target=2,work=20000000,proof_method='decomposition',memory_mb=512,cpu_seconds=180,wall_seconds=360))
answer=batch([task],1)[0];save(root/'positive_surface2.json',dict(source=source,tasks=[task.to_dict()],answers=[answer]))
r=answer['result'];print('PHYSICAL_SEPARATOR',r.get('status'),r.get('proof',{}).get('method'),flush=True)
if r.get('status')=='CERTIFIED' and r.get('proof',{}).get('method')=='component-separator-location-dp-1':
 t=Task(dict(circuit=cc.to_dict(),certificate=r),'verify',cc.code.input_hash,{'p':.001},'matching',0,source,dict(work=20000000,memory_mb=512,cpu_seconds=180,wall_seconds=360));a=batch([t],1)[0];save(root/'independent.json',dict(task=t.to_dict(),answer=a));assert a['result'].get('verified');print('PHYSICAL_SEPARATOR_REPLAYED',flush=True)

