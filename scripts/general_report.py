"""Write the scientific report from verified raw results; no inferred certificates."""
import json
from pathlib import Path
from ftqec.results.artifacts import source_identity,save
from ftqec.evaluation.resources import resources
from ftqec.circuits.model import Circuit
source=source_identity();s=json.loads(Path('results/general_competitive/summary.json').read_text());assert s['source']==source
root=Path('results/general_competitive/final')/source
read=lambda p:json.loads(Path(p).read_text())
fronts=read(f'results/pareto/general_competitive/{source}.json')
release=Path('results/general_competitive/release')/source
assert read(release/'clean_install.json')['status']=='PASS'
archive_ok=(release/'archive_precheck.json').exists()

def table(headers,rows):
 return '| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+''.join('| '+' | '.join(str(x).replace('|','/') for x in row)+' |\n' for row in rows)
def link(path):return '['+Path(path).name+'](../'+str(path).replace('\\','/')+')'
def f(x):return f'{x:.3f}'
method_rows=[]
for r in s['methods']:
 eligible='eligible logical-channel projections' if r['requested_method']=='graph' else 'arbitrary supported signatures'
 method_rows.append([r['requested_method'],r['actual_method'],eligible,r['target'],int(r['status']=='CERTIFIED'),int(r['status']=='INVALID'),int(r['status']=='UNKNOWN'),f(r['cpu']),f(r['wall']),f(r['peak_rss']/2**20),r.get('independent',{}).get('verified',False),link(r['evidence'])])
old=read('results/discovery/autonomous/surface_target10/checkpoint.json');oldvalid=[r for r in old['rows'] if r.get('certify',{}).get('status')=='CERTIFIED']
oldq=min(oldvalid,key=lambda r:(r['resources']['Q'],r['resources']['QD']));oldd=min(oldvalid,key=lambda r:(r['resources']['D'],r['resources']['QD']))
resource_rows=[]
for label,r in [('Previous low-Q',oldq),('Previous low-D',oldd)]:
 v=r['resources'];resource_rows.append([label,v['Q'],v['D'],v['QD'],v['two_q_gates'],'CERTIFIED',r['id'],old['source'][:12]])
reference=next(r for r in fronts['all_known_including_reference'] if r['reference'])
for label,r in [('Independent reference',reference)]:
 v=r['resources'];resource_rows.append([label,v['Q'],v['D'],v['QD'],v['two_q_gates'],'CERTIFIED',r['id'],source[:12]])
seen=set()
for r in sorted(fronts['discovery'],key=lambda r:(r['resources']['Q'],r['resources']['D'],r['id'])):
 v=r['resources'];key=tuple(v[k] for k in ('Q','D','QD','two_q_gates'))
 if key in seen:continue
 seen.add(key);resource_rows.append(['New discovery frontier',*key,'CERTIFIED',r['id'],source[:12]])
family_rows=[]
for r in s['families']:
 name='steane' if r['name']=='color_small' else 'surface10_seed0' if r['name'] in ('surface10_seed8','surface10_seed16') else r['name']
 algebraic=read(Path('results/general_competitive/algebraic')/source/(name+'.json'))['certificate']['exact_distance']
 v=r['best'];best='—' if v is None else f"{v['Q']}/{v['D']}/{v['QD']}/{v['two_q_gates']}"
 family_rows.append([r['name'],f"[[{r['n']},{r['k']},{algebraic}]]",r['target'],r['generated'],r['compiled'],r['distinct'],r['simulated'],r['certified'],r['harmful'],r['unknown'],r['construction_unknown'],best,f(r['cpu']),f(r['wall'])])
