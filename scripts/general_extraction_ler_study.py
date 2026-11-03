"""Frozen matched-noise, matched-decoder comparison of two certified target-five circuits."""
import json,time,hashlib
from pathlib import Path
from scipy.stats import beta
from ftqec.results.artifacts import save,source_identity,digest
from ftqec.execution.tasks import Task,batch
from ftqec.circuits.model import Circuit
source=source_identity();root=Path('results/ler')/source/'target5_matched';root.mkdir(parents=True,exist_ok=True)
state=json.loads((Path('results/non_graphlike')/source/'population_study/shor5_random_101/checkpoint.json').read_text());low=next(r for r in state['rows'] if r.get('certify',{}).get('status')=='CERTIFIED')
allocated=json.loads((Path('results/pareto')/source/'allocation_study/rows.json').read_text());fast=next(r for r in allocated if r['slot']==16)
assert fast['certification']['result']['status']=='CERTIFIED'
cases=[('low_qubit',low['circuit']),('low_qd',fast['circuit'])]
protocol=dict(source=source,circuits={n:digest(c) for n,c in cases},p=[.0001,.001],seeds=[90000,90001,90002,90003],shots_per_batch=32768,decoder='one_mechanism_lookup',workers=2,memory_mb=384,cpu=120,wall=240,confidence='Clopper-Pearson exact binomial, Bonferroni four-arm simultaneous 95 percent coverage',scope='Declared explicit-operation noise with ideal code-space boundaries and logical-Z preparation. One-mechanism decoder includes zero fallback. No hardware memory, optimal decoder, or decoder-independent claim.',driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol);save(root/'protocol_hash.json',dict(sha256=digest(protocol)))
start=time.perf_counter();cpu=time.process_time();summary=[]
for name,data in cases:
 c=Circuit.from_dict(data)
 for p in protocol['p']:
  path=root/(name+'_'+str(p)+'.json')
  if path.exists():answers=json.loads(path.read_text())['answers']
  else:
   tasks=[Task(data,'simulation',c.code.input_hash,{'p':p},protocol['decoder'],seed,source,dict(shots=32768,max_decoder_faults=10000,memory_mb=384,cpu_seconds=120,wall_seconds=240)) for seed in protocol['seeds']]
   answers=batch(tasks,2);save(path,dict(tasks=[t.to_dict() for t in tasks],answers=answers))
  completed=[a['result'] for a in answers if 'failures' in a['result'] and 'shots' in a['result']]
  n=sum(r['shots'] for r in completed);f=sum(r['failures'] for r in completed);alpha=.05/4
  ci=[float(beta.ppf(alpha/2,f,n-f+1)) if f else 0.,float(beta.ppf(1-alpha/2,f+1,n-f)) if f<n else 1.] if n else None
  summary.append(dict(case=name,circuit=digest(data),p=p,shots=n,failures=f,rate=f/n if n else None,simultaneous_interval=ci,completed_batches=len(completed),decoder_unknown=sum(r.get('decoder_unknown',0) for r in completed),raw=str(path)))
  print('LER',name,p,f,n,flush=True)
save(root/'summary.json',dict(source=source,arms=summary,protocol=protocol));save(root/'complete.json',dict(source=source,wall=time.perf_counter()-start,controller_cpu=time.process_time()-cpu))
