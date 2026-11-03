# General fault-tolerant extraction: scientific results

Scientific source `d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306`; FTQEC 0.1.0.

The defining target-five milestone is demonstrated. A code-only random-population verified-cat discovery on independently validated [[25,1,5]] is graph-ineligible for the implemented portfolio and independently certified at exact extraction distance five. The existing full-signature MITM engine supplies this proof. The new separator backend does not receive credit for it.

The adopted alternatives include Q=36,D=329,QD=11,844 and Q=105,D=46,QD=4,830, both with 248 two-qubit gates. The lower-qubit option remains. Five other allocation/scheduling neighbors were invalidated: noiseless equivalence did not preserve fault tolerance.

Claims use ideal initial/final syndrome boundaries and explicit operation-local faults. They do not certify arbitrary-input physical memory, implicit idle noise, hardware routing, decoder-independent performance or global optimality.

[Complete machine-readable results](../results/general_extraction/report/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/summary.json); [independently verified bundles](../results/exports/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/finalists/index.json); [unresolved obligations](../results/general_extraction/audit/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/unknown_obligations.json).

## Separate scientific objectives

| Objective | Status | Interpretation |
|---|---|---|
| Architecture repair | PARTIAL | Real compositions and mechanism replays; no certified invalid-to-valid six-arm repair. |
| General certification | PASS | Non-surface graph-ineligible target-five positive via MITM. |
| Computational efficiency | PASS, narrow | Lower separator CPU/memory on the same target-three graph-ineligible control across three rotations. |
| Autonomous optimization | PASS | Code-only discovery and certified QD improvement without reference seeds. |
| Generalization | PASS, scoped | Independent HGP target-three positives and certified resource improvement; no second-family distance-five claim. |
| Reproducibility | PASS | Complete circuits, schedules, proofs and public reconstruction. |

## Table A — Architecture repair and resource outcomes

