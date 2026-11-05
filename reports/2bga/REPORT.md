# 2BGA extraction and repeated physical memory: development report

## Outcome and scope

The code-only population discovered a verified-cat architecture for the supplied independently validated **[[24,2,4]] code: four noisy rounds, independently checked target-distance-four certificates in both X and Z memory sectors**. Its best paired resources are Q=192, D=96/94 (X/Z), QD=18432/18048, and 2016 two-qubit gates per sector. Single extraction depth is 23. This does not establish published-reference competitiveness. The completed development records below distinguish certified controls, verified-invalid circuits, partial bounds, and unproved candidates. There is no claim of a competitive certified 2BGA frontier, a decoder-independent reliability advantage, or a globally optimal schedule.

The physical task is noisy product preparation, repeated CSS measurements, and destructive physical data readout. X and Z memory sectors are separate experiments. No perfect final syndrome is inserted. This is not an arbitrary-input encoding or physical hardware-routing certificate. All experiments in the tables use operation-local noise p=0.001 and no implicit idle noise. An explicit-storage mode is implemented and tested separately. Reset/readout faults and correlated two-qubit alternatives are retained with location exclusivity.

Implementation commit: `481226173795c618e8e2a64474234c95eed41702`. Final scientific source: `8a43717de1b7ce80e7e457cff96e090ba73617299fcccdba0efbb26b547be51f`. Phase-one source is retained independently in `implementation-source.zip`; expanded and final sources are in `expanded/source.zip` and `streamed/source.zip`. Replaying a proof requires its matching scientific source. These are development phases with different sources and seeds, not a matched causal comparison of search policies.

The complete local epoch is `results/2bga/epoch-20261105`. Links below refer to local raw artifacts; the supplied archive and correspondence have not been published. The previous large-population matrix and original external evidence repository were not modified.

## Inputs and conventions — report questions 1–3

The archive contains 17 code JSON inputs, construction scripts, summary metadata, a README and accompanying notes. It supplies neither executable extraction reference circuits nor schedules nor separately certified logical-operator files. All inputs were imported. The convention is HX=[L(a)|R(b)], HZ=[R(b)^T|L(a)^T], with the supplied multiplication-table ordering retained. Full redundant checks, rather than only the input independent basis, are measured. Every supplied full check has weight six.

All group tables, left/right actions, CSS commutation, ranks and stabilizer-span equivalences passed the algebra audit. Distances remain supplied claims except the three independently enumerated distance-four codes. “Integer program” in archive metadata is not a portable checked solver proof. See [archive-audit.json](../../results/2bga/epoch-20261105/archive-audit.json), [small-code-distance.json](../../results/2bga/epoch-20261105/small-code-distance.json), `algebra/` and `normalized/`.

| Input | n | k | Supplied d | Independent distance |
|---|---|---|---|---|
| 2bga_D12_n48_k4_d6.json | 48 | 4 | 6 | not completed |
| 2bga_D12_n48_k4_d8.json | 48 | 4 | 8 | not completed |
| 2bga_D14_n56_k6_d4.json | 56 | 6 | 4 | not completed |
| 2bga_D15_n60_k4_d6.json | 60 | 4 | 6 | not completed |
| 2bga_D15_n60_k4_d8.json | 60 | 4 | 8 | not completed |
| 2bga_D18_n72_k12_d4.json | 72 | 12 | 4 | not completed |
| 2bga_D18_n72_k4_d8.json | 72 | 4 | 8 | not completed |
| 2bga_D21_n84_k4_d10.json | 84 | 4 | 10 | not completed |
| 2bga_D21_n84_k8_d6.json | 84 | 8 | 6 | not completed |
| 2bga_D6_n24_k2_d4.json | 24 | 2 | 4 | 4 |
| 2bga_D6_n24_k4_d4.json | 24 | 4 | 4 | 4 |
| 2bga_D9_n36_k4_d6.json | 36 | 4 | 6 | not completed |
| 2bga_D9_n36_k8_d4.json | 36 | 8 | 4 | 4 |
| bb_n108_k8_d10.json | 108 | 8 | 10 | not completed |
| bb_n144_k12_d12.json | 144 | 12 | 12 | not completed |
| bb_n72_k12_d6.json | 72 | 12 | 6 | not completed |
| bb_n90_k8_d10.json | 90 | 8 | 10 | not completed |

![Measured architecture resources](../../results/2bga/epoch-20261105/resource_outcomes.png)

## Architecture and resource results — questions 4–8, 11–12

The first phase used full-check group-term orderings. The expanded phase added structured axis orders, bare/flagged/cat/verified-cat gadgets, reused ancilla slots, and existing dependency-aware critical-path, conflict-color and resource scheduling. Parents and mutations are recorded; generation two includes witness-guided mutation. No successful reference circuit or schedule was supplied as a seed. Uniform ordering does not constitute a proved non-abelian symmetry; no fault-orbit quotient was used.

Every resource tuple below is recomputed from actual operations and schedules. D includes unit-duration explicit gates, preparation and readout; BARRIER has zero duration. Two-qubit layer counts are occupied layers of this schedule, not a separately minimized two-qubit circuit. The single column is the ideal-boundary extraction template depth; memory D includes physical boundaries. X/Z depths differ because X preparation/readout uses explicit H gates. Rows without a proof were retained, not declared valid at the target. Short IDs are display abbreviations; full identities are in summary.json and exports.

