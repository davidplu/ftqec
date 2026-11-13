# Controlled optimization: interim evidence

This is an interim research record, not the final Phase 4 report. The fixed-pool campaign is running. Its primary matched-seed contrast is incomplete, so no promotion-policy superiority is established. The snapshots below describe the first completed arm; later results must be read from their own immutable receipts.

Checkpoint interpretation follows [analysis amendment 1](PHASE4_ANALYSIS_AMENDMENT_1.md): an exhausted queue does not count as consumption of an unreached CPU checkpoint. Earlier raw coverage fields and interim analyses remain preserved; corrected analyses retain both raw and measured coverage.

## Preserved baseline and corrected execution

The preservation audit checked all 1,327 historical manifest members, eight exported baseline/control circuits, and eight physical weight-six upper witnesses. The preserved baseline passed 175 tests. The corrected experimental implementation passed 189 tests. Raw records are in `results/phase4/epoch-20261111/phase3-integrity.json`, `baseline-replays.json`, `baseline-upper-replays.json`, `baseline-tests.log`, and `results/phase4/epoch-20261111-v2/adapter-fix-full-tests.log`.

Protocol versions remain separate. Version 1 stopped after repeated progress accounting decompressed large circuit payloads; scalar SQL accounting replaced that path. Version 2 completed its first pool, but a certificate adapter used the wrong upper-witness field for the row-relaxation checker. Those proof packets were rejected, not adopted. Version 3 corrected the contract and required fresh full proofs and independent checks. It retains the complete source-bound construction pool and charges its original CPU equally to every policy. No promotion answers were imported.

Current scientific source: `e882794750da70f76ce6e7163aa19f42d48a09b1ad743a31c00d0f915e5a8557`.

Current fixed-pool protocol: `c2c08ca340d6876a900da2c4a56aac1151ea590f6c7ddeba1a5e7378071cdbf3`.

The current wheel was installed into a new environment and passed public optimize, resume, export, and verify-export checks. Both full-size Q=84 exports also passed public reconstruction, Stim compatibility, resource recomputation, certificate binding, and positive proof replay. These post-hoc export checks have separate receipts in `results/phase4/epoch-20261112-v3/package-validation.json`; they are not credited as controlled-policy outcomes. The wheel SHA-256 is `cf645847bb1a2a2bd3bc015c3d3d7d7ccecd2ac6425601ebc091b1e8f95acdfb`.

## First completed randomized-policy arm

Seed 74011's pool contains 100 proposals, 97 compiled paired architectures, and three memory-censored constructions. These are not 100 distinct certified circuits. Shared measured preparation cost is 2,073.28125 CPU seconds. The randomized policy evaluated 11 pairs, including a final admitted evaluation that finished after its last checkpoint. Its 22 sector evaluations yielded seven independently certified sectors and 15 independently verified INVALID sectors. Only two complete X/Z pairs qualified for adoption; unpaired positive sectors are not paired architectures.

| Newly evaluated pair | Q | X depth | Z depth | X QD | Z QD | Two-qubit gates per sector | Exact extraction distance |
|---|---:|---:|---:|---:|---:|---:|---:|
| Lower-qubit alternative | 84 | 328 | 326 | 27,552 | 27,384 | 2,592 | 6 in both sectors |
| Historical resource tuple rediscovered | 144 | 76 | 74 | 10,944 | 10,656 | 2,592 | 6 in both sectors |

The 84-qubit pair expands the lower-qubit choices relative to the preserved Q=120/Q=144 frontier, at much greater depth and QD. It does not dominate the shallow reference. No global optimum or reliability advantage follows. The Q=144 pair reproduces a historical resource tuple; it is not a resource record.

The Q=84 identities are X `5a5f548aaa15403b67dbe2e0a4f43677902069eb6c8afaf4a66b9b472233d423` and Z `4ccf3b05b76fe64173bfea20b0c9263ce0f3686015674872e61fe2b67434ba8d`. Their availability was recorded at total algorithm CPU 2,218.25 seconds. The second pair became available at 2,340.171875 seconds. Both include charged pool preparation and both-sector independent verification.

