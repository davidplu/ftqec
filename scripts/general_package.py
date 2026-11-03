"""Stream-verify a local source/evidence delivery; never push or publish."""
import hashlib,json,subprocess,zipfile,sys,time
import psutil
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
started=time.perf_counter();cpu_started=time.process_time()
root=Path.cwd().resolve();source=source_identity();release=root/'results/general_competitive/release'/source;out=root/'dist/general_competitive'/source
assert json.loads((root/'results/general_competitive/final'/source/'complete.json').read_text())['source']==source
assert json.loads((root/'results/general_competitive/summary.json').read_text())['scientific_audit']
assert json.loads((release/'clean_install.json').read_text())['status']=='PASS'
commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def build():
 files=[]
 for folder in ('src','tests','docs','scripts','examples','results','benchmarks','.github'):
  files += [p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p) and p.suffix!='.pyc' and p!=root/'results/artifact_manifest.json']
 for name in ('README.md','CONTRIBUTING.md','pyproject.toml','.gitignore','.gitattributes','LICENSE','CITATION.cff','CODE_OF_CONDUCT.md'):
  if (root/name).exists():files.append(root/name)
 files+=list((root/'dist').rglob('*.whl'))
 members={p.relative_to(root).as_posix():sha(p) for p in files}
 archive=out/'FTQEC_source_and_scientific_evidence.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for p in sorted(files):z.write(p,p.relative_to(root).as_posix())
  z.writestr('PACKAGE_CONTENTS.json',json.dumps(dict(source=source,delivery_base_commit=commit,members=members,scope='All retained source-bound evidence, including failed/interrupted epochs. Active external manifest excluded to avoid recursion. Prior source wheels and source snapshots included; Git history supplied separately.'),sort_keys=True))
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(members)+1
  for name,value in members.items():
   with z.open(name) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==value,name
 return archive,members
archive,members=build()
save(release/'archive_precheck.json',dict(source=source,status='PASS',members=len(members),cpu=time.process_time()-cpu_started,wall=time.perf_counter()-started,peak_working_set=psutil.Process().memory_info().peak_wset,scope='Complete first-pass streaming SHA-256 and ZIP CRC verification before final report promotion'))
subprocess.run([sys.executable,'scripts/general_report.py'],check=True)
archive,members=build()
save(root/'results/artifact_manifest.json',dict(source=source,delivery_base_commit=commit,status='PASS',archive=archive.relative_to(root).as_posix(),sha256=sha(archive),bytes=archive.stat().st_size,members=members,wheel_verified_files=57,zip_crc_and_sha_verified=True,packaging_cost=dict(cpu=time.process_time()-cpu_started,wall=time.perf_counter()-started,peak_working_set=psutil.Process().memory_info().peak_wset,cpu_scope='Packaging interpreter only; report subprocess CPU excluded; wall includes report subprocess'),prior_manifest='results/general_competitive/baseline/previous/results/artifact_manifest.json',scope='Local delivery only; no public push or cloud execution'))
print('FINAL_ARCHIVE_VERIFIED',len(members),archive.stat().st_size,sha(archive),flush=True)
