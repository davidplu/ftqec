import time
from pathlib import Path
from ftqec.architectures.references import rotated_surface
from ftqec.architectures.coloring import colored_orders
from ftqec.architectures.population import Genome,compile
from ftqec.results.artifacts import source_identity,save
from ftqec.screening.structural import check
from ftqec.evaluation.resources import resources
from ftqec.certification.exact import certify
root=Path('results/general_competitive/color_development')/source_identity()
for distance in (5,10):
 inp,_=rotated_surface(distance,1);start=time.perf_counter();cpu=time.process_time()
 choice,receipt=colored_orders(inp,distance,0)
 save(root/f'construction{distance}.json',dict(receipt,cpu=time.process_time()-cpu,wall=time.perf_counter()-start))
 print(distance,receipt['status'],receipt['nodes'] if 'nodes' in receipt else receipt,flush=True)
 if choice:
  orders,layers=choice;c=compile(inp,Genome('bare',orders,tuple(range(len(orders))),1,False,schedule='colored',interaction_layers=layers));check(c)
  proof=certify(c,distance,2000000,root/f'proofs{distance}')
  save(root/f'result{distance}.json',dict(source=source_identity(),circuit=c.to_dict(),resources=resources(c),certificate=proof,cpu=time.process_time()-cpu,wall=time.perf_counter()-start))
  print(resources(c),proof['status'],flush=True)
