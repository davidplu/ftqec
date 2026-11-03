"""Replay all randomized-development harmful witnesses under their exact source."""
import sys,json,time
from pathlib import Path
old='6c675260b459a563ddafe02e5da9696b92a2f812064ac29e441a6181fceece2d'
base=Path('results/competitive_export/order_development')/old
sys.path.insert(0,str((base/'source').resolve()))
from ftqec.results.artifacts import source_identity,save
from ftqec.circuits.model import Circuit
from ftqec.certification.exact import verify
assert source_identity()==old
rows=[];start=time.perf_counter();cpu=time.process_time()
for p in sorted(base.glob('*/seed*.json')):
 packet=json.loads(p.read_text())
 for i,(t,a) in enumerate(zip(packet['tasks'],packet['answers'])):
  if a['result']['status']=='INVALID':
   v=verify(Circuit.from_dict(t['circuit']),a['result'],2000000);assert v['verified'];rows.append(dict(packet=str(p),index=i,status='INVALID',replay=v))
  else:rows.append(dict(packet=str(p),index=i,status=a['result']['status'],reason=a['result'].get('reason'),qualification='Not a positive or negative scientific result; unresolved task retained'))
save(base/'independent_replay.json',dict(source=old,rows=rows,cpu=time.process_time()-cpu,wall=time.perf_counter()-start));print('DEVELOPMENT_WITNESSES_REPLAYED',len(rows),flush=True)
