# Controlled optimization protocol

This prospective campaign tests promotion policies; it does not assume that frontier promotion is superior. Phase 3's exact-distance-six Q=120 and Q=144 discoveries and adapted published reference remain external benchmarks. They are not initialization circuits, mutation guides, or supplied fault witnesses.

The executable, immutable protocol is `results/phase4/epoch-20261111/protocol-A-v1.json`. Its content digest binds the complete code input, scientific source, dependency versions, seeds, scoring rules, and experimental budgets. A frozen source copy accompanies it. Changes after outcomes require a new protocol version and separate results.

## Preservation

The original worktree and Phase 3 epoch are untouched. The preserved source is `e9bcf97c248fa36c850136f68a62df079c6b49a641b5ec471a68ab5e13606489`, at Git commit `1508d04e4abc5ca7546045869998703c47315c3f`. Phase 4 rechecked all 1,327 manifest members, reconstructed and verified eight baseline/control export bundles, and independently replayed their eight weight-six physical witnesses. The unchanged baseline passed 175 tests. Audit costs are outside the promotion comparison.

## Experiment A: fixed pools

Five generator seeds are 74011, 74023, 74039, 74051, and 74071. Each initial pool contains 100 proposals, generated with the existing code-derived `structured` generator. Generation is independent of every promotion outcome. The architecture vocabulary includes term scheduling, pooled ancillas, independent/redundant checks, flags, cats, and verified cats. The input is the preserved supplied [[72,12,6]] code. Six noisy rounds, physical preparation/readout, and the operation-local fault model are unchanged. Construction and physical fault screening use the shared scientific engines.

Deduplication uses the pair of physical circuit identities. Aliased proposals, invalid construction, verified harmful screens, and memory-censored construction remain in the pool ledger. Pools are sealed before any policy evaluation. All policies receive exactly the same identities, measured resources, and screening information. There is no cross-policy proof cache.

Policies are:

1. **Direct:** ascending proposal index.
2. **Random:** a uniform permutation, with promotion seed equal to generator seed plus 100000.
3. **Scalar resource:** ascending mean of Q/144, D/76, QD/10944, and two-qubit gates/2592, using worse-sector resources. Ties use proposal index then identity.
4. **Legacy:** within each original ten-proposal window, select two eligible pairs by the previous rotating qubit-budget stratum, then QD, index, and identity. No final sweep.
5. **Fixed-pool frontier sweep:** evaluate every screened nondominated resource point, including ties and lower-Q alternatives, by QD/index/identity; then the remaining eligible pairs in original order.

The fifth policy isolates the sweep's selection effect on an already available pool. It is **not** an end-to-end measurement of the legacy-then-final-sweep optimizer. That integrated timing belongs to Experiment B. Randomize policy execution order deterministically with seed 74000 plus the generator seed; preserve the chosen order before the first run.

Every selected sector receives 32 BP-OSD simulation shots at p=0.001, followed by the same automatic exact-certification portfolio with a 50,000,000-work proof safeguard and a 512-MiB worker ceiling. Simulation does not certify or reject a candidate. Fresh independent verification follows every positive or negative proof result. Positive adoption requires independently verified lower bound six **and** a legal weight-six physical upper witness in both sectors. Upper witnesses are searched from the new circuit's physical readout locations, without historical witness seeds. A failed upper search preserves the lower proof but leaves exact-distance adoption UNKNOWN.

## Actual compute and checkpoints

Let P be measured worker plus controller CPU for the shared, sealed pool. Each policy is charged P, then its own actual CPU. Checkpoints are **P+100, P+250, P+500, and P+1000 CPU seconds**. This formula is frozen before P is measured. Report P separately; the primary paired analysis compares policies on the same pool, never different preparation costs as though they were equal.

One policy worker is admitted at a time. CPU includes all worker attempts, interpreter startup, worker output serialization, and the controller's process CPU through recorded snapshots, including checkpoint and task-serialization work. The final controller shutdown tail is outside internal snapshots and must be measured separately or explicitly reported as unmeasured. Controller RSS is sampled at task boundaries, not represented as continuous peak measurement. Worker RSS uses the existing supervisor sampler. Record wall time, per-tier costs, and disk bytes separately. No CPU is silently imputed for interrupted tasks.

