"""Prospectively frozen final experiments, resumable by complete stage packets."""
import json,time,hashlib,subprocess
from pathlib import Path
from dataclasses import replace,asdict
import psutil
from ftqec.results.artifacts import source_identity,source_records,digest,save
from ftqec.execution.runtime import runtime_identity
from ftqec.execution.tasks import Task,batch
from ftqec.optimization.engine import Config,optimize
from ftqec.architectures.population import Genome,compile
from ftqec.architectures.allocation import compact
from ftqec.codes.input import load
from ftqec.codes.families import hamming_hypergraph_product
from ftqec.circuits.model import Circuit
from ftqec.screening.structural import check
from ftqec.evaluation.resources import resources
from ftqec.certification.eligibility import assess,verify as verify_eligibility
from ftqec.delivery.export import export_result
from ftqec.delivery.verify import verify_bundle
from ftqec.scheduling.analysis import analyze

OLD='0e15b68fc104513af365fe022cb271d7da3408d08a9882d381a9a047f2a08e0c'


def main():
 source=source_identity();root=Path('results/competitive_export/final')/source;root.mkdir(parents=True,exist_ok=True)
 protocol=dict(source=source,runtime=runtime_identity(),driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),seeds=[24,32,40],cross_seeds=[24,32],families=['surface','steane','shor_product','hypergraph_product'],methods=['graph','mitm','dp','sat','decomposition'],work=2000000,workers=2,task_memory_mb=512,task_cpu_seconds=120,task_wall_seconds=240,population=4,generations=2,initial_shots=64,further_shots=256,finalists=2,noise_p=.001,decoder='auto',controls=['legacy_hybrid','joint_multifidelity','random','witness','hybrid'],control_seed=24,control_cpu_seconds=60,control_wall_seconds=120,ler=dict(p=.01,shots_per_batch=65536,batches=8,seeds=list(range(81000,81008)),decoder='matching'),scope='Finite prospective study; surface and Shor development disclosed; Hamming HGP family evaluated without outcome-driven tuning; no universal generalization or global optimum claim')
 if (root/'protocol.json').exists():assert json.loads((root/'protocol.json').read_text())==protocol
 else:save(root/'protocol.json',protocol)
 start=time.perf_counter();cpu=time.process_time()
 def task(c,tier,target=3,method='auto',seed=0,shots=65536,p=.001,decoder='matching',certificate=None):
  payload=c.to_dict() if certificate is None else dict(circuit=c.to_dict(),certificate=certificate)
  return Task(payload,tier,c.code.input_hash,{'p':p},decoder,seed,source,dict(target=target,work=2000000,proof_method=method,shots=shots,memory_mb=512,cpu_seconds=120,wall_seconds=240,proof_directory=str(root/'proofs')))
 def stage(name,tasks):
  path=root/(name+'.json')
  if path.exists():
   packet=json.loads(path.read_text());assert packet['source']==source and packet['tasks']==[t.to_dict() for t in tasks];return packet['answers']
  tick=time.perf_counter();cost=time.process_time();answers=batch(tasks,2)
  save(path,dict(source=source,tasks=[t.to_dict() for t in tasks],answers=answers,controller_cpu=time.process_time()-cost,wall=time.perf_counter()-tick));return answers
 def campaign(name,data,target,seed,control=None):
  path=root/'optimizer'/name
  cfg=Config(population=4,generations=2,workers=2,seed=seed,target=target,finalists=2,initial_shots=64,further_shots=256,proof_work=2000000,task_cpu_seconds=120,task_wall_seconds=240)
  if control:
   mode,strategy=control;cfg=replace(cfg,synthesis_mode=mode,strategy=strategy,task_cpu_seconds=60,task_wall_seconds=120)
  if name.startswith('surface10_seed'):cfg=replace(cfg,population=2,generations=1)
  checkpoint=path/'checkpoint.json'
  if checkpoint.exists():
   state=json.loads(checkpoint.read_text())
   if state['status']=='REQUESTED_GENERATIONS_COMPLETED':assert state['source']==source and state['config']==asdict(cfg);return state
  state=optimize(data,path,cfg);print('OPTIMIZER',name,state['status'],len(state['rows']),flush=True);return state
 oldroot=Path('results/general_competitive/final')/OLD
 surface=json.loads((oldroot/'inputs/surface10.json').read_text());states={}
 for seed in (24,32,40):states[f'surface10_seed{seed}']=campaign(f'surface10_seed{seed}',surface,10,seed)
 shor=json.loads(Path('results/autonomous/posthoc_shor_diagnosis/candidate.json').read_text())
 # Only the original code input is used for autonomous family trials.
 shor_code=shor['circuit']['code']
 family_inputs={'steane':json.loads(Path('examples/steane.json').read_text()),'shor_product4':shor_code,'hgp58':hamming_hypergraph_product().to_dict()}
 from competitive_algebraic import css_distance
 for name,data in family_inputs.items():
  tick=time.perf_counter();cost=time.process_time();algebraic=css_distance(load(data).code,max_weight=4);save(root/'algebraic'/f'{name}.json',dict(result=algebraic,cpu=time.process_time()-cost,wall=time.perf_counter()-tick,source=source))
  save(root/'inputs'/f'{name}.json',data)
  for seed in (24,32):states[f'{name}_seed{seed}']=campaign(f'{name}_seed{seed}',data,4 if name=='shor_product4' else 3,seed)
 controls={'legacy_hybrid':('legacy','hybrid'),'joint_multifidelity':('joint','multifidelity'),'random':('joint','random'),'witness':('joint','witness'),'hybrid':('joint','hybrid')}
 for name,policy in controls.items():states['control_'+name]=campaign('control_'+name,surface,10,24,policy)
 # Retained reference/control circuits are loaded only after code-only searches.
 prior_front=json.loads(Path('results/pareto/general_competitive',OLD+'.json').read_text())
 best=min((r for s in states.values() if s['config']['target']==10 for r in s['rows'] if r.get('certify',{}).get('status')=='CERTIFIED'),key=lambda r:r['resources']['QD'])
 from ftqec.codes.distance import certify_code
 algebraic_surface=certify_code(load(surface).code,10);assert algebraic_surface['status']=='CERTIFIED' and algebraic_surface['independent']['verified'];save(root/'algebraic/surface10.json',algebraic_surface)
 c=Circuit.from_dict(best['circuit']);save(root/'best_critical_path.json',analyze(c))
 reference=Circuit.from_dict(json.loads((oldroot/'target10/reference.json').read_text())['tasks'][0]['circuit'])
 stage('controls/reference',[task(reference,'certify',10)])
 seen=set()
 for row in prior_front['discovery']:
  metric=row['resources'];key=(metric['Q'],metric['D'])
  if key in seen:continue
  seen.add(key);oldc=Circuit.from_dict(row['circuit']);stage(f'carry_forward/Q{key[0]}_D{key[1]}',[task(oldc,'certify',10)])
 inp=load(surface);g=Genome.from_dict(best['genome'])
 for slots in (1,25,50,99):
  genome=replace(g,schedule='critical_path',ancilla_slots=slots,interaction_layers=())
  constructed=stage(f'allocation/construct_{slots}',[Task(dict(code_input=inp.to_dict(),genome=genome.to_dict()),'construct',inp.identity,{'p':.001},'matching',0,source,dict(memory_mb=512,cpu_seconds=120,wall_seconds=240))])[0]['result']
  if 'circuit' in constructed:stage(f'allocation/certify_{slots}',[task(Circuit.from_dict(constructed['circuit']),'certify',10)])
 repaired=Circuit.from_dict(json.loads((oldroot/'shor_repair/adjacent_False.json').read_text())['tasks'][0]['circuit'])
 repaired=compact(repaired);check(repaired)
 stage('repair/compressed',[task(repaired,'certify',4,method='mitm')])
 for label,cc,target in [('surface10',c,10),('shor4',repaired,4)]:
  e=assess(cc);v=verify_eligibility(cc,e);assert v['verified'];save(root/'eligibility'/f'{label}.json',dict(receipt=e,independent=v,circuit=cc.to_dict()))
  stage('methods/'+label,[task(cc,'certify',target,method=m) for m in protocol['methods']])
 # The new exact method is exercised directly at target three, including where
 # older methods would return through their shared singleton/pair shortcut.
 steane_positive=next((r for name,s in states.items() if name.startswith('steane') for r in s['rows'] if r.get('certify',{}).get('status')=='CERTIFIED'),None)
 if steane_positive:
  cc=Circuit.from_dict(steane_positive['circuit']);e=assess(cc);v=verify_eligibility(cc,e);assert v['verified'];save(root/'eligibility/steane.json',dict(receipt=e,independent=v,circuit=cc.to_dict()))
  stage('methods/steane_decomposition',[task(cc,'certify',3,method='decomposition')])
 # Fixed new batches; no optional stopping and no pooling with earlier epochs.
 oldstate=json.loads((oldroot/'optimizer/surface10_seed0/checkpoint.json').read_text());previous=Circuit.from_dict(next(r['circuit'] for r in oldstate['rows'] if r.get('certify',{}).get('status')=='CERTIFIED' and r['resources']['D']==12))
 for name,cc in [('discovered',c),('previous_depth12',previous),('reference',reference)]:
  stage('ler/'+name,[task(cc,'simulation',10,seed=seed,p=.01,shots=65536,decoder='matching') for seed in range(81000,81008)])
 # Replay all reported positive and negative final certificates in bounded workers.
 for name,state in states.items():
  rows=[r for r in state['rows'] if r.get('certify',{}).get('status') in ('CERTIFIED','INVALID')]
  if rows:
   answers=stage('audit/'+name,[task(Circuit.from_dict(r['circuit']),'verify',state['config']['target'],certificate=r['certify']) for r in rows])
   assert all(a['result'].get('verified') for a in answers),(name,answers)
  finalists=[r for r in rows if r['certify']['status']=='CERTIFIED']
  choices=finalists or rows or state['rows']
  if choices:
   chosen=min(choices,key=lambda r:r['resources']['QD']);out=root/'exports'/name
   if not out.exists():export_result(root/'optimizer'/name,chosen['id'],out)
   v=verify_bundle(out)
   if chosen.get('certify',{}).get('status')=='CERTIFIED':assert v['positive_certificate_verified']
   save(root/'export_audit'/f'{name}.json',v)
 # Deliver each adopted auxiliary frontier/control circuit through the same
 # public export API, with explicit origin and complete evaluator records.
 auxiliary=[]
 for folder in ('carry_forward','allocation','repair','controls'):
  for path in sorted((root/folder).glob('*.json')):
   packet=json.loads(path.read_text())
   for t,a in zip(packet.get('tasks',[]),packet.get('answers',[])):
    cert=a['result']
    if t['tier']!='certify' or cert.get('status')!='CERTIFIED':continue
    cc=Circuit.from_dict(t['circuit']);cid=digest(cc.to_dict());label=folder+'_'+path.stem
    run=root/'delivery_records'/label;run.mkdir(parents=True,exist_ok=True)
    row=dict(id=cid,circuit=cc.to_dict(),certify=cert,resources=resources(cc),construction=dict(method='retained_control_or_allocation_ablation',origin=str(path)),parent=None)
    requests={a['task']:a};save(run/'tasks'/(a['task']+'.json'),dict(task=t,answer=a))
    for extra in sorted((root/'ler').glob('*.json')):
     data=json.loads(extra.read_text())
     for tt,aa in zip(data['tasks'],data['answers']):
      if tt['circuit']==cc.to_dict():requests[aa['task']]=aa;save(run/'tasks'/(aa['task']+'.json'),dict(task=tt,answer=aa))
    save(run/'checkpoint.json',dict(source=source,code=cc.code.to_dict(),config=dict(p=.001,decoder=t['decoder'],seed=t['seed']),rows=[row],tasks=requests))
    out=root/'exports'/label
    if not out.exists():export_result(run,cid,out)
    v=verify_bundle(out);assert v['positive_certificate_verified'];save(root/'export_audit'/(label+'.json'),v);auxiliary.append(dict(label=label,circuit=cid,run=str(run),bundle=str(out)))
 save(root/'delivery_index.json',dict(source=source,auxiliary=auxiliary,optimizer_runs=[dict(name=name,path=str(root/'optimizer'/name),bundle=str(root/'exports'/name)) for name in states],public_commands='ftqec list-results --run RUN; ftqec export CIRCUIT_ID --run RUN --format bundle --output NEW_DIRECTORY'))
 elapsed=time.perf_counter()-start
 save(root/'complete.json',dict(source=source,driver_session_cpu=time.process_time()-cpu,driver_session_wall=elapsed,peak_controller_working_set=psutil.Process().memory_info().peak_wset,qualification='Session controller costs; worker task records and any prior driver sessions accounted separately'))
 print('FINAL_CAMPAIGN_COMPLETE',root,flush=True)
if __name__=='__main__':main()
