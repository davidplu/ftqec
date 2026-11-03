# Reproducing the autonomous campaign

The authoritative implementation is identified by the complete scientific source hash in `results/autonomous/campaign/protocol.json`. Exact study drivers and their hashes are retained with the experiments. Python and dependency versions are in `results/autonomous/release/environment.json` and `environment_requirements.txt`.

## Run a new code-only optimization

Install the packaged wheel with the matching extra in a separate environment. Preserve the delivered evidence and choose a fresh output directory:

```sh
ftqec optimize code.json --target-distance 10 --strategy hybrid --decoder auto --workers 2 --output runs/new-discovery
```

The input is a stabilizer-code JSON file, not a successful circuit. Use the same seed, population, shot allocation, proof budget and convergence patience from the prospective protocol for a matched reproduction. The Python `Config` interface exposes the full study configuration. The public CLI exposes the common options. A finite CLI smoke test is separately labeled and does not replace the anytime campaign.

## Re-run the exact studies

Use an isolated checkout or extracted source working directory with the recorded scientific implementation, the delivered study scripts and examples, and a fresh experimental output tree. Do not run those scripts over the delivered evidence: they intentionally use fixed relative output locations and resume existing source-bound checkpoints. The study sequence is `python scripts/autonomous_sequence.py`; it runs the primary ladder, separate-family generation comparisons, scaling, positive retention, decoder comparisons and independent reference controls in order. Within optimizer runs, bounded evaluator processes execute in parallel.

After the sequence completes, run `scripts/autonomous_code_audit.py`, `scripts/autonomous_audit.py`, `scripts/autonomous_report.py` and `scripts/autonomous_report_details.py`. The release report additionally records a separate installed-CLI smoke test. Reproduced timings depend on host contention, dependency builds and processor characteristics; exact stochastic counts also require the recorded runtime and random seeds.

## Recover old epochs

Earlier scientific epochs retain their own archived source and proof identities. Directly checking them with the latest source is expected to fail source-identity validation. Use the matching archived implementation in an isolated environment. The initial interrupted epoch was moved byte-for-byte into directories ending `_initial_epoch`; `results/autonomous/initial_epoch_preservation.json` maps each preserved directory back to its original location. Reconstruct those original relative locations in an isolated copy if an old certificate refers to a proof path. Never move them over current evidence.

The old epoch's elapsed timings include recorded system standby, and some interrupted controller costs could not be recovered. They are preserved scientific evidence, not clean timing baselines for the current implementation.

## Delivery verification

`results/artifact_manifest.json` is an external sidecar for the source/evidence ZIP. The ZIP contains `PACKAGE_CONTENTS.json` with every payload member's SHA-256. The sidecar is excluded from its own archive to avoid recursive hashing; its previous historical version is preserved under `results/autonomous/baseline/`. The separate Git bundle preserves local commit history. No public push or cloud resources are required.

On Windows, enable long paths for the isolated Git checkout with `git config --local core.longpaths true`; source-bound proof partitions have deeply nested hash directories. The working repository uses this local setting. No global Git or Windows setting was changed.
