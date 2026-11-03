# Certification research paused

Paused at user request. This branch preserves experimental changes, not an adopted improvement. The published baseline remains on the default branch; its original local history is preserved separately.

The baseline suite passed 126 tests. Both historical target-5 positives were independently verified again. Eager range indexes increased CPU cost and caused one positive to hit its resource limit. Deferred index construction restored positive completion but did not improve total CPU: low-qubit 21.21875 versus 19.390625 seconds; low-QD 37.265625 versus 15.34375 seconds. These are single-run measurements. The prior UNKNOWN remained UNKNOWN under all three configurations. No new target-7 or target-10 certificate was obtained.

The experimental MITM changes are retained for inspection, not recommended as the default. The recorded baseline and benchmark execution totals do not establish ten hours of continuous research. The original campaign start and amended deadline are preserved in results/certification_research/campaign_20261102. The source-bound packets contain the actual backend, independent-verifier result, and resource-limit reasons. HGP target-3 used the pre-existing pair checker and does not demonstrate a MITM improvement.

This commit includes compact raw task receipts and their hashes. Large proof databases, population studies, and historical archives remain locally preserved; they are not represented as uploaded by this note. No frozen population campaign was resumed. The separately modified historical SQLite copy from interrupted worktree creation is excluded.