| Case | Architecture | Parent | Q | D | QD | 2Q gates | Outcome | CPU/wall s | Evidence |
|---|---|---|---:|---:|---:|---:|---|---|---|
| Certified 3476e5062b45 | verified_cat | code-only | 36 | 329 | 11844 | 248 | Independently verified target 5 | replay 11.578/14.155 | [bundle](../results/exports/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/finalists/bundles/5_3476e5062b459ff7feaef86f341e08d87951cd2ea661c17af034e06457ebb4f1) |
| Certified 8f16cbac22aa | verified_cat | code-only | 289 | 86 | 24854 | 360 | Independently verified target 5 | replay 39.641/50.049 | [bundle](../results/exports/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/finalists/bundles/5_8f16cbac22aa69e67ce8188bf454c2fa72110fcaacb1dad53d9afb7b66123630) |
| Certified a415957cdb37 | verified_cat | 8f16cbac22aa69e67ce8188bf454c2fa72110fcaacb1dad53d9afb7b66123630 | 129 | 86 | 11094 | 360 | Independently verified target 5 | replay 38.422/49.304 | [bundle](../results/exports/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/finalists/bundles/5_a415957cdb374c038c7eb01df1819a2f99f760b38d76de8ff6b0722df58f5559) |
| Certified b1aad234226a | verified_cat | db9bf9ac0ca54b3b412185936acbd03c8525cbe04612a030393f6c1df4b749bc | 105 | 46 | 4830 | 248 | Independently verified target 5 | replay 20.797/24.677 | [bundle](../results/exports/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/finalists/bundles/5_b1aad234226ae2e9045a86cdcd585d8c7945e5b069ce65d94cef93310594f613) |
| Certified db9bf9ac0ca5 | verified_cat | code-only | 36 | 329 | 11844 | 248 | Independently verified target 5 | replay 10.328/12.574 | [bundle](../results/exports/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/finalists/bundles/5_db9bf9ac0ca54b3b412185936acbd03c8525cbe04612a030393f6c1df4b749bc) |
| Original negative parent | flagged | historical control | 105 | 101 | 10605 | 384 | INVALID; upper 4 independently replayed | historical 142.234/193.745 | [parent packet](../results/repair_trajectories/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor5_six_arm/parent_input.json) |
| Invalid-parent repair seed 0 | flagged | 5cf57d016850adf7a48c467628a79f9036c769fa4572474083d35a9f78af0e25 | 105 | 103 | 10815 | 384 | INVALID; lower 3, upper 4 | evaluation 111.344/149.026 | [lineage](../results/repair_trajectories/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor5_six_arm/rows.json) |
| Invalid-parent repair seed 1 | flagged | 5cf57d016850adf7a48c467628a79f9036c769fa4572474083d35a9f78af0e25 | 105 | 100 | 10500 | 384 | UNKNOWN; lower 3, upper none | evaluation 124.828/170.238 | [lineage](../results/repair_trajectories/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor5_six_arm/rows.json) |
| Invalid-parent repair seed 2 | flagged | 5cf57d016850adf7a48c467628a79f9036c769fa4572474083d35a9f78af0e25 | 105 | 101 | 10605 | 384 | UNKNOWN; lower 3, upper none | evaluation 125.406/161.284 | [lineage](../results/repair_trajectories/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor5_six_arm/rows.json) |
| Invalid-parent repair seed 3 | verified_cat | 5cf57d016850adf7a48c467628a79f9036c769fa4572474083d35a9f78af0e25 | 129 | 293 | 37797 | 1168 | UNKNOWN; lower 3, upper none | evaluation 155.312/190.694 | [lineage](../results/repair_trajectories/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor5_six_arm/rows.json) |
| Invalid-parent repair seed 4 | verified_cat | 5cf57d016850adf7a48c467628a79f9036c769fa4572474083d35a9f78af0e25 | 129 | 293 | 37797 | 1168 | UNKNOWN; lower 3, upper none | evaluation 150.078/184.553 | [lineage](../results/repair_trajectories/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor5_six_arm/rows.json) |
| Invalid-parent repair seed 5 | flagged | 5cf57d016850adf7a48c467628a79f9036c769fa4572474083d35a9f78af0e25 | 105 | 101 | 10605 | 384 | UNKNOWN; lower 3, upper none | evaluation 125.219/165.640 | [lineage](../results/repair_trajectories/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor5_six_arm/rows.json) |
| Allocation slots 1 | verified_cat | db9bf9ac0ca54b3b412185936acbd03c8525cbe04612a030393f6c1df4b749bc | 36 | 293 | 10548 | 248 | INVALID; lower 1, upper 4 | evaluation 22.234/27.626 | [raw](../results/pareto/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/allocation_study/rows.json) |
| Allocation slots 2 | verified_cat | db9bf9ac0ca54b3b412185936acbd03c8525cbe04612a030393f6c1df4b749bc | 47 | 147 | 6909 | 248 | INVALID; lower 1, upper 4 | evaluation 27.438/33.457 | [raw](../results/pareto/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/allocation_study/rows.json) |
| Allocation slots 4 | verified_cat | db9bf9ac0ca54b3b412185936acbd03c8525cbe04612a030393f6c1df4b749bc | 69 | 74 | 5106 | 248 | INVALID; lower 1, upper 4 | evaluation 31.969/37.583 | [raw](../results/pareto/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/allocation_study/rows.json) |
| Allocation slots 8 | verified_cat | db9bf9ac0ca54b3b412185936acbd03c8525cbe04612a030393f6c1df4b749bc | 81 | 53 | 4293 | 248 | INVALID; lower 1, upper 4 | evaluation 29.516/34.690 | [raw](../results/pareto/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/allocation_study/rows.json) |
| Allocation slots 16 | verified_cat | db9bf9ac0ca54b3b412185936acbd03c8525cbe04612a030393f6c1df4b749bc | 105 | 46 | 4830 | 248 | CERTIFIED; lower 5, upper 5 | evaluation 64.250/72.961 | [raw](../results/pareto/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/allocation_study/rows.json) |
| Allocation slots 24 | verified_cat | db9bf9ac0ca54b3b412185936acbd03c8525cbe04612a030393f6c1df4b749bc | 129 | 39 | 5031 | 248 | INVALID; lower 1, upper 4 | evaluation 26.906/32.172 | [raw](../results/pareto/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/allocation_study/rows.json) |

All Table A cases use [[25,1,5]] at requested target five. CPU/wall labels distinguish separate replay from summed construction/evaluation stages. Exact parent identities, genomes, operator sequences, physical circuits, lower bounds, witness weights and CPU/wall records are in each lineage packet. All dominated positives remain exported. Compaction-only outcomes are separate from schedule changes.

