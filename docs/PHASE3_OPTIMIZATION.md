# Paired repeated-memory architecture discovery

The experimental paired-memory driver generates architectures from the supplied
2BGA code, constructs actual six-round X- and Z-memory circuits, screens physical
faults, samples selected candidates with BP-OSD, and certifies selected finalists.
Only a pair with independently verified certificates in **both** sectors enters
its paired resource frontier. A single-sector certificate is retained separately.

```powershell
ftqec optimize code.json --memory-rounds 6 --phase3 --target 6 --output run `
  --strategy structured --candidate-goal 100 --window 10 --promotion 2 `
  --workers 1 --seed 73029 --proof-method auto --proof-work 50000000 `
  --decoder bposd --memory-shots 32 --memory-noise 0.001
```

Install the decoding dependencies described in the user guide before selecting
BP-OSD. Thirty-two shots are a development screening batch, not adequate evidence
of logical-reliability superiority. The code input must contain the supported
two-block group-algebra representation, not just an unlabeled stabilizer list.

Omit `--candidate-goal` for an anytime run. This driver sets no worker CPU or
wall-clock timeout. Memory admission, the 512 MiB worker ceiling, proof-work
limits, and explicit cancellation remain active. `--experiment-cpu` is optional:
it checks accumulated worker plus controller CPU at window boundaries. A window
can overshoot this measurement checkpoint; it is not a strict matched-compute
budget and does not terminate a running proof. Do not label two such runs a
matched-compute comparison without inspecting their actual accounting.

## Architecture proposals and scientific boundaries

Proposals include code-derived X/Z term orders, shared ancilla batches, shuffled
check orders, independent subsets of the measured check basis, and existing
flagged/cat/verified-cat families. Ancilla budgets rotate through the requested
strata. The requested budget is a proposal parameter; recomputed circuit resources
are authoritative. A term-order parity prefilter rejects unwanted ancilla cross
couplings, followed by the existing signed-instrument correctness check.

The generator never imports or seeds from the published reference implementation.
Witness-guided proposals select an interaction axis implicated by a replayable
physical witness. This is a heuristic proposal mechanism, not a proof that the
mutation repairs that fault. Incompatible swaps fall back to random code-derived
orders and are labeled accordingly. Descendants must be evaluated again.

Policies are `random`, `structured`, `witness`, `multifidelity`, `hybrid`,
`costaware`, and `costhybrid`. Their implementation does not establish an empirical
advantage. The cost-aware policy uses observed certified-family costs; it is not
a calibrated universal prediction model.

The physical model remains the declared operation-local model with the repeated
memory preparation/readout boundaries. This experimental driver rejects explicit
idle-noise requests. Certificates do not imply arbitrary-input memory fidelity,
hardware routing correctness, or decoder-independent reliability.

## Automatic exact certification

`auto` considers the number of projected mechanisms and estimated enumeration
work before selecting the time-collapse reduction for repeated-memory circuits.
The complete physical inventory is retained, checked independently, and supplied
to the proof backend. Legacy selection remains available as `auto_legacy`.
Manual backend choices remain available. The selector is currently a conservative
measured-size heuristic; it does not exhaustively profile every competing method.

The reduced syndrome equations yield a lower bound, not an assumed equivalence
between a memory experiment and one extraction round. The pair/triple producer
and canonical-branch checker independently enumerate the reduced minimum. A new
optional lifting proof uses a parity vector constant within every full preimage
class, with an odd XOR across the support. An independent dot-product checker
verifies these vectors without trusting the Gaussian-elimination producer.
This excludes a full-syndrome lift for that support. Excluding **all** reduced
minimum supports improves the lower bound by exactly one, not arbitrarily many.
Inconclusive affine proofs fall back to the existing exact lifting algorithms.

Native integer bitsets replace Python set allocation in canonical branching.
The original set implementation remains as a regression oracle. This is a local
Python optimization, not a port of the upstream accelerated C/OpenMP kernels.

## Checkpointing, cancellation, and evidence

The output directory contains `population.sqlite`, `checkpoint.json`,
`summary.json`, `compute.json`, `frontier.json`, and per-candidate proof folders.
The database stores source-bound tasks, exact circuits, proposal ancestry, results,
and execution measurements. The paired frontier aggregates each resource using
the worse sector and retains nondominated alternatives.

Repeat the same command and output directory to reuse completed tasks. Source,
code, and scientific configuration must match. A later source revision requires
a new experiment directory or the preserved source runtime. Do not edit source
files underneath an active run. Pending proposal windows are durably recorded.

To cancel, create `cancel.json` containing `{}` in the run directory. The worker
supervisor observes cancellation; interrupted outcomes remain distinct from
scientific invalidity. Cancelled task answers are currently cached, so rerunning
does not automatically retry every cancelled task. A proof-stage continuation
that resumes an internal enumeration frontier is not yet implemented; completed
tasks and verified partial bounds are preserved, but unfinished enumerations may
restart. These are explicit limitations of the current recovery implementation.

Use the existing public export and verify-export commands with an exact candidate
identity from the SQLite run. Keep its matching source runtime with the bundle.
Export reconstruction, resource recomputation, and proof verification are separate
checks; generating an export alone does not establish certification.
