# FTQEC large population scientific report

Report issued 2 November 2026. **Research status: PARTIAL, with a resource-limited experiment.** This is the completed report of evidence available at issuance, not a claim that the full research mission or validation matrix has finished.

## Findings

Three campaigns reached at least 10,000 distinct timed circuits: two surface-code campaigns and one Shor-product campaign. The next Shor campaign stopped at the worker memory admission reserve. Nine planned runs completed, one stopped, and the remaining planned runs have no completion receipt. The matrix contains 42 planned runs.

Large populations are computationally feasible on this machine for the completed inputs. Their scientific superiority is not established. The two large surface runs have mixed resource tradeoffs, and both reach Q=17, D=8, QD=136, with 24 two-qubit gates. A smaller surface run already reached that tuple. Neither larger candidate counts nor lower full-run wall time establish a matched-compute improvement.

The principal blocker is now memory admission, followed by the dependent validation chain. Resume the preserved stopped experiment under unchanged safeguards after sufficient memory is available; complete the frozen matrix and independent checks before making comparative claims. No cloud resources are required by the evidence presented here.

## Scope and reproducibility

Scientific source: `3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab`. Repository commit at reporting: `e3ad4dbf843711a75c7382f21ef4070c1bac5f2b`. Protocol: [protocol.json](../../../campaigns/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/protocol.json). Target extraction distance is 3 for this population matrix. These experiments do not establish new distance-5 or distance-10 results.

Physical resource tuples refer to actual circuits under the declared operation-local fault model and ideal boundary assumptions. They are not physical-memory or hardware-routing guarantees. Simulation is decoder-conditional and does not certify fault tolerance. UNKNOWN, UNSUPPORTED and resource stops remain distinct from replayed INVALID witnesses.

## Table A Population scaling

| Run | Generated | Physical identities | Timed structures | Controller CPU s | Elapsed s | Controller peak MiB | Worker aggregate peak MiB | Status and evidence |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| shor3_hybrid_p10000_n10000_s2001 | 11024 | 8881 | 8831 | 1663.65625 | 48138.39909970001 | 165.39 | 641.28 | RESOURCE_SAFETY_INTERVENTION [experiment_receipt.json](../../../../populations/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/study/shor3_hybrid_p10000_n10000_s2001/experiment_receipt.json) |
| shor3_hybrid_p1000_n10000_s2001 | 12384 | 10146 | 10026 | 2074.65625 | 3971.9878850000096 | 122.10 | 629.10 | REQUESTED_CANDIDATE_GOAL_COMPLETED [experiment_receipt.json](../../../../populations/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/study/shor3_hybrid_p1000_n10000_s2001/experiment_receipt.json) |
| shor3_hybrid_p100_n1000_s2001 | 1264 | 1044 | 1035 | 298.796875 | 503.0631861000147 | 117.73 | 628.73 | REQUESTED_CANDIDATE_GOAL_COMPLETED [experiment_receipt.json](../../../../populations/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/study/shor3_hybrid_p100_n1000_s2001/experiment_receipt.json) |
| shor3_hybrid_p100_n100_s2001 | 164 | 150 | 150 | 37.375 | 62.46420409998973 | 121.21 | 625.86 | REQUESTED_CANDIDATE_GOAL_COMPLETED [experiment_receipt.json](../../../../populations/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/study/shor3_hybrid_p100_n100_s2001/experiment_receipt.json) |
| surface3_hybrid_p10000_n10000_s2001 | 13392 | 10712 | 10001 | 2160.25 | 4312.680324200017 | 137.15 | 629.45 | REQUESTED_CANDIDATE_GOAL_COMPLETED [experiment_receipt.json](../../../../populations/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/study/surface3_hybrid_p10000_n10000_s2001/experiment_receipt.json) |
| surface3_hybrid_p1000_n10000_s2001 | 13768 | 11282 | 10049 | 2723.03125 | 4805.492241700005 | 108.19 | 628.98 | REQUESTED_CANDIDATE_GOAL_COMPLETED [experiment_receipt.json](../../../../populations/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/study/surface3_hybrid_p1000_n10000_s2001/experiment_receipt.json) |
| surface3_hybrid_p1000_n1000_s2002 | 1320 | 1094 | 1024 | 277.3125 | 473.48608400000376 | 126.16 | 628.99 | REQUESTED_CANDIDATE_GOAL_COMPLETED [experiment_receipt.json](../../../../populations/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/study/surface3_hybrid_p1000_n1000_s2002/experiment_receipt.json) |
| surface3_hybrid_p100_n1000_s2001 | 1364 | 1150 | 1036 | 183.140625 | 466.38321490000817 | 78.05 | 628.41 | REQUESTED_CANDIDATE_GOAL_COMPLETED [experiment_receipt.json](../../../../populations/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/study/surface3_hybrid_p100_n1000_s2001/experiment_receipt.json) |
| surface3_hybrid_p100_n1000_s2002 | 1300 | 1107 | 1020 | 296.75 | 504.8291596999916 | 125.54 | 628.12 | REQUESTED_CANDIDATE_GOAL_COMPLETED [experiment_receipt.json](../../../../populations/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/study/surface3_hybrid_p100_n1000_s2002/experiment_receipt.json) |
| surface3_hybrid_p100_n100_s2001 | 164 | 149 | 139 | 20.65625 | 50.60886670000036 | 70.30 | 627.56 | REQUESTED_CANDIDATE_GOAL_COMPLETED [experiment_receipt.json](../../../../populations/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/study/surface3_hybrid_p100_n100_s2001/experiment_receipt.json) |

