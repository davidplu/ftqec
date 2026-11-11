# Paired 2BGA architecture discovery: scientific report

This report records the completed experiments and delivery checks on
2026-11-11. **The research mission remains PARTIAL.** It is not a claim that
all acceptance gates have passed. Raw evidence is preserved under
`results/phase3/epoch-20261109/`; that private local evidence directory is excluded
from Git. The implementation guide is [PHASE3_OPTIMIZATION.md](PHASE3_OPTIMIZATION.md).

## Principal result and scope

Two code-only searches each completed 100 architecture proposals. Each retained
194 distinct compiled sector circuits within its own run; these counts must not
be added as a claim of uniqueness across runs. The first search produced a paired
target-six architecture using **120 physical qubits**, compared with the preserved
144-qubit baseline. Its worse-sector depth is 124 instead of 76, and its worse-sector
QD is 14,880 instead of 10,944. This is a 24-qubit reduction (16.7%) with a depth/QD
tradeoff, not a dominance improvement in all resource dimensions.

The second run produced a certified 132-qubit pair with worse-sector depth 148
and QD 19,536. It is dominated by the first run's 120-qubit pair on the reported
aggregate resource dimensions and is retained as evidence rather than promoted
as a better frontier point. Both new pairs use 2,592 two-qubit gates per sector.

A recorded follow-up promoted all seven previously unproved pairs with Q≤144
and worse-sector depth below 76 from those same autonomous populations. It found
one **new paired depth improvement: Q=144, D=64/62, QD=9,216/8,928**, with 2,592
two-qubit gates per sector. Both sectors passed fresh export reconstruction,
independent proof replay, and six-location upper-witness replay. Thus this pair
has exact distance six and matches the adapted reference's resource tuple. It
reduces baseline depth by 12 layers in each sector. The 120-qubit alternative
remains nondominated. This continuation was a recorded resource-based selection,
not a reference-seeded proposal or a change to the completed campaigns' counts.

The circuit-distance lower bounds cover the unchanged declared operation-local
fault universe and the actual six-round physical X/Z preparation and readout
boundaries. Fresh legal six-location witnesses were replayed for every positive
sector in both campaigns (`upper-witnesses/summary.json`). Together with the
independently checked lower-bound certificates these establish exact distance six.
They do not establish arbitrary-input memory fidelity, implicit storage noise,
hardware-route correctness, or decoder-independent reliability.

## Source and discovery provenance

| Campaign | Scientific source | Seed | Proposals | Compiled sector circuits | Positive sectors | Certified pairs | Invalid sectors | UNKNOWN proofs |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `discovery-structured-73011` | `e1b83faf1e84860831a28e48355de20b245b2c3adbe3a3722d77debec1066713` | 73011 | 100 | 194 | 3 | 1 | 12 | 5 |
| `discovery-affine-73029` | `fde497d647be84a403e617746ee9be2162d592242bf84c207840715416c78dd7` | 73029 | 100 | 194 | 7 | 1 | 29 | 4 |

Counts come from each run's `summary.json`. A circuit that has not been promoted
to a proof task is not counted as a completed UNKNOWN proof. Invalid counts include
screening or certification witnesses. The runs differ in source, seed, and number
of promotions (one versus two pairs per window). They are **not** a matched-compute
test of the affine method or a controlled multi-seed policy comparison.

Each campaign also had three construction attempts stopped by the worker memory
ceiling, recorded as UNKNOWN before circuit adoption. These are separate from
the proof-stage UNKNOWN counts and are preserved in
`censored-construction-summary.json`. The earlier reference admission failure,
baseline test failures, projection-refinement safeguard, and interrupted first
campaign are retained in their original logs. The initial baseline suite had six
worker-dependent failures and 162 passes; its targeted retry passed 11 tests.
The later complete suites passed 173 and then 175 tests. No scientific result is
inferred from those software-test outcomes alone.

