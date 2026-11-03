"""Independent candidate, resource, witness and ancestry audit of frozen populations."""
import json,time,collections,argparse
from pathlib import Path
from ftqec.results.artifacts import source_identity,save,digest
from ftqec.optimization.store import PopulationStore
from ftqec.optimization.diversity import timed_structure
from large_scale_structure import ancilla_invariant
from ftqec.circuits.model import Circuit
from ftqec.circuits.identity import physical_identity
from ftqec.faults.verification import verify_witness
s=source_identity();campaign=Path('results/large_scale/campaigns')/s;protocol=json.loads((campaign/'protocol.json').read_text());out=Path('results/large_scale/audit')/s;out.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--job',action='append');args=parser.parse_args()
if args.job:
 protocol['jobs']=[j for j in protocol['jobs'] if j['name'] in args.job]
 assert len(protocol['jobs'])==len(args.job),'Unknown job'
 out=out/'subsets'/digest(dict(jobs=sorted(args.job),audit=__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest()));out.mkdir(parents=True,exist_ok=True)
else:assert (campaign/'complete.json').exists(),'Audit only closed, completed campaign matrix'
audit_identity=dict(source=s,driver=__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest(),diversity_helper=__import__('hashlib').sha256(Path(__file__).with_name('large_scale_structure.py').read_bytes()).hexdigest(),jobs=[j['name'] for j in protocol['jobs']])
if (out/'audit_protocol.json').exists():assert json.loads((out/'audit_protocol.json').read_text())==audit_identity
else:save(out/'audit_protocol.json',audit_identity)
start=time.perf_counter();cpu=time.process_time();runs=[];family_points=collections.defaultdict(list)
witnesses={};unknown=[]

def skyline(rows):
 rows=list(rows);keys=('Q','D','QD','two_q_gates');tuples={tuple(r['resources'][k] for k in keys) for r in rows}
 nondominated={p for p in tuples if not any(q!=p and all(a<=b for a,b in zip(q,p)) for q in tuples)}
 return [r for r in rows if tuple(r['resources'][k] for k in keys) in nondominated]

def independent_resources(c):
 ready=[0]*c.num_qubits;ends=[]
 for op in c.operations:
  begin=max([ready[q] for q in op.qubits]+[ends[i] for i in op.deps]+[0]);end=begin+int(op.gate!='BARRIER');ends.append(end)
  for q in op.qubits:ready[q]=end
 q=c.code.n+len(c.syndrome_qubits)+len(c.flag_qubits);d=max(ends,default=0)
 return dict(Q=q,D=d,QD=q*d,two_q_gates=sum(op.gate in ('CX','CZ','SWAP') for op in c.operations))

