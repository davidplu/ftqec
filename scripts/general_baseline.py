"""Preserve the completed autonomous epoch before general-certification work."""
import hashlib,json,subprocess,time,shutil,sys
from pathlib import Path
from ftqec.results.artifacts import source_identity,source_records,save
from ftqec.execution.clocks import active_time
root=Path('results/general_competitive/baseline');root.mkdir(parents=True,exist_ok=True)
assert not (root/'audit.json').exists(),'Baseline already exists; preserve it'
source=source_identity();assert source=='e0fc9c0ee3642bc7f14d4bb9354a56af6a98584ca1b2d0eb478e14bfaccf929e'
commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
manifest=json.loads(Path('results/artifact_manifest.json').read_text());bad=[]
for name,sha in manifest['members'].items():
 p=Path(name)
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:bad.append(name)
assert not bad,bad
assert hashlib.sha256(Path(manifest['archive']).read_bytes()).hexdigest()==manifest['sha256']
evidence={p.as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('results','benchmarks') for p in Path(folder).rglob('*') if p.is_file() and root not in p.parents and '__pycache__' not in p.parts}
for name in ('docs/RESULTS.md','docs/LIMITATIONS.md','docs/SCIENTIFIC_PROTOCOL.md','README.md','results/artifact_manifest.json'):
 target=root/'previous'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(name,target)
shutil.copy2(r'C:\Users\david\.codex\attachments\eb4c2b82-c2a0-4b64-910c-0ca51929d603\Pasted text.txt',root/'request_partial.txt')
save(root/'audit.json',dict(commit=commit,source=source,package_version='0.1.0',archive_verified=True,verified_manifest_members=len(manifest['members']),evidence=evidence,source_records=source_records('src/ftqec'),request_ends_mid_item='Section 37, K. Ancilla'))
print('BASELINE_HASH_AUDIT_PASS',len(evidence),'evidence files',flush=True)
start=time.perf_counter();active=active_time()
with (root/'tests.txt').open('w',encoding='utf-8') as out:
 result=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','--basetemp=.private/general-baseline-20261029'],stdout=out,stderr=subprocess.STDOUT)
after=source_identity();save(root/'test_receipt.json',dict(source_before=source,source_after=after,unchanged=after==source,returncode=result.returncode,wall=time.perf_counter()-start,active_wall=active_time()-active))
print((root/'tests.txt').read_text()[-3000:],flush=True)
raise SystemExit(result.returncode if source==after else 3)
