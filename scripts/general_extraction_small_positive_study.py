"""Matched small physical graph-ineligible control; distinct from target-five milestone."""
import json,time,hashlib
from pathlib import Path
from ftqec.results.artifacts import save,source_identity,digest
from ftqec.codes.families import shor_product
from ftqec.architectures.population import Genome,compile
from ftqec.screening.structural import check
from ftqec.certification.eligibility import assess,verify
from ftqec.execution.tasks import Task,batch
source=source_identity();root=Path('results/certification')/source/'small_positive_matched';root.mkdir(parents=True,exist_ok=True)
from ftqec.circuits.model import Circuit
from ftqec.codes.input import load
old='2c806077ca35e80028b6f49add2dbd46390d1d400bb8f7b28452d3f3f038ae58'
c=Circuit.from_dict(json.loads((Path('results/competitive_export/delivery')/old/'exports/repair_compressed/circuit.json').read_text()))
inp=load(c.code.to_dict());g=None;check(c);e=assess(c);v=verify(c,e);assert v['verified']
protocol=dict(source=source,circuit=digest(c.to_dict()),target=3,methods=['decomposition_legacy','decomposition_span','decomposition'],work=20000000,cpu=120,wall=240,memory_mb=384,workers=1,repeats=3,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),qualification='Preserved target-four positive tested at target three; not autonomous discovery. Target three does not satisfy target-five milestone. Three repeats rotate execution order.')
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
save(root/'input.json',dict(code=inp.to_dict(),genome=None,circuit=c.to_dict(),eligibility=e,independent=v))
start=time.perf_counter();cpu=time.process_time()
for repeat in range(3):
 methods=protocol['methods'][repeat:]+protocol['methods'][:repeat]
 for method in methods:
  path=root/f'{repeat}_{method}.json'
  if path.exists():continue
  task=Task(c.to_dict(),'certify',inp.identity,{'p':.001},'auto',repeat,source,dict(target=3,proof_method=method,work=20000000,memory_mb=384,cpu_seconds=120,wall_seconds=240))
  answer=batch([task],1)[0];save(path,dict(task=task.to_dict(),answer=answer));print('SMALL_PROOF',repeat,method,answer['result'].get('status'),answer['result'].get('proof',{}).get('method'),flush=True)
save(root/'complete.json',dict(source=source,wall=time.perf_counter()-start,controller_cpu=time.process_time()-cpu))