Stop dispatching another pair after the maximum finite experimental checkpoint. An admitted paired evaluation finishes; retained overshoot outcomes cannot count at earlier checkpoints. A pair becomes available only after both independent checks and the recorded durable processing. Use strict completion CPU below the checkpoint. Checkpoints not reached by a blocked run are NOT_REACHED; they are not zeros at a completed budget. Queue exhaustion is a genuine stopping outcome. Early exhaustion does not authorize extra candidates.

A hard controller interruption censors subsequent matched-compute claims because its unrecorded CPU tail is unknown; completed tasks and earlier evidence are preserved. Normal memory-admission stops preserve measured costs and resume using the same source/protocol identity. The normal optimizer receives no global runtime cutoff. Worker CPU/wall limits are explicitly `None`; memory safeguards, cancellation, and proof-work limits remain.

## Outcomes and analysis

The frozen normalized four-objective hypervolume reference is Q=200, D=1024, QD=204800, two-qubit gates=20000. Compute the exact union of dominated boxes, retaining physical ties and all certified alternatives even outside that reference box. QD is derived from Q and D; report the individual objectives so the redundant dimension does not hide the tradeoff.

Report per-seed frontiers and paired hypervolume differences at every matched checkpoint, paired wins/ties/losses, medians, and all raw values. With five seeds, use an exact two-sided paired sign-randomization test and descriptive uncertainty; do not claim an advantage from one favorable seed. Prespecify the primary contrast as frontier versus legacy at P+1000. Other contrasts/checkpoints are descriptive, with no unadjusted multiple-comparison significance claims.

Missed opportunities are exact pool identities independently certified by another completed policy or a separately costed post-hoc audit. Unproven promising resources are not missed certified winners. Post-hoc audit outcomes never guide the compared policy runs. Report time to first certified pair and first strict resource improvement over external Phase 3 benchmarks; absence is right-censored, not an invented duration.

## Subsequent stages, frozen before their outcomes

Experiment B will compare the same five allocation policies with the same code-derived hybrid generator, five seeds, ten-proposal windows, 100-proposal initial goals, and total CPU checkpoints 500, 1000, and 2000 seconds. Its frontier arm must preserve the actual legacy-window selection followed by the integrated final sweep. It must not substitute Experiment A's sweep-first ordering. Generation and promotion random streams remain separate. A separate executable protocol must bind the completed adaptive implementation before running it.

Population scaling next generates a 1000-proposal pool using seed 74011, with the same five fixed-pool policies at P+1000, P+2500, and P+5000. This is the primary larger-population scale. Expansion to 10000 proposals requires at least one newly certified resource tuple beyond the 100-proposal pool, at least 10% additional distinct physical pairs in the last 100 proposals, and sufficient measured local memory/disk. Failure to meet these conditions is reported, not silently omitted.

Generation comparisons hold promotion fixed and compare random, structured, and witness-guided hybrid generation at matched actual CPU, separately from allocation-policy effects. Transfer cases are the supplied `2bga_D6_n24_k2_d4` and `2bga_D9_n36_k8_d4`, with requested extraction target four and six noisy rounds; their algebraic labels are not themselves new independent distance proofs. Use the same five seeds and initial 100 proposals, with total CPU checkpoints 500/1000/2000 for adaptive experiments. Do not tune based on transfer outcomes.

For reliability, evaluate the frozen historical baseline, Q120, shallow, reference, and any distinct adopted new frontier representatives at p=0.001 and 0.003, **1024 shots per sector per noise point**, with the same validated BP-OSD configuration. Derive independent sampler seeds from the exact circuit identity, noise, sector, and master seed 374011. Do not infer physical coupling from matching numeric seeds. Report binomial uncertainty and decoder-conditional failure rates, including all zero-failure intervals. Reliability is a separate experiment and its CPU is not charged to promotion quality.

Policy F is NOT_RUN: a validated cost/progress/resource predictor has not been established. No cloud resources are authorized or needed to begin this campaign. Every stage retains negative, UNKNOWN, interrupted, and censored outcomes. Implementation and test success alone cannot pass a scientific acceptance gate.
