# Repeated-memory exact certification

The existing graph-potential, MITM, DP, SAT and decomposition portfolio now accepts the validated physical CSS memory task. The full inventory includes correlated gate alternatives, reset/preparation effects, measurement flips, terminal readout and enabled storage locations, with one alternative per physical location.

For memory tasks the detector vector contains only declared physical measurement parities and the logical vector only declared readout observables. Neither perfect final syndromes nor residual unmeasured data logicals are inserted. Graph methods must pass full-signature eligibility; other exact methods retain their original semantics. Each complete certificate is rebound to the exact circuit, source and memory-sector fault contract and independently checked using the forward inventory. Negative witnesses are independently replayed.

A single-round extraction certificate is not reused as a repeated-memory certificate. Comparisons of r=1 versus r>1 must use the same physical memory boundary convention. Comparing ideal extraction to physical memory instead changes both the repetition and the boundary task.

The singleton/pair producer now scans for a later singleton even after discovering a pair, fixing the conservative UNKNOWN-at-target-2 failure described in the supplied notes. Independent verification remains mandatory.

`--no-time-limits` removes worker CPU/elapsed timers, not proof-work or memory bounds. UNKNOWN is preserved when an exact method cannot finish its obligation. No global efficiency or global-optimality claim is made.
