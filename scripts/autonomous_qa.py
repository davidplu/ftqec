import subprocess,time,json
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
from ftqec.execution.clocks import active_time
root=Path("results/autonomous/release");root.mkdir(parents=True,exist_ok=True)
source=source_identity();start=time.perf_counter();active=active_time()
with (root/"tests.txt").open("w",encoding="utf-8") as stream:
 result=subprocess.run([str(Path(".venv/Scripts/python.exe")),"-m","pytest","-q","-p","no:cacheprovider","--basetemp=.private/autonomous-frozen-final"],stdout=stream,stderr=subprocess.STDOUT)
end=source_identity();save(root/"test_source_receipt.json",dict(source_before=source,source_after=end,unchanged=source==end,returncode=result.returncode,wall=time.perf_counter()-start,active_wall=active_time()-active))
print((root/"tests.txt").read_text()[-4000:])
raise SystemExit(result.returncode if source==end else 3)