Elapsed clocks are retained as measured, including interruptions or suspension; the stopped run is not a comparable completed timing. Controller and worker peaks are separate sampled maxima. Do not add nested CPU clocks twice. Independent audits overlapped some campaigns, so wall comparisons are observational.

### Audited evaluation counts and worker costs

| Run | Screened | Simulated candidates | Certification attempts | Positive | Invalid | Worker CPU s | Evidence |
|---|---:|---:|---:|---:|---:|---:|---|
| shor3_hybrid_p100_n1000_s2001 | 1044 | 200 | 200 | 130 | 132 | 1664.156 | [summary.json](../../../audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/subsets/19c69c961ce54849cb90806c270536ceeac78f0669ead2a302c4aadf8ff4bfc6/summary.json) |
| shor3_hybrid_p100_n100_s2001 | 150 | 24 | 24 | 15 | 25 | 206.094 | [summary.json](../../../audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/subsets/1c1062d0c8e200388dcd4bd7296ca73900dd8cf8c5075f1dd48f3edc08b399c1/summary.json) |
| surface3_hybrid_p10000_n10000_s2001 | 10712 | 1680 | 1680 | 1298 | 398 | 16136.016 | [summary.json](../../../audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/subsets/12156b307f28130cf396b3690f4d321e683c3b8005c58cad07c49b96ec208d3f/summary.json) |
| surface3_hybrid_p1000_n10000_s2001 | 11282 | 1760 | 1760 | 1400 | 379 | 16491.141 | [summary.json](../../../audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/subsets/0656e718226475f065606e9692a432c0f7fb7d0ba3b29b975da5fb8ef10d260c/summary.json) |
| surface3_hybrid_p100_n1000_s2001 | 1150 | 216 | 216 | 169 | 48 | 1849.016 | [summary.json](../../../audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/subsets/e7262425da0251dbc4ea9e88d47bf9cf92b821a313ad6e12e7aaa45132af04e5/summary.json) |
| surface3_hybrid_p100_n100_s2001 | 149 | 24 | 24 | 17 | 7 | 215.297 | [summary.json](../../../audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/subsets/a46c02db412d793d3560bb4635d13ae21c97f4a1fa959c61c0a4492c7efeb698/summary.json) |

Counts are per run, not deduplicated across runs. Positive counts reflect bound certificates and their recorded independent checks; fresh export replay is a separate delivery check. Only runs with retained independent audit summaries appear above.

## Table B Search strategy comparison

| Comparison | Status | Conclusion |
|---|---|---|
| Hybrid versus random, witness, multifidelity and costhybrid | NOT_RUN as a completed matched comparison | No superiority claim |