The completed randomized arm consumed 939.859375 worker CPU seconds and 61.109375 controller CPU seconds, with measured elapsed time 1,008.2064942999277 seconds. Its external measurement driver consumed another 1.859375 CPU seconds, separately reported. Worker CPU divides into simulation 392.1875, certification 438.234375, and independent verification 109.4375 seconds. Shared preparation is additional for each policy comparison but counted once when totaling actual campaign execution. Summed worker wall times are not experiment elapsed time. Sampled process peaks are not simultaneous aggregate memory measurements.

Evidence: `results/phase4/epoch-20261112-v3/fixed-pool/seed-74011/{pool,random}/`, including `comparison.json`, `population.sqlite`, proof artifacts, and whole-controller receipts. `interim-analysis-001.json` records the first completed arm and explicitly lists 24 missing comparison arms. It contains zero completed frontier-versus-legacy seed pairs. The direct arm was still running when this note was prepared. The first randomized arm partly overlapped final regression testing on the shared laptop; execution was not on an otherwise isolated host. Whole-process CPU remains measured; wall-time interpretation must retain that limitation.

## Remaining scientific obligations

### Three completed arms of the first seed

The current corrected analysis is `interim-analysis-004.json`. At the common checkpoint of preparation CPU plus 1,000 seconds (3,073.28125 total algorithm CPU seconds for this pool):

| Policy | Certified paired frontier: (Q, worse D, worse QD) | Frozen hypervolume | Actual policy CPU through exit, excluding shared preparation |
|---|---|---:|---:|
| Direct | (144, 82, 11,808) | 0.211269699375 | 1,026.203125 |
| Random | (84, 328, 27,552); (144, 76, 10,944) | 0.36717061125 | 1,000.96875 |
| Frontier | (144, 64, 9,216) | 0.2181984 | 4,056.296875 |

Every listed circuit uses 2,592 two-qubit gates per sector. The reference point remains Q=200, D=1,024, QD=204,800, gates=20,000. These are separate frontier tuples; the minimum Q and minimum D need not occur in one circuit. Random's larger scalar hypervolume in this seed does not mean it dominates frontier's shallower design in every resource.

The frontier arm's admitted Q=78 pair caused substantial overshoot. Its X and Z certification attempts returned UNKNOWN/MEMORY_LIMIT after 1,751.34375 and 1,622.0 worker CPU seconds respectively. Both outcomes are retained; neither yields a paired certificate. Results finishing after the checkpoint do not count at that checkpoint. The frontier arm completed ten pair evaluations with five certified sectors, nine INVALID sectors, and six UNKNOWN sectors; only one complete pair qualified. Actual arm elapsed time was 3,989.9518131001387 seconds. Raw evidence includes `Q78-X-censored-certification.json`, `Q78-Z-certification-outcome.json`, and the whole-controller receipt.

The scalar resource-ranked arm was running at this update. Legacy and the other seeds remained incomplete. No matched frontier-versus-legacy seed comparison was yet complete, and there is no overall policy-superiority conclusion.

### Post-hoc selection diagnosis

The frozen seed-74011 ranking placed the certified Q=84 pair first in random order, 24th in direct order, 33rd in frontier order, and outside the legacy selection. Its sole raw-resource dominator was pair `32b4577c6e6fa981a93065ba5d763fb08d6956cdd4243a347ea6318e58302d87`, with Q=84, worse-sector D=286, QD=24,024, and 2,160 two-qubit gates. Both sectors of that apparently cheaper pair were subsequently independently verified INVALID by the frontier arm.

This explains a specific selection mechanism: static resource dominance by a physically invalid candidate postponed a valid lower-qubit alternative. The fixed-pool ordering is not refreshed after verification. The valid alternative remains eligible later in the queue; it is not permanently rejected. Refreshing after a verified invalid result is a hypothesis for a separate prospective comparison, not an improvement already tested here. No ranking or budget was changed after observing this case.

