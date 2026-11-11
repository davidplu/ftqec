# CLI workflows and recovery

## Repeated noisy CSS memory experiments

For the supplied 2BGA JSON convention, validate the algebra and optimize actual repeated circuits:

```bash
ftqec validate-2bga code.json --output algebra.json
ftqec optimize code.json --memory-rounds 4 --target-distance 4 --population 8 --generations 2 --workers 2 --no-time-limits --output runs/memory
ftqec list-results --run runs/memory --all
```

Use the exact circuit identity returned by `list-results` with the existing export commands. Each X or Z memory sector has a separate identity and certificate. Both are required for the paired frontier. `UNKNOWN` remains unresolved even when export reconstruction succeeds. See [repeated extraction](REPEATED_ROUND_EXTRACTION.md), [search and allocation](LOW_DEPTH_OPTIMIZATION.md), [certification](REPEATED_ROUND_CERTIFICATION.md), and [development results](2BGA_BENCHMARKS.md).

The physical task uses noisy product preparation, repeated CSS measurements and destructive data readout. It is not an arbitrary-input encoder certificate. Storage noise is absent unless `--explicit-idles` is selected. For other CSS codes, `ftqec repeat single-circuit.json --rounds 4 --memory-basis Z --output memory.json` constructs the same declared task from a validated single-round template. The existing general stabilizer optimizer remains available without `--memory-rounds`.

## Optimize a code

A bounded smoke run:

```bash
ftqec optimize examples/steane.json --output runs/smoke --generations 1 --population 8 --workers 1 --seed 0
```

For larger populations use `--storage sqlite`, `--window 32`, and `--promotion 8`. `--candidate-goal` requests a finite number of meaningful circuit structures; generated proposals, distinct physical identities, and structural classes are different counts. The current window can overshoot the requested goal. A candidate goal is not a guarantee that every candidate is simulated or certified.

Use `--no-time-limits` to disable both worker CPU and elapsed-time cutoffs for a long evaluation. Memory safeguards and `ftqec cancel` remain active. This option does not change the physical fault model, proof-work allowance, generation count, or certification requirements. Defaults remain 300 CPU seconds and 600 active elapsed seconds per task. Changed settings require a new output directory; old checkpoints retain their original settings and source identity.

```bash
ftqec optimize code.json --output runs/unlimited-time --no-time-limits
```

`--target-distance` aliases `--target`. Available strategies are `random`, `witness`, `multifidelity`, `hybrid`, `costaware`, and `costhybrid`. Available decoders are `auto`, `matching`, and `one_mechanism_lookup`. Use `ftqec optimize --help` for defaults. A strategy name does not establish empirical superiority.

## Cancel and resume

```bash
ftqec cancel runs/smoke
```

The cancellation marker is `runs/smoke/cancel.json`. After workers have stopped, preserve the checkpoint and receipts. Remove only that marker when intentionally resuming, then rerun the same input and configuration against the same output directory. Source/runtime/configuration mismatches must not be bypassed. Do not launch two controllers against one run directory.

The frozen baseline has a known pending-final-window recovery defect discovered during development: interruption immediately after the goal candidate is persisted can cause premature completion on resume. Keep the pending state and do not treat the goal status alone as complete evaluation. The staged correction and regression are preserved in `scripts/large_scale_delivery_fixes.py` and `benchmarks/recovery/test_pending_window.py`; they are not silently applied to old scientific epochs.

## Inspect and deliver results

For experimental paired X/Z repeated-memory discovery, see
[the paired-memory guide](PHASE3_OPTIMIZATION.md). That driver has no worker CPU
or elapsed-time cutoff; memory safeguards and proof-work limits remain active.
Its optional experimental CPU checkpoint is checked between windows and can
overshoot by an entire window.

`ftqec list-results --run runs/smoke` lists available candidates; `--all` includes more than the selected frontier. Export formats are `bundle`, `circuit-json`, `schedule-json`, and `stim`. Use a new output directory to preserve prior artifacts. A bundle carries circuit and schedule identities and available certification evidence. Verify a bundle with `ftqec verify-export PATH --require-certified`; omit the flag only when intentionally inspecting a non-positive bundle.

`ftqec render-schedule SCHEDULE_JSON --output timeline.svg` renders a schedule. Optional `--start`, `--stop`, and `--qubits` control the view, not the circuit being certified.

## Certify a compiled circuit

```bash
ftqec certify exported/steane/circuit.json --target 5 --proof-method mitm --proof-work 20000000 --output runs/proof
```

This takes a compiled circuit, not a stabilizer-code input. Inspect the resulting `certificate.json`: status, achieved lower bound, harmful upper witness when present, independent verification, and unresolved obligations all matter. The command completing successfully is not equivalent to CERTIFIED.
