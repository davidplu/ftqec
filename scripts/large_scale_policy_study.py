"""Isolated evaluation-policy comparison on a frozen positive-containing pool."""
import json,time,hashlib
from pathlib import Path
from dataclasses import asdict
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.circuits.model import Circuit
from ftqec.evaluation.resources import resources
from ftqec.execution.tasks import Task,batch
from ftqec.optimization.adaptive import choose
from ftqec.optimization.costs import CostModel
from ftqec.simulation.sequential import combine
s=source_identity();old='d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306';root=Path('results/large_scale/evaluation_policies')/s;root.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(Path(p).read_text())
index=read(Path('results/exports')/old/'finalists/index.json');records=index['records'] if isinstance(index,dict) and 'records' in index else index
if isinstance(records,dict):records=records.get('results',records.get('finalists',[]))
cases=[]
for prefix,name in [('db9bf9ac','shor5_low_qubit'),('b1aad234','shor5_low_qd'),('04c290a8','hgp3_positive')]:
 r=next(x for x in records if x['id'].startswith(prefix));cases.append(dict(name=name,circuit=read(Path(r['bundle'])/'circuit.json'),target=r['target'],prior_truth='CERTIFIED',origin=r['bundle']))
small=Path('results/general_extraction/controls')/old/'exports/physical_separator2/circuit.json';cases.append(dict(name='surface2_positive',circuit=read(small),target=2,prior_truth='CERTIFIED',origin=str(small)))
parent=Path('results/repair_trajectories')/old/'shor5_six_arm/parent_input.json';packet=read(parent)['packet'];cases.append(dict(name='shor5_negative_parent',circuit=packet['task']['circuit'],target=5,prior_truth='INVALID',origin=str(parent)))
for file,name,truth,target in [(Path('results/repair_trajectories')/old/'shor5_six_arm/seed1_mitm.json','shor5_unresolved','UNKNOWN',5),(Path('results/certification')/old/'small_matched/0_decomposition.json','shor3_negative','INVALID',3)]:
 p=read(file);cases.append(dict(name=name,circuit=p['task']['circuit'],target=target,prior_truth=truth,origin=str(file)))
protocol=dict(source=s,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=cases,policies=['direct','fixed','adaptive'],orders=[['direct','fixed','adaptive'],['adaptive','direct','fixed']],shots=256,p=.001,decoder='one_mechanism_lookup',label_work=20000000,policy_work=2000000,scope='Same physical pool under every policy. Prior labels remain distinct from fresh labeling. UNKNOWN is not a negative. Complete labelled-subset retention only; no unlabelled-pool recall claim.')
if (root/'protocol.json').exists():assert read(root/'protocol.json')==protocol
else:save(root/'protocol.json',protocol)
records_out=[];active_policy="label"
def evaluate(case,tier,rep,label=False):
 c=Circuit.from_dict(case['circuit']);work=20000000 if label else 2000000
 task=Task(case['circuit'],tier,c.code.input_hash,dict(p=.001),'one_mechanism_lookup',4100+rep,s,dict(target=case['target'],shots=256,max_decoder_faults=100000,work=work,proof_method='auto',memory_mb=384,cpu_seconds=120 if label else 60,wall_seconds=240 if label else 120,proof_directory=str((root/'proofs'/('label' if label else str(rep)+'_'+active_policy)/case['name']).resolve())))
 a=batch([task],1,memory_mb=384)[0];return dict(task=task.to_dict(),answer=a)
for case in cases:
 p=root/'labels'/(case['name']+'.json')
 if not p.exists():save(p,evaluate(case,'certify',0,True))
 print('LABEL',case['name'],read(p)['answer']['result'].get('status'),flush=True)