## Table B — Matched exact-certification methods

| Input/method | Family | Graph eligible | Locations | Alternatives | Detectors | Target | Outcome / accepted proof | Lower | Upper | Width | States | CPU s | Wall s | Peak MiB | Independent |
|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| [d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor4_positive_decomposition](../results/general_extraction/proof_development/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor4_positive_decomposition.json) | shor_product4 | False | 480 | 3984 | 111 | 4 | UNKNOWN / pairs | 3 | None | 22 | 19400 | 2.266 | 2.572 | 43.04 | True |
| [d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor4_positive_decomposition_legacy](../results/general_extraction/proof_development/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor4_positive_decomposition_legacy.json) | shor_product4 | False | 480 | 3984 | 111 | 4 | UNKNOWN / pairs | 3 | None | 39 | 22548 | 3.297 | 3.603 | 46.27 | True |
| [d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor5_unresolved_decomposition](../results/general_extraction/proof_development/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor5_unresolved_decomposition.json) | shor_product_5_5 | False | 800 | 6688 | 184 | 5 | UNKNOWN / pairs | 3 | None | 22 | 63464 | 6.062 | 6.360 | 70.62 | True |
| [d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor5_unresolved_decomposition_legacy](../results/general_extraction/proof_development/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor5_unresolved_decomposition_legacy.json) | shor_product_5_5 | False | 800 | 6688 | 184 | 5 | UNKNOWN / pairs | 3 | None | 29 | 41276 | 11.969 | 12.364 | 61.02 | True |
| [small_matched/0_decomposition](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_matched/0_decomposition.json) | shor_product_3_3 | True | 240 | 1968 | 56 | 3 | INVALID / pairs | 1 | 2 | None | None | 0.453 | 0.661 | 31.56 | True |
| [small_matched/0_decomposition_legacy](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_matched/0_decomposition_legacy.json) | shor_product_3_3 | True | 240 | 1968 | 56 | 3 | INVALID / pairs | 1 | 2 | None | None | 0.438 | 0.605 | 31.68 | True |
| [small_matched/0_decomposition_span](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_matched/0_decomposition_span.json) | shor_product_3_3 | True | 240 | 1968 | 56 | 3 | INVALID / pairs | 1 | 2 | None | None | 0.531 | 0.752 | 31.46 | True |
| [small_matched/1_decomposition](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_matched/1_decomposition.json) | shor_product_3_3 | True | 240 | 1968 | 56 | 3 | INVALID / pairs | 1 | 2 | None | None | 0.516 | 0.775 | 31.75 | True |
| [small_matched/1_decomposition_legacy](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_matched/1_decomposition_legacy.json) | shor_product_3_3 | True | 240 | 1968 | 56 | 3 | INVALID / pairs | 1 | 2 | None | None | 0.625 | 0.834 | 31.63 | True |
| [small_matched/1_decomposition_span](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_matched/1_decomposition_span.json) | shor_product_3_3 | True | 240 | 1968 | 56 | 3 | INVALID / pairs | 1 | 2 | None | None | 0.453 | 0.687 | 31.68 | True |
| [small_matched/2_decomposition](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_matched/2_decomposition.json) | shor_product_3_3 | True | 240 | 1968 | 56 | 3 | INVALID / pairs | 1 | 2 | None | None | 0.594 | 0.813 | 31.82 | True |
| [small_matched/2_decomposition_legacy](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_matched/2_decomposition_legacy.json) | shor_product_3_3 | True | 240 | 1968 | 56 | 3 | INVALID / pairs | 1 | 2 | None | None | 0.500 | 0.821 | 31.73 | True |
| [small_matched/2_decomposition_span](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_matched/2_decomposition_span.json) | shor_product_3_3 | True | 240 | 1968 | 56 | 3 | INVALID / pairs | 1 | 2 | None | None | 0.484 | 0.724 | 31.73 | True |
| [small_positive_matched/0_decomposition](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_positive_matched/0_decomposition.json) | shor_product4 | False | 480 | 3984 | 111 | 3 | CERTIFIED / closed-physical-domain-separator-1 | 3 | 4 | 31 | 3389 | 2.891 | 3.001 | 37.88 | True |
| [small_positive_matched/0_decomposition_legacy](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_positive_matched/0_decomposition_legacy.json) | shor_product4 | False | 480 | 3984 | 111 | 3 | CERTIFIED / pairs | 3 | 4 | 99 | 29715 | 19.859 | 20.366 | 52.01 | True |
| [small_positive_matched/0_decomposition_span](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_positive_matched/0_decomposition_span.json) | shor_product4 | False | 480 | 3984 | 111 | 3 | CERTIFIED / pairs | 3 | 4 | 99 | 21887 | 20.156 | 20.687 | 48.87 | True |
| [small_positive_matched/1_decomposition](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_positive_matched/1_decomposition.json) | shor_product4 | False | 480 | 3984 | 111 | 3 | CERTIFIED / closed-physical-domain-separator-1 | 3 | 4 | 31 | 3389 | 4.062 | 4.297 | 37.68 | True |
| [small_positive_matched/1_decomposition_legacy](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_positive_matched/1_decomposition_legacy.json) | shor_product4 | False | 480 | 3984 | 111 | 3 | CERTIFIED / pairs | 3 | 4 | 99 | 29715 | 14.547 | 14.875 | 51.19 | True |
| [small_positive_matched/1_decomposition_span](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_positive_matched/1_decomposition_span.json) | shor_product4 | False | 480 | 3984 | 111 | 3 | CERTIFIED / pairs | 3 | 4 | 99 | 21887 | 22.250 | 22.659 | 49.25 | True |
| [small_positive_matched/2_decomposition](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_positive_matched/2_decomposition.json) | shor_product4 | False | 480 | 3984 | 111 | 3 | CERTIFIED / closed-physical-domain-separator-1 | 3 | 4 | 31 | 3389 | 3.172 | 3.310 | 37.84 | True |
| [small_positive_matched/2_decomposition_legacy](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_positive_matched/2_decomposition_legacy.json) | shor_product4 | False | 480 | 3984 | 111 | 3 | CERTIFIED / pairs | 3 | 4 | 99 | 29715 | 13.484 | 13.727 | 51.85 | True |
| [small_positive_matched/2_decomposition_span](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_positive_matched/2_decomposition_span.json) | shor_product4 | False | 480 | 3984 | 111 | 3 | CERTIFIED / pairs | 3 | 4 | 99 | 21887 | 20.172 | 20.457 | 48.65 | True |

