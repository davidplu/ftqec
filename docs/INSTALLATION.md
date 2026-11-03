# Installation and troubleshooting

## Environment

Use a dedicated virtual environment with Python 3.11 or newer. Python 3.12 is the CI version. Install from the repository root with `python -m pip install -e '.[dev,matching]'`. Core requirements are declared in `pyproject.toml`; the matching extra adds PyMatching. Development tools include pytest, Ruff and mypy. Avoid mixing a globally installed package with a different source checkout.

For an end-user installation use `python -m pip install .` or `python -m pip install '.[matching]'`. Confirm `ftqec --help` works. The package's scientific source identity is separate from its public version number: two installations labeled 0.1.0 may contain different research source bytes.

## Common failures

| Symptom | Diagnosis and action |
|---|---|
| `ftqec` command not found | Activate the environment and reinstall with that environment's Python |
| `No module named tests` | Use the repository root; the test package and pytest path configuration must be present |
| Matching unavailable | Install the matching extra; inspect recorded fallback before comparing LER |
| Worker admission reserve | Free memory or reduce requested concurrency; do not lower safety reserves to claim completion |
| UNKNOWN after proof work | Inspect bounds and unresolved obligations; increase a justified per-task budget or choose an eligible exact method |
| Source mismatch during verification | Reconstruct the matching source environment; do not rewrite certificate identities |
| Historical artifact missing | Obtain the original evidence package; missing artifacts are not scientific invalidity |

Do not copy credentials or virtual environments into a repository. Preserve interrupted task receipts before retrying. The scripts directory contains research drivers with historical paths and is not a generic command-line API.
