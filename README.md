# FTQEC

FTQEC 0.1.0 is a research toolkit for synthesizing, screening, simulating, and independently certifying stabilizer-code syndrome-extraction circuits. It compiles actual circuits and preserves the distinction between physical resource estimates, simulation results, harmful fault witnesses, and rigorous certificates.

**Research status:** the certification campaign is paused. The default branch preserves the baseline implementation. Experimental MITM indexing changes and their negative performance results are on `codex/certification-research-20261102`; they are not adopted improvements. This repository is a publication snapshot. Large historical proof databases and full local Git history are not included; see [publication scope](PUBLICATION_STATUS.md).

## Quick start

Python 3.11 or newer is required; CI uses Python 3.12. From a clone of this repository:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e '.[dev,matching]'
ftqec --help
ftqec optimize examples/steane.json --output runs/steane --generations 1 --population 8 --workers 1
ftqec list-results --run runs/steane
```

This finite run is a smoke experiment, not a promise of a certified finalist. Omit `--generations` only when you intend an anytime optimization run. Per-task safeguards still apply. Matching is optional; install `.[dev]` without it for the base development environment. Decoder fallback must be reported when interpreting reliability results.

## What FTQEC does

1. Validate the supplied stabilizers and derive code information.
2. Generate bare, flagged, cat, and verified-cat extraction candidates with order, scheduling, and ancilla-allocation choices.
3. Compile circuits and check noiseless measurement semantics.
4. Compute Q, D, QD, and two-qubit gate counts from the circuit.
5. Screen physical faults and simulate selected candidates.
6. Apply exact certification to selected finalists and retain certified Pareto alternatives.
7. Export circuits, schedules, and verification bundles.

General stabilizer input compatibility is retained; CSS codes are the main research focus. This is not a complete hardware placement/routing compiler or a universally efficient certifier.

## Input example

```json
{
  "name": "steane",
  "n": 7,
  "generators": ["IIIXXXX", "IXXIIXX", "XIXIXIX", "IIIZZZZ", "IZZIIZZ", "ZIZIZIZ"]
}
```

Each Pauli string has `n` symbols. The input validator checks the stabilizer representation. A code's algebraic distance and an extraction circuit's detector-model distance are different quantities; metadata alone is not proof of either.

## Certification and export

Use `list-results` to obtain a real candidate ID, then substitute it for `CIRCUIT_ID`:

```bash
ftqec export CIRCUIT_ID --run runs/steane --format bundle --output exported/steane
ftqec verify-export exported/steane --require-certified
ftqec render-schedule exported/steane/schedule.json --output exported/steane/timeline.svg
ftqec certify exported/steane/circuit.json --target 5 --proof-method mitm --proof-work 20000000 --output runs/certification
```

`--require-certified` exits unsuccessfully if a positive certificate is not independently established. Exporting a circuit by itself does not certify it. Source mismatch, exhausted work, and resource intervention must remain explicit.

## Reading outcomes

| Outcome | Meaning |
|---|---|
| CERTIFIED | Required exclusion bound independently verified under the declared model |
| INVALID | Legal harmful physical faults below the target independently replayed |
| UNKNOWN | Proof incomplete; retain verified partial bounds and outstanding obligations |
| UNSUPPORTED | Chosen method cannot soundly handle the input/model |

Certificates use operation-local faults and ideal syndrome boundaries. They do **not** establish arbitrary-input physical-memory protection. Monte Carlo results are conditional on decoder, noise model, preparation sector, sample size, and uncertainty. Zero observed failures is not zero logical error rate.

## Documentation

- [Documentation guide](docs/README.md)
- [Installation and troubleshooting](docs/INSTALLATION.md)
- [CLI workflows and recovery](docs/USER_GUIDE.md)
- [Developer guide and CI](docs/DEVELOPMENT.md)
- [Certification methods and scientific contract](docs/CERTIFICATION_GUIDE.md)
- [Evidence and reproduction](docs/EVIDENCE_GUIDE.md)
- [Source structure](src/README.md), [tests](tests/README.md), [experiment scripts](scripts/README.md)
- [Historical results](docs/RESULTS.md) and [limitations](docs/LIMITATIONS.md)
- [Large-population report](reports/large_scale/FTQEC_SCIENTIFIC_REPORT.md)

Historical reports describe specific frozen epochs and may refer to artifacts retained only in the original evidence repository. Their numerical claims are not automatically revalidated by a passing software test suite.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Keep scientific changes narrow, preserve negative and unresolved outcomes, and provide independent proof checks and matched measurements for claimed improvements. Do not initialize autonomous searches with successful reference schedules. See [LICENSE](LICENSE) for the existing licensing terms.
