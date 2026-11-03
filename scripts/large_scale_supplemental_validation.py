"""Run supplemental evidence checks after the frozen primary validation sequence."""
import json,time,subprocess,sys,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
s=source_identity();root=Path('results/large_scale/supplemental_validation')/s;root.mkdir(parents=True,exist_ok=True);upstream=Path('results/large_scale/validation_pipeline')/s/'state.json'
stages=['large_scale_window_counts.py','large_scale_provenance_audit.py','large_scale_signature_diversity.py','large_scale_preservation_check.py']
protocol=dict(source=s,stage_order=stages,drivers={n:hashlib.sha256((Path('scripts')/n).read_bytes()).hexdigest() for n in stages},upstream=str(upstream),scope='Supplemental source-bound verification, not new optimizer outcomes. Failures preserve logs and stop this sequence. Final interpretation and delivery fixes remain separate.')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
start=time.perf_counter();cpu=time.process_time();save(root/'state.json',dict(source=s,status='WAITING_FOR_PRIMARY_VALIDATION'))
while True:
 if (root/'cancel.json').exists():save(root/'state.json',dict(source=s,status='CANCELLED'));raise SystemExit(2)
 state=json.loads(upstream.read_text()) if upstream.exists() else {};status=state.get('status','WAITING')
 if status=='STAGES_COMPLETE_REPORT_AND_RELEASE_AUDIT_STILL_REQUIRED':break
 if status in ('STAGE_FAILED','BLOCKED_BY_EXPERIMENT_RESOURCE_STOP','CANCELLED_BEFORE_VALIDATION','CANCELLED_BETWEEN_STAGES'):
  save(root/'state.json',dict(source=s,status='BLOCKED_UPSTREAM',upstream_state=state));raise SystemExit(2)
 time.sleep(5)
waiting=time.perf_counter()-start
for name in stages:
 assert source_identity()==s and hashlib.sha256((Path('scripts')/name).read_bytes()).hexdigest()==protocol['drivers'][name]
 receipt=root/(name+'.receipt.json')
 if receipt.exists() and json.loads(receipt.read_text())['returncode']==0:continue
 if (root/'cancel.json').exists():save(root/'state.json',dict(source=s,status='CANCELLED',stage=name));raise SystemExit(2)
 save(root/'state.json',dict(source=s,status='RUNNING',stage=name));t=time.perf_counter();log=root/(name+'.log');print('SUPPLEMENTAL_START',name,flush=True)
 with log.open('a',encoding='utf-8') as f:
  f.write('\nSTART '+str(time.time())+'\n');f.flush();p=subprocess.run([sys.executable,str(Path('scripts')/name)],stdout=f,stderr=subprocess.STDOUT)
 save(receipt,dict(source=s,stage=name,returncode=p.returncode,stage_wall=time.perf_counter()-t,log=str(log)))
 if p.returncode:save(root/'state.json',dict(source=s,status='STAGE_FAILED',stage=name,returncode=p.returncode,log=str(log)));raise SystemExit(p.returncode)
 print('SUPPLEMENTAL_COMPLETE',name,flush=True)
save(root/'state.json',dict(source=s,status='COMPLETE_FINAL_REPORT_REQUIRED',waiting_wall=waiting,wrapper_controller_cpu=time.process_time()-cpu,scope='Waiting overlaps the experiment and primary-validation clocks; do not add waiting wall to their elapsed time. Wrapper CPU excludes child processes.'))