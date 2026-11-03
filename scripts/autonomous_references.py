"""Independent reference controls, never used as population seeds."""
import os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):os.environ[key]="1"
import json,hashlib
from pathlib import Path
from ftqec.architectures.references import rotated_surface
from ftqec.screening.structural import check
from ftqec.evaluation.resources import resources
from ftqec.execution.tasks import Task,batch
from ftqec.results.artifacts import source_identity,save
root=Path("results/certificates/reference_validation");root.mkdir(parents=True,exist_ok=True)
source=source_identity();protocol=dict(source=source,scientific_implementation_commit="3e50ef90cea15a778181fa8dc24d3056fdf6bb48",targets=list(range(1,11)),rounds=1,experiment_class="REFERENCE_VALIDATION",driver_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
p=root/"protocol.json"
if p.exists():assert json.loads(p.read_text())==protocol
else:save(p,protocol)
summary=[]
for target in range(1,11):
 path=root/f"target{target}.json"
 if path.exists():record=json.loads(path.read_text())
 else:
  inp,c=rotated_surface(max(2,target),1);check(c)
  t=Task(c.to_dict(),"certify",inp.identity,{"p":.001},"matching",0,source,dict(target=target,work=20000000,memory_mb=512,cpu_seconds=300,wall_seconds=600))
  a=batch([t],1,512)[0];record=dict(source=source,experiment_class="REFERENCE_VALIDATION",target=target,circuit=c.to_dict(),task=t.to_dict(),answer=a,resources=resources(c));save(path,record)
 summary.append(dict(target=target,status=record["answer"]["result"]["status"],resources=record["resources"],cpu=record["answer"]["cpu"],wall=record["answer"]["wall"]))
 print("REFERENCE",target,summary[-1]["status"],flush=True)
save(root/"summary.json",dict(source=source,rows=summary))
