"""Freeze a backend-contract correction without changing the sealed candidate pool."""
import datetime,hashlib,json,shutil,sqlite3,subprocess
from pathlib import Path
from ftqec.results.artifacts import save,digest,source_identity,source_records
from ftqec.execution.runtime import runtime_identity

root=Path(__file__).resolve().parents[2];old=root/'results/phase4/epoch-20261111-v2'
epoch=root/'results/phase4/epoch-20261112-v3';path=epoch/'protocol-A-v3.json'
if path.exists():raise SystemExit('Protocol already frozen')
prior=json.loads((old/'protocol-A-v2.json').read_text());source=source_identity()
regression=old/('adapter-regression-'+source[:12])/'summary.json'
check=json.loads(regression.read_text())
assert check['source']==source and len(check['results'])==2
assert all(r['verification']['verified'] and r['verification']['status']=='CERTIFIED' for r in check['results'])
before=source_records(old/'frozen-A-v2/src/ftqec');after=source_records(root/'src/ftqec')
changed=[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]
assert set(changed)<=set(['experiments/verification.py','experiments/controlled.py','experiments/adaptive.py']),changed
snapshot=epoch/'frozen-A-v3/src';snapshot.mkdir(parents=True,exist_ok=True)
shutil.copytree(root/'src/ftqec',snapshot/'ftqec',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
spec={k:v for k,v in prior.items() if k not in ('identity','created_utc','source','runtime','git_commit','source_snapshot','document_sha256','amendment','supersedes')}
spec.update(schema='controlled-fixed-pool-3',source=source,runtime=runtime_identity(),client_date='2026-11-12',
    created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
    source_snapshot='frozen-A-v3/src',supersedes=prior['identity'],amendment=(root/'docs/PHASE4_PROTOCOL_V3.md').read_text(),
    document_sha256=hashlib.sha256((root/'docs/PHASE4_PROTOCOL_V3.md').read_bytes()).hexdigest(),
    reused_preparation=dict(seed=74011,construction_source=prior['source'],scope='Complete sealed code-only pool; all preparation CPU retained; no promotion answers reused',
        unchanged_scientific_engines=True,changed_files=sorted(changed)),
    engineering_regression=dict(path=str(regression.resolve()),sha256=hashlib.sha256(regression.read_bytes()).hexdigest(),scope='Not a controlled comparison'))
spec['identity']=digest(spec);save(path,spec);save(epoch/'input-code72.json',spec['code'])
origin=old/'fixed-pool/seed-74011/pool';dest=epoch/'fixed-pool/seed-74011/pool';dest.mkdir(parents=True)
with sqlite3.connect((origin/'population.sqlite').resolve().as_uri()+'?mode=ro',uri=True) as db:
    assert not db.execute("SELECT 1 FROM tasks WHERE tier NOT IN ('construct_2bga','screen') LIMIT 1").fetchone()
    assert not db.execute('SELECT 1 FROM candidates WHERE status IS NOT NULL LIMIT 1').fetchone()
    with sqlite3.connect(dest/'population.sqlite') as target:db.backup(target)
for name in ('pool.json','checkpoint.json','controller-1.log','controller-process-1.json'):
    if (origin/name).exists():shutil.copy2(origin/name,dest/name)
pool=json.loads((origin/'pool-accounted.json').read_text())
original_hash=pool.pop('hash');pool.update(protocol=spec['identity'],evaluation_source=source,origin_pool_hash=original_hash,
    provenance='Compilation and initial screening from the complete preserved v2 pool; preparation CPU charged, no promotion results imported')
pool['hash']=digest(pool);save(dest/'pool-accounted.json',pool)
shutil.copytree(old/'frozen-A-v2/src',epoch/'generation-source/src')
archive=epoch/'frozen-A-v3/benchmarks';archive.mkdir(parents=True)
for name in ('run_fixed_pool.py','freeze_v3.py'):shutil.copy2(root/'benchmarks/phase4'/name,archive/name)
print(json.dumps(dict(protocol=str(path),identity=spec['identity'],source=source,shared_preparation_cpu=pool['shared_cpu']),indent=2))