## Table C Evaluation policy comparison

| Policy | Positive retention | False rejection | CPU savings |
|---|---|---|---|
| Direct certification | NOT_RUN | NOT_RUN | NOT_RUN |
| Fixed screening funnel | NOT_RUN | NOT_RUN | NOT_RUN |
| Adaptive allocation | NOT_RUN | NOT_RUN | NOT_RUN |

The isolated pool experiment is downstream of the incomplete campaign matrix. Absence of a recorded rejection is not evidence of perfect recall.

## Table D Cross family certified frontiers

| Run | Audited nondominated Q, D, QD, two-qubit-gate tuples | Evidence |
|---|---|---|
| shor3_hybrid_p100_n1000_s2001 | [(10, 56, 560, 24), (12, 30, 360, 24), (14, 16, 224, 24), (17, 12, 204, 24)] | [summary.json](../../../audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/subsets/19c69c961ce54849cb90806c270536ceeac78f0669ead2a302c4aadf8ff4bfc6/summary.json) |
| shor3_hybrid_p100_n100_s2001 | [(10, 56, 560, 24), (17, 14, 238, 24)] | [summary.json](../../../audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/subsets/1c1062d0c8e200388dcd4bd7296ca73900dd8cf8c5075f1dd48f3edc08b399c1/summary.json) |
| surface3_hybrid_p10000_n10000_s2001 | [(10, 56, 560, 24), (12, 19, 228, 24), (17, 8, 136, 24)] | [summary.json](../../../audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/subsets/12156b307f28130cf396b3690f4d321e683c3b8005c58cad07c49b96ec208d3f/summary.json) |
| surface3_hybrid_p1000_n10000_s2001 | [(10, 48, 480, 24), (12, 21, 252, 24), (13, 14, 182, 24), (15, 12, 180, 24), (17, 8, 136, 24)] | [summary.json](../../../audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/subsets/0656e718226475f065606e9692a432c0f7fb7d0ba3b29b975da5fb8ef10d260c/summary.json) |
| surface3_hybrid_p100_n1000_s2001 | [(10, 48, 480, 24), (15, 12, 180, 24), (17, 8, 136, 24)] | [summary.json](../../../audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/subsets/e7262425da0251dbc4ea9e88d47bf9cf92b821a313ad6e12e7aaa45132af04e5/summary.json) |
| surface3_hybrid_p100_n100_s2001 | [(13, 240, 3120, 112), (15, 12, 180, 24), (17, 8, 136, 24)] | [summary.json](../../../audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/subsets/a46c02db412d793d3560bb4635d13ae21c97f4a1fa959c61c0a4492c7efeb698/summary.json) |

HGP population results: NOT_RUN in this completed evidence set. Existing historical HGP, Shor distance-5 and surface distance-10 evidence remains separate; this report does not substitute a historical result for a new population discovery.

## Table E Parallel scaling

| Scope | Status | Interpretation |
|---|---|---|
| Population campaigns | Parallel worker execution recorded | Requested worker count is not sustained utilization |
| Final extended matched scaling validation | NOT_RUN | Queued behind the unfinished matrix; no final scaling claim |

## Table F Acceptance gates

