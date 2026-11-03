import json,time,subprocess,sys,os,hashlib
from pathlib import Path
import psutil
origin=Path('C:/Users/david/ftqec');root=origin/'results/certification_research/campaign_20261102'
clock=json.loads((root/'deadline_amendment.json').read_text());deadline=clock['deadline_unix']
def save(name,data):
 p=root/name;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix('.tmp');q.write_text(json.dumps(data,indent=2));q.replace(p)
def run(command,name):
 if time.time()>=deadline:save('state.json',dict(status='DEADLINE_REACHED'));return False
 if psutil.disk_usage('.').free<1536*1024**2:save('state.json',dict(status='DISK_RESERVE'));return False
 start=time.time();env=dict(os.environ,PYTHONPATH=str(Path('src').resolve()))
 with (root/(name+'.log')).open('a') as f:
  p=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT,env=env)
  save('state.json',dict(status='RUNNING',stage=name,pid=p.pid,deadline_unix=deadline))
  while p.poll() is None:
   save('heartbeat.json',dict(unix=time.time(),pid=p.pid,stage=name,deadline_unix=deadline))
   if time.time()>=deadline or (root/'cancel.json').exists():
    children=psutil.Process(p.pid).children(recursive=True)
    for child in reversed(children):
     try:child.kill()
     except psutil.Error:pass
    p.kill();p.wait();save(name+'_receipt.json',dict(status='CANCELLED',start=start,end=time.time()));return False
   time.sleep(1)
 save(name+'_receipt.json',dict(returncode=p.returncode,start=start,end=time.time()))
 return p.returncode==0
if not (root/'baseline_tests_receipt.json').exists() and not run([sys.executable,'-m','pytest','-q'],'baseline_tests'):save('state.json',dict(status='BASELINE_STOPPED'));raise SystemExit(1)
if not run([sys.executable,'scripts/certification_research_measure.py'],'matched_baseline'):save('state.json',dict(status='MEASUREMENT_STOPPED'));raise SystemExit(1)
save('state.json',dict(status='BASELINE_MEASUREMENTS_COMPLETE_AWAITING_RESEARCH_ANALYSIS',unix=time.time(),deadline_unix=deadline,active_workers=False))
