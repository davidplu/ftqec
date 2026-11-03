"""Prospective distinct-population scaling with separately counted scientific tiers."""
import os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):os.environ[key]="1"
import json,time,gzip,hashlib
from pathlib import Path
import psutil
from ftqec.results.artifacts import source_identity,save
from ftqec.codes.input import load
from ftqec.architectures.population import sample,compile
from ftqec.architectures.references import rotated_surface
from ftqec.circuits.identity import physical_identity
from ftqec.screening.structural import check
from ftqec.evaluation.resources import resources
from ftqec.certification.exact import screen,certify
from ftqec.simulation.monte_carlo import evaluate
from ftqec.optimization.selection import pareto
from ftqec.execution.clocks import active_time
root=Path("benchmarks/population_scaling/autonomous")
root.mkdir(parents=True,exist_ok=True)
source=source_identity();inp,_=rotated_surface(3,1)
protocol=dict(source=source,scientific_implementation_commit="3e50ef90cea15a778181fa8dc24d3056fdf6bb48",seed=31415926,target=3,milestones=[100,1000,10000],input=inp.to_dict(),
              screens="every distinct circuit",simulations="each 100th distinct circuit plus first eight",
              certificates="each 250th distinct circuit plus first eight",shots=128,p=.001,decoder="auto",
              maximum_attempts=20000,scope="finite scaling workload; not an optimization time cutoff",
              driver_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
p=root/"protocol.json"
if p.exists():assert json.loads(p.read_text())==protocol
else:save(p,protocol)
seen=set();counts=dict(generated=0,compiled=0,noiseless=0,screened=0,simulated=0,certification_attempted=0,certified=0,invalid=0)
front=[];all_cost=[]
for file in sorted(root.glob("chunk_*.json.gz")):
 blob=json.loads(gzip.decompress(file.read_bytes()))
 counts=blob["counts"];front=blob["frontier"];all_cost.append(blob["cost"])
 for row in blob["rows"]:seen.add(row["id"])
start=time.perf_counter();active_start=active_time();cpu=time.process_time();peak=psutil.Process().memory_info().rss;pending=[];part=len(all_cost)
while len(seen)<10000 and counts["generated"]<20000:
 if source_identity()!=source:raise RuntimeError("source changed")
 if psutil.virtual_memory().available<512*1024**2:
  print("RESOURCE_SAFETY_INTERVENTION",flush=True);break
 seed=protocol["seed"]+counts["generated"];counts["generated"]+=1
 g=sample(inp,seed,3)
 try:c=compile(inp,g);counts["compiled"]+=1;check(c);counts["noiseless"]+=1
 except ValueError:continue
 cid=physical_identity(c)
 if cid in seen:continue
 seen.add(cid);count=len(seen)
 row=dict(id=cid,seed=seed,genome=g.to_dict(),circuit=c.to_dict(),resources=resources(c))
 row["screen"]=screen(c,100000,target=3);counts["screened"]+=1
 if row["screen"]["status"]=="FAULT_INVALID":counts["invalid"]+=1
 else:
  if count<=8 or count%100==0:
   row["simulation"]=evaluate(c,.001,128,seed,100000,decoder="auto")
   counts["simulated"]+="shots" in row["simulation"]
  if count<=8 or count%250==0:
   row["certify"]=certify(c,3,200000)
   counts["certification_attempted"]+=1
   counts["certified"]+=row["certify"]["status"]=="CERTIFIED"
   if row["certify"]["status"]=="CERTIFIED":front=pareto(front+[dict(id=cid,resources=row["resources"],genome=row["genome"])])
 pending.append(row);peak=max(peak,psutil.Process().memory_info().rss)
 if count%100==0:
  cost=dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-start,active_wall=active_time()-active_start,peak_rss=peak)
  packet=dict(source=source,counts=counts.copy(),rows=pending,frontier=front,cost=cost)
  (root/f"chunk_{part:05d}.json.gz").write_bytes(gzip.compress(json.dumps(packet,sort_keys=True).encode()))
  all_cost.append(cost);pending=[];part+=1;start=time.perf_counter();active_start=active_time();cpu=time.process_time()
  if count in protocol["milestones"]:
   save(root/f"population_{count}.json",dict(source=source,distinct=count,counts=counts,certified_frontier=front,
        cpu=sum(x["cpu"] for x in all_cost),wall=sum(x["wall"] for x in all_cost),active_wall=sum(x["active_wall"] for x in all_cost),peak_rss=max(x["peak_rss"] for x in all_cost),
        scope="one persistent local evaluator; full screening, declared sampled simulation/certification; not 10000 certificates"))
   print("SCALING",count,counts,flush=True)
if pending:
 cost=dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-start,active_wall=active_time()-active_start,peak_rss=peak)
 packet=dict(source=source,counts=counts.copy(),rows=pending,frontier=front,cost=cost,reason="resource intervention or finite generation ceiling")
 (root/f"chunk_{part:05d}.json.gz").write_bytes(gzip.compress(json.dumps(packet,sort_keys=True).encode()))
if len(seen)>=10000:save(root/"complete.json",dict(source=source,distinct=len(seen),counts=counts))
