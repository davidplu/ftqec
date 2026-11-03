"""Prospective repeated serial/parallel cheap-stage comparison on identical code-only inputs."""
import json,time,threading
from pathlib import Path
import psutil
from ftqec.execution.tasks import Task,batch
from ftqec.architectures.population import sample
from ftqec.codes.input import load
from ftqec.results.artifacts import source_identity,save,digest
s=source_identity();root=Path('results/compute')/s/'parallel_scaling_extended';root.mkdir(parents=True,exist_ok=True)
code=load(json.loads(Path('benchmarks/distance_ladder/autonomous/surface_target3.json').read_text())['code'])
tasks=[Task(dict(code_input=code.to_dict(),genome=sample(code,3100+i,3).to_dict()),'construct_screen',code.identity,dict(p=.001),'one_mechanism_lookup',3100+i,s,dict(target=3,work=200000,memory_mb=256,cpu_seconds=60,wall_seconds=120)) for i in range(32)]
orders=[[1,2,4,8,12,16],[16,12,8,4,2,1],[4,1,12,2,16,8]]
protocol=dict(driver_sha256=__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest(),source=s,tasks=[t.to_dict() for t in tasks],worker_orders=orders,memory_mb=256,physical_cores=psutil.cpu_count(logical=False),logical_cores=psutil.cpu_count(),scope='Identical fresh supervised tasks. Repeated blocked worker-count comparison; no cache reuse. Aggregate RSS is directly sampled, not summed worker maxima.')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
rows=[];expected=None
for rep,order in enumerate(orders):
 for workers in order:
  path=root/f'r{rep}_w{workers}.json'
  if path.exists():row=json.loads(path.read_text());rows.append(row);expected=expected or row['scientific_output'];continue
  stop=threading.Event();samples=[];controller=psutil.Process()
  def monitor():
   while not stop.wait(.02):
    processes=controller.children(recursive=True);rss=0;active=0
    for p in processes:
     try:rss+=p.memory_info().rss;active+=1
     except psutil.Error:pass
    samples.append(dict(time=time.perf_counter(),aggregate_child_rss=rss,active_processes=active,controller_rss=controller.memory_info().rss))
  thread=threading.Thread(target=monitor,daemon=True);thread.start();t=time.perf_counter();c=time.process_time()
  try:answers=batch(tasks,workers,memory_mb=256)
  finally:stop.set();thread.join()
  elapsed=time.perf_counter()-t;cost=time.process_time()-c
  outputs=[digest({k:a['result'].get(k) for k in ('status','circuit','structural','resources','screen')}) for a in answers]
  expected=expected or outputs;assert outputs==expected,'Scientific output changed across worker counts'
  intervals=[(a.get('dispatch_monotonic'),a.get('completion_monotonic')) for a in answers];points=sorted([(a,1) for a,b in intervals if a is not None]+[(b,-1) for a,b in intervals if b is not None]);peak=active=0
  for _,d in points:active+=d;peak=max(peak,active)
  row=dict(rep=rep,requested_workers=workers,observed_peak_workers=peak,controller_cpu=cost,worker_cpu=sum(a['cpu'] for a in answers),elapsed_wall=elapsed,peak_worker_rss=max(a.get('peak_rss',a['rss']) for a in answers),peak_aggregate_rss=max((x['aggregate_child_rss'] for x in samples),default=0),worker_utilization=sum(a['cpu'] for a in answers)/(max(1,peak)*elapsed),queue_wall=sum(a.get('queue_wall',0) for a in answers),answers=answers,samples=samples,scientific_output=outputs,output_equivalent=True)
  save(path,row);rows.append(row);print('PARALLEL',rep,workers,round(elapsed,3),flush=True)
for row in rows:
 base=next(x for x in rows if x['rep']==row['rep'] and x['requested_workers']==1);row['speedup_vs_same_block_serial']=base['elapsed_wall']/row['elapsed_wall']
save(root/'summary.json',dict(source=s,rows=[{k:v for k,v in r.items() if k not in ('answers','samples','scientific_output')} for r in rows]));print('PARALLEL_COMPLETE',flush=True)
