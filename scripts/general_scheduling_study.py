"""Prospective scheduling/allocation ablation on the frozen source."""
import time,json,hashlib
from pathlib import Path
from dataclasses import replace
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.architectures.references import rotated_surface
from ftqec.architectures.synthesis import generate
from ftqec.architectures.population import compile
from ftqec.screening.structural import check
from ftqec.evaluation.resources import resources
from ftqec.execution.tasks import Task,batch
from ftqec.certification.exact import verify
from ftqec.circuits.model import Circuit
source=source_identity();root=Path('results/general_competitive/scheduling')/source
protocol=dict(source=source,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),input='surface10 stabilizers only',seed=4,methods=['list','critical_path','conflict_color','resource'],slots=[1,25,50,99],target=10,work=2000000,workers=2,qualification='Fixed interaction orders isolate scheduling/allocation; independently re-certify every output; no global optimum or matched optimizer throughput claim')
root.mkdir(parents=True,exist_ok=True)
if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
else:save(root/'protocol.json',protocol)
inp,_=rotated_surface(10,1);start=time.perf_counter();cpu=time.process_time();g,receipt=generate(inp,4,10)
save(root/'construction.json',dict(receipt,cpu=time.process_time()-cpu,wall=time.perf_counter()-start))
cases=[(m,99) for m in protocol['methods']]+[('critical_path',n) for n in (1,25,50)]
for method,slots in cases:
 path=root/f'{method}_{slots}.json'
 if path.exists():continue
 start=time.perf_counter();cpu=time.process_time()
 c=compile(inp,replace(g,rounds=1,shared=False,ancilla_slots=slots,schedule=method));check(c);metric=resources(c)
 compile_cost=dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-start)
 task=Task(c.to_dict(),'certify',inp.identity,dict(p=.001),'auto',4,source,dict(target=10,work=2000000,proof_method='graph',memory_mb=512,cpu_seconds=300,wall_seconds=600))
 answer=batch([task],workers=2,memory_mb=512)[0]
 verification=verify(c,answer['result'],2000000) if 'proof' in answer['result'] else dict(verified=False,reason=answer['result'].get('reason'))
 save(path,dict(source=source,circuit=c.to_dict(),resources=metric,compile_cost=compile_cost,task=task.to_dict(),answer=answer,independent_replay=verification))
 print(method,slots,metric['D'],answer['result']['status'],flush=True)
save(root/'complete.json',dict(source=source,protocol=digest(protocol)))
