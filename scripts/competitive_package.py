"""Package the current research epoch and hash the complete retained workspace evidence."""
import hashlib,json,zipfile,time,subprocess
from pathlib import Path
import psutil
from ftqec.results.artifacts import source_identity,save
root=Path.cwd();source=source_identity();out=root/'dist/competitive_export'/source;release=root/'results/competitive_export/release'/source
assert json.loads((release/'clean_install.json').read_text())['status']=='PASS'
assert json.loads((root/'results/competitive_export/preservation.json').read_text())['mismatches']==[]
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
start=time.perf_counter();cpu=time.process_time();commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
files=[]
for folder in ('src','tests','docs','scripts','examples','.github'):
 files += [p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p) and p.suffix!='.pyc']
files += [p for p in (root/'results/competitive_export').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
for base in ('results','benchmarks'):
 for folder in (root/base).iterdir():
  if folder.is_dir() and folder.name!='competitive_export':
   files += [p for p in (folder/'competitive_export').rglob('*') if p.is_file()]
for name in ('README.md','CONTRIBUTING.md','pyproject.toml','.gitignore','.gitattributes','LICENSE','CITATION.cff','CODE_OF_CONDUCT.md'):files.append(root/name)
files += list((root/'dist/competitive_export').glob('*/*.whl'))
files=sorted(set(files));members={p.relative_to(root).as_posix():sha(p) for p in files}
archive=out/'FTQEC_competitive_research_bundle.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p in files:z.write(p,p.relative_to(root).as_posix())
 z.writestr('PACKAGE_CONTENTS.json',json.dumps(dict(source=source,delivery_base_commit=commit,members=members,scope='Current implementation, complete current research epochs, preserved source snapshots, tests, docs, benchmarks and wheels. Full prior historical evidence remains in the previous source-and-scientific-evidence archive identified by the baseline audit; not duplicated here.'),sort_keys=True))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,wanted in members.items():
  with z.open(name) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==wanted,name
save(release/'package_verification.json',dict(source=source,archive=str(archive.relative_to(root)),sha256=sha(archive),bytes=archive.stat().st_size,members=len(members),verified=True,cpu=time.process_time()-cpu,wall=time.perf_counter()-start,peak_working_set=psutil.Process().memory_info().peak_wset,scope='Current research epoch archive, not a duplicate of all historical epochs'))
# Complete manifest covers all retained scientific epochs, including ones outside this incremental archive.
allfiles=[]
for folder in ('src','tests','docs','scripts','examples','results','benchmarks','.github'):
 allfiles += [p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p) and p.suffix!='.pyc' and p!=root/'results/artifact_manifest.json']
for name in ('README.md','CONTRIBUTING.md','pyproject.toml','.gitignore','.gitattributes','LICENSE','CITATION.cff','CODE_OF_CONDUCT.md'):allfiles.append(root/name)
allfiles+=list((root/'dist').rglob('*.whl'))
allmembers={p.relative_to(root).as_posix():sha(p) for p in sorted(set(allfiles))}
save(root/'results/artifact_manifest.json',dict(source=source,delivery_base_commit=commit,status='PASS',archive=str(archive.relative_to(root)),sha256=sha(archive),bytes=archive.stat().st_size,members=allmembers,archive_members=members,zip_crc_and_sha_verified=True,prior_manifest='results/competitive_export/baseline/previous/results/artifact_manifest.json',scope='Manifest covers all retained workspace evidence; archive contains the current research epoch and references the independently preserved prior full archive. No public push or cloud execution.',cost=dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-start,peak_working_set=psutil.Process().memory_info().peak_wset)))
print('PACKAGE_AND_FULL_MANIFEST_VERIFIED',len(members),len(allmembers),archive.stat().st_size,flush=True)