Matched target-three median CPU: legacy 14.547s; span-only 20.172s; reduced separator 3.172s. Legacy and span-only exhausted separator work and retained valid pair certificates. The reduced backend completed its separator proof. All establish the same requested lower bound. This is a forced-backend comparison; the automatic target-three pair checker is a separate cheaper path.

Physical locations, full alternatives, detector/logical dimensions and repeated signatures are in [raw evidence](../results/compute/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/structure_profiles.json). Per-layer hashes, transitions and censored progress remain in raw packets. A new matched full-size SAT/standalone-DP comparison is NOT_RUN; their existing exact semantics remain regression-tested. The target-five MITM positive is not substituted into these timing comparisons.

## Table C — Cross-family code-only populations

| Run | Generated | Compiled | Distinct | Noiseless valid | Screened | Simulated | Certified | Invalid | UNKNOWN | Worker CPU s | Controller CPU s | Wall s | Peak worker MiB | Best Q/D/QD/2Q |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| [hgp58_hybrid_331](../results/non_graphlike/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/population_study/hgp58_hybrid_331/checkpoint.json) | 12 | 12 | 12 | 12 | 12 | 12 | 4 | 0 | 0 | 60.391 | 92.109 | 142.624 | 85.13 | 100/49/4900/240 |
| [hgp58_hybrid_443](../results/non_graphlike/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/population_study/hgp58_hybrid_443/checkpoint.json) | 12 | 12 | 10 | 12 | 10 | 10 | 4 | 0 | 0 | 76.078 | 212.359 | 274.978 | 112.73 | 100/48/4800/720 |
| [shor5_costhybrid_101](../results/non_graphlike/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/population_study/shor5_costhybrid_101/checkpoint.json) | 12 | 12 | 10 | 12 | 8 | 5 | 0 | 3 | 7 | 505.469 | 90.969 | 603.812 | 113.11 | none |
| [shor5_costhybrid_211](../results/non_graphlike/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/population_study/shor5_costhybrid_211/checkpoint.json) | 12 | 12 | 11 | 12 | 9 | 6 | 0 | 7 | 4 | 334.656 | 85.078 | 404.350 | 98.78 | none |
| [shor5_hybrid_101](../results/non_graphlike/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/population_study/shor5_hybrid_101/checkpoint.json) | 12 | 12 | 10 | 12 | 10 | 9 | 0 | 3 | 2 | 235.672 | 95.984 | 268.947 | 113.53 | none |
| [shor5_hybrid_211](../results/non_graphlike/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/population_study/shor5_hybrid_211/checkpoint.json) | 12 | 12 | 9 | 12 | 9 | 8 | 0 | 4 | 1 | 117.938 | 29.297 | 144.543 | 79.81 | none |
| [shor5_random_101](../results/non_graphlike/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/population_study/shor5_random_101/checkpoint.json) | 12 | 12 | 12 | 12 | 12 | 12 | 1 | 2 | 1 | 187.578 | 98.516 | 250.261 | 86.47 | 36/329/11844/248 |
| [shor5_random_211](../results/non_graphlike/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/population_study/shor5_random_211/checkpoint.json) | 12 | 12 | 12 | 12 | 12 | 12 | 0 | 3 | 1 | 143.062 | 53.156 | 178.504 | 88.42 | none |
| [shor5_witness_101](../results/non_graphlike/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/population_study/shor5_witness_101/checkpoint.json) | 12 | 12 | 10 | 12 | 10 | 9 | 0 | 3 | 2 | 225.844 | 83.188 | 247.120 | 113.98 | none |
| [shor5_witness_211](../results/non_graphlike/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/population_study/shor5_witness_211/checkpoint.json) | 12 | 12 | 11 | 12 | 11 | 10 | 0 | 3 | 2 | 157.969 | 74.141 | 183.323 | 96.27 | none |

