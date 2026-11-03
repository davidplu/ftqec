import json,time
from pathlib import Path
from ftqec.optimization.engine import Config,optimize
from ftqec.results.artifacts import source_identity,save
s=source_identity();p=Path('results/large_scale/development')/s;p.mkdir(parents=True,exist_ok=True)
code=json.loads(Path('benchmarks/distance_ladder/autonomous/surface_target3.json').read_text())
print('INPUT_KEYS',list(code),flush=True)
if 'code' in code:code=code['code']
config=Config(storage='sqlite',population=32,generations=1,window=16,promotion=4,workers=4,seed=1501,target=3,proof_work=200000,initial_shots=32,further_shots=128,finalists=2,memory_mb=256,task_cpu_seconds=30,task_wall_seconds=60)
save(p/'pilot_protocol.json',dict(source=s,code=code,config=config.__dict__))
t=time.perf_counter();x=optimize(code,p/'pilot',config);save(p/'pilot_receipt.json',dict(source=s,status=x['status'],unique=x['unique_circuits'],wall=time.perf_counter()-t));print('PILOT_COMPLETE',x['status'],x['unique_circuits'],flush=True)
