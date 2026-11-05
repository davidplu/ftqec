# Supplied 2BGA benchmark development

Epoch: `results/2bga/epoch-20261105` (local evidence; supplied archive not automatically published).

Start with independently distance-4-validated [[24,2,4]], [[24,4,4]], and [[36,8,4]] dihedral examples. The supplied [[72,12,6]] abelian example is a separate challenging development case; its supplied distance requires independent evidence. There are no supplied executable reference circuits or schedules. The archive's notes and generator are provenance, not proof artifacts for its integer-programming lower bounds.

Freeze inputs, seeds, physical noise, sector, rounds and gate-duration conventions before comparisons. Development runs are not held-out final benchmarks. Preserve failed compilation, INVALID, UNKNOWN and resource stops. Measure both r=1 and r=d under the same physical boundary model to investigate any distance loss.

References to investigate independently: [Bravyi et al. syndrome circuits](https://www.nature.com/articles/s41586-024-07107-7), [general qLDPC compilation](https://arxiv.org/abs/2603.21499), and [2BGA constructions](https://arxiv.org/abs/2306.16400). Literature performance is not a locally reproduced matched reference result.

## Decoder follow-up

The [LDPC project's BP+OSD implementation](https://software.roffe.eu/ldpc/ldpc/bposd_decoder.html) accepts a binary check matrix and channel probabilities and uses ordered-statistics decoding when belief propagation fails to converge. Its [Stim/Sinter integration](https://software.roffe.eu/ldpc/stim_integration.html) is a concrete integration candidate. This is an investigation result, not an implemented or measured decoder in this campaign. A future adapter must document any independent-bit approximation to categorical operation-local fault alternatives, retain the unchanged physical sampler, and compare matched seeds/noise/tasks with uncertainty. Such a decoder approximation must never alter the exact certification inventory.

The development results and all acceptance gates are in [the scientific report](../reports/2bga/REPORT.md). The report lives at `reports/2bga/REPORT.md` from the repository root; raw local evidence is intentionally separate from the public source package.
