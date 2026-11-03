"""Development-only code-input synthesis; never import a reference constructor."""
import json,time
from pathlib import Path
from ftqec.codes.input import load
from ftqec.architectures.synthesis import generate
from ftqec.execution.tasks import Task,batch
from ftqec.results.artifacts import source_identity,save

def main():
 source=source_identity();root=Path('results/competitive_export/development')/source;root=root/str(time.time_ns());root.mkdir(parents=True,exist_ok=False)
 old=Path('results/general_competitive/final/0e15b68fc104513af365fe022cb271d7da3408d08a9882d381a9a047f2a08e0c/optimizer/surface10_seed0/checkpoint.json')
 inp=load(json.loads(old.read_text())['code']);start=time.perf_counter();cpu=time.process_time()
 g,receipt=generate(inp,0,10,parallel=True,joint=True)
 save(root/'generation.json',dict(source=source,input=inp.to_dict(),genome=g.to_dict(),receipt=receipt,cpu=time.process_time()-cpu,wall=time.perf_counter()-start))
 print('GENERATED',g.schedule,receipt,flush=True)
 task=Task(dict(code_input=inp.to_dict(),genome=g.to_dict()),'construct',inp.identity,{'p':.001},'matching',0,source,dict(memory_mb=512,cpu_seconds=300,wall_seconds=600))
 answer=batch([task],1)[0];save(root/'construction.json',dict(task=task.to_dict(),answer=answer));print('CONSTRUCTION',answer['result'].keys(),flush=True)
 if answer['result'].get('circuit'):
  c=answer['result']['circuit'];t=Task(c,'certify',inp.identity,{'p':.001},'matching',0,source,dict(memory_mb=512,cpu_seconds=300,wall_seconds=600,target=10,work=2000000,proof_method='auto',proof_directory=str(root/'proofs')))
  a=batch([t],1)[0];save(root/'certificate.json',dict(task=t.to_dict(),answer=a));print('CERTIFICATE',a['result'].get('status'),answer['result'].get('resources'),flush=True)
if __name__=='__main__':main()
