# Certification methods and scientific contract

## Exact problem

At each physical fault location choose identity or one enabled nonidentity alternative. A nonidentity choice costs one faulty location, even when it has correlated effects on two qubits. At most one alternative may be selected at a location. XOR all detector and logical signatures. A harmful assignment has zero detector signature and a nonzero logical signature.

Target d certification excludes every legal harmful assignment of weight less than d. An exact-distance claim additionally needs a matching independently replayed harmful witness of weight d. Algebraic code distance does not automatically establish extraction distance.

## Portfolio

| CLI method | Approach and limitations |
|---|---|
| `auto` | Eligible graph reasoning and bounded exact fallback; inspect the actual selected backend |
| `graph` | Structural graph proofs only where eligibility and global coverage hold |
| `mitm` | Full-signature meet-in-the-middle with exact physical-location assignment and independent reverse joins |
| `dp` | Location-aware exact dynamic programming; potentially exponential state growth |
| `sat` | Physical-domain CNF with bounded search and independently checked proof evidence; UNSAT text alone is insufficient |
| `decomposition` | Whole-location domain reduction followed by exact separator processing |
| `decomposition_span` | Detector-span coordinates and separator/suffix-span processing |
| `decomposition_legacy` | Preserved earlier decomposition backend for comparisons |

A requested method is not always the backend responsible for a completed lower bound: inexpensive pair checks can settle a low-distance input before the requested expensive backend contributes. Always report actual proof provenance.

## Independent evidence

Positive verification checks exact circuit/source/model identities and proof coverage. Negative replay checks complete physical faults, legal locations, detector parity and logical effect. Correlated faults must not be split into independent graph edges merely to obtain eligibility. A raw signature touching more than two detectors is not, by itself, proof of ineligibility under every valid projection.

## Limits

General exact exclusion can grow exponentially. Work, CPU, memory or cancellation limits yield UNKNOWN when proof obligations remain. A partial lower bound remains useful but does not certify the requested higher target. Graph-eligible surface results cannot substitute for graph-ineligible non-surface milestones. Certificates here concern the declared extraction model with ideal boundaries, not arbitrary-input physical memory or a routed hardware implementation.
