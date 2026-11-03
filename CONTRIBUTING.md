# Contributing

Create a feature branch and submit a pull request for scientific changes. Keep main stable. Explain the mathematical scope, evidence level and limitations. Run `pytest`, `ruff check src tests` and `mypy src` before review; inherited code may still require typing cleanup as documented in acceptance.

Architecture additions must compile to the common Circuit IR, pass signed stabilizer-measurement and logical-preservation flows, and compare optimized signatures against forward propagation and independent simultaneous-fault replay. Include negative and positive controls. Never relabel UNKNOWN as INVALID or infer distance from Monte Carlo.

Evaluation tiers must use a source-bound serializable Task and durable result artifacts. Explicitly declare noise, decoder, seed, limits, CPU/wall scope and statistical decision rule. No billable infrastructure without authorization. No reserved held-out inputs in development.

Contributors must confirm rights to submitted work; no authorship or publication agreement is assumed.