ler_rows=[[r['variant'],r['decoder'],r['seed'],r['failures'],r['shots'],f"[{r['confidence'][0]:.6g}, {r['confidence'][1]:.6g}]",f(r['cpu'])] for r in s['ler'] if r.get('shots')]
precision=s['precision'];resolved=[r for r in precision['comparisons'] if r['resolved']]
precision_text=('Resolved lower-rate intervals: '+', '.join(r['lower']+' below '+r['higher'] for r in resolved)+'. These statements apply only to the declared matching decoder and p=0.01 follow-up.') if resolved else 'The simultaneous intervals still overlap; no architecture-level LER ordering is established, and overlap does not establish equality.'
precision_rows=[[r['name'],r['failures'],r['shots'],f'{r["rate"]:.7g}',f'[{r["simultaneous_interval"][0]:.7g}, {r["simultaneous_interval"][1]:.7g}]',f(r['worker_cpu'])] for r in precision['results']]
repair_rows=[[r['variant'],r['status'],r['lower_bound'],r['upper_bound'],r['resources']['Q'],r['resources']['D'],f(r['cpu']),link(r['evidence'])] for r in s['repairs']]
schedule_rows=[[r['variant'],r['resources']['Q'],r['resources']['D'],r['resources']['QD'],r['status'],f(r['cpu']),f(r['wall']),link(r['evidence'])] for r in s['scheduling']]
control_rows=[[r['name'],f(r['random_cpu']),f(r['hybrid_cpu']),r['random_certified'],r['hybrid_certified'],f(r['common_cpu']),r['random_construction_unknown'],r['hybrid_construction_unknown']] for r in s['controls']]
recovery_root=Path('results/general_competitive/proof_continuation')/source
recovery=[]
for p in sorted(recovery_root.glob('*.json')):
 r=read(p)
 if 'answer' in r:recovery.append(dict(id=r['row_id'],status=r['answer']['result']['status'],upper_bound=r['answer']['result'].get('upper_bound'),cpu=r['answer']['cpu'],verified=r['independent_replay']['verified'],evidence=p.as_posix()))
