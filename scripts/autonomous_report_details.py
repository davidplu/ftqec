"""Add source-qualified release evidence to the generated scientific report."""
import json,hashlib
from pathlib import Path
from collections import Counter
from ftqec.results.artifacts import source_identity,save
source=source_identity()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
ladder=read('benchmarks/distance_ladder/autonomous/summary.json')['rows']
refs=read('results/certificates/reference_validation/summary.json')['rows']
qa=read('results/autonomous/release/test_source_receipt.json')
lines=['','## Independent release verification','',
'All 77 tests passed under identical before/after scientific source hashes. Basic correctness linting and static type checking passed. Independent release replay rechecked the minimum-QD positive at each target and all recorded primary and comparison campaign harmful witnesses, plus selected independently bounded UNKNOWN candidates. A data-qubit permutation and generator reorder were also validated without reference schedules.',
'', 'The interrupted initial epoch is retained separately. Windows recorded standby during its unusually long elapsed interval; that elapsed time is not uninterrupted compute. A sharing violation and early resource-pause reporting failure were fixed before the repeated epoch. An intermediate test invocation overlapped source edits and is explicitly excluded from release validation. The authoritative test receipt is `results/autonomous/release/test_source_receipt.json`. The repeated target-eight campaign also spanned system suspension: 33,294.127 elapsed seconds versus 850.390 active seconds. Its active-time safeguards allowed continuation; the elapsed column is not uninterrupted compute. The recorded clock difference and Windows events are preserved in the release evidence.',
'', 'The signed noiseless Stim flow oracle has a documented false-acceptance bound of 2^-256; physical inventory propagation, potential inequalities and fault-witness replay are checked independently. Certificates remain conditioned on the declared instrument and operation-local fault model.',
'', '## Per-target rejection, memory and first discovery','',
'| Target | Verified fault rejections | Proof UNKNOWN | First certificate elapsed s | Active elapsed s | Peak sampled worker MiB |','|---:|---:|---:|---:|---:|---:|']
for r in ladder:
 c=r['compute'];first=c.get('first_certified',{}).get('elapsed_wall')
 lines.append(f"| {r['target']} | {r['fault_rejected']} | {r['unknown']} | {format(first,'.3f') if first is not None else 'unobserved'} | {sum(x.get('active_wall',x['wall']) for x in c['sessions']):.3f} | {max((v['peak_rss'] for v in c['tiers'].values()),default=0)/2**20:.2f} |")
lines+=['','First-certificate time is relative to the recorded session. Worker RSS is sampled and does not include all controller/host memory. Each action retains a 512 MiB worker allowance, 300 CPU-second and 600 active-second safeguard; host admission preserves a 512 MiB reserve. These are per-action safeguards, not a global optimization cutoff. Windows active elapsed time excludes system sleep; ordinary elapsed time remains separately reported. Nested decoder timing is not added again to enclosing task CPU.',
'', '## Independent reference resource controls','',
'Reference circuits are controls and were never supplied to the optimizer. This table exposes the optimization gap: a discovered certified circuit need not match a known schedule on depth.',
'', '| Target | Reference status | Q | D | QD | Two-qubit gates |','|---:|---|---:|---:|---:|---:|']
for r in refs:
 m=r['resources'];lines.append(f"| {r['target']} | {r['status']} | {m['Q']} | {m['D']} | {m['QD']} | {m['two_q_gates']} |")
lines+=['','## Successful families and improvement history','', '| Target | Certified architecture counts | Generations | First frontier points | Final frontier points |','|---:|---|---:|---:|---:|']
for r in ladder:
 s=read(f"results/discovery/autonomous/{r['name']}/checkpoint.json")
 counts=Counter(v['genome']['family'] for v in s['rows'] if v.get('certify',{}).get('status')=='CERTIFIED')
 h=r['frontier_history'];lines.append(f"| {r['target']} | {dict(counts)} | {len(s['generation_compute'])} | {len(h[0]['certified_pareto']) if h else 0} | {len(h[-1]['certified_pareto']) if h else 0} |")
lines+=['','Counts of frontier identities can change without better resource coordinates. The complete generation histories and circuit resources, rather than frontier size alone, are the evidence of improvement. Stopping means the declared resource-coordinate plateau, not exhaustive optimality.',
'', '## Remaining engineering and scientific work','',
'- Resource-LER selection remains limited by broad candidate-wise intervals; allocate more paired samples prospectively to resolve uncertain frontier comparisons.',
'- Policy comparisons use one trial and coarse completed-wave checkpoints. Repeat frozen seeds and compare achieved frontiers at common measured CPU budgets before claiming efficiency gains.',
'- Scaling stores and screens 10,000 actual circuits, but does not demonstrate a 10,000-member fully evaluated optimizer population. Add a disk-backed population/checkpoint store and a prospective population-size quality study.',
'- High-distance autonomous results cover the surface construction family. First diagnose and repair the measured Shor interval-hook failures; use a fresh non-surface CSS family split for follow-up performance claims, preserving unsuccessful and unresolved proofs.',
'- Known reference controls may retain a depth advantage. Improve generic scheduling while preserving each independently checked physical certificate.']
generation=read('benchmarks/policy_comparison/autonomous_generation/summary.json')['rows']
lines += ['', '## Separate-family unresolved obligations', '', '| Family | Strategy | Certificate outcomes | Independently verified lower bound among UNKNOWN |', '|---|---|---|---:|']
obligations=[]
for run in generation:
 state=read('results/discovery/autonomous_comparison/'+run['name']+'/'+run['strategy']+'/checkpoint.json')
 counts=Counter(r.get('certify',{}).get('status','NOT_SELECTED') for r in state['rows'])
 lower=1
 for r in state['rows']:
  cert=r.get('certify',{})
  if cert.get('status')=='UNKNOWN':
   if cert.get('independent',{}).get('verified'):lower=max(lower,cert.get('lower_bound',1))
   obligations.append(dict(family=run['name'],strategy=run['strategy'],id=r['id'],architecture=r['genome']['family'],lower_bound=cert.get('lower_bound',1),independent=cert.get('independent'),unresolved=cert.get('unresolved',[]),progress=cert.get('progress',[])))
 lines.append(f"| {run['name']} | {run['strategy']} | {dict(counts)} | {lower} |")