| Run | ID / family / sector | r / target | Q | Single D | Memory D | QD | 2Q gates | 2Q layers | Outcome | Lower / upper |
|---|---|---|---|---|---|---|---|---|---|---|
| 2bga_D6_n24_k2_d4-r1 | 8768fc6a31 / group_term / X | 1 / 4 | 48 | 12 | 16 | 768 | 144 | 9 | INVALID | 1 / 2 |
| 2bga_D6_n24_k2_d4-r1 | b6ca894135 / group_term / Z | 1 / 4 | 48 | 12 | 14 | 672 | 144 | 9 | INVALID | 1 / 3 |
| 2bga_D6_n24_k2_d4-r2 | 61316695db / group_term / X | 2 / 4 | 48 | 12 | 28 | 1344 | 288 | 18 | INVALID | 1 / 2 |
| 2bga_D6_n24_k2_d4-r2 | a3169b2604 / group_term / Z | 2 / 4 | 48 | 12 | 26 | 1248 | 288 | 18 | UNKNOWN | 3 / None |
| 2bga_D6_n24_k4_d4-r4 | c481283014 / group_term / X | 4 / 4 | 48 | 12 | 52 | 2496 | 576 | 36 | UNKNOWN | 3 / None |
| 2bga_D6_n24_k4_d4-r4 | a9d94b5b77 / group_term / Z | 4 / 4 | 48 | 12 | 50 | 2400 | 576 | 36 | INVALID | 1 / 2 |
| 2bga_D9_n36_k8_d4-r4 | 6a41c409da / group_term / X | 4 / 4 | 72 | 12 | 52 | 3744 | 864 | 36 | UNKNOWN | 3 / None |
| 2bga_D9_n36_k8_d4-r4 | 8c990d91b3 / group_term / Z | 4 / 4 | 72 | 12 | 50 | 3600 | 864 | 36 | UNKNOWN | 3 / None |
| bb_n72_k12_d6-r6 | 535b23e8df / group_term / X | 6 / 6 | 144 | 12 | 76 | 10944 | 2592 | 54 | UNKNOWN | 3 / None |
| bb_n72_k12_d6-r6 | 5b6c16d76c / group_term / Z | 6 / 6 | 144 | 12 | 74 | 10656 | 2592 | 54 | UNKNOWN | 3 / None |
| d6-k2-r4 | 1a5a2ed425 / group_term / X | 4 / 4 | 48 | 12 | 52 | 2496 | 576 | 36 | INVALID | 1 / 2 |
| d6-k2-r4 | 0f492e9a53 / group_term / Z | 4 / 4 | 48 | 12 | 50 | 2400 | 576 | 36 | UNKNOWN | 3 / None |
| expanded-d6-k2-r4 | 1a5a2ed425 / group_term / X | 4 / 4 | 48 | 12 | 52 | 2496 | 576 | 36 | INVALID | 1 / 2 |
| expanded-d6-k2-r4 | 0f492e9a53 / group_term / Z | 4 / 4 | 48 | 12 | 50 | 2400 | 576 | 36 | UNKNOWN | 3 / None |
| expanded-d6-k2-r4 | 7f8aa7871b / group_term / X | 4 / 4 | 48 | 14 | 60 | 2880 | 576 | 44 | UNKNOWN | 3 / None |
| expanded-d6-k2-r4 | d545f8dd38 / group_term / Z | 4 / 4 | 48 | 14 | 58 | 2784 | 576 | 44 | INVALID | 1 / 2 |
| expanded-d6-k2-r4 | 230ef3b1b1 / group_term / X | 4 / 4 | 48 | 14 | 60 | 2880 | 576 | 44 | INVALID | 1 / 2 |
| expanded-d6-k2-r4 | a4b6eba73e / group_term / Z | 4 / 4 | 48 | 14 | 58 | 2784 | 576 | 44 | INVALID | 1 / 2 |
| expanded-d6-k2-r4 | fae95eca53 / flagged / X | 4 / 4 | 168 | 52 | 212 | 35616 | 1536 | 120 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 03ac1d4fcc / flagged / Z | 4 / 4 | 168 | 52 | 210 | 35280 | 1536 | 120 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | c0d21ac1a4 / cat / X | 4 / 4 | 168 | 14 | 60 | 10080 | 1056 | 40 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 07bb71c7f2 / cat / Z | 4 / 4 | 168 | 14 | 58 | 9744 | 1056 | 40 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 4b9e515bad / verified_cat / X | 4 / 4 | 192 | 23 | 96 | 18432 | 2016 | 64 | UNKNOWN | 3 / None |
| expanded-d6-k2-r4 | fd780f50d1 / verified_cat / Z | 4 / 4 | 192 | 23 | 94 | 18048 | 2016 | 64 | UNKNOWN | 3 / None |
| expanded-d6-k2-r4 | 389264fdb4 / bare / X | 4 / 4 | 36 | 18 | 76 | 2736 | 576 | 48 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 2081a23a70 / bare / Z | 4 / 4 | 36 | 18 | 74 | 2664 | 576 | 48 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 2286c64717 / group_term / X | 4 / 4 | 48 | 15 | 64 | 3072 | 576 | 48 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | eab8931c40 / group_term / Z | 4 / 4 | 48 | 15 | 62 | 2976 | 576 | 48 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 66471e17cd / cat / X | 4 / 4 | 168 | 14 | 60 | 10080 | 1056 | 40 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 5b85534250 / cat / Z | 4 / 4 | 168 | 14 | 58 | 9744 | 1056 | 40 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 4a3a235bb5 / group_term / X | 4 / 4 | 48 | 14 | 60 | 2880 | 576 | 44 | INVALID | 1 / 2 |
| expanded-d6-k2-r4 | 72f7846e49 / group_term / Z | 4 / 4 | 48 | 14 | 58 | 2784 | 576 | 44 | INVALID | 1 / 2 |
| expanded-d6-k2-r4 | 627388642a / flagged / X | 4 / 4 | 168 | 49 | 200 | 33600 | 1536 | 112 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 2df8dca2ec / flagged / Z | 4 / 4 | 168 | 49 | 198 | 33264 | 1536 | 112 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 9ad73cc59a / bare / X | 4 / 4 | 36 | 18 | 76 | 2736 | 576 | 48 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | a3d734297c / bare / Z | 4 / 4 | 36 | 18 | 74 | 2664 | 576 | 48 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 08f859784a / verified_cat / X | 4 / 4 | 192 | 24 | 100 | 19200 | 2016 | 72 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 34122f3cf6 / verified_cat / Z | 4 / 4 | 192 | 24 | 98 | 18816 | 2016 | 72 | NOT_RUN | None / None |
| expanded-d6-k2-r4 | 1fa3ba8c32 / verified_cat / X | 4 / 4 | 192 | 23 | 96 | 18432 | 2016 | 64 | UNKNOWN | 3 / None |
| expanded-d6-k2-r4 | 50f6ff49ff / verified_cat / Z | 4 / 4 | 192 | 23 | 94 | 18048 | 2016 | 64 | UNKNOWN | 3 / None |
| streamed-d6-k2-r4 | 1a5a2ed425 / group_term / X | 4 / 4 | 48 | 12 | 52 | 2496 | 576 | 36 | INVALID | 1 / 2 |
| streamed-d6-k2-r4 | 0f492e9a53 / group_term / Z | 4 / 4 | 48 | 12 | 50 | 2400 | 576 | 36 | INVALID | 1 / 3 |
| streamed-d6-k2-r4 | 7f8aa7871b / group_term / X | 4 / 4 | 48 | 14 | 60 | 2880 | 576 | 44 | INVALID | 1 / 3 |
| streamed-d6-k2-r4 | d545f8dd38 / group_term / Z | 4 / 4 | 48 | 14 | 58 | 2784 | 576 | 44 | INVALID | 1 / 2 |
| streamed-d6-k2-r4 | 230ef3b1b1 / group_term / X | 4 / 4 | 48 | 14 | 60 | 2880 | 576 | 44 | INVALID | 1 / 2 |
| streamed-d6-k2-r4 | a4b6eba73e / group_term / Z | 4 / 4 | 48 | 14 | 58 | 2784 | 576 | 44 | INVALID | 1 / 2 |
| streamed-d6-k2-r4 | fae95eca53 / flagged / X | 4 / 4 | 168 | 52 | 212 | 35616 | 1536 | 120 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 03ac1d4fcc / flagged / Z | 4 / 4 | 168 | 52 | 210 | 35280 | 1536 | 120 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | c0d21ac1a4 / cat / X | 4 / 4 | 168 | 14 | 60 | 10080 | 1056 | 40 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 07bb71c7f2 / cat / Z | 4 / 4 | 168 | 14 | 58 | 9744 | 1056 | 40 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 4b9e515bad / verified_cat / X | 4 / 4 | 192 | 23 | 96 | 18432 | 2016 | 64 | CERTIFIED | 4 / None |
| streamed-d6-k2-r4 | fd780f50d1 / verified_cat / Z | 4 / 4 | 192 | 23 | 94 | 18048 | 2016 | 64 | CERTIFIED | 4 / 4 |
| streamed-d6-k2-r4 | 389264fdb4 / bare / X | 4 / 4 | 36 | 18 | 76 | 2736 | 576 | 48 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 2081a23a70 / bare / Z | 4 / 4 | 36 | 18 | 74 | 2664 | 576 | 48 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 2286c64717 / group_term / X | 4 / 4 | 48 | 15 | 64 | 3072 | 576 | 48 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | eab8931c40 / group_term / Z | 4 / 4 | 48 | 15 | 62 | 2976 | 576 | 48 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 66471e17cd / cat / X | 4 / 4 | 168 | 14 | 60 | 10080 | 1056 | 40 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 5b85534250 / cat / Z | 4 / 4 | 168 | 14 | 58 | 9744 | 1056 | 40 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 4a3a235bb5 / group_term / X | 4 / 4 | 48 | 14 | 60 | 2880 | 576 | 44 | INVALID | 1 / 2 |
| streamed-d6-k2-r4 | 72f7846e49 / group_term / Z | 4 / 4 | 48 | 14 | 58 | 2784 | 576 | 44 | INVALID | 1 / 2 |
| streamed-d6-k2-r4 | 627388642a / flagged / X | 4 / 4 | 168 | 49 | 200 | 33600 | 1536 | 112 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 2df8dca2ec / flagged / Z | 4 / 4 | 168 | 49 | 198 | 33264 | 1536 | 112 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 9ad73cc59a / bare / X | 4 / 4 | 36 | 18 | 76 | 2736 | 576 | 48 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | a3d734297c / bare / Z | 4 / 4 | 36 | 18 | 74 | 2664 | 576 | 48 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 08f859784a / verified_cat / X | 4 / 4 | 192 | 24 | 100 | 19200 | 2016 | 72 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 34122f3cf6 / verified_cat / Z | 4 / 4 | 192 | 24 | 98 | 18816 | 2016 | 72 | NOT_RUN | None / None |
| streamed-d6-k2-r4 | 1fa3ba8c32 / verified_cat / X | 4 / 4 | 192 | 23 | 96 | 18432 | 2016 | 64 | CERTIFIED | 4 / None |
| streamed-d6-k2-r4 | 50f6ff49ff / verified_cat / Z | 4 / 4 | 192 | 23 | 94 | 18048 | 2016 | 64 | CERTIFIED | 4 / 4 |
| refined-2bga_D6_n24_k2_d4-r2 | 61316695db / group_term / X | 2 / 4 | 48 | 12 | 28 | 1344 | 288 | 18 | INVALID | 1 / 2 |
| refined-2bga_D6_n24_k2_d4-r2 | a3169b2604 / group_term / Z | 2 / 4 | 48 | 12 | 26 | 1248 | 288 | 18 | INVALID | 1 / 3 |
| refined-2bga_D6_n24_k4_d4-r4 | c481283014 / group_term / X | 4 / 4 | 48 | 12 | 52 | 2496 | 576 | 36 | CERTIFIED | 4 / None |
| refined-2bga_D6_n24_k4_d4-r4 | a9d94b5b77 / group_term / Z | 4 / 4 | 48 | 12 | 50 | 2400 | 576 | 36 | INVALID | 1 / 2 |
| refined-2bga_D9_n36_k8_d4-r4 | 6a41c409da / group_term / X | 4 / 4 | 72 | 12 | 52 | 3744 | 864 | 36 | INVALID | 1 / 3 |
| refined-2bga_D9_n36_k8_d4-r4 | 8c990d91b3 / group_term / Z | 4 / 4 | 72 | 12 | 50 | 3600 | 864 | 36 | INVALID | 1 / 3 |
| refined-bb_n72_k12_d6-r6 | 535b23e8df / group_term / X | 6 / 6 | 144 | 12 | 76 | 10944 | 2592 | 54 | UNKNOWN | 4 / None |
| refined-bb_n72_k12_d6-r6 | 5b6c16d76c / group_term / Z | 6 / 6 | 144 | 12 | 74 | 10656 | 2592 | 54 | UNKNOWN | 4 / None |
| refined-d6-k2-r4 | 1a5a2ed425 / group_term / X | 4 / 4 | 48 | 12 | 52 | 2496 | 576 | 36 | INVALID | 1 / 2 |
| refined-d6-k2-r4 | 0f492e9a53 / group_term / Z | 4 / 4 | 48 | 12 | 50 | 2400 | 576 | 36 | INVALID | 1 / 3 |
| refined-population | fae95eca53 / flagged / X | 4 / 4 | 168 | 52 | 212 | 35616 | 1536 | 120 | CERTIFIED | 4 / None |
| refined-population | 03ac1d4fcc / flagged / Z | 4 / 4 | 168 | 52 | 210 | 35280 | 1536 | 120 | INVALID | 1 / 3 |
| refined-population | c0d21ac1a4 / cat / X | 4 / 4 | 168 | 14 | 60 | 10080 | 1056 | 40 | INVALID | 1 / 2 |
| refined-population | 07bb71c7f2 / cat / Z | 4 / 4 | 168 | 14 | 58 | 9744 | 1056 | 40 | INVALID | 1 / 2 |
| refined-population | 389264fdb4 / bare / X | 4 / 4 | 36 | 18 | 76 | 2736 | 576 | 48 | INVALID | 1 / 3 |
| refined-population | 2081a23a70 / bare / Z | 4 / 4 | 36 | 18 | 74 | 2664 | 576 | 48 | INVALID | 1 / 2 |
| refined-population | 2286c64717 / group_term / X | 4 / 4 | 48 | 15 | 64 | 3072 | 576 | 48 | CERTIFIED | 4 / None |
| refined-population | eab8931c40 / group_term / Z | 4 / 4 | 48 | 15 | 62 | 2976 | 576 | 48 | INVALID | 1 / 3 |
| refined-population | 66471e17cd / cat / X | 4 / 4 | 168 | 14 | 60 | 10080 | 1056 | 40 | INVALID | 1 / 2 |
| refined-population | 5b85534250 / cat / Z | 4 / 4 | 168 | 14 | 58 | 9744 | 1056 | 40 | INVALID | 1 / 2 |
| refined-population | 627388642a / flagged / X | 4 / 4 | 168 | 49 | 200 | 33600 | 1536 | 112 | CERTIFIED | 4 / None |
| refined-population | 2df8dca2ec / flagged / Z | 4 / 4 | 168 | 49 | 198 | 33264 | 1536 | 112 | CERTIFIED | 4 / 4 |
| refined-population | 9ad73cc59a / bare / X | 4 / 4 | 36 | 18 | 76 | 2736 | 576 | 48 | INVALID | 1 / 3 |
| refined-population | a3d734297c / bare / Z | 4 / 4 | 36 | 18 | 74 | 2664 | 576 | 48 | INVALID | 1 / 3 |
| refined-population | 08f859784a / verified_cat / X | 4 / 4 | 192 | 24 | 100 | 19200 | 2016 | 72 | CERTIFIED | 4 / None |
| refined-population | 34122f3cf6 / verified_cat / Z | 4 / 4 | 192 | 24 | 98 | 18816 | 2016 | 72 | CERTIFIED | 4 / 4 |
| baseline-comparison | 537afde732 / verified_cat / X | 4 / 4 | 192 | 33 | 136 | 26112 | 2016 | 108 | CERTIFIED | 4 / None |
| baseline-comparison | 4aa88f6076 / verified_cat / Z | 4 / 4 | 192 | 33 | 134 | 25728 | 2016 | 108 | CERTIFIED | 4 / 4 |