assert all(r['verified'] for r in recovery if r['status'] in ('CERTIFIED','INVALID'))
gates={
'A':('PASS','Historical evidence hashes, immutable earlier epochs and separate original repository','None within the audited preservation scope'),
'B':('PASS','Complete physical alternatives in shared backward/forward inventories and exact CNF','Explicit-operation model; implicit idles are not added'),
'C':('PASS','Fresh positive graph certificates through target ten and independent replay','No claim for graph-ineligible projections'),
'D':('PASS','Full-signature MITM positive target-five physical circuit','Efficient applicability to all families is not established'),
'E':('PASS','Correlated alternatives and physical-location assignment in actual proofs; exhaustive adversarial oracles','No independent-Pauli-component approximation'),
'F':('PASS','Forward-inventory, partition/join, graph and Boolean witness replay','SAT branch-proof checker validated on small exact oracles; high-target SAT remained UNKNOWN'),
'G':('PASS','Actual raw non-graphlike target-five CSS circuit, MITM proof and independent replay','The surface example also admits useful graph projections'),
'H':('PARTIAL','Matched method costs at targets three, five and ten; graph ladder and complete controller/worker accounting','Broader non-graphlike scaling and competitive SAT/DP performance remain unresolved'),
'I':('PASS','Dependency DAG and actual list/critical-path/color/resource schedules','Conservative DAG preserves all explicit compiler dependencies'),
'J':('PASS','Code-only parallel extraction produces certified depth-twelve circuits','Dedicated-ancilla CSS coloring is restricted to check weight at most four'),
'K':('PASS','Certified intermediate allocations and actual Q/D/QD tradeoffs','Allocation study is finite, not a global optimum'),
'L':('PASS','Every adopted modified circuit receives fresh independent certification','This is re-evaluation, not a theorem that all reorderings preserve distance'),
'M':('PASS','Autonomous target-ten depth and QD halved from the preserved baseline','Architecture-generation improvement, not an allocation-policy speedup claim'),
'N':('PASS','Q=199, D=12, QD=2388, two-qubit count 360; independent target-ten certificates','Depth-eight reference remains better at the same Q'),
'O':('PASS','Q=101 alternative retained together with intermediate allocations','Discovery-only and reference-inclusive frontiers are separate'),
'P':('PASS','Joint resource coordinates recomputed from exact certified circuit identities','Resource-LER frontiers remain estimates'),
'Q':('PASS','Matched-noise fixed-shot matching/lookup comparisons with confidence intervals','Architecture-level matching-decoder superiority is unresolved'),
'R':('PASS','Generic adjacent/nested flag repairs independently certify the preserved Shor diagnostic at exact distance four','Not every autonomous repair candidate succeeds; original UNKNOWN/INVALID rows remain'),
'S':('PARTIAL','Autonomous Steane and Shor9 positives, plus separately certified Shor-product repairs','No broad non-surface target-five/ten competitive claim; color_small duplicates Steane'),
'T':('PASS','Observed overlapping local evaluator processes, durable checkpoints, repeated seeds and independent audit','No measured serial-versus-parallel speedup claim'),
'U':('PARTIAL','Existing API/CLI regressions and isolated installed optimize/resume pass','The standalone clean baseline has no public Search command; large-code screening remains a separate future interface'),
'V':('PASS' if archive_ok else 'PARTIAL','Clean wheel byte equality, installed CLI, local commits and artifact manifest','Final archive verification pending' if not archive_ok else 'Local delivery only; no public push')}
save('results/general_competitive/acceptance.json',dict(source=source,gates={k:dict(status=v[0],evidence=v[1],unresolved=v[2]) for k,v in gates.items()},overall='DEFINING_MILESTONES_MET_WITH_EXPLICIT_PARTIAL_GATES'))
compute=s['compute'];best=s['best_target10'];hyper=s['raw_hyperedges']
text=f'''# General certification and autonomous optimization: scientific results

Scientific source: `{source}`. Implementation commit: `{s['implementation_commit']}`. The package remains FTQEC 0.1.0. The current source is distinct from every preserved development and earlier final epoch.

Both defining milestones were demonstrated: a full-signature MITM target-five certificate on an actual CSS circuit with raw non-graphlike physical effects, and code-only autonomous target-ten extraction at **Q=199, D=12, QD=2,388, 360 two-qubit gates**. The target-ten result was independently certified for optimization seeds 0, 8 and 16. Depth and QD are half the previous autonomous values; the depth gap to the independent depth-eight reference is reduced by 75%, not eliminated.

The overall framework is not declared universally complete. Gates H, S and U remain partial. All distance claims concern extraction with ideal initial/final syndrome boundaries and explicit operation-local faults. They are not arbitrary-input physical-memory or hardware-routing guarantees. No billable cloud work or public push occurred.

The prospective protocol and raw results are in [the final epoch](../{root.as_posix()}/protocol.json). [The machine-readable summary](../results/general_competitive/summary.json) links every numerical table to raw records. The full historical regression suite passed before changes; the complete final suite is recorded in the release test receipt. {s['preservation_files']} prior evidence files were hash-checked; the old external manifest is preserved when replaced. All 41 prior resource-Pareto rows and the original Shor witness were also freshly replayed using their original source wheel; [the receipt](../results/general_competitive/historical_frontier_replay.json) states that scope.

## A. Certification-method comparison

All rows use the same complete operation-local Pauli/measurement fault universe with location exclusivity. CPU is whole evaluator-process CPU, including startup and serialization; wall is evaluator elapsed time; peak is sampled worker RSS. Independent-check cost is also stored separately in each positive result and is already included in the enclosing CPU total. Do not add it twice.

{table(['Requested method','Actual proof','Eligible class','Target','Positive','Negative','UNKNOWN','CPU s','Wall s','Peak MiB','Independent bound checked','Raw'],method_rows)}
At target three, all requests used the shared singleton/pair shortcut; these rows are not SAT, MITM or DP scalability results. On the matched higher-target eligible circuits, graph potentials were faster. MITM certified target five using raw signatures; its target-ten attempt remained UNKNOWN at the work safeguard. DP and SAT remained UNKNOWN at targets five and ten. Complete unresolved intervals and reasons remain in the raw results.

The target-five inventory contains **{hyper['alternatives']} physical alternatives**, including **{hyper['raw_hyperedges']} alternatives affecting more than two raw detectors**. MITM did not replace these with graph edges. The example also admits sound graph projections; it does not establish efficient certification of projection-ineligible non-surface families. Small exhaustive physical-alternative and SAT-assignment oracles validate correlated and location-exclusive cases separately.

## B. Target-ten resources

Each row reports all coordinates from one actual circuit. The first two rows retain the previous scientific source and proof artifacts. The reference was never an initialization seed. Exact IDs and source identities distinguish circuit instances from resource estimates.

{table(['Circuit','Q','D','QD','2Q','Certification','Circuit identity','Source prefix'],resource_rows)}
![Certified target-ten resource tradeoffs](../results/pareto/general_competitive/{source}/resource_frontier.png)

[The full certified archive](../results/pareto/general_competitive/{source}.json) retains every nondominated alternative, not just the displayed representative for each resource tuple. The discovery-only frontier excludes the reference; the all-known frontier includes it and correctly allows it to dominate discoveries at the same Q. The Q=101 alternative remains nondominated in both.

## C. Cross-family and distance-ladder results

Code parameters are independently checked in [the algebraic evidence](../results/general_competitive/algebraic/{source}). Algebraic distance is separate from requested extraction distance. Counts are per trial and are not globally deduplicated. Compiled counts completed constructor outputs; censored tasks may have compiled before timing out and are not counted as completed outputs. Simulated means completed shots. Certified means independently checked positive. A construction UNKNOWN is not a fault-invalid circuit. Unselected finalists and cheaply rejected circuits are not silently counted as completed certificates.

{table(['Trial','Algebraic parameters','Target','Generated','Compiled','Distinct valid','Simulated','Certified','Harmful','Proof UNKNOWN','Construction UNKNOWN','Best Q/D/QD/2Q','CPU s','Wall s'],family_rows)}
`color_small` has the identical stabilizer generators as Steane and is not counted as another independent construction family. The surface ladder and repaired Shor mechanism were disclosed development inputs. These finite trials demonstrate construction and recovery capabilities, not held-out universal competitiveness or global convergence.

## Scheduling and ancilla allocation

{table(['Method / slots','Q','D','QD','Status','CPU s','Wall s','Raw'],schedule_rows)}
These ablations hold code-derived interaction orders fixed. Critical-path, conflict-color and resource priority reduced depth relative to list scheduling on this instance; the joint hook/color constructor achieved the best discovery depth. The best circuit schedules up to {best['peak_simultaneous_data_interactions']} data interactions simultaneously. Intermediate ancilla allocations produce useful tradeoffs but do not beat the dedicated colored circuit's QD here. The tiny exhaustive scheduler only establishes optimality for its declared small conservative DAG; no large-circuit scheduling optimum is claimed.

## Shor hook diagnosis and repair

{table(['Variant','Outcome','Verified lower','Upper witness','Q','D','CPU s','Raw'],repair_rows)}
The original weight-three harmful mechanism remains preserved. Single-flag variants remain invalid. Adjacent/nested intervals establish full target-four exclusion with independent replay, rather than merely eliminating one witness address. The optimizer now uses physical ancilla-hook metadata to propose those generic repairs and records witness provenance. Separate bounded proof continuations of autonomous UNKNOWN candidates are retained below; they do not rewrite the original-budget outcomes.

{table(['Autonomous candidate','Continuation outcome','Upper witness','CPU s','Independent replay','Raw'],[[r['id'],r['status'],r['upper_bound'],f(r['cpu']),r['verified'],link(r['evidence'])] for r in recovery])}

## Decoder-conditional logical error evaluation

Every row uses 20,480 fixed shots, the declared operation-level noise probability in its trial name, and the same prepared logical-Z task. Intervals are per-cell 95% Wilson intervals, not simultaneous bounds over the full table. Two independent seeds are retained separately. Matching and one-mechanism lookup are different decoders and are never mixed into one resource-LER frontier.

{table(['Circuit / p','Decoder','Seed','Failures','Shots','95% interval','CPU s'],ler_rows)}
The matching-versus-lookup gap is resolved under these conditions. The pilot matching samples do not establish a reliability ordering among the discovered, low-qubit and reference architectures. Zero observed failures retains a nonzero upper uncertainty bound. Depth improvements alone do not establish lower LER, particularly because this fault model adds noise to explicit operations, not implicit idle time.

### Independent precision follow-up

The pilot's low counts motivated a separate, predeclared fixed-size follow-up at p=0.01: 1,048,576 new matching-decoder shots per circuit, in sixteen bounded batches with new seeds. Pilot samples are not pooled into these intervals. Exact Clopper-Pearson intervals use per-circuit alpha 0.05/3, giving simultaneous coverage of at least 95% across these three circuits by Bonferroni. There was no sampling until significance.

{table(['Circuit','Failures','New shots','Estimated rate','Simultaneous exact interval','Worker CPU s'],precision_rows)}

{precision_text} Raw batches, seeds, limits and their scoped costs are in [the precision study](../results/general_competitive/ler_precision/{source}/protocol.json).

## Actual-compute controls and execution

{table(['Family','Random CPU s','Hybrid CPU s','Random positives','Hybrid positives','Common CPU horizon s','Random construction UNKNOWN','Hybrid construction UNKNOWN'],control_rows)}
The paired controls use identical population settings and per-action allowances. CPU figures cover recorded optimizer controller spans plus completed evaluators; standalone driver setup and final export tails are outside that span. These are not whole-control-job totals. [The raw comparison](../results/compute/general_competitive/{source}.json) records frontiers at common measured worker-plus-controller CPU horizons. A null observation means no complete generation checkpoint at that horizon, not that no individual certificate existed. Equal generations or fewer certification calls do not establish savings. Candidate guidance and witness repair differ between arms, so these are generation-strategy comparisons, not isolated evaluation-allocation speedups.

A preserved earlier control exposed an unsupervised noiseless-validation bottleneck on a generated 59,760-operation, 11,430-detector circuit. Its interrupted costs and a bounded diagnostic are retained in the earlier source epoch. Construction is now supervised and checkpointed before work; CPU or memory limits preserve UNKNOWN candidates. There is no global optimizer time cutoff. Per-action limits and finite prospective trial populations are explicitly declared.

The final main campaign consumed **{f(compute['total_cpu'])} CPU seconds**, comprising {f(compute['controller_cpu'])} controller seconds and {f(compute['worker_cpu'])} completed evaluator seconds. Elapsed wall was {f(compute['wall'])} seconds; active wall was {f(compute['active_wall'])} seconds. Controller peak working set was {f(compute['peak_controller_working_set']/2**20)} MiB; maximum sampled evaluator RSS was {f(compute['peak_worker_sampled_rss']/2**20)} MiB. There were {compute['evaluator_tasks']} evaluator tasks and an observed peak of {compute['observed_concurrent_evaluators']} overlapping evaluators. These are main-campaign totals. Supplementary measured costs and validation receipts are separately recorded; test receipts include elapsed test time, not a reconstructed whole-project CPU total. Packaging costs are in the external manifest. No whole-project total is claimed.

## D. Acceptance gates

{table(['Gate','Status','Evidence','Unresolved requirement / scope'],[[k,*v] for k,v in gates.items()])}

## Answers to the final scientific questions

1. Implemented exact methods are singleton/pair exclusion, graph potentials, physical-location frontier DP, full-signature MITM and bounded physical-fault CNF/DPLL. No SMT, ILP or specialized treewidth/compositional backend is claimed.
2. MITM, location DP and SAT accept arbitrary supported detector signatures; graph potentials require verified channel eligibility.
3. Each correlated physical alternative carries one operation identity. MITM uses distinct-location matching, DP processes one location at a time, and SAT includes at-most-one clauses per location.
4. SAT retains every physical alternative, including zero-effect alternatives, and imposes exact detector parity, nonzero logical parity and a physical-location weight bound.
5. SAT UNSAT claims require a complete independently checked binary branch/unit-refutation tree. Small exact oracle tests establish positive tree checking; the tested higher-target physical SAT runs were UNKNOWN, not unchecked successes.
6. Yes: the raw-hyperedge CSS target-five circuit has a full-signature MITM certificate and independent replay. Its projection eligibility is explicitly disclosed above.
7. Graph potentials were fastest on the matched eligible higher-target controls. Target-three timings measure the shared pair shortcut.
8. Actual measured CPU, wall, memory and completed lower bounds are in the method and ladder tables. General exact methods hit work safeguards at target ten; no universal scaling law is inferred from three method-control targets.
9. All UNKNOWN proof and construction outcomes remain explicit in the tables and raw progress records. Work, recursion, CPU and memory safeguards are distinguished from harmful witnesses.
10. General parity/weight/location constraints retain a combinatorial search space. MITM half sets grow binomially, DP frontier states can grow exponentially, and SAT branch trees can be exponential. No universally efficient exact method is claimed.
11. Yes: the autonomous certified target-ten discovery frontier improved.
12. Best discovery: Q=199, D=12, QD=2388, 360 two-qubit gates. The separately supplied reference remains Q=199, D=8, QD=1592, 360 two-qubit gates.
13. Yes, depth twelve at Q=199 was independently certified.
14. The discovery is four layers above the depth-eight reference, with 50% greater depth/QD at the same Q; it closes 75% of the previous depth gap.
15. Yes: Q=101 and intermediate-Q alternatives remain on the joint certified discovery frontier.
16. Joint hook-guided coloring produced the best discovery. Fixed-order dependency schedulers produced the ablation results above; none is claimed globally optimal.
17. The best compiled circuit has the measured concurrent data-interaction count reported above, with actual dedicated-ancilla preparation and readout.
18. Allocation materially changes QD and the frontier; maximal parallelism is not assumed optimal a priori. The best measured QD here uses dedicated colored extraction.
19. No harmful sub-target faults were admitted by the independently certified scheduling ablations. Other population proposals were invalid; their failure is not automatically attributable to scheduling alone.
20. Yes: every adopted circuit has a fresh source-bound certificate and independent check; resource coordinates were recomputed.
21. Target-three autonomous positives extend to Steane and Shor9, with separately certified target-four Shor-product repairs. Broader high-distance non-surface competitiveness remains unresolved.
22. Generic adjacent/nested flags repair the preserved Shor mechanism in fully certified circuits. Other autonomous repair proposals remain negative or unresolved, as recorded.
23. Yes for the decoder comparison under declared noise/task assumptions. The independent million-shot follow-up above states exactly which architecture comparisons, if any, are resolved.
24. The target-ten resource result repeated across three optimization seeds. Pilot LER uses two independent seeds per cell; the precision follow-up uses sixteen new fixed batches. Other-family optimization remains a limited seed study.
25. Yes, paired controls are compared at common actual-CPU checkpoint horizons. Coarse observation granularity and censored construction prevent an unrestricted fine-grained throughput claim.
26. Main-campaign CPU, wall, active wall and process memory are reported above, with separate raw costs for supplementary work.
27. Local computing completed the declared main studies. Large general proofs and expensive construction remain bounded UNKNOWN where appropriate.
28. Cloud escalation was neither used nor justified as a substitute for the observed algorithmic/validation bottlenecks.
29. Historical artifacts remain hash-preserved and the final complete suite passes. Earlier source epochs and all negative/interrupted outcomes remain available.
30. H, S and U remain partial. The most justified next research step is a decomposition-aware exact proof study on repaired, projection-ineligible non-surface target-five circuits, using the newly supervised construction pipeline and matched actual-compute controls. A standalone inexpensive Search interface remains distinct from deep single-code Optimize.

## Reproducibility and limitations

See [general certification](GENERAL_CERTIFICATION.md), [proof methods](EXACT_PROOF_METHODS.md), [parallel scheduling](PARALLEL_SCHEDULING.md), [ancilla allocation](ANCILLA_OPTIMIZATION.md), [non-graphlike validation](NONGRAPHLIKE_VALIDATION.md), and [the protocol](OPTIMIZATION_PROTOCOL.md). The local delivery manifest identifies source files, proof artifacts, seeds, raw failures and hashes. The wheel was checked byte-for-byte and installed into a clean environment; the public optimization CLI and checkpoint resume were exercised there. The source/evidence archive is local only.
'''
Path('docs/RESULTS.md').write_text(text,encoding='utf-8')
Path('docs/LIMITATIONS.md').write_text('''# Scientific and implementation limits

Extraction certificates assume ideal initial/final syndrome boundaries and explicit operation-local faults. They do not certify arbitrary-input physical memory, implicit idle noise or routed hardware.

The raw non-graphlike target-five milestone uses a surface CSS circuit that also admits sound graph projections. Projection-ineligible non-surface target-five efficiency is not established. MITM is disk-backed but still combinatorial; DP and bounded SAT can exhaust work. The SAT backend is a small exact encoding/proof oracle, not an industrial solver. SMT, ILP, specialized treewidth and compositional proof engines are not implemented.

Joint coloring currently supports CSS check weight at most four with dedicated bare ancillas. General scheduling retains explicit dependencies conservatively. Ancilla and population searches are finite experimental samples, not global optima. General stabilizer compatibility is retained, but broad non-CSS optimization is not established.

Noiseless construction is supervised and durably checkpointed. Large generated circuits may remain UNKNOWN at declared per-action safeguards. Unknown construction is not fault invalidity. The prior unsupervised-control interruption and its costs remain preserved.

The independent depth-eight reference still beats the best depth-twelve discovery at the same Q. Lower-Q alternatives remain represented. Matching-versus-lookup differences do not imply architecture-level LER superiority. Pilot intervals are per-cell; the independent precision study uses simultaneous exact intervals and reports only the comparisons they resolve. Low-noise matching results can remain uncertain.

Steane and color_small are the same stabilizer input. Limited seeds and code families do not establish universal high-distance generalization. Actual-CPU comparisons use coarse generation checkpoints; missing early observations are not zero discoveries. Supplementary, audit, packaging and historical costs must not be folded into or omitted from the stated main-campaign scope.

The clean baseline has no standalone public Search command. Cheap large-scale screening remains a separate future interface; deep Optimize is not a surrogate code search. Gates H, S and U are therefore explicitly partial. See RESULTS.md and the raw source-bound artifacts for all remaining UNKNOWN, INVALID, censored and interrupted experiments.
''',encoding='utf-8')
print('REPORT_WRITTEN',len(text),'characters',flush=True)
