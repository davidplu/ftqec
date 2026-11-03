# Reproducing the general-extraction delivery

This delivery preserves FTQEC 0.1.0. Read RESULTS.md for the scientific claims and limitations, GENERAL_EXTRACTION_BRIEF.md for a short discussion summary, and GENERAL_CERTIFICATION.md for the exact reduction argument.

The archive contains the current source, tests, drivers, tested wheel, frozen protocols, all new raw outcomes, proof tables, complete circuits, and reconstructed schedules. Its root artifact_manifest.json binds every member to SHA-256. The separate package_verification.json records the archive hash and complete streamed member/CRC verification. FINAL_STATE.json records the final local Git commit. These external receipts avoid self-referential hashes.

Older scientific epochs remain in the separately preserved FTQEC_competitive_research_bundle.zip, identified by path and hash in the new manifest. Historical comparison links may require that archive extracted alongside this delivery. The new target-five bundles contain their own circuit and proof evidence.

Use Python 3.11 or newer in a fresh environment. Install the included wheel or `pip install .`; optional matching support is `pip install '.[matching]'`. The recorded dependency versions are in results/general_extraction/release under the scientific source identity. The tested isolated installation used offline copies of those dependencies; it did not use system site-packages.

To check a delivered certificate:

```text
ftqec verify-export BUNDLE_DIRECTORY --proof-work 20000000 --require-certified
```

Select a complete bundle listed in results/exports/SOURCE/finalists/index.json. Both circuit.json and schedule.json are present; verification reconstructs resources and checks the certificate binding. Public Optimize, resume, circuit/bundle/Stim/schedule export, render-schedule, and verify-export command transcripts are preserved in the clean_install.json receipt.

For a fresh public run:

```text
ftqec optimize examples/surface_small.json --output runs/fresh-example --target 2 --population 2 --generations 1 --workers 1
ftqec list-results --run runs/fresh-example
```

Repeating Optimize with the same output resumes its durable checkpoint. This small command checks the public workflow; it is not the target-five scientific experiment. The exact target-five population settings and input codes are in results/non_graphlike/SOURCE/population_study/protocol.json, with code-only seeds and measured computation. The corresponding scripts/general_extraction_population_study.py is the frozen driver. To repeat a scientific campaign, use a separate checkout/output destination, preserving the original frozen directories; do not overwrite completed evidence. Reconstruction checks can run directly against existing bundles.

The full historical/current test run and admission retry receipts are retained under results/general_extraction. The adopted source passed 118 tests. Four initial memory-admission failures remain recorded, followed by successful retries after available memory increased. Per-worker memory/CPU safeguards remain active; resource stops are UNKNOWN, not physical invalidity.

The domain quotient is exclusively a proof transformation. Simulations and decoder probabilities use the original physical fault model. Certification is scoped to the explicit operation-local fault model and ideal boundaries; it does not establish arbitrary-input physical-memory performance or hardware routing correctness.

No public push or cloud execution was performed.