Evidence: [summary.json](../../results/2bga/epoch-20261105/summary.json) and each run's checkpoint, task packets, proofs and frontier. Two verified-cat architecture pairs were independently certified in the streamed population. Its frontier.json records paired certified alternatives. The shallower pair has sector identities beginning 4b9e515bad and fd780f50d1. Lower-qubit candidates remain in checkpoints even when they have greater depth. A generated circuit or UNKNOWN bound is not a certified Pareto point.

A post-search proof follow-up certifies a lower-qubit flagged pair: Q=168, D=200/198, QD=33600/33264, and 1536 two-qubit gates. This pair was generated by the population but was not selected for proof in its original run. A single-sector Q=48 positive has an INVALID partner and is excluded from the paired frontier. The derived combined-frontier.json retains the flagged/cat tradeoff and identifies all origins; it is not retroactively presented as the optimizer's returned frontier.

The post-discovery generic check-serial baseline uses the same verified-cat genome and Q=192, but D=136/134 and QD=26112/25728, with the same 2016 two-qubit gates. Both sectors are certified and independently replayed. Thus the discovered schedule reduces four-round depth by 40 at unchanged Q/gate count relative to this internal baseline. This is not a published reference or a matched search-policy experiment. Baseline protocol, simulations and receipts are in streamed/baseline-comparison/.

