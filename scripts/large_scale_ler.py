"""Prospectively frozen resource-selected, matched-decoder final LER evaluation."""
import json,time,hashlib,argparse
from pathlib import Path
from scipy.stats import beta
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.execution.tasks import Task,batch
from ftqec.circuits.model import Circuit
s=source_identity();root=Path('results/ler/large_scale')/s;root.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--freeze-only',action='store_true');args=parser.parse_args()
rules=dict(source=s,selection='Within each independently verified family frontier, take the lexicographic minimum (metric,circuit hash) for Q, D, and QD; deduplicate exact circuits. No simulation outcome used in selection.',p=[.0001,.001],seeds=[93000,93001,93002,93003],shots_per_batch=32768,decoder='one_mechanism_lookup',max_decoder_faults=100000,workers=1,memory_mb=384,cpu_seconds=120,wall_seconds=240,interval='Fixed-sample Clopper-Pearson, Bonferroni over every frozen selected circuit/noise arm. No interval or superiority claim for an arm with incomplete batches.',scope='Operation-local depolarization, reset X, measurement flip, ideal boundaries, logical-Z preparation; explicit one-mechanism decoder with zero fallback. Not decoder-independent or hardware-memory performance.',driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
p=root/'selection_protocol.json'
if p.exists():assert json.loads(p.read_text())==rules
else:save(p,rules)
if args.freeze_only:print('LER_SELECTION_RULES_FROZEN');raise SystemExit(0)
records=json.loads((Path('results/exports/large_scale')/s/'index.json').read_text())['records'];selected={}
for family in sorted({r['family'] for r in records}):
 rows=[r for r in records if r['family']==family]
 for metric in ('Q','D','QD'):
  row=min(rows,key=lambda r:(r['resources'][metric],r['circuit']));selected[row['circuit']]=row
assert selected,'No verified finalists available'
protocol=dict(rules,selected=list(selected.values()),arms=len(selected)*len(rules['p']))
p=root/'protocol.json'
if p.exists():assert json.loads(p.read_text())==protocol
else:save(p,protocol)
summary=[]
for cid,row in sorted(selected.items()):
 data=json.loads((Path(row['bundle'])/'circuit.json').read_text());assert digest(data)==cid;c=Circuit.from_dict(data)
 for noise in rules['p']:
  packets=[]
  for seed in rules['seeds']:
   path=root/'batches'/cid/str(noise)/(str(seed)+'.json')
   task=Task(data,'simulation',c.code.input_hash,dict(p=noise),rules['decoder'],seed,s,dict(shots=rules['shots_per_batch'],max_decoder_faults=rules['max_decoder_faults'],memory_mb=384,cpu_seconds=120,wall_seconds=240))
   if path.exists():packet=json.loads(path.read_text());assert packet['task']==task.to_dict()
   else:packet=dict(task=task.to_dict(),answer=batch([task],1,memory_mb=384)[0]);save(path,packet)
   packets.append(packet)
  completed=[x['answer']['result'] for x in packets if 'shots' in x['answer']['result'] and 'failures' in x['answer']['result']]
  n=sum(x['shots'] for x in completed);f=sum(x['failures'] for x in completed);complete=len(completed)==len(rules['seeds']);alpha=.05/protocol['arms'];ci=None
  if complete:ci=[float(beta.ppf(alpha/2,f,n-f+1)) if f else 0.,float(beta.ppf(1-alpha/2,f+1,n-f)) if f<n else 1.]
  summary.append(dict(circuit=cid,family=row['family'],resources=row['resources'],p=noise,shots=n,failures=f,complete=complete,completed_batches=len(completed),rate=f/n if n else None,simultaneous_interval=ci,decoder_unknown=sum(x.get('decoder_unknown',0) for x in completed),worker_cpu=sum(x['answer']['cpu'] for x in packets),raw_directory=str(root/'batches'/cid/str(noise))))
  save(root/'summary_partial.json',dict(source=s,arms=summary));print('LER_ARM',row['family'],cid[:12],noise,f,n,complete,flush=True)
save(root/'summary.json',dict(source=s,protocol=protocol,arms=summary));save(root/'complete.json',dict(source=s,complete_arms=sum(r['complete'] for r in summary),declared_arms=protocol['arms']))