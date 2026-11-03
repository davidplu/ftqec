"""Replay evidence from the isolated policy study; never infer truth from timeout."""
import argparse, hashlib, json, time
from pathlib import Path
from ftqec.results.artifacts import source_identity, save, digest
from ftqec.execution.tasks import Task, batch
from ftqec.circuits.model import Circuit
from ftqec.faults.verification import verify_witness

parser=argparse.ArgumentParser()
parser.add_argument('--wait',action='store_true')
parser.add_argument('--freeze-only',action='store_true')
args=parser.parse_args()
s=source_identity()
root=Path('results/large_scale/policy_evidence_audit')/s
root.mkdir(parents=True,exist_ok=True)
study=Path('results/large_scale/evaluation_policies')/s
upstream=Path('results/large_scale/supplemental_validation')/s/'state.json'
def read(p): return json.loads(p.read_text())
protocol=dict(source=s,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),upstream=str(upstream),study=str(study),work=20000000,memory_mb=384,cpu_seconds=120,wall_seconds=240,scope='Fresh bounded independent positive proof replay and independent legal harmful-fault replay for every label and policy result. Complete-pool recall remains UNKNOWN if any label is unresolved. Group resource comparisons by identical code input and requested target. Validation costs are separate from policy costs.')
if (root/'protocol.json').exists(): assert read(root/'protocol.json')==protocol
else: save(root/'protocol.json',protocol)
if args.freeze_only: print('POLICY_AUDIT_PROTOCOL_FROZEN'); raise SystemExit(0)
if args.wait:
 save(root/'state.json',dict(source=s,status='WAITING_FOR_SUPPLEMENTAL_VALIDATION'))
 while True:
  if (root/'cancel.json').exists(): save(root/'state.json',dict(source=s,status='CANCELLED')); raise SystemExit(2)
  status=read(upstream).get('status') if upstream.exists() else 'WAITING'
  if status=='COMPLETE_FINAL_REPORT_REQUIRED': break
  if status in ('BLOCKED_UPSTREAM','STAGE_FAILED','CANCELLED'):
   save(root/'state.json',dict(source=s,status='BLOCKED_UPSTREAM',upstream=read(upstream))); raise SystemExit(2)
  time.sleep(5)
assert (study/'complete.json').exists()
assert source_identity()==s
save(root/'state.json',dict(source=s,status='RUNNING'))
start=time.perf_counter(); cpu=time.process_time()
cases=read(study/'protocol.json')['cases']; checks=[]; unresolved=[]

def check(packet, origin):
 task=Task(**packet['task']); answer=packet['answer']; result=answer['result']
 assert task.source==s and task.identity==answer['task']
 c=Circuit.from_dict(task.circuit); exact=digest(c.to_dict())
 assert task.code_identity==c.code.input_hash
 status=result.get('status','SIMULATED'); target=task.limits['target']
 checked=dict(origin=origin,circuit=exact,code=c.code.input_hash,target=target,status=status)
 if status=='CERTIFIED':
  assert result['source']==s and result['circuit']==exact and result.get('independent',{}).get('verified')
  key=digest(dict(circuit=exact,certificate=result)); path=root/'positive_replays'/(key+'.json')
  verifier=Task(dict(circuit=c.to_dict(),certificate=result),'verify',c.code.input_hash,task.noise,task.decoder,0,s,dict(work=protocol['work'],memory_mb=protocol['memory_mb'],cpu_seconds=protocol['cpu_seconds'],wall_seconds=protocol['wall_seconds']))
  if path.exists(): replay=read(path); assert replay['task']==verifier.to_dict()
  else: replay=dict(task=verifier.to_dict(),answer=batch([verifier],1,memory_mb=384)[0]); save(path,replay)
  checked['positive_replay']=str(path)
  if not replay['answer']['result'].get('verified'):
   save(root/'state.json',dict(source=s,status='BLOCKED_PROOF_REPLAY',origin=origin,replay=str(path))); raise RuntimeError('Positive replay incomplete; preserve outcome and diagnose before adoption')
  checked['positive_verified']=True
 witnesses=[]
 for kind in ('witness','upper_witness'):
  witness=result.get(kind)
  if witness:
   replay=verify_witness(c,witness); assert replay['verified']
   weight=len(witness['faults'])
   if kind=='witness': assert weight<target
   witnesses.append(dict(kind=kind,weight=weight,witness=witness,replay=replay))
 if status in ('INVALID','FAULT_INVALID'): assert any(w['kind']=='witness' for w in witnesses)
 checked['witness_replays']=witnesses
 if status in ('UNKNOWN','UNSUPPORTED'): unresolved.append(dict(origin=origin,circuit=exact,target=target,result=result))
 checks.append(checked)
 return checked

labels={}
for case in cases:
 path=study/'labels'/(case['name']+'.json'); labels[case['name']]=check(read(path),str(path))
policies=[]
for completed in sorted(study.glob('r*_*/complete.json')):
 rows=[]
 for case in cases:
  path=completed.parent/(case['name']+'.json'); record=read(path)
  assert record['case']==case['name']
  assert digest(record['row']['circuit'])==digest(case['circuit'])
  evidence=[check(p,str(path)+':packet'+str(i)) for i,p in enumerate(record['packets'])]
  rejected=any(x['status'] in ('INVALID','FAULT_INVALID') for x in evidence)
  certified=any(x.get('positive_verified') for x in evidence)
  assert rejected==record['hard_rejected']
  assert not (rejected and certified)
  truth=labels[case['name']]
  if truth.get('positive_verified'): assert not rejected
  if certified: assert truth['status'] not in ('INVALID','FAULT_INVALID')
  rows.append(dict(case=case['name'],code=truth['code'],target=truth['target'],fresh_label=truth['status'],hard_rejected=rejected,positive_verified=certified,resources=record['row']['resources']))
 groups={}
 for row in rows: groups.setdefault(row['code']+':'+str(row['target']),[]).append(row)
 frontiers={}
 keys=('Q','D','QD','two_q_gates')
 for key,group in groups.items():
  positives=[r for r in group if r['positive_verified']]
  frontiers[key]=[r['case'] for r in positives if not any(all(t['resources'][k]<=r['resources'][k] for k in keys) and any(t['resources'][k]<r['resources'][k] for k in keys) for t in positives)]
 n=sum(labels[r['case']].get('positive_verified',False) for r in rows)
 policies.append(dict(policy=completed.parent.name,rows=rows,verified_label_positive_count=n,verified_label_positive_retained=sum(labels[r['case']].get('positive_verified',False) and not r['hard_rejected'] for r in rows),newly_verified_positive_count=sum(r['positive_verified'] for r in rows),complete_pool_recall_status='LABELS_COMPLETE' if all(x['status'] in ('CERTIFIED','INVALID','FAULT_INVALID') for x in labels.values()) else 'UNKNOWN',certified_frontiers_by_code_and_target=frontiers,original_measured_costs=read(completed)))
save(root/'summary.json',dict(source=s,study_protocol_sha256=hashlib.sha256((study/'protocol.json').read_bytes()).hexdigest(),checks=checks,labels=labels,policies=policies,unresolved=unresolved,validation_controller_cpu=time.process_time()-cpu,validation_wall=time.perf_counter()-start,scope=protocol['scope']))
save(root/'state.json',dict(source=s,status='COMPLETE_REPORT_INTERPRETATION_REQUIRED',summary=str(root/'summary.json')))
print('POLICY_EVIDENCE_AUDIT_COMPLETE',flush=True)