Separate surface-code controls received independently verified target-three certificates in both sectors at r=1,2,3. They are explicitly excluded from the supplied-code milestone and all population seeds. See [expanded/controls/index.json](../../results/2bga/epoch-20261105/expanded/controls/index.json) and the six complete circuit/certificate records beside it. Their purpose is physical-boundary correctness, not 2BGA performance.

## Fault diagnosis and repetition — questions 9–10

No demonstrated single-round-certified-to-repeated-invalid lineage was obtained. The principal bare templates were already invalid in the ideal extraction task; unresolved single-round proofs also cannot establish distance loss. Physical r=1 versus r>1 and ideal extraction versus physical memory change different aspects of the task and must not be conflated.

The first [[24,2,4]] X-memory witness uses two legal IZ faults on Z-check CNOT ancillas in round zero (checks 13 and 16, interaction position 3). Propagation creates an undetected logical effect after the remaining rounds and physical readout. The independently replayed witness is in the d6-k2-r4 X export. It is a spatial hook mechanism persisting through time, not evidence that the faults themselves straddle two rounds. The r=1 Z experiment also has a verified weight-three witness. All subsequent negative witnesses, including their physical operations, labels and round indices, are retained in checkpoints and export receipts.

The implementation fixes an independently reproduced producer defect: an early weight-two candidate previously hid a later weight-one witness, yielding conservative UNKNOWN at target two. The producer now gives the singleton precedence; the independent checker was retained.

## Simulation and decoders — questions 13–15

