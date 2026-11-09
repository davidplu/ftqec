# FTQEC: mechanism reduction and repeated-memory distance certification

## Principal finding

The preserved six-round [[72,12,6]] FTQEC circuits have **exact circuit distance six in both declared memory sectors**. Each lower bound excludes all harmful faults of weights one through five under the unchanged operation-local physical model. Separate legal six-location witnesses attain the bound. Independent forward-inventory reconstruction, a different exhaustive search algorithm, and physical witness replay support this result. This is not a claim about arbitrary-input quantum-memory fidelity, implicit storage noise, routed hardware, or logical error rates.

The X circuit is `11f144ae49d0b328fda6c4f00f22d531f35b2ac5cc65ca02c1e4692f17b03585`; the Z circuit is `17fd73a1ee9064172e74e9298154c825f4ccd2f642233d38fd479fbce0aa579d`. They are the preserved autonomous Phase 2 circuits, not the authors' circuits or the separately adapted reference schedule. Their complete circuits, inventories, reductions, proofs, physical witnesses, and fresh replay receipts are in `sector-revision/previous-X/` and `sector-revision/previous-Z/`.

The overall integration mission is **PARTIAL**, despite meeting its main distance-six milestone. The accelerated upstream kernels are not ported, automatic portfolio selection is unchanged, and a broad matched-compute optimizer benefit is not established.

## Sources and compatibility

