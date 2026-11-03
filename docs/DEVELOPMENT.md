# Development and CI

## Local checks

From the repository root in an isolated development environment:

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m ruff check src tests --select E9,F63,F7,F82
python -m mypy src --ignore-missing-imports --follow-untyped-imports
```

The test package includes explicit package markers so shared scientific helpers resolve consistently under the pytest console script and `python -m pytest`. CI runs the full suite rather than dropping failing scientific tests. The selected Ruff rules cover syntax/undefined-name classes, not a claim that the entire codebase satisfies every style rule. Mypy uses the configuration shown above; this is not strict-mode typing.

## What tests demonstrate

Small independent exhaustive oracles check fault semantics and proof logic. Integration tests check public workflows, persistence, and export. Passing tests does not replace a source-bound positive certificate on a target research input. Resource-limited tests require diagnosis; do not turn them into unconditional skips.

## Change discipline

Keep source edits separate from frozen experimental epochs. Record the exact code and runtime used for a measurement. Never mutate the compiler or proof engine while workers from the measured source are still running. After an algorithmic change, rerun relevant independent oracles, then matched scientific comparisons and the complete suite. Compare actual CPU and wall time, not just work counters or candidate counts.

Research scripts may reference external historical evidence. Ordinary unit/integration tests should construct tractable inputs themselves wherever practical. A missing historical archive must be explicitly documented rather than represented as a failed physical circuit.