| Gate | Requirement | Status | Evidence or unresolved requirement |
|---|---|---|---|
| A | Historical preservation | PARTIAL | Full matrix and final validation remain incomplete. |
| B | Disk population storage | PASS | Completed large campaigns and disk-backed retained populations, Table A; engineering demonstration, not superiority. |
| C | Genuine 10000 candidate optimization | PASS | Completed large campaigns and disk-backed retained populations, Table A; engineering demonstration, not superiority. |
| D | Effective diversity | PARTIAL | Timed and ancilla-relabel signatures audited; no quotient by all code automorphisms. |
| E | Parallel cheap evaluation | PARTIAL | Full matrix and final validation remain incomplete. |
| F | Adaptive Monte Carlo | PARTIAL | Full matrix and final validation remain incomplete. |
| G | Cost-aware scheduling | PARTIAL | Full matrix and final validation remain incomplete. |
| H | Verified early rejection | PARTIAL | Independent witness replay in audited subsets; full-matrix audit outstanding. |
| I | Positive retention | NOT_RUN | Required completed comparative evidence is unavailable, Tables B and C. |
| J | Rigorous finalists | PARTIAL | Full matrix and final validation remain incomplete. |
| K | Certified Pareto correctness | PARTIAL | Full matrix and final validation remain incomplete. |
| L | Matched capacity comparison | NOT_RUN | Required completed comparative evidence is unavailable, Tables B and C. |
| M | Matched strategy comparison | NOT_RUN | Required completed comparative evidence is unavailable, Tables B and C. |
| N | Isolated policy comparison | NOT_RUN | Required completed comparative evidence is unavailable, Tables B and C. |
| O | Cross-family evaluation | PARTIAL | Full matrix and final validation remain incomplete. |
| P | Local multicore scaling | PARTIAL | Full matrix and final validation remain incomplete. |
| Q | Cloud escalation justified only by need | PASS | No cloud provisioning; completed local runs demonstrate local feasibility for those inputs. |
| R | Circuit exports | PARTIAL | First completed campaign has verified exports; full adopted frontier export validation outstanding. |
| S | Reproducibility | PARTIAL | Full matrix and final validation remain incomplete. |
| T | Packaging | PARTIAL | Full matrix and final validation remain incomplete. |

## Answers to all required report questions

### 1. How many distinct candidates were generated, compiled, screened, simulated, and certified?

See Table A and the linked per-run audits for measured counts and costs. Totals across the unfinished matrix are not available; unaudited or unattempted candidates are not counted as certified or invalid.

### 2. Was a genuine 10,000-candidate optimization campaign completed?

Yes. Three run receipts meet the 10,000 timed-structure goal (Table A); the fourth large run stopped at 8,831 structures and does not meet it.

### 3. How was effective architecture diversity measured?

Physical identity, timed-structure hashes, and an independent ancilla-relabel invariant distinguish exact duplication from structural diversity. Near buckets are descriptors, not proven scientific equivalence classes. Data-code automorphisms are not fully quotiented.

### 4. Did the optimizer preserve multiple extraction families?

Multiple extraction families are retained in the disk populations. Surface and Shor runs use the same generic pipeline. A complete cross-family generalization comparison is still incomplete.

### 5. How much compute was spent at each evaluation tier?

See Table A and the linked per-run audits for measured counts and costs. Totals across the unfinished matrix are not available; unaudited or unattempted candidates are not counted as certified or invalid.

### 6. How much compute did early rejection save compared with evaluating every candidate through the same expensive pipeline?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 7. Were any independently certified positive circuits falsely rejected?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 8. Were any valuable certified Pareto points lost during screening?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 9. Did adaptive evaluation improve the quality of discovered circuits per CPU-hour?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 10. How did the best certified frontier change over successive generations?

Per-run frontier histories and audited resource alternatives are retained in the Table A/D artifacts. The large surface runs share the best-QD tuple already found in a small run; final temporal and matched-compute interpretation remains incomplete.

### 11. How many candidates were exact duplicates, near-duplicates, or meaningfully different architectures?

Physical identity, timed-structure hashes, and an independent ancilla-relabel invariant distinguish exact duplication from structural diversity. Near buckets are descriptors, not proven scientific equivalence classes. Data-code automorphisms are not fully quotiented.

### 12. Did increasing population size improve the best certified Q, D, QD, two-qubit gate count, or decoder-conditional LER?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 13. How much of any improvement came from population diversity rather than simply performing more evaluations?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 14. Did the optimizer continue improving after discovering its first certified circuit?

Per-run frontier histories and audited resource alternatives are retained in the Table A/D artifacts. The large surface runs share the best-QD tuple already found in a small run; final temporal and matched-compute interpretation remains incomplete.

### 15. How many candidates received actual physical fault screening?

See Table A and the linked per-run audits for measured counts and costs. Totals across the unfinished matrix are not available; unaudited or unattempted candidates are not counted as certified or invalid.

