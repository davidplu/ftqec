import subprocess,json,os,hashlib,zipfile
from pathlib import Path
from ftqec.results.artifacts import save,source_identity
root=Path.cwd();source=source_identity();python=root/('.private/general-install-'+source[:12]+'/Scripts/python.exe');cwd=python.parents[1];out=root/'results/general_competitive/release'/source/'cli_smoke';env=dict(os.environ);env.pop('PYTHONPATH',None)
probe=subprocess.check_output([str(python),'-c','import ftqec,json;from ftqec.results.artifacts import source_identity;print(json.dumps(dict(path=ftqec.__file__,source=source_identity())))'],cwd=cwd,env=env,text=True)
identity=json.loads(probe);assert str(cwd).lower() in identity['path'].lower();assert identity['source']==source
cmd=[str(python),'-m','ftqec.cli.main','optimize',str(root/'examples/surface_small.json'),'--output',str(out),'--target-distance','3','--population','2','--generations','1','--workers','1','--proof-method','mitm']
runs=[]
for _ in range(2):
 r=subprocess.run(cmd,cwd=cwd,env=env,text=True,capture_output=True);runs.append(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,runs[-1]
state=json.loads((out/'checkpoint.json').read_text());assert len(state['sessions'])==2
wheel=root/'dist/general_competitive'/source/'ftqec-0.1.0-py3-none-any.whl'
with zipfile.ZipFile(wheel) as z:
 names=[]
 for p in (root/'src/ftqec').rglob('*.py'):
  name=p.relative_to(root/'src').as_posix();assert z.read(name)==p.read_bytes();names.append(name)
save(out.parent/'clean_install.json',dict(status='PASS',source=source,import_identity=identity,commands=cmd,runs=runs,checkpoint_sessions=2,wheel_sha256=hashlib.sha256(wheel.read_bytes()).hexdigest(),wheel_source_files=len(names),scientific_status=[r.get('certify',{}).get('status') for r in state['rows']]))
print('CLEAN_INSTALL_CLI_RESUME_PASS',len(names),flush=True)
