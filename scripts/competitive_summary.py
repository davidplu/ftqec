"""Derive comparison tables from immutable completed campaign packets."""
import json,math,hashlib,subprocess
from pathlib import Path
from scipy.stats import beta
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.circuits.model import Circuit
from ftqec.circuits.identity import physical_identity
from ftqec.faults.signatures import enumerate_faults
from ftqec.evaluation.resources import resources
from ftqec.optimization.selection import pareto
source=source_identity();experiment_source='29bb185a85b2bb0f36e73bb52fe8a08a5f384a7239fb8e8220886ced4ac73b41';root=Path('results/competitive_export/final')/experiment_source;delivery=Path('results/competitive_export/delivery')/source
read=lambda p:json.loads(Path(p).read_text())
assert (root/'completion_extension.json').exists() and (delivery/'complete.json').exists() and (root/'independent_extension/complete.json').exists()
states={p.parent.name:read(p) for p in (root/'optimizer').glob('*/checkpoint.json')}
alltasks={};families=[];front=[]
for name,s in states.items():
 for key,a in s['tasks'].items():alltasks.setdefault(key,a)
 rows=s['rows'];valid=[r for r in rows if r.get('certify',{}).get('status')=='CERTIFIED']
 for r in rows:
  metric=resources(Circuit.from_dict(r['circuit']));assert all(r['resources'][k]==v for k,v in metric.items());assert physical_identity(Circuit.from_dict(r['circuit']))==r['id']
 if s['config']['target']==10:
  for r in valid:front.append(dict(r,origin=name,source=s['source'],reference=False))
 n=rows[0]['circuit']['code']['n'] if rows else None
 best=min(valid,key=lambda r:r['resources']['QD']) if valid else None
 families.append(dict(name=name,target=s['config']['target'],n=n,generated=sum(g['generated'] for g in s.get('generation_compute',[])),compiled=sum(g['compiled'] for g in s.get('generation_compute',[])),distinct=len(rows),simulated=sum(any(b.get('shots',0)>0 for b in r.get('simulation_batches',[])) for r in rows),simulation_attempts=sum(bool(r.get('simulation_batches')) for r in rows),certified=len(valid),harmful=sum(r.get('certify',{}).get('status')=='INVALID' or r.get('screen',{}).get('status')=='FAULT_INVALID' for r in rows),unknown=sum(r.get('certify',{}).get('status')=='UNKNOWN' for r in rows),construction_unknown=len(s.get('construction_unknown',[])),best=best['resources'] if best else None,cpu=sum(a['cpu'] for a in s['tasks'].values())+sum(v['cpu'] for v in s['sessions']),wall=sum(v['wall'] for v in s['sessions']),evidence=str(root/'optimizer'/name/'checkpoint.json')))
family_frontiers={}
for name,state in states.items():
 if name.startswith('control_'):continue
 family=name.split('_seed')[0]
 family_frontiers.setdefault(family,[]).extend(dict(row,origin=name,source=state['source']) for row in state['rows'] if row.get('certify',{}).get('status')=='CERTIFIED')
family_frontiers={family:pareto(rows) for family,rows in family_frontiers.items()}
save(Path('results/cross_family/competitive_export')/source/'frontiers.json',dict(source=source,discovery_source=experiment_source,frontiers=family_frontiers,qualification='Certified frontiers across the declared seeds; duplicates and historical rows remain in original checkpoints'))
methods=[];aux=[]
for folder in ('carry_forward','allocation','repair','controls','methods','ler','audit'):
 for p in sorted((root/folder).glob('*.json')):
  packet=read(p)
  for t,a in zip(packet.get('tasks',[]),packet.get('answers',[])):
   alltasks.setdefault(a['task'],a);r=a['result']
   if folder=='methods':
    methods.append(dict(family=p.stem,fault_alternatives=sum(1 for _ in enumerate_faults(Circuit.from_dict(t['circuit']))),detectors=len(t['circuit']['detectors'])+len(t['circuit']['code']['generators']),requested=t['limits']['proof_method'],target=t['limits']['target'],status=r.get('status'),lower_bound=r.get('lower_bound'),upper_bound=r.get('upper_bound'),method=r.get('proof',{}).get('method'),independent=r.get('independent',{}),cpu=a['cpu'],wall=a['wall'],peak=a.get('peak_rss',a['rss']),evidence=str(p),progress=r.get('progress',[]),proof=r.get('proof',{})))
   if folder in ('carry_forward','allocation','repair','controls') and t['tier']=='certify':
    cc=Circuit.from_dict(t['circuit']);metric=resources(cc);row=dict(id=digest(cc.to_dict()),circuit=cc.to_dict(),resources=metric,certify=r,origin=folder+'_'+p.stem,source=packet['source'],reference=folder=='controls',evidence=str(p));aux.append(row)
    if r.get('status')=='CERTIFIED' and t['limits']['target']==10:front.append(row)
