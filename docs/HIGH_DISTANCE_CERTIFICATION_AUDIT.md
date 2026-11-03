# High-distance certification audit

The historical repository is read-only and remains separate. No stored physical-memory result or winning architecture is imported. The new extraction contract must be verified on its own IR.

| Historical component | Decision | Representation/model and semantics | Cost/verification |
|---|---|---|---|
| Pauli/symplectic kernels and scalar replay | REUSE_UNCHANGED | Clifford Circuit IR; operation-local physical alternatives; unsigned error effects, signed ideal semantics | Existing independent regressions retained |
| `certification_v6/graph.py` graph potentials | REFACTOR_AND_REUSE | Applicable only after every physical singleton projects to at most two detectors; location exclusivity relaxed for a conservative lower bound | BFS in a doubled logical-parity cover; O(V²) potential storage per channel; independent integer edge inequalities |
| `certification_v6/dp.py` physical-location frontier DP | REFACTOR_AND_REUSE | Exactly one alternative per physical location; completed detector support can be closed | Exponential in active frontier; explicit work/state/inventory caps; separate per-weight forward checker |
| `v21/pairs.py` exact singleton/pair predicate | REFACTOR_AND_REUSE | Equal detector signatures, different logical signatures, different locations | Linear grouped/ordered scans; independent forward inventory and separate ordered predicate |
| Backward algebraic signatures | REFACTOR_AND_REUSE | Full measured records, ideal terminal stabilizer syndrome, logical Pauli cosets | Streaming reverse maps avoid all-suffix materialization; SQLite keeps full alternatives |
| Forward bit-lane verification | REFACTOR_AND_REUSE | Same physical universe, independent forward Clifford propagation | O(G*F/batch); bounded128-lane chunks, compared with scalar replay and old suffix signatures |
| Exact low-weight subset search | RETAIN | Existing extraction low-order kernel | Exhaustive/joins for small controls; no target9 claim from a larger loop limit |
| Historical MITM joins | AUDIT_ONLY | Linear physical signatures plus location-disjointness tracking | Exponential half-weight tables; existing complete independent recipe is coupled to historical DB; not silently migrated |
| Historical CP-SAT audit | AUDIT_ONLY | Physical variant parity and exclusivity | Exports model and solver response, explicitly no portable UNSAT proof; not accepted as standalone positive evidence |
| Historical rank-universe continuation | ADAPT_CONCEPT | Historical task class/observable boundaries differ | Task/inventory/partition binding retained conceptually; new graph roots are independently checked complete partitions |
| Hardware routing / full-memory orchestration | EXCLUDE_FROM_CORE | Different task/physical layout scope | Historical evidence remains archived, no cross-scope certificate reuse |

New algorithms accept positive requested targets including2/3/5/7/9; method eligibility and resource limits determine CERTIFIED, INVALID or UNKNOWN. High-target API acceptance is not scientific success. Final results must identify actual complete positive proofs.
