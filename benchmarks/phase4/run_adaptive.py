"""Run preregistered adaptive blocks only after the fixed-pool comparison."""
import argparse,datetime,hashlib,json,os,random,site,subprocess,sys,time
from pathlib import Path
import psutil
from ftqec.results.artifacts import digest,save
from ftqec.execution.tasks import completed_process_cpu


def execute(spec_path,root,snapshot,seed,policy,strategy):
    root.mkdir(parents=True,exist_ok=True);attempt=len(list(root.glob('controller-process-*.json')))+1
    args=['ftqec.experiments.adaptive','--protocol',str(spec_path),'--output',str(root),'--seed',str(seed),'--policy',policy,'--generator',strategy]
    paths=[str(snapshot)]+[p for p in sys.path if 'ftqec-phase4' not in p and p not in ('',str(Path.cwd()))]
    bootstrap='import sys,site,runpy;sys.prefix='+repr(sys.prefix)+';sys.exec_prefix='+repr(sys.exec_prefix)+';sys.path[: ]='+repr(paths)+';'
    bootstrap+='[site.addsitedir(p) for p in '+repr(site.getsitepackages())+'];sys.argv='+repr(args)+';runpy.run_module("ftqec.experiments.adaptive",run_name="__main__")'
    start=time.perf_counter();peak=0;cpu=0;supervisor=time.process_time()
    with (root/f'controller-{attempt}.log').open('w') as log:
        child=subprocess.Popen([getattr(sys,'_base_executable',sys.executable),'-S','-c',bootstrap],stdout=log,stderr=subprocess.STDOUT)
        proc=psutil.Process(child.pid);print(json.dumps(dict(event='started',pid=child.pid,seed=seed,policy=policy,generator=strategy,output=str(root))),flush=True)
        while child.poll() is None:
            try:
                peak=max(peak,proc.memory_info().rss);t=proc.cpu_times();cpu=t.user+t.system
            except psutil.NoSuchProcess:pass
            time.sleep(.1)
        child.wait();cpu,scope=completed_process_cpu(child,cpu)
    receipt=dict(pid=child.pid,returncode=child.returncode,whole_controller_cpu=cpu,cpu_scope=scope,wall=time.perf_counter()-start,
        sampled_peak_rss=peak,supervisor_cpu=time.process_time()-supervisor,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save(root/f'controller-process-{attempt}.json',receipt);print(json.dumps(dict(event='finished',**receipt)),flush=True)
    if child.returncode:raise SystemExit('Stopped at a preserved blocker; inspect controller log before resuming')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True);p.add_argument('--case');p.add_argument('--seeds',nargs='*',type=int);a=p.parse_args()
    path=Path(a.plan).resolve();epoch=path.parent;plan=json.loads(path.read_text())
    if digest({k:v for k,v in plan.items() if k!='identity'})!=plan['identity']:raise SystemExit('Plan hash mismatch')
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=plan['driver_sha256']:raise SystemExit('Frozen driver mismatch')
    # No implicit wait or skipped prerequisite: the main controller decides when to launch.
    fixed=Path(plan['prerequisite_fixed_pool'])
    for seed in plan['seeds']:
        for policy in ('direct','random','resource','legacy','frontier'):
            f=fixed/'fixed-pool'/f'seed-{seed}'/policy/'comparison.json'
            if not f.exists():raise SystemExit('Fixed-pool prerequisite incomplete')
            row=json.loads(f.read_text())
            if row['protocol']!=plan['prerequisite_protocol'] or row['state']['status'] not in ('EXPERIMENT_CHECKPOINT_REACHED','EXHAUSTED_POLICY_QUEUE') or row['accounting_censored']:
                raise SystemExit('Fixed-pool prerequisite unresolved or censored')
    seeds=a.seeds or plan['seeds']
    if any(s not in plan['seeds'] for s in seeds):raise SystemExit('Seed outside frozen plan')
    if a.case and a.case not in {c['name'] for c in plan['cases']}:raise SystemExit('Case outside frozen plan')
    for case in plan['cases']:
        if a.case and case['name']!=a.case:continue
        spec_path=epoch/case['protocol'];spec=json.loads(spec_path.read_text())
        if spec['identity']!=case['identity'] or digest({k:v for k,v in spec.items() if k!='identity'})!=case['identity']:raise SystemExit('Case protocol mismatch')
        for seed in seeds:
            arms=[(policy,strategy) for policy in case['policies'] for strategy in case['generators']]
            random.Random(seed+84000).shuffle(arms)
            for policy,strategy in arms:
                out=epoch/case['name']/f'seed-{seed}'/strategy/policy
                if (out/'comparison.json').exists():
                    old=json.loads((out/'comparison.json').read_text())
                    if old['state']['status'] in ('COMPLETE','EXPERIMENT_CHECKPOINT_REACHED'):continue
                execute(spec_path,out,epoch/plan['source_snapshot'],seed,policy,strategy)
    print('Selected adaptive blocks complete',flush=True)


if __name__=='__main__':main()
