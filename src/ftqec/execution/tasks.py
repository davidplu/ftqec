import os,time
from .clocks import active_time,ACTIVE_CLOCK_SCOPE
from dataclasses import dataclass,asdict,field
from .runtime import runtime_identity
from concurrent.futures import ThreadPoolExecutor
import psutil
from ..results.artifacts import digest,source_identity
from ..circuits.model import Circuit

@dataclass(frozen=True)
class Task:
    circuit: dict
    tier: str
    code_identity: str
    noise: dict
    decoder: str
    seed: int
    source: str
    limits: dict
    runtime: dict=field(default_factory=runtime_identity)
    @property
    def identity(self):
        value=asdict(self);value["limits"].pop("cancel_file",None);value["limits"].pop("proof_directory",None)
        return digest(value)
    def to_dict(self):return asdict(self)

def execute(task):
    if task.source!=source_identity():raise ValueError("Scientific source mismatch")
    if task.runtime!=runtime_identity():raise ValueError("Scientific runtime mismatch")
    start=time.perf_counter();cpu=time.process_time()
    if task.tier in ("construct","construct_screen"):
        from ..codes.input import load
        from ..architectures.population import Genome,compile
        from ..screening.structural import check
        from ..evaluation.resources import resources
        from ..optimization.instrumentation import timed
        c=None
        try:
            inp=load(task.circuit["code_input"]);g=Genome.from_dict(task.circuit["genome"])
            proposal=None;proposal_cost=None
            if task.circuit.get("synthesis"):
                from ..architectures.synthesis import generate
                choice,proposal_cost=timed(lambda:generate(inp,task.seed,task.limits.get("target",3),**task.circuit["synthesis"]))
                g,proposal=choice
            c,compile_cost=timed(compile,inp,g)
            structural,structural_cost=timed(check,c)
            metric,resource_cost=timed(resources,c)
            result=dict(status="STRUCTURALLY_VALID",circuit=c.to_dict(),structural=structural,resources=metric,phase_costs=dict(compilation=compile_cost,structural=structural_cost,resources=resource_cost))
            result["genome"]=g.to_dict()
            if proposal is not None:result["construction"]=proposal;result["phase_costs"]["proposal"]=proposal_cost
            if task.tier=="construct_screen":
                from ..certification.exact import screen
                result["screen"],result["phase_costs"]["screen"]=timed(lambda:screen(c,task.limits["work"],target=task.limits.get("target",3)))
        except ValueError as exc:
            result=dict(status="STRUCTURALLY_INVALID",reason=str(exc))
            if c is not None:result["circuit"]=c.to_dict()
        return dict(task=task.identity,result=result,cpu=time.process_time()-cpu,wall=time.perf_counter()-start,rss=psutil.Process().memory_info().rss,pid=os.getpid())
    if task.tier=="verify":
        from ..certification.exact import verify
        c=Circuit.from_dict(task.circuit["circuit"])
        result=verify(c,task.circuit["certificate"],task.limits.get("work",200000))
        return dict(task=task.identity,result=result,cpu=time.process_time()-cpu,wall=time.perf_counter()-start,rss=psutil.Process().memory_info().rss,pid=os.getpid())
    c=Circuit.from_dict(task.circuit)
    if task.tier=="simulation":
        from ..simulation.monte_carlo import evaluate
        result=evaluate(c,task.noise["p"],task.limits["shots"],task.seed,task.limits.get("max_decoder_faults",10000),decoder=task.decoder)
    elif task.tier=="screen":
        from ..certification.exact import screen
        result=screen(c,task.limits["work"],target=task.limits.get("target",3))
    elif task.tier=="certify":
        from ..certification.exact import certify
        result=certify(c,task.limits["target"],task.limits["work"],task.limits.get("proof_directory"),method=task.limits.get("proof_method","auto"))
    else:raise ValueError("Unknown task tier")
    return dict(task=task.identity,result=result,cpu=time.process_time()-cpu,wall=time.perf_counter()-start,rss=psutil.Process().memory_info().rss,pid=os.getpid())

