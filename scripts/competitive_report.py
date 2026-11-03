"""Generate the final report from verified raw evidence."""
import json
from pathlib import Path
from ftqec.results.artifacts import save,source_identity
read=lambda p:json.loads(Path(p).read_text())
s=read('results/competitive_export/summary.json');source=source_identity();assert s['source']==source
root=Path('results/competitive_export/final')/s['experiment_source'];delivery=Path('results/competitive_export/delivery')/source
front=read(Path('results/pareto/competitive_export')/(source+'.json'))
def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+''.join('| '+' | '.join(str(v).replace('|','/') for v in row)+' |\n' for row in rows)
def link(p):return '['+Path(p).name+'](../'+str(p).replace('\\','/')+')'
def f(v):return f'{v:.3f}'
resource=[];seen=set()
for r in sorted(front['archive'],key=lambda r:(r['resources']['Q'],r['resources']['D'],r['origin'])):
 v=r['resources'];key=(r['origin'],r['id'])
 if key in seen:continue
 seen.add(key);resource.append([r['origin'],r['id'],r['source'],v['Q'],v['D'],v['QD'],v['two_q_gates'],r['certify']['status'],r['certify'].get('independent',{}).get('verified')])
methods=[]
for r in s['methods']:
 family=r['family'].replace('_decomposition','');epath=root/'eligibility'/(family+'.json');eligible=r.get('graph_eligible',read(epath)['receipt']['eligible'] if epath.exists() else 'see inventory')
 methods.append([r['family'],eligible,r['target'],r['requested'],r['method'],r['fault_alternatives'],r['lower_bound'],r['upper_bound'],r['status'],f(r['cpu']),f(r['wall']),f(r['peak']/2**20),r['independent'].get('verified',False),link(r['evidence'])])
families=[]
for r in s['families']:
 if r['name'].startswith('control_'):continue
 family=r['name'].split('_seed')[0];a=read(root/'algebraic'/('surface10.json' if family=='surface10' else family+'.json'));params='[[100,1,10]]' if family=='surface10' else str([[a['result']['n'],a['result']['k'],a['result']['distance']]])
 v=r['best'];best='/'.join(str(v[k]) for k in ('Q','D','QD','two_q_gates')) if v else 'none'
 families.append([r['name'],params,r['target'],r['generated'],r['compiled'],r['distinct'],r['simulated'],r['certified'],r['harmful'],r['unknown'],r['construction_unknown'],best,f(r['cpu']),f(r['wall']),link(r['evidence'])])
