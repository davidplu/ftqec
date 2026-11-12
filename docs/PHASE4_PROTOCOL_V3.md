# Controlled comparison: verification-contract correction

Version 3 retains the scientific settings, policies, seed list, CPU checkpoints, fault model, and primary statistical contrast of version 2. It corrects the adapter that assembles an exact-distance certificate from a lower proof and a physical upper witness. The pair/graph verifier expects `upper_witness`; the physical-row-relaxation verifier expects `witness`. The version-2 adapter supplied only the former. The affected checker therefore rejected the assembled certificates, and no affected pair was adopted.

The first four affected physical upper witnesses independently replayed successfully. That does not, by itself, certify their lower bounds. Fresh production and full independent verification are required by the new regression before this protocol is frozen. The regression is a post-hoc engineering audit and is not credited to a controlled policy checkpoint.

The interrupted version-2 random-policy attempts remain intact. Their reported UNKNOWN outcomes are adapter failures, not physical invalidity or evidence that the underlying lower-bound problem is intractable. They must not be pooled with version-3 performance measurements.

The completed first pool is reused in full: all 100 proposals, 97 compiled pairs, initial screens, and three memory-censored constructions. Its original construction source and hashes remain recorded. Its full measured preparation CPU is charged equally to every policy; reuse does not make preparation free. No certification, simulation, or verification answer from the interrupted policy run is imported into a new policy database. The generator, compiler, physical fault engines, scheduling, and resource-accounting files are checked byte-for-byte against the preserved construction source. Only the experiment adapter, experimental metadata, and adaptive-parent handling differ.

The new adaptive-parent guard prevents a valid weight-at-target upper witness from being mistaken for a below-target failure requiring repair. Only independently replayed, below-target negative witnesses may guide fault repair. No adaptive scientific experiment had run before this correction. The earlier adaptive plan remains preserved but must be superseded before execution.

New experiment checkpoints also retain the normalized code input needed by the public export command. This is provenance wiring, not a circuit or proof change.

The executable protocol is `results/phase4/epoch-20261112-v3/protocol-A-v3.json`. Its source snapshot and the older generation-source snapshot are both preserved. All five policies restart with fresh proof and simulation tasks under the corrected source. The predeclared policy ordering and scoring rules do not change in response to the diagnostic results.
