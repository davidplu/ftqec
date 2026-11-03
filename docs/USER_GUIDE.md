# CLI workflows and recovery

## Optimize a code

A bounded smoke run:

```bash
ftqec optimize examples/steane.json --output runs/smoke --generations 1 --population 8 --workers 1 --seed 0
```

For larger populations use `--storage sqlite`, `--window 32`, and `--promotion 8`. `--candidate-goal` requests a finite number of meaningful circuit structures; generated proposals, distinct physical identities, and structural classes are different counts. The current window can overshoot the requested goal. A candidate goal is not a guarantee that every candidate is simulated or certified.

`--target-distance` aliases `--target`. Available strategies are `random`, `witness`, `multifidelity`, `hybrid`, `costaware`, and `costhybrid`. Available decoders are `auto`, `matching`, and `one_mechanism_lookup`. Use `ftqec optimize --help` for defaults. A strategy name does not establish empirical superiority.

## Cancel and resume

```bash
ftqec cancel runs/smoke
```

The cancellation marker is `runs/smoke/cancel.json`. After workers have stopped, preserve the checkpoint and receipts. Remove only that marker when intentionally resuming, then rerun the same input and configuration against the same output directory. Source/runtime/configuration mismatches must not be bypassed. Do not launch two controllers against one run directory.

The frozen baseline has a known pending-final-window recovery defect discovered during development: interruption immediately after the goal candidate is persisted can cause premature completion on resume. Keep the pending state and do not treat the goal status alone as complete evaluation. The staged correction and regression are preserved in `scripts/large_scale_delivery_fixes.py` and `benchmarks/recovery/test_pending_window.py`; they are not silently applied to old scientific epochs.

## Inspect and deliver results

`ftqec list-results --run runs/smoke` lists available candidates; `--all` includes more than the selected frontier. Export formats are `bundle`, `circuit-json`, `schedule-json`, and `stim`. Use a new output directory to preserve prior artifacts. A bundle carries circuit and schedule identities and available certification evidence. Verify a bundle with `ftqec verify-export PATH --require-certified`; omit the flag only when intentionally inspecting a non-positive bundle.

`ftqec render-schedule SCHEDULE_JSON --output timeline.svg` renders a schedule. Optional `--start`, `--stop`, and `--qubits` control the view, not the circuit being certified.

## Certify a compiled circuit

```bash
ftqec certify exported/steane/circuit.json --target 5 --proof-method mitm --proof-work 20000000 --output runs/proof
```

This takes a compiled circuit, not a stabilizer-code input. Inspect the resulting `certificate.json`: status, achieved lower bound, harmful upper witness when present, independent verification, and unresolved obligations all matter. The command completing successfully is not equivalent to CERTIFIED.
