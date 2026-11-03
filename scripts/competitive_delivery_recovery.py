"""Fresh source-bound certification and public delivery after an export-only fix.
The discovery epoch is immutable; no prior source identity or result is rewritten.
"""
import json,time,hashlib,psutil,shutil
from pathlib import Path
from ftqec.results.artifacts import source_identity,source_records,digest,save
from ftqec.circuits.model import Circuit
from ftqec.circuits.identity import physical_identity
from ftqec.evaluation.resources import resources
from ftqec.execution.tasks import Task,batch
from ftqec.delivery.export import export_result
from ftqec.delivery.verify import verify_bundle
OLD='29bb185a85b2bb0f36e73bb52fe8a08a5f384a7239fb8e8220886ced4ac73b41'
def main():
 start=time.perf_counter();cpu=time.process_time();source=source_identity();assert source!=OLD
 root=Path('results/competitive_export/final')/OLD;out=Path('results/competitive_export/delivery')/source;out.mkdir(parents=True,exist_ok=True)
 oldrecords=json.loads((Path('results/competitive_export/source')/OLD/'identity.json').read_text())
 oldfiles=source_records(Path('results/competitive_export/source')/OLD/'ftqec');newfiles=source_records('src/ftqec');changed=[p for p in newfiles if oldfiles.get(p)!=newfiles[p]]
 assert set(changed)=={'delivery/export.py','delivery/verify.py'},changed
 protocol=dict(discovery_source=OLD,delivery_source=source,changed_files=changed,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),reason='Resume the preserved delivery after a guarded UNKNOWN lacked a certificate. Keep that exact UNKNOWN as certification_attempt and export its circuit/schedule without claiming a certificate. Original protocol, driver, task packets and failed checkpoint are retained.',workers=2,memory_mb=512,cpu_seconds=180,wall_seconds=360,work=20000000)
 if (out/'recovery_protocol.json').exists():assert json.loads((out/'recovery_protocol.json').read_text())==protocol
 else:save(out/'recovery_protocol.json',protocol)
 selections=[]
 for p in sorted((root/'optimizer').glob('*/checkpoint.json')):
  s=json.loads(p.read_text());rows=s['rows'];valid=[r for r in rows if r.get('certify',{}).get('status')=='CERTIFIED'];chosen=min(valid or rows,key=lambda r:r['resources']['QD']) if rows else None
  if chosen:selections.append((p.parent.name,chosen,s['code'],s['config'],str(p)))
 for folder in ('carry_forward','allocation','repair','controls'):
  for p in sorted((root/folder).glob('*.json')):
   packet=json.loads(p.read_text())
   for t,a in zip(packet.get('tasks',[]),packet.get('answers',[])):
    if t['tier']!='certify' or a['result'].get('status')!='CERTIFIED':continue
    cc=Circuit.from_dict(t['circuit']);r=dict(id=physical_identity(cc),circuit=cc.to_dict(),certify=a['result'],resources=resources(cc))
    selections.append((folder+'_'+p.stem,r,cc.code.to_dict(),dict(target=t['limits']['target'],p=.001,decoder=t['decoder'],seed=t['seed']),str(p)))
 followup=Path('results/competitive_export/target5_followup')/source
 assert (followup/'complete.json').exists()
 for path in sorted(followup.glob('*.json')):
  packet=json.loads(path.read_text())
  if 'answer' not in packet:continue
  cert=packet['answer']['result']
  if cert.get('status') not in ('CERTIFIED','INVALID'):continue
  t=packet['task'];cc=Circuit.from_dict(t['circuit']);auditpath=out/'followup_replay'/(path.stem+'.json')
  if not auditpath.exists():
   vt=Task(dict(circuit=cc.to_dict(),certificate=cert),'verify',cc.code.input_hash,{'p':.001},'matching',0,source,dict(work=20000000,memory_mb=512,cpu_seconds=180,wall_seconds=360));va=batch([vt],1)[0];save(auditpath,dict(task=vt.to_dict(),answer=va));assert va['result'].get('verified'),va
  if cert['status']=='CERTIFIED':selections.append(('target5_'+path.stem,dict(id=physical_identity(cc),circuit=cc.to_dict(),certify=cert,resources=resources(cc)),cc.code.to_dict(),dict(target=5,p=.001,decoder='matching',seed=0),str(path)))
 index=[]
 for label,original,code,cfg,origin in selections:
  run=out/'records'/label;cc=Circuit.from_dict(original['circuit']);target=cfg['target'];packetpath=out/'certification'/(label+'.json')
  task=Task(cc.to_dict(),'certify',cc.code.input_hash,{'p':.001},cfg.get('decoder','matching'),cfg.get('seed',0),source,dict(target=target,work=20000000,proof_method='auto',memory_mb=512,cpu_seconds=180,wall_seconds=360,proof_directory=str(out/'proofs'/label)))
  if packetpath.exists():packet=json.loads(packetpath.read_text());assert packet['task']==task.to_dict();answer=packet['answer']
  else:answer=batch([task],1)[0];save(packetpath,dict(task=task.to_dict(),answer=answer))
  cert=answer['result']
  if original.get('certify',{}).get('status')=='CERTIFIED':assert cert.get('status')=='CERTIFIED',(label,cert)
  row=dict(id=physical_identity(cc),circuit=cc.to_dict(),resources=resources(cc),certify=cert,genome=original.get('genome'),parent=original.get('parent'),original_discovery=dict(source=original.get('certify',{}).get('source',OLD),record=original,origin=origin,sha256=hashlib.sha256(Path(origin).read_bytes()).hexdigest()),construction=dict(method='fresh_certification_of_unchanged_discovered_circuit',not_new_discovery=True))
  if cert.get('circuit')!=digest(cc.to_dict()) or cert.get('source')!=source:
   row.pop('certify');row['certification_attempt']=cert;row['certificate_availability']='No completed bound certificate; evaluation remains UNKNOWN'
   if (run/'checkpoint.json').exists() and not (run/'checkpoint_before_guard_receipt_fix.json').exists():shutil.copyfile(run/'checkpoint.json',run/'checkpoint_before_guard_receipt_fix.json')
  row['matched_ler']=[json.loads(p.read_text()) for p in (root/'ler').glob('*.json') if json.loads(p.read_text())['tasks'][0]['circuit']==cc.to_dict()]
  save(run/'tasks'/(answer['task']+'.json'),dict(task=task.to_dict(),answer=answer));save(run/'checkpoint.json',dict(source=source,code=code,config=cfg,rows=[row],tasks={answer['task']:answer},origin=origin))
  bundle=out/'exports'/label
  if not bundle.exists():export_result(run,row['id'],bundle)
  v=verify_bundle(bundle,20000000)
  if cert.get('status')=='CERTIFIED':assert v['positive_certificate_verified'],(label,v)
  save(out/'verification'/(label+'.json'),v);index.append(dict(label=label,run=str(run),bundle=str(bundle),circuit=digest(cc.to_dict()),candidate_id=row['id'],source=source,discovery_source=OLD,status=cert.get('status'),verification=v,resources=resources(cc)));print('DELIVERED',label,cert.get('status'),flush=True)
 save(out/'index.json',dict(source=source,discovery_source=OLD,records=index));save(out/'complete.json',dict(source=source,controller_cpu=time.process_time()-cpu,peak_controller_working_set=psutil.Process().memory_info().peak_wset,wall=time.perf_counter()-start,records=len(index)))
 save(root/'completion_extension.json',dict(discovery_source=OLD,delivery_source=source,completion=str(out/'complete.json'),qualification='Original driver encountered an export identity integration error; immutable research results audited under original source and delivered with fresh certification under the export-only fix.'))
 print('DELIVERY_COMPLETE',source,flush=True)
if __name__=='__main__':main()