fronts=dict(source=source,discovery=pareto([r for r in front if not r['reference']]),all_known_including_reference=pareto(front),archive=front)
save(Path('results/pareto/competitive_export')/(source+'.json'),fronts)
ler=[]
for p in sorted((root/'ler').glob('*.json')):
 packet=read(p);answers=packet['answers'];ok=[a for a in answers if a['result'].get('shots')]
 if len(ok)!=len(answers):ler.append(dict(name=p.stem,status='INCOMPLETE',evidence=str(p)));continue
 failures=sum(a['result']['failures'] for a in ok);shots=sum(a['result']['shots'] for a in ok);rate=failures/shots
 # Exact binomial Clopper-Pearson intervals with Bonferroni family-wise coverage.
 alpha=.05/3;lo=0. if failures==0 else float(beta.ppf(alpha/2,failures,shots-failures+1));hi=1. if failures==shots else float(beta.ppf(1-alpha/2,failures+1,shots-failures))
 ler.append(dict(name=p.stem,status='COMPLETE',failures=failures,shots=shots,rate=rate,simultaneous_interval=[lo,hi],decoder=ok[0]['result']['decoder'],p=.01,cpu=sum(a['cpu'] for a in ok),evidence=str(p)))
comparisons=[]
for a in ler:
 for b in ler:
  if a.get('status')==b.get('status')=='COMPLETE' and a['name']<b['name']:
   lo,hi=sorted((a,b),key=lambda r:r['rate']);comparisons.append(dict(lower=lo['name'],higher=hi['name'],resolved=lo['simultaneous_interval'][1]<hi['simultaneous_interval'][0]))
controls={k:s for k,s in states.items() if k.startswith('control_')};common=min(sum(t['cpu'] for t in s['tasks'].values())+sum(v['cpu'] for v in s['sessions']) for s in controls.values());matched=[]
for name,s in controls.items():
 eligible=[h for h in s['frontier_history'] if h['coordinator_cpu']+h['cumulative_sampled_worker_cpu']<=common]
 h=max(eligible,key=lambda h:h['generation']) if eligible else None
 ids=h['certified_pareto'] if h else [];rows=[r for r in s['rows'] if r['id'] in ids]
 matched.append(dict(name=name,common_cpu_budget=common,last_observed_checkpoint_cpu=h['coordinator_cpu']+h['cumulative_sampled_worker_cpu'] if h else 0,checkpoint_generation=h['generation'] if h else 0,frontier=[dict(id=r['id'],resources=r['resources']) for r in rows],qualification='Last completed measured CPU checkpoint at or below common budget; unobserved within-generation improvements are not inferred'))
exportrows=[]
extra_delivery=Path('results/competitive_export/frontier_delivery')/source
assert (extra_delivery/'complete.json').exists()
for record in read(delivery/'index.json')['records']+read(extra_delivery/'index.json')['records']:
 manifest=read(Path(record['bundle'])/'manifest.json');exportrows.append(dict(name=record['label'],manifest=manifest,evaluation_status=record['status'],verification=record['verification'],evidence=str(Path(record['bundle']).parents[1]/'verification'/(record['label']+'.json'))))
for path in (root/'independent_extension').glob('*.json'):
 packet=read(path)
 if 'answer' in packet:alltasks.setdefault(packet['answer']['task'],packet['answer'])
for path in list((delivery/'certification').glob('*.json'))+list((delivery/'followup_replay').glob('*.json'))+list((extra_delivery/'certification').glob('*.json')):
 packet=read(path);alltasks.setdefault(packet['answer']['task'],packet['answer'])
validation=Path('results/competitive_export/method_validation')/source
vp=read(validation/'positive_surface2.json');vt=vp['tasks'][0];va=vp['answers'][0];vr=va['result'];alltasks.setdefault(va['task'],va)
if (validation/'independent.json').exists():
 audit=read(validation/'independent.json');alltasks.setdefault(audit['answer']['task'],audit['answer']);assert audit['answer']['result'].get('verified')
