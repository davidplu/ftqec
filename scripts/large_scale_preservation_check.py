"""Recheck immutable historical delivery bytes and archived member integrity."""
import json,time,hashlib,zipfile
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
s=source_identity();old='d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306';root=Path('results/large_scale/preservation')/s;root.mkdir(parents=True,exist_ok=True)
def sha(stream):
 h=hashlib.sha256()
 for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def file_sha(path):
 with Path(path).open('rb') as f:return sha(f)
start=time.perf_counter();cpu=time.process_time();manifest_path=Path('results/general_extraction/release')/old/'artifact_manifest.json';manifest=json.loads(manifest_path.read_text());archive=Path('dist/general_extraction')/old/'FTQEC_general_extraction_research_bundle.zip'
assert file_sha(archive)=='27c45c0296bed2e4e3ac23299c004422b9127d732428d294fca3023e8ab15108'
checked=0;live_checked=0;missing=[]
with zipfile.ZipFile(archive) as z:
 assert json.loads(z.read('artifact_manifest.json'))==manifest
 for name,expected in manifest['members'].items():
  with z.open(name) as f:assert sha(f)==expected,name
  checked+=1
  if name.startswith('results/') and old in name:
   path=Path(name)
   if path.exists():assert file_sha(path)==expected,name;live_checked+=1
   else:missing.append(name)
assert checked>0
prior=manifest['historical_archive'];assert Path(prior['path']).stat().st_size==prior['bytes'] and file_sha(prior['path'])==prior['sha256']
save(root/'complete.json',dict(source=s,preserved_source=old,archive=str(archive),archive_sha256='27c45c0296bed2e4e3ac23299c004422b9127d732428d294fca3023e8ab15108',archived_members_verified=checked,live_source_bound_result_files_verified=live_checked,archived_but_missing_live_paths=missing,prior_archive_verified=prior,controller_cpu=time.process_time()-cpu,wall=time.perf_counter()-start,scope='Byte-exact prior source and scientific evidence retained in verified historical archives. Current source/documentation may evolve; immutable old-source result paths checked separately where present.'))
print('HISTORICAL_PRESERVATION_VERIFIED',checked,live_checked,len(missing),flush=True)