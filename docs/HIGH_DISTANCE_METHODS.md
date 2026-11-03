# Structural high-distance methods

## Graph relaxation and integer potentials

Apply a declared binary linear map to physical detector signatures; zero full syndrome implies zero projected syndrome. Eligibility requires every physical alternative to have at most two projected detector endpoints. Never decompose a hyperedge into separately charged edges. Duplicate projected edges may merge only in the scratch graph; the full inventory and multiplicity remain bound.

In a doubled graph, edges toggle the selected logical parity. Any projected zero-syndrome harmful physical set decomposes into cycles, at least one with odd logical parity. An integer potential with source0, opposite logical copy at least t, and absolute difference at most1 on every lifted edge proves that every such path has length at least t. Check all roots and every logical coordinate. Relaxing location exclusivity can make a lower bound weaker, never unsound. Relaxed paths become negative claims only after distinct-location full-circuit replay.

The checker regenerates effects forward in128-lane batches, compares the complete canonical inventory hash, rebuilds eligibility and verifies edge inequalities directly without rerunning BFS. Root fragments are task/graph/target bound and checked when resumed. Missing/duplicate logical partitions or missing roots invalidate acceptance.

## Physical-location frontier DP

Process operation locations once, choosing none or exactly one alternative. Retain minimum cost for each detector/logical state; this dominance is sound because every future location is disjoint from the prefix. Discard a nonzero detector after its last possible affecting location. Independent checking uses per-weight sets and suffix support, rather than producer min-cost maps. State/work/inventory limits produce UNKNOWN. Completed milestones are not a downgraded requested target.

Inventories use SQLite with a2MiB page cache and disk-backed temporary storage. Backward transfer uses rolling maps instead of all circuit suffixes; independent forward propagation has a fixed lane batch. DP remains exponential in frontier width and has explicit caps. Worker memory guards remain active; this is not universal bounded-time high-distance certification.
