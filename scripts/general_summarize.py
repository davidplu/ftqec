"""Derive tables and claim boundaries from the final epoch's raw artifacts."""
import json,time,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.circuits.model import Circuit
from ftqec.evaluation.resources import resources
from ftqec.optimization.selection import pareto,reliability_pareto
from ftqec.certification.exact import verify
from ftqec.scheduling.scheduler import schedule
source=source_identity();root=Path('results/general_competitive/final')/source
assert (root/'complete.json').exists()
assert json.loads((root/'audit.json').read_text())['all_verified']
read=lambda p:json.loads(Path(p).read_text())
base=read('results/general_competitive/baseline/audit.json')
bad=[name for name,sha in base['evidence'].items() if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=sha]
# The external delivery manifest may be replaced only after its old bytes were preserved.
if bad==['results/artifact_manifest.json']:
 assert hashlib.sha256(Path('results/general_competitive/baseline/previous/results/artifact_manifest.json').read_bytes()).hexdigest()==base['evidence'][bad[0]];bad=[]
assert not bad,bad
all_answers=[];family=[];candidate_rows=[];states={}
for path in sorted((root/'optimizer').glob('*/checkpoint.json')):
 state=read(path);states[path.parent.name]=state;rows=state['rows'];answers=list(state['tasks'].values());all_answers+=answers
 positives=[r for r in rows if r.get('certify',{}).get('status')=='CERTIFIED']
 candidate_rows+= [dict(r,origin=path.as_posix(),reference=False,target=state['config']['target']) for r in positives]
 cpu=sum(a['cpu'] for a in answers)+sum(s['cpu'] for s in state['sessions'])
 family.append(dict(name=path.parent.name,n=state['code']['n'],k=Circuit.from_dict(rows[0]['circuit']).code.k if rows else None,target=state['config']['target'],generated=sum(g['generated'] for g in state.get('generation_compute',[])),compiled=sum(g['compiled'] for g in state.get('generation_compute',[])),distinct=len(rows),simulated=sum(r.get('simulation',{}).get('shots',0)>0 for r in rows),certified=len(positives),harmful=sum(r.get('certify',{}).get('status')=='INVALID' or r.get('screen',{}).get('status')=='FAULT_INVALID' for r in rows),unknown=sum(r.get('certify',{}).get('status')=='UNKNOWN' for r in rows),not_certified=sum('certify' not in r for r in rows),construction_unknown=len(state.get('construction_unknown',[])),best=min((r['resources'] for r in positives),key=lambda r:r['QD'],default=None),cpu=cpu,wall=sum(s['wall'] for s in state['sessions']),first_certified=state.get('first_certified'),evidence=path.as_posix()))
methods=[];ler=[];repairs=[]
for path in sorted(root.glob('*/*.json')):
 packet=read(path)
 if not ('tasks' in packet and 'answers' in packet):continue
 all_answers+=packet['answers']
 for task,a in zip(packet['tasks'],packet['answers']):
  c=Circuit.from_dict(task['circuit']);r=a['result'];metric=resources(c)
  item=dict(evidence=path.as_posix(),task=a['task'],target=task['limits']['target'],requested_method=task['limits'].get('proof_method'),actual_method=r.get('proof',{}).get('method'),status=r.get('status','SIMULATED'),lower_bound=r.get('lower_bound'),upper_bound=r.get('upper_bound'),independent=r.get('independent'),cpu=a['cpu'],wall=a['wall'],peak_rss=a.get('peak_rss',a['rss']),body_cpu=a.get('body_cpu'),independent_cost=r.get('independent_cost'),reason=r.get('reason'),unresolved=r.get('unresolved'),progress=r.get('progress'),resources=metric,circuit=digest(c.to_dict()))
  if path.parent.name=='methods':methods.append(item)
  if path.parent.name=='shor_repair':repairs.append(dict(item,variant=path.stem))
  if path.parent.name=='ler':ler.append(dict(item,variant=path.stem,p=task['noise']['p'],seed=task['seed'],decoder=r.get('decoder'),shots=r.get('shots'),failures=r.get('failures'),confidence=r.get('confidence'),rate=r.get('rate')))
  if path.parent.name=='target10' and r.get('status')=='CERTIFIED':candidate_rows.append(dict(id=digest(c.to_dict()),circuit=c.to_dict(),resources=metric,certify=r,origin=path.as_posix(),reference=path.stem=='reference',target=10))
