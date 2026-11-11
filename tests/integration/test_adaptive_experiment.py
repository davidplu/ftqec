import json,os,subprocess,sys
from pathlib import Path
from ftqec.results.artifacts import save,digest,source_identity
from ftqec.optimization.store import PopulationStore
from tests.scientific.test_repeated_memory import small


def test_adaptive_worker_pipeline_resume(tmp_path):
    spec=dict(source=source_identity(),code=small(),settings=dict(rounds=2,target=2,shots=4,work=200000,noise=.001),
        candidate_goal=2,total_cpu_checkpoints=[1000],hypervolume_reference=dict(Q=30,D=300,QD=9000,two_q_gates=1000))
    spec['identity']=digest(spec);save(tmp_path/'protocol.json',spec)
    env=dict(os.environ,PYTHONPATH=str(Path('src').resolve()))
    args=[sys.executable,'-m','ftqec.experiments.adaptive','--protocol',str(tmp_path/'protocol.json'),'--output',str(tmp_path/'run'),
          '--seed','74001','--policy','frontier','--generator','hybrid']
    first=subprocess.run(args,capture_output=True,text=True,env=env)
    assert first.returncode==0,first.stdout+first.stderr
    result=json.loads((tmp_path/'run/comparison.json').read_text())
    assert result['state']['status']=='COMPLETE'
    assert result['state']['index']==2 and result['state']['phase']=='final_sweep'
    assert not result['accounting_censored']
    with PopulationStore(tmp_path/'run/population.sqlite',readonly=True) as db:cpu=db.worker_cpu()
    second=subprocess.run(args,capture_output=True,text=True,env=env)
    assert second.returncode==0,second.stdout+second.stderr
    with PopulationStore(tmp_path/'run/population.sqlite',readonly=True) as db:assert db.worker_cpu()==cpu
