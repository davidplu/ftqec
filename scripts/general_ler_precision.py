"""Fixed-size independent precision follow-up; no sampling-until-significance."""
import json,time,hashlib
from pathlib import Path
from scipy.stats import beta
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.execution.tasks import Task,batch
from ftqec.circuits.model import Circuit
source=source_identity();base=Path('results/general_competitive/final')/source
state=json.loads((base/'optimizer/surface10_seed0/checkpoint.json').read_text())
best=min([r for r in state['rows'] if r.get('certify',{}).get('status')=='CERTIFIED'],key=lambda r:r['resources']['QD'])
circuits={'discovered':best['circuit']}
for name in ('low_qubit','reference'):circuits[name]=json.loads((base/'target10'/(name+'.json')).read_text())['tasks'][0]['circuit']
root=Path('results/general_competitive/ler_precision')/source;root.mkdir(parents=True,exist_ok=True)
protocol=dict(source=source,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),circuit_ids={n:digest(c) for n,c in circuits.items()},p=.01,decoder='matching',blocks=16,shots_per_block=65536,total_shots_per_circuit=1048576,seeds=list(range(71000,71016)),familywise_alpha=.05,per_circuit_alpha=.05/3,interval='exact Clopper-Pearson with Bonferroni over the three circuits',scope='Independent new samples; do not pool the pilot. Fixed sample size chosen before follow-up outcomes. Initial low counts motivated this separate precision study; no optional stopping or architecture superiority assumed.')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
for block,seed in enumerate(protocol['seeds']):
 path=root/f'block{block:02}.json'
 if path.exists():continue
 tasks=[Task(c,'simulation',digest(c['code']),dict(p=.01),'matching',seed,source,dict(shots=65536,target=10,work=0,max_decoder_faults=100000,memory_mb=512,cpu_seconds=300,wall_seconds=600)) for c in circuits.values()]
 start=time.perf_counter();cpu=time.process_time();answers=batch(tasks,2,memory_mb=512)
 save(path,dict(source=source,names=list(circuits),tasks=[t.to_dict() for t in tasks],answers=answers,controller_cpu=time.process_time()-cpu,wall=time.perf_counter()-start))
 print('LER_PRECISION',block,[a['result'].get('failures',a['result'].get('reason')) for a in answers],flush=True)
results=[]
for name in circuits:
 selected=[]
 for p in sorted(root.glob('block*.json')):
  packet=json.loads(p.read_text());i=packet['names'].index(name);selected.append(packet['answers'][i])
 complete=all(a['result'].get('shots')==65536 and a['result'].get('decoder')=='correlated_matching' for a in selected)
 if not complete:results.append(dict(name=name,status='INCOMPLETE',answers=[a['result'] for a in selected]));continue
 n=sum(a['result']['shots'] for a in selected);k=sum(a['result']['failures'] for a in selected);alpha=.05/3
 lo=float(beta.ppf(alpha/2,k,n-k+1)) if k else 0.;hi=float(beta.ppf(1-alpha/2,k+1,n-k)) if k<n else 1.
 results.append(dict(name=name,status='COMPLETE',circuit=digest(circuits[name]),shots=n,failures=k,rate=k/n,simultaneous_interval=[lo,hi],worker_cpu=sum(a['cpu'] for a in selected),worker_wall_sum=sum(a['wall'] for a in selected),peak_sampled_rss=max(a.get('peak_rss',a['rss']) for a in selected)))
assert all(r['status']=='COMPLETE' for r in results),results
comparisons=[dict(lower=a['name'],higher=b['name'],resolved=a['simultaneous_interval'][1]<b['simultaneous_interval'][0]) for a in results for b in results if a is not b]
save(root/'summary.json',dict(source=source,protocol=digest(protocol),results=results,comparisons=comparisons,qualification=protocol['scope']))
print('LER_PRECISION_COMPLETE',results,flush=True)