Shor-product [[25,1,5]] requests target five; Hamming hypergraph-product [[58,16,3]] requests target three. [Algebraic evidence](../results/non_graphlike/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/population_study/algebraic.json). Distinct counts are per run, not across repeated trials. Screened but unproved candidates are not silently classified UNKNOWN or INVALID. Post-study deferred certification/allocation costs are separate and not retroactively credited to original policies.

## Table D — Screening and allocation comparison limits

| Comparison | Status | Positive retention / false rejection | Interpretation |
|---|---|---|---|
| Random/witness/hybrid populations | Finite observed trials | NOT_RUN as complete ground-truth rates | Actual costs above; equal generations are not matched compute. |
| Cost-aware hybrid | Finite observed trials | NOT_RUN as complete ground-truth rates | Generation and evaluation effects remain coupled. |
| Direct certification vs fixed multifidelity on a common pool | NOT_RUN | NOT_RUN | No causal allocation advantage claimed. |
| Fixed vs cost-aware allocation at matched CPU checkpoints | NOT_RUN | NOT_RUN | Requires a frozen common pool and retention ground truth. |

## Table E — Acceptance gates

| Gate | Status | Evidence type | Evidence | Unresolved requirement |
|---|---|---|---|---|
| A | PASS | Scientific preservation | 29,374 prior files matched; admission-stopped baseline tests passed on retry; 118 current tests pass. | None within frozen scope. |
| B | PASS | Scientific replay | 13 harmful Shor witnesses independently replayed among 25 preserved controls. | Other historical epochs remain unchanged. |
| C | PASS | Scientific diagnosis | Independent individual and simultaneous propagation establishes hook spread and flag cancellation. | Gate context alone is not causation. |
| D | PASS | Engineering and construction | Generic flag, cat, verification, order, repetition and allocation operators produce real circuits. | No universal repair guarantee. |
| E | PARTIAL | Scientific repair | Six composed descendants evaluated and retained. | No certified invalid-to-valid six-arm lineage. |
| F | PARTIAL | Evaluation pipeline | Singleton screening, mapped-witness replay and exact prefix checks reject harmful candidates. | No comprehensive cheap multi-fault screen or shared cross-run negative cache. |
| G | PASS | Population discovery | Bare, flagged, cat and verified-cat populations retained; random generation found the qualifying positive. | No general witness/hybrid advantage. |
| H | PASS | Scientific eligibility | Every configured projection independently audited. | Portfolio-relative ineligibility only. |
| I | PASS | Scientific exact method | Reduced separator independently completes graph-ineligible target-three control. | No separator target-five positive. |
| J | PARTIAL | Exact-method research | MITM and SAT semantics preserved; existing MITM supplies target-five proof. | No new MITM-partition or incremental-SAT advance. |
| K | PASS | Scientific verification | Adopted positives separately replayed; exports reconstructed; reported negative/upper witnesses replayed. | None for adopted results. |
| L | PASS | Primary scientific milestone | Code-only [[25,1,5]], independent graph ineligibility and exact-distance-five proof, exported. | Ideal-boundary extraction scope. |
| M | PASS | Cross-family science | Independent HGP target-three positives and a re-certified improvement from Q100 D53 720 two-qubit gates to Q100 D49 240 gates. | High-distance gains outside the primary family remain unestablished. |
| N | PASS | Certified resources | Q36 D329 and Q105 D46 target-five alternatives adopted; target-ten frontier preserved. | Finite frontier, not global optimum. |
| O | PASS | Decoder-conditional science | Matched 131,072-shot arms with exact simultaneous intervals. | Overlapping intervals; one-mechanism decoder and ideal boundaries. |
| P | PASS | Execution evidence | Actual worker PIDs and overlapping intervals. | Individual worker peak is not aggregate system peak. |
| Q | PASS | Public delivery | Installed Optimize/resume/export/verify-export and independent reconstruction pass. | Legacy raw guard-only bundle-export limitation remains. |
| R | PASS | Reproducible delivery | Protocols, raw outcomes, source, tested wheel and integrity release. | Final archive/manifest receipts accompany delivery; no push/cloud. |