Proposals use code-derived interaction orders, ancilla pools, check ordering and
basis choices, and existing flag/cat alternatives. The published reference is not
an optimizer seed or proposal guide. The first campaign's source is retained in
`source-discovery.zip` and `frozen-runtime/`; the second is retained in
`source-affine-discovery.zip`. The baseline source was frozen before implementation.

## Resource comparison

| Construction | Q | Worse-sector D | Worse-sector QD | Two-qubit gates per sector | Classification |
|---|---:|---:|---:|---:|---|
| Preserved baseline | 144 | 76 | 10,944 | 2,592 | Previously autonomous, exact six in both sectors |
| New shallow pair | 144 | 64 | 9,216 | 2,592 | Autonomous proposal, resource-selected follow-up; exact six in both sectors |
| New lower-qubit pair | 120 | 124 | 14,880 | 2,592 | Autonomous, paired target-six certificates |
| Other new pair | 132 | 148 | 19,536 | 2,592 | Autonomous, dominated aggregate tuple retained |
| Adapted published schedule | 144 | 64 | 9,216 | 2,592 | Reference only, paired target-six certificates |

The 120-qubit identities are X
`e55b9baf8ea80cdbec22b98fc6184b050aed037ea7e81b92b5e2dc0952a4c6e8`
and Z `d1935e454288a7de2ba1b21d849e091ae6780a2c505b1667f95d4093c619779f`.
The 132-qubit identities are X
`06a8d93b902a35aceaefddd29805c9adaaeb4d633397551237e0edaf76b6369f`
and Z `d982bd0bf61e3844542961938481e97cc78e21311af9e571d99c50594da6ad70`.
Exact per-sector resources and ancestry are retained in the population databases.

The shallow pair is X
`5086d9e6ee32d0620a84b351f504ccb6e0276dc4ec4d31592eab065f2494628d`
and Z `069823828f774acebad8b5aabcff36022887d68501f47d87a0f7908a4e8bd4cd`.
Its original proposal is `4163b19152040247fcfde002d1839578a2ed7f4f9510da1fd6a70025187c28c2`
in seed 73029. `shallow-promotion/protocol.json` froze the complete qualifying
candidate list before certification. Fourteen sector proofs yielded five positives,
four negatives, and five UNKNOWN outcomes; precisely one complete pair passed.
All five positives and all four negatives were freshly checked in
`followup-delivery/`. Its task-complete public exports are in that directory's
`exports/` subdirectory. Neither the published schedule nor its order was used
in selecting or generating these candidates.

An earlier autonomous shallow pair has Q=144 and D=64/62. Re-evaluation with the
affine proof certifies its Z sector at lower bound six, but its X sector remains
UNKNOWN at lower bound four (`affine-validation/summary.json`). It must not enter
the paired certified frontier. This earlier unresolved pair is different from
the newly certified shallow pair above.

The adapted published reference uses the separately audited code equivalence and
schedule reconstruction, with the same FTQEC operation-duration and boundary
conventions (`reference-affine/protocol.json`). Its X/Z certificates establish
lower bound six at Q=144, D=64/62, QD=9,216/8,928. This is not a reproduction of the
authors' complete published noise/decoder experiment. The original publication's
CNOT-layer convention must not be compared directly with all-operation depth.

## Certification and acceleration

The automatic portfolio now selects the validated time-collapse method for
eligible repeated-memory inputs based on projected problem size and proof work.
The original automatic portfolio remains available as `auto_legacy`. This is a
practical selector, not evidence that one method is uniformly best.

The independent canonical checker was profiled before replacing allocation-heavy
sets with integer bitsets. On the same 180-column input and exactly 10,354,713
visited proof nodes, the two uninstrumented set-reference trials took 22.921875
and 26.890625 CPU seconds; integer-bitset trials took 14.328125 and 13.65625 seconds.
Every result excluded weights through five. Raw inputs, timing, source identities,
and results are in `checker-comparison.json`. No per-method peak-memory comparison
was measured, and these measurements do not establish better optimizer outcomes.