The frontier arm independently rediscovered a Q=144, worse-sector D=64, QD=9,216 pair before this diagnosis. Its later long proof concerned an unproved Q=78, D=12,964, QD=1,011,192, 6,912-two-qubit-gate alternative. These raw resources do not establish fault tolerance. They illustrate why retaining low-qubit alternatives can incur substantial proof cost even outside the frozen hypervolume reference box.

Raw records: `seed-74011-rank-diagnostic.json`, `seed-74011-resource-diagnostic.json`, and `seed-74011-dominance-outcome-diagnostic.json` under the current epoch. These diagnostics are separate from policy decisions and do not supply outcomes to another policy.

The invalid dominator's retained physical witnesses have weight four in X and five in Z; both were independently replayed. `seed-74011-dominance-negative-evidence.json` contains the original certificates and verification receipts. Extracting these records is not an additional proof execution.

### Certification-cost diagnosis

A short profile of the long Q=78 proof found the worker in `span_decomposition.decompose`, called by the quotient-decomposition backend. The source repeatedly scores every remaining location to select the next elimination step, rebuilding detector-support sets. For a component with m locations, that loop performs m(m+1)/2 score evaluations; this is preprocessing before the dynamic-programming work counter is initialized. This identifies a polynomial preprocessing bottleneck in the sampled window, not evidence that the exact search itself had become exponential.

The ten-second, ten-samples-per-second nonblocking observation retained 99 samples, 94 with a decomposition frame. Some stacks were incomplete. This is a brief diagnostic, not a complete runtime decomposition or a measured optimization speedup. An equivalence-tested bitset implementation of the same ordering is a justified future engineering experiment. No backend was changed in the running comparison.

Retained evidence: `long-proof-stack-001.txt`, `long-proof-profile-001.txt`, its log, and `long-proof-profile-001-provenance.json`. The profiler was installed separately from the pinned research environment. See the [profiler's documentation](https://github.com/benfred/py-spy) for its external sampling mechanism and nonblocking limitations. Sampling overhead was not independently measured; the shared-laptop and diagnostic-instrumentation qualification remains part of the timing evidence.

The Q=78 X-sector attempt subsequently returned UNKNOWN/MEMORY_LIMIT after 1,751.34375 worker CPU seconds and 1,761.388229599921 elapsed worker seconds. `Q78-X-censored-certification.json` retains the completed task receipt. No positive proof or new lower bound is adopted from that terminated attempt. The earlier profile identifies a sampled preprocessing hotspot; it does not identify the precise allocation that eventually crossed the process-memory safeguard. The admitted Z-sector attempt was still running when this update was written.

The larger reliability study has a prepared catalogue of the eight preserved control sectors in `results/phase4/planned-reliability/controls.json`. Their original proof sources and lower/upper verification receipts remain attached. This is input preparation only: final discovery selection and the complete 1024-shot sampling manifest are not yet frozen, and no larger reliability batches have run.

### Outstanding experiments

1. Complete all five policies on all five fixed-pool seeds and analyze the prespecified frontier-versus-legacy contrast.
2. Execute the separately frozen adaptive comparison, preserving the actual end-of-population sweep timing.
3. Execute the 1,000-proposal scale stage. Cross-population claims require matched total CPU, including different construction costs.
4. Complete generation-policy and two-code transfer experiments.
5. Freeze finalist selection and run the larger BP-OSD reliability study with uncertainty.
6. Reconstruct and independently verify every adopted export, close the compute ledger, and produce the full report and final integrity manifest.

The adaptive and scaling plans are frozen, not completed experiments. Missing results are NOT_RUN or incomplete, never evidence of equivalence or failure. Policy F remains NOT_RUN because a validated cost predictor was not established. No billable cloud resources have been provisioned, and no Phase 4 changes have been pushed publicly.

See [execution and resume instructions](../benchmarks/phase4/README.md). The normal optimizer has no global CPU timeout. Finite experimental comparison checkpoints, memory safeguards, and proof-work safeguards remain distinct controls.
