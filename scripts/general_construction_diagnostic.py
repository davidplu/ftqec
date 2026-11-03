import time
from pathlib import Path
from ftqec.architectures.references import rotated_surface
from ftqec.architectures.population import sample,compile
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.execution.tasks import Task,batch
root=Path('results/general_competitive/construction_diagnostic')/source_identity();root.mkdir(parents=True,exist_ok=True)
inp,_=rotated_surface(10,1);g=sample(inp,2,10);start=time.perf_counter();cpu=time.process_time();c=compile(inp,g)
receipt=dict(source=source_identity(),genome=g.to_dict(),operations=len(c.operations),detectors=len(c.detectors),compile_cpu=time.process_time()-cpu,compile_wall=time.perf_counter()-start)
save(root/'compiled.json',receipt);print('COMPILED',len(c.operations),len(c.detectors),receipt['compile_cpu'],flush=True)
# A bounded structural-validation diagnostic, not a requested-distance certificate.
task=Task(c.to_dict(),'certify',inp.identity,dict(p=.001),'auto',2,source_identity(),dict(target=1,work=0,memory_mb=512,cpu_seconds=30,wall_seconds=60))
answer=batch([task],workers=1,memory_mb=512)[0]
save(root/'guarded_validation.json',dict(task=task.to_dict(),answer=answer,qualification='Target one isolates mandatory noiseless validation; no higher-distance claim'))
print(answer['result']['status'],answer['result'].get('reason'),answer['cpu'],flush=True)