The affine lifting proof supplies a binary parity vector for each reduced minimum
support. All full preimages in one class have a common parity, while the selected
classes have odd total parity. An independent dot-product checker verifies every
preimage and excludes a zero full syndrome. It does not call the Gaussian producer.
The complete minimized-support list is checked independently before using this
proof. The resulting lower-bound increment is exactly one. Inconclusive affine
systems do not establish a physical witness or invalidate a circuit.

This resolved the shallow Z-sector lifting-memory bottleneck. It did not resolve
the X sector. An adaptive projection probe added detector constraints derived from
the obstructions: its first refinement had 858 mechanisms and reduced minimum
four; the next had 2,136 mechanisms and stopped at the pair-table safety bound.
That experiment remains unresolved (`refinement-probe/`, `refinement.log`). No
weaker fault model or larger unguarded proof table was adopted.

For the subsequently discovered winning pair, both reduced minima are five.
`matched-lifting/protocol.json` compares full independent certificate replay on
those exact circuits, with the same 50-million-operation allowance and 512 MiB
worker ceiling. Only the lifting proof route differs:

| Sector | Lifting checker | Target-six replay | CPU s | Wall s | Sampled peak RSS bytes |
|---|---|---|---:|---:|---:|
| X | Layered reachable sets | UNKNOWN: internal memory-safety bound | 7.375 | 7.593763 | 110,149,632 |
| X | Affine parity proof | Verified | 6.890625 | 7.211190 | 66,678,784 |
| Z | Layered reachable sets | UNKNOWN: internal memory-safety bound | 8.09375 | 8.256529 | 166,539,264 |
| Z | Affine parity proof | Verified | 7.40625 | 7.618577 | 67,575,808 |

The old path is censored, so these numbers are not a completed-proof speedup
ratio. They demonstrate proof completion at lower sampled memory on matched
obligations. The legacy receipt's generic method label still says “layered
lifting” for successful affine verification; the recorded proof's
`affine_lifting` field and independently checked parity vectors specify the actual
route. No unchecked solver response is used.

## Compute and reliability

| Campaign | Worker CPU s | Controller CPU s | Sum of controller-session wall s | Maximum sampled worker RSS bytes |
|---|---:|---:|---:|---:|
| 73011 | 2,507.640625 | 910.6875 | 3,311.4500593 | 539,291,648 |
| 73029 | 3,776.984375 | 971.828125 | 4,728.0784234 | 540,360,704 |

These values come from the per-run `compute.json` files. Runs overlapped, so their
wall times must not be added as total elapsed time. Worker RSS is sampled and can
briefly overshoot the configured ceiling before intervention. These totals cover
the discovery campaigns, not subsequent export audits, reference proofs, tests,
or reliability comparisons. Full campaign-wide accounting remains incomplete.

The first run simulated 20 sector circuits with 640 total BP-OSD shots; the second
simulated 40 with 1,280 shots. These development samples do not establish logical
error-rate superiority. The completed final comparisons use BP-OSD 2.4.1, 128
shots per sector at each of p=0.001 and p=0.003, with matched physical models,
boundaries, and decoder settings. There are 2,048 final-comparison shots across
the baseline, Q120 pair, shallow winner, and adapted reference. Failure means
**any logical observable prediction mismatch in the entire six-round experiment**,
not an error rate per round or per encoded qubit.

| Circuit pair | p | X failures / shots | Z failures / shots |
|---|---:|---:|---:|
| Preserved baseline | 0.001 | 0/128 | 0/128 |
| Q120 alternative | 0.001 | 0/128 | 0/128 |
| Shallow autonomous winner | 0.001 | 0/128 | 0/128 |
| Adapted reference | 0.001 | 0/128 | 0/128 |
| Preserved baseline | 0.003 | 0/128 | 0/128 |
| Q120 alternative | 0.003 | 0/128 | 0/128 |
| Shallow autonomous winner | 0.003 | 1/128 | 0/128 |
| Adapted reference | 0.003 | 1/128 | 0/128 |

