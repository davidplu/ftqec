# Reproduce the repeated-memory development work

Use the source commit and scientific hash in REPORT.md. The private local evidence epoch is `results/2bga/epoch-20261105`; the original supplied archive is not bundled into Git. The wheel and source snapshots in that epoch preserve the exact bytes used for scientific identities.

## Public smoke workflow

Install FTQEC in a fresh virtual environment following `docs/INSTALLATION.md`, then run from the checkout:

```bash
ftqec validate-2bga examples/two_block_small.json --output runs/algebra.json
ftqec optimize examples/two_block_small.json --memory-rounds 2 --target 2 --population 2 --generations 1 --workers 1 --memory-shots 16 --proof-work 20000 --no-time-limits --output runs/memory-smoke
ftqec list-results --run runs/memory-smoke --all
```

This six-qubit example is an integration control, not a replacement for the supplied research benchmarks. Repeat the optimize command unchanged to test checkpoint reuse. Use an exact identity from list-results:

```bash
ftqec export CIRCUIT_ID --run runs/memory-smoke --output bundles/memory-smoke
ftqec verify-export bundles/memory-smoke --proof-work 20000
```

`verified` confirms bundle integrity and reconstruction. Only `positive_certificate_verified` confirms an independently replayed positive certificate. INVALID and UNKNOWN bundles are intentionally exportable.

## Supplied-code experiments

Place the unmodified supplied archive in a separate local evidence epoch. Validate every JSON before use. The command arrays in `development-measurements.json` and `expanded/measurement.json` are the authoritative experiment invocations; `expanded/protocol.json` freezes the second development phase. Use new output directories when source, input, worker configuration or noise changes. Never overwrite the original experiments to reproduce them.

The repeated-memory search requires multiplication-table metadata in addition to the stabilizer basis. Generic CSS circuits can instead use the public repeat constructor. The experiment uses explicit physical product preparation/readout and separate X/Z memory sectors; it does not prepare an arbitrary unknown encoded state.

## Replay archived evidence

The first and expanded phases intentionally have different source identities. For the first phase, make a separate copy of the checkout at the implementation commit and restore the files in `implementation-source.zip` into that copy. Install that copy in its own environment. For the expanded phase use `expanded/source.zip` or the matching wheel. Confirm `ftqec.results.artifacts.source_identity()` equals the evidence source before replay. Do not restore an old snapshot over an active campaign.

Run `ftqec verify-export` on each exported bundle. The independent verifier reconstructs the schedule, resources and Stim model, and replays the bound evidence. UNKNOWN receipts can contain independently verified partial lower bounds; their target remains unresolved. Unfinished worker receipts are preserved separately from mathematical certificates.

`artifact_manifest.json` lists SHA-256 hashes for all scientific files, logs, source snapshots and package wheels in the epoch. The disposable clean-install virtual environment is excluded; its installation log and installed CLI receipts are included. The scientific artifacts and local Git commits are not automatically uploaded by these commands.

## Runtime and interpretation

Campaign commands disable CPU and active elapsed timers with `--no-time-limits`. Memory admission, worker memory limits, cancellation, finite proof-work safeguards and checkpoints remain. A finite generation count is the recorded development measurement condition, not a permanent optimizer time limit. No claim of matched-compute policy superiority follows from these development phases.

The public CLI clean-install receipt is `clean-cli.json`. The final full suite and the additional interrupted-task recovery test have separate logs. Exact failures, UNKNOWN obligations and unsuccessful build/setup attempts are retained alongside positive controls.

## Final streamed phase

Use `streamed/source.zip` and its matching wheel for the final target-four positives. Confirm source identity `8a43717de1b7ce80e7e457cff96e090ba73617299fcccdba0efbb26b547be51f`. The authoritative commands/settings are `streamed/protocol.json` and `streamed/measurement.json`. Positive bundles are in `streamed/bundles/`; run `ftqec verify-export BUNDLE --proof-work 200000000 --require-certified`. The larger allowance matters for independent replay; generated bundle instructions may show a smaller default. The clean-installed CLI receipt is `streamed/clean-cli.json`; the full suite log is `streamed-full-tests.log`. Earlier failures and subsequent resume logs are preserved separately.