for job in protocol['jobs']:
 root=Path('results/populations')/s/'study'/job['name'];done=out/'runs'/(job['name']+'.json')
 if done.exists():
  prior=json.loads(done.read_text());runs.append(prior)
  for key,value in prior['witness_replays'].items():
   if key not in witnesses:witnesses[key]=dict(value,origins=[])
   witnesses[key]['origins'].extend(value['origins'])
  unknown.extend(prior['unknown_obligations'])
  for r in prior['positive_points']:family_points[job['family']].append(r)
  continue
 assert json.loads((root/'experiment_receipt.json').read_text())['status']=='REQUESTED_CANDIDATE_GOAL_COMPLETED'
 run_wall=time.perf_counter();run_cpu=time.process_time()
 counts=collections.Counter();features=collections.defaultdict(collections.Counter);points=[];ids={};classes=set();costs={};events=[];evidence=[];compiled_payloads=set();valid_payloads=set()
 with PopulationStore(root/'population.sqlite',readonly=True) as db:
  state=db.get_meta('state');summaries={r['id']:r for r in db.summaries()}
  for cid,index in summaries.items():
   r=db.get(cid);c=Circuit.from_dict(r['circuit']);exact=digest(c.to_dict());assert physical_identity(c)==cid
   assert timed_structure(c)==r['diversity']['timed_structure'];classes.add(r['diversity']['timed_structure'])
   metric=independent_resources(c);assert all(metric[k]==r['resources'][k]==index['resources'][k] for k in metric)
   assert index['certify']['status']==r.get('certify',{}).get('status') and index['screen']['status']==r.get('screen',{}).get('status')
   assert r['structural']['circuit']==exact;ids[cid]=r.get('parent');counts['distinct_compiled']+=1
   g=r['genome'];features['ancilla_relabel_invariant'][ancilla_invariant(c)]+=1;features['family'][g['family']]+=1;features['allocation'][str((len(c.syndrome_qubits),len(c.flag_qubits)))]+=1
   features['basis'][digest([str(x) for x in c.code.generators])]+=1;features['orders'][digest(g['orders'])]+=1;features['check_order'][digest(g['checks'])]+=1
   features['flag_configuration'][g['flag_style'] if g['family']=='flagged' else 'not_applicable']+=1
   features['cat_verification'][str(g['verification_rounds']) if g['family']=='verified_cat' else 'not_applicable']+=1
   features['schedule'][g['schedule']]+=1;features['depth'][str(metric['D'])]+=1;features['QD'][str(metric['QD'])]+=1
   counts['screened']+=int('screen' in r);counts['simulated']+=int('simulation_batches' in r);counts['certification_attempted']+=int('certify' in r)
   if 'screen' in r:features['screen_work'][str(r['screen'].get('work','unrecorded'))]+=1
   cert=r.get('certify',{});status=cert.get('status')
   if status=='CERTIFIED':
    assert cert.get('independent',{}).get('verified') and cert['circuit']==exact and cert['source']==s
    counts['certified']+=1;point=dict(id=cid,circuit=exact,run=str(root),family=job['family'],resources=metric,target=job['config']['target'],source=s);points.append(point);family_points[job['family']].append(point)
   invalid=r.get('screen',{}).get('status')=='FAULT_INVALID' or status=='INVALID';counts['invalid']+=int(invalid)
   if status in ('UNKNOWN','UNSUPPORTED'):
    counts[status.lower()]+=1;unknown.append(dict(candidate=cid,circuit=exact,run=str(root),target=job['config']['target'],status=status,lower_bound=cert.get('lower_bound'),reason=cert.get('reason'),unresolved=cert.get('unresolved')))
   for label,result in [('screen',r.get('screen',{})),('certify',cert)]:
    for kind in ('witness','upper_witness'):
     witness=result.get(kind)
     if not witness:continue
     key=digest(dict(circuit=exact,witness=witness))
     if key not in witnesses:
      checked=verify_witness(c,witness);assert checked['verified'],(job['name'],cid,kind,checked)
      weight=len(witness['faults'])
      if kind=='witness':assert weight<job['config']['target']
      witnesses[key]=dict(circuit=exact,weight=weight,kind=kind,verified=checked,origins=[])
     witnesses[key]['origins'].append(dict(run=str(root),candidate=cid,stage=label))
  for cid,parent in ids.items():
   seen=set();at=cid
   while ids[at] is not None:
    assert at not in seen;seen.add(at);assert ids[at] in ids;at=ids[at]
  assert len(classes)==db.meaningful_count()
  for packet in db.packets():
   task,a=packet['task'],packet['answer'];tier=task['tier'];v=costs.setdefault(tier,dict(executions=0,cpu=0.,body_cpu=0.,summed_wall=0.,shots=0,queue_wall=0.,peak_rss=0))
   v['executions']+=1;v['cpu']+=a['cpu'];v['body_cpu']+=a.get('body_cpu',0);v['summed_wall']+=a['wall'];v['shots']+=a['result'].get('shots',0);v['queue_wall']+=a.get('queue_wall',0);v['peak_rss']=max(v['peak_rss'],a.get('peak_rss',a.get('rss',0)))
   if tier.startswith('construct'):
    if 'circuit' in a['result']:
     compiled_payloads.add(digest(a['result']['circuit']))
     if a['result'].get('status')=='STRUCTURALLY_VALID':valid_payloads.add(digest(a['result']['circuit']))
    counts['constructed_attempts']+=int('circuit' in a['result']);counts['noiseless_valid_attempts']+=int(a['result'].get('status')=='STRUCTURALLY_VALID');counts['construction_unknown']+=int(a['result'].get('status')=='UNKNOWN')
  counts['distinct_constructed_payloads']=len(compiled_payloads);counts['distinct_noiseless_valid_payloads']=len(valid_payloads)
  from ftqec.optimization.store import unpack
  for kind,blob,sha in db.db.execute("SELECT kind,payload,hash FROM events WHERE kind='frontier' ORDER BY seq"):
   event=unpack(blob,sha);events.append(event)
  archive=json.loads((root/'archives.json').read_text());expected={r['id'] for r in skyline([x for x in summaries.values() if x['certify']['status']=='CERTIFIED'])}
  assert expected==set(archive['certified_pareto'])
  local_witnesses={key:dict(value,origins=[x for x in value['origins'] if x['run']==str(root)]) for key,value in witnesses.items() if any(x['run']==str(root) for x in value['origins'])}
  local_unknown=[x for x in unknown if x['run']==str(root)]
  record=dict(audit_cpu=time.process_time()-run_cpu,audit_wall=time.perf_counter()-run_wall,witness_replays=local_witnesses,unknown_obligations=local_unknown,source=s,job=job,status=state['status'],generated_attempts=state['generated'],counts=dict(counts),meaningful_structures=len(classes),ancilla_relabel_invariant_classes=len(features['ancilla_relabel_invariant']),features={k:dict(v) for k,v in features.items()},costs=costs,outer_receipt=json.loads((root/'experiment_receipt.json').read_text()),frontier_history=events,positive_points=points,independent_candidate_resource_ancestry_and_frontier_checks=True)
 save(done,record);runs.append(record);save(out/'witness_replay_partial.json',dict(source=s,records=witnesses));save(out/'unknown_partial.json',unknown);print('AUDITED',job['name'],len(classes),flush=True)
# Preserve the full positive archive; adopt only deterministic representatives of each resource tuple.
frontiers={};representatives=[]
for family,points in family_points.items():
 by_circuit={}
 for point in points:by_circuit.setdefault(point['circuit'],point)
 front=skyline(by_circuit.values());frontiers[family]=front;by_resource={}
 for r in sorted(front,key=lambda r:r['circuit']):by_resource.setdefault(tuple(r['resources'][k] for k in ('Q','D','QD','two_q_gates')),r)
 representatives.extend(by_resource.values())
save(out/'summary.json',dict(source=s,audit_identity=audit_identity,completed_run_audit_cpu=sum(r['audit_cpu'] for r in runs),completed_run_audit_wall=sum(r['audit_wall'] for r in runs),invocation_clock_scope='Outer wall and controller_cpu describe this invocation only; completed_run_audit fields sum retained run receipts across resumes.',runs=runs,certified_frontiers=frontiers,export_representatives=representatives,wall=time.perf_counter()-start,controller_cpu=time.process_time()-cpu,scope='Exact candidate identity, resource recomputation, acyclic local ancestry, all reported physical witnesses, and certified skyline recomputation. Raw equal-resource positives are retained; exported representatives are selected without LER outcomes.'))
save(out/'witness_replay.json',dict(source=s,records=witnesses));save(out/'unknown_obligations.json',dict(source=s,records=unknown));print('POPULATION_AUDIT_COMPLETE',flush=True)
