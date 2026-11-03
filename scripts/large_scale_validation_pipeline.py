"""Continue frozen validation after experiments finish, with durable stage receipts."""
import json,time,subprocess,sys,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
s=source_identity();root=Path('results/large_scale/validation_pipeline')/s;root.mkdir(parents=True,exist_ok=True)
stages=['large_scale_parallel_extended.py','large_scale_audit.py','large_scale_controls.py','large_scale_exports.py','large_scale_comparisons.py','large_scale_ler.py']
protocol=dict(source=s,stages={name:hashlib.sha256((Path('scripts')/name).read_bytes()).hexdigest() for name in stages},prerequisites=[str(Path('results/large_scale/campaigns')/s/'complete.json'),str(Path('results/large_scale/evaluation_policies')/s/'complete.json')],scope='No permanent global runtime limit. Validation starts after closed experimental campaigns and isolated evaluation-policy study. A failed stage stops the chain and retains its logs; pipeline completion is not the final scientific report or acceptance verdict.')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
save(root/'state.json',dict(source=s,status='WAITING_FOR_EXPERIMENTS',protocol=protocol))
while not all(Path(p).exists() for p in protocol['prerequisites']):
 if (root/'cancel.json').exists():save(root/'state.json',dict(source=s,status='CANCELLED_BEFORE_VALIDATION'));raise SystemExit(2)
 if (Path('results/large_scale/campaigns')/s/'resource_stop.json').exists():save(root/'state.json',dict(source=s,status='BLOCKED_BY_EXPERIMENT_RESOURCE_STOP'));raise SystemExit(2)
 time.sleep(5)
for stage,expected in protocol['stages'].items():
 assert source_identity()==s and hashlib.sha256((Path('scripts')/stage).read_bytes()).hexdigest()==expected,'Frozen validation source changed'
 if (root/'cancel.json').exists():save(root/'state.json',dict(source=s,status='CANCELLED_BETWEEN_STAGES',stage=stage));raise SystemExit(2)
 receipt=root/(stage+'.receipt.json')
 if receipt.exists() and json.loads(receipt.read_text())['returncode']==0:continue
 save(root/'state.json',dict(source=s,status='RUNNING',stage=stage));start=time.perf_counter();print('VALIDATION_START',stage,flush=True)
 log=root/(stage+'.log')
 with log.open('a',encoding='utf-8') as f:
  f.write('\nSTART '+str(time.time())+'\n');f.flush();process=subprocess.run([sys.executable,str(Path('scripts')/stage)],stdout=f,stderr=subprocess.STDOUT)
 save(receipt,dict(source=s,stage=stage,returncode=process.returncode,wall=time.perf_counter()-start,log=str(log)))
 if process.returncode:
  save(root/'state.json',dict(source=s,status='STAGE_FAILED',stage=stage,returncode=process.returncode,log=str(log)));raise SystemExit(process.returncode)
 print('VALIDATION_COMPLETE',stage,flush=True)
save(root/'state.json',dict(source=s,status='STAGES_COMPLETE_REPORT_AND_RELEASE_AUDIT_STILL_REQUIRED'));print('VALIDATION_STAGES_COMPLETE',flush=True)