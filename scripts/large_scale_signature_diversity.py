"""Full-fault signature diagnostics on a prospectively selected diversity sample."""
import sys,json,time,hashlib,collections,subprocess,os,site
from pathlib import Path
import psutil
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.circuits.model import Circuit
from ftqec.optimization.store import PopulationStore
from ftqec.execution.tasks import completed_process_cpu
from ftqec.execution.clocks import active_time

if len(sys.argv)>1 and sys.argv[1]=='--worker':
 from ftqec.faults.signatures import signatures
 task=json.loads(Path(sys.argv[2]).read_text());assert task['source']==source_identity();c=Circuit.from_dict(task['circuit']);start=time.perf_counter();cpu=time.process_time();inventory=signatures(c);locations=collections.Counter(x.fault.location for x in inventory)
 payload=[dict(fault=x.fault.to_dict(),detectors=x.detectors,flags=x.flags,logical=x.logical,data=x.data) for x in inventory]
 hist=lambda fn:dict(collections.Counter(str(fn(x)) for x in inventory))
 save(sys.argv[3],dict(source=source_identity(),circuit=digest(c.to_dict()),status='MEASURED',inventory_count=len(inventory),inventory_hash=digest(payload),locations=len(locations),alternatives_per_location=dict(collections.Counter(str(n) for n in locations.values())),detector_weights=hist(lambda x:x.detectors.bit_count()),logical_weights=hist(lambda x:x.logical.bit_count()),flag_weights=hist(lambda x:x.flags.bit_count()),null_effects=sum(x.detectors==0 and x.logical==0 for x in inventory),correlated_nonidentity_alternatives=sum(sum(p!='I' for p in x.fault.label)>1 for x in inventory),body_cpu=time.process_time()-cpu,body_wall=time.perf_counter()-start,pid=os.getpid(),rss=psutil.Process().memory_info().rss,scope='Complete unchanged operation-local inventory of this sampled circuit. Raw detector weight is not a graph-ineligibility proof. Same-location alternatives remain mutually exclusive; histogramming does not replace their joint semantics.'))
 raise SystemExit(0)

s=source_identity();root=Path('results/large_scale/signature_diversity')/s;root.mkdir(parents=True,exist_ok=True)
rules=dict(source=s,selection='Two smallest distinct physical circuit hashes per extraction architecture family within each input-code family, over the full closed population matrix. No screening, certification, or simulation outcome used.',memory_mb=384,cpu_seconds=60,active_wall_seconds=120,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Descriptive sampled diversity, not a population-wide distribution estimate or new certification result.')
if (root/'selection_protocol.json').exists():assert json.loads((root/'selection_protocol.json').read_text())==rules
else:save(root/'selection_protocol.json',rules)
if '--freeze-only' in sys.argv:print('SIGNATURE_SAMPLE_RULES_FROZEN');raise SystemExit(0)
audit=json.loads((Path('results/large_scale/audit')/s/'summary.json').read_text());groups={}
for run in audit['runs']:
 family=run['job']['family'];path=Path('results/populations')/s/'study'/run['job']['name']
 with PopulationStore(path/'population.sqlite',readonly=True) as db:
  for row in db.summaries():
   key=(family,row['genome']['family']);group=groups.setdefault(key,{})
   if row['id'] in group:continue
   if len(group)<2 or row['id']<max(group):
    group[row['id']]=dict(id=row['id'],family=family,architecture=key[1],run=str(path))
    if len(group)>2:del group[max(group)]
cases=[row for key in sorted(groups) for row in groups[key].values()];protocol=dict(rules,cases=cases)
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
results=[]
for case in cases:
 cid=case['id'];receipt=root/'receipts'/(cid+'.json')
 if receipt.exists():results.append(json.loads(receipt.read_text()));continue
 if psutil.virtual_memory().available<896*1024**2:raise MemoryError('Preserved worker admission reserve')
 with PopulationStore(Path(case['run'])/'population.sqlite',readonly=True) as db:data=db.get(cid)['circuit']
 task=root/'tasks'/(cid+'.json');answer=root/'answers'/(cid+'.json');save(task,dict(source=s,circuit=data));start=time.perf_counter();active_start=active_time();peak=0;used=0.;reason=None
 bootstrap='import sys,site,runpy;sys.prefix='+repr(sys.prefix)+';sys.exec_prefix='+repr(sys.exec_prefix)+';sys.path[: ]='+repr(sys.path)+';[site.addsitedir(p) for p in '+repr(site.getsitepackages())+'];runpy.run_path('+repr(str(Path(__file__).resolve()))+',run_name="__main__")'
 executable=getattr(sys,'_base_executable',sys.executable)
 with (root/(cid+'.log')).open('a',encoding='utf-8') as log:
  process=subprocess.Popen([executable,'-S','-c',bootstrap,'--worker',str(task.resolve()),str(answer.resolve())],stdout=log,stderr=log);monitor=psutil.Process(process.pid)
  while process.poll() is None:
   try:peak=max(peak,monitor.memory_info().rss);times=monitor.cpu_times();used=times.user+times.system
   except psutil.NoSuchProcess:break
   if peak>384*1024**2:reason='MEMORY_LIMIT'
   if used>60:reason='CPU_LIMIT'
   if active_time()-active_start>120:reason='ACTIVE_WALL_LIMIT'
   if (root/'cancel.json').exists():reason='CANCELLED'
   if reason:process.kill();break
   time.sleep(.02)
  process.wait();used,cpu_scope=completed_process_cpu(process,used)
 result=json.loads(answer.read_text()) if answer.exists() and not reason and process.returncode==0 else dict(status='UNKNOWN',reason=reason or 'WORKER_ERROR')
 if result['status']=='MEASURED':assert result['pid']==process.pid and result['circuit']==digest(data)
 row=dict(case,result=result,cpu=used,cpu_scope=cpu_scope,wall=time.perf_counter()-start,peak_rss=max(peak,result.get('rss',0)));save(receipt,row);results.append(row);print('SIGNATURE_SAMPLE',case['family'],case['architecture'],result['status'],flush=True)
 if reason=='CANCELLED':raise SystemExit(2)
save(root/'summary.json',dict(source=s,protocol=protocol,records=results));print('SIGNATURE_DIVERSITY_COMPLETE',flush=True)