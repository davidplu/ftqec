# Architecture generation

The optimizer accepts stabilizer JSON only. No successful circuit, layout, coordinates, reference schedule or reference genome enters `generate` or `hook_orders`. Code names and metadata are not consulted by synthesis. The benchmark preparation layer exports stabilizers before optimizer invocation; reference circuits are separate controls.

Supported families are bare ancillas, interval flags, GHZ cats and verified GHZ cats. Flags can bracket one interval, adjacent intervals or nested suffixes. Verification measures a full star of cat ZZ parities for a configurable number of rounds. Every candidate is checked with signed stabilizer measurement flows and logical-preservation flows. A family name never asserts fault tolerance.

Random sampling varies interaction permutations, check order, ancilla sharing, rounds, flag style, verification count and check-serial/axis-grouped scheduling. Mutations also change signed generator bases using actual commuting Pauli products. Recombination carries orders together with their generator basis. Physical identity includes gates, schedule, measurement parities and boundary semantics; duplicate circuits are not counted twice.

The code-only hook-graph operator is an additional CSS construction strategy. It greedily evaluates check interaction orders against projected data-error graphs. It uses every one-qubit Pauli and possible ancilla-propagated suffix combined with a data-gate Pauli. Orders of weight at most four are enumerated; larger checks have bounded sampled options. These are construction heuristics. Only a complete physical inventory and independent proof can certify the compiled circuit.
