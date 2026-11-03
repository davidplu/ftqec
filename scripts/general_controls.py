"""Prospective random-generation controls, compared at recorded actual CPU checkpoints."""
import json,hashlib
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.architectures.references import rotated_surface
from ftqec.codes.input import load
from ftqec.optimization.engine import Config,optimize
source=source_identity();root=Path('results/general_competitive/controls')/source
protocol=dict(source=source,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),families=['surface10','steane','shor9'],seed=0,population=4,generations=3,finalists=4,workers=2,proof_work=2000000,task_cpu_seconds=30,task_wall_seconds=60,strategies=['random','hybrid'],comparison='random versus physical-witness hybrid with identical per-action allowances and population settings; compare common measured worker-plus-controller CPU checkpoints',qualification='Generation-boundary observations can be unobserved at early CPU horizons; no interpolation of first certificate or throughput claim')
root.mkdir(parents=True,exist_ok=True)
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
for name in protocol['families']:
 inp=rotated_surface(10,1)[0] if name=='surface10' else load(json.loads(Path('examples',name+'.json').read_text()))
 for strategy in protocol['strategies']:
  state=optimize(inp.to_dict(),root/name/strategy,Config(population=4,generations=3,workers=2,seed=0,target=10 if name=='surface10' else 3,strategy=strategy,proof_work=2000000,finalists=4,task_cpu_seconds=30,task_wall_seconds=60))
  print(name,strategy,[(r['resources']['Q'],r['resources']['D'],r.get('certify',{}).get('status')) for r in state['rows']], 'construction_unknown',len(state.get('construction_unknown',[])),flush=True)
save(root/'complete.json',dict(source=source,protocol=digest(protocol)))
