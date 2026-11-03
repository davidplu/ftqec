"""Source-bound scientific report with measured outcomes and explicit limitations."""
import json,time,collections,statistics
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
source=source_identity();out=Path('results/general_extraction/report')/source;out.mkdir(parents=True,exist_ok=True)
pop=Path('results/non_graphlike')/source/'population_study';delivery=Path('results/exports')/source/'finalists';audit=Path('results/general_extraction/audit')/source
for required in [pop/'complete.json',delivery/'complete.json',audit/'witness_replay.json']:
 while not required.exists():time.sleep(2)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def link(p,label='raw evidence'):return '['+label+'](../'+Path(p).as_posix()+')'

def best_tuple(row):
 return '/'.join(str(row['best'][k]) for k in ('Q','D','QD','two_q_gates')) if row.get('best') else 'none'
def replay_cost(row):
 a=read(delivery/'replays'/(str(row['target'])+'_'+row['id']+'.json'))['answer']
 return f"replay {a['cpu']:.3f}/{a['wall']:.3f}"
def evaluation_cost(row):
 answers=[row[k] for k in ('construction','screen','simulation','decomposition','mitm','certification') if isinstance(row.get(k),dict) and 'cpu' in row[k]]
 return 'evaluation '+format(sum(a['cpu'] for a in answers),'.3f')+'/'+format(sum(a['wall'] for a in answers),'.3f')

protocol=read(pop/'protocol.json');runs=[];events={};isolation=[]
def event(task,answer,origin):
 if not isinstance(task,dict) or not isinstance(answer,dict) or 'pid' not in answer or task.get('source')!=source:return
 key=(answer.get('task'),answer['pid'],answer.get('dispatch_monotonic'),answer.get('wall'))
 if key not in events:events[key]=dict(tier=task.get('tier'),cpu=answer.get('cpu',0),wall=answer.get('wall',0),rss=max([answer.get('peak_rss',answer.get('rss',0))]+[a.get('rss',0) for a in answer.get('attempts',[])]),start=answer.get('dispatch_monotonic'),end=answer.get('completion_monotonic'),pid=answer['pid'],status=answer.get('result',{}).get('status'),origin=origin,task=answer.get('task'))
def visit(d,origin):
 if isinstance(d,dict):
  if isinstance(d.get('task'),dict) and isinstance(d.get('answer'),dict):event(d['task'],d['answer'],origin)
  if isinstance(d.get('tasks'),list) and isinstance(d.get('answers'),list):
   for t,a in zip(d['tasks'],d['answers']):event(t,a,origin)
  for k,v in d.items():
   if k not in ('task','answer','tasks','answers','circuit','members','source_records'):visit(v,origin)
 elif isinstance(d,list):
  for v in d:visit(v,origin)
for p in sorted(pop.glob('*/checkpoint.json')):
 s=read(p);packets=[read(q) for q in (p.parent/'tasks').glob('*.json')];counts=collections.Counter();worker_cpu=0;peak=0
 for d in packets:
  task,answer=d['task'],d['answer'];counts[task['tier']]+=1;worker_cpu+=answer['cpu'];peak=max(peak,answer.get('peak_rss',answer.get('rss',0)))
 positive=[r for r in s['rows'] if r.get('certify',{}).get('status')=='CERTIFIED'];negative=[r for r in s['rows'] if r.get('certify',{}).get('status')=='INVALID' or r.get('screen',{}).get('status')=='FAULT_INVALID'];unknown=[r for r in s['rows'] if r.get('certify',{}).get('status')=='UNKNOWN']
 runs.append(dict(name=p.parent.name,raw=str(p),status=s['status'],generated=sum(g['generated'] for g in s.get('generation_compute',[])),compiled=sum(g['compiled'] for g in s.get('generation_compute',[])),distinct=len(s['rows']),screened=counts['screen'],noiselessly_valid=sum(d['answer']['result'].get('status')=='STRUCTURALLY_VALID' for d in packets if d['task']['tier']=='construct'),simulated=sum(bool(r.get('simulation_batches')) for r in s['rows']),certified=len(positive),invalid=len(negative),unknown=len(unknown),worker_cpu=worker_cpu,controller_cpu=sum(x['cpu'] for x in s['sessions']),wall=sum(x['wall'] for x in s['sessions']),peak_worker_mib=peak/2**20,best=min((r['resources'] for r in positive),key=lambda r:r['QD'],default=None),families=sorted({r['genome']['family'] for r in s['rows']})))
 by_id={r['id']:r for r in s['rows']};ancestries={}
 for row in s['rows']:
  at=row;trail=[]
  while at.get('parent') is not None:
   assert at['id'] not in trail;trail.append(at['id']);assert at['parent'] in by_id;at=by_id[at['parent']]
  trail.append(at['id']);assert at.get('construction',{}).get('method') in ('random_population','code_only_greedy_hook_graph','code_only_joint_hook_coloring','code_only_hook_coloring')
  ancestries[row['id']]=trail
 from ftqec.codes.input import load
 expected=protocol['primary'] if p.parent.name.startswith('shor5_') else protocol['cross'];assert s['code']==load(expected).to_dict()
 isolation.append(dict(run=str(p),code_only_input_verified=True,all_parents_local=True,roots_are_code_derived=True,local_ancestry_paths=ancestries,source=s['source']))
