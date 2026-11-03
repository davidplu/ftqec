# Large-scale autonomous optimization

This development cycle evaluates the complete optimizer, preserving FTQEC 0.1.0 and the existing scientific engines. Scientific conclusions will be bound to frozen campaign artifacts; storage capacity alone is not a scientific success.

The public Optimize API supports `storage="sqlite"`, and the CLI supports `--storage sqlite`. Automatic storage selection uses SQLite for populations of at least 100 or an explicit candidate goal. `--window` bounds simultaneous construction/evaluation records; it is not the total population size. The durable candidate archive remains available for family-balanced parent selection, mutation, recombination, certification elitism, and Pareto retention.

`--candidate-goal` is an optional finite experimental population target, not a global runtime limit. Without a finite population experiment or user cancellation, optimization retains its operational convergence behavior and per-task safeguards. A sampled plateau is not global optimality.

All construction, noiseless checks, resources, screening, simulation, and certification use the existing scientific engines. A measured development pilot found that process overhead dominated construction and singleton screening. A fused supervised cheap-stage task therefore performs those unchanged operations together where a fixed screening funnel is selected. Cost-aware small-target runs preserve direct certification.

Development results and failed integration checks are retained under `results/large_scale/`. The final report must distinguish generated attempts, exact physical candidates, meaningful structural classes, screened circuits, simulated circuits, and independently certified finalists. No optimization advantage is established by this implementation description.

The population parameter also bounds the active parent pool queried from the durable archive. Working-window size controls materialized circuits independently. Matched-compute studies therefore distinguish active-parent capacity from cumulative candidate goals and from additional search time.

The existing code-only guided proposal engine is preserved in the supervised construction task, alongside random proposals. Its actual returned genome and provenance are stored; the initial queued seed is not misreported as the final genome. Guidance remains a proposal mechanism, never a fault-tolerance certificate. Resource-limited proposal tasks remain UNKNOWN.
