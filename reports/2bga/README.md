# 2BGA repeated-memory research results

[Full scientific report](REPORT.md) · [Reproduction instructions](REPRODUCE.md)

The code-only population discovered a verified-cat extraction architecture for the supplied independently validated [[24,2,4]] code. Four noisy rounds, physical preparation, and physical readout were certified at circuit distance at least four in both separately evaluated X and Z memory sectors. The certificates cover the declared operation-local fault universe, including correlated two-qubit alternatives and location exclusivity. They do not cover arbitrary-input encoding or implicit idle noise.

| Architecture | Physical qubits | Four-round depth X / Z | QD X / Z | Two-qubit gates per sector |
|---|---:|---:|---:|---:|
| Code-only verified-cat discovery | 192 | 96 / 94 | 18432 / 18048 | 2016 |
| Lower-qubit flagged candidate, certified in post-search follow-up | 168 | 200 / 198 | 33600 / 33264 | 1536 |
| Post-discovery generic serial baseline | 192 | 136 / 134 | 26112 / 25728 | 2016 |

All three pairs have independently checked target-four certificates. The internal serial comparison establishes a scheduling improvement at unchanged qubit and two-qubit-gate counts. It is not a reproduced published reference. The lower-qubit candidate remains a useful finite-population Pareto alternative; no global optimum is claimed.

The main implementation advance is exact streamed exclusion of harmful weight-three configurations without a stored quadratic pair table. Its checker independently reverses enumeration and checks physical location matching. A matched surface-code control showed lower measured CPU and peak worker memory than the existing meet-in-the-middle implementation; broader performance claims need additional matched experiments.

All 17 supplied codes passed group, CSS, rank, and span validation. Three small codes received independent algebraic distance-four checks. The larger [[72,12,6]] memory experiment remains UNKNOWN at requested target six, with verified lower bound four and weights four and five unresolved. Other supplied distances remain qualified claims where no portable proof was supplied.

The complete current suite passed 155 tests. Fresh installation, public optimization/resume, export/reconstruction, and installed positive-certificate verification were exercised. Historical artifact bytes were checked; the entire separate historical proof repository was not replayed.

The next scientific step is a matched executable-reference comparison with a validated correlated multi-fault decoder. Current short simulations with a one-mechanism fallback do not establish reliability superiority. Controller overhead and selective proof promotion also limit larger-population searches.

Raw source-bound results, failures, proof artifacts, schedules, input archive, and integrity manifest are retained in the local evidence epoch. That epoch contains supplied private correspondence and is excluded from Git. No evidence or source changes from this campaign have been pushed publicly.
