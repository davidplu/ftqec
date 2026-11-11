"""Freeze accounting correction before any promotion-policy outcomes."""
import json,shutil,subprocess,hashlib,datetime
from pathlib import Path
from ftqec.results.artifacts import digest,save,source_identity,source_records
from ftqec.execution.runtime import runtime_identity

root=Path(__file__).resolve().parents[2];old=root/'results/phase4/epoch-20261111'
epoch=root/'results/phase4/epoch-20261111-v2';path=epoch/'protocol-A-v2.json'
if path.exists():raise SystemExit('Protocol already frozen; do not overwrite')
previous=json.loads((old/'protocol-A-v1.json').read_text())
source=source_identity();snapshot=epoch/'frozen-A-v2/src';snapshot.mkdir(parents=True,exist_ok=True)
shutil.copytree(root/'src/ftqec',snapshot/'ftqec',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
assert digest(source_records(snapshot/'ftqec'))==source
amendment=(root/'docs/PHASE4_PROTOCOL_V2.md').read_text()
spec={k:v for k,v in previous.items() if k not in ('identity','created_utc','source','runtime','git_commit','source_snapshot','document_sha256','driver_sha256')}
spec.update(schema='controlled-fixed-pool-2',source=source,runtime=runtime_identity(),
    created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),source_snapshot='frozen-A-v2/src',
    supersedes=previous['identity'],amendment=amendment,
    document_sha256=hashlib.sha256((root/'docs/PHASE4_PROTOCOL_V2.md').read_bytes()).hexdigest(),
    driver_sha256=hashlib.sha256((root/'benchmarks/phase4/run_fixed_pool.py').read_bytes()).hexdigest())
spec['identity']=digest(spec);save(path,spec)
save(epoch/'input-code72.json',spec['code'])
archive=epoch/'frozen-A-v2/benchmarks';archive.mkdir(parents=True)
shutil.copy2(root/'benchmarks/phase4/run_fixed_pool.py',archive/'run_fixed_pool.py')
shutil.copy2(root/'benchmarks/phase4/freeze_v2.py',archive/'freeze_v2.py')
shutil.copy2(root/'docs/PHASE4_PROTOCOL_V2.md',epoch/'frozen-A-v2/PROTOCOL_AMENDMENT.md')
print(json.dumps(dict(protocol=str(path),source=source,identity=spec['identity']),indent=2))
