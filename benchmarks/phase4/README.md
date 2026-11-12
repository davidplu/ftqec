# Controlled optimization experiments

These scripts compare promotion policies using measured CPU and independently verified paired circuits. A running campaign is not a completed scientific comparison. Read the frozen protocol and its amendments before interpreting results:

- [Original protocol](../../docs/PHASE4_PROTOCOL.md)
- [Accounting correction](../../docs/PHASE4_PROTOCOL_V2.md)
- [Verification-contract correction](../../docs/PHASE4_PROTOCOL_V3.md)

The active fixed-pool epoch is `results/phase4/epoch-20261112-v3`. Earlier epochs are retained, including interrupted tasks and rejected proof packets. The corrected source is `e882794750da70f76ce6e7163aa19f42d48a09b1ad743a31c00d0f915e5a8557`. No policy receives another policy's proof answers.

## Run and resume

Use the pinned research environment, with `PYTHONPATH=src`, from this checkout. Run only one controller for a particular output directory. These are the same commands for initial execution and resume:

```powershell
python benchmarks/phase4/run_fixed_pool.py --protocol results/phase4/epoch-20261112-v3/protocol-A-v3.json
python benchmarks/phase4/analyze_fixed_pool.py results/phase4/epoch-20261112-v3 --output results/phase4/epoch-20261112-v3/analysis.json
```

The fixed-pool driver records each child process ID, log, full controller CPU, sampled memory peak, and exit code. Each policy directory retains `progress.json`, `population.sqlite`, proof files, and its final `comparison.json`. Missing comparisons remain missing; analysis does not replace them with zero performance. Do not run the first command concurrently with an existing campaign.

After all fixed-pool blocks complete without censored accounting, run the main adaptive comparison:

```powershell
python benchmarks/phase4/run_adaptive.py --plan results/phase4/epoch-20261112-adaptive/plan.json --case main72
```

The adaptive driver checks the fixed-pool prerequisite. Its frontier policy preserves legacy-window promotion followed by the final sweep. A finite compute checkpoint can arrive before that sweep; this is a measured outcome, not permission to change the policy.

## Later stages

`freeze_scaling.py` freezes the predeclared 1000-proposal, seed-74011 experiment with all five policies and preparation CPU plus 1000/2500/5000 CPU-second checkpoints. Launch it only after the main adaptive comparison. This is a single-seed descriptive scale study. Within that pool the policies share total compute checkpoints; comparing it directly with the 100-proposal results does **not** isolate population-size effects at equal total CPU. That additional claim requires separately frozen common absolute checkpoints.

The adaptive plan also binds generation comparisons and the supplied 24- and 36-qubit transfer inputs. Run those cases after population scaling, in the declared order. `run_ler.py` performs the separately budgeted, 1024-shot BP-OSD finalist measurements only after finalist selection is frozen. Simulation never substitutes for an exact-distance proof.

## Evidence and limitations

`prepare_delivery.py` creates a separate export catalogue from sealed pools and policy databases. Copies are evidence reuse, not new executions; do not add their task CPU again. Public export verification must bind the exact circuit, schedule, fault model, source, and proof. Keep verification receipts outside the bundle being verified.

Worker CPU and wall-time limits are absent. Finite prospective experiment checkpoints stop new dispatch for fair comparison; an admitted paired evaluation finishes and its overshoot remains recorded. Memory and proof-work safeguards remain. A memory intervention is UNKNOWN, not physical invalidity. No cloud spending or public publication is performed by these scripts.
