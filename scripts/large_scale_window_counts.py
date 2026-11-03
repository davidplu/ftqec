"""Independently reconstruct completed-window population counts for compute comparisons."""
import argparse,json,bisect,time,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
from ftqec.optimization.store import PopulationStore,unpack
parser=argparse.ArgumentParser();parser.add_argument('--job',action='append');args=parser.parse_args();s=source_identity();base=Path('results/large_scale/campaigns')/s;protocol=json.loads((base/'protocol.json').read_text());jobs=protocol['jobs']
if args.job:jobs=[j for j in jobs if j['name'] in args.job];assert len(jobs)==len(args.job)
else:assert (base/'complete.json').exists()
root=Path('results/large_scale/window_counts')/s
if args.job:root=root/'subsets'/hashlib.sha256('|'.join(sorted(args.job)).encode()).hexdigest()
root.mkdir(parents=True,exist_ok=True);results=[]
for job in jobs:
 path=Path('results/populations')/s/'study'/job['name'];assert json.loads((path/'experiment_receipt.json').read_text())['status']=='REQUESTED_CANDIDATE_GOAL_COMPLETED';out=root/(job['name']+'.json')
 if out.exists():results.append(json.loads(out.read_text()));continue
 start=time.perf_counter();cpu=time.process_time();order={k:[] for k in ('indexed','certified','invalid','unknown','unsupported','simulated')};families={};events=[];capacity=job['config']['population']
 with PopulationStore(path/'population.sqlite',readonly=True) as db:
  for blob,sha in db.db.execute('SELECT payload,hash FROM candidates'):
   row=unpack(blob,sha);ordinal=row['attempt']['generation']*capacity+row['attempt']['index'];order['indexed'].append(ordinal);families.setdefault(row['genome']['family'],[]).append(ordinal);status=row.get('certify',{}).get('status')
   if status=='CERTIFIED':order['certified'].append(ordinal)
   if status in ('UNKNOWN','UNSUPPORTED'):order[status.lower()].append(ordinal)
   if status=='INVALID' or row.get('screen',{}).get('status')=='FAULT_INVALID':order['invalid'].append(ordinal)
   if row.get('simulation_batches'):order['simulated'].append(ordinal)
  for values in list(order.values())+list(families.values()):values.sort()
  for blob,sha in db.db.execute("SELECT payload,hash FROM events WHERE kind='frontier' ORDER BY seq"):
   event=unpack(blob,sha);counts={k:bisect.bisect_left(v,event['generated']) for k,v in order.items()};assert counts['indexed']==event['unique'];events.append(dict(event,completed_candidate_counts=counts,architecture_family_counts={k:bisect.bisect_left(v,event['generated']) for k,v in families.items()}))
 record=dict(source=s,job=job['name'],events=events,controller_cpu=time.process_time()-cpu,wall=time.perf_counter()-start,scope='Candidate status counted only at fully completed window boundaries, using preserved first-construction ordinal. Population identity and event unique-count agreement are independently checked. No interpolated discovery time.');save(out,record);results.append(record);print('WINDOW_COUNTS_VERIFIED',job['name'],len(events),flush=True)
save(root/'index.json',dict(source=s,records=[dict(job=r['job'],path=str(root/(r['job']+'.json'))) for r in results],driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))