"""Execute the frozen fixed-pool campaign, retaining whole-controller receipts.

No global timeout. A memory admission failure stops cleanly for later resume.
Use the same command to resume; completed comparisons are not re-run.
"""
import argparse,datetime,hashlib,json,os,random,site,subprocess,sys,time
from pathlib import Path
import psutil
from ftqec.results.artifacts import digest,save
from ftqec.execution.tasks import completed_process_cpu


def invoke(args,root,snapshot,protocol):
    root.mkdir(parents=True,exist_ok=True)
    attempt=len(list(root.glob('controller-process-*.json')))+1
    log=root/f'controller-{attempt}.log'
    env=dict(os.environ,PYTHONPATH=str(snapshot))
    paths=[str(snapshot)]+[p for p in sys.path if 'ftqec-phase4' not in p and p not in ('',str(Path.cwd()))]
    bootstrap='import sys,site,runpy;sys.prefix='+repr(sys.prefix)+';sys.exec_prefix='+repr(sys.exec_prefix)+';sys.path[: ]='+repr(paths)+';'
    bootstrap+='[site.addsitedir(p) for p in '+repr(site.getsitepackages())+'];sys.argv='+repr(['ftqec.experiments.controlled',*args,'--protocol',str(protocol)])+';runpy.run_module("ftqec.experiments.controlled",run_name="__main__")'
    start=time.perf_counter();controller_cpu=time.process_time();peak=0;sample=0
    with log.open('w',encoding='utf-8') as stream:
        process=subprocess.Popen([getattr(sys,'_base_executable',sys.executable),'-S','-c',bootstrap],env=env,stdout=stream,stderr=subprocess.STDOUT)
        print(json.dumps(dict(event='started',pid=process.pid,args=args,log=str(log))),flush=True)
        monitor=psutil.Process(process.pid)
        while process.poll() is None:
            try:
                peak=max(peak,monitor.memory_info().rss);times=monitor.cpu_times();sample=times.user+times.system
            except psutil.NoSuchProcess:pass
            time.sleep(.1)
        process.wait();cpu,scope=completed_process_cpu(process,sample)
    receipt=dict(args=args,pid=process.pid,returncode=process.returncode,whole_controller_cpu=cpu,cpu_scope=scope,
        wall=time.perf_counter()-start,sampled_peak_rss=peak,supervisor_cpu=time.process_time()-controller_cpu,
        finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save(root/f'controller-process-{attempt}.json',receipt)
    print(json.dumps(dict(event='finished',**receipt)),flush=True)
    if process.returncode:raise SystemExit('Controller stopped; inspect preserved log and resume after resolving blocker')
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--protocol',required=True);p.add_argument('--seeds',nargs='*',type=int)
    a=p.parse_args();path=Path(a.protocol).resolve();spec=json.loads(path.read_text());epoch=path.parent
    if digest({k:v for k,v in spec.items() if k!='identity'})!=spec['identity']:raise SystemExit('Protocol hash mismatch')
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=spec['driver_sha256']:raise SystemExit('Driver differs from frozen protocol')
    selected=a.seeds or spec['generator_seeds']
    if any(s not in spec['generator_seeds'] for s in selected):raise SystemExit('Seed outside frozen protocol')
    snapshot=epoch/spec['source_snapshot']
    for seed in selected:
        pool=epoch/'fixed-pool'/f'seed-{seed}'/'pool'
        accounted=pool/'pool-accounted.json'
        if not accounted.exists():
            receipt=invoke(['pool','--output',str(pool),'--seed',str(seed),'--count',str(spec['initial_proposals'])],pool,snapshot,path)
            data=json.loads((pool/'pool.json').read_text())
            receipts=[json.loads(f.read_text()) for f in sorted(pool.glob('controller-process-*.json'))]
            # Keep the original pool manifest immutable. This separately hashed envelope
            # charges the full controller exit tail, including sealing the original pool.
            data['unadjusted_pool_hash']=data.pop('hash')
            cpu=sum(r['whole_controller_cpu'] for r in receipts)
            data['controller']=dict(data['controller'],cpu=cpu,whole_process_receipts=receipts)
            data['shared_cpu']=cpu+sum(t['cpu'] for t in data['tiers'].values())
            data['hash']=digest(data);save(accounted,data)
        policies=list(spec['policies']);random.Random(74000+seed).shuffle(policies)
        order_path=pool.parent/'policy-order.json'
        if not order_path.exists():save(order_path,dict(seed=seed,policies=policies,protocol=spec['identity']))
        for policy in policies:
            output=pool.parent/policy
            if (output/'comparison.json').exists():
                old=json.loads((output/'comparison.json').read_text())
                if old['state']['status'] in ('EXPERIMENT_CHECKPOINT_REACHED','EXHAUSTED_POLICY_QUEUE'):continue
            invoke(['compare','--pool',str(accounted),'--output',str(output),'--policy',policy,'--seed',str(seed+100000)],output,snapshot,path)
    print('Completed selected fixed-pool seed blocks',flush=True)


if __name__=='__main__':main()