for rep,policies in enumerate(protocol['orders']):
 for policy in policies:
  active_policy=policy
  out=root/f'r{rep}_{policy}';out.mkdir(exist_ok=True)
  if (out/'complete.json').exists():continue
  observations=[];rows=[];resumed_cases=0;reused_partial_packets=0;start=time.perf_counter();cpu=time.process_time()
  for case in cases:
   final_path=out/(case['name']+'.json')
   if final_path.exists():
    resumed_cases+=1;old_record=read(final_path);rows.append(old_record)
    for packet in old_record['packets']:
     a=packet['answer'];tier=packet['task']['tier'];observations.append(dict(tier=tier,target=case['target'],operations=len(case['circuit']['operations']),cpu=a['cpu'],status=a['result'].get('status','SIMULATED'),censored=a['result'].get('status')=='UNKNOWN',supported=a['result'].get('reason')!='UNSUPPORTED_PROOF_METHOD'))
    continue
   row=dict(id=case['name'],circuit=case['circuit'],resources=resources(Circuit.from_dict(case['circuit'])),genome=dict(family=case['circuit'].get('experiment',{}).get('family','unknown')));packets=[];decisions=[]
   partial=out/'partial'/(case['name']+'.json');cached=read(partial) if partial.exists() else [];reused_partial_packets+=len(cached)
   def action(tier):
    packet=next((p for p in cached if p['task']['tier']==tier),None)
    if packet is None:packet=evaluate(case,tier,rep);cached.append(packet);save(partial,cached)
    packets.append(packet);a=packet['answer'];row[tier]=a['result'];observations.append(dict(tier=tier,target=case['target'],operations=len(case['circuit']['operations']),cpu=a['cpu'],status=a['result'].get('status','SIMULATED'),censored=a['result'].get('status')=='UNKNOWN',supported=a['result'].get('reason')!='UNSUPPORTED_PROOF_METHOD'))
    if tier=='simulation' and 'shots' in row[tier]:row['simulation']=combine([row[tier]])
   if policy=='direct':action('certify')
   elif policy=='fixed':
    action('screen')
    if row['screen'].get('status')!='FAULT_INVALID':action('simulation');action('certify')
   else:
    for step in range(3):
     decision=choose(row,case['target'],CostModel(observations),1);decisions.append(decision)
     if decision['action'] in ('retain','reject_with_proof'):break
     action(decision['action'])
     if row[decision['action']].get('status')=='UNKNOWN':break
   invalid=row.get('screen',{}).get('status')=='FAULT_INVALID' or row.get('certify',{}).get('status')=='INVALID'
   if not invalid and 'simulation' not in row:action('simulation')
   if case['prior_truth']=='CERTIFIED':assert not invalid,(case['name'],policy,'False rejection of independently certified positive')
   record=dict(case=case['name'],prior_truth=case['prior_truth'],fresh_label=read(root/'labels'/(case['name']+'.json'))['answer']['result'].get('status'),row=row,packets=packets,decisions=decisions,hard_rejected=invalid)
   save(out/(case['name']+'.json'),record);rows.append(record)
  save(out/'complete.json',dict(source=s,policy=policy,rep=rep,resumed_cases=resumed_cases,reused_partial_packets=reused_partial_packets,whole_policy_wall_comparable=(resumed_cases==0 and reused_partial_packets==0),clock_scope='Controller CPU and wall describe this invocation; worker CPU covers all retained packets. Interrupted or cached invocations do not support whole-policy wall comparison.',controller_cpu=time.process_time()-cpu,wall=time.perf_counter()-start,worker_cpu=sum(p['answer']['cpu'] for r in rows for p in r['packets']),known_positive_retained=sum(r['prior_truth']=='CERTIFIED' and not r['hard_rejected'] for r in rows),known_positive_total=sum(r['prior_truth']=='CERTIFIED' for r in rows),false_hard_rejections=sum(r['prior_truth']=='CERTIFIED' and r['hard_rejected'] for r in rows)))
  print('POLICY',rep,policy,'COMPLETE',flush=True)
save(root/'complete.json',dict(source=s,scope='All declared pool policies finished; interpret costs using their actual raw worker/controller records.'))
