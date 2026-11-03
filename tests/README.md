# Regression tests

Run `python -m pytest -q` from the repository root. Install the development extra first. `scientific` contains exactness, fault semantics, solver, population and export regressions; `integration` covers the public pipeline. Small exhaustive oracles are independent checks, not positive certificates for large research circuits.

Package markers make helper imports portable in CI. Do not skip a failing scientific test to make a badge green; inspect the failure and preserve its evidence. Historical experiment replay requires the original artifacts described in [the evidence guide](../docs/EVIDENCE_GUIDE.md).