The reported 95% intervals are [0, 0.02913696] for 0/128 and
[0.00138043, 0.04292626] for 1/128 (point estimate 0.0078125). They overlap;
**no logical-reliability ranking is established**. Raw outcomes, decoder parameters,
sampling hashes, CPU, wall time and memory are in `ler-comparison/` and
`shallow-ler/`. The frozen protocol text originally called the draws independent.
The `sampling-clarification.json` files correct that wording: the same numerical
seed was used, but neither independence across circuits nor physical-location
coupling was established. Marginal intervals are reported; no paired-sample or
independence-based significance test is applied.

Actual two-worker overlap in the first discovery campaign is recorded with task
identities and distinct process IDs in `multicore-evidence.json`. The second
campaign used one worker. No cloud resources were provisioned.

## Required report answers

1. **New distance-six architectures?** Yes: the two initial paired constructions
   and the shallow follow-up pair; all have fresh independent export/proof checks.
2. **Lowest certified Q?** 120 for a newly discovered pair. A 96-qubit X sector
   was certified alone; its missing certified Z partner prevents paired adoption.
3. **Shallowest new paired circuit?** D=64/62 at Q=144.
4. **Best paired QD?** 9,216/8,928 for that shallow pair. This is a finite observed
   frontier, not a global-optimality result.
5. **Two-qubit gates?** 2,592 per sector for the new adopted pairs.
6. **Improvement over Q144/D76/74?** Separate alternatives improve Q to 120 and
   depth to 64/62. No single new pair simultaneously attains both improvements.
7. **Architecture changes?** Shared syndrome-ancilla pools and code-derived orders;
   exact proposal genomes and histories are preserved in SQLite.
8. **Witness repair benefit?** Not established: both completed campaigns used the
   structured policy. Implemented repair operators are not a comparison result.
9. **Distinct generated circuits?** 194 within each campaign, after 100 proposals.
10. **Simulated?** 20 and 40 sector circuits respectively.
11. **Certified?** Three and seven sector positives initially, plus five follow-up
    positives; the follow-up adds one complete shallow pair.
12. **Invalid?** Twelve and 29 initially, plus four follow-up sector outcomes.
13. **UNKNOWN?** Five and four initially, plus five in the follow-up; unpromoted
    circuits remain unevaluated at the proof tier.
14. **Compute?** Per-run measurements above; whole-delivery accounting incomplete.
15. **Time-collapse throughput?** It completed actual selected proofs; matched
    checker acceleration is measured, but broad old/new portfolio timing is absent.
16. **Better certified optimization outcomes?** Not attributable to the backend:
    promotion count and source differ. The lower-qubit result is real.
17. **Adaptive versus random?** NOT_RUN under matched actual compute.
18. **Independent seeds?** Two seeds completed, but differing configurations prevent
    a controlled reproducibility claim about one policy or one improvement.
19. **Published reference?** Adapted reference is certified and shallower; original
    published reliability protocol has not been reproduced.
20. **BP-OSD LER?** The 2,048-shot final comparison above is complete; uncertainty
    is too broad to rank the architectures reliably.
21. **Other 2BGA codes?** Twelve proposals each were evaluated on supplied [[24,2,4]]
    and [[36,8,4]] inputs, producing 24 sector circuits each. Neither produced a
    certified target-four pair: the first had three negative and one UNKNOWN
    promoted sectors; the second had four negatives. These are negative transfer
    results, not a positive generalization claim. Worker/controller CPU seconds
    were 43.328125/11.34375 and 60.609375/15.1875; elapsed session times were
    62.8300641 and 83.5519447 seconds (`generalization/*/compute.json`).
22. **Unresolved?** Shallow X-sector exclusion through five, proof resumability,
    matched policy comparisons, and broader-code experiments.
23. **Bottlenecks?** Expanded projection mechanism counts, exact pair-table growth,
    lifting state growth in the legacy checker, and available RAM.
