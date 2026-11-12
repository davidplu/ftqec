"""Execute a frozen list of independent 1024-shot physical-memory BP-OSD batches.

The manifest must be sealed before sampling. Rates are per six-round block and
per logical Pauli sector, not per gate, per round, or decoder-independent rates.
"""
import argparse,json,time
from pathlib import Path
from ftqec.execution.tasks import Task,batch
from ftqec.execution.runtime import runtime_identity
from ftqec.execution.locking import RunLock
from ftqec.optimization.store import PopulationStore
from ftqec.experiments.controlled import scalar_tiers
from ftqec.results.artifacts import save,digest,source_identity


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--protocol',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    spec=json.loads(Path(a.protocol).read_text())
    if digest({k:v for k,v in spec.items() if k!='identity'})!=spec['identity']:raise ValueError('Protocol integrity')
    if spec['source']!=source_identity() or spec['runtime']!=runtime_identity():raise ValueError('Frozen source/runtime mismatch')
    if spec['shots']!=1024 or spec['noise_points']!=[.001,.003]:raise ValueError('Unplanned sampling settings')
    root=Path(a.output);root.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    with RunLock(root/'run.lock'),PopulationStore(root/'population.sqlite',spec['identity']) as db:
        previous=db.get_meta('controller',dict(cpu=0.,wall=0.,clean=True,censored=False))
        censored=previous['censored'] or not previous['clean']
        db.set_meta('controller',dict(previous,clean=False,censored=censored))
        outcomes=db.get_meta('outcomes',{})
        try:
            for entry in spec['circuits']:
                circuit=entry['circuit'];cid=digest(circuit)
                if cid!=entry['identity']:raise ValueError('Circuit identity mismatch')
                for noise in spec['noise_points']:
                    seed=int(digest(dict(master=374011,circuit=cid,p=noise,basis=circuit['experiment']['memory_basis']))[:8],16)
                    task=Task(circuit,'simulation',digest(circuit['code']),dict(p=noise),'bposd',seed,spec['source'],
                        dict(shots=spec['shots'],memory_mb=512,cpu_seconds=None,wall_seconds=None,max_decoder_faults=200000,
                             cancel_file=str((root/'cancel.json').resolve())))
                    db.queue(task,cid);answer=db.answer(task.identity)
                    if answer is None:
                        if (root/'cancel.json').exists():raise InterruptedError('Explicit cancellation')
                        answer=batch([task],1,512,on_result=lambda t,r:db.complete(t.identity,r))[0]
                    outcomes[task.identity]=dict(circuit=cid,classification=entry['classification'],label=entry['label'],
                        basis=circuit['experiment']['memory_basis'],result=answer['result'],worker_cpu=answer['cpu'],worker_wall=answer['wall'])
                    db.set_meta('outcomes',outcomes)
                    db.set_meta('controller',dict(cpu=previous['cpu']+time.process_time(),wall=previous['wall']+time.perf_counter()-start,clean=False,censored=censored))
                    save(root/'summary.json',dict(protocol=spec['identity'],outcomes=outcomes,tiers=scalar_tiers(db),
                        qualification='Independent sampler streams; marginal binomial intervals; no decoder-independent or per-round superiority claim'))
                    print(json.dumps(dict(completed_batches=len(outcomes),label=entry['label'],basis=circuit['experiment']['memory_basis'],p=noise,shots=answer['result'].get('shots'),failures=answer['result'].get('failures'))),flush=True)
        finally:
            db.set_meta('controller',dict(cpu=previous['cpu']+time.process_time(),wall=previous['wall']+time.perf_counter()-start,clean=True,censored=censored))


if __name__=='__main__':main()