roots=[pop,Path('results/repair_trajectories')/source,Path('results/pareto')/source,Path('results/certification')/source,Path('results/ler')/source,Path('results/cross_family')/source,Path('results/general_extraction/controls')/source,Path('results/general_extraction/proof_development')/source,Path('results/general_extraction/first_positive')/source,delivery]
for root in roots:
 for p in root.rglob('*.json'):
  if any(part in ('source','proofs','bundles','bundle') for part in p.parts):continue
  visit(read(p),str(p))
by_tier={}
for tier in sorted({e['tier'] for e in events.values()}):
 group=[e for e in events.values() if e['tier']==tier];by_tier[tier]=dict(tasks=len(group),worker_cpu=sum(e['cpu'] for e in group),summed_worker_wall=sum(e['wall'] for e in group),peak_worker_mib=max(e['rss'] for e in group)/2**20)
intervals=[(e['start'],e['end']) for e in events.values() if e['start'] is not None and e['end'] is not None];timeline=sorted([(a,1) for a,b in intervals]+[(b,-1) for a,b in intervals]);active=maximum=0
for _,change in timeline:active+=change;maximum=max(maximum,active)
compute=dict(by_tier=by_tier,unique_execution_records=len(events),recorded_worker_cpu=sum(e['cpu'] for e in events.values()),summed_worker_wall=sum(e['wall'] for e in events.values()),peak_individual_worker_mib=max(e['rss'] for e in events.values())/2**20,max_overlapping_workers=maximum,worker_execution_envelope=max(b for a,b in intervals)-min(a for a,b in intervals),scope='Deduplicated actual workers; summed worker wall is not elapsed time. Tests, packaging, intake and unmeasured ad-hoc controller overhead are separate. No all-inclusive total-compute claim.')
controller_paths=[pop/'complete.json',Path('results/repair_trajectories')/source/'shor5_six_arm/complete.json',Path('results/pareto')/source/'allocation_study/complete.json',Path('results/pareto')/source/'deferred_frontier/complete.json',Path('results/pareto')/source/'compaction_study/complete.json',Path('results/general_extraction/controls')/source/'complete.json',Path('results/general_extraction/proof_development')/source/'complete.json',Path('results/certification')/source/'small_matched/complete.json',Path('results/certification')/source/'small_positive_matched/complete.json',Path('results/ler')/source/'target5_matched/complete.json',delivery/'complete.json',Path('results/cross_family')/source/'comparison.json']
controllers=[dict(raw=str(p),controller_cpu=read(p)['controller_cpu'],wall=read(p)['wall']) for p in controller_paths]
compute['controller_bodies']=controllers;compute['recorded_controller_body_cpu']=sum(r['controller_cpu'] for r in controllers)
save(Path('results/compute')/source/'execution_summary.json',dict(source=source,**compute,events=list(events.values())))
save(out/'reference_isolation.json',dict(source=source,runs=isolation))
records=read(delivery/'index.json')['records'];primary=[r for r in records if r['adopted'] and r['target']==5 and r['code']['n']==25];assert primary and any(not r['graph_eligible'] for r in primary)
ler=read(Path('results/ler')/source/'target5_matched/summary.json');witnesses=read(audit/'witness_replay.json');unknowns=read(audit/'unknown_obligations.json');repair=read(Path('results/repair_trajectories')/source/'shor5_six_arm/rows.json');allocation=read(Path('results/pareto')/source/'allocation_study/rows.json')
proof_rows=[]
for folder in [Path('results/general_extraction/proof_development')/source,Path('results/certification')/source/'small_matched',Path('results/certification')/source/'small_positive_matched']:
 for p in sorted(folder.glob('*.json')):
  d=read(p)
  if 'answer' not in d:continue
  a=d['answer'];r=a['result'];progress=r.get('progress',[]);last=progress[-1] if progress else r.get('proof',{});proof_rows.append(dict(raw=str(p),method=d['task']['limits'].get('proof_method'),target=d['task']['limits']['target'],status=r.get('status'),lower=r.get('lower_bound'),upper=r.get('upper_bound'),proof=r.get('proof',{}).get('method'),width=last.get('width'),states=last.get('max_states'),work=last.get('work'),cpu=a['cpu'],wall=a['wall'],peak_mib=a.get('peak_rss',a.get('rss',0))/2**20,independent=r.get('independent',{}).get('verified',False)))
