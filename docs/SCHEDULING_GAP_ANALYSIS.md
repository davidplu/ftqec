# Scheduling gap analysis

The preserved source's actual depth-12 discovery and depth-8 reference were reconstructed before implementation. Machine-readable critical paths are in `results/competitive_export/baseline/`. The discovery's longest path crosses four X interactions and four Z interactions; the constructor colored those phases separately. It also used controlled-P ancilla-X-readout gadgets for both check types, with 198 Hadamards versus 100 in the reference.

Wire-order constraints are necessary for that concrete sequence, not necessarily for a different equivalent measurement circuit. Joint X/Z interaction coloring enforces qubit conflicts and even relative-order parity over every opposite-axis shared support. Native Z-parity extraction replaces the unflagged Z gadget with data-to-ancilla CNOTs and Z readout. Neither transformation carries an automatic distance guarantee: every adopted result is revalidated and independently certified. The reference is only a diagnostic comparator; its circuit, interaction layers and coordinates are not supplied to the constructor.

The analysis API `ftqec.scheduling.analysis.analyze(circuit)` lists every concrete dependency edge, a critical path and layer counts. It distinguishes explicit, commuting-wire and noncommuting-wire edges. These local constraints do not prove global optimality over architecture changes.
