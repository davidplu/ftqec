# Evidence and reproduction

## Repository contents

The publication snapshot includes source, tests, documentation, examples and benchmark specifications. Main preserves baseline code; the separate certification-research branch includes raw task receipts for the paused indexing experiments. Large historical proof databases, population databases, archives and the original local Git history remain outside this snapshot. No claim is made that every archived experiment can be replayed from a clone alone.

## Reproduction checklist

1. Select an experiment and locate its exact source identity, input circuit, fault model, target, seed and runtime versions.
2. Obtain the required evidence bundle, including any external databases or verifiable inventory references.
3. Use a new output directory and the matching source environment.
4. Replay positive proofs and legal harmful witnesses independently.
5. Reconstruct exported circuits and schedules and recompute Q, D, QD and two-qubit gates.
6. Compare actual CPU, wall, memory and verifier costs on identical obligations; preserve failed and censored attempts.

Resource tuples must refer to one circuit. Finite Pareto frontiers are best-found alternatives, not global optima. Equal candidate counts are not matched compute. Verification costs nested inside task CPU must not be added twice.

## Paused certification study

The baseline reproduced two previously established target-5 positives. Eager range indexes were slower; deferred index construction restored positive completion but did not beat baseline total CPU. The prior UNKNOWN remained unresolved, and no new target-7 or target-10 positive was obtained. These are single-run measurements. See the experimental branch's `docs/CERTIFICATION_RESEARCH_PAUSED.md` and compact receipts for exact numbers.

The 10-hour campaign allowance was not ten hours of documented continuous computation. Receipts, actual worker activity and downtime must be reported separately. Research is paused; documentation and CI maintenance do not resume it.

## Manifests and links

`publication_source_manifest.json` records the imported snapshot; later commits are changes beyond that import. Experimental receipt manifests bind the selected raw files. These are not complete manifests of every locally preserved artifact. Historical report links may refer to the original evidence layout and require that evidence repository. Never substitute a missing artifact with fabricated or relabeled proof data.
