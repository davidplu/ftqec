# Simulation and decoding

Stim samples the physical circuit with operation depolarization, reset X errors and measurement flips, with ideal code-space initialization in a fixed logical-Z sector and perfect final syndrome readout. This conditional reliability experiment is not arbitrary-input physical memory. The certification fault universe includes all allowed alternatives, independently of their stochastic probability.

The legacy decoder chooses the most probable single DEM mechanism and predicts zero for missing syndromes. It is weak for multiple faults. The optional `matching` extra installs PyMatching; `--decoder matching` requests correlated two-pass matching, and `auto` records any unsupported graph-model reason before explicitly falling back to lookup. Matching is a heuristic, not optimal maximum-likelihood decoding.

Matching uses an invertible temporal detector basis and requires successful graphlike decomposition. Stim disjoint-channel approximation is disabled. Suggested correlated components are passed to correlation-enabled matching at construction and inference. Hyperedges are never silently discarded. The full physical circuit remains the sampler. Certification uses its separate undecomposed physical inventory.

Each evaluation records decoder/version, model hashes, shots, failures, seed, build/inference cost and fallback status. Resource-LER dominance compares only equal decoder, noise and physical probability. Repeated looks combine independent deterministic-seed batches with candidate-wise Hoeffding alpha spending alpha/(look*(look+1)); this is not simultaneous population-wide coverage. Broad intervals and zero failures do not establish zero LER.

Primary implementation references: [PyMatching correlated matching API](https://github.com/oscarhiggott/PyMatching/blob/master/src/pymatching/matching.py), [Stim DEM semantics](https://github.com/quantumlib/Stim/blob/main/doc/file_format_dem_detector_error_model.md), and [Stim error analysis options](https://github.com/quantumlib/Stim/blob/main/doc/usage_command_line.md). Runtime versions are retained in experiment receipts.
