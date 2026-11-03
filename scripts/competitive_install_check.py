"""Exercise installed public commands without checkout import paths."""
import subprocess,json,os,hashlib,zipfile,ftqec
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
root=Path.cwd();source=source_identity();venv=root/('.private/competitive-install-'+source[:12]);python=venv/'Scripts/python.exe';out=root/'results/competitive_export/release'/source;out.mkdir(parents=True,exist_ok=True)
env=dict(os.environ);env.pop('PYTHONPATH',None);records=[]
def run(args):
 r=subprocess.run([str(python),*args],cwd=venv,env=env,text=True,capture_output=True);records.append(dict(args=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(out/'cli_attempts.json',records);assert r.returncode==0,records[-1];return r.stdout
identity=json.loads(run(['-c','import ftqec,json;from ftqec.results.artifacts import source_identity;print(json.dumps(dict(path=ftqec.__file__,source=source_identity())))']));assert str(venv).lower() in identity['path'].lower() and identity['source']==source
base=['-m','ftqec.cli.main'];work=out/'cli_run'
args=base+['optimize',str(root/'examples/surface_small.json'),'--output',str(work),'--target','2','--population','2','--generations','1','--workers','1']
run(args);run(args)
state=json.loads((work/'checkpoint.json').read_text());assert len(state['sessions'])==2
listed=json.loads(run(base+['list-results','--run',str(work)]));assert listed['results'];cid=listed['results'][0]['circuit_id']
for fmt,name in [('bundle','bundle'),('stim','circuit.stim'),('schedule-json','schedule.json'),('circuit-json','circuit.json')]:run(base+['export',cid,'--run',str(work),'--format',fmt,'--output',str(out/name)])
v=json.loads(run(base+['verify-export',str(out/'bundle'),'--require-certified']));assert v['positive_certificate_verified']
run(base+['verify-export',str(out/'schedule.json')]);run(base+['render-schedule',str(out/'schedule.json'),'--output',str(out/'timeline.svg')])
wheel=root/'dist/competitive_export'/source/'ftqec-0.1.0-py3-none-any.whl'
with zipfile.ZipFile(wheel) as z:
 package=Path(ftqec.__file__).parent;files=list(package.rglob('*.py'))
 for p in files:assert z.read('ftqec/'+p.relative_to(package).as_posix())==p.read_bytes()
save(out/'clean_install.json',dict(status='PASS',source=source,import_identity=identity,checkpoint_sessions=2,wheel_sha256=hashlib.sha256(wheel.read_bytes()).hexdigest(),wheel_source_files=len(files),certificate_verified=v['positive_certificate_verified'],commands=records))
print('CLEAN_INSTALL_CLI_EXPORT_RESUME_PASS',flush=True)
