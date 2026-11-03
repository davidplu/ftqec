# Exact schedule export

`ftqec export CIRCUIT_ID --run runs/local --format schedule-json --output exports/schedule.json` emits operation IDs, full operation metadata, qubits, explicit and wire-order dependencies, start/end layers, parallel groups, measurement indices, ancilla reset epochs, reuse boundaries and depth. The circuit's metadata, detectors, logical observables and exact content identity are included, allowing independent reconstruction without the optimizer checkpoint.

`ftqec verify-export exports/schedule.json` reconstructs operations directly from schedule rows and recomputes all resource fields without calling the export producer or scheduler. The bundle's `schedule.txt` is a human-readable layer listing generated from the same data. Unit-duration gates and zero-duration barriers match current resource accounting; these are not hardware-calibrated durations. A standalone schedule carries reconstruction evidence, while the research bundle additionally binds and replays certification.

For a compact selected-layer view, run `ftqec render-schedule exports/finalist/schedule.json --start 0 --stop 8 --qubits 32 --output exports/timeline.svg`. The view is generated after independent reconstruction, labels its partial qubit coverage, and preserves full gate operands in hover text.
