"""Verify immutable pre-existing scientific evidence with streaming hashes."""
from pathlib import Path
import hashlib,json,time,subprocess
from ftqec.results.artifacts import save,source_identity
start=time.perf_counter();cpu=time.process_time();a=json.loads(Path('results/competitive_export/baseline/audit.json').read_text());bad=[]
for name,wanted in a['evidence'].items():
 p=Path(name)
 if not p.exists():bad.append(dict(path=name,reason='missing'));continue
 with p.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
 if actual!=wanted:bad.append(dict(path=name,reason='hash mismatch'))
save('results/competitive_export/preservation.json',dict(source=source_identity(),count=len(a['evidence']),mismatches=bad,cpu=time.process_time()-cpu,wall=time.perf_counter()-start,baseline_commit=a['commit'],scope='Every frozen pre-existing evidence file; documents are preserved as baseline copies and may be updated separately'))
print('PRESERVATION',len(a['evidence']),len(bad),flush=True);assert not bad,bad
