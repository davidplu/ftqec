# Population optimization

Random, witness-guided, multi-fidelity, hybrid, cost-aware and cost-hybrid strategies share the general stabilizer IR and physical evaluation engines. Hybrid generation combines code-only construction, broad random candidates, certified-parent mutations and occasional recombination. References never become seeds.

Evaluation records structural correctness and resources, then uses cheap physical fault screening, adaptive noisy simulation and rigorous finalist certification. Cost-aware allocation can bypass the funnel when estimated direct certification is cheaper. A verified below-target harmful witness is terminal; simulation failures and proof UNKNOWN are not hard-rejection rules. Unsupported decoding is separate from certification UNKNOWN.

The optimizer maintains distinct resource-only, estimated resource-LER, certified resource and certified-circuit estimated-LER archives. Simulation dominance is conditioned on decoder/noise/probability. Operational plateau is based on certified resource coordinates, not merely new circuit IDs; it does not prove optimality.

Local tasks run in isolated actual Python interpreter processes. Admission respects the maximum requested worker memory, a 512 MiB host reserve and CPU count. Queues submit at most twice the admitted worker count. Windows CPU includes completed kernel+user process time, startup and output serialization. RSS is an observed peak. Controller costs and nested decoder costs are separate to avoid double counting.

Generation checkpoints retain pending candidate IDs so an interrupted evaluation can resume without losing its population. Tasks and caches bind source, circuit, model, decoder, seed and work limits; operational cancellation/proof-directory paths do not change scientific identity. User cancellation and memory admission interventions preserve partial outcomes. An anytime run has no fixed global runtime limit.

Windows checkpoint replacement retries transient sharing violations while retaining the fully written temporary file. Active task time is measured with QueryUnbiasedInterruptTime, excluding standby; ordinary elapsed wall time is retained separately. Python and relevant runtime package versions are included in scientific task/cache identity. See [Microsoft's active-time semantics](https://learn.microsoft.com/en-us/windows/win32/sysinfo/interrupt-time).
