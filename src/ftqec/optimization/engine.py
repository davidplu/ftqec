from ..circuits.identity import physical_identity
from .instrumentation import timed
from ..execution.clocks import active_time,ACTIVE_CLOCK_SCOPE
from ..execution.runtime import runtime_identity
import json,time,subprocess
from dataclasses import dataclass,asdict
from pathlib import Path
from ..codes.input import load
from ..architectures.population import sample,mutate,recombine,compile,Genome
from ..screening.structural import check
from ..evaluation.resources import resources
from ..execution.tasks import Task,batch
from ..results.artifacts import digest,source_identity,save
from .selection import pareto,promising,reliability_pareto

@dataclass(frozen=True)
class Config:
    population: int=24
    generations: int|None=None
    workers: int=1
    seed: int=0
    p: float=.001
    initial_shots: int=128
    further_shots: int=512
    finalists: int=2
    target: int=3
    proof_method: str="auto"
    synthesis_mode: str="joint"
    proof_work: int=200000
    strategy: str="hybrid"
    decoder: str="auto"
    max_decoder_faults: int=100000
    memory_mb: int=512
    task_cpu_seconds: float=300
    task_wall_seconds: float=600
    convergence_generations: int=8
    storage: str="auto"
    window: int=32
    promotion: int=8
    candidate_goal: int|None=None
    fuse_cheap: bool=True


