# Adaptive scheduler

Use `ftqec optimize examples/steane.json --strategy costaware`. This is an additive route through the same scientific evaluation tasks, durable checkpoints and guarded local workers. Existing policies remain available.

A direct certificate is selected if predicted certification CPU is at most screen plus simulation CPU. Otherwise a screen is eligible when rejection probability times certification cost exceeds screen cost. Remaining uncertainty receives simulation, then certification. Every seventh decision position reserves direct exploration. Only independently replayed harmful faults cause hard fault rejection; UNKNOWN remains uncertain.

Sequential simulation uses deterministic independent batch seeds, 64/256 shots in the research protocol (public optimizer uses its configured batch sizes). At look t, Hoeffding bounds spend alpha/(t(t+1)); the union bound protects all declared repeated looks for each candidate. Stop when interval width is at most0.2 or after two looks, retaining remaining uncertainty. Candidate-wise coverage is not simultaneous population-wide coverage. The old fixed-funnel Wilson estimates remain explicitly fixed-policy evidence; they are not relabeled as confidence sequences.

The default optimizer has no global time cutoff. User-controlled generations, cancellation, per-task guards and duplicate-only batch plateaus remain distinct. A plateau is not global optimality. Frontier history records cumulative worker/coordinator compute. Worker crashes receive at most one retry; memory/CPU/time interventions are not blindly retried.

For the prospective batch sizes, Hoeffding at look t spends alpha/(t(t+1)), so the probability of any interval miss is at most the sum of those terms, alpha. This argument requires the declared deterministic potential batch sizes; arbitrary data-dependent sample counts at a given look require a different bound.
