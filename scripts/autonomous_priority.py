"""Execute the frozen target-ten ladder entry early; the ladder reuses its checkpoint."""
import os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):os.environ[key]="1"
import json
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
from ftqec.architectures.references import rotated_surface
from ftqec.codes.distance import certify_code
from ftqec.optimization.engine import Config,optimize
root=Path("results/autonomous/campaign")
assert source_identity()==json.loads((root/"protocol.json").read_text())["source"]
name="surface_target10";p=root/"codes"/(name+".json")
if not p.exists():
 inp,_=rotated_surface(10,1);save(p,inp.to_dict());save(root/"algebraic"/(name+".json"),certify_code(inp.code,10))
cfg=Config(population=8,workers=2,seed=20261028,target=10,strategy="hybrid",initial_shots=64,further_shots=256,finalists=3,proof_work=20000000,decoder="auto",convergence_generations=3)
s=optimize(json.loads(p.read_text()),Path("results/discovery/autonomous")/name,cfg)
print(s["status"],len(s["rows"]),sum(r.get("certify",{}).get("status")=="CERTIFIED" for r in s["rows"]),flush=True)