The independent HGP comparison re-certifies the previous Q100,D53,720-two-qubit circuit and the new Q100,D49,240-two-qubit circuit at target three. Previous Q64,D72 and Q59,D408 alternatives remain certified. [Cross-family comparison](../results/cross_family/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/comparison.json). This is a finite resource improvement, not a second-family distance-five result.

## Decoder-conditional reliability

| Circuit | Physical p | Failures / shots | Rate | Simultaneous interval |
|---|---:|---:|---:|---|
| low_qubit | 0.0001 | 11 / 131072 | 8.392334e-05 | [3.4018746045893254e-05, 0.00017066507414274042] |
| low_qubit | 0.001 | 1680 / 131072 | 0.012817383 | [0.012054246837380208, 0.013614139941787031] |
| low_qd | 0.0001 | 14 / 131072 | 0.00010681152 | [4.8828269436987255e-05, 0.00020137354607580816] |
| low_qd | 0.001 | 1609 / 131072 | 0.012275696 | [0.011528945458885881, 0.013056109524543781] |

[Frozen LER protocol](../results/ler/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/target5_matched/protocol.json). Both circuits use the same one-mechanism lookup decoder with explicit zero fallback. Exact binomial intervals use a four-arm Bonferroni correction and overlap at both noise levels. No reliability ordering is established. Automatic matching rejected unsupported detector decomposition; that fallback record is retained. Logical-Z-sector operation-noise experiments are not complete physical-memory or decoder-independent guarantees.

## Recorded computation

| Stage | Actual worker executions | Worker CPU s | Summed worker wall s | Peak individual worker MiB |
|---|---:|---:|---:|---:|
| certify | 105 | 2871.391 | 3513.105 | 121.28 |
| construct | 132 | 330.875 | 357.140 | 104.58 |
| screen | 115 | 55.328 | 79.403 | 61.09 |
| simulation | 167 | 264.984 | 355.303 | 112.73 |
| verify | 14 | 135.234 | 168.977 | 45.19 |

Observed peak overlap: 4 workers. Recorded worker CPU: 3657.812s. Worker execution envelope: 3377.049s. Deduplicated actual workers; summed worker wall is not elapsed time. Tests, packaging, intake and unmeasured ad-hoc controller overhead are separate. No all-inclusive total-compute claim.

[Execution records](../results/compute/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/execution_summary.json). Controller body CPU/wall are saved separately by each driver; population costs appear in Table C. Local computing sufficed for the declared experiments. No cloud resources were provisioned.

## Explicit scientific questions

Controller body costs below include the population driver once; its per-run session costs in Table C must not be added again. Startup and uninstrumented ad-hoc first-positive export overhead are not included.

