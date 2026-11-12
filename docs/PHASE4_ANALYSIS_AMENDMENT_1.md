# Analysis amendment: measured checkpoint coverage

Analysis convention: `measured-checkpoint-coverage-1`.

The frozen execution programs treat an exhausted policy queue (or a completed adaptive population) as observed at later checkpoints, even if the process consumed less than the requested CPU. This conflicts with the request to mark unconsumed checkpoints NOT_REACHED. Execution snapshots are preserved verbatim, but their coverage field is not sufficient for a matched-compute claim.

The corrected analysis requires measured total algorithm CPU to reach each checkpoint: charged pool preparation, where applicable, plus completed worker CPU plus the whole controller-process CPU receipts. An exhausted queue below the checkpoint is NOT_REACHED. Missing controller receipts are UNCONFIRMED_ACCOUNTING, never imputed zero. Interrupted/censored accounting remains excluded from matched comparisons. Raw coverage is retained alongside corrected coverage.

This amendment changes reporting eligibility, not proposals, ranking, random streams, proof budgets, stopping decisions, certificates, or frontiers available at recorded event times. It applies identically to all policies. A new analysis identity distinguishes the corrected outputs from earlier interim analyses. No frozen execution protocol or raw snapshot is overwritten.

At amendment time only seed-74011 random and direct arms had completed under fixed-pool protocol `c2c08ca340d6876a900da2c4a56aac1151ea590f6c7ddeba1a5e7378071cdbf3`. Both stopped after consuming their last comparison checkpoint, so neither completed arm's checkpoint eligibility changes. The frontier arm was running. No adaptive, scaling, generation, or transfer arm had run. Earlier analyses remain retained and are superseded for checkpoint-coverage interpretation.

Queue exhaustion can still be described as a legitimate stopping outcome. It cannot be reported as actual expenditure of unused compute, and no additional candidates are introduced to manufacture a reached checkpoint. The final report must state how many planned matched comparisons remain unavailable for this reason.
