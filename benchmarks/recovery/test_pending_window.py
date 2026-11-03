"""Regression tests installed with the post-study delivery corrections."""
import json
from pathlib import Path
from types import SimpleNamespace
from ftqec.optimization.engine import Config,optimize
from ftqec.optimization.store import PopulationStore
from ftqec.execution import tasks

def test_goal_resume_finishes_durable_pending_window(tmp_path,monkeypatch):
 code=json.loads(Path('examples/surface_small.json').read_text())
 config=Config(storage='sqlite',population=1,window=1,promotion=1,finalists=1,candidate_goal=1,target=2,workers=1,initial_shots=8,further_shots=8,proof_work=200000,memory_mb=256,task_cpu_seconds=60,task_wall_seconds=120,seed=0)
 original=PopulationStore.put;injected=False
 def interrupt_after_write(self,row):
  nonlocal injected
  original(self,row)
  if not injected:injected=True;raise KeyboardInterrupt('test interruption after final candidate persistence')
 with monkeypatch.context() as patch:
  patch.setattr(PopulationStore,'put',interrupt_after_write)
  first=optimize(code,tmp_path,config)
 assert first['status']=='CANCELLED' and first.get('pending')
 second=optimize(code,tmp_path,config)
 assert second['status']=='REQUESTED_CANDIDATE_GOAL_COMPLETED'
 assert not second.get('pending') and second['generated']>first['generated']
 with PopulationStore(tmp_path/'population.sqlite',readonly=True) as db:
  packets=list(db.packets())
 assert sum(p['task']['tier']=='construct' for p in packets)==1
 assert any(p['task']['tier']=='screen' for p in packets)
 assert all(p['answer']['result'].get('reason')!='WORKER_ERROR' for p in packets)

def test_admission_receipt_matches_actual_executor_capacity(monkeypatch):
 original=tasks.ThreadPoolExecutor;observed=[]
 def executor(*args,**kwargs):observed.append(kwargs['max_workers']);return original(*args,**kwargs)
 monkeypatch.setattr(tasks,'ThreadPoolExecutor',executor)
 monkeypatch.setattr(tasks.psutil,'virtual_memory',lambda:SimpleNamespace(available=1280*1024**2))
 monkeypatch.setattr(tasks.os,'cpu_count',lambda:16)
 monkeypatch.setattr(tasks,'retry',lambda task,queued:dict(result=dict(status='TEST_ONLY')))
 answers=tasks.batch([SimpleNamespace(limits={'memory_mb':256}) for _ in range(12)],workers=8,memory_mb=256)
 assert observed==[3]
 assert all(a['admission']['admitted_workers']==observed[0] for a in answers)
 assert all(a['admission']['requested_workers']==8 for a in answers)
 assert all(a['admission']['safety_reserve_bytes']==512*1024**2 for a in answers)