The following estimates use actual repeated Stim circuits. Each confidence interval belongs to the displayed decoder and sample count. “Any logical failure” across k observables is the reported event. The expanded search first uses 128 shots and gives selected finalists a separate 512-shot batch with a distinct seed; both batches are preserved, and this table shows the latest successful batch. This allocation is not a statistically controlled stopping rule for superiority claims.

| Run / ID / sector | Decoder | Failures / shots | Rate | 95% interval | Unmatched lookup syndromes |
|---|---|---|---|---|---|
| 2bga_D6_n24_k2_d4-r1 / 8768fc6a31 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 1 / 128 | 0.007812 | [0.00138, 0.042926] | 2 |
| 2bga_D6_n24_k2_d4-r1 / b6ca894135 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 0 / 128 | 0.0 | [0.0, 0.029137] | 1 |
| 2bga_D6_n24_k2_d4-r2 / 61316695db / X | one_mechanism_max_probability_lookup_with_zero_fallback | 3 / 128 | 0.023438 | [0.008002, 0.066644] | 11 |
| 2bga_D6_n24_k2_d4-r2 / a3169b2604 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 3 / 128 | 0.023438 | [0.008002, 0.066644] | 11 |
| 2bga_D6_n24_k4_d4-r4 / c481283014 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 9 / 128 | 0.070312 | [0.03743, 0.128235] | 22 |
| 2bga_D6_n24_k4_d4-r4 / a9d94b5b77 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 5 / 128 | 0.039062 | [0.016799, 0.088187] | 18 |
| 2bga_D9_n36_k8_d4-r4 / 6a41c409da / X | one_mechanism_max_probability_lookup_with_zero_fallback | 26 / 128 | 0.203125 | [0.142557, 0.280993] | 51 |
| 2bga_D9_n36_k8_d4-r4 / 8c990d91b3 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 30 / 128 | 0.234375 | [0.169394, 0.314835] | 48 |
| bb_n72_k12_d6-r6 / 535b23e8df / X | one_mechanism_max_probability_lookup_with_zero_fallback | 72 / 128 | 0.5625 | [0.475981, 0.645377] | 113 |
| bb_n72_k12_d6-r6 / 5b6c16d76c / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 66 / 128 | 0.515625 | [0.429862, 0.600477] | 114 |
| d6-k2-r4 / 1a5a2ed425 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 10 / 128 | 0.078125 | [0.042987, 0.137847] | 33 |
| d6-k2-r4 / 0f492e9a53 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 13 / 128 | 0.101562 | [0.060319, 0.166025] | 35 |
| expanded-d6-k2-r4 / 1a5a2ed425 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 30 / 512 | 0.058594 | [0.041348, 0.082413] | 95 |
| expanded-d6-k2-r4 / 0f492e9a53 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 37 / 512 | 0.072266 | [0.052881, 0.098021] | 106 |
| expanded-d6-k2-r4 / 7f8aa7871b / X | one_mechanism_max_probability_lookup_with_zero_fallback | 39 / 512 | 0.076172 | [0.05622, 0.102437] | 110 |
| expanded-d6-k2-r4 / d545f8dd38 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 49 / 512 | 0.095703 | [0.073149, 0.124279] | 108 |
| expanded-d6-k2-r4 / 230ef3b1b1 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 39 / 512 | 0.076172 | [0.05622, 0.102437] | 120 |
| expanded-d6-k2-r4 / a4b6eba73e / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 49 / 512 | 0.095703 | [0.073149, 0.124279] | 115 |
| expanded-d6-k2-r4 / fae95eca53 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 30 / 128 | 0.234375 | [0.169394, 0.314835] | 93 |
| expanded-d6-k2-r4 / 03ac1d4fcc / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 24 / 128 | 0.1875 | [0.129361, 0.263849] | 98 |
| expanded-d6-k2-r4 / c0d21ac1a4 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 22 / 128 | 0.171875 | [0.116331, 0.24654] | 89 |
| expanded-d6-k2-r4 / 07bb71c7f2 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 25 / 128 | 0.195312 | [0.13594, 0.272441] | 90 |
| expanded-d6-k2-r4 / 4b9e515bad / X | one_mechanism_max_probability_lookup_with_zero_fallback | 139 / 512 | 0.271484 | [0.23477, 0.311602] | 483 |
| expanded-d6-k2-r4 / fd780f50d1 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 139 / 512 | 0.271484 | [0.23477, 0.311602] | 482 |
| expanded-d6-k2-r4 / 389264fdb4 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 11 / 128 | 0.085938 | [0.048663, 0.147341] | 28 |
| expanded-d6-k2-r4 / 2081a23a70 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 2 / 128 | 0.015625 | [0.004295, 0.055181] | 21 |
| expanded-d6-k2-r4 / 2286c64717 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 11 / 128 | 0.085938 | [0.048663, 0.147341] | 41 |
| expanded-d6-k2-r4 / eab8931c40 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 5 / 128 | 0.039062 | [0.016799, 0.088187] | 18 |
| expanded-d6-k2-r4 / 66471e17cd / X | one_mechanism_max_probability_lookup_with_zero_fallback | 26 / 128 | 0.203125 | [0.142557, 0.280993] | 86 |
| expanded-d6-k2-r4 / 5b85534250 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 29 / 128 | 0.226562 | [0.162632, 0.306427] | 90 |
| expanded-d6-k2-r4 / 4a3a235bb5 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 34 / 512 | 0.066406 | [0.047907, 0.091363] | 108 |
| expanded-d6-k2-r4 / 72f7846e49 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 32 / 512 | 0.0625 | [0.044617, 0.0869] | 105 |
| expanded-d6-k2-r4 / 627388642a / X | one_mechanism_max_probability_lookup_with_zero_fallback | 29 / 128 | 0.226562 | [0.162632, 0.306427] | 104 |
| expanded-d6-k2-r4 / 2df8dca2ec / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 29 / 128 | 0.226562 | [0.162632, 0.306427] | 104 |
| expanded-d6-k2-r4 / 9ad73cc59a / X | one_mechanism_max_probability_lookup_with_zero_fallback | 13 / 128 | 0.101562 | [0.060319, 0.166025] | 30 |
| expanded-d6-k2-r4 / a3d734297c / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 9 / 128 | 0.070312 | [0.03743, 0.128235] | 28 |
| expanded-d6-k2-r4 / 08f859784a / X | one_mechanism_max_probability_lookup_with_zero_fallback | 33 / 128 | 0.257812 | [0.189869, 0.339869] | 115 |
| expanded-d6-k2-r4 / 34122f3cf6 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 31 / 128 | 0.242188 | [0.176187, 0.323211] | 123 |
| expanded-d6-k2-r4 / 1fa3ba8c32 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 133 / 512 | 0.259766 | [0.223671, 0.299438] | 474 |
| expanded-d6-k2-r4 / 50f6ff49ff / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 141 / 512 | 0.275391 | [0.238478, 0.315649] | 476 |
| streamed-d6-k2-r4 / 1a5a2ed425 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 30 / 512 | 0.058594 | [0.041348, 0.082413] | 95 |
| streamed-d6-k2-r4 / 0f492e9a53 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 37 / 512 | 0.072266 | [0.052881, 0.098021] | 106 |
| streamed-d6-k2-r4 / 7f8aa7871b / X | one_mechanism_max_probability_lookup_with_zero_fallback | 39 / 512 | 0.076172 | [0.05622, 0.102437] | 110 |
| streamed-d6-k2-r4 / d545f8dd38 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 49 / 512 | 0.095703 | [0.073149, 0.124279] | 108 |
| streamed-d6-k2-r4 / 230ef3b1b1 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 39 / 512 | 0.076172 | [0.05622, 0.102437] | 120 |
| streamed-d6-k2-r4 / a4b6eba73e / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 49 / 512 | 0.095703 | [0.073149, 0.124279] | 115 |
| streamed-d6-k2-r4 / fae95eca53 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 30 / 128 | 0.234375 | [0.169394, 0.314835] | 93 |
| streamed-d6-k2-r4 / 03ac1d4fcc / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 24 / 128 | 0.1875 | [0.129361, 0.263849] | 98 |
| streamed-d6-k2-r4 / c0d21ac1a4 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 22 / 128 | 0.171875 | [0.116331, 0.24654] | 89 |
| streamed-d6-k2-r4 / 07bb71c7f2 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 25 / 128 | 0.195312 | [0.13594, 0.272441] | 90 |
| streamed-d6-k2-r4 / 4b9e515bad / X | one_mechanism_max_probability_lookup_with_zero_fallback | 139 / 512 | 0.271484 | [0.23477, 0.311602] | 483 |
| streamed-d6-k2-r4 / fd780f50d1 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 139 / 512 | 0.271484 | [0.23477, 0.311602] | 482 |
| streamed-d6-k2-r4 / 389264fdb4 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 11 / 128 | 0.085938 | [0.048663, 0.147341] | 28 |
| streamed-d6-k2-r4 / 2081a23a70 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 2 / 128 | 0.015625 | [0.004295, 0.055181] | 21 |
| streamed-d6-k2-r4 / 2286c64717 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 11 / 128 | 0.085938 | [0.048663, 0.147341] | 41 |
| streamed-d6-k2-r4 / eab8931c40 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 5 / 128 | 0.039062 | [0.016799, 0.088187] | 18 |
| streamed-d6-k2-r4 / 66471e17cd / X | one_mechanism_max_probability_lookup_with_zero_fallback | 26 / 128 | 0.203125 | [0.142557, 0.280993] | 86 |
| streamed-d6-k2-r4 / 5b85534250 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 29 / 128 | 0.226562 | [0.162632, 0.306427] | 90 |
| streamed-d6-k2-r4 / 4a3a235bb5 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 34 / 512 | 0.066406 | [0.047907, 0.091363] | 108 |
| streamed-d6-k2-r4 / 72f7846e49 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 32 / 512 | 0.0625 | [0.044617, 0.0869] | 105 |
| streamed-d6-k2-r4 / 627388642a / X | one_mechanism_max_probability_lookup_with_zero_fallback | 29 / 128 | 0.226562 | [0.162632, 0.306427] | 104 |
| streamed-d6-k2-r4 / 2df8dca2ec / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 29 / 128 | 0.226562 | [0.162632, 0.306427] | 104 |
| streamed-d6-k2-r4 / 9ad73cc59a / X | one_mechanism_max_probability_lookup_with_zero_fallback | 13 / 128 | 0.101562 | [0.060319, 0.166025] | 30 |
| streamed-d6-k2-r4 / a3d734297c / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 9 / 128 | 0.070312 | [0.03743, 0.128235] | 28 |
| streamed-d6-k2-r4 / 08f859784a / X | one_mechanism_max_probability_lookup_with_zero_fallback | 33 / 128 | 0.257812 | [0.189869, 0.339869] | 115 |
| streamed-d6-k2-r4 / 34122f3cf6 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 31 / 128 | 0.242188 | [0.176187, 0.323211] | 123 |
| streamed-d6-k2-r4 / 1fa3ba8c32 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 133 / 512 | 0.259766 | [0.223671, 0.299438] | 474 |
| streamed-d6-k2-r4 / 50f6ff49ff / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 141 / 512 | 0.275391 | [0.238478, 0.315649] | 476 |
| baseline-comparison / 537afde732 / X | one_mechanism_max_probability_lookup_with_zero_fallback | 147 / 512 | 0.287109 | [0.249621, 0.327768] | 486 |
| baseline-comparison / 4aa88f6076 / Z | one_mechanism_max_probability_lookup_with_zero_fallback | 164 / 512 | 0.320312 | [0.281363, 0.361938] | 477 |

