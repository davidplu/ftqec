import argparse,json
from pathlib import Path
from ..optimization.engine import Config,optimize
from ..execution.tasks import Task,guarded
from ..results.artifacts import save

def main():
    p=argparse.ArgumentParser(description="FTQEC syndrome-extraction population research")
    sub=p.add_subparsers(dest="command",required=True)
    o=sub.add_parser("optimize");o.add_argument("code",type=Path);o.add_argument("--output",type=Path,default=Path("runs/local"));o.add_argument("--generations",type=int);o.add_argument("--population",type=int,default=24);o.add_argument("--workers",type=int,default=1);o.add_argument("--seed",type=int,default=0);o.add_argument("--target","--target-distance",type=int,default=3);o.add_argument("--strategy",choices=["random","witness","multifidelity","hybrid","costaware","costhybrid"],default="hybrid")
    o.add_argument("--decoder",choices=["auto","matching","one_mechanism_lookup"],default="auto");o.add_argument("--proof-work",type=int,default=20000000);o.add_argument("--convergence-generations",type=int,default=8)
    o.add_argument("--synthesis-mode",choices=("legacy","joint"),default="joint")
    o.add_argument("--no-time-limits",action="store_true",help="Disable worker CPU and elapsed-time cutoffs; retain memory safeguards and cancellation")
    o.add_argument("--storage",choices=("auto","json","sqlite"),default="auto");o.add_argument("--window",type=int,default=32);o.add_argument("--promotion",type=int,default=8);o.add_argument("--candidate-goal",type=int)
    cert=sub.add_parser("certify");cert.add_argument("circuit",type=Path);cert.add_argument("--target",type=int,default=9);cert.add_argument("--proof-work",type=int,default=20000000);cert.add_argument("--output",type=Path,required=True)
    for parser in (o,cert):parser.add_argument("--proof-method",choices=("auto","graph","dp","mitm","sat","decomposition","decomposition_legacy","decomposition_span"),default="auto")
    w=sub.add_parser("worker");w.add_argument("task",type=Path);w.add_argument("output",type=Path)
    c=sub.add_parser("cancel");c.add_argument("output",type=Path)
    e=sub.add_parser("export");e.add_argument("circuit_id");e.add_argument("--run",type=Path,default=Path("runs/local"));e.add_argument("--format",choices=("bundle","stim","schedule-json","circuit-json"),default="bundle");e.add_argument("--output",type=Path,required=True);e.add_argument("--noise-p",type=float)
    v=sub.add_parser("verify-export");v.add_argument("path",type=Path);v.add_argument("--proof-work",type=int,default=20000000);v.add_argument("--require-certified",action="store_true")
    t=sub.add_parser("render-schedule");t.add_argument("schedule",type=Path);t.add_argument("--output",type=Path,required=True);t.add_argument("--start",type=int,default=0);t.add_argument("--stop",type=int);t.add_argument("--qubits",type=int,default=32)
    l=sub.add_parser("list-results");l.add_argument("--run",type=Path,default=Path("runs/local"));l.add_argument("--all",action="store_true")
    a=p.parse_args()
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
