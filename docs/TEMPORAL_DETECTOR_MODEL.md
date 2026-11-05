# Physical temporal detector model

For product preparation in basis B, only first-round B-type stabilizers have a known initial value. The conjugate checks are initially random and do not define first-round detectors. Later detectors compare the same check's complete outcome parity between adjacent rounds. Flag parities remain explicit. Final B-type checks compare the last syndrome with the parity of physical data readouts. Logical observables are final readout parities in the same B sector.

The verifier checks complete history coverage, per-wire round operations against the signed-flow-verified extraction template, physical boundary operations, exact temporal parity definitions, and logical readout supports. Stim signed flows independently verify detector/observable determinism. A separate boolean-array engine replays simultaneous faults across all rounds. The inventory's independent forward and backward engines agree on controls without appending an ideal syndrome or unmeasured logical effect.

Storage noise is explicit rather than inferred from elapsed circuit depth. A storage-enabled task is rejected when live-qubit schedule gaps lack physical IDLE operations.
