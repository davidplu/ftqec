"""Create and verify a local source/evidence archive; never publish."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
root=Path.cwd().resolve();out=root/'dist/autonomous';out.mkdir(parents=True,exist_ok=True)
assert json.loads((root/'results/autonomous/sequence_status.json').read_text())['status']=='COMPLETE'
source=source_identity();commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
wheel=next(out.glob('ftqec-*.whl'))
with zipfile.ZipFile(wheel) as z:
 checked=[]
 for p in (root/'src/ftqec').rglob('*.py'):
  name=p.relative_to(root/'src').as_posix();assert z.read(name)==p.read_bytes(),name;checked.append(name)
 assert len(checked)==53
save(root/'results/autonomous/release/wheel_verification.json',dict(source=source,files=len(checked),wheel=wheel.name,sha256=hashlib.sha256(wheel.read_bytes()).hexdigest(),status='PASS'))
# Proposed packaging gate is committed into the payload; roll back if verification fails.
a=root/'results/autonomous/acceptance.json';accept=json.loads(a.read_text());accept['gates']['T']=dict(status='PASS',scope='Wheel source equality and complete ZIP member SHA/CRC verification; external artifact manifest records result')
save(a,accept)
r=root/'docs/RESULTS.md';report=r.read_text(encoding='utf-8');report=report.replace('| T | PARTIAL | Package verification is recorded separately in the release manifest |','| T | PASS | Wheel source equality and complete archive member SHA/CRC verification; see external artifact manifest |');r.write_text(report,encoding='utf-8')
files=[]
for folder in ['src','tests','docs','scripts','examples','results','benchmarks','.github']:
 for p in (root/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p) and p.suffix!='.pyc' and p!=root/'results/artifact_manifest.json':files.append(p)
for name in ['README.md','CONTRIBUTING.md','pyproject.toml','.gitignore','.gitattributes','LICENSE','CITATION.cff','CODE_OF_CONDUCT.md']:
 if (root/name).exists():files.append(root/name)
files.append(wheel)
manifest={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
path=out/'FTQEC_autonomous_source_and_evidence.zip'
try:
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(files):z.write(p,p.relative_to(root).as_posix())
  z.writestr('PACKAGE_CONTENTS.json',json.dumps(dict(source=source,base_commit=commit,members=manifest,excluded='Active external artifact manifest is a sidecar to avoid recursive hashing; its previous version is preserved in baseline. Git history is supplied separately.'),sort_keys=True))
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  for name,sha in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==sha,name
  assert len(z.namelist())==len(manifest)+1
except BaseException:
 accept['gates']['T']['status']='FAIL';save(a,accept)
 r.write_text(report.replace('| T | PASS |','| T | FAIL |'),encoding='utf-8');raise
save(root/'results/artifact_manifest.json',dict(source=source,base_commit=commit,status='PASS',archive=str(path.relative_to(root)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,members=manifest,wheel_verified_files=len(checked),zip_crc_and_sha_verified=True,prior_manifest='results/autonomous/baseline/prior_artifact_manifest.json',scope='Local only; no public push or cloud execution'))
print('PACKAGE_VERIFIED',len(manifest),'files',path.stat().st_size,'bytes',flush=True)
