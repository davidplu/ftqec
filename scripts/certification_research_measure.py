import json,time
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
from ftqec.circuits.model import Circuit
from ftqec.execution.tasks import Task,batch
origin=Path('C:/Users/david/ftqec');root=origin/'results/certification_research/campaign_20261102';s=source_identity();old='d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306'
index=json.loads((origin/'results/exports'/old/'finalists/index.json').read_text())['records'];cases=[]
for prefix,name,target in [('db9bf9ac','shor5_low_qubit',5),('b1aad234','shor5_low_qd',5),('04c290a8','hgp3',3)]:
 r=next(r for r in index if r['id'].startswith(prefix));p=Path(r['bundle']);p=p if p.is_absolute() else origin/p
 cases.append(dict(name=name,target=target,circuit=json.loads((p/'circuit.json').read_text())))
p=origin/'results/repair_trajectories'/old/'shor5_six_arm/seed1_mitm.json';packet=json.loads(p.read_text());cases.append(dict(name='shor5_prior_unknown',target=5,circuit=packet['tasks'][0]['circuit']))
methods=['mitm','decomposition','decomposition_span','dp','sat'];protocol=dict(source=s,cases=cases,methods=methods,work=2000000,memory_mb=384,cpu_seconds=60,wall_seconds=120,scope='Frozen matched baseline before algorithm changes. Actual backend and bounds must be read from results; requested method is not a completion claim.')
p=root/'matched_protocol.json'
if p.exists():assert json.loads(p.read_text())==protocol
else:save(p,protocol)
deadline=json.loads((root/'deadline_amendment.json').read_text())['deadline_unix']
for case in cases:
 for method in methods:
  if time.time()+125>=deadline:raise SystemExit('No new uncheckpointable task near deadline')
  path=root/'baseline_packets'/(case['name']+'_'+method+'.json')
  if path.exists():continue
  c=Circuit.from_dict(case['circuit']);task=Task(case['circuit'],'certify',c.code.input_hash,dict(p=.001),'auto',0,s,dict(target=case['target'],proof_method=method,work=2000000,memory_mb=384,cpu_seconds=60,wall_seconds=120,proof_directory=str(root/'proofs'/case['name']/method)))
  answer=batch([task],1,memory_mb=384)[0];save(path,dict(task=task.to_dict(),answer=answer));print(case['name'],method,answer['result'].get('status'),flush=True)
