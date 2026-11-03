# Current general-extraction extension

See [General certification](GENERAL_CERTIFICATION.md) for the whole-location reduction proof and independent checker. Source `d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306` adds suffix-span pruning and exact domain compression while retaining the prior backend as `decomposition_legacy`. The source-bound matched studies are under `results/general_extraction/proof_development/` and `results/certification/d9b1e28e6919cb04178ec813ffe6ad477d0ba546163a45255714d28030a13306/small_positive_matched/`. The target-five discovery uses MITM; it is not a separator target-five positive.

The previous documentation follows as historical algorithm context.

# Component and separator certification

A physical location is a finite-domain variable: identity, or exactly one complete fault alternative. Detector-connected components contain entire locations, including all their alternatives. Distinct components share neither locations nor detector coordinates. Any globally undetected harmful configuration must contain an undetected component with nonzero logical effect; conversely that component alone, with identity elsewhere, is harmful. Thus every component must exclude such assignments below the target. Logical components are not assumed to compose as independent fault-tolerant gadgets.

Within a component, a greedy location ordering minimizes the active detector frontier. A detector is removed only after its last incident variable, and only if its accumulated parity is zero. States retain full active detector parity, logical parity and minimum physical fault weight. Lower-weight representatives dominate at the same processed-location boundary because all future choices are identical. State hashes bind every elimination layer.

The verifier reconstructs forward physical effects, checks exhaustive location coverage and disjoint detector support, and runs a separate suffix-parity recurrence over all alternatives. It compares each transition-table hash and independently checks state/width accounting. Work exhaustion is UNKNOWN with completed progress preserved. The width is that of the declared elimination order, not a claimed minimum treewidth.

The implementation compares the estimated frontier width in raw detector coordinates with an invertible basis of the complete physical detector-signature span. It chooses the narrower of those two declared orders. The independent checker reconstructs the basis and verifies every physical alternative. This is an exact parity-coordinate change, not deletion or graphlike approximation of correlated faults. The developmental span-only attempt and its larger frontier remain in the raw record.

A real surface_small target2 circuit has a completed component-separator proof and separate independent replay. The forced Steane target3 attempt exhausted separator work and retained a pair certificate; it is not counted as a separator proof. Shor4 and the target5 follow-ups remain separator-limited. The target5 nested follow-up reaches100001 states with a completed lower bound3, leaving weights3–4 unresolved by this method; MITM subsequently finds a harmful weight4 witness for that candidate. See [the method table and follow-up](RESULTS.md).