24. **Reproducibility?** Source snapshots and complete tasks are retained. Ten
    initial positives, five follow-up positives, and three control positives
    passed fresh export/proof checks. The 41 initial, four follow-up, and seven
    transfer-study negative outcomes replayed. All 175 final tests passed in
    236.27 seconds. A fresh final installation passed public optimize, resume,
    export, and verify-export commands. The source-matched installed CLI also
    replayed the full shallow winner in both sectors (`installed-winner-X.log`,
    `installed-winner-Z.log`, `installed-final-smoke/receipt.json`).
25. **Strongest conclusion?** Code-only proposals yielded both a genuine lower-qubit
    tradeoff and a paired depth/QD improvement matching the adapted reference's
    resources. The original promotion policy missed the shallow winner. Affine
    lifting completed both of its proofs. No LER advantage or matched-compute
    whole-optimizer advantage is established.

## Acceptance gates at this checkpoint

| Gate | Status | Evidence and unresolved requirement |
|---|---|---|
| A Historical preservation | PASS | 448 prior artifact hashes verified again after work; all 175 final tests passed |
| B Baseline reproduction | PASS | Both prior certified exports and six-fault witnesses replayed |
| C Architecture vocabulary | PASS | Actual compiled pooled/order/basis and existing repair alternatives |
| D Ancilla optimization | PASS | Paired Q120 certificates, from Q144 baseline |
| E Repeated depth optimization | PASS | Freshly verified autonomous D64/62 pair, versus preserved D76/74 |
| F Automatic portfolio | PASS | Used in both completed campaigns; legacy option retained |
| G Reduction correctness | PASS | Full inventories independently reconstructed; exact proof checks and oracle regressions |
| H Population search | PARTIAL | Two completed 100-proposal campaigns; 1,000/10,000 scales untested |
| I Multi-seed optimization | PARTIAL | Two seeds with differing configuration; no controlled replication |
| J Old/new comparison | NOT_RUN | No matched actual-compute portfolio experiment |
| K Witness repair comparison | NOT_RUN | Structured campaigns do not test repair-policy advantage |
| L Certified frontier improvement | PASS | Both Q120 alternative and D64/62 pair independently verified |
| M BP-OSD evaluation | PARTIAL | Matched final measurements completed with uncertainty; no adequately resolved LER ranking |
| N Published reference | PARTIAL | Adapted paired certificate completed; full published noise experiment absent |
| O Larger-code generalization | PARTIAL | Negative 24/36-qubit transfer studies completed; larger inputs untested |
| P Acceleration benchmark | PARTIAL | Matched checker CPU/proof work measured; peak-memory comparison absent |
| Q Compute accounting | PARTIAL | Controller and worker campaign costs recorded; total delivery not yet consolidated |
| R Independent proofs | PASS | 18 positive sector/control proofs and 52 negative outcomes freshly checked |
| S Circuit/schedule export | PASS | Positive exports reconstructed; task-complete bundles and source-matched installed checks |
| T Reproducible delivery | PASS | Final suite, clean installed CLI, matching source wheels, manifest and local commits |

The final implementation integrates a generic screened-resource-frontier sweep
into finite optimizer runs. It includes ties and low-qubit alternatives, performs
simulation before proof, checkpoints pending final pairs, and respects cancellation
and explicit experimental compute checkpoints. A new interrupted-sweep regression
passes; applying its selector to the untouched seed-73029 population selects the
winning pair (`integrated-selector-real-population.json`). This is engineering
integration evidence, not a fresh large campaign or a matched-compute advantage.
The source is `e9bcf97c248fa36c850136f68a62df079c6b49a641b5ec471a68ab5e13606489`,
implementation commit `b15745d`. All **175 tests passed in 236.27 seconds** after
these changes. The delivery fix also propagates SQLite format metadata so ordinary
exports include their actual task packets. The original scientific populations
remain unchanged; task-complete delivery copies are in `complete-task-exports/`.

The next scientific step is a controlled matched-compute test of that integrated
promotion policy while retaining the established 120-qubit alternative.
The declared reliability measurements are complete, but larger samples are needed
for precise reliability comparisons. Unknown proofs and failed/resource-censored attempts remain evidence;
none are reclassified as invalid without a replayed harmful fault configuration.
