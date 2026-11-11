"""Freeze before experimental outcomes; never overwrite a protocol."""
import json,shutil,subprocess,hashlib,datetime,sys
from pathlib import Path
from ftqec.results.artifacts import digest,save,source_identity,source_records
from ftqec.execution.runtime import runtime_identity

root=Path(__file__).resolve().parents[2]
epoch=root/'results/phase4/epoch-20261111'
path=epoch/'protocol-A-v1.json'
if path.exists():raise SystemExit('Protocol already frozen; inspect it rather than replace it')
baseline=root.parent/'ftqec-tropidist/results/phase3/epoch-20261109'
source=source_identity()
snapshot=epoch/'frozen-A-v1/src'
snapshot.mkdir(parents=True,exist_ok=True)
shutil.copytree(root/'src/ftqec',snapshot/'ftqec',ignore=shutil.ignore_patterns('__pycache__','*.pyc'),dirs_exist_ok=False)
assert digest(source_records(snapshot/'ftqec'))==source
doc=root/'docs/PHASE4_PROTOCOL.md'
spec=dict(schema='controlled-fixed-pool-1',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
          source=source,runtime=runtime_identity(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
          code=json.loads((baseline/'input-code72.json').read_text()),
          settings=dict(rounds=6,target=6,shots=32,work=50000000,noise=.001),
          generator_seeds=[74011,74023,74039,74051,74071],initial_proposals=100,
          generator='structured',promotion_seed_offset=100000,simulation_seed_rule='promotion seed + first 32 bits SHA256 of exact circuit identity',
          policies=['direct','random','resource','legacy','frontier'],promotion_cpu_checkpoints=[100,250,500,1000],
          hypervolume_reference=dict(Q=200,D=1024,QD=204800,two_q_gates=20000),
          source_snapshot='frozen-A-v1/src',
          document_sha256=hashlib.sha256(doc.read_bytes()).hexdigest(),
          driver_sha256=hashlib.sha256((root/'benchmarks/phase4/run_fixed_pool.py').read_bytes()).hexdigest(),
          baseline_source='e9bcf97c248fa36c850136f68a62df079c6b49a641b5ec471a68ab5e13606489',
          primary_contrast='frontier - legacy paired hypervolume at shared preparation CPU + 1000',
          policy_F='NOT_RUN: no validated cost/progress/resource predictor',
          protocol_document=doc.read_text())
spec['identity']=digest(spec)
save(path,spec)
print(json.dumps(dict(protocol=str(path),identity=spec['identity'],source=source),indent=2))