Matched internal-baseline simulation (p=0.001, seed 200, 512 shots each):

| Role / sector | Failures / shots | Rate | 95% interval |
|---|---|---|---|
| discovery / X | 146 / 512 | 0.285156 | [0.247762, 0.325751] |
| discovery / Z | 129 / 512 | 0.251953 | [0.216291, 0.29131] |
| generic serial baseline / X | 147 / 512 | 0.287109 | [0.249621, 0.327768] |
| generic serial baseline / Z | 164 / 512 | 0.320312 | [0.281363, 0.361938] |

These small, weak-decoder samples do not establish architecture reliability superiority. The confidence intervals and unmatched-lookup counts must be considered, not only the central rates.


Matching is attempted only through its supported correlated decomposition. Unsupported hyperedge decomposition is retained as a decoder receipt, without dropping physical faults or turning it into graphlike certification. Automatic fallback is a one-mechanism maximum-probability lookup with zero fallback, not a competitive multi-fault 2BGA decoder. Its poor performance does not establish intrinsic architecture inferiority. BP-OSD was not implemented or benchmarked. No reliability superiority is claimed.

Published references were identified but no matched executable reference experiment was reproduced. Reference comparison is NOT_RUN. Literature depth numbers cannot be compared directly to these explicit H/reset/readout counts. Relevant primary sources: [2BGA construction](https://arxiv.org/abs/2306.16400), [bivariate bicycle memory](https://www.nature.com/articles/s41586-024-07107-7), and [general syndrome compilation](https://arxiv.org/abs/2603.21499).

## Streamed proof and failed attempts

The new fixed-weight-three backend groups complete detector/logical effects, retaining every physical location domain, and scans complementary effects without storing a quadratic pair table. The independent checker reverses enumeration and uses Hall conditions to verify distinct-location feasibility. Singleton/pair prefixes remain independently checked. Correlated faults are not split into independent edges. This establishes target four after excluding all smaller weights; at higher targets it supplies only a partial bound. Dense joins can still be costly. No arbitrary-distance polynomial algorithm is claimed.

The expanded population and resume failed at a process-monitor launch race; its raw checkpoint remained RUNNING and is reported as INTERRUPTED_MONITOR_FAILURE. Monitoring attachment now runs inside a guarded loop and unexpected controller errors are durably saved. The streamed population completed both generations. Subsequent proof-only and serial-baseline attempts initially stopped at the unchanged memory reserve; initial failure logs and resumed outcomes remain separate. They are not physical invalidity evidence.

## Work, proof limits and reproducibility — questions 16–18

Counts below are per-run totals, not globally distinct architecture counts. X/Z sectors are different physical circuits. A structurally valid proposal produces both sectors; duplicate proposals can reuse tasks. CPU includes measured workers (startup and serialization included on Windows); worker wall sums overlap and must not be mistaken for experiment elapsed time. Peak RSS is the maximum worker sample, not a summed or process-tree peak. Controller times are separately retained in compute.json. Concurrent tests/audits and dynamic admission prevent treating these development timings as matched performance comparisons.

| Run | Proposals | Valid proposals | Distinct rows | Simulated rows | Proof outcomes | Worker CPU s | Worker wall sum s | Peak worker MiB | Max overlapping workers |
|---|---|---|---|---|---|---|---|---|---|
| 2bga_D6_n24_k2_d4-r1 | 8 | 1 | 2 | 2 | {'INVALID': 2} | 10.234 | 14.352 | 77.78 | 2 |
| 2bga_D6_n24_k2_d4-r2 | 8 | 1 | 2 | 2 | {'INVALID': 1, 'UNKNOWN': 1} | 14.172 | 19.729 | 78.18 | 2 |
| 2bga_D6_n24_k4_d4-r4 | 8 | 1 | 2 | 2 | {'INVALID': 1, 'UNKNOWN': 1} | 57.516 | 84.095 | 79.95 | 2 |
| 2bga_D9_n36_k8_d4-r4 | 8 | 1 | 2 | 2 | {'UNKNOWN': 2} | 57.484 | 70.507 | 80.9 | 2 |
| bb_n72_k12_d6-r6 | 8 | 1 | 2 | 2 | {'UNKNOWN': 2} | 470.406 | 505.265 | 106.89 | 2 |
| d6-k2-r4 | 8 | 1 | 2 | 2 | {'INVALID': 1, 'UNKNOWN': 1} | 20.094 | 26.674 | 79.7 | 2 |
| expanded-d6-k2-r4 | 16 | 15 | 28 | 28 | {'INVALID': 6, 'NOT_RUN': 16, 'UNKNOWN': 6} | 523.109 | 598.369 | 89.32 | 2 |
| streamed-d6-k2-r4 | 16 | 15 | 28 | 28 | {'CERTIFIED': 4, 'INVALID': 8, 'NOT_RUN': 16} | 336.078 | 498.608 | 89.35 | 2 |
| refined-2bga_D6_n24_k2_d4-r2 | 0 | 0 | 2 | 0 | {'INVALID': 2} | 1.141 | 1.505 | 34.22 | 1 |
| refined-2bga_D6_n24_k4_d4-r4 | 0 | 0 | 2 | 0 | {'CERTIFIED': 1, 'INVALID': 1} | 3.375 | 3.856 | 39.89 | 1 |
| refined-2bga_D9_n36_k8_d4-r4 | 0 | 0 | 2 | 0 | {'INVALID': 2} | 2.016 | 2.433 | 38.74 | 1 |
| refined-bb_n72_k12_d6-r6 | 0 | 0 | 2 | 0 | {'UNKNOWN': 2} | 249.391 | 257.709 | 61.1 | 1 |
| refined-d6-k2-r4 | 0 | 0 | 2 | 0 | {'INVALID': 2} | 1.469 | 1.774 | 36.12 | 1 |
| refined-population | 0 | 0 | 16 | 0 | {'CERTIFIED': 6, 'INVALID': 10} | 82.516 | 86.275 | 53.03 | 1 |
| baseline-comparison | 0 | 0 | 2 | 2 | {'CERTIFIED': 2} | 108.469 | 110.461 | 50.18 | 1 |

### Matched exact-method control

| Method / sector | Exact circuit | Status | Worker CPU s | Wall s | Peak worker MiB | Independent |
|---|---|---|---|---|---|---|
| mitm-Z | e66d5e00e79b | CERTIFIED | 33.796875 | 46.498952 | 44.539 | True |
| triples-Z | e66d5e00e79b | CERTIFIED | 0.875 | 1.068427 | 34.66 | True |
| triples-X | 5f253b9ea9bb | CERTIFIED | 1.015625 | 1.129152 | 34.883 | True |

This separate four-round distance-four surface control was never an optimizer seed. MITM-Z and triples-Z use the same exact circuit, physical model and target. One sequential invocation per method, with other audit activity on the host, supports only this measured comparison, not a universal speedup or matched whole-search advantage. Raw tasks and independently checked receipts: streamed/method-comparison/.


Across these runs the summary records 40 distinct physical identities. CPU/elapsed cutoffs were disabled for campaign workers; memory limits and finite per-proof work remained. Finite generations are prospective development measurement conditions, not a global optimizer deadline. Local execution was sufficient for these bounded experiments; no cloud resources were provisioned.

The [[72,12,6]] six-round X inventory contains 42,624 physical alternatives. Its decomposition profile reports raw separator width 97 and span width 387; incomplete state growth is retained in the progress records. The original attempts reached lower bound three; the streamed follow-up reached lower bound four in both sectors, leaving weights four and five unresolved. Target-four UNKNOWN circuits retain weight-three obligations. These are mathematical proof-work bottlenecks, not evidence of invalidity; simply removing CPU limits does not remove exponential state growth. No new temporal decomposition or unproved symmetry reduction was introduced.

Verification artifacts include [export-audit.json](../../results/2bga/epoch-20261105/export-audit.json), [expanded/export-audit.json](../../results/2bga/epoch-20261105/expanded/export-audit.json), [streamed/clean-cli.json](../../results/2bga/epoch-20261105/streamed/clean-cli.json), [streamed/independent-audit.json](../../results/2bga/epoch-20261105/streamed/independent-audit.json), [streamed/installed-positive-verification.json](../../results/2bga/epoch-20261105/streamed/installed-positive-verification.json), [final-preservation.json](../../results/2bga/epoch-20261105/final-preservation.json), [streamed-full-tests.log](../../results/2bga/epoch-20261105/streamed-full-tests.log), [interrupted-recovery-test.log](../../results/2bga/epoch-20261105/interrupted-recovery-test.log), and [artifact_manifest.json](../../results/2bga/epoch-20261105/artifact_manifest.json). The full current suite passed 155 tests in 349.87 seconds, including independent streamed-proof and monitor-race regressions. The earlier baseline passed 133 tests. Ruff and the repository's configured mypy checks passed. An unconfigured mypy attempt lacked third-party stubs; the configured invocation is retained. Clean installation used the built wheel, then executed validation, optimization, completed-checkpoint resume, list-results, export and verify-export outside the checkout. Pending-construction interruption recovery is separately tested.

The selected historical scientific records and all baseline-tracked benchmark/report/result files retain their original hashes, as enumerated in final-preservation.json. Full independent replay of the original external historical proof repository was not performed, so historical preservation is PARTIAL rather than a claim of universal revalidation. Failed build attempts (missing build backend / restricted dependency access), the corrected control setup requiring a single-round template, failed candidates and incomplete proofs are retained or recorded in the epoch. The installed package and all three scientific source snapshots support replay without the current editable checkout.

## Acceptance gates — question 19

| Gate | Requirement | Status | Evidence / unresolved requirement |
|---|---|---|---|
| A | Historical preservation | PARTIAL | Full tests and all baseline-tracked historical artifact hashes; external original proofs not fully replayed |
| B | Archive inspection | PASS | 17 original code files and archive preserved; supplied circuits/schedules absent |
| C | Algebraic validation | PASS | All 17 group/CSS/span/rank receipts; three independent distances, other distances qualified |
| D | Code-only architecture generation | PASS | Actual source-derived circuits, retained genomes and parents; no reference seeds |
| E | Low-depth optimization | PARTIAL | Certified depth improvement over generic serial baseline; published-reference competitiveness NOT_RUN |
| F | Repeated construction | PASS | Actual operations, records, reset boundaries and r=d supplied circuits |
| G | Temporal detectors | PASS | Independent signed flows, full-history checks and tamper tests |
| H | Cross-round propagation | PASS | Forward/backward inventories and independent replay controls; physical history retained |
| I | Noisy simulation | PASS | Actual repeated circuits, noise/seed/decoder/intervals recorded; no superiority claim |
| J | Decoder applicability | PARTIAL | Matching eligibility enforced; weak fallback; no competitive hypergraph decoder |
| K | Cheap screening | PASS | Complete or work-qualified singleton screening; verified negatives only |
| L | Repeated exact certification | PASS | Supplied [[24,2,4]] r=4 both sectors target4; target6 remains UNKNOWN |
| M | Positive-proof verification | PASS | Supplied positives independently checked with reverse triple enumeration and location-domain matching |
| N | Harmful witness replay | PASS | Reported negative proof records independently replayed |
| O | Single/repeated comparison | PARTIAL | r=1,2,d and ideal-template comparisons; no certified distance-loss lineage |
| P | Certified repeated frontier | PASS | Finite-population paired certified frontier; no global optimum claim |
| Q | Reference comparison | NOT_RUN | No matched executable reference reproduction |
| R | Cross-code generalization | PARTIAL | Multiple dihedral and abelian inputs plus separate surface controls; broad positive evidence absent |
| S | Circuit/schedule export | PASS | Exact reconstruction, resources, Stim and proof binding audited |
| T | Packaging/reproducibility | PASS | Source snapshots, local commits, wheel, clean CLI, resume checks and integrity manifest |

## Explicit result digest

The completed final population generated 16 proposals, accepted 15 structurally valid proposals, retained 28 distinct sector circuits, simulated 28 rows, and returned {'CERTIFIED': 4, 'INVALID': 8, 'NOT_RUN': 16}. These are stage counts, not a claim that every proposal is a distinct architecture. The smallest generated template depth in this population was 12, while the best paired certified template depth was 23. The lowest generated repeated depth was 50; it must not be substituted for the certified 96/94 pair. Follow-up proof results are separately tabulated above.


## Next scientific step — question 20

The next scientific step is a prospectively matched depth/QD comparison against an executable reference, with a validated correlated multi-fault decoder. The positive architecture uses substantial cat-verification and ancilla overhead. Preserve lower-qubit candidates while broadening proof promotion beyond the current family sample.

The supplied-code repeated-memory positive is demonstrated. The broader mission remains PARTIAL: published-reference competitiveness, larger-code complete proofs, competitive decoding, and broad positive generalization remain unresolved. The completed main run measured 795.094 controller CPU seconds versus 336.078 worker CPU seconds, exposing a controller scaling concern. Checkpoint serialization is a suspected bottleneck, not a separately measured attribution.
