"""Independent replays of every reported final-epoch proof and physical witness."""
import sys,json,time,psutil
from pathlib import Path
old='29bb185a85b2bb0f36e73bb52fe8a08a5f384a7239fb8e8220886ced4ac73b41'
sys.path.insert(0,str((Path('results/competitive_export/source')/old).resolve()))
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.circuits.model import Circuit
from ftqec.execution.tasks import Task,batch
from ftqec.certification.exact import verify_witness
assert source_identity()==old
root=Path('results/competitive_export/final')/old;out=root/'independent_extension';out.mkdir(exist_ok=True)
items={};witnesses={};start=time.perf_counter();cpu=time.process_time()
for path in (root/'optimizer').glob('*/checkpoint.json'):
 s=json.loads(path.read_text())
 for r in s['rows']:
  c=r['circuit'];cert=r.get('certify',{})
  if cert.get('status') in ('CERTIFIED','INVALID'):items[digest(dict(circuit=c,certificate=cert))]=(c,cert,str(path))
  for field in ('screen','certify'):
   for name in ('witness','upper_witness'):
    w=r.get(field,{}).get(name)
    if w:witnesses[digest(dict(circuit=c,witness=w))]=(c,w,str(path))
for folder in ('carry_forward','allocation','repair','controls','methods'):
 for path in (root/folder).glob('*.json'):
  packet=json.loads(path.read_text())
  for t,a in zip(packet.get('tasks',[]),packet.get('answers',[])):
   cert=a['result']
   if t['tier']=='certify' and cert.get('status') in ('CERTIFIED','INVALID'):items[digest(dict(circuit=t['circuit'],certificate=cert))]=(t['circuit'],cert,str(path))
for key,(c,cert,origin) in items.items():
 path=out/(key+'.json')
 if path.exists():continue
 task=Task(dict(circuit=c,certificate=cert),'verify',Circuit.from_dict(c).code.input_hash,{'p':.001},'matching',0,old,dict(work=20000000,memory_mb=512,cpu_seconds=180,wall_seconds=360))
 a=batch([task],1)[0];save(path,dict(origin=origin,task=task.to_dict(),answer=a));assert a['result'].get('verified'),a
for key,(c,w,origin) in witnesses.items():
 v=verify_witness(Circuit.from_dict(c),w);assert v['verified'];save(out/('witness_'+key+'.json'),dict(origin=origin,circuit=digest(c),witness=w,replay=v))
save(out/'complete.json',dict(source=old,certificates=len(items),physical_witnesses=len(witnesses),controller_cpu=time.process_time()-cpu,peak_controller_working_set=psutil.Process().memory_info().peak_wset,wall=time.perf_counter()-start));print('EPOCH_AUDIT_COMPLETE',len(items),len(witnesses),flush=True)