### 16. How many candidates were rejected using independently replayed harmful faults?

See Table A and the linked per-run audits for measured counts and costs. Totals across the unfinished matrix are not available; unaudited or unattempted candidates are not counted as certified or invalid.

### 17. What was the distribution of harmful fault weights?

Witness weights and independent replay results are retained in each linked audit under witness_replays. A whole-matrix weight distribution has not been completed.

### 18. How many Monte Carlo simulation batches and shots were completed?

See Table A and the linked per-run audits for measured counts and costs. Totals across the unfinished matrix are not available; unaudited or unattempted candidates are not counted as certified or invalid.

### 19. Did adaptive simulation allocate more shots to promising or uncertain candidates?

The pipeline uses staged simulation and repeated-look uncertainty handling; statistical uncertainty is not a physical invalidity witness. Differential allocation benefit and population-wide statistical ranking are not established by this report.

### 20. Were statistical stopping rules valid under repeated inspection?

The pipeline uses staged simulation and repeated-look uncertainty handling; statistical uncertainty is not a physical invalidity witness. Differential allocation benefit and population-wide statistical ranking are not established by this report.

### 21. How did decoder choice affect candidate rankings?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 22. Were statistically uncertain candidates preserved rather than incorrectly hard-rejected?

The pipeline uses staged simulation and repeated-look uncertainty handling; statistical uncertainty is not a physical invalidity witness. Differential allocation benefit and population-wide statistical ranking are not established by this report.

### 23. Did early screening reduce total computation after including screening overhead?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 24. Which evaluation tiers dominated total CPU and wall-clock time?

See Table A and the linked per-run audits for measured counts and costs. Totals across the unfinished matrix are not available; unaudited or unattempted candidates are not counted as certified or invalid.

### 25. How many distinct candidates received rigorous certification attempts?

See Table A and the linked per-run audits for measured counts and costs. Totals across the unfinished matrix are not available; unaudited or unattempted candidates are not counted as certified or invalid.

### 26. How many independently verified positive certificates were produced?

See Table A and the linked per-run audits for measured counts and costs. Totals across the unfinished matrix are not available; unaudited or unattempted candidates are not counted as certified or invalid.

### 27. How many candidates were proven INVALID?

See Table A and the linked per-run audits for measured counts and costs. Totals across the unfinished matrix are not available; unaudited or unattempted candidates are not counted as certified or invalid.

### 28. How many remained UNKNOWN or UNSUPPORTED?

See Table A and the linked per-run audits for measured counts and costs. Totals across the unfinished matrix are not available; unaudited or unattempted candidates are not counted as certified or invalid.

### 29. Which certification methods were selected, and why?

Screening precedes selected rigorous certification. Method selection and per-task outcomes are retained in raw packets. Full portfolio profiling and the effect of deferred promising candidates remain unresolved.

### 30. Did the optimizer avoid expensive certification of already-invalid candidates?

Screening precedes selected rigorous certification. Method selection and per-task outcomes are retained in raw packets. Full portfolio profiling and the effect of deferred promising candidates remain unresolved.

### 31. Did any certification bottleneck prevent promising candidates from reaching the certified frontier?

Screening precedes selected rigorous certification. Method selection and per-task outcomes are retained in raw packets. Full portfolio profiling and the effect of deferred promising candidates remain unresolved.

### 32. Were all adopted certificates independently verified under the exact declared fault model?

The first closed surface campaign has independently verified export bundles, including reconstruction and resource checks. The full-matrix adopted-finalist verification is still pending; do not extend the subset result to every retained circuit.

### 33. Which independent CSS construction families were evaluated?

Surface and Shor-product campaigns have completed runs. Hamming HGP is planned but has no completed campaign in this report. Therefore all-family success and HGP frontier improvement are not demonstrated.

### 34. Did each family produce at least one autonomous certified circuit?

Surface and Shor-product campaigns have completed runs. Hamming HGP is planned but has no completed campaign in this report. Therefore all-family success and HGP frontier improvement are not demonstrated.

### 35. How did the best certified resource frontiers differ between families?

