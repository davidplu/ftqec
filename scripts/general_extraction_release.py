"""Freeze and verify a portable scientific delivery without modifying prior epochs."""
import argparse,hashlib,json,re,subprocess,time,zipfile,shutil
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
root=Path.cwd();source=source_identity();release=Path('results/general_extraction/release')/source;dist=Path('dist/general_extraction')/source

def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()

def git(*args):return subprocess.check_output(['git',*args],text=True).strip()

def audit():
 start=time.perf_counter();old=json.loads(next(Path('results/general_extraction/baseline').glob('*/*/prior_manifest.json')).read_text());checked=0;bad=[]
 for name,sha in old['members'].items():
  p=Path(name)
  if p.parts[0] not in ('results','benchmarks'):continue
  checked+=1
  if not p.exists() or digest(p)!=sha:bad.append(name)
 assert checked>0 and not bad,bad
 report=Path('docs/RESULTS.md').read_text(encoding='utf-8');missing=[]
 for url in re.findall(r'\]\(([^)]+)\)',report):
  if url.startswith('../') and not (Path('docs')/url).exists():missing.append(url)
 assert not missing,missing
 assert set(map(int,re.findall(r'^(\d+)\. ',report,re.M)))==set(range(1,41))
 summary=json.loads((Path('results/general_extraction/report')/source/'summary.json').read_text());assert len(summary['delivery'])==13
 wheel=dist/'ftqec-0.1.0-py3-none-any.whl'
 with zipfile.ZipFile(wheel) as z:
  paths=list(Path('src/ftqec').rglob('*.py'))
  for p in paths:assert z.read(p.relative_to('src').as_posix())==p.read_bytes()
 save(release/'final_audit.json',dict(source=source,historical_scientific_files=checked,mismatches=bad,report_questions=40,broken_report_links=missing,adopted_bundles=13,wheel_python_files=len(paths),wheel_sha256=digest(wheel),wall=time.perf_counter()-start))
 print('AUDIT_PASS',checked,flush=True)

def package():
 start=time.perf_counter();commit=git('rev-parse','HEAD');assert not git('status','--porcelain'),'Commit evidence before packaging'
 files=set()
 for name in git('ls-files').splitlines():
  p=Path(name)
  if p.parts[0] not in ('results','dist') and p.is_file():files.add(p)
 roots=[Path('results/general_extraction')]+[Path('results')/x/source for x in ('non_graphlike','repair_trajectories','fault_diagnosis','certification','pareto','ler','compute','exports','cross_family')]
 for base in roots:
  files.update(p for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 files.add(dist/'ftqec-0.1.0-py3-none-any.whl')
 old=Path('dist/competitive_export/2c806077ca35e80028b6f49add2dbd46390d1d400bb8f7b28452d3f3f038ae58/FTQEC_competitive_research_bundle.zip')
 oldsha=digest(old);assert oldsha=='e438a88788d6e1dcc12764065880373e20549b43e1787311f0883f98953cc750'
 manifest=dict(source=source,evidence_commit=commit,members={p.as_posix():digest(p) for p in sorted(files)},historical_archive=dict(path=old.as_posix(),sha256=oldsha,bytes=old.stat().st_size),scope='All new raw evidence including failed and UNKNOWN proof states, current source and wheel. Historical epochs remain in the separately preserved hash-bound archive. Manifest excludes itself and subsequent package-verification receipts to avoid circular hashes.')
 manifest_path=dist/'artifact_manifest.json';save(manifest_path,manifest)
 archive=dist/'FTQEC_general_extraction_research_bundle.zip';assert not archive.exists()
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for i,p in enumerate(sorted(files)):
   z.write(p,p.as_posix())
   if i%1000==0:print('PACKAGED',i,'/',len(files),flush=True)
  z.write(manifest_path,'artifact_manifest.json')
 print('VERIFYING_ARCHIVE',flush=True)
 with zipfile.ZipFile(archive) as z:
  assert len(z.infolist())==len(files)+1
  for name,sha in manifest['members'].items():
   h=hashlib.sha256()
   with z.open(name) as f:
    for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
   assert h.hexdigest()==sha,name
  assert z.read('artifact_manifest.json')==manifest_path.read_bytes()
 receipt=dict(status='PASS',source=source,evidence_commit=commit,archive=archive.as_posix(),sha256=digest(archive),bytes=archive.stat().st_size,members=len(files)+1,uncompressed_bytes=sum(p.stat().st_size for p in files),manifest=manifest_path.as_posix(),manifest_sha256=digest(manifest_path),all_member_hashes_and_crc_verified=True,historical_archive=manifest['historical_archive'],wall=time.perf_counter()-start)
 save(release/'package_verification.json',receipt);print(json.dumps(receipt),flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['audit','package']);args=parser.parse_args();globals()[args.action]()