methods.append(dict(family='surface2_separate_validation',graph_eligible=read(validation/'eligibility.json')['receipt']['eligible'],fault_alternatives=sum(1 for _ in enumerate_faults(Circuit.from_dict(vt['circuit']))),requested='decomposition',target=2,status=vr.get('status'),lower_bound=vr.get('lower_bound'),upper_bound=vr.get('upper_bound'),method=vr.get('proof',{}).get('method'),independent=vr.get('independent',{}),cpu=va['cpu'],wall=va['wall'],peak=va.get('peak_rss',va['rss']),evidence=str(validation/'positive_surface2.json'),progress=vr.get('progress',[]),proof=vr.get('proof',{}),qualification='Separate post-campaign physical backend validation, not a matched method comparison'))
followup=Path('results/competitive_export/target5_followup')/source
assert (followup/'complete.json').exists()
followup_rows=[]
for path in sorted(followup.glob('*.json')):
 packet=read(path)
 if 'answer' not in packet:continue
 a=packet['answer'];t=packet['task'];r=a['result']
 followup_rows.append(dict(name=path.stem,status=r.get('status'),reason=r.get('reason') or [p.get('reason') for p in r.get('progress',[]) if p.get('reason')],progress=[{k:p.get(k) for k in ('method','reason','width','max_states','work','candidate_widths')} for p in r.get('progress',[])],unresolved=r.get('unresolved',[]),lower_bound=r.get('lower_bound'),upper_bound=r.get('upper_bound'),independent=r.get('independent',{}),cpu=a['cpu'],wall=a['wall'],peak=a.get('peak_rss',a['rss']),evidence=str(path)))
followup_cost=dict(controller=read(followup/'complete.json'),worker_cpu=sum(r['cpu'] for r in followup_rows),rows=followup_rows,scope='Separate prospective follow-up, not pooled with original method limits')
processes=[]
for a in alltasks.values():
 for v in a.get('attempts',[a]):
  if 'dispatch_monotonic' in v:processes.append(v)
overlaps=[(a['pid'],b['pid']) for i,a in enumerate(processes) for b in processes[i+1:] if a['pid']!=b['pid'] and max(a['dispatch_monotonic'],b['dispatch_monotonic'])<min(a['completion_monotonic'],b['completion_monotonic'])]
sessions=[read(p) for p in root.glob('driver_session_*.json')]
extensions=[read(root/'independent_extension/complete.json'),read(delivery/'complete.json'),read(extra_delivery/'complete.json')]
monitor=list((delivery/'execution').glob('driver_session_*.json'))
if monitor:
 measured=[read(p) for p in monitor];extensions[1]=dict(controller_cpu=sum(x['cpu'] for x in measured),wall=sum(x['wall'] for x in measured),peak_controller_working_set=max(x['peak_working_set'] for x in measured))
compute=dict(worker_cpu=sum(a['cpu'] for a in alltasks.values()),controller_cpu=sum(v['cpu'] for v in sessions)+sum(v['controller_cpu'] for v in extensions),session_wall=sum(v['wall'] for v in sessions)+sum(v['wall'] for v in extensions),peak_worker_rss=max(a.get('peak_rss',a['rss']) for a in alltasks.values()),peak_controller_working_set=max([v['peak_working_set'] for v in sessions]+[v['peak_controller_working_set'] for v in extensions]),overlapping_process_pairs=overlaps,unique_task_results=len(alltasks),unmeasured_controller_attempts=[str(delivery/'incomplete_delivery_attempt.json'),str(delivery/'incomplete_recovery_attempt.json')],scope='Recorded final campaign and completion only; two failed delivery-controller intervals are unmeasured. Their workers remain counted.  coordinator includes optimizer sessions and independent bundle replay, so do not add those again. Memory columns are individual-process maxima, not simultaneous system peak. Development, tests, packaging and installed smoke are reported separately.')
save('results/competitive_export/summary.json',dict(source=source,experiment_source=experiment_source,implementation_commit='28e4de0202b1a8427535b508e13688a06b0efe8e',delivery_implementation_commit='835c158482731ffb6cdfcda5c5abc9ee2a8614fc',followup=followup_cost,families=families,methods=methods,auxiliary=[{k:v for k,v in r.items() if k not in ('circuit','certify')}|dict(status=r['certify']['status'],lower_bound=r['certify'].get('lower_bound'),upper_bound=r['certify'].get('upper_bound'),independent=r['certify'].get('independent')) for r in aux],ler=ler,ler_comparisons=comparisons,matched_compute=matched,exports=exportrows,compute=compute,scope='Finite study, not global optima or physical-memory guarantees'))
for name in ('scheduling','target10','non_graphlike','cross_family','shor_repair','export_verification'):
 save(Path('benchmarks')/name/'competitive_export'/source/'index.json',dict(source=source,protocol=str(root/'protocol.json'),summary='results/competitive_export/summary.json',qualification='Index into complete raw experiment records; no duplicate evidence'))
for name in ('scheduling','certification','cross_family','shor_repair','exports','ler','compute'):
 save(Path('results')/name/'competitive_export'/source/'index.json',dict(source=source,raw=str(root),summary='results/competitive_export/summary.json'))
print('SUMMARY_COMPLETE',len(alltasks),flush=True)