exports=[[r['name'],r['manifest']['circuit'],r['manifest']['schedule'],r['manifest']['evidence_source'],'JSON/Stim/schedule JSON+text/proof bundle',r.get('evaluation_status',r['verification']['recorded_status']),r['verification']['reconstruction_verified'],r['verification']['resource_recomputation_verified'],r['verification']['certificate_binding_verified'],r['verification']['positive_certificate_verified'],link(r['evidence'])] for r in s['exports']]
ler=[[r['name'],r.get('failures'),r.get('shots'),r.get('rate'),r.get('simultaneous_interval'),r.get('decoder'),link(r['evidence'])] for r in s['ler']]
matched=[[r['name'],f(r['common_cpu_budget']),f(r['last_observed_checkpoint_cpu']),r['checkpoint_generation'],len(r['frontier']),min((x['resources']['QD'] for x in r['frontier']),default='none')] for r in s['matched_compute']]
resolved=[r for r in s['ler_comparisons'] if r['resolved']]
ler_conclusion=('Nonoverlapping simultaneous intervals support '+', '.join(r['lower']+' below '+r['higher'] for r in resolved)+' for this noise model and matching decoder only.') if resolved else 'Simultaneous intervals overlap: no architecture-level logical-error ordering is established. Overlap does not establish equality.'
preservation=read('results/competitive_export/preservation.json');tests=read(Path('results/competitive_export/implementation_tests')/source/'receipt.json');install=read(Path('results/competitive_export/release')/source/'clean_install.json');assert tests['returncode']==0 and install['status']=='PASS'
gates={
'A':('PASS','Historical hashes unchanged; old documents and epochs preserved','No historical numerical evidence rewritten'),
'B':('PASS','Actual critical paths diagnose four-layer phase separation','Eight-layer lower bound is gadget-vocabulary specific'),
'C':('PASS','Joint parity-constrained coloring and dependency schedulers','No universal schedule optimum or CP-SAT result'),
'D':('PASS','Certified target10 shares interaction layers across CSS axes','Joint coloring currently requires check weight at most four'),
'E':('PASS','Compiled allocation ablations and certified lower-Q alternatives','Finite study, not global allocation optimum'),
'F':('PASS','Independent replay and fresh certification of delivered circuits','Negative transformations are retained'),
'G':('PASS','Code-only seeds 24,32,40 certify Q199/D8 at target10','Reference loaded after discovery trials'),
'H':('PASS','D12 to8 and QD2388 to1592 at fixed Q199','Actual 360 two-qubit gates'),
'I':('PASS','Q101 and intermediate alternatives retained','Dominated historical rows remain archived'),
'J':('PASS','Whole-location alternatives and full signatures','Explicit-operation, ideal-boundary model'),
'K':('PASS','Independent Shor graph-projection obstruction checks','Ineligible for implemented portfolio, not every conceivable graph encoding'),
'L':('PARTIAL','Exact component/separator elimination and independent checker','Positive physical proof required; see method table'),
'M':('FAIL','No graph-ineligible non-surface target5 positive','Nine weight4 witnesses and seven resource-limited UNKNOWN Shor5 tasks'),
'N':('PASS','All reported final positives and negatives independently replayed','UNKNOWN remains unresolved; unchecked UNSAT not accepted'),
'O':('PARTIAL','Surface, Steane, Hamming-HGP autonomous positives','Autonomous Shor target4 trials failed'),
'P':('PASS','Shor4 repair Q136 to64, independently recertified','Unused ancillas removed; depth and verification gates unchanged'),
'Q':('PASS','Installed complete circuit JSON/Stim export','Ideal simulation boundaries explicitly marked'),
'R':('PASS','Exact schedule JSON/text and public SVG renderer','Large displayed subsets labelled'),
'S':('PASS','Independent schedule and resource reconstruction','Producer metrics not trusted'),
'T':('PASS','Candidate, exact circuit, fault model and source bindings','Each delivered positive freshly certified under matching source'),
'U':('PASS','Fixed batches, matched decoder/noise and simultaneous intervals','Decoder-independent superiority not claimed'),
'V':('PASS','Actual populations, histories, repairs and Pareto archives','Finite search does not establish global optimum'),
'W':('PARTIAL','Actual CPU checkpoint comparisons','One control seed and coarse checkpoints limit speedup claims'),
'X':('PASS','Overlapping worker intervals, seeds, durable resume','No measured parallel speedup claim'),
'Y':('PARTIAL','Legacy API default and installed optimize/resume preserved','Standalone baseline has no Search command'),
'Z':('PASS','Clean installation, full tests, bundles, source snapshots and manifest','Local delivery; no public push')}
positive=[r for r in s['methods'] if r['requested']=='decomposition' and r['method']=='component-separator-location-dp-1' and r['status']=='CERTIFIED' and r['independent'].get('verified')]
if positive:gates['L']=('PASS','Independently checked physical separator proof: '+', '.join(r['family'] for r in positive),'High-distance graph-ineligible target5 still unresolved')
save('results/competitive_export/acceptance.json',dict(source=source,experiment_source=s['experiment_source'],gates={k:dict(status=v[0],evidence=v[1],unresolved=v[2]) for k,v in gates.items()},overall='PARTIAL: graph-ineligible non-surface target5 not achieved'))
followup_table=table(['Case/method','Status','Reason','Lower','Upper','CPU s','Wall s','Peak MiB','Raw'],[[r['name'],r['status'],r['reason'],r['lower_bound'],r['upper_bound'],f(r['cpu']),f(r['wall']),f(r['peak']/2**20),link(r['evidence'])] for r in s['followup']['rows']])
compute=s['compute'];totalcpu=compute['worker_cpu']+compute['controller_cpu']
qa=[
'Compiler phase separation placed four X interaction layers before four Z layers. Native Z readout and parity-constrained shared layers close that gap.',
'Wire conflicts, reset/measurement lifecycles and instrument parity remain necessary. Separate compiler phases were conservative; cancelling pairs permit collective rewrites beyond pairwise commuting swaps.',
'Joint support coloring, algebraic hook guidance, dependency/critical-path/list/resource/conflict schedules, small exact DAG scheduling and unused-ancilla compaction are implemented. CP-SAT is not claimed.',
'Yes. Three independent code-only seeds certify target10 at Q199,D8; see Table A and source-bound optimizer records.',
'The depth-eight discovery has Q199,D8,QD1592 and 360 two-qubit gates. Table A preserves complete resource tuples and identities.',
'Yes. Q101 and intermediate allocations remain in the archive and nondominance is recomputed.',
'Allocation ablations compile real circuits and receive fresh certification. The frontier records show which survive; no global allocation optimum is claimed.',
'Yes. A shared four-color interaction assignment permits both axes to overlap. Earliest-start scheduling places CNOTs in five global layers,1–5; the certified eight-layer critical path contains four CNOTs. Actual layer counts are retained in best_critical_path.json.',
'Some general mutations and schedules remain harmful, with replayed witnesses. Adopted depth-eight circuits have positive target10 certificates.',
'Discovery uses only code supports/logicals and generic parity constraints. Reference circuits are loaded after all code-only trials, not used as seeds.',
'All configured projections are checked. A failing logical channel has explicit projected degree-greater-than-two physical obstructions for every choice, independently checked by forward propagation.',
'Flagged Shor-product circuits fail the declared graph portfolio. Raw hyperedges alone do not establish this; the old graph-eligible surface target5 case is not relabelled.',
'Whole-location detector components, exact invertible detector coordinates and greedy separator-frontier elimination were added, with a separate transition-table verifier.',
'No. Nine randomized Shor5 tasks found harmful weight4 witnesses and seven exhausted per-task safeguards. The positive graph-ineligible Shor result remains target4.',
'Yes. Each variable chooses identity or one complete alternative at a physical location. Correlated components are not independently selectable.',
'All reported final positives are replayed under exact source binding. Delivered circuits also receive fresh certification after the export-only fix.',
'Table B compares identical physical circuits and obligations. Shared pair shortcuts are labelled by actual proof; they do not demonstrate SAT or MITM scaling.',
'Raw packets retain whole-process CPU, wall, individual-worker peak RSS, proof tables, widths and unresolved progress. Guard termination is not scientific invalidity.',
'UNKNOWN method and randomized-development packets retain reasons and inputs. A killed worker may lack a serialized intermediate bound; this is stated rather than inferred.',
'Exact state growth can be exponential in separator width or fault weight. Coordinate/order choices are heuristics, not minimum-treewidth or universal-efficiency proofs.',
'Surface [[100,1,10]], Steane [[7,1,3]], Shor-product [[16,1,4]] and Hamming-HGP [[58,16,3]]; algebraic distances are independently checked.',
'Autonomous positives occurred for surface, Steane and Hamming-HGP. Frozen autonomous Shor target4 trials did not certify a candidate.',
'The retained certified Shor4 repair improves Q136 to64 by deleting unused allocated ancillas; D83 and 228 two-qubit gates are unchanged. This is distinct from autonomous repair discovery.',
'Tables A/C and complete archives give actual Q/D/QD/2Q tuples, never componentwise mixtures from different circuits.',
'The same pipeline produces positives in three families. Competitive high-distance depth is established on the surface development case only.',
'Target10 uses three seeds; other families use two. Strategy controls use one seed and do not establish across-seed superiority.',
'No family-name winning schedule or reference seed was added. Joint coloring has a check-weight restriction; native-Z simplification applies to bare pure-Z checks.',
'Actual Steane/HGP autonomous positives and Shor repair compression support limited generalization. Shor autonomous failure and the target5 proof gap remain.',
'Yes: list-results supplies a candidate ID, then export writes complete JSON, compatible Stim or a research bundle.',
'Yes: schedule-json includes starts, dependencies, measurement indices and ancilla lifecycles; render-schedule writes SVG.',
'Yes. Independent reconstruction checks all gate, timing, dependency and full circuit identity bindings.',
'Yes within the declared representation. Ideal Stim boundary operations are distinguished from physical extraction gates; physical memory remains outside scope.',
'Yes. The installed audit exposed and fixed a physical candidate ID versus serialized circuit ID mismatch; both are now explicitly retained.',
'Compatible exports load into Stim and are checked against the independently constructed simulation model.',
'Yes. verify-export --require-certified requires positive proof replay; ordinary verification separately reports reconstruction and proof status.',
'Yes. Resources are recomputed from reconstructed operations/schedules; bundles retain inputs, provenance, proof, source and simulation evidence.',
'Fixed matching-decoder batches use the same p=.01 noise, seeds and shot budgets. The uncertainty table qualifies every comparison.',
ler_conclusion+' Resource improvement is separate from rate ordering.',
f'Recorded discovery/completion CPU is {totalcpu:.3f}s and summed recorded session wall is {compute["session_wall"]:.3f}s. Individual-worker peak is {compute["peak_worker_rss"]/2**20:.3f}MiB. Development/tests/packaging have separate receipts.',
'Local execution completed the finite campaign and delivery. Resource-limited general proofs remain unresolved.',
'No cloud was provisioned. Counterexample repair and exact-proof width are the next bottlenecks, not a demonstrated need to spend on cloud.',
'Every frozen historical evidence hash matches; the complete existing and new suite passes. Scientific behavior is also checked by independent source-specific replays.',
'Gate M fails; O,W,Y remain partial. Gate L follows the actual physical method result rather than software tests. See the complete A-Z matrix.',
'Use Shor hook witnesses to repair candidates, then reduce exact separator/constraint width to obtain one independently checkable graph-ineligible non-surface target5 positive.'
]
text=f'''# Competitive synthesis, exact certification and reproducible delivery

Three code-only target10 seeds certify **Q199, D8, QD1592 and 360 two-qubit gates**. The graph-ineligible non-surface target-five milestone is **not achieved**. The overall mission remains partial.

Discovery source: {s['experiment_source']}. Delivery source: {source}. Implementation commits: {s['implementation_commit']} (discovery engines), {s['delivery_implementation_commit']} (delivery fix). Only export/verification identity integration changed between these sources; scientific engines are byte-identical. The original campaign and failed installed export are preserved. Each delivered circuit receives fresh certification instead of rewriting its old source identity. See {link(delivery/'protocol.json')}. FTQEC remains 0.1.0.

Distance claims cover explicit operation-local faults with ideal code-space initial/final syndrome boundaries, not arbitrary-input physical memory, implicit idle noise or hardware routing. No global optimum or universal polynomial certification is claimed.

## Four independent milestones

| Milestone | Status | Evidence and limit |
| --- | --- | --- |
| Competitive autonomous target10 | PASS | Three code-only seeds independently certify Q199/D8; no reference seed. |
| Graph-ineligible non-surface target5+ | FAIL | No positive; exact physical witnesses and unresolved proof obligations retained. |
| Cross-family generalization | PARTIAL | Surface, Steane and HGP autonomous positives plus certified Shor repair compression; autonomous Shor4 trials fail and broad competitiveness is unestablished. |
| Reproducible circuit delivery | PASS | 29 inspected bundles: 26 positive, two negative and one UNKNOWN; installed public commands and independent reconstruction verified. |

## Table A — Target10 certified resource archive

Reference rows are explicit and never seeded discovery. Optimizer physical candidate IDs and exact auxiliary IDs are distinguished in raw records; exports bind both candidate and full serialized identity. The [full Pareto archive](../results/pareto/competitive_export/{source}.json) separates discovery-only and reference-inclusive frontiers.

{table(['Origin','Circuit/candidate ID','Source','Q','D','QD','2Q','Status','Independent'],resource)}

D12 to8 and QD2388 to1592 are one-third reductions at fixed Q199, closing the four-layer reference gap. These are best-found compiled results, not global optima.

![Certified resource tradeoffs](../results/pareto/competitive_export/2c806077ca35e80028b6f49add2dbd46390d1d400bb8f7b28452d3f3f038ae58/resource_frontier.png)

Only plotted points are compiled candidates; connecting lines guide the eye.

## Table B — Matched certification methods

Complete correlated alternatives and location exclusivity are retained. CPU includes evaluator startup/serialization. Producer independent-check cost is already included; later replay cost is separately recorded. For UNKNOWN rows an independent check validates only the completed lower bound, not the requested distance. Actual proof names expose shortcut use. The surface2 row is a separately labelled physical backend validation, not a matched timing comparison; the Steane target3 request retained its pair proof after separator work exhausted. Widths, tables, detector counts and unresolved progress remain in the raw artifacts.

{table(['Family','Graph eligible','Target','Requested','Actual proof','Alternatives','Lower','Upper','Status','CPU s','Wall s','Peak MiB','Independent','Raw'],methods)}

### Target-five follow-up on unresolved Shor cases

{followup_table}

Cases were selected before outcomes as the first unresolved adjacent and nested cases in original seed order. Separate limits are 20 million proof operations and180 CPU seconds per task. Follow-up worker CPU is {s['followup']['worker_cpu']:.3f}s; controller and wall costs remain in its complete receipt. Initial UNKNOWN results remain unchanged even if this follow-up finds a witness.

## Table C — Cross-family autonomous optimization

Generated/compiled counts include duplicates. Certified/UNKNOWN columns count certification outcomes; harmful counts candidates with a screen or certification witness, without double counting. Simulated counts completed shot batches; failed attempts and unselected rows remain in checkpoints. Code distances are separately verified algebraic quantities.

{table(['Run','Algebraic n/k/d','Target','Generated','Compiled','Distinct','Simulated','Certified','Harmful','UNKNOWN','Construction UNKNOWN','Best Q/D/QD/2Q','CPU s','Wall s','Raw'],families)}

The Hamming hypergraph-product construction follows [Tillich and Zemor](https://arxiv.org/abs/0903.0566); matrices and algebraic audits are preserved. Steane is not double-counted as an independent seven-qubit color family.

## Table D — Export verification

Every bundle contains complete JSON circuit, JSON/text schedule, compatible Stim, resources, source and proof/evidence. SVG is available through the public renderer. A negative or UNKNOWN bundle can reconstruct correctly without a positive certificate. A guard-terminated UNKNOWN has no completed bound certificate: its exact outcome remains in certification_attempt, and the verifier separately reports certificate replay as not run.

{table(['Name','Exact circuit','Schedule','Evidence source','Formats','Recorded status','Reconstruction','Resources','Binding','Positive replay','Raw'],exports)}

[Full target10 gate timeline](../results/exports/competitive_export/2c806077ca35e80028b6f49add2dbd46390d1d400bb8f7b28452d3f3f038ae58/target10_schedule_all_qubits.svg) · [Compact data-qubit view](../results/exports/competitive_export/2c806077ca35e80028b6f49add2dbd46390d1d400bb8f7b28452d3f3f038ae58/target10_schedule.png)

## Reliability and actual-compute comparisons

Each arm uses eight new batches of 65,536 shots at p=.01, matched seeds and the matching decoder. Reset/readout bit flips, other one-qubit depolarization and two-qubit depolarization are explicit; ideal boundaries are noiseless and implicit idles absent. Stim prepares a logical-Z sector; these rates concern its declared logical observables and are narrower than full logical-coset fault exclusion. Simultaneous 95% exact binomial Clopper-Pearson intervals use Bonferroni adjustment across three arms.

{table(['Arm','Failures','Shots','Rate','Simultaneous interval','Decoder','Raw'],ler)}

{ler_conclusion}

![Decoder-conditional error-rate comparison](../results/pareto/competitive_export/2c806077ca35e80028b6f49add2dbd46390d1d400bb8f7b28452d3f3f038ae58/logical_error_rates.png)

{table(['Control','Common actual CPU budget s','Observed checkpoint CPU s','Generation','Certified frontier size','Best QD'],matched)}

Comparisons use the last completed controller-plus-worker CPU checkpoint at or below a common budget. No within-generation events are inferred. One control seed and coarse checkpoints limit algorithmic speedup conclusions.

Recorded worker CPU: {compute['worker_cpu']:.3f}s; controller CPU: {compute['controller_cpu']:.3f}s; summed session wall: {compute['session_wall']:.3f}s. Peak individual worker RSS: {compute['peak_worker_rss']/2**20:.3f}MiB; controller peak: {compute['peak_controller_working_set']/2**20:.3f}MiB. These are not a simultaneous whole-system memory peak. Two failed delivery-controller intervals were not captured; their worker results and costs are retained. Thus recorded CPU is not a complete total for all attempts. [The summary](../results/competitive_export/summary.json) records overlapping worker PID intervals. Development, tests, preservation and packaging have separate receipts and are excluded from these campaign totals.

## Table E — Acceptance gates

{table(['Gate','Status','Evidence','Qualification'],[[k,*v] for k,v in gates.items()])}

## Answers to all 44 required questions

'''+''.join(f'{i}. {answer}\n\n' for i,answer in enumerate(qa,1))+f'''
## Reproduction and remaining work

Installed commands, checkpoint/resume, all export formats and independent positive verification pass; see {link(Path('results/competitive_export/release')/source/'clean_install.json')}. Full-suite results are in {link(Path('results/competitive_export/implementation_tests')/source/'receipt.json')}. Historical preservation covers {preservation['count']} files with zero mismatches.

Use ftqec list-results --run RUN, then ftqec export ID --run RUN --format bundle --output NEW_DIRECTORY, and ftqec verify-export NEW_DIRECTORY --require-certified. Current-source records are indexed in {link(delivery/'index.json')}. Render schedule.json with ftqec render-schedule.

The next justified step is a graph-ineligible non-surface target-five proof campaign driven by actual Shor hook witnesses and measured separator width. Increasing a global runtime limit, compiling a distance-five code, or reusing the old graph-eligible surface certificate does not meet that missing milestone.
'''
Path('docs/RESULTS.md').write_text(text,encoding='utf-8')
Path('docs/LIMITATIONS.md').write_text("""# Scientific limitations

The graph-ineligible non-surface target-five positive milestone is not achieved. Target10 depth8 is certified for three code-only seeds, not globally optimal. Autonomous target4 Shor populations failed in the finite study; compacting an existing repair is reported separately.

Exact separator elimination can grow exponentially. Raw/span coordinate selection is exact but heuristic. UNKNOWN preserves unresolved obligations. Graph ineligibility refers to the implemented projection portfolio.

Certificates cover explicit operation-local faults and ideal boundaries, not arbitrary-input physical memory, implicit idles, routing or arbitrary hardware noise. Logical-error measurements are decoder-conditional; see RESULTS.md for uncertainty.

Controls use measured CPU but one seed and coarse checkpoints. The baseline has no public Search command. CP-SAT performance, universal exact efficiency and broad high-distance non-surface superiority are not claimed.

Raw guard-only optimizer rows do not contain a bound certificate and direct bundle export rejects them. Complete individual circuit/schedule formats work; supplied normalized delivery records retain UNKNOWN task evidence separately and export without a certificate. Two failed delivery-controller timing intervals were unmeasured; recorded worker costs remain intact.

The installed export audit found a candidate-versus-exact-ID mismatch. Its failure is preserved; only delivery code changed and delivered circuits received fresh source-bound certification. Use verify-export --require-certified under the matching source.
""",encoding='utf-8')
print('REPORT_WRITTEN',len(qa),flush=True)