def _optimize(data,output,config=Config()):
    if config.population<1 or config.initial_shots<1 or config.further_shots<1 or config.finalists<0:raise ValueError("Positive population/shot limits required")
    if config.generations is not None and config.generations<1:raise ValueError("Positive generation count")
    if config.strategy not in ("random","witness","multifidelity","hybrid","costaware","costhybrid"):raise ValueError("Unknown strategy")
    if type(config.target) is not int or config.target<1:raise ValueError("Positive target required")
    if config.workers<1 or config.memory_mb<1 or config.convergence_generations<1:raise ValueError("Positive execution limits required")
    if config.synthesis_mode not in ("legacy","joint"):raise ValueError("Unknown synthesis mode")
    inp=load(data);root=Path(output);root.mkdir(parents=True,exist_ok=True);source=source_identity();identity=digest(dict(code=inp.to_dict(),config=asdict(config),source=source,runtime=runtime_identity()))
    statefile=root/"checkpoint.json";start=time.perf_counter();active_start=active_time();cpu=time.process_time()
    if statefile.exists():
        state=json.loads(statefile.read_text())
        if state["identity"]!=identity:raise ValueError("Resume identity mismatch")
        if state.get("checkpoint_digest")!=digest({k:v for k,v in state.items() if k!="checkpoint_digest"}):raise ValueError("Checkpoint corruption")
        for tid,answer in state["tasks"].items():
            stored=json.loads((root/"tasks"/(tid+".json")).read_text())
            if digest(answer)!=state["task_hashes"].get(tid) or stored!={"task":stored["task"],"answer":answer} or Task(**stored["task"]).identity!=tid:raise ValueError("Cached task corruption")
    else:
        try:commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=Path(__file__).resolve().parents[3],stderr=subprocess.DEVNULL,text=True).strip()
        except (OSError,subprocess.CalledProcessError):commit="UNCOMMITTED"
        state=dict(identity=identity,source=source,runtime=runtime_identity(),commit=commit,code=inp.to_dict(),config=asdict(config),generation=0,rows=[],seen=[],tasks={},task_hashes={},sessions=[])
    def persist():
        state["checkpoint_digest"]=digest({k:v for k,v in state.items() if k!="checkpoint_digest"})
        save(statefile,state)
    def evaluate(rows,tier,shots=0,stream=0):
        tasks=[];todo=[]
        for row in rows:
            task=Task(row["circuit"],tier,inp.identity,dict(p=config.p),config.decoder,config.seed+stream+int(row["id"][:8],16),source,dict(shots=shots,work=config.proof_work,proof_method=config.proof_method,target=config.target,memory_mb=config.memory_mb,cpu_seconds=config.task_cpu_seconds,wall_seconds=config.task_wall_seconds,max_decoder_faults=config.max_decoder_faults,cancel_file=str((root/"cancel.json").resolve()),proof_directory=str((root/"proofs"/row["id"]).resolve())))
            if task.identity not in state["tasks"]:todo.append(task)
            else:
                state["cache_hits"]=state.get("cache_hits",0)+1
                answer=state["tasks"][task.identity]
                stored=json.loads((root/"tasks"/(task.identity+".json")).read_text())
                if digest(answer)!=state["task_hashes"].get(task.identity) or stored!={"task":task.to_dict(),"answer":answer}:raise ValueError("Cached task corruption")
            tasks.append(task)
        answers=batch(todo,config.workers,memory_mb=config.memory_mb) if todo else []
        for task,answer in zip(todo,answers):state["tasks"][task.identity]=answer;state["task_hashes"][task.identity]=digest(answer);save(root/"tasks"/(task.identity+".json"),dict(task=task.to_dict(),answer=answer));persist()
        for row,task in zip(rows,tasks):
            answer=state["tasks"][task.identity];row[tier]=answer["result"]
            if task.identity not in state.setdefault("cost_observation_ids",[]):
                state["cost_observation_ids"].append(task.identity)
                state.setdefault("cost_observations",[]).append(dict(tier=tier,target=config.target,operations=len(task.circuit["operations"]),cpu=answer["cpu"],scientific_body_cpu=answer.get("body_cpu"),retry_count=answer.get("retry_count",0),cpu_scope=answer.get("cpu_scope"),wall=answer["wall"],status=answer["result"].get("status","SIMULATED"),supported=answer["result"].get("reason")!="UNSUPPORTED_PROOF_METHOD",reason=answer["result"].get("reason"),censored=answer["result"].get("status")=="UNKNOWN" and answer["result"].get("reason")!="UNSUPPORTED_PROOF_METHOD"))
    persist()
    try:
        while config.generations is None or state["generation"]<config.generations:
            if (root/"cancel.json").exists():state["status"]="CANCELLED";break
            generation=state["generation"];new=[];compile_cpu=time.process_time();compile_wall=time.perf_counter();compiled=0
            from ..architectures.synthesis import generate
            pending=state.get("pending_generation")
            building=state.get("construction_pending")
            if pending and pending["generation"]==generation:
                new=[r for r in state["rows"] if r["id"] in pending["ids"]]
                first_candidate=config.population
            elif building and building["generation"]==generation:
                new=[r for r in state["rows"] if r["id"] in building["ids"]]
                first_candidate=building["index"];compiled=building.get("compiled",0)
            else:first_candidate=0
            for i in range(first_candidate,config.population):
                if building and building["index"]==i and "genome" in building:
                    g=Genome.from_dict(building["genome"]);construction=building["construction"]
                    parent=next((r for r in state["rows"] if r["id"]==building.get("parent")),None)
                else:
                    seed=config.seed+generation*config.population+i;parent=None
                    if state["rows"] and config.strategy!="random" and i%3:
                        parents=[r for r in state["rows"] if r.get("certify",{}).get("status")=="CERTIFIED"] or state["rows"];parent=parents[seed%len(parents)];g=mutate(inp,Genome.from_dict(parent["genome"]),seed,(parent.get("screen",{}).get("witness") or parent.get("certify",{}).get("witness")) if config.strategy in ("hybrid","witness","costhybrid") else None,target=config.target,compact_ancillas=config.synthesis_mode=="joint")
                        construction=dict(method="mutation",parent=parent["id"])
                        witness=parent.get("screen",{}).get("witness") or parent.get("certify",{}).get("witness")
                        if witness and config.strategy in ("hybrid","witness","costhybrid"):
                            construction.update(method="physical_witness_guided_repair",witness_hash=digest(witness),affected_checks=sorted({f["check"] for f in witness.get("faults",[]) if type(f.get("check")) is int}),repair_family=g.family,flag_style=g.flag_style,qualification="candidate repair; fresh full physical certification required")
                        if i%7==0:g=recombine(g,sample(inp,seed+10**6,config.target))
                    else:g,construction=generate(inp,seed,config.target,guided=config.strategy!="random",parallel=True,joint=config.synthesis_mode=="joint")
                state["construction_pending"]=dict(generation=generation,index=i,ids=[r["id"] for r in new],compiled=compiled,genome=g.to_dict(),construction=construction,parent=parent["id"] if parent else None)
                persist()
                task=Task(dict(code_input=inp.to_dict(),genome=g.to_dict()),"construct",inp.identity,dict(p=config.p),config.decoder,config.seed+generation*config.population+i,source,dict(target=config.target,memory_mb=config.memory_mb,cpu_seconds=config.task_cpu_seconds,wall_seconds=config.task_wall_seconds,cancel_file=str((root/"cancel.json").resolve())))
                if task.identity in state["tasks"]:
                    answer=state["tasks"][task.identity];state["cache_hits"]=state.get("cache_hits",0)+1
                else:
                    # Separate entry point keeps construction and evaluation admission
                    # independently testable; both use the same bounded supervisor.
                    from ..execution.tasks import batch as construction_batch
                    answer=construction_batch([task],1,memory_mb=config.memory_mb)[0]
                    state["tasks"][task.identity]=answer;state["task_hashes"][task.identity]=digest(answer)
                    save(root/"tasks"/(task.identity+".json"),dict(task=task.to_dict(),answer=answer))
                result=answer["result"]
                compiled+=int("circuit" in result)
                if result.get("status")!="STRUCTURALLY_VALID":
                    bucket="construction_unknown" if result.get("status")=="UNKNOWN" else "structural_rejections"
                    state.setdefault(bucket,[]).append(dict(genome=g.to_dict(),task=task.identity,status=result.get("status"),reason=result.get("reason"),construction=construction))
                else:
                    from ..circuits.model import Circuit
                    c=Circuit.from_dict(result["circuit"]);structural=result["structural"];metric=result["resources"]
                    if structural["circuit"]!=digest(c.to_dict()):raise ValueError("Constructed circuit identity mismatch")
                    cid=physical_identity(c)
                    if cid not in state["seen"]:
                        state["seen"].append(cid)
                        row=dict(id=cid,circuit=c.to_dict(),genome=g.to_dict(),construction=construction,parent=parent["id"] if parent else None,structural=structural,resources=dict(metric,rounds=g.rounds),generation=generation,phase_costs=result["phase_costs"],features=dict(fault_locations=sum(o.gate!="BARRIER" for o in c.operations),detectors=len(c.detectors)+len(c.code.generators),logical_observables=2*c.code.k+len(c.observables)))
                        new.append(row);state["rows"].append(row)
                state["construction_pending"]=dict(generation=generation,index=i+1,ids=[r["id"] for r in new],compiled=compiled)
                persist();building=None
            if not pending:state.setdefault("generation_compute",[]).append(dict(generation=generation,generated=config.population,compiled=compiled,unique=len(new),compile_and_check_cpu=time.process_time()-compile_cpu,compile_and_check_wall=time.perf_counter()-compile_wall,scope="Controller only; construction worker costs are in task totals"))
            state.pop("construction_pending",None)
            state["pending_generation"]=dict(generation=generation,ids=[r["id"] for r in new]);persist()
            if config.strategy in ("costaware","costhybrid"):
                from .adaptive import drive
                drive(new,evaluate,state,config)
            else:
                evaluate(new,"screen")
                eligible=[r for r in new if r["screen"]["status"]!="FAULT_INVALID"]
                evaluate(eligible,"simulation",config.initial_shots)
                from ..simulation.sequential import combine
                for row in eligible:
                    if "shots" in row["simulation"]:
                        row["simulation_batches"]=[row["simulation"]]
                        row["simulation"]=combine(row["simulation_batches"])
                simulated=[r for r in eligible if "confidence" in r["simulation"]]
                selected=promising(simulated)
                unresolved=[r for r in eligible if r not in simulated]
                if selected and "first_promising" not in state:state["first_promising"]=dict(session=len(state["sessions"]),elapsed_wall=time.perf_counter()-start)
                if config.strategy in ("hybrid","multifidelity"):
                    evaluate(selected,"simulation",config.further_shots,10**10)
                    for row in selected:
                        if "shots" in row["simulation"]:row["simulation_batches"].append(row["simulation"])
                        row["simulation"]=combine(row["simulation_batches"])
                finalists=sorted(selected,key=lambda r:(r["simulation"]["confidence"][1],r["resources"]["QD"],r["id"]))[:config.finalists]
                finalists+=unresolved[:max(0,config.finalists-len(finalists))]
                evaluate(finalists,"certify")
                if any(r["certify"].get("status")=="CERTIFIED" for r in finalists) and "first_certified" not in state:state["first_certified"]=dict(session=len(state["sessions"]),elapsed_wall=time.perf_counter()-start)
            if any(r.get("certify",{}).get("status")=="CERTIFIED" for r in new) and "first_certified" not in state:
                state["first_certified"]=dict(session=len(state["sessions"]),elapsed_wall=time.perf_counter()-start)
            state.pop("pending_generation",None)
            state["generation"]+=1;state["status"]="RUNNING"
            front=pareto([r for r in state["rows"] if r.get("certify",{}).get("status")=="CERTIFIED"])
            shape=sorted(set(tuple(r["resources"][k] for k in ("Q","D","QD","two_q_gates")) for r in front))
            shape=[list(x) for x in shape]
            state["stagnant_generations"]=state.get("stagnant_generations",0)+1 if shape==state.get("frontier_shape") else 0
            state["frontier_shape"]=shape
            state.setdefault("frontier_history",[]).append(dict(generation=state["generation"],cumulative_sampled_worker_cpu=sum(t["cpu"] for t in state["tasks"].values()),coordinator_cpu=sum(s["cpu"] for s in state["sessions"])+time.process_time()-cpu,certified_pareto=[r["id"] for r in pareto([r for r in state["rows"] if r.get("certify",{}).get("status")=="CERTIFIED"])]))
            state["empty_generations"]=0 if new else state.get("empty_generations",0)+1
            persist()
            if state["empty_generations"]>=4:state["status"]="SAMPLED_NEIGHBORHOOD_PLATEAU";break
            export(state,root)
            if state["stagnant_generations"]>=config.convergence_generations:state["status"]="OPERATIONAL_FRONTIER_PLATEAU";break
        else:state["status"]="REQUESTED_GENERATIONS_COMPLETED"
    except KeyboardInterrupt:state["status"]="CANCELLED"
    except MemoryError as e:state["status"]="RESOURCE_SAFETY_INTERVENTION";state["resource_reason"]=str(e)
    finally:
        state["sessions"].append(dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-start,active_wall=active_time()-active_start,active_clock_scope=ACTIVE_CLOCK_SCOPE));persist();export(state,root)
    return state