| Controller receipt | Body CPU s | Wall s |
|---|---:|---:|
| [results\non_graphlike\d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306\population_study](../results/non_graphlike/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/population_study/complete.json) | 939.266 | 2723.295 |
| [results\repair_trajectories\d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306\shor5_six_arm](../results/repair_trajectories/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/shor5_six_arm/complete.json) | 39.016 | 1045.245 |
| [results\pareto\d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306\allocation_study](../results/pareto/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/allocation_study/complete.json) | 16.094 | 249.419 |
| [results\pareto\d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306\deferred_frontier](../results/pareto/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/deferred_frontier/complete.json) | 3.266 | 146.298 |
| [results\pareto\d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306\compaction_study](../results/pareto/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/compaction_study/complete.json) | 2.703 | 122.942 |
| [results\general_extraction\controls\d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306](../results/general_extraction/controls/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/complete.json) | 66.484 | 170.157 |
| [results\general_extraction\proof_development\d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306](../results/general_extraction/proof_development/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/complete.json) | 2.562 | 27.065 |
| [results\certification\d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306\small_matched](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_matched/complete.json) | 0.953 | 7.479 |
| [results\certification\d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306\small_positive_matched](../results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_positive_matched/complete.json) | 3.094 | 124.397 |
| [results\ler\d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306\target5_matched](../results/ler/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/target5_matched/complete.json) | 2.141 | 17.221 |
| [results\exports\d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306\finalists](../results/exports/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/finalists/complete.json) | 186.422 | 379.182 |
| [results\cross_family\d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306](../results/cross_family/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/comparison.json) | 0.484 | 4.012 |

All-known historical and new certified discovery alternatives remain in [the merged frontier archive](../results/pareto/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/all_known_frontiers.json). Historical certificates retain their original source identities.

1. Preserved witnesses include propagated ancilla faults and multi-fault flag cancellation. Thirteen harmful Shor controls were independently replayed; the diagnosis index retains each physical configuration.

2. Implemented overlapping flags and a six-arm portfolio combining implicated-check ordering, verified-cat verification, repetition, scheduling and compaction. Existing basis/cat/adjacent/nested operators remain.

3. Mapped mechanisms may change, but failed operation-context transfer is NOT_TRANSFERABLE, not elimination. No composed six-arm descendant became independently certified at target five.

4. No certified invalid-to-valid six-arm lineage was established. The successful code-only verified-cat discovery is a separate result, not relabelled as a repair.

5. The valid-parent allocation descendant uses Q=105,D=46,QD=4,830 versus Q=36,D=329,QD=11,844. Both use 248 two-qubit gates, recomputed from exported schedules.

6. The qualifying verified-cat target-five circuit and Shor target-four control are graph-ineligible for the implemented portfolio. Every adopted circuit has an eligibility receipt.

7. All configured projection masks and physical obstructions are retained. The first positive fails all four choices for logical channel zero; two choices for channel one are eligible, insufficient for full graph certification.

8. Yes. Circuit b090363c8b677a189be3c07d0b459bfba25896b708b9afb8a5dba8cf7bde1472 on [[25,1,5]] has an independently replayed MITM lower bound and matching weight-five upper witness.

9. MITM supplies target-five positives; graph proves eligible target-ten controls; reduced separator completes graph-ineligible target-three and physical target-two controls. Bounded higher-target separator proofs remain UNKNOWN; new full-size SAT/DP comparisons were not run.

10. Whole-location reduction improves separator CPU, memory and completion on the matched target-three control. Span pruning alone did not improve the initial bounded study. No universal or target-five separator advantage is claimed.

11. Table B and raw progress provide maximum states, widths, transitions and complete per-layer hashes. A censored prefix maximum is not a completed-graph width.

12. Repeated signatures, XOR-closed physical domains, inclusion, disjoint components and suffix-span impossibility tests support exact reduction. Structure profiles quantify the successful cat circuit versus dense flag controls.

13. Yes. Full inventories are hash-bound; independent domain coverage and closure checks prove a cost-nonincreasing physical replacement. Correlated components are never split and location exclusivity is preserved.

14. Every adopted positive receives separate proof replay and export reconstruction. Reported harmful and matching upper witnesses have a separate replay index. Produced positives also have internal independent checks.

