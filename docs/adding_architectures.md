# Adding an architecture

Implement a pure compiler from CodeInput and Genome to the common Circuit IR. Declare every allocation, reset, gate, measurement, detector and observable. Canonical physical identity ignores descriptive labels but retains gate order, scheduled timing and record parities. Do not deduplicate by resource counts alone.

Require signed Stim measurement flows and logical-preservation flows. Compare optimized fault effects with forward propagation and Boolean replay, including non-CSS Y interactions and correlated gate faults. Include a verified negative witness and independently verified positive control where feasible. A family name is not a fault-tolerance guarantee.

Expose mutations only after recompilation and independent correctness checks. Ancilla reuse must preserve reset epochs. New classical feed-forward, non-Clifford or postselection semantics require extending the IR and scientific engines, not embedding an opaque callback.
