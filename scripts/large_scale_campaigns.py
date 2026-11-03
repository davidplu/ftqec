"""Frozen code-only large-population experiments; safe to resume the same epoch."""
import json,time,shutil,subprocess,sys,threading
from pathlib import Path
import psutil
from ftqec.optimization.engine import Config,optimize
from ftqec.codes.families import shor_product,hamming_hypergraph_product
from ftqec.results.artifacts import source_identity,save,digest
source=source_identity();root=Path('results/large_scale/campaigns')/source;root.mkdir(parents=True,exist_ok=True)
surface=json.loads(Path('benchmarks/distance_ladder/autonomous/surface_target3.json').read_text())['code']
codes=dict(surface3=surface,shor3=shor_product(3).to_dict(),hgp58=hamming_hypergraph_product().to_dict())
base=dict(storage='sqlite',window=64,promotion=8,workers=8,target=3,proof_work=200000,initial_shots=64,further_shots=256,finalists=8,memory_mb=256,task_cpu_seconds=60,task_wall_seconds=120)
jobs=[]
# Freeze all family settings before inspecting any final-family outcome.
for family in codes:
 for capacity,goal,seed in [(100,100,2001),(100,1000,2001),(1000,10000,2001),(10000,10000,2001),(100,1000,2002),(1000,1000,2002)]:
  jobs.append(dict(name=f'{family}_hybrid_p{capacity}_n{goal}_s{seed}',family=family,config=dict(base,population=capacity,candidate_goal=goal,seed=seed,strategy='hybrid')))
for family in codes:
 for strategy in ('random','witness','multifidelity','costhybrid'):
  for seed in (2001,2002):jobs.append(dict(name=f'{family}_{strategy}_p100_n100_s{seed}',family=family,config=dict(base,population=100,candidate_goal=100,seed=seed,strategy=strategy)))
protocol=dict(source=source,codes=codes,jobs=jobs,matched_cpu_checkpoints=[30,60,120,240,480,960,1920,3840,7680],matched_wall_checkpoints=[30,60,120,240,480,960,1920,3840],qualification='Finite candidate-count experiments; checkpoints are measurement conditions, not permanent runtime limits. Matched comparisons use completed frontier snapshots at or below the common actual compute threshold. No interpolation or equal-generation speed claim. Candidate-generation and frozen-pool allocation studies are separate.',driver_sha256=__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest(),hardware=dict(physical_cores=psutil.cpu_count(logical=False),logical_cores=psutil.cpu_count()),reference_inputs=False)
path=root/'protocol.json'
if path.exists():assert json.loads(path.read_text())==protocol
else:
 save(path,protocol);save(root/'protocol_hash.json',dict(sha256=digest(protocol)))
 for p in Path('src/ftqec').rglob('*.py'):
  q=root/'source'/p.relative_to('src');q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
# Never run a final epoch without a passing full-suite receipt for these exact source bytes.
receipts=list((Path('results/large_scale/tests')/source).glob('*/receipt.json'))
assert any(json.loads(p.read_text()).get('returncode')==0 for p in receipts),'Full suite has not passed for current source'
start=time.perf_counter();cpu=time.process_time()
for job in jobs:
 out=Path('results/populations')/source/'study'/job['name'];receipt=out/'experiment_receipt.json'
 if receipt.exists() and json.loads(receipt.read_text()).get('status')=='REQUESTED_CANDIDATE_GOAL_COMPLETED':continue
 if psutil.disk_usage('.').free<1536*1024**2:
  save(root/'resource_stop.json',dict(reason='DISK_SAFETY_RESERVE',job=job,available=psutil.disk_usage('.').free));print('DISK_SAFETY_RESERVE',flush=True);sys.exit(2)
 battery=psutil.sensors_battery()
 if battery and not battery.power_plugged and battery.percent<20:
  save(root/'resource_stop.json',dict(reason='LOW_BATTERY',job=job,battery=battery._asdict()));print('LOW_BATTERY',flush=True);sys.exit(2)
 print('START',job['name'],flush=True);t=time.perf_counter();c=time.process_time()
 stop=threading.Event();samples=[];process=psutil.Process()
 def monitor():
  while not stop.wait(.2):
   rss=0;active=0
   for child in process.children(recursive=True):
    try:rss+=child.memory_info().rss;active+=1
    except psutil.Error:pass
   samples.append(dict(time=time.perf_counter(),worker_rss=rss,controller_rss=process.memory_info().rss,active_processes=active))
 thread=threading.Thread(target=monitor,daemon=True);thread.start()
 try:state=optimize(codes[job['family']],out,Config(**job['config']))
 finally:stop.set();thread.join()
 save(out/'memory_samples.json',dict(source=source,samples=samples,scope='Direct 0.2-second samples of this controller and its child processes; brief peaks may be missed.'))
 save(receipt,dict(source=source,protocol_hash=digest(protocol),job=job,status=state['status'],distinct_exact=state['unique_circuits'],meaningful_structures=state['meaningful_circuits'],generated=state['generated'],controller_call_cpu=time.process_time()-c,elapsed_call_wall=time.perf_counter()-t,peak_sampled_worker_aggregate_rss=max((x['worker_rss'] for x in samples),default=0),peak_sampled_controller_rss=max((x['controller_rss'] for x in samples),default=0),scope='Outer optimizer invocation, including final persistence; do not add its nested session CPU again.'))
 print('FINISH',job['name'],state['status'],state['meaningful_circuits'],flush=True)
 if state['status'] in ('CANCELLED','RESOURCE_SAFETY_INTERVENTION'):sys.exit(2)
save(root/'complete.json',dict(source=source,wall=time.perf_counter()-start,controller_cpu=time.process_time()-cpu,scope='This driver invocation; nested optimizer receipts must not be added again.'))
print('CAMPAIGNS_COMPLETE',flush=True)
