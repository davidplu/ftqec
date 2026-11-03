# Shor multi-fault diagnosis

The current source is `d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306`. The preserved `[[16,1,4]]` repair remains a target-four control; it is never substituted for the independently validated `[[25,1,5]]` development code.

The new replay index is [the source-bound diagnosis index](../results/fault_diagnosis/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/index.json). It covers 25 preserved controls and independently replays all 13 harmful witnesses among them. Original packets and hashes remain unchanged. Each replay retains the exact circuit, physical alternatives, simultaneous propagation, and per-fault propagation contributions.

The target-five nested-flag failure combines three syndrome-X injections at flag opening/closing gates with a data-X fault. The individual flag effects cancel, and the simultaneous final data error is a logical X row. Full propagation, not the gate-role labels, establishes this mechanism. Additional proof time cannot certify that unchanged circuit.

Round-prefixed flag records were absent from the separate diagnostic flag bitmap in the previous implementation. The new implementation identifies flag measurements by their allocated physical qubits in both optimized and independent engines. Explicit flag detector parity was already included in certification. Historical evidence is retained under its exact original source; current replays do not rewrite it.

Context and causal conclusions are separate: verification/preparation/readout contexts and correlated physical alternatives are recorded independently of whether they actually spread data error or cancel flag evidence. No Pauli components are split into separate physical faults.
