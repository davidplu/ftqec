"""Freeze adaptive, generation, and transfer settings before their outcomes."""
import datetime,hashlib,json,shutil,subprocess
from pathlib import Path
from ftqec.results.artifacts import save,digest,source_identity
from ftqec.execution.runtime import runtime_identity

root=Path(__file__).resolve().parents[2];epoch=root/'results/phase4/epoch-20261111-adaptive'
if (epoch/'plan.json').exists():raise SystemExit('Adaptive plan already frozen')
base=json.loads((root/'results/phase4/epoch-20261111-v2/protocol-A-v2.json').read_text())
assert source_identity()==base['source'],'Freeze a separate source amendment before changing algorithms'
snapshot=epoch/'frozen/src';snapshot.mkdir(parents=True,exist_ok=True)
shutil.copytree(root/'src/ftqec',snapshot/'ftqec',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
cases=[('main72',base['code'],6,base['policies'],['hybrid']),
       ('generation72',base['code'],6,['frontier'],['random_unfiltered','structured'])]
inputs=root.parent/'ftqec-user-test-20261105/results/2bga/epoch-20261105/normalized'
for name in ('2bga_D6_n24_k2_d4','2bga_D9_n36_k8_d4'):
    cases.append((name,json.loads((inputs/(name+'.json')).read_text()),4,base['policies'],['hybrid']))
plan=dict(source=base['source'],runtime=runtime_identity(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
          created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),seeds=base['generator_seeds'],
          source_snapshot='frozen/src',prerequisite_fixed_pool=str((root/'results/phase4/epoch-20261111-v2').resolve()),
          prerequisite_protocol=base['identity'],driver_sha256=hashlib.sha256((root/'benchmarks/phase4/run_adaptive.py').read_bytes()).hexdigest(),cases=[],
          qualification='Generation comparisons reuse the prospectively identical main72/hybrid/frontier control, with its measured costs; no free proof tasks are transferred.',
          interpretation='An end-only frontier sweep may not activate before a finite compute checkpoint. Report its actual activation, including no activation, rather than substituting sweep-first selection.')
for name,code,target,policies,generators in cases:
    spec=dict(source=base['source'],runtime=runtime_identity(),code=code,settings=dict(base['settings'],target=target),
        candidate_goal=100,total_cpu_checkpoints=[500,1000,2000],hypervolume_reference=base['hypervolume_reference'],
        seeds=base['generator_seeds'],policies=policies,generators=generators,code_label=name,
        boundary='six noisy rounds, physical preparation and readout, unchanged explicit-operation local faults',
        scope='Prospective adaptive experiment; not the fixed-pool sweep-first experiment',parent_protocol=base['identity'])
    spec['identity']=digest(spec);save(epoch/name/'protocol.json',spec)
    plan['cases'].append(dict(name=name,protocol=name+'/protocol.json',identity=spec['identity'],policies=policies,generators=generators))
plan['identity']=digest(plan);save(epoch/'plan.json',plan)
shutil.copy2(root/'benchmarks/phase4/run_adaptive.py',epoch/'frozen/run_adaptive.py')
print(json.dumps(dict(plan=str(epoch/'plan.json'),identity=plan['identity']),indent=2))
