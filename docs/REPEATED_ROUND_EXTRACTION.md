# Repeated extraction and physical memory

`ftqec repeat single-circuit.json --rounds 4 --output repeated.json` materializes extraction operations with unique records and explicit round dependencies. This retains the historical ideal-boundary extraction task.

Add `--memory-basis Z` or `--memory-basis X` for a different task: physical product preparation, repeated CSS projection/extraction, and destructive physical data readout. Every reset, H, CNOT, measurement, and enabled IDLE is a fault location. No ideal final stabilizer readout is appended. X and Z sectors are separate experiments, not interchangeable certificates or an arbitrary-input encoding proof.

`--explicit-idles` materializes storage operations for live qubits in unoccupied scheduled ticks. The default is no storage noise, explicitly recorded. Noise assumptions must match across compared circuits.

The input must be a validated single-round extraction circuit. The generic constructor supports existing CSS extraction templates; the population specialization searches supplied group-term and generic bare/flag/cat architectures. Existing general stabilizer optimization remains available. The specialized search uses its documented hybrid policy; legacy strategy, SQLite storage and candidate-goal options apply to the original optimizer, not this opt-in development driver.