scheduling=[]
for path in sorted((Path('results/general_competitive/scheduling')/source).glob('*.json')):
 packet=read(path)
 if 'answer' not in packet:continue
 assert packet['independent_replay']['verified'];c=Circuit.from_dict(packet['circuit']);assert resources(c)==packet['resources']
 scheduling.append(dict(variant=path.stem,resources=packet['resources'],cpu=packet['answer']['cpu']+packet['compile_cost']['cpu'],wall=packet['answer']['wall']+packet['compile_cost']['wall'],status=packet['answer']['result']['status'],evidence=path.as_posix()))
 if packet['answer']['result']['status']=='CERTIFIED':candidate_rows.append(dict(id=digest(c.to_dict()),circuit=c.to_dict(),resources=packet['resources'],certify=packet['answer']['result'],origin=path.as_posix(),reference=False,target=10))
front=pareto([r for r in candidate_rows if r['target']==10 and not r['reference']]);known=pareto([r for r in candidate_rows if r['target']==10])
assert any(r['resources']['Q']==101 for r in front)
for r in front:assert r['certify']['independent']['verified']
best=min(front,key=lambda r:r['resources']['QD']);c=Circuit.from_dict(best['circuit']);starts=schedule(c).starts
parallel=Counter(t for op,t in zip(c.operations,starts) if op.role=='data_interaction')
controls=[]
controlroot=Path('results/general_competitive/controls')/source
assert (controlroot/'complete.json').exists()
control_audit=[]
for path in sorted(controlroot.glob('*/random/checkpoint.json')):
 random=read(path);name=path.parent.parent.name;hybrid=read(path.parent.parent/'hybrid/checkpoint.json')
 def total(s):return sum(a['cpu'] for a in s['tasks'].values())+sum(a['cpu'] for a in s['sessions'])
 common=min(total(random),total(hybrid));observations=[]
 for f in (.25,.5,.75,1):
  budget=common*f;values={}
  for label,s in (('random',random),('hybrid',hybrid)):
   events=[e for e in s.get('frontier_history',[]) if e['cumulative_sampled_worker_cpu']+e['coordinator_cpu']<=budget]
   values[label]=events[-1]['certified_pareto'] if events else None
  observations.append(dict(cpu_budget=budget,observations=values,qualification='None means no complete logged generation at this horizon, not absence of an early certificate'))
 for arm_name,arm in (('random',random),('hybrid',hybrid)):
  for row in arm['rows']:
   if row.get('certify',{}).get('status')=='CERTIFIED':candidate_rows.append(dict(row,origin=(path.parent.parent/arm_name/'checkpoint.json').as_posix(),reference=False,target=arm['config']['target']))
 for row in random['rows']+hybrid['rows']:
  if row.get('certify',{}).get('status') in ('CERTIFIED','INVALID'):
   checked=verify(Circuit.from_dict(row['circuit']),row['certify'],2000000);assert checked['verified'];control_audit.append(dict(id=row['id'],verified=checked))
 controls.append(dict(name=name,random_cpu=total(random),hybrid_cpu=total(hybrid),random_certified=sum(r.get('certify',{}).get('status')=='CERTIFIED' for r in random['rows']),hybrid_certified=sum(r.get('certify',{}).get('status')=='CERTIFIED' for r in hybrid['rows']),common_cpu=common,random_construction_unknown=len(random.get('construction_unknown',[])),hybrid_construction_unknown=len(hybrid.get('construction_unknown',[])),checkpoints=observations,evidence=path.as_posix()))
