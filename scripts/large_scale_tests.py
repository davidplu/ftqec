import subprocess,time
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
s=source_identity();p=Path('results/large_scale/tests')/s/str(time.time_ns());p.mkdir(parents=True);t=time.perf_counter();print(str(p),flush=True)
with (p/'pytest.txt').open('w') as f:r=subprocess.run([r'.venv\Scripts\python.exe','-m','pytest','-q'],stdout=f,stderr=subprocess.STDOUT)
save(p/'receipt.json',dict(source=s,returncode=r.returncode,wall=time.perf_counter()-t));print('TEST_RETURN',r.returncode,flush=True)
