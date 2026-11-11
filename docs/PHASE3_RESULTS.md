# Paired 2BGA architecture discovery: evidence checkpoint

This report records the completed search campaigns and ongoing delivery work on
2026-11-11. **The research mission remains PARTIAL.** It is not a final claim that
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

Proposals use code-derived interaction orders, ancilla pools, check ordering and
basis choices, and existing flag/cat alternatives. The published reference is not
an optimizer seed or proposal guide. The first campaign's source is retained in
`source-discovery.zip` and `frozen-runtime/`; the second is retained in
`source-affine-discovery.zip`. The baseline source was frozen before implementation.

## Resource comparison

| Construction | Q | Worse-sector D | Worse-sector QD | Two-qubit gates per sector | Classification |
|---|---:|---:|---:|---:|---|
| Preserved baseline | 144 | 76 | 10,944 | 2,592 | Previously autonomous, exact six in both sectors |
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

An earlier autonomous shallow pair has Q=144 and D=64/62. Re-evaluation with the
affine proof certifies its Z sector at lower bound six, but its X sector remains
UNKNOWN at lower bound four (`affine-validation/summary.json`). It must not enter
the paired certified frontier. No new paired autonomous depth improvement over
76/74 has yet been established by these results.

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
error-rate superiority. A prospectively specified comparison of the baseline and
120-qubit pair uses BP-OSD, 128 shots per sector at each of p=0.001 and p=0.003,
with the same physical model and boundaries (`ler-comparison/protocol.json`). It
is still being measured at this checkpoint. Different circuits do not share a
location-by-location coupled noise sample, so no paired-sample inference is used.

## Required report answers

1. **New distance-six architectures?** Yes: the two paired constructions above;
   final export replay is being completed separately.
2. **Lowest certified Q?** 120 for a newly discovered pair. A 96-qubit X sector
   was certified alone; its missing certified Z partner prevents paired adoption.
3. **Shallowest new paired circuit?** Worse-sector D=124; the preserved baseline
   remains shallower. A new D=62 Z sector has no certified X partner.
4. **Best paired QD?** The preserved baseline's worse-sector 10,944 remains better
   than the new paired alternatives. This is a finite observed frontier.
5. **Two-qubit gates?** 2,592 per sector for both new pairs.
6. **Improvement over Q144/D76/74?** Q improved to 120; paired depth did not improve.
7. **Architecture changes?** Shared syndrome-ancilla pools and code-derived orders;
   exact proposal genomes and histories are preserved in SQLite.
8. **Witness repair benefit?** Not established: both completed campaigns used the
   structured policy. Implemented repair operators are not a comparison result.
9. **Distinct generated circuits?** 194 within each campaign, after 100 proposals.
10. **Simulated?** 20 and 40 sector circuits respectively.
11. **Certified?** Three and seven sector positives, one complete pair per campaign.
12. **Invalid?** Twelve and 29 sector outcomes respectively.
13. **UNKNOWN?** Five and four completed proof outcomes respectively; unpromoted
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
20. **BP-OSD LER?** Screening batches are retained; final comparison is in progress.
21. **Other 2BGA codes?** This campaign has not yet completed larger-code validation.
22. **Unresolved?** Shallow X-sector exclusion through five, proof resumability,
    matched policy comparisons, and broader-code experiments.
23. **Bottlenecks?** Expanded projection mechanism counts, exact pair-table growth,
    lifting state growth in the legacy checker, and available RAM.
24. **Reproducibility?** Source snapshots and complete tasks are retained. All ten
    campaign positives passed fresh export reconstruction and proof replay; all
    41 reported harmful-witness outcomes replayed. All 173 tests passed in 350.50
    seconds. A fresh installation passed public optimize, resume, export, and
    verify-export commands (`fresh-audits/*/summary.json`,
    `full-suite-20261111.log`, `installed-smoke/receipt.json`).
25. **Strongest conclusion?** Autonomous ancilla reuse found a genuine lower-qubit
    distance-six tradeoff. No autonomous paired depth or LER advantage is established.

## Acceptance gates at this checkpoint

| Gate | Status | Evidence and unresolved requirement |
|---|---|---|
| A Historical preservation | PASS | 448 prior artifact hashes verified; all 173 current/historical tests passed |
| B Baseline reproduction | PASS | Both prior certified exports and six-fault witnesses replayed |
| C Architecture vocabulary | PASS | Actual compiled pooled/order/basis and existing repair alternatives |
| D Ancilla optimization | PASS | Paired Q120 certificates, from Q144 baseline |
| E Repeated depth optimization | PARTIAL | Shallow generated circuits; no improved certified autonomous pair |
| F Automatic portfolio | PASS | Used in both completed campaigns; legacy option retained |
| G Reduction correctness | PASS | Full inventories independently reconstructed; exact proof checks and oracle regressions |
| H Population search | PARTIAL | Two completed 100-proposal campaigns; 1,000/10,000 scales untested |
| I Multi-seed optimization | PARTIAL | Two seeds with differing configuration; no controlled replication |
| J Old/new comparison | NOT_RUN | No matched actual-compute portfolio experiment |
| K Witness repair comparison | NOT_RUN | Structured campaigns do not test repair-policy advantage |
| L Certified frontier improvement | PASS | Lower-Q pair established and both exported sectors independently verified |
| M BP-OSD evaluation | PARTIAL | Screening done; matched final measurements running |
| N Published reference | PARTIAL | Adapted paired certificate completed; full published noise experiment absent |
| O Larger-code generalization | NOT_RUN | No new broader-code campaign completed |
| P Acceleration benchmark | PARTIAL | Matched checker CPU/proof work measured; peak-memory comparison absent |
| Q Compute accounting | PARTIAL | Controller and worker campaign costs recorded; total delivery not yet consolidated |
| R Independent proofs | PASS | All ten campaign positives and 41 harmful-witness outcomes freshly replayed |
| S Circuit/schedule export | PASS | All ten campaign-positive exports independently reconstructed and checked |
| T Reproducible delivery | PARTIAL | Full suite and clean installed CLI passed; final manifest/report consolidation outstanding |

The next scientific step is a controlled matched-compute comparison that promotes
promising shallow X/Z pairs while retaining the established 120-qubit alternative.
Before that comparison, finish delivery validation and the declared reliability
measurement. Unknown proofs and failed/resource-censored attempts remain evidence;
none are reclassified as invalid without a replayed harmful fault configuration.
