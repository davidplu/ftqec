"""Fresh isolated wheel installation with exactly copied offline dependencies."""
import os,sys,json,shutil,subprocess,venv,hashlib,zipfile
from pathlib import Path
from importlib.metadata import distribution
from pip._vendor.packaging.requirements import Requirement
from ftqec.results.artifacts import source_identity,save
from ftqec.execution.runtime import runtime_identity
s=source_identity();repo=Path.cwd();root=repo/'results/large_scale/install'/s;root.mkdir(parents=True,exist_ok=True);envdir=repo/'.private'/('large-scale-install-'+s[:12]);python=envdir/'Scripts/python.exe'
wheel=repo/'dist/large_scale'/s/'ftqec-0.1.0-py3-none-any.whl'
with zipfile.ZipFile(wheel) as archive:
 expected={'ftqec/'+p.relative_to(repo/'src/ftqec').as_posix():p for p in (repo/'src/ftqec').rglob('*.py')}
 assert set(expected)=={n for n in archive.namelist() if n.startswith('ftqec/') and n.endswith('.py')}
 for name,path in expected.items():assert archive.read(name)==path.read_bytes()
if not python.exists():venv.EnvBuilder(with_pip=True).create(envdir)
base=Path(sys.prefix)/'Lib/site-packages';dest=envdir/'Lib/site-packages';pending=[n for n,v in runtime_identity()['packages'].items() if v is not None];seen=set();copied={}
while pending:
 name=pending.pop();dist=distribution(name);key=dist.metadata['Name'].lower()
 if key in seen:continue
 seen.add(key)
 for requirement in dist.requires or []:
  req=Requirement(requirement)
  if req.marker is None or req.marker.evaluate({'extra':''}):pending.append(req.name)
 files={}
 for item in dist.files or []:
  p=Path(dist.locate_file(item)).resolve()
  if not p.is_relative_to(base.resolve()) or not p.is_file() or '__pycache__' in p.parts:continue
  rel=p.relative_to(base.resolve());q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True);sha=hashlib.sha256(p.read_bytes()).hexdigest()
  if not q.exists() or hashlib.sha256(q.read_bytes()).hexdigest()!=sha:shutil.copyfile(p,q)
  assert hashlib.sha256(q.read_bytes()).hexdigest()==sha;files[rel.as_posix()]=sha
 copied[key]=dict(version=dist.version,files=files)
save(root/'offline_dependencies.json',dict(source=s,method='New isolated venv; dependency distribution files copied byte-exact from recorded scientific runtime; FTQEC installed from wheel. No shared system-site-packages, source-path injection, or online resolver.',distributions=copied))
env=dict(os.environ);env.pop('PYTHONPATH',None);calls=[]
def run(args):
 proc=subprocess.run([str(python),*args],cwd=envdir,env=env,text=True,capture_output=True);calls.append(dict(args=args,returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr));save(root/'commands.json',calls);assert proc.returncode==0,calls[-1];return proc.stdout
run(['-m','pip','install','--no-index','--no-deps',str(wheel)])
identity=json.loads(run(['-c','import ftqec,json;from ftqec.results.artifacts import source_identity;from ftqec.execution.runtime import runtime_identity;print(json.dumps(dict(path=ftqec.__file__,source=source_identity(),runtime=runtime_identity())))']))
assert identity['source']==s and Path(identity['path']).is_relative_to(envdir) and identity['runtime']==runtime_identity()
basecli=['-m','ftqec.cli.main'];work=root/'cli_run';args=basecli+['optimize',str(repo/'examples/surface_small.json'),'--output',str(work),'--target','2','--population','2','--generations','1','--workers','1','--storage','sqlite','--window','2','--promotion','2']
run(args);run(args)
listed=json.loads(run(basecli+['list-results','--run',str(work)]));assert listed['results'];cid=listed['results'][0]['circuit_id']
for fmt,name in [('bundle','bundle'),('stim','circuit.stim'),('schedule-json','schedule.json'),('circuit-json','circuit.json')]:
 if not (root/name).exists():run(basecli+['export',cid,'--run',str(work),'--format',fmt,'--output',str(root/name)])
verification=json.loads(run(basecli+['verify-export',str(root/'bundle'),'--require-certified']));assert verification['positive_certificate_verified']
run(basecli+['verify-export',str(root/'schedule.json')])
from ftqec.optimization.store import PopulationStore
with PopulationStore(work/'population.sqlite',readonly=True) as db:state=db.get_meta('state');assert len(state['sessions'])>=2
save(root/'complete.json',dict(status='PASS',source=s,import_identity=identity,checkpoint_sessions=len(state['sessions']),wheel_sha256=hashlib.sha256(wheel.read_bytes()).hexdigest(),source_files=len(expected),verification=verification,qualification='Offline isolated install; dependencies copied from exact recorded distributions, not freshly resolved from a package index.'))
print('ISOLATED_SQLITE_CLI_INSTALL_EXPORT_RESUME_PASS',flush=True)