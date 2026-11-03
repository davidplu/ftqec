# FTQEC

FTQEC is an initial research implementation for generating, screening, simulating and selectively certifying stabilizer syndrome-extraction circuits. Broad population exploration is primary; witness-guided mutations are optional. Simulation estimates and rigorous certificates are separate evidence.

## Install and run

Python 3.11 or newer:

```sh
python -m venv .venv
# Activate your virtual environment, then:
pip install -e ".[dev]"
ftqec optimize examples/steane.json --output runs/steane
```

The default run is anytime: interrupt with Ctrl+C or use `ftqec cancel runs/steane`. Resume with the same input and configuration. For a finite smoke run, add `--generations 1 --population 8`. `--workers 2` enables bounded local process evaluation. No cloud credentials are required. No cloud resources launch automatically.

## Pipeline and evidence

General binary symplectic code validation → actual circuit compilation → independent noiseless measurement-flow checks → resource accounting → cheap single-fault screening → progressive Stim simulations → confidence-aware diverse selection → exact analysis of selected finalists.

The compiler supports bare, interval-flagged, GHZ-cat and parity-verified-cat extraction, interaction permutations, ancilla reuse/allocation and repeated rounds. A parity-verified cat is a compiled verification circuit; its name does not assert fault tolerance. All families must pass the same tests.

CSS and non-CSS stabilizer inputs are supported. Development examples include perfect, Steane/color, Shor and a small surface patch. The color/Steane and local-Clifford perfect-code controls are related constructions, not independent evidence of family-level generalization. Subsystem, bosonic and non-stabilizer codes are unsupported.

Archives distinguish structural validity, resource Pareto points, statistical promise, verified fault invalidity, UNKNOWN and independent certification. Resource coordinates always refer to one actual circuit. No statistical result proves circuit distance. No resource Pareto point is automatically rejected before reliability evaluation.

## Scientific scope and limitations

Certificates concern extraction with ideal initial/final syndrome boundaries and explicit operation-local faults. They do **not** certify complete physical memory or arbitrary-input logical protection. Every positive integer target is accepted; the current development ladder covers 1 through 10, including even targets. Eligible structural proofs and bounded exact fallback preserve UNKNOWN when obligations remain unresolved. See the current results for independently certified autonomous discoveries, separately from reference controls. The simulator prepares an ideal logical-Z sector. It supports correlation-aware matching where eligible and a limited one-mechanism lookup decoder with explicit fallback records. Neither decoder is claimed to be generally optimal.

No hardware placement or routing is in the execution path. See [scientific scope](docs/scientific_scope.md), [reproducibility](docs/reproducibility.md), [acceptance report](docs/acceptance.md) and [provenance](docs/provenance.json). Remaining features and failed/inconclusive experiments are reported openly. No broad screening-efficiency or architecture-superiority claim is made without positive controls and matched results.

## Collaboration

See CONTRIBUTING.md. This repository prepares a workflow for collaboration; it does not imply an authorship, affiliation or publication agreement. Publishing and licensing decisions remain with the project owner. Historical methods are traceable in provenance; the historical repository remains untouched.

Measured development results, including the negative small-pool CPU-saving result, are in [development measurements](docs/development_results.md).

## Cost-aware evaluation study

Use `ftqec optimize examples/steane.json --strategy costaware` for the additive cost-aware route. Direct certification can bypass screening and simulation. Sequential batches use candidate-wise alpha spending; UNKNOWN and unsupported methods stay separate.

The measured study found direct certification cheapest on both final-family target2 pools. See [results and all acceptance gates](docs/RESULTS.md), [cost model](docs/EVALUATION_COST_MODEL.md), [prospective protocol](docs/SCIENTIFIC_PROTOCOL.md), and [limitations](docs/LIMITATIONS.md). That earlier 10,000-circuit benchmark measured compilation/noiseless checks. The new scaling study separately records screening, sampled simulation and certification; neither is 10,000 complete evaluations.

To reproduce the frozen study without overwriting evidence, use a fresh local checkout at scientific commit `5f562c0` and an isolated environment, then run `python scripts/cost_study.py`. Its study directory refuses an existing run. The exact study-source archive is retained separately from the final portability fixes; current-release timings are not substituted for those measurements.

## High-distance certification

Run `ftqec certify circuit.json --target 9 --proof-work 20000000 --output runs/certificate`. The exported circuit and certificate can be checked independently. Use `--strategy hybrid` for code-only distance-aware population optimization, or `--strategy costhybrid` for empirical allocation with the direct-certification shortcut. See [measured results](docs/RESULTS.md), [local feasibility](docs/LOCAL_FEASIBILITY.md), [proof contract](docs/CERTIFICATION_CONTRACT.md), and [limitations](docs/LIMITATIONS.md).

## Autonomous integer-distance optimization

