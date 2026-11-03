"""Frozen code-only populations and independent-family validation."""
import json,time,hashlib,shutil
from pathlib import Path
from ftqec.results.artifacts import save,source_identity,digest
from ftqec.codes.families import shor_product,hamming_hypergraph_product
from ftqec.optimization.engine import optimize,Config
from ftqec.codes.logicals import logical_basis
from competitive_algebraic import css_distance
source=source_identity();root=Path('results/non_graphlike')/source/'population_study';root.mkdir(parents=True,exist_ok=True)
primary=shor_product(5);cross=hamming_hypergraph_product()
protocol=dict(source=source,primary=primary.to_dict(),cross=cross.to_dict(),primary_seeds=[101,211],cross_seeds=[331,443],
 strategies=['random','witness','hybrid','costhybrid'],population=6,generations=2,workers=2,
 target=5,proof_work=2000000,task_cpu_seconds=60,task_wall_seconds=120,memory_mb=384,
 initial_shots=64,further_shots=256,finalists=2,p=.001,decoder='auto',
 driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 qualification='Finite prospective measurement conditions, not global optimizer limits. No reference circuits or repaired genomes supplied. Cross-family outcomes are not used for tuning. Matched actual CPU checkpoints required for efficiency claims.')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:
 save(root/'protocol.json',protocol);save(root/'protocol_hash.json',dict(sha256=digest(protocol)))
 shutil.copytree('src/ftqec',root/'source/ftqec',ignore=shutil.ignore_patterns('__pycache__'))
start=time.perf_counter();cpu=time.process_time()
if not (root/'algebraic.json').exists():save(root/'algebraic.json',dict(primary=css_distance(primary.code,5),cross=css_distance(cross.code,3)))
for family,inp,target,seeds,strategies in [('shor5',primary,5,[101,211],protocol['strategies']),('hgp58',cross,3,[331,443],['hybrid'])]:
 for strategy in strategies:
  for seed in seeds:
   config=Config(population=6,generations=2,workers=2,seed=seed,target=target,proof_work=2000000,strategy=strategy,memory_mb=384,task_cpu_seconds=60,task_wall_seconds=120,initial_shots=64,further_shots=256,finalists=2)
   state=optimize(inp.to_dict(),root/f'{family}_{strategy}_{seed}',config)
   print('POPULATION',family,strategy,seed,state['status'],len(state['rows']),flush=True)
save(root/'complete.json',dict(source=source,controller_cpu=time.process_time()-cpu,wall=time.perf_counter()-start))