15. The UNKNOWN index retains each exact circuit, target, method, recorded verified bound and unresolved interval/guard reason. Missing bounds are not invented.

16. The deterministic portfolio uses graph eligibility and exact structure reduction before MITM/DP. The qualifying proof needed MITM after separator incompletion. A learned or broadly optimal selector was not established.

17. Table C records actual generated, compiled, screened, simulated and certified counts. Duplicate physical circuits and repeated trials are distinguished in raw records.

18. Verified-cat generation produced the strongest target-five discoveries. Several flagged multi-fault repair descendants were invalid or unresolved.

19. No certified invalid-to-valid multi-fault repair gain was shown. A generic valid-parent allocation change improved certified QD while preserving the lower-qubit alternative.

20. Real compositions were evaluated, but the six-arm study does not establish superiority over isolated repairs. That causal ablation is NOT_RUN.

21. Five scheduling/allocation descendants of a certified parent became invalid. Historical fault transfer is tracked separately; noiseless semantics does not imply distance preservation.

22. The target-five frontier includes Q=36,D=329,QD=11,844 and Q=105,D=46,QD=4,830, both with 248 two-qubit gates. Exact finite frontiers and dominated positives are preserved.

23. Yes. Lower-Q nondominated alternatives remain, and equal-resource distinct physical discoveries retain separate provenance.

24. Each checkpoint retains generation-level frontier histories and simulation batches. No general monotone reliability improvement or global convergence is inferred.

25. Yes. Frozen inputs contain only code data; all ancestry roots are code-derived and every parent is local to the same run. Historical controls and post-discovery studies are separately labelled.

26. Shor-product and Hamming hypergraph-product are distinct CSS construction families. Surface circuits are preserved controls, not new cross-family discoveries.

27. Yes, the code-only [[25,1,5]] discovery qualifies. A second independent non-surface distance-five family result remains unestablished.

28. Cross-family optimization was evaluated separately. New high-distance repair and separator gains outside the primary construction family remain unestablished.

29. Unsupported matching decomposition, invalid controls, guarded UNKNOWN proofs and unproved screened candidates remain distinct. Non-CSS high-distance optimization is outside this cycle.

30. Actual Shor/HGP outcomes, generic metadata-based operators and exhaustive small-domain oracles support scoped applicability, not universal efficient certification or broad high-distance generalization.

31. Actual worker CPU/wall/peak appear in stage tables and receipts; controller body costs are separate. Unmeasured startup or interactive overhead is not presented as an all-inclusive total.

32. The reduced separator completes the matched small graph-ineligible proof with less CPU and memory than prior separator attempts, at the same requested bound. No unmatched-input timing establishes a speedup.

33. Singleton screening and mapped-witness replay stop deep work when they find a witness. No exhaustive cheap multi-fault screen or shared cross-run negative cache was demonstrated.

34. Yes. Distinct supervised PIDs have overlapping measured intervals; the exact peak overlap is in the execution summary.

35. Local computing completed the declared experiments, exports and tests. Proof safeguards still produced UNKNOWN; baseline memory-admission failures passed after memory was freed.

36. No cloud escalation was required or provisioned. Exponential state growth alone is not a justification for billable cloud resources.

37. All 29,374 frozen prior files matched. Four initial admission failures were preserved and passed on retry. The adopted source passes 118 tests.

38. Yes. Export verification reconstructs circuits, exact schedules, dependencies, detector definitions and resources, then replays bound proof evidence. The isolated installed package also verifies the target-five bundle.

39. Gates E,F,J remain PARTIAL: certified invalid-to-valid composition, comprehensive multi-fault early rejection, new MITM/SAT advances. High-distance cross-family generalization is also not claimed.

40. Derive fault-aware scheduling constraints from replayed witnesses of the five rejected allocation descendants, then test those repairs prospectively on fresh code-only inputs with complete re-certification.

## Reproduction

Install the matching wheel/source and run `ftqec verify-export BUNDLE --proof-work 20000000 --require-certified`. Optimize into a fresh output directory; never overwrite frozen folders. Raw settings, seeds, task identities, circuits, failures, proof states and source snapshots accompany delivery. The previous scientific archive is separately preserved and hash-referenced.

The release receipt records the final commit, source and integrity manifests. No public push occurred.