```sh
pip install -e ".[matching]"
ftqec optimize code.json --target-distance 10 --strategy hybrid --decoder auto --workers 2 --output runs/discovery
```

The optimizer consumes only stabilizers. It generates random and fault-propagation-aware candidates, checks semantics, simulates, and independently certifies finalists. All positive integer targets are accepted; 1–10 is the current validation range. Runs have no default global time cutoff and stop on user cancellation or declared operational convergence. Use `--convergence-generations` to configure unchanged-frontier patience. Per-task resource safeguards remain active.

`auto` uses correlated matching where supported and records any lookup fallback. Install the optional matching extra for the stronger decoder. Reliability comparisons remain decoder-conditional. After cancellation through `ftqec cancel`, remove the run's `cancel.json` marker before resuming the same configuration.

See [architecture generation](docs/ARCHITECTURE_GENERATION.md), [distance-aware synthesis](docs/DISTANCE_AWARE_SYNTHESIS.md), [integer-distance certification](docs/CERTIFICATION_1_TO_10.md), [simulation and decoding](docs/SIMULATION_AND_DECODING.md), and [optimization](docs/OPTIMIZATION_ALGORITHM.md). The current measured [results](docs/RESULTS.md) and [limitations](docs/LIMITATIONS.md) distinguish actual discovery, reference validation, unfinished scaling and uncertainty.

## General exact proofs and parallel architecture synthesis

```sh
ftqec certify circuit.json --target 5 --proof-method mitm --output runs/exact
ftqec optimize code.json --target-distance 10 --proof-method auto --workers 2 --output runs/parallel
```

The proof portfolio preserves graph potentials and location-aware DP, and adds full-signature, location-exclusive meet-in-the-middle exclusion plus a bounded SAT backend with independently checked branching proofs. A raw hyperedge is not silently decomposed for exact certification. Positive proofs require independent replay; incomplete work remains UNKNOWN.

Code-only hook-guided coloring, dependency scheduling, intermediate ancilla allocation and physical-witness flag repair extend the population optimizer. Actual compiled circuits determine Q, D, QD and gate counts. Compilation and noiseless validation now run in supervised workers, with the exact pending genome checkpointed before work. Resource limits do not convert a candidate into a fault-invalid circuit.

The preserved previous study (see results/competitive_export/baseline/previous/docs/RESULTS.md) documented two earlier milestones: a general-method target-five certificate on a raw non-graphlike CSS circuit, and independently certified autonomous target-ten extraction at Q=199 and depth 12. That earlier report preserves lower-qubit alternatives, unknown outcomes and the depth-eight reference. These results use ideal syndrome boundaries and do not certify full physical memory.

Read [general certification](docs/GENERAL_CERTIFICATION.md), [exact proof methods](docs/EXACT_PROOF_METHODS.md), [parallel scheduling](docs/PARALLEL_SCHEDULING.md), [ancilla optimization](docs/ANCILLA_OPTIMIZATION.md), and [the prospective protocol](docs/OPTIMIZATION_PROTOCOL.md). No standalone public Search command is introduced; inexpensive code screening remains distinct from deep single-code optimization.

## Competitive synthesis and inspectable delivery

The current campaign closes the target-ten depth gap: code-only seeds 24, 32 and 40 produce independently certified Q=199, D=8 circuits. The harder graph-ineligible non-surface target-five milestone remains unmet. The [current scientific report](docs/RESULTS.md) separates these outcomes, family-level failures, lower-qubit alternatives and decoder-conditional uncertainty.

```sh
ftqec list-results --run runs/discovery
ftqec export CIRCUIT_ID --run runs/discovery --format bundle --output exported/circuit
ftqec verify-export exported/circuit --require-certified
ftqec render-schedule exported/circuit/schedule.json --output exported/timeline.svg
```

Use `--format circuit-json`, `schedule-json`, or `stim` for individual artifacts. Export preserves the physical candidate ID and the exact serialized circuit ID separately; certificates bind the latter. Source mismatches are explicit, never accepted as positive proof. See [circuit export](docs/CIRCUIT_EXPORT.md), [schedule export](docs/SCHEDULE_EXPORT.md), [competitive scheduling](docs/COMPETITIVE_SCHEDULING.md), and [separator certification](docs/DECOMPOSITION_CERTIFICATION.md).


## General graph-ineligible extraction milestone

FTQEC now has a code-only, independently certified graph-ineligible target-five discovery for [[25,1,5]] under the operation-local ideal-boundary model. The finite frontier includes Q=36,D=329 and Q=105,D=46. The target-five proof uses exact MITM; new separator-domain reduction has a separate graph-ineligible target-three positive.

See [results](docs/RESULTS.md), [general certification](docs/GENERAL_CERTIFICATION.md) and [limitations](docs/LIMITATIONS.md). Decoder-conditional LER intervals overlap. Every schedule transformation requires fresh certification.
