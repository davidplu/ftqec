"""Matched small physical graph-ineligible control; distinct from target-five milestone."""
import json,time,hashlib
from pathlib import Path
from ftqec.results.artifacts import save,source_identity,digest
from ftqec.codes.families import shor_product
from ftqec.architectures.population import Genome,compile
from ftqec.screening.structural import check
from ftqec.certification.eligibility import assess,verify
from ftqec.execution.tasks import Task,batch
source=source_identity();root=Path('results/certification')/source/'small_matched';root.mkdir(parents=True,exist_ok=True)
inp=shor_product(3);orders=tuple(tuple(q for q in range(inp.code.n) if (p.x|p.z)>>q&1) for p in inp.code.generators)
g=Genome('flagged',orders,tuple(range(len(orders))),rounds=2,shared=False,flag_style='adjacent',schedule='critical_path',compact_ancillas=True)
c=compile(inp,g);check(c);e=assess(c);v=verify(c,e);assert v['verified']
protocol=dict(source=source,circuit=digest(c.to_dict()),target=3,methods=['decomposition_legacy','decomposition_span','decomposition'],work=20000000,cpu=120,wall=240,memory_mb=384,workers=1,repeats=3,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),qualification='Small matched physical control; target three does not satisfy target-five milestone. Three repeats rotate execution order.')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
save(root/'input.json',dict(code=inp.to_dict(),genome=g.to_dict(),circuit=c.to_dict(),eligibility=e,independent=v))
start=time.perf_counter();cpu=time.process_time()
for repeat in range(3):
 methods=protocol['methods'][repeat:]+protocol['methods'][:repeat]
 for method in methods:
  path=root/f'{repeat}_{method}.json'
  if path.exists():continue
  task=Task(c.to_dict(),'certify',inp.identity,{'p':.001},'auto',repeat,source,dict(target=3,proof_method=method,work=20000000,memory_mb=384,cpu_seconds=120,wall_seconds=240))
  answer=batch([task],1)[0];save(path,dict(task=task.to_dict(),answer=answer));print('SMALL_PROOF',repeat,method,answer['result'].get('status'),answer['result'].get('proof',{}).get('method'),flush=True)
save(root/'complete.json',dict(source=source,wall=time.perf_counter()-start,controller_cpu=time.process_time()-cpu))