# Rebuild joint archives after incorporating certified control-arm discoveries.
front=pareto([r for r in candidate_rows if r['target']==10 and not r['reference']]);known=pareto([r for r in candidate_rows if r['target']==10])
best=min(front,key=lambda r:r['resources']['QD']);c=Circuit.from_dict(best['circuit']);starts=schedule(c).starts
parallel=Counter(t for op,t in zip(c.operations,starts) if op.role=='data_interaction')
from ftqec.faults.verification import verify_witness
screen_audit=[]
for path in list((root/'optimizer').glob('*/checkpoint.json'))+list(controlroot.glob('*/*/checkpoint.json')):
 for row in read(path)['rows']:
  if row.get('screen',{}).get('status')=='FAULT_INVALID':
   checked=verify_witness(Circuit.from_dict(row['circuit']),row['screen']['witness']);assert checked['verified'];screen_audit.append(dict(path=path.as_posix(),id=row['id'],verified=checked))
precision=read(Path('results/general_competitive/ler_precision')/source/'summary.json')
assert all(r['status']=='COMPLETE' for r in precision['results'])
sessions=[read(p) for p in root.glob('driver_session_*.json')]
assert sessions and all(s['returncode']==0 for s in sessions)
events=[]
for a in all_answers:
 if 'dispatch_monotonic' in a:events.extend([(a['dispatch_monotonic'],1),(a['completion_monotonic'],-1)])
running=peak=0
for _,delta in sorted(events,key=lambda x:(x[0],x[1])):running+=delta;peak=max(peak,running)
compute=dict(controller_cpu=sum(s['cpu'] for s in sessions),worker_cpu=sum(a['cpu'] for a in all_answers),wall=sum(s['wall'] for s in sessions),active_wall=sum(s['active_wall'] for s in sessions),peak_controller_working_set=max(s['peak_working_set'] for s in sessions),peak_worker_sampled_rss=max(a.get('peak_rss',a['rss']) for a in all_answers),observed_concurrent_evaluators=peak,evaluator_tasks=len(all_answers),scope='Final main campaign only; controller includes candidate generation, supervision, persistence and audit; construction/evaluation workers counted once. Scheduling, controls, packaging, tests and earlier epochs are separate workloads.')
compute['total_cpu']=compute['controller_cpu']+compute['worker_cpu']
summary=dict(source=source,implementation_commit=states['surface10_seed0']['commit'],preservation_files=len(base['evidence']),preservation_verified=True,methods=methods,families=family,ler=ler,repairs=repairs,scheduling=scheduling,compute=compute,controls=controls,best_target10=dict(id=best['id'],resources=best['resources'],origin=best['origin'],peak_simultaneous_data_interactions=max(parallel.values())),raw_hyperedges=read(root/'methods/inventory5.json'),scientific_audit=read(root/'audit.json')['all_verified'],control_audit=control_audit,screen_witness_audit=screen_audit,precision=precision,color_small_duplicates_steane=True)
save('results/general_competitive/summary.json',summary)
for folder,content in [('certification',dict(methods=methods,repairs=repairs)),('scheduling',dict(comparisons=scheduling)),('pareto',dict(discovery=front,all_known_including_reference=known,coordinate_best={k:[r['id'] for r in front if r['resources'][k]==min(x['resources'][k] for x in front)] for k in ('Q','D','QD','two_q_gates')})),('ler',dict(comparisons=ler,precision=precision)),('compute',dict(main=compute,controls=controls))]:save(Path('results')/folder/'general_competitive'/f'{source}.json',dict(source=source,**content))
for folder,target in [('certification_methods','certification'),('non_graphlike','certification'),('scheduling','scheduling'),('target10','pareto')]:save(Path('benchmarks')/folder/'general_competitive'/f'{source}.json',dict(source=source,protocol=(root/'protocol.json').as_posix(),results=f'results/{target}/general_competitive/{source}.json',qualification='See raw source-bound final epoch; do not merge earlier-source outcomes'))
print(json.dumps(dict(source=source,compute=compute,best=summary['best_target10'],hyperedges=summary['raw_hyperedges'],families=family,controls=controls),indent=2))