Per-run frontier histories and audited resource alternatives are retained in the Table A/D artifacts. The large surface runs share the best-QD tuple already found in a small run; final temporal and matched-compute interpretation remains incomplete.

### 36. Did the same generic optimization operators work across multiple families?

Multiple extraction families are retained in the disk populations. Surface and Shor runs use the same generic pipeline. A complete cross-family generalization comparison is still incomplete.

### 37. Did any architecture family consistently outperform the others?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 38. Were reference circuits excluded from initialization and candidate guidance?

The frozen protocol supplies code inputs and separates candidate-generation experiments from a later fixed-pool policy study. Full provenance validation remains pending; references must not be treated as discovery seeds.

### 39. Did the optimizer improve the previously established non-surface [[25,1,5]] resource frontier?

Historical results are preserved separately. No new distance-5 optimization improvement or distance-10 revalidation is established by this target-3 matrix; the final preservation/control checks remain pending.

### 40. Did the optimizer preserve the independently certified distance-10 surface-code frontier?

Historical results are preserved separately. No new distance-5 optimization improvement or distance-10 revalidation is established by this target-3 matrix; the final preservation/control checks remain pending.

### 41. Did the optimizer improve the HGP [[58,16,3]] frontier?

Surface and Shor-product campaigns have completed runs. Hamming HGP is planned but has no completed campaign in this report. Therefore all-family success and HGP frontier improvement are not demonstrated.

### 42. Which code families remained difficult, unsupported, or unresolved?

Surface and Shor-product campaigns have completed runs. Hamming HGP is planned but has no completed campaign in this report. Therefore all-family success and HGP frontier improvement are not demonstrated.

### 43. Did large-population optimization outperform smaller-population optimization at matched actual CPU?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 44. Did it outperform at matched wall-clock time?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 45. Did the hybrid strategy outperform random search?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 46. Did witness-guided search provide measurable benefit?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 47. Did cost-aware evaluation outperform a fixed screening funnel?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 48. Did either screening strategy outperform direct certification?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 49. Were the comparisons repeated across independent seeds?

Smaller surface studies include seeds 2001 and 2002. The completed 10,000-structure studies use seed 2001; they do not support broad multi-seed superiority claims.

### 50. Were the results statistically distinguishable, or were the experiments too small to support superiority claims?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 51. Were candidate-generation effects separated from evaluation-allocation effects?

The frozen protocol supplies code inputs and separates candidate-generation experiments from a later fixed-pool policy study. Full provenance validation remains pending; references must not be treated as discovery seeds.

### 52. Did the optimizer preserve independently certified positives under every evaluation policy?

Not established. The required completed matched-compute or fixed-pool comparison is unavailable. Table B/C records the missing evidence; no advantage or perfect positive-retention claim is made.

### 53. How many physical and logical CPU cores were available?

The protocol records 12 physical and 16 logical cores and requests eight workers per campaign. Requested workers are not measured utilization. The extended matched parallel-scaling validation remains pending; no whole-optimizer scaling factor is inferred.

### 54. How many workers were actually active simultaneously?

The protocol records 12 physical and 16 logical cores and requests eight workers per campaign. Requested workers are not measured utilization. The extended matched parallel-scaling validation remains pending; no whole-optimizer scaling factor is inferred.

### 55. What was the measured worker utilization?

The protocol records 12 physical and 16 logical cores and requests eight workers per campaign. Requested workers are not measured utilization. The extended matched parallel-scaling validation remains pending; no whole-optimizer scaling factor is inferred.

### 56. What were the coordinator and worker CPU costs?

See Table A and the linked per-run audits for measured counts and costs. Totals across the unfinished matrix are not available; unaudited or unattempted candidates are not counted as certified or invalid.

### 57. What were the peak individual-worker and aggregate memory requirements?

See Table A and the linked per-run audits for measured counts and costs. Totals across the unfinished matrix are not available; unaudited or unattempted candidates are not counted as certified or invalid.

### 58. How did throughput change with worker count?

The protocol records 12 physical and 16 logical cores and requests eight workers per campaign. Requested workers are not measured utilization. The extended matched parallel-scaling validation remains pending; no whole-optimizer scaling factor is inferred.

