"""Finite development controls; no final-family claims."""
import json,time
from pathlib import Path
from dataclasses import replace
from ftqec.results.artifacts import source_identity,save
from ftqec.codes.families import shor_product,hamming_hypergraph_product
from ftqec.architectures.population import Genome,compile
from ftqec.architectures.allocation import compact
from ftqec.scheduling.dependencies import reorder
from ftqec.circuits.model import Circuit
from ftqec.screening.structural import check
from ftqec.evaluation.resources import resources
from ftqec.certification.eligibility import assess,verify
from ftqec.execution.tasks import Task,batch


def main():
 source=source_identity();root=Path('results/competitive_export/proof_development')/source/str(time.time_ns());root.mkdir(parents=True)
 old=Path('results/general_competitive/final/0e15b68fc104513af365fe022cb271d7da3408d08a9882d381a9a047f2a08e0c/shor_repair/adjacent_False.json')
 prior=Circuit.from_dict(json.loads(old.read_text())['tasks'][0]['circuit']);cases=[]
 for method in ('list','critical_path'):
  c=reorder(compact(prior),method);cases.append(('shor4_compact_'+method,c,4))
 inp=shor_product(5);save(root/'shor5_input.json',inp.to_dict())
 orders=tuple(tuple(q for q in range(inp.code.n) if (p.x|p.z)>>q&1) for p in inp.code.generators)
 for style in ('adjacent','nested'):
  g=Genome('flagged',orders,tuple(range(len(orders))),shared=False,flag_style=style,schedule='critical_path',compact_ancillas=True)
  cases.append(('shor5_'+style,compile(inp,g),5))
 for name,c,target in cases:
  check(c);e=assess(c);v=verify(c,e);assert v['verified']
  save(root/(name+'_input.json'),dict(circuit=c.to_dict(),resources=resources(c),eligibility=e,eligibility_verification=v,target=target))
  tasks=[Task(c.to_dict(),'certify',c.code.input_hash,{'p':.001},'one_mechanism_lookup',0,source,dict(target=target,work=2000000,proof_method=m,memory_mb=512,cpu_seconds=120,wall_seconds=240,proof_directory=str(root/name/m))) for m in ('decomposition','mitm')]
  answers=batch(tasks,2);save(root/(name+'_answers.json'),dict(tasks=[t.to_dict() for t in tasks],answers=answers))
  print(name,'graph',e['eligible'],'resources',resources(c),'proofs',[(a['result'].get('status'),a['result'].get('upper_bound'),a['result'].get('lower_bound')) for a in answers],flush=True)
 save(root/'complete.json',dict(source=source));print('COMPLETE',root,flush=True)
if __name__=='__main__':main()