def export(state,root):
    rows=state["rows"];certified=[r for r in rows if r.get("certify",{}).get("status")=="CERTIFIED"]
    archives=dict(structurally_valid=[r["id"] for r in rows],resource_pareto=[r["id"] for r in pareto(rows)],
        statistically_promising=[r["id"] for r in promising([x for x in rows if "confidence" in x.get("simulation",{})])],
        fault_invalid=[r["id"] for r in rows if r.get("screen",{}).get("status")=="FAULT_INVALID" or r.get("certify",{}).get("status")=="INVALID"],
        certification_unknown=[r["id"] for r in rows if r.get("certify",{}).get("status")=="UNKNOWN"],certified=[r["id"] for r in certified],certified_pareto=[r["id"] for r in pareto(certified)])
    archives["estimated_resource_ler_pareto"]=[r["id"] for r in reliability_pareto(rows)]
    archives["certified_circuits_estimated_ler_pareto"]=[r["id"] for r in reliability_pareto(certified)]
    save(root/"archives.json",archives)
    tiers={}
    for row in state["tasks"].values():
        task_path=root/"tasks"/(row["task"]+".json")
        tier=json.loads(task_path.read_text())["task"]["tier"]
        bucket=tiers.setdefault(tier,dict(cpu=0.,wall=0.,tasks=0,shots=0,peak_rss=0))
        bucket["cpu"]+=row["cpu"];bucket["wall"]+=row["wall"];bucket["tasks"]+=1;bucket["shots"]+=row["result"].get("shots",0);bucket["peak_rss"]=max(bucket["peak_rss"],row.get("peak_rss",row["rss"]))
    save(root/"compute.json",dict(cache_hits=state.get("cache_hits",0),tiers=tiers,generation_compute=state.get("generation_compute",[]),first_promising=state.get("first_promising"),first_certified=state.get("first_certified"),tasks=len(state["tasks"]),aggregate_worker_cpu=sum(t["cpu"] for t in state["tasks"].values()),worker_wall_sum=sum(t["wall"] for t in state["tasks"].values()),sessions=state["sessions"],unique_circuits=len(rows),scope="Worker CPU and coordinator session CPU separate; no claimed algorithmic speedup"))

def optimize(data,output,config=Config()):
    from ..execution.locking import RunLock
    with RunLock(Path(output)/"run.lock"):
        if config.storage not in ("auto","json","sqlite"):raise ValueError("Unknown population storage")
        if config.storage=="json" and config.candidate_goal is not None:raise ValueError("Candidate goal requires disk-backed storage")
        if config.storage=="sqlite" or (config.storage=="auto" and (config.population>=100 or config.candidate_goal is not None)):
            from .disk_engine import run
            return run(data,output,config)
        return _optimize(data,output,config)