### 59. Did serial-versus-parallel comparisons demonstrate real wall-clock speedup?

The protocol records 12 physical and 16 logical cores and requests eight workers per campaign. Requested workers are not measured utilization. The extended matched parallel-scaling validation remains pending; no whole-optimizer scaling factor is inferred.

### 60. Did task serialization, checkpointing, or queue management become a bottleneck?

Startup, task body and persistence costs are separately retained. No unmeasured subsystem is assigned the residual CPU cost; a bottleneck intervention requires profiling rather than a guessed decoder-caching benefit.

### 61. Did local hardware complete the required 10,000-candidate campaign?

Yes. Three run receipts meet the 10,000 timed-structure goal (Table A); the fourth large run stopped at 8,831 structures and does not meet it.

### 62. Was cloud computing necessary or justified by actual measurements?

Cloud execution was not used. A local worker memory admission stop is recorded, but this alone does not establish that paid cloud execution is necessary.

### 63. Were all historical scientific artifacts preserved?

Historical results are preserved separately. No new distance-5 optimization improvement or distance-10 revalidation is established by this target-3 matrix; the final preservation/control checks remain pending.

### 64. Did the complete existing and new test suites pass?

The preserved frozen-source full-suite receipt passed before campaign execution. Delivery fixes were tested separately and are not applied to the frozen study source; final delivery-source testing is outstanding.

### 65. Were exported circuits and schedules independently reconstructed?

The first closed surface campaign has independently verified export bundles, including reconstruction and resource checks. The full-matrix adopted-finalist verification is still pending; do not extend the subset result to every retained circuit.

### 66. Were resource metrics recomputed from actual exported circuits?

The first closed surface campaign has independently verified export bundles, including reconstruction and resource checks. The full-matrix adopted-finalist verification is still pending; do not extend the subset result to every retained circuit.

### 67. Were all certification identities and fault-model bindings verified?

The first closed surface campaign has independently verified export bundles, including reconstruction and resource checks. The full-matrix adopted-finalist verification is still pending; do not extend the subset result to every retained circuit.

### 68. Were the experiments reproducible from the retained source, seeds, and configuration?

Source, seeds, protocol, checkpoints and raw results are retained. Reproducibility infrastructure exists; the complete final replay and release-manifest audit has not finished.

### 69. Which acceptance gates remain incomplete?

Table F lists every gate. PASS for demonstrated storage/scale and the no-cloud policy is not overall research completion.

### 70. What is the single most justified next scientific development step?

Recover the memory-stopped campaign from its durable checkpoint without lowering reserves, then complete the frozen matched comparisons and independent validation. This is more justified than expanding the architecture search or claiming superiority from partial data.

## Exact blocker and delivery limitations

Checkpoint: [checkpoint.json](../../../../populations/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/study/shor3_hybrid_p10000_n10000_s2001/checkpoint.json). Status `RESOURCE_SAFETY_INTERVENTION`; reason `Worker admission reserve`. This is a computational censoring outcome, not physical invalidity. The saved elapsed wall time must not be interpreted as continuous active computation.

validation_pipeline: `WAITING_FOR_EXPERIMENTS`; [state.json](../../../validation_pipeline/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/state.json).
supplemental_validation: `WAITING_FOR_PRIMARY_VALIDATION`; [state.json](../../../supplemental_validation/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/state.json).
policy_evidence_audit: `WAITING_FOR_SUPPLEMENTAL_VALIDATION`; [state.json](../../../policy_evidence_audit/3d0fac278b3f57e24867a6358cc800e7e88c1b476d322aaf228369bce86237ab/state.json).

The waiting files describe persisted state, not proof that a process is currently alive. No running-process claim is made here. The report does not stop, restart or modify any experiment. Recovery fixes remain staged separately to preserve frozen source identity.

## Evidence manifest

The accompanying report_evidence_manifest.json binds every linked artifact by SHA-256 as read for this report. It is a report evidence manifest, not the still-outstanding whole-repository release manifest. Historical and incomplete outcomes remain in their original locations.
