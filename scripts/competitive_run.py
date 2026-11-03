"""Observe the real campaign interpreter; include full controller CPU and wall."""
import sys,site,subprocess,time,hashlib
from pathlib import Path
import psutil
from ftqec.results.artifacts import source_identity,save
from ftqec.execution.tasks import completed_process_cpu
from ftqec.execution.clocks import active_time
root=Path('results/competitive_export/final')/source_identity();root.mkdir(parents=True,exist_ok=True)
script=Path('scripts/competitive_campaign.py').resolve()
bootstrap='import sys,site,runpy;sys.prefix='+repr(sys.prefix)+';sys.exec_prefix='+repr(sys.exec_prefix)+';sys.path[: ]='+repr(sys.path)+';[site.addsitedir(p) for p in '+repr(site.getsitepackages())+'];runpy.run_path('+repr(str(script))+',run_name="__main__")'
index=len(list(root.glob('driver_session_*.json')));log=root/f'driver_session_{index}.log'
start=time.perf_counter();active=active_time();peak=used=0
with log.open('w',encoding='utf-8') as output:
 process=subprocess.Popen([sys._base_executable,'-S','-c',bootstrap],stdout=output,stderr=subprocess.STDOUT)
 monitor=psutil.Process(process.pid);last=''
 while process.poll() is None:
  try:
   info=monitor.memory_info();peak=max(peak,getattr(info,'peak_wset',info.rss));t=monitor.cpu_times();used=t.user+t.system
  except psutil.NoSuchProcess:break
  text=log.read_text(encoding='utf-8')
  if text!=last:print(text[len(last):],end='',flush=True);last=text
  time.sleep(.5)
 process.wait();cpu,scope=completed_process_cpu(process,used)
text=log.read_text(encoding='utf-8')
if text!=last:print(text[len(last):],end='',flush=True)
save(root/f'driver_session_{index}.json',dict(source=source_identity(),driver_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),pid=process.pid,returncode=process.returncode,cpu=cpu,cpu_scope=scope,wall=time.perf_counter()-start,active_wall=active_time()-active,peak_working_set=peak,qualification='Controller costs include construction, persistence, admission, and final independent audit; evaluator process costs are recorded separately and must be added once'))
sys.exit(process.returncode)
