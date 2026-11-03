"""Reproduce interruption exactly after the final candidate becomes durable."""
import json,sys
from pathlib import Path
from ftqec.optimization.engine import Config,optimize
from ftqec.optimization.store import PopulationStore
from ftqec.results.artifacts import source_identity,save
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True);code=json.loads(Path('examples/surface_small.json').read_text());config=Config(storage='sqlite',population=1,window=1,promotion=1,finalists=1,candidate_goal=1,target=2,workers=1,initial_shots=8,further_shots=8,proof_work=200000,memory_mb=256,task_cpu_seconds=60,task_wall_seconds=120,seed=0);original=PopulationStore.put;interrupted=False

def inject(self,row):
 global interrupted
 original(self,row)
 if not interrupted:
  interrupted=True;raise KeyboardInterrupt('Deterministic test interruption immediately after candidate persistence')
PopulationStore.put=inject
try:first=optimize(code,out/'run',config)
finally:PopulationStore.put=original
assert first['status']=='CANCELLED' and first.get('pending')
second=optimize(code,out/'run',config)
record=dict(source=source_identity(),interrupted_status=first['status'],interrupted_generated=first['generated'],resumed_status=second['status'],resumed_generated=second['generated'],pending_after_resume=bool(second.get('pending')),resumed_window_completed=not second.get('pending') and second['generated']>first['generated'])
save(out/'receipt.json',record);print(json.dumps(record),flush=True)