Authoritative sources: [paper and supplement](https://arxiv.org/pdf/2611.08247) and [upstream implementation](https://github.com/Fanerst/tropidist), audited at `b03ec2d4077f287f89f97b5c2c16ce5ce17c2c58` (MIT). The complete paper is retained as `paper.pdf`/`paper.txt`. See `docs/TROPIDIST_INTEGRATION.md` for the reduction proof and algorithm contracts.

FTQEC minimizes the number of distinct faulty physical locations with zero detector XOR and nonzero logical XOR. The paper minimizes unit-cost mechanism supports. These minima agree only after checking complete allowed Pauli groups and binary measurement flips, using Lemma 2.2. Physical alternatives, locations, operation origins, detector and logical signatures, boundaries, and correlated two-qubit effects remain in the original inventory. Mechanism merging changes the feasible representation, but the two explicit inequalities in the integration guide prove equality of minimum harmful weight. It is not a probability-preserving transformation.

Time collapse is an explicit detector-row parity map, followed by dropping opposite-memory-sector check constraints. The logical vector is retained. Any harmful full support maps to a reduced harmful support of no greater weight, so the reduced minimum is a lower bound. No equality or all-round-count theorem is assumed. The full fault universe includes noisy product preparation, syndrome rounds, physical readout, and whatever idle locations are explicitly present. These primary circuits declare no implicit idle faults.

For these FTQEC circuits, the final reduction has 36 detector coordinates and 180 joint mechanisms per sector. Complete enumeration found no harmful support through weight five; independent canonical branching confirmed that exclusion. Unlike the authors' BB72 example, no extra minimum-support lifting exclusion was needed to reach six. Witness lifting remains implemented and tested for cases where it is needed.

## Algorithm reproduction

Unmodified upstream NumPy rank DP agreed with exhaustive oracles on 300 stored random problems (seed 61108247; `upstream-numpy.json`). The authors' unmodified `tests/independent_bb72.py` reproduced collapsed distance five and excluded every weight-five lift, then found real weight-six witnesses in both authors' sectors (`upstream-independent-bb72.log`). Those results do not certify FTQEC's different circuits.

The accelerated upstream suite could not start here: its pytest fixture imports the Unix-only `resource` module. No C/OpenMP compiler was on PATH and WSL was not installed. The checkout initially hit Windows path-length limits; restoring with Git long-path support recovered a clean, unchanged upstream checkout. The full accelerated suite and published server-scale benchmark matrix were not reproduced. No published server timings are presented as local measurements.

FTQEC's new producer uses exact pair/triple joins through weight five; its checker uses canonical residual branching. The lifting producer uses a meet-in-the-middle join, while the checker uses layered syndrome sets. This is a transparent Python implementation inspired by the paper, not an upstream accelerated-kernel port. The rank-based DP kernel is reproduced separately, not used to issue the new FTQEC certificates.

## Historical controls and primary experiment

Values below come from `sector-revision/summary.json`. CPU and wall are seconds; peak_rss is bytes, measured by the existing isolated worker supervisor. Each task retained its memory protection and had no CPU or wall-clock cutoff. Subsequent fresh replays are additional work, recorded separately in `fresh-replay-summary.json`.

| name | status | lower_bound | upper_bound | projected_mechanisms | cpu | wall | peak_rss |
|---|---|---|---|---|---|---|---|
| surface3 | CERTIFIED | 3 | 3 | 359 | 0.734375 | 0.9306244000326842 | 41472000 |
| surface3-invalid-target5 | INVALID | 3 | 3 | 359 | 0.6875 | 0.896076500066556 | 42299392 |
| shor25 | CERTIFIED | 5 | 5 | 619 | 51.046875 | 51.88237680005841 | 76320768 |
| cat24-X | CERTIFIED | 4 | 4 | 432 | 6.125 | 6.539955600048415 | 76247040 |
| cat24-Z | CERTIFIED | 4 | 4 | 420 | 7.53125 | 8.00068270007614 | 74424320 |
| previous-X | CERTIFIED | 6 | None | 180 | 33.140625 | 33.706253699958324 | 85913600 |
| previous-Z | CERTIFIED | 6 | None | 180 | 31.734375 | 32.53745850000996 | 85004288 |

The `upper_bound=None` entries for the two primary producer runs are supplemented by `weight6-witness.json` and `fresh-replay.json` in each sector directory, establishing exact distance six. The surface3-invalid-target5 control is intentionally INVALID at exact distance three. Shor25 agrees at exact distance five; both verified-cat24 memory sectors agree at exact distance four.

The initial all-sector reduction stopped at the pair-table safeguard for surface5, cat24 X/Z, and both primary circuits (`controls/`, `primary/`). Those attempts remain UNKNOWN, not invalid. Surface5 remains an incomplete new-method control. These failed attempts were retained, not overwritten by the sector revision.

## Existing-method comparison

`matched/protocol` is encoded in each packet and `run_matched.py`: same exact X circuit and target six, one worker, 512 MiB worker ceiling, no time limit, 200,000 counted proof-work operations for each existing backend. The new reduction experiment used 50,000,000 counted operations. Operation units differ between algorithms, so this is an obligation/completion comparison, **not a matched-compute speedup measurement**. All methods receive the complete physical model. SAT's missing bound below means worker interruption before a verified result, not a harmful witness.

| method | status | lower_bound | upper_bound | cpu | wall | peak_rss |
|---|---|---|---|---|---|---|
| graph | UNKNOWN | 3 | None | 9.71875 | 10.115523900021799 | 49520640 |
| mitm | UNKNOWN | 3 | None | 29.09375 | 32.74111990001984 | 64020480 |
| dp | UNKNOWN | 3 | None | 8.140625 | 8.358895300072618 | 52674560 |
| sat | UNKNOWN | None | None | 6.34375 | 6.6507252000737935 | 536920064 |
| decomposition | UNKNOWN | 3 | None | 163.546875 | 165.26126639998984 | 105508864 |
| triples | UNKNOWN | 3 | None | 5.703125 | 6.016301000025123 | 56459264 |

The historical independent lower bound four is preserved in the exact-circuit-bound `primary/*/historical-packet.json`; the smaller work allowance in this comparison does not revoke it. The new lower bound six strengthens that evidence. No method is declared universally fastest from these unequal completed obligations.

## Additional supplied codes

The scaling pilot prospectively used the supplied target as round count, unchanged explicit-operation faults, 512 MiB workers, and 2,000,000 counted operations. Supplied algebraic distance labels remain claims. The first shuffled interleaving failed signed noiseless-flow validation for all six inputs (`larger/summary.json`). A generic all-X-then-all-Z order repaired that structural issue without a successful reference seed; its results are below. Structural invalidity is separate from physical harmful-fault invalidity.

| name | basis | target | status | lower_bound | upper_bound | reason | cpu | wall | peak_rss |
|---|---|---|---|---|---|---|---|---|---|
| 2bga_D9_n36_k8_d4 | X | 4 | INVALID | 3 | 3 | None | 2.796875 | 3.2560247000074014 | 52744192 |
| 2bga_D9_n36_k8_d4 | Z | 4 | INVALID | 3 | 3 | None | 2.625 | 2.9915499999187887 | 50880512 |
| 2bga_D12_n48_k4_d6 | X | 6 | INVALID | 5 | 5 | None | 16.265625 | 16.76441479998175 | 71892992 |
| 2bga_D12_n48_k4_d6 | Z | 6 | UNKNOWN | 4 | 4 | None | 12.25 | 12.706062400015071 | 71159808 |
| 2bga_D21_n84_k4_d10 | X | 10 | UNKNOWN | 1 | None | Independent branch-check work limit | 30.84375 | 31.453237400040962 | 165732352 |
| 2bga_D21_n84_k4_d10 | Z | 10 | UNKNOWN | 1 | None | Independent branch-check work limit | 31.96875 | 33.333328400040045 | 171892736 |
| bb_n90_k8_d10 | X | 10 | UNKNOWN | 1 | None | Independent branch-check work limit | 35.390625 | 36.00894830003381 | 188076032 |
| bb_n90_k8_d10 | Z | 10 | UNKNOWN | 1 | None | Independent branch-check work limit | 35.640625 | 36.28872680000495 | 184864768 |
| bb_n108_k8_d10 | X | 10 | UNKNOWN | 1 | None | Triple-scan work limit | 42.09375 | 42.88098210003227 | 211927040 |
| bb_n108_k8_d10 | Z | 10 | UNKNOWN | 1 | None | Triple-scan work limit | 39.25 | 39.94180220004637 | 220647424 |
| bb_n144_k12_d12 | X | 12 | UNKNOWN | 1 | None | Triple-scan work limit | 95.9375 | 97.35452559997793 | 410079232 |
| bb_n144_k12_d12 | Z | 12 | UNKNOWN | 1 | None | Triple-scan work limit | 87.421875 | 88.6188664000947 | 376659968 |

Preserve the raw UNKNOWN entry for the [[48,4,6]] Z run: its wrapper requested extra verification beyond the required lower bound and exhausted its work allowance despite a replayed weight-four counterexample. A separate correction/replay receipt, when present, establishes the negative target conclusion without overwriting that record. Larger UNKNOWN results do not establish their supplied code or extraction distances. The corrected [[48,4,6]] Z run is independently INVALID with exact distance four (`corrected-negative/packet.json`). Exponential branch growth, not graph eligibility, limits these attempts.

## Answers to the required research questions

1. **Problem solved:** minimum support under binary zero-syndrome constraints and a nonzero logical label; block-weight variants cover Pauli code distance. Dense rank DP solves nonzero logical-row queries via tropical minimum cost; sparse DP and weight-bounded search solve exhaustive threshold obligations.
2. **Comparison with FTQEC:** equal minimum faulty-location weight only under audited completeness and composition closure; not identical feasible configurations or probabilities.
3. **Algorithms reproduced:** unmodified NumPy dense rank DP on random exhaustive oracles; authors' independent BB72 pair/triple and lifting script; new independently checked FTQEC pair/triple reduction path. Accelerated sparse DP/search not reproduced.
4. **Published benchmarks reproduced:** authors' six-round BB72 X/Z independent derivation; not the full benchmark matrix.
5. **Unmodified compatibility:** the independent Python paths ran unmodified. The full upstream test/build path is blocked by Unix `resource` and the absent compatible C/OpenMP environment.
6. **Transformations:** lossless physical inventory IR; audited joint-signature quotient; explicit time-row parity projection; memory-sector row relaxation; mapped physical witness replay.
7. **Soundness:** minimum equality follows Lemma 2.2's two inequalities after closure checks. Row projection gives a lower bound only. Minimum-level lifting is exhaustive and separately checked where invoked.
8. **Historical certificate agreement:** exact surface3, Shor25, and cat24 X/Z agreement; higher surface control remained UNKNOWN at a safeguard.
9. **Invalid controls:** known distance-three circuit at target five rejected; scaling also found actual legal harmful witnesses.
10. **Time collapse:** yes as a fixed-circuit lower-bound projection. A theorem for arbitrary round counts was not assumed.
11. **Six-round BB72:** yes, both exact circuit identities, both declared Pauli memory sectors.
12. **Lower bound:** six, excluding every harmful physical configuration of weights one through five.
13. **Witnesses:** matching weight-six witnesses in both primary sectors; lower-than-target witnesses in scaling cases. All accepted witnesses are replayed in the original physical circuit.
14. **Fastest method:** no valid overall speed ranking from unmatched completed obligations. The new method completed a proof that the comparison attempts did not.
15. **Memory:** measured per-worker peaks appear in tables and packets; they do not include all controller, operating-system, or unrelated-process memory. SAT was memory-censored.
16. **Independent verification:** forward instead of backward fault propagation, canonical branching instead of producer joins, full physical witness replay, and standalone evidence replay. Portable public recipes reconstruct their own inventories.
17. **Additional codes:** the six supplied 36-, 48-, 84-, 90-, 108-, and 144-qubit inputs were attempted; the 24- and 72-qubit cases appear as controls/primary. Exact outcomes and construction failures are retained.
18. **Scaling:** row projection sharply reduces repeated-memory columns, but canonical branching can still exhaust work on larger projected problems. This is not universal efficient certification.
19. **Optimizer impact:** the public optimizer accepts the new opt-in backend; a finite integration pilot, if present below, tests execution and resume. A broad multi-seed, matched-compute improvement in certified Pareto quality is not established.
20. **Unresolved:** accelerated upstream build/portability, automatic cost-based portfolio selection, stronger resumable proof search on larger instances, and a substantive matched-compute architecture-search comparison. The next justified step is a substantive multi-seed, prospectively matched optimizer campaign using the validated reduction, with complete CPU accounting and independent frontier replay.

## Acceptance gates

PASS means the stated demonstrated scope, not a stronger untested interpretation.

| Gate | Status | Evidence |
|---|---|---|
| A | PASS | Complete paper and source audit; retained PDF, pinned upstream and integration guide. |
| B | PASS | Closure-tested minimum-weight equivalence; no probability equivalence claimed. |
| C | PARTIAL | Independent BB72 and NumPy DP reproduced; accelerated upstream suite blocked on this Windows environment. |
| D | PASS | Versioned full physical inventory, forward/backward validation, collision composition and tampering tests. |
| E | PARTIAL | Surface3 reproduced; surface5 new-method attempt censored. |
| F | PASS | Shor25 exact five, physical upper and independent replay. |
| G | PASS | Both four-round verified-cat24 sectors exact four. |
| H | PASS | Known invalid target rejected with physical replay. |
| I | PASS | Fixed-circuit lower-bound projection proved; no all-round equivalence claim. |
| J | PASS | Reduction and provenance mapping executed on actual physical-memory circuits. |
| K | PASS | Both preserved six-round BB72 circuits attempted and completed. |
| L | PASS | Independent lower bound six and physical upper six in each sector. |
| M | PARTIAL | Same-input method measurements retained; equal completed-obligation timing and accelerated rank-DP comparison incomplete. |
| N | PASS | Independent forward/canonical proof replay and portable recipe verifier. |
| O | PASS | Accepted physical witnesses replayed with location exclusivity. |
| P | PARTIAL | Explicit public time_collapse method and shared worker integration; automatic selector unchanged. |
| Q | PARTIAL | Supplied scaling inputs attempted; several proofs remain UNKNOWN. |
| R | PARTIAL | Finite paired integration pilot only; broad matched-compute optimizer benefit not established. |
| S | PASS | Historical Nov5 manifest audit and unchanged tracked Phase2 source; no old results overwritten. |
| T | PARTIAL | Raw evidence, source archives, scripts, package and report retained; accelerated upstream and broad optimizer reproduction remain incomplete. |

## Delivery and reproduction

Run the scientific suite with `python -m pytest -q`. Public certification uses `ftqec certify circuit.json --target 6 --proof-method time_collapse --proof-work 50000000 --output NEW_DIRECTORY`. The task-worker route supplies process-level memory supervision. Optimizer runs retain checkpoint/resume and explicit cancellation; the experiment scripts disable CPU and wall limits while retaining memory and counted-work safeguards.

Use the source archive and wheel matching an evidence bundle's source identity for strict export verification. `exports-v2/X` and `exports-v2/Z` are recertification bundles of preserved circuits, not newly discovered optimizer candidates. The first export attempt retained a dependent check list as its input-code basis; verification rejected it. The v2 records use the original independent input-code basis and preserve the exact extraction circuit. Both failed and corrected bundles remain for audit.

`artifact_manifest.json` hashes the evidence package; runtime environments, caches, and the manifest itself are explicitly excluded. `delivery.json` records source identity, Git source commit, package identities, test logs and verification locations. No cloud resources were provisioned and no changes were pushed publicly.

### Primary physical resources

| sector | Q | D | QD | two_q_gates |
|---|---|---|---|---|
| X | 144 | 76 | 10944 | 2592 |
| Z | 144 | 74 | 10656 | 2592 |
These resources are recomputed from the exported schedules, not new architecture improvements.

### Source identities

```json
{
  "branch": "codex/tropidist-integration",
  "export_evidence_source": "01a8552560eec5c209413b7b84bab4281bd1942ed25eb7233e26b18f423b0938",
  "export_matching_package": "package/ftqec-0.1.0-py3-none-any.whl",
  "export_source_archive": "source-portfolio.zip",
  "exports": [
    "exports-v2/X",
    "exports-v2/Z"
  ],
  "final_package": "package-final/ftqec-0.1.0-py3-none-any.whl",
  "final_source_archive": "source-final.zip",
  "fresh_primary_replay": "fresh-replay-summary.json",
  "historical_hash_audit": "historical-hash-audit.json",
  "primary_evidence_source": "78cf97e565a09a09fafb0e7181bf793dfe6b7cb011ea37c104e87e2e4e58b652",
  "publication": "local only; no push",
  "qualifications": [
    "Source archives preserve exact bytes; verify-export requires matching scientific source identity.",
    "New research findings do not establish an optimizer frontier improvement."
  ],
  "source_commit": "0baac6eb76e8411b929d03904d137da28004c14f",
  "source_identity": "910aa59c950c66fc8ac54c712517587a688564fe152d9d70a6d42b824a005ad3",
  "test_logs": [
    "full-tests.log",
    "final-tests.log"
  ],
  "upstream_commit": "b03ec2d4077f287f89f97b5c2c16ce5ce17c2c58"
}
```

### Optimizer pilot

| method | status | generated | compiled | simulated | certified | invalid | unknown | worker_cpu | controller_cpu | wall | resume_reused_tasks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| triples | REQUESTED_GENERATIONS_COMPLETED | 2 | 4 | 4 | 0 | 2 | 0 | 10.734375 | 5.15625 | 18.084680099971592 | True |
| time_collapse | REQUESTED_GENERATIONS_COMPLETED | 2 | 4 | 4 | 0 | 2 | 0 | 16.640625 | 6.890625 | 26.730685299960896 | True |

### Pilot compute checkpoints

| method | worker_cpu_checkpoint | checkpoint_reached | completed_tasks | certified | invalid |
|---|---|---|---|---|---|
| triples | 10 | True | 14 | 0 | 2 |
| triples | 30 | False | 16 | 0 | 4 |
| triples | 60 | False | 16 | 0 | 4 |
| time_collapse | 10 | True | 12 | 0 | 0 |
| time_collapse | 30 | False | 16 | 0 | 2 |
| time_collapse | 60 | False | 16 | 0 | 2 |
At the shared 10-second worker-CPU checkpoint neither arm had a certified circuit. The 30- and 60-second checkpoints were not reached and are NOT_RUN comparisons. Controller CPU differs and is reported separately. No search advantage was demonstrated.

### Final verification

........................................................................ [ 42%]
........................................................................ [ 85%]
........................                                                 [100%]
168 passed in 312.37s (0:05:12)

Corrected 48-qubit Z replay: {'status': 'INVALID', 'lower_bound': 4, 'upper_bound': 4, 'independent': {'lower_bound': 4, 'method': 'forward inventory/canonical branching/layered lifting', 'verified': True}, 'unresolved': None}

Complete X/Z bundles passed reconstruction, Stim, resource and positive-proof replay in the clean installed environment; see verify-export-v2-X.log and verify-export-v2-Z.log.

### Historical integrity audit

```json
{
  "historical_manifest": "C:\\Users\\david\\qLDPC synthesizer\\ftqec-user-test-20261105\\results\\2bga\\epoch-20261105\\artifact_manifest.json",
  "checked": 1521,
  "bytes": 1490218674,
  "mismatches": [],
  "wall": 24.225616400013678
}
```
