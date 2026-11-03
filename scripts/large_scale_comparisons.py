"""Matched recorded-compute comparisons, never equal-count superiority claims."""
import json,csv,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
s=source_identity();root=Path('results/large_scale/comparisons')/s;root.mkdir(parents=True,exist_ok=True);summary=json.loads((Path('results/large_scale/audit')/s/'summary.json').read_text());protocol=json.loads((Path('results/large_scale/campaigns')/s/'protocol.json').read_text());runs={r['job']['name']:r for r in summary['runs']}

def metrics(event):
 rows=event.get('certified',[]);tuples={tuple(r['resources'][k] for k in ('Q','D','QD','two_q_gates')) for r in rows}
 return dict(certified_frontier_identities=len(rows),certified_resource_tuples=len(tuples),best_QD=min((r['resources']['QD'] for r in rows),default=None),resource_tuples=sorted(tuples))

def value(event,clock):return event['worker_cpu']+event['controller_cpu'] if clock=='total_cpu' else event['elapsed_wall']

def previous(run,clock,budget):
 eligible=[e for e in run['frontier_history'] if value(e,clock)<=budget]
 return max(eligible,key=lambda e:value(e,clock)) if eligible else dict(worker_cpu=0,controller_cpu=0,elapsed_wall=0,certified=[],generated=0)

comparisons=[]
for family in protocol['codes']:
 for seed in (2001,2002):
  selected=[r for r in runs.values() if r['job']['family']==family and r['job']['config']['seed']==seed and r['job']['config']['strategy']=='hybrid' and r['job']['config']['candidate_goal']>=1000]
  comparisons.append(('population_capacity',family,seed,selected))
  selected=[r for r in runs.values() if r['job']['family']==family and r['job']['config']['seed']==seed and r['job']['config']['candidate_goal']==100]
  comparisons.append(('strategy',family,seed,selected))
rows=[]
for study,family,seed,group in comparisons:
 if len(group)<2:continue
 for clock,checkpoints in [('total_cpu',protocol['matched_cpu_checkpoints']),('elapsed_wall',protocol['matched_wall_checkpoints'])]:
  common=max(0,min(max((value(e,clock) for e in r['frontier_history']),default=0) for r in group))
  for budget in checkpoints:
   if budget>common:continue
   for run in group:
    event=previous(run,clock,budget);config=run['job']['config'];rows.append(dict(study=study,family=family,seed=seed,clock=clock,declared_checkpoint=budget,actual_recorded_compute=value(event,clock),unobserved_checkpoint_gap=budget-value(event,clock),job=run['job']['name'],population=config['population'],strategy=config['strategy'],generated_at_snapshot=event['generated'],**metrics(event)))
save(root/'matched_checkpoints.json',dict(source=s,rows=rows,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Complete recorded window snapshots at or below prospectively frozen common actual compute checkpoints. CPU includes worker plus controller. Snapshot gaps are explicit; intermediate frontier improvements cannot be inferred. Wall comparisons are observational local runs; concurrent validation is disclosed separately. One large-campaign seed does not establish statistical superiority.'))
if rows:
 with (root/'matched_checkpoints.csv').open('w',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
# Within-run evolution and time to the first recorded positive are observed window bounds.
evolution=[]
for run in runs.values():
 history=run['frontier_history'];positive=[e for e in history if e.get('certified')];first=positive[0] if positive else None
 evolution.append(dict(job=run['job'],first_positive_recorded_total_cpu=value(first,'total_cpu') if first else None,first_positive_recorded_wall=first['elapsed_wall'] if first else None,first_positive_QD=metrics(first)['best_QD'] if first else None,final=metrics(history[-1]) if history else metrics({}),scope='First observed completed-window positive; not an exact within-window discovery timestamp.'))
save(root/'frontier_evolution.json',dict(source=s,records=evolution));print('MATCHED_COMPUTE_COMPARISONS_WRITTEN',len(rows),flush=True)