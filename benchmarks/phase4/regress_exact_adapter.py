"""Fresh full-size proof/verification regression after upper-witness schema repair.

These are post-hoc engineering audits, not credited promotion-policy outcomes.
Original packets and certificate provenance are never rewritten.
"""
import json,time
from pathlib import Path
from ftqec.optimization.store import PopulationStore
from ftqec.execution.tasks import Task,batch
from ftqec.results.artifacts import save,digest,source_identity

repo=Path(__file__).resolve().parents[2];old=repo/'results/phase4/epoch-20261111-v2'
spec=json.loads((old/'protocol-A-v2.json').read_text());source=source_identity()
root=old/('adapter-regression-'+source[:12]);root.mkdir(parents=True,exist_ok=True)
with PopulationStore(old/'fixed-pool/seed-74011/random/population.sqlite',readonly=True) as db:
    rows=[db.get(s['id']) for s in db.summaries() if s['resources']['Q']==84]
if len(rows)!=2 or {r['circuit']['experiment']['memory_basis'] for r in rows}!={'X','Z'}:raise ValueError('Expected preserved paired regression input')
start=time.process_time();results=[]
with PopulationStore(root/'population.sqlite',digest(dict(source=source,inputs=[r['id'] for r in rows]))) as db:
    for row in rows:
        c=row['circuit'];cid=row['id']
        for tier in ('certify','verify_exact'):
            payload=c if tier=='certify' else dict(circuit=c,certificate=cert)
            task=Task(payload,tier,digest(c['code']),dict(p=.001),'bposd',94711,source,
                dict(target=6,work=50000000,memory_mb=512,cpu_seconds=None,wall_seconds=None,
                     proof_directory=str((root/cid/tier).resolve())))
            db.queue(task,cid);answer=db.answer(task.identity)
            if answer is None:answer=batch([task],1,512,on_result=lambda t,a:db.complete(t.identity,a))[0]
            if tier=='certify':cert=answer['result']
            else:checked=answer['result']
        result=dict(circuit=cid,resources=row['resources'],basis=c['experiment']['memory_basis'],
            verification=checked,scope='Post-hoc adapter regression, outside controlled policy budgets')
        results.append(result);save(root/(cid+'.json'),result)
        print(json.dumps(dict(circuit=cid,basis=result['basis'],status=checked['status'],verified=checked.get('verified'),resources=row['resources'])),flush=True)
    save(root/'summary.json',dict(source=source,construction_source=spec['source'],worker_cpu=db.worker_cpu(),
        controller_cpu=time.process_time()-start,results=results,scope='Engineering regression, not a frozen policy comparison'))
assert all(r['verification']['status']=='CERTIFIED' and r['verification']['verified'] for r in results)
