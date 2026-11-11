import argparse,json
from pathlib import Path
from ..optimization.engine import Config,optimize
from ..execution.tasks import Task,guarded
from ..results.artifacts import save

def main():
    p=argparse.ArgumentParser(description="FTQEC syndrome-extraction population research")
    sub=p.add_subparsers(dest="command",required=True)
    o=sub.add_parser("optimize");o.add_argument("code",type=Path);o.add_argument("--output",type=Path,default=Path("runs/local"));o.add_argument("--generations",type=int);o.add_argument("--population",type=int,default=24);o.add_argument("--workers",type=int,default=1);o.add_argument("--seed",type=int,default=0);o.add_argument("--target","--target-distance",type=int,default=3);o.add_argument("--strategy",choices=["random","structured","witness","multifidelity","hybrid","costaware","costhybrid"],default="hybrid")
    o.add_argument("--decoder",choices=["auto","matching","one_mechanism_lookup","bposd"],default="auto");o.add_argument("--proof-work",type=int,default=20000000);o.add_argument("--convergence-generations",type=int,default=8)
    o.add_argument("--memory-rounds",type=int,help="Evaluate supplied 2BGA architecture populations in both physical memory sectors")
    o.add_argument('--phase3',action='store_true',help='Use disk-backed paired-memory architecture discovery')
    o.add_argument('--no-finalist-sweep',action='store_true',help='Disable the finite paired-memory run final resource-frontier proof sweep')
    o.add_argument('--experiment-cpu',type=float,help='Finite experiment checkpoint in combined controller and worker CPU seconds; no task timeout')
    o.add_argument("--memory-shots",type=int,default=128,help="Initial shots per memory sector; selected finalists receive a separate 4x batch")
    o.add_argument("--memory-noise",type=float,default=.001,help="Operation-local error probability for physical memory experiments")
    o.add_argument("--explicit-idles",action="store_true",help="Include active storage locations in repeated memory")
    o.add_argument("--synthesis-mode",choices=("legacy","joint"),default="joint")
    o.add_argument("--no-time-limits",action="store_true",help="Disable worker CPU and elapsed-time cutoffs; retain memory safeguards and cancellation")
    o.add_argument("--storage",choices=("auto","json","sqlite"),default="auto");o.add_argument("--window",type=int,default=32);o.add_argument("--promotion",type=int,default=8);o.add_argument("--candidate-goal",type=int)
    cert=sub.add_parser("certify");cert.add_argument("circuit",type=Path);cert.add_argument("--target",type=int,default=9);cert.add_argument("--proof-work",type=int,default=20000000);cert.add_argument("--output",type=Path,required=True)
    for parser in (o,cert):parser.add_argument("--proof-method",choices=("auto","graph","dp","mitm","triples","sat","decomposition","decomposition_legacy","decomposition_span","time_collapse","auto_legacy"),default="auto")
    w=sub.add_parser("worker");w.add_argument("task",type=Path);w.add_argument("output",type=Path)
    c=sub.add_parser("cancel");c.add_argument("output",type=Path)
    e=sub.add_parser("export");e.add_argument("circuit_id");e.add_argument("--run",type=Path,default=Path("runs/local"));e.add_argument("--format",choices=("bundle","stim","schedule-json","circuit-json"),default="bundle");e.add_argument("--output",type=Path,required=True);e.add_argument("--noise-p",type=float)
    v=sub.add_parser("verify-export");v.add_argument("path",type=Path);v.add_argument("--proof-work",type=int,default=20000000);v.add_argument("--require-certified",action="store_true")
    t=sub.add_parser("render-schedule");t.add_argument("schedule",type=Path);t.add_argument("--output",type=Path,required=True);t.add_argument("--start",type=int,default=0);t.add_argument("--stop",type=int);t.add_argument("--qubits",type=int,default=32)
    l=sub.add_parser("list-results");l.add_argument("--run",type=Path,default=Path("runs/local"));l.add_argument("--all",action="store_true")
    b=sub.add_parser('validate-2bga');b.add_argument('code',type=Path);b.add_argument('--output',type=Path,required=True)
    r=sub.add_parser('repeat');r.add_argument('circuit',type=Path);r.add_argument('--rounds',type=int,required=True);r.add_argument('--memory-basis',choices=('X','Z'));r.add_argument('--explicit-idles',action='store_true');r.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.command=='validate-2bga':
        from ..codes.two_block import parse
        result=parse(json.loads(a.code.read_text())).receipt;save(a.output,result);print(json.dumps(result));return
    if a.command=='repeat':
        from ..circuits.model import Circuit
        from ..circuits.repeated import repeat,memory
        from ..screening.structural import check
        c=Circuit.from_dict(json.loads(a.circuit.read_text()));c=memory(c,a.rounds,a.memory_basis,a.explicit_idles) if a.memory_basis else repeat(c,a.rounds)
        check(c);save(a.output,c.to_dict());print(json.dumps(dict(output=str(a.output),rounds=a.rounds,boundary_model=c.boundary_model)));return
    if a.command=='optimize' and a.memory_rounds is not None:
        if a.phase3:
            if a.explicit_idles:raise ValueError('Phase 3 currently preserves the baseline explicit-operation noise model without added idles')
            from ..optimization.phase3 import optimize as phase3
            state=phase3(json.loads(a.code.read_text()),a.output,rounds=a.memory_rounds,target=a.target,candidate_goal=a.candidate_goal,workers=a.workers,seed=a.seed,policy=a.strategy,proof_method=a.proof_method,work=a.proof_work,window=a.window,promotions=a.promotion,shots=a.memory_shots,decoder=a.decoder,noise=a.memory_noise,experiment_cpu=a.experiment_cpu,finalist_sweep=not a.no_finalist_sweep)
            print(json.dumps(dict(status=state['status'],proposals=state['index'],output=str(a.output))));return
        from ..optimization.repeated import optimize as optimize_memory
        state=optimize_memory(json.loads(a.code.read_text()),a.output,a.memory_rounds,a.target,population=a.population,generations=a.generations,workers=a.workers,seed=a.seed,work=a.proof_work,no_time_limits=a.no_time_limits,idles=a.explicit_idles,decoder=a.decoder,proof_method=a.proof_method,shots=a.memory_shots,p=a.memory_noise,strategy=a.strategy,promotion=a.promotion)
        print(json.dumps(dict(status=state['status'],circuits=len(state['rows']),output=str(a.output))));return
    if a.command=="list-results":
        from ..delivery.export import list_results
        print(json.dumps(list_results(a.run,a.all)));return
    if a.command=="render-schedule":
        from ..delivery.timeline import render
        print(json.dumps(render(a.schedule,a.output,a.start,a.stop,a.qubits)));return
    if a.command=="export":
        from ..delivery.export import export_result
        print(json.dumps(export_result(a.run,a.circuit_id,a.output,a.format,a.noise_p)));return
    if a.command=="verify-export":
        from ..delivery.verify import verify_bundle
        result=verify_bundle(a.path,a.proof_work);print(json.dumps(result))
        if a.require_certified and not result.get("positive_certificate_verified"):p.exit(2,"Independent positive certificate was not established.\n")
        return
    if a.command=="certify":
        from ..circuits.model import Circuit
        from ..certification.exact import certify
        c=Circuit.from_dict(json.loads(a.circuit.read_text()));a.output.mkdir(parents=True,exist_ok=True)
        result=certify(c,a.target,a.proof_work,a.output/"proofs",method=a.proof_method);save(a.output/"circuit.json",c.to_dict());save(a.output/"certificate.json",result);print(json.dumps(dict(status=result["status"],target=a.target,lower_bound=result.get("lower_bound"))));return
    if a.command=="cancel":save(a.output/"cancel.json",dict(reason="user cancellation"));return
    if a.command=="worker":save(a.output,guarded(Task(**json.loads(a.task.read_text()))));return
    state=optimize(json.loads(a.code.read_text()),a.output,Config(population=a.population,generations=a.generations,workers=a.workers,seed=a.seed,target=a.target,strategy=a.strategy,decoder=a.decoder,proof_work=a.proof_work,proof_method=a.proof_method,synthesis_mode=a.synthesis_mode,convergence_generations=a.convergence_generations,storage=a.storage,window=a.window,promotion=a.promotion,candidate_goal=a.candidate_goal,task_cpu_seconds=None if a.no_time_limits else 300,task_wall_seconds=None if a.no_time_limits else 600))
    print(json.dumps(dict(status=state["status"],unique_circuits=state.get("unique_circuits",len(state.get("rows",[]))),output=str(a.output))))

if __name__=="__main__":main()
