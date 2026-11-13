# Exact mechanism reduction and repeated-memory certification

This experimental, opt-in backend implements a transparent Python proof path
motivated by [arXiv:2611.08247](https://arxiv.org/pdf/2611.08247), especially
Supplementary Lemma 2.2 and Sections 5.1 and 5.4. It does **not** vendor the
authors' accelerated kernels or claim their benchmark performance.

The upstream implementation is [tropidist](https://github.com/Fanerst/tropidist),
audited at `b03ec2d4077f287f89f97b5c2c16ce5ce17c2c58`, MIT license.
The new FTQEC source preserves the original physical fault inventory and all
existing certifiers. The current `auto` portfolio can select this path for eligible
repeated-memory circuits; `auto_legacy` retains the previous selection behavior.
See [the paired-memory guide](PHASE3_OPTIMIZATION.md) for the later integration.

## Public use

```shell
ftqec certify circuit.json --target 6 --proof-method time_collapse --proof-work 50000000 --output runs/collapse
ftqec optimize code.json --memory-rounds 6 --target 6 --proof-method time_collapse --proof-work 50000000 --no-time-limits --output runs/population
```

`--proof-work` bounds individual enumeration/checker operations, not CPU time.
Worker memory protections remain in effect. An incomplete task is UNKNOWN.
Use a new output directory for a new scientific attempt. The optimizer retains
its source-bound task cache and durable checkpoints. Individual enumerations
restart from their stage; arbitrary internal search-stack resume is not yet
implemented. The direct certify command runs in the caller process; use the
existing task worker interface when process memory isolation is required.

The certificate contains a portable projection recipe. The existing
`ftqec.certification.exact.verify` entry point rebuilds the physical inventory
and rechecks the recipe, without trusting a solver completion flag or requiring
the producer's temporary tables. Complete optimizer bundles use the existing
export and verify-export tooling. Full production export validation of every
new large finalist remains a separate delivery check.

## Mathematical contract

For physical location i, let A_i be its complete allowed alternatives, including
identity. Each alternative contributes a detector vector s and logical vector l.
A legal configuration selects at most one nonidentity alternative per location;
its weight is the number of such locations. Minimize weight subject to XOR(s)=0
and XOR(l) nonzero.

For the declared operation-local model, every one-qubit location has all three
nonidentity Paulis, every two-qubit location has all fifteen, and measurement
outcome flips form a binary group. The adapter checks the full allowed label set
and pairwise composition of propagated detector, logical, and data effects.
Explicit idle operations are included; unlisted idle locations are not added.
Neither an ideal-boundary extraction certificate nor a single memory-sector
certificate acquires a stronger physical-memory scope through this adapter.

Merge only identical **joint detector and logical** signatures into unit-cost
mechanisms, retaining every physical alternative and its location as provenance.
This is not equality of feasible physical configurations or probabilities.
It is equality of their minimum harmful weights:

1. Any legal r-location configuration maps to a mechanism support of size at
   most r after parity cancellation, so mechanism minimum <= physical minimum.
2. Choose a physical representative of each selected mechanism. Compose any
   representatives sharing a location. Closure supplies an allowed alternative
   at that location, or identity, with unchanged effects and no greater cost.
   Thus physical minimum <= mechanism minimum.

These inequalities prove equality (paper Lemma 2.2). Without the closure and
completeness checks the transformation must not issue certificates. It must not
be used as a decoder likelihood model: probabilities and multiplicities are
not preserved.

## Detector projection and time collapse

For any explicit binary row map T, `D e = 0` implies `T D e = 0`; logical rows
are unchanged. Therefore d(TD,L) <= d(D,L). Row groups store the parity map.
Equal reduced joint signatures retain lists of full-column preimages.

For repeated CSS memory, syndrome-difference detectors are grouped by check
across time. The optional sector projection retains checks of the declared
memory basis and retains separately grouped flag channels. Dropping opposite
sector constraints is a **relaxation**, not an assumed equality. The lower-bound
argument needs neither graph eligibility nor a symmetry of all circuit rounds.
It covers noisy preparation, resets, measurements, destructive readout,
correlated Paulis, multiple logical bits, and explicit idles by applying T to
their complete, unchanged signatures.

The stronger paper statement that certain reduced problems are independent of
round count requires additional repeated-circuit assumptions. FTQEC does not
infer a result for a different number of rounds from this implementation.

If the projected minimum is L, all its minimum supports are enumerated. A
full weight-L harmful support must map to exactly L nonzero distinct projected
columns: any cancellation or discarded zero column would give a smaller
projected harmful support, contradicting minimality. Thus all full weight-L
supports are covered by choosing one preimage per class of every minimum.
Complete exclusion of these choices raises the lower bound by one. The producer
uses a two-sided syndrome join; the checker uses layered reachable-syndrome sets.
This implementation does not extrapolate this argument to further weights.

Every accepted upper witness is composed at physical locations and replayed with
the separate Boolean-array physical fault simulator. A reduced witness alone
does not establish an upper bound for the original circuit.

## Algorithms and independent checks

- Producer: exact single/pair, pair/single, pair/pair, triple/pair joins through
  weight five, retaining all minimum supports. This is a small-instance Python
  implementation, not the upstream optimized completion-table search.
- Checker: canonical residual branching. Anchor the smallest support index;
  select an unsatisfied row; partition extensions by their first selected
  candidate in that row. Stops at zero syndrome are sufficient for a minimum
  harmful support, which cannot contain a proper zero-syndrome subset.
- Inventory: backward propagation in the producer; independent forward
  propagation before acceptance and again during standalone replay.
- Safety: bounded pair tables, reachable-state sets, and counted work. Reaching
  a safeguard preserves incomplete obligations, never an inferred positive.
- Portable proof recipe: exact circuit/source/model bindings, original inventory
  hash and count, explicit row groups, lower bound, and physical upper witness
  when available. Reverification reconstructs rather than trusts saved tables.

The paper's dense rank DP tracks only extendible syndrome states on each cut,
with width rank(prefix)+rank(suffix)-rank(total), and solves separate nonzero
logical-row queries. Its sparse weight-truncated DP uses bounded forward/backward
states and complete joins; its branching solver uses completion tables and
admissible pruning. Those scalable upstream kernels are not ported here.
The unmodified NumPy rank-DP evaluator was reproduced on recorded random oracles.
The accelerated path needs a compatible C/OpenMP build and Unix-specific support
not available in this Windows environment. No universal polynomial-time exact
distance algorithm is claimed: cut width, support search, and lifting can grow
exponentially.

## Evidence and limitations

See `results/tropidist/epoch-20261109/RESEARCH_REPORT.md` for source-bound controls,
the actual six-round circuits, failed full-sector attempts, replay receipts,
timings, and acceptance gates. Historical Phase 2 and November 5 evidence was
not overwritten. A faster certificate alone is not evidence of improved
architecture search, lower logical error rate, or global optimality.
