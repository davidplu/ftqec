"""Development-only probes; outputs are source-bound, never overwrite prior runs."""
import time
from pathlib import Path
import psutil
from ftqec.architectures.references import rotated_surface
from ftqec.architectures.synthesis import hook_orders
from ftqec.architectures.population import Genome,compile
from ftqec.certification.exact import certify
from ftqec.certification.inventory import forward
from ftqec.scheduling.scheduler import schedule
from ftqec.screening.structural import check
from ftqec.results.artifacts import save,source_identity,digest
root=Path('results/general_competitive/development')/source_identity()
root.mkdir(parents=True,exist_ok=True)
for distance in (5,10):
    inp,_=rotated_surface(distance,1)
    t=time.perf_counter();cpu=time.process_time()
    orders,receipt=hook_orders(inp,distance,0)
    save(root/f'guidance{distance}.json',receipt)
    for method in ('critical_path','conflict_color','resource'):
        c=compile(inp,Genome('bare',orders,tuple(range(len(orders))),1,False,schedule=method))
        check(c)
        s=schedule(c)
        proof=certify(c,distance,2000000,root/f'proofs{distance}_{method}',method='mitm' if distance==5 else 'graph')
        inv=forward(c)
        hyper=sum(d.bit_count()>2 for _,_,d,l,_ in inv.rows())
        inv.close()
        record=dict(source=source_identity(),circuit=c.to_dict(),id=digest(c.to_dict()),schedule=s.to_dict(),Q=c.num_qubits,QD=c.num_qubits*s.depth,certificate=proof,raw_hyperedges=hyper,cpu=time.process_time()-cpu,wall=time.perf_counter()-t,peak_working_set=psutil.Process().memory_info().peak_wset,qualification='Development probe; cumulative timings include guidance and preceding variants')
        save(root/f'probe{distance}_{method}.json',record)
        print(distance,method,c.num_qubits,s.depth,proof['status'],proof.get('lower_bound'),hyper,flush=True)
