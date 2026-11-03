# Exact proof methods

## Existing engines

Singleton/pair exclusion uses physical locations and complete detector/logical effects; a distinct ordered scan checks it. Graph potentials require every projected physical alternative to be graph eligible. Each logical channel must be covered. A sound projection is a relaxation used only to prove exclusion, not a replacement of hyperedges in the general fault universe. Location-frontier DP keeps legal alternatives grouped by physical operation; its checker uses a separate per-weight suffix-support recurrence.

## Full-signature meet in the middle

A minimum harmful set contains neither a zero-effect alternative nor two alternatives with identical detector/logical effects: deleting such a singleton or cancelling pair preserves harmful parity and decreases weight. Therefore the producer groups equal effects but retains their complete sets of physical locations. Every candidate effect set must admit a distinct-location assignment; grouping never identifies different locations or permits two alternatives at one location.

For each weight w, sorted distinct effect IDs are split after floor(w/2). Disk-backed halves are joined on equal detector parity and unequal logical parity, requiring the left maximum ID to precede the right minimum. This covers each effect set once. Bipartite matching enforces physical realizability. Half partitions record exact binomial counts and ordered SHA-256 digests. Transactional checkpoints bind source, inventory, target and method version.

The checker rebuilds the complete forward inventory, independently enumerates recursive half combinations, traverses joins in reverse and uses separate recursive location assignment. It compares coverage counts and partition hashes. Prefix singleton/pair exclusions are independently checked when the MITM starts at weight three. This is independent recomputation, not a succinct proof system. Disk and exponential combination growth remain limitations.

## Physical-fault SAT

The CNF retains one binary variable per original physical alternative. XOR circuits impose zero detector parity and nonzero logical parity. Pairwise location clauses impose exclusivity. An exact sequential threshold counter excludes weight at or above the requested target. No Pauli component splitting or graph decomposition is used.

A bounded DPLL producer records a binary branch tree. Every UNSAT leaf must be refutable by unit propagation; both values of each branch variable must be checked. The separate set-clause verifier reconstructs the formula from forward effects and replays the complete tree. SAT models become independently replayed physical witnesses. Work and recursion limits yield UNKNOWN. This small backend is an encoding oracle, not a competitive industrial SAT solver; no external UNSAT status is accepted. Tests enumerate all physical assignments on small correlated/location-exclusive instances.