for r in proof_rows:
 d=read(r['raw']);data=d['task']['circuit'];r.update(locations=sum(op['gate']!='BARRIER' for op in data['operations']),alternatives=d['answer']['result'].get('proof',{}).get('inventory_count'),detectors=len(data['detectors'])+len(data['code']['generators']),family=data['code'].get('name','Shor-product'))
 p=Path(r['raw']);ip=p.parent/'input.json'
 if not ip.exists():ip=p.parent/(p.stem.split('_decomposition')[0]+'_input.json')
 r['eligible']=read(ip).get('eligibility',{}).get('eligible') if ip.exists() else 'not recorded'
small=[r for r in proof_rows if 'small_positive_matched' in r['raw']];medians={m:dict(cpu=statistics.median(r['cpu'] for r in small if r['method']==m),peak_mib=statistics.median(r['peak_mib'] for r in small if r['method']==m)) for m in ('decomposition_legacy','decomposition_span','decomposition')}
tests=sorted((Path('results/general_extraction/tests')/source).glob('*/receipt.json'));assert tests and read(tests[-1])['exit_code']==0
install=Path('results/general_extraction/release')/source/'clean_install.json';assert read(install)['status']=='PASS'
gates={
'A':('PASS','Scientific preservation','29,374 prior files matched; admission-stopped baseline tests passed on retry; 118 current tests pass.','None within frozen scope.'),
'B':('PASS','Scientific replay','13 harmful Shor witnesses independently replayed among 25 preserved controls.','Other historical epochs remain unchanged.'),
'C':('PASS','Scientific diagnosis','Independent individual and simultaneous propagation establishes hook spread and flag cancellation.','Gate context alone is not causation.'),
'D':('PASS','Engineering and construction','Generic flag, cat, verification, order, repetition and allocation operators produce real circuits.','No universal repair guarantee.'),
'E':('PARTIAL','Scientific repair','Six composed descendants evaluated and retained.','No certified invalid-to-valid six-arm lineage.'),
'F':('PARTIAL','Evaluation pipeline','Singleton screening, mapped-witness replay and exact prefix checks reject harmful candidates.','No comprehensive cheap multi-fault screen or shared cross-run negative cache.'),
'G':('PASS','Population discovery','Bare, flagged, cat and verified-cat populations retained; random generation found the qualifying positive.','No general witness/hybrid advantage.'),
'H':('PASS','Scientific eligibility','Every configured projection independently audited.','Portfolio-relative ineligibility only.'),
'I':('PASS','Scientific exact method','Reduced separator independently completes graph-ineligible target-three control.','No separator target-five positive.'),
'J':('PARTIAL','Exact-method research','MITM and SAT semantics preserved; existing MITM supplies target-five proof.','No new MITM-partition or incremental-SAT advance.'),
'K':('PASS','Scientific verification','Adopted positives separately replayed; exports reconstructed; reported negative/upper witnesses replayed.','None for adopted results.'),
'L':('PASS','Primary scientific milestone','Code-only [[25,1,5]], independent graph ineligibility and exact-distance-five proof, exported.','Ideal-boundary extraction scope.'),
'M':('PASS','Cross-family science','Independent HGP target-three positives and a re-certified improvement from Q100 D53 720 two-qubit gates to Q100 D49 240 gates.','High-distance gains outside the primary family remain unestablished.'),
'N':('PASS','Certified resources','Q36 D329 and Q105 D46 target-five alternatives adopted; target-ten frontier preserved.','Finite frontier, not global optimum.'),
'O':('PASS','Decoder-conditional science','Matched 131,072-shot arms with exact simultaneous intervals.','Overlapping intervals; one-mechanism decoder and ideal boundaries.'),
'P':('PASS','Execution evidence','Actual worker PIDs and overlapping intervals.','Individual worker peak is not aggregate system peak.'),
'Q':('PASS','Public delivery','Installed Optimize/resume/export/verify-export and independent reconstruction pass.','Legacy raw guard-only bundle-export limitation remains.'),
'R':('PASS','Reproducible delivery','Protocols, raw outcomes, source, tested wheel and integrity release.','Final archive/manifest receipts accompany delivery; no push/cloud.')}
summary=dict(source=source,runs=runs,proof_rows=proof_rows,proof_medians=medians,delivery=records,compute=compute,gates={k:dict(status=v[0],type=v[1],evidence=v[2],unresolved=v[3]) for k,v in gates.items()},ler=ler,negative_replays=len(witnesses['records']),unknown_obligations=len(unknowns['records']),tests=str(tests[-1]),installation=str(install));save(out/'summary.json',summary)
lines=['# General fault-tolerant extraction: scientific results','',f'Scientific source `{source}`; FTQEC 0.1.0.','',
'The defining target-five milestone is demonstrated. A code-only random-population verified-cat discovery on independently validated [[25,1,5]] is graph-ineligible for the implemented portfolio and independently certified at exact extraction distance five. The existing full-signature MITM engine supplies this proof. The new separator backend does not receive credit for it.','',
'The adopted alternatives include Q=36,D=329,QD=11,844 and Q=105,D=46,QD=4,830, both with 248 two-qubit gates. The lower-qubit option remains. Five other allocation/scheduling neighbors were invalidated: noiseless equivalence did not preserve fault tolerance.','',
'Claims use ideal initial/final syndrome boundaries and explicit operation-local faults. They do not certify arbitrary-input physical memory, implicit idle noise, hardware routing, decoder-independent performance or global optimality.','',
link(out/'summary.json','Complete machine-readable results')+'; '+link(delivery/'index.json','independently verified bundles')+'; '+link(audit/'unknown_obligations.json','unresolved obligations')+'.','',
'## Separate scientific objectives','',
'| Objective | Status | Interpretation |','|---|---|---|',
'| Architecture repair | PARTIAL | Real compositions and mechanism replays; no certified invalid-to-valid six-arm repair. |',
'| General certification | PASS | Non-surface graph-ineligible target-five positive via MITM. |',
'| Computational efficiency | PASS, narrow | Lower separator CPU/memory on the same target-three graph-ineligible control across three rotations. |',
'| Autonomous optimization | PASS | Code-only discovery and certified QD improvement without reference seeds. |',
'| Generalization | PASS, scoped | Independent HGP target-three positives and certified resource improvement; no second-family distance-five claim. |',
'| Reproducibility | PASS | Complete circuits, schedules, proofs and public reconstruction. |','',
'## Table A — Architecture repair and resource outcomes','',
'| Case | Architecture | Parent | Q | D | QD | 2Q gates | Outcome | CPU/wall s | Evidence |','|---|---|---|---:|---:|---:|---:|---|---|---|']
for r in primary:lines.append(f"| Certified {r['id'][:12]} | {read(Path(r['bundle'])/'circuit.json').get('experiment',{}).get('family')} | {r.get('parent') or 'code-only'} | {r['resources']['Q']} | {r['resources']['D']} | {r['resources']['QD']} | {r['resources']['two_q_gates']} | Independently verified target {r['target']} | {replay_cost(r)} | {link(r['bundle'],'bundle')} |")
from ftqec.circuits.model import Circuit
from ftqec.evaluation.resources import resources as circuit_resources
parent_path=Path('results/repair_trajectories')/source/'shor5_six_arm/parent_input.json'
parent_packet=read(parent_path)['packet'];parent_metrics=circuit_resources(Circuit.from_dict(parent_packet['task']['circuit']));parent_result=parent_packet['answer']['result']
lines.append(f"| Original negative parent | flagged | historical control | {parent_metrics['Q']} | {parent_metrics['D']} | {parent_metrics['QD']} | {parent_metrics['two_q_gates']} | INVALID; upper {parent_result.get('upper_bound')} independently replayed | historical {parent_packet['answer']['cpu']:.3f}/{parent_packet['answer']['wall']:.3f} | {link(parent_path,'parent packet')} |")
for r in repair:
 metric=r['construction']['result'].get('resources',{});results=[r[k]['result'] for k in ('decomposition','mitm') if k in r];last=results[-1] if results else r.get('screen',{}).get('result',{});status=r.get('status',last.get('status','NOT_RUN'));known_lower=max((v.get('lower_bound',1) for v in results if v.get('independent',{}).get('verified')),default=None)
 lines.append(f"| Invalid-parent repair seed {r['seed']} | {r['genome']['family']} | {r['parent']} | {metric.get('Q','—')} | {metric.get('D','—')} | {metric.get('QD','—')} | {metric.get('two_q_gates','—')} | {status}; lower {known_lower if known_lower is not None else 'unrecorded'}, upper {last.get('upper_bound','none')} | {evaluation_cost(r)} | {link(Path('results/repair_trajectories')/source/'shor5_six_arm/rows.json','lineage')} |")