def batch(tasks,workers=1,memory_mb=256,on_result=None):
    if workers<1 or memory_mb<1:raise ValueError("Positive worker/resource configuration")
    memory_mb=max([memory_mb]+[t.limits.get("memory_mb",256) for t in tasks])
    available=psutil.virtual_memory().available;admitted=min(workers,os.cpu_count() or 1,max(0,(available-512*1024**2)//(memory_mb*1024**2)))
    if not admitted:raise MemoryError("Worker admission reserve")
    # Each evaluation is an isolated process, monitored and terminated only by its own supervisor.
    queued=time.perf_counter()
    answers=[]
    with ThreadPoolExecutor(max_workers=admitted) as pool:
        for start in range(0,len(tasks),2*admitted):
            chunk=tasks[start:start+2*admitted]
            for task,answer in zip(chunk,pool.map(lambda t:retry(t,queued),chunk)):
                answers.append(answer)
                if on_result is not None:on_result(task,answer)
    return answers

def guarded(task,queued=None):
    import subprocess,sys,tempfile,json
    from pathlib import Path
    from ..results.artifacts import save
    with tempfile.TemporaryDirectory(prefix="ftqec-") as directory:
        root=Path(directory);serialization_cpu=time.process_time();serialization_wall=time.perf_counter();save(root/"task.json",task.to_dict())
        serialization=dict(cpu=time.process_time()-serialization_cpu,wall=time.perf_counter()-serialization_wall)
        with (root/"stderr.txt").open("w") as log:
            start=time.perf_counter();active_start=active_time()
            process=subprocess.Popen(worker_command(root/"task.json",root/"answer.json"),stdout=log,stderr=log)
            monitor=psutil.Process(process.pid);peak=0;used=0.;reason=None
            while process.poll() is None:
                try:
                    peak=max(peak,monitor.memory_info().rss);t=monitor.cpu_times();used=t.user+t.system
                except psutil.NoSuchProcess:break
                if peak>task.limits.get("memory_mb",256)*1024**2:reason="MEMORY_LIMIT"
                if used>task.limits.get("cpu_seconds",120):reason="CPU_LIMIT"
                if active_time()-active_start>task.limits.get("wall_seconds",180):reason="ACTION_WALL_LIMIT"
                if task.limits.get("cancel_file") and Path(task.limits["cancel_file"]).exists():reason="CANCELLED"
                if reason:process.kill();break
                time.sleep(.02)
            process.wait()
            used,cpu_scope=completed_process_cpu(process,used)
        if reason or process.returncode or not (root/"answer.json").exists():
            return dict(task=task.identity,result=dict(status="UNKNOWN",reason=reason or "WORKER_ERROR",stderr=(root/"stderr.txt").read_text()[-4000:]),cpu=used,wall=time.perf_counter()-start,rss=peak,pid=process.pid,cpu_scope=cpu_scope,active_wall=active_time()-active_start,active_clock_scope=ACTIVE_CLOCK_SCOPE,task_serialization=serialization)
        answer=json.loads((root/"answer.json").read_text())
        if answer.get("pid")!=process.pid:raise RuntimeError("Evaluator PID differs from supervised PID; reject invalid resource accounting")
        peak=max(peak,answer["rss"])
        answer["supervised_pid"]=process.pid
        answer["body_cpu"]=answer["cpu"];answer["body_wall"]=answer["wall"];answer["cpu"]=used;answer["wall"]=time.perf_counter()-start;answer["cpu_scope"]=cpu_scope;answer["task_serialization"]=serialization;answer["peak_rss"]=peak;answer["dispatch_monotonic"]=start;answer["completion_monotonic"]=time.perf_counter();answer["queue_wall"]=start-queued if queued else 0.;answer["active_wall"]=active_time()-active_start;answer["active_clock_scope"]=ACTIVE_CLOCK_SCOPE;return answer

def retry(task,queued=None):
    attempts=[]
    for _ in range(2):
        answer=guarded(task,queued);attempts.append(dict(answer))
        if answer["result"].get("reason")!="WORKER_ERROR":break
    answer=dict(answer);answer["attempts"]=attempts;answer["retry_count"]=len(attempts)-1
    answer["cpu"]=sum(a["cpu"] for a in attempts);answer["wall"]=sum(a["wall"] for a in attempts)
    return answer

def completed_process_cpu(process,fallback):
    if os.name=="nt":
        import ctypes
        from ctypes import wintypes
        created=wintypes.FILETIME();exited=wintypes.FILETIME();kernel=wintypes.FILETIME();user=wintypes.FILETIME()
        call=ctypes.WinDLL("kernel32",use_last_error=True).GetProcessTimes
        call.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4;call.restype=wintypes.BOOL
        if call(wintypes.HANDLE(int(process._handle)),ctypes.byref(created),ctypes.byref(exited),ctypes.byref(kernel),ctypes.byref(user)):
            ticks=lambda t:(t.dwHighDateTime<<32)|t.dwLowDateTime
            return (ticks(kernel)+ticks(user))*1e-7,"completed Windows process kernel+user CPU including startup and output serialization"
    return fallback,"last live whole-process CPU sample; exit tail may be omitted"

def worker_command(task_path,answer_path):
    import sys,site
    if os.name=="nt" and getattr(sys,"_base_executable",None):
        # The Windows venv redirector spawns another interpreter. Launch the real
        # executable directly and reconstruct the parent's exact import context.
        paths=list(sys.path);sites=site.getsitepackages()
        bootstrap="import sys,site,runpy;sys.prefix="+repr(sys.prefix)+";sys.exec_prefix="+repr(sys.exec_prefix)+";sys.path[: ]="+repr(paths)+";"
        bootstrap+="[site.addsitedir(p) for p in "+repr(sites)+"];runpy.run_module('ftqec.execution.worker',run_name='__main__')"
        return [sys._base_executable,"-S","-c",bootstrap,str(task_path),str(answer_path)]
    return [sys.executable,"-m","ftqec.execution.worker",str(task_path),str(answer_path)]