save(Path('results/autonomous/release/family_obligations.json'),dict(source=source,rows=obligations))
lines += ['', 'NOT_SELECTED means no positive certification was attempted for that candidate in the declared search; it is not INVALID. An independently established lower bound of three at requested target four leaves harmful weight-three configurations unresolved. This can reflect proof complexity or an undiscovered harmful configuration; it does not establish distance four. Failed final-family runs are retained without tuning the frozen optimizer on their outcomes.']
diagnostic=read('results/autonomous/posthoc_shor_diagnosis/result.json')
assert diagnostic['status']=='VERIFIED_WEIGHT_THREE_WITNESS'
lines += ['', '## Post-evaluation Shor failure diagnosis', '',
'After freezing and completing all comparison arms, a separate diagnostic selected the lowest-QD independently bounded UNKNOWN Shor candidate (`d82e4390d31ed266`): Q=31, D=32, QD=992. The independent lower bound was three. It found legal faults at operations 20, 33 and 36, with labels IX, XI and XI respectively. Two X faults on syndrome ancilla 29 bracket interactions with data qubits 5, 4 and 6; the data X on qubit 7 completes logical operator `IIIIXXXXIIIIIIII`. Every detector and flag remains zero. Independent physical replay verifies the harmful weight-three witness.',
'',f"This establishes failure of requested target four for that one candidate, consistent with its earlier UNKNOWN result. The diagnostic examined {diagnostic['pairs_examined']} fault pairs and used {diagnostic['cpu']:.3f} body CPU seconds; this is not a matched-policy timing comparison. Original benchmark decisions and counts remain unchanged. The other unresolved candidates are not reclassified from this one example. The helper never promotes positive certificates; its artifacts are in `results/autonomous/posthoc_shor_diagnosis`."]
concurrency=read('results/autonomous/release/concurrency.json')
ratio=(concurrency.get('best_measured_overlap') or {}).get('worker_cpu_per_elapsed_second',0)
lines += ['',f"Observed simultaneous evaluator lifetimes: {concurrency['observed_peak_concurrent_evaluators']}. The strongest measured two-worker interval used {ratio:.3f} CPU seconds per elapsed second. A ratio above one establishes multicore execution during that interval; it is not a serial-versus-parallel speedup benchmark. Whole-process CPU includes all native-library threads; the ratio is not a count of evaluator processes."]
scaling=read('results/autonomous/release/scaling_accounting.json')
lines += ['', '## Scaling accounting and diversity', '', f"All {scaling['unique_circuits']} circuit identities are unique across {scaling['chunks']} preserved chunks. Architecture counts: {scaling['families']}. There are {scaling['distinct_resource_vectors']} distinct (Q, D, QD, two-qubit gates, measurements) resource vectors. A memory pause at 9,335 circuits preserved its partial chunk; the unchanged study resumed and reached 10,000.", '', scaling['qualification'], '', f"The observed protocol-to-completion file timestamp span was {scaling['observed_file_timestamp_span']:.3f} seconds, including the pause. Complete end-to-end CPU accounting for checkpoint packing and recovery remains an instrumentation follow-up.", '', '## Research figures', '', '![Target-10 resource comparison](../results/autonomous/release/figures/target10_resources.png)', '', '![Matched decoder comparison](../results/autonomous/release/figures/target10_decoders.png)']
with Path('docs/RESULTS.md').open('a',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
print('Release detail appended for',len(ladder),'targets')

compute_root=Path('results/compute/autonomous');compute_root.mkdir(parents=True,exist_ok=True)
for row in ladder:save(compute_root/(row['name']+'.json'),dict(source=source,compute=row['compute'],discovery_run='results/discovery/autonomous/'+row['name']))
save(compute_root/'index.json',dict(source=source,primary_runs=[r['name'] for r in ladder],scaling='benchmarks/population_scaling/autonomous',generation_comparisons='benchmarks/policy_comparison/autonomous_generation',allocation='benchmarks/policy_comparison/autonomous',decoder='results/ler/autonomous_decoder',scope='Per-experiment accounting; no sum of nested decoder and worker CPU'))