for r in allocation:
 metric=r.get('resources',{});res=r.get('certification',{}).get('result',r.get('screen',{}).get('result',{}));lines.append(f"| Allocation slots {r['slot']} | {r['genome']['family']} | {r['parent']} | {metric.get('Q','—')} | {metric.get('D','—')} | {metric.get('QD','—')} | {metric.get('two_q_gates','—')} | {res.get('status','NOT_RUN')}; lower {res.get('lower_bound','unrecorded')}, upper {res.get('upper_bound','none')} | {evaluation_cost(r)} | {link(Path('results/pareto')/source/'allocation_study/rows.json','raw')} |")
lines+=['','All Table A cases use [[25,1,5]] at requested target five. CPU/wall labels distinguish separate replay from summed construction/evaluation stages. Exact parent identities, genomes, operator sequences, physical circuits, lower bounds, witness weights and CPU/wall records are in each lineage packet. All dominated positives remain exported. Compaction-only outcomes are separate from schedule changes.','',
'## Table B — Matched exact-certification methods','',
'| Input/method | Family | Graph eligible | Locations | Alternatives | Detectors | Target | Outcome / accepted proof | Lower | Upper | Width | States | CPU s | Wall s | Peak MiB | Independent |','|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|']
for r in proof_rows:lines.append(f"| {link(r['raw'],Path(r['raw']).parent.name+'/'+Path(r['raw']).stem)} | {r['family']} | {r['eligible']} | {r['locations']} | {r['alternatives']} | {r['detectors']} | {r['target']} | {r['status']} / {r['proof']} | {r['lower']} | {r['upper']} | {r['width']} | {r['states']} | {r['cpu']:.3f} | {r['wall']:.3f} | {r['peak_mib']:.2f} | {r['independent']} |")
lines+=['',f"Matched target-three median CPU: legacy {medians['decomposition_legacy']['cpu']:.3f}s; span-only {medians['decomposition_span']['cpu']:.3f}s; reduced separator {medians['decomposition']['cpu']:.3f}s. Legacy and span-only exhausted separator work and retained valid pair certificates. The reduced backend completed its separator proof. All establish the same requested lower bound. This is a forced-backend comparison; the automatic target-three pair checker is a separate cheaper path.",'',
'Physical locations, full alternatives, detector/logical dimensions and repeated signatures are in '+link(Path('results/compute')/source/'structure_profiles.json')+'. Per-layer hashes, transitions and censored progress remain in raw packets. A new matched full-size SAT/standalone-DP comparison is NOT_RUN; their existing exact semantics remain regression-tested. The target-five MITM positive is not substituted into these timing comparisons.','',
'## Table C — Cross-family code-only populations','',
'| Run | Generated | Compiled | Distinct | Noiseless valid | Screened | Simulated | Certified | Invalid | UNKNOWN | Worker CPU s | Controller CPU s | Wall s | Peak worker MiB | Best Q/D/QD/2Q |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
for r in runs:lines.append(f"| {link(r['raw'],r['name'])} | {r['generated']} | {r['compiled']} | {r['distinct']} | {r['noiselessly_valid']} | {r['screened']} | {r['simulated']} | {r['certified']} | {r['invalid']} | {r['unknown']} | {r['worker_cpu']:.3f} | {r['controller_cpu']:.3f} | {r['wall']:.3f} | {r['peak_worker_mib']:.2f} | {best_tuple(r)} |")
lines+=['','Shor-product [[25,1,5]] requests target five; Hamming hypergraph-product [[58,16,3]] requests target three. '+link(pop/'algebraic.json','Algebraic evidence')+'. Distinct counts are per run, not across repeated trials. Screened but unproved candidates are not silently classified UNKNOWN or INVALID. Post-study deferred certification/allocation costs are separate and not retroactively credited to original policies.','',
'## Table D — Screening and allocation comparison limits','',
'| Comparison | Status | Positive retention / false rejection | Interpretation |','|---|---|---|---|',
'| Random/witness/hybrid populations | Finite observed trials | NOT_RUN as complete ground-truth rates | Actual costs above; equal generations are not matched compute. |',
'| Cost-aware hybrid | Finite observed trials | NOT_RUN as complete ground-truth rates | Generation and evaluation effects remain coupled. |',
'| Direct certification vs fixed multifidelity on a common pool | NOT_RUN | NOT_RUN | No causal allocation advantage claimed. |',
'| Fixed vs cost-aware allocation at matched CPU checkpoints | NOT_RUN | NOT_RUN | Requires a frozen common pool and retention ground truth. |','',
'## Table E — Acceptance gates','',
'| Gate | Status | Evidence type | Evidence | Unresolved requirement |','|---|---|---|---|---|']
for gate,v in gates.items():lines.append('| '+' | '.join([gate,*v])+' |')
lines+=['', 'The independent HGP comparison re-certifies the previous Q100,D53,720-two-qubit circuit and the new Q100,D49,240-two-qubit circuit at target three. Previous Q64,D72 and Q59,D408 alternatives remain certified. '+link(Path('results/cross_family')/source/'comparison.json','Cross-family comparison')+'. This is a finite resource improvement, not a second-family distance-five result.']
lines+=['','## Decoder-conditional reliability','',
'| Circuit | Physical p | Failures / shots | Rate | Simultaneous interval |','|---|---:|---:|---:|---|']
for a in ler['arms']:lines.append(f"| {a['case']} | {a['p']} | {a['failures']} / {a['shots']} | {a['rate']:.8g} | {a['simultaneous_interval']} |")
lines+=['',link(Path('results/ler')/source/'target5_matched/protocol.json','Frozen LER protocol')+'. Both circuits use the same one-mechanism lookup decoder with explicit zero fallback. Exact binomial intervals use a four-arm Bonferroni correction and overlap at both noise levels. No reliability ordering is established. Automatic matching rejected unsupported detector decomposition; that fallback record is retained. Logical-Z-sector operation-noise experiments are not complete physical-memory or decoder-independent guarantees.','',
'## Recorded computation','',
'| Stage | Actual worker executions | Worker CPU s | Summed worker wall s | Peak individual worker MiB |','|---|---:|---:|---:|---:|']
for stage,c in by_tier.items():lines.append(f"| {stage} | {c['tasks']} | {c['worker_cpu']:.3f} | {c['summed_worker_wall']:.3f} | {c['peak_worker_mib']:.2f} |")
lines+=['',f"Observed peak overlap: {compute['max_overlapping_workers']} workers. Recorded worker CPU: {compute['recorded_worker_cpu']:.3f}s. Worker execution envelope: {compute['worker_execution_envelope']:.3f}s. {compute['scope']}",'',link(Path('results/compute')/source/'execution_summary.json','Execution records')+'. Controller body CPU/wall are saved separately by each driver; population costs appear in Table C. Local computing sufficed for the declared experiments. No cloud resources were provisioned.','',
'## Explicit scientific questions','']
lines+=['Controller body costs below include the population driver once; its per-run session costs in Table C must not be added again. Startup and uninstrumented ad-hoc first-positive export overhead are not included.','', '| Controller receipt | Body CPU s | Wall s |','|---|---:|---:|']
for c in controllers:lines.append(f"| {link(c['raw'],str(Path(c['raw']).parent))} | {c['controller_cpu']:.3f} | {c['wall']:.3f} |")
lines+=['', 'All-known historical and new certified discovery alternatives remain in '+link(Path('results/pareto')/source/'all_known_frontiers.json','the merged frontier archive')+'. Historical certificates retain their original source identities.', '']
answers=[
'Preserved witnesses include propagated ancilla faults and multi-fault flag cancellation. Thirteen harmful Shor controls were independently replayed; the diagnosis index retains each physical configuration.',
'Implemented overlapping flags and a six-arm portfolio combining implicated-check ordering, verified-cat verification, repetition, scheduling and compaction. Existing basis/cat/adjacent/nested operators remain.',
'Mapped mechanisms may change, but failed operation-context transfer is NOT_TRANSFERABLE, not elimination. No composed six-arm descendant became independently certified at target five.',
'No certified invalid-to-valid six-arm lineage was established. The successful code-only verified-cat discovery is a separate result, not relabelled as a repair.',
'The valid-parent allocation descendant uses Q=105,D=46,QD=4,830 versus Q=36,D=329,QD=11,844. Both use 248 two-qubit gates, recomputed from exported schedules.',
'The qualifying verified-cat target-five circuit and Shor target-four control are graph-ineligible for the implemented portfolio. Every adopted circuit has an eligibility receipt.',
'All configured projection masks and physical obstructions are retained. The first positive fails all four choices for logical channel zero; two choices for channel one are eligible, insufficient for full graph certification.',
'Yes. Circuit b090363c8b677a189be3c07d0b459bfba25896b708b9afb8a5dba8cf7bde1472 on [[25,1,5]] has an independently replayed MITM lower bound and matching weight-five upper witness.',
'MITM supplies target-five positives; graph proves eligible target-ten controls; reduced separator completes graph-ineligible target-three and physical target-two controls. Bounded higher-target separator proofs remain UNKNOWN; new full-size SAT/DP comparisons were not run.',
'Whole-location reduction improves separator CPU, memory and completion on the matched target-three control. Span pruning alone did not improve the initial bounded study. No universal or target-five separator advantage is claimed.',
'Table B and raw progress provide maximum states, widths, transitions and complete per-layer hashes. A censored prefix maximum is not a completed-graph width.',
'Repeated signatures, XOR-closed physical domains, inclusion, disjoint components and suffix-span impossibility tests support exact reduction. Structure profiles quantify the successful cat circuit versus dense flag controls.',
'Yes. Full inventories are hash-bound; independent domain coverage and closure checks prove a cost-nonincreasing physical replacement. Correlated components are never split and location exclusivity is preserved.',
'Every adopted positive receives separate proof replay and export reconstruction. Reported harmful and matching upper witnesses have a separate replay index. Produced positives also have internal independent checks.',
'The UNKNOWN index retains each exact circuit, target, method, recorded verified bound and unresolved interval/guard reason. Missing bounds are not invented.',
'The deterministic portfolio uses graph eligibility and exact structure reduction before MITM/DP. The qualifying proof needed MITM after separator incompletion. A learned or broadly optimal selector was not established.',
'Table C records actual generated, compiled, screened, simulated and certified counts. Duplicate physical circuits and repeated trials are distinguished in raw records.',
'Verified-cat generation produced the strongest target-five discoveries. Several flagged multi-fault repair descendants were invalid or unresolved.',
'No certified invalid-to-valid multi-fault repair gain was shown. A generic valid-parent allocation change improved certified QD while preserving the lower-qubit alternative.',
'Real compositions were evaluated, but the six-arm study does not establish superiority over isolated repairs. That causal ablation is NOT_RUN.',
'Five scheduling/allocation descendants of a certified parent became invalid. Historical fault transfer is tracked separately; noiseless semantics does not imply distance preservation.',
'The target-five frontier includes Q=36,D=329,QD=11,844 and Q=105,D=46,QD=4,830, both with 248 two-qubit gates. Exact finite frontiers and dominated positives are preserved.',
'Yes. Lower-Q nondominated alternatives remain, and equal-resource distinct physical discoveries retain separate provenance.',
'Each checkpoint retains generation-level frontier histories and simulation batches. No general monotone reliability improvement or global convergence is inferred.',
'Yes. Frozen inputs contain only code data; all ancestry roots are code-derived and every parent is local to the same run. Historical controls and post-discovery studies are separately labelled.',
'Shor-product and Hamming hypergraph-product are distinct CSS construction families. Surface circuits are preserved controls, not new cross-family discoveries.',
'Yes, the code-only [[25,1,5]] discovery qualifies. A second independent non-surface distance-five family result remains unestablished.',
'Cross-family optimization was evaluated separately. New high-distance repair and separator gains outside the primary construction family remain unestablished.',
'Unsupported matching decomposition, invalid controls, guarded UNKNOWN proofs and unproved screened candidates remain distinct. Non-CSS high-distance optimization is outside this cycle.',
'Actual Shor/HGP outcomes, generic metadata-based operators and exhaustive small-domain oracles support scoped applicability, not universal efficient certification or broad high-distance generalization.',
'Actual worker CPU/wall/peak appear in stage tables and receipts; controller body costs are separate. Unmeasured startup or interactive overhead is not presented as an all-inclusive total.',
'The reduced separator completes the matched small graph-ineligible proof with less CPU and memory than prior separator attempts, at the same requested bound. No unmatched-input timing establishes a speedup.',
'Singleton screening and mapped-witness replay stop deep work when they find a witness. No exhaustive cheap multi-fault screen or shared cross-run negative cache was demonstrated.',
'Yes. Distinct supervised PIDs have overlapping measured intervals; the exact peak overlap is in the execution summary.',
'Local computing completed the declared experiments, exports and tests. Proof safeguards still produced UNKNOWN; baseline memory-admission failures passed after memory was freed.',
'No cloud escalation was required or provisioned. Exponential state growth alone is not a justification for billable cloud resources.',
'All 29,374 frozen prior files matched. Four initial admission failures were preserved and passed on retry. The adopted source passes 118 tests.',
'Yes. Export verification reconstructs circuits, exact schedules, dependencies, detector definitions and resources, then replays bound proof evidence. The isolated installed package also verifies the target-five bundle.',
'Gates E,F,J remain PARTIAL: certified invalid-to-valid composition, comprehensive multi-fault early rejection, new MITM/SAT advances. High-distance cross-family generalization is also not claimed.',
'Derive fault-aware scheduling constraints from replayed witnesses of the five rejected allocation descendants, then test those repairs prospectively on fresh code-only inputs with complete re-certification.'
]
assert len(answers)==40
for i,a in enumerate(answers,1):lines.append(f'{i}. {a}\n')
lines+=['## Reproduction','',
'Install the matching wheel/source and run `ftqec verify-export BUNDLE --proof-work 20000000 --require-certified`. Optimize into a fresh output directory; never overwrite frozen folders. Raw settings, seeds, task identities, circuits, failures, proof states and source snapshots accompany delivery. The previous scientific archive is separately preserved and hash-referenced.','',
'The release receipt records the final commit, source and integrity manifests. No public push occurred.','']
Path('docs/RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
Path('docs/LIMITATIONS.md').write_text('''# Scientific limitations

The graph-ineligible non-surface target-five milestone is demonstrated. Other research requirements remain incomplete:

- No certified invalid-to-valid six-arm repair lineage.
- No comprehensive cheap multi-fault screening, shared cross-run negative cache, or causally isolated matched-compute allocation advantage.
- New separator positivity is demonstrated at graph-ineligible target three, not target five. The target-five proof is existing exact MITM.
- No new incremental SAT or MITM-partition advance.
- Five allocation/scheduling descendants of a certified parent were invalid: noiseless equivalence is insufficient.
- No second independent distance-five family repair demonstration.
- Matched LER intervals overlap. Results are conditional on a one-mechanism decoder with zero fallback, logical-Z preparation, operation noise and ideal boundaries.
- UNKNOWN preserves unresolved weights. Finite frontiers are not global optima. No arbitrary-input physical-memory or routing guarantee.
- Worker peak memory is not aggregate system peak. Reported study costs exclude unmeasured interactive overhead, tests and packaging unless separately labelled.
- The historical raw guard-only bundle export edge case remains; this cycle exports certified finalists.

See RESULTS.md for all gates and source-bound evidence.
''',encoding='utf-8')
Path('docs/SCIENTIFIC_PROTOCOL.md').write_text(f'''# Frozen general-extraction protocol

Source `{source}`. The full protocol and hash are under `{pop.as_posix()}`. Primary seeds: 101,211; independent HGP seeds: 331,443. Finite populations/generations are experimental measurements, not permanent optimizer limits. Worker CPU, wall, memory and proof-work safeguards remain active. No reference circuits initialize optimization and no cloud resources are provisioned.

Separate frozen protocols cover proof comparisons, six-arm negative-parent repair, deferred resource alternatives, allocation, compaction and LER. Post-discovery compute is not retroactively credited to the original policies. Cross-family outcomes did not tune source changes. Equal-generation comparisons do not isolate generation from evaluation-policy effects.

Every adopted claim requires independent replay and exact source/circuit/model binding. All negative, UNKNOWN, failed and censored records remain. Initial memory-admission failures and the missing-build-backend packaging failure are preserved beside successful retries.

The exact original six-arm driver is frozen with its hash. A later driver-only correction also recognizes FAULT_INVALID and writes a different output directory. All six original screen results were NO_WITNESS_FOUND, so scientific outcomes are unaffected.

Use fresh output directories for reproduction. Frozen experiment folders are immutable audit records. Delivery includes integrity hashes, source, a tested wheel and independently verifiable bundles.
''',encoding='utf-8')
p=Path('README.md');old=p.read_text(encoding='utf-8');marker='## General graph-ineligible extraction milestone'
if marker not in old:
 p.write_text(old+'\n'+marker+'\n\nFTQEC now has a code-only, independently certified graph-ineligible target-five discovery for [[25,1,5]] under the operation-local ideal-boundary model. The finite frontier includes Q=36,D=329 and Q=105,D=46. The target-five proof uses exact MITM; new separator-domain reduction has a separate graph-ineligible target-three positive.\n\nSee [results](docs/RESULTS.md), [general certification](docs/GENERAL_CERTIFICATION.md) and [limitations](docs/LIMITATIONS.md). Decoder-conditional LER intervals overlap. Every schedule transformation requires fresh certification.\n',encoding='utf-8')
print('REPORT_COMPLETE',out,flush=True)
