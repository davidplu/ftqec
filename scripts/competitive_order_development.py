"""Generic randomized flag-order development; all outcomes retained."""
import json,time,random
from pathlib import Path
from dataclasses import replace
from ftqec.results.artifacts import source_identity,save
from ftqec.codes.families import shor_product
from ftqec.architectures.population import sample,compile
from ftqec.architectures.allocation import compact
from ftqec.circuits.model import Circuit
from ftqec.screening.structural import check
from ftqec.evaluation.resources import resources
from ftqec.certification.eligibility import assess,verify
from ftqec.execution.tasks import Task,batch

def main():
 source=source_identity();root=Path('results/competitive_export/order_development')/source/str(time.time_ns());root.mkdir(parents=True)
 inp=shor_product(5);save(root/'protocol.json',dict(source=source,code=inp.to_dict(),seeds=list(range(8)),styles=['adjacent','nested'],rounds=2,work=2000000,scope='development, not final-family evaluation'))
 old=Path('results/general_competitive/final/0e15b68fc104513af365fe022cb271d7da3408d08a9882d381a9a047f2a08e0c/shor_repair/adjacent_False.json');c=compact(Circuit.from_dict(json.loads(old.read_text())['tasks'][0]['circuit']))
 t=Task(c.to_dict(),'certify',c.code.input_hash,{'p':.001},'one_mechanism_lookup',0,source,dict(target=4,work=20000000,proof_method='decomposition',memory_mb=512,cpu_seconds=120,wall_seconds=240))
 a=batch([t],1)[0];save(root/'decomposition_shor4.json',dict(task=t.to_dict(),answer=a));print('DECOMPOSITION4',a['result'].get('status'),[(p.get('reason'),p.get('width'),p.get('max_states')) for p in a['result'].get('progress',[])],flush=True)
 for seed in range(8):
  tasks=[];inputs=[]
  for style in ('adjacent','nested'):
   g=replace(sample(inp,seed,5),family='flagged',shared=False,rounds=2,flag_style=style,schedule='critical_path',compact_ancillas=True)
   c=compile(inp,g);check(c);e=assess(c);v=verify(c,e);assert v['verified'];inputs.append(dict(genome=g.to_dict(),resources=resources(c),eligibility=e,eligibility_verification=v))
   tasks.append(Task(c.to_dict(),'certify',inp.identity,{'p':.001},'one_mechanism_lookup',seed,source,dict(target=5,work=2000000,proof_method='mitm',memory_mb=512,cpu_seconds=120,wall_seconds=240,proof_directory=str(root/f'seed{seed}_{style}'))))
  answers=batch(tasks,2);save(root/f'seed{seed}.json',dict(inputs=inputs,tasks=[t.to_dict() for t in tasks],answers=answers));print('SEED',seed,[(i['eligibility']['eligible'],a['result'].get('status'),a['result'].get('lower_bound'),a['result'].get('upper_bound')) for i,a in zip(inputs,answers)],flush=True)
 save(root/'complete.json',dict(source=source));print('COMPLETE',root,flush=True)
if __name__=='__main__':main()
