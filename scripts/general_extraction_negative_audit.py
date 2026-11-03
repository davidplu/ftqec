"""Separate physical replay of every newly reported negative and matching upper witness."""
import json,time
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.circuits.model import Circuit
from ftqec.faults.verification import verify_witness
source=source_identity();pop=Path('results/non_graphlike')/source/'population_study'
while not (pop/'complete.json').exists():time.sleep(2)
roots=[pop,Path('results/repair_trajectories')/source,Path('results/pareto')/source,Path('results/certification')/source,Path('results/cross_family')/source,Path('results/general_extraction/controls')/source,Path('results/general_extraction/proof_development')/source]
seen={};unknown={};start=time.perf_counter();cpu=time.process_time()
def check(task,answer,origin):
 if not isinstance(task,dict) or not isinstance(answer,dict) or task.get('tier') not in ('certify','screen'):return
 data=task.get('circuit');r=answer.get('result',{})
 if not isinstance(data,dict) or 'operations' not in data:return
 for key in ('witness','upper_witness'):
  w=r.get(key)
  if not w:continue
  identity=digest(dict(circuit=data,witness=w));entry=seen.get(identity)
  if entry:entry['origins'].append(origin);continue
  v=verify_witness(Circuit.from_dict(data),w);assert v['verified'],(origin,v)
  target=task['limits'].get('target');weight=len(w['faults'])
  if key=='witness' and target is not None:assert weight<target
  if key=='upper_witness' and r.get('exact_distance') is not None:assert weight==r['exact_distance']
  seen[identity]=dict(circuit=digest(data),target=target,weight=weight,kind=key,origins=[origin],replay=v)
 if r.get('status')=='UNKNOWN':
  identity=digest(dict(circuit=data,target=task['limits'].get('target'),method=task['limits'].get('proof_method'),reason=r.get('reason'),lower=r.get('lower_bound')))
  unknown.setdefault(identity,dict(circuit=digest(data),target=task['limits'].get('target'),method=task['limits'].get('proof_method'),lower_bound=r.get('lower_bound'),unresolved=r.get('unresolved'),reason=r.get('reason'),origins=[]))['origins'].append(origin)
def visit(d,origin):
 if isinstance(d,dict):
  if isinstance(d.get('task'),dict) and isinstance(d.get('answer'),dict):check(d['task'],d['answer'],origin)
  if isinstance(d.get('tasks'),list) and isinstance(d.get('answers'),list):
   for i,(t,a) in enumerate(zip(d['tasks'],d['answers'])):check(t,a,origin+'#'+str(i))
  for k,v in d.items():
   if k not in ('task','answer','tasks','answers','circuit','source_records','prior_manifest','members'):visit(v,origin+'/'+k)
 elif isinstance(d,list):
  for i,v in enumerate(d):visit(v,origin+'/'+str(i))
for root in roots:
 for p in root.rglob('*.json'):
  if any(x in p.parts for x in ('source','proofs','bundles')):continue
  visit(json.loads(p.read_text(encoding='utf-8')),str(p))
out=Path('results/general_extraction/audit')/source
save(out/'witness_replay.json',dict(source=source,records=list(seen.values()),wall=time.perf_counter()-start,controller_cpu=time.process_time()-cpu))
save(out/'unknown_obligations.json',dict(source=source,records=list(unknown.values()),qualification='UNKNOWN is retained with exactly its recorded verified bound and unresolved interval; missing bounds are not invented.'))
print('NEW_WITNESSES_REPLAYED',len(seen),'UNKNOWN_OBLIGATIONS',len(unknown),flush=True)
