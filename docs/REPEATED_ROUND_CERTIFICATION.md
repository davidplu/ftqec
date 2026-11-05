# Repeated-memory exact certification

The existing graph-potential, MITM, DP, SAT and decomposition portfolio now accepts the validated physical CSS memory task. The full inventory includes correlated gate alternatives, reset/preparation effects, measurement flips, terminal readout and enabled storage locations, with one alternative per physical location.

For memory tasks the detector vector contains only declared physical measurement parities and the logical vector only declared readout observables. Neither perfect final syndromes nor residual unmeasured data logicals are inserted. Graph methods must pass full-signature eligibility; other exact methods retain their original semantics. Each complete certificate is rebound to the exact circuit, source and memory-sector fault contract and independently checked using the forward inventory. Negative witnesses are independently replayed.

A single-round extraction certificate is not reused as a repeated-memory certificate. Comparisons of r=1 versus r>1 must use the same physical memory boundary convention. Comparing ideal extraction to physical memory instead changes both the repetition and the boundary task.

The singleton/pair producer now scans for a later singleton even after discovering a pair, fixing the conservative UNKNOWN-at-target-2 failure described in the supplied notes. Independent verification remains mandatory.

`--no-time-limits` removes worker CPU/elapsed timers, not proof-work or memory bounds. UNKNOWN is preserved when an exact method cannot finish its obligation. No global efficiency or global-optimality claim is made.

## Streamed weight-three exclusion

Profiling the supplied verified-cat candidate exposed 6,300 distinct detector/logical effects. Materializing every pair would require 19,841,850 records before the three-fault join. The `triples` method instead scans pairs and looks up the complementary detector effect in a linear-size index. No quadratic pair table is stored. It applies to arbitrary detector signatures under the existing additive physical fault model, not only graphlike signatures.

A separately checked singleton/pair prefix is mandatory. If a minimum harmful triple contained a null effect or two identical effects, removing those effects would leave a smaller harmful set, contradicting that prefix. Therefore three distinct nonzero effects suffice. Equal effects retain all possible physical locations; a matching assigns each selected effect to a distinct location. Correlated Pauli components are never split.

The independent verifier rebuilds the effect domains from the forward inventory, reverses the complement enumeration, and applies the three-set form of Hall's condition: each domain is nonempty, every pair union has at least two locations, and the total union has at least three. It verifies all pair/join coverage counts and exact circuit/source/inventory bindings. Independent exhaustive physical oracles cover the grouping and location-exclusivity cases.

`--proof-method triples` can complete target four; for a higher target it can only establish a partial lower bound of four. The automatic portfolio also attempts it after an eligible graph proof fails. Time grows with the pair scan and matching candidates; worst-case dense joins need not be quadratic. This is not a generally efficient arbitrary-distance algorithm. A work-limited scan stays UNKNOWN and restarts rather than treating an unverified partial scan as a certificate. Existing disk-backed MITM and other methods remain available.
