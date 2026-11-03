import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path('.private/prior-frontier-replay').resolve()))
from ftqec.results.artifacts import source_identity,save
from ftqec.certification.exact import verify
from ftqec.circuits.model import Circuit
from ftqec.optimization.selection import pareto
from ftqec.faults.verification import verify_witness
source=source_identity();assert source=='e0fc9c0ee3642bc7f14d4bb9354a56af6a98584ca1b2d0eb478e14bfaccf929e'
start=time.perf_counter();cpu=time.process_time();receipts=[]
for path in sorted(Path('results/discovery/autonomous').glob('*/checkpoint.json')):
 state=json.loads(path.read_text());rows=pareto([r for r in state['rows'] if r.get('certify',{}).get('status')=='CERTIFIED'])
 for row in rows:
  checked=verify(Circuit.from_dict(row['circuit']),row['certify'],20000000);assert checked['verified'];receipts.append(dict(path=path.as_posix(),id=row['id'],verification=checked))
 print(path.parent.name,len(rows),flush=True)
row=json.loads(Path('results/autonomous/posthoc_shor_diagnosis/candidate.json').read_text());w=json.loads(Path('results/autonomous/posthoc_shor_diagnosis/result.json').read_text())['witness'];wcheck=verify_witness(Circuit.from_dict(row['circuit']),w);assert wcheck['verified']
save('results/general_competitive/historical_frontier_replay.json',dict(source=source,source_origin='dist/autonomous/ftqec-0.1.0-py3-none-any.whl extracted into isolated import root',receipts=receipts,shor_witness=wcheck,cpu=time.process_time()-cpu,wall=time.perf_counter()-start,all_verified=True,scope='All old resource-Pareto rows across target-one-through-ten; not every historical intermediate circuit'))
print('HISTORICAL_FRONTIERS_REPLAYED',len(receipts),flush=True)
