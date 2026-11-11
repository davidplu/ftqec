"""Matched progress-accounting microbenchmark under the existing 512 MiB ceiling."""
import argparse,json,os,site,subprocess,sys,time
from pathlib import Path
import psutil
from ftqec.optimization.store import PopulationStore
from ftqec.experiments.controlled import scalar_tiers
from ftqec.execution.tasks import completed_process_cpu
from ftqec.results.artifacts import save,digest,source_identity


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('database');p.add_argument('output');p.add_argument('--worker',choices=('payloads','scalars'))
    a=p.parse_args();root=Path(a.output);root.mkdir(parents=True,exist_ok=True)
    if a.worker:
        start=time.process_time()
        with PopulationStore(a.database,readonly=True) as db:
            result=db.totals() if a.worker=='payloads' else scalar_tiers(db)
        result={k:{field:r[field] for field in ('tasks','cpu','summed_wall','peak_rss')} for k,r in result.items()}
        save(root/(a.worker+'-result.json'),dict(source=source_identity(),body_cpu=time.process_time()-start,scalars=result,identity=digest(result)))
        return
    receipts=[]
    for method in ('payloads','scalars'):
        args=[str(Path(__file__).resolve()),str(Path(a.database).resolve()),str(root.resolve()),'--worker',method]
        code='import sys,site,runpy;sys.prefix='+repr(sys.prefix)+';sys.exec_prefix='+repr(sys.exec_prefix)+';sys.path[: ]='+repr(sys.path)+';'
        code+='[site.addsitedir(p) for p in '+repr(site.getsitepackages())+'];sys.argv='+repr(args)+';runpy.run_path(sys.argv[0],run_name="__main__")'
        start=time.perf_counter();peak=0;cpu=0;reason=None
        with (root/(method+'.log')).open('w') as log:
            child=subprocess.Popen([getattr(sys,'_base_executable',sys.executable),'-S','-c',code],stdout=log,stderr=log)
            proc=psutil.Process(child.pid)
            while child.poll() is None:
                try:
                    peak=max(peak,proc.memory_info().rss);t=proc.cpu_times();cpu=t.user+t.system
                    if peak>512*1024**2:reason='MEMORY_LIMIT';child.kill();break
                except psutil.NoSuchProcess:pass
                time.sleep(.01)
            child.wait();cpu,scope=completed_process_cpu(child,cpu)
        receipts.append(dict(method=method,cpu=cpu,cpu_scope=scope,wall=time.perf_counter()-start,peak_rss=peak,
            returncode=child.returncode,status=reason or ('COMPLETE' if child.returncode==0 else 'ERROR')))
    save(root/'receipts.json',dict(source=source_identity(),database=str(Path(a.database).resolve()),receipts=receipts))
    if all(r['status']=='COMPLETE' for r in receipts):
        values=[json.loads((root/(r['method']+'-result.json')).read_text()) for r in receipts]
        assert values[0]['identity']==values[1]['identity'],'Accounting totals disagree'
    print(json.dumps(receipts,indent=2))


if __name__=='__main__':main()
