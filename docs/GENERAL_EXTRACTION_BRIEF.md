# Discussion brief for Professor Kim

FTQEC now discovers and independently certifies a non-surface, graph-ineligible extraction circuit at distance five from code-only input. The development code is Shor-product [[25,1,5]], with independently checked algebraic distance. The successful architecture is verified-cat extraction. The existing exact MITM engine supplies the target-five proof; the new separator algorithm is not responsible for that certificate.

Two certified resource choices are Q=36,D=329,QD=11,844 and Q=105,D=46,QD=4,830, both with 248 two-qubit gates. The lower-qubit alternative remains. Five other scheduling/allocation changes introduced harmful faults, despite preserving noiseless extraction semantics.

The new exact backend compresses only whole physical fault domains under a checked XOR-closure argument, then applies suffix-span separator DP. It completes an independently verified graph-ineligible target-three control with lower measured CPU and memory than the previous separator attempts. It does not yet provide a target-five separator proof.

The independent Hamming hypergraph-product [[58,16,3]] study improves a certified Q=100,D=53,720-two-qubit control to Q=100,D=49,240 gates. Earlier lower-qubit alternatives are preserved. This is cross-family evidence at target three, not a second-family distance-five result.

Matched decoder-conditional LER measurements use 131,072 shots per circuit/noise arm. Confidence intervals overlap, so they do not establish reliability superiority. The extraction certificate concerns harmful undetected faults under ideal boundaries; decoder failure probability is a separate quantity.

The most justified next experiment is to derive fault-aware scheduling constraints from the five rejected allocation descendants and test those repairs prospectively. The six-arm negative-parent repair study did not yield a certified invalid-to-valid lineage.

Scientific source: `d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306`. See [the full results](RESULTS.md), [physical diagnosis](SHOR_FAULT_DIAGNOSIS.md), and [exact-method argument](GENERAL_CERTIFICATION.md) for raw evidence and limitations.
