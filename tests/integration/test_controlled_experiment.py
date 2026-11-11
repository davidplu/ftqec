"""Exercise durable experiment delivery with real isolated worker processes."""
import json
import os
from pathlib import Path
import subprocess
import sys
from ftqec.results.artifacts import digest,save,source_identity
from ftqec.optimization.store import PopulationStore
from tests.scientific.test_repeated_memory import small


def test_fixed_pool_resume_and_independent_policy_accounting(tmp_path):
    spec=dict(source=source_identity(),code=small(),settings=dict(rounds=2,target=2,shots=4,work=200000,noise=.001),
              promotion_cpu_checkpoints=[1000],hypervolume_reference=dict(Q=30,D=300,QD=9000,two_q_gates=1000))
    spec['identity']=digest(spec);save(tmp_path/'protocol.json',spec)
    env=dict(os.environ,PYTHONPATH=str(Path('src').resolve()))
    def run(*args):
        result=subprocess.run([sys.executable,'-m','ftqec.experiments.controlled',*args,'--protocol',str(tmp_path/'protocol.json')],env=env,capture_output=True,text=True)
        assert result.returncode==0,result.stdout+result.stderr
    run('pool','--seed','74001','--count','2','--output',str(tmp_path/'pool'))
    original=(tmp_path/'pool/pool.json').read_bytes()
    run('pool','--seed','74001','--count','2','--output',str(tmp_path/'pool'))
    assert (tmp_path/'pool/pool.json').read_bytes()==original
    for policy in ('direct','frontier'):
        root=tmp_path/policy
        run('compare','--pool',str(tmp_path/'pool/pool.json'),'--seed','174001','--policy',policy,'--output',str(root))
        result=json.loads((root/'comparison.json').read_text())
        assert not result['accounting_censored']
        assert result['checkpoints'][0]['coverage']=='OBSERVED'
        with PopulationStore(root/'population.sqlite',readonly=True) as db:
            worker_cpu=db.worker_cpu();tasks=list(db.packets());assert worker_cpu>0 and tasks
            assert all(t['task']['limits']['cpu_seconds'] is None for t in tasks)
        run('compare','--pool',str(tmp_path/'pool/pool.json'),'--seed','174001','--policy',policy,'--output',str(root))
        with PopulationStore(root/'population.sqlite',readonly=True) as db:assert db.worker_cpu()==worker_cpu
