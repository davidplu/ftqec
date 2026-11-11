# Fixed-pool protocol A, version 2

Version 2 preserves every scientific choice in `PHASE4_PROTOCOL.md`: code, rounds, fault model, architecture generator, five seeds, five policies, 32-shot pre-proof simulation, certification portfolio, upper-witness search, compute checkpoints, hypervolume reference, and statistical contrasts. The original document is embedded in the new executable protocol alongside this amendment.

The executable protocol is `results/phase4/epoch-20261111-v2/protocol-A-v2.json`. The new source snapshot is `frozen-A-v2/src`. Version 1 remains preserved at `results/phase4/epoch-20261111/`; do not resume it as though it were version 2 or combine its partial preparation costs with the new policy comparisons.

## Reason for amendment, before policy outcomes

The first preparation run exposed repeated full-payload decompression in progress accounting. After each task, `PopulationStore.totals()` reread the complete growing task archive, including large cat-circuit payloads. This was an instrumentation scalability defect, not evidence for or against a promotion policy. No policy comparison or certification promotion had started when version 1 was stopped through its durable cancellation mechanism.

The retained version-1 process receipt records 583.984375 controller CPU seconds over 1018.5757394 elapsed seconds and a sampled controller peak of 1,609,662,464 bytes. These are measurements of the interrupted preparation run, not a matched policy comparison. A separate bounded microbenchmark on its saved database stopped payload-based accounting at the unchanged 512-MiB ceiling; scalar accounting completed. Because the old measurement was censored, no completed-method speed ratio is claimed. Raw receipts are in the version-1 epoch's `accounting-profile/` directory.

The correction reads task counts, CPU, wall time, and sampled worker peaks directly from the scalar execution table. Full task payloads remain intact for independent audits and separately measured offline analysis. Newly completed answers are reused in memory instead of being immediately decompressed a second time from disk. No proof, fault, circuit, or resource-ranking semantics changed. The public export checkpoint metadata is also now emitted directly by the experiment runner.

The new run starts from code-only input and regenerates its pools. No completed version-1 construction, screen, or proof is transferred as free work. All interrupted version-1 records remain available, including the cancellation reason and complete controller process receipt.

The adaptive runner has been implemented and tested on small engineering fixtures, but it is not part of Experiment A's outcome. Its scientific execution still requires its own frozen protocol and separate reporting after the fixed-pool study.
