# Ancilla allocation

Genomes retain the shared/dedicated choices and add an optional integer `ancilla_slots` between one and the number of stabilizer checks. Checks are assigned cyclically to actual syndrome slots. Bare, flagged and cat architectures allocate their real syndrome, flag and verification resources according to the slot count. Reset/measurement lifetimes and noncommuting wire dependencies enforce reuse ordering.

The coloring constructor currently requires dedicated syndrome ancillas and bare CSS gadgets. Intermediate allocations use general dependency scheduling. Allocation mutations return colored parents to the general scheduler when the coloring assumptions change. Cat width, flag intervals and verification repetitions remain existing population choices.

Q, D, QD and two-qubit counts are recomputed from each actual compiled circuit. Lower-qubit certified alternatives are retained on the joint resource Pareto frontier even when they have larger depth. No general claim that additional ancillas improve QD follows from an allocation parameter or a unit test.
