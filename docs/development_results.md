# Development measurements

Scientific source: `c24fc39b1fb7544a27b299172bab01c42a08e1221bc87ac4d5bd01fd9dcd6c4d`. Scientific commit: `3cf0bae`. All measurements below use this source. Earlier epochs remain preserved separately.

## Population compilation

1000 actual circuits compiled and passed independent noiseless flow checks; 1000 distinct physical circuit identities. CPU 39.297 s; wall 39.610 s; 25.25 circuits/s. This measures compilation/checking, not thousand-candidate simulation or certification.

## Matched development comparison

Same inputs, physical probability 0.001, declared decoder, seeds, population4 and two generations. Target2; no equal-compute or superiority claim. Worker CPU uses last-live process samples; exact body counters are retained separately.

| Code | Policy | Distinct circuits within run | Certified target2 points | Sampled worker CPU (s) |
|---|---|---:|---:|---:|
| surface_small | random | 8 | 4 | 0.438 |
| surface_small | witness | 7 | 4 | 0.453 |
| surface_small | multifidelity | 7 | 4 | 0.500 |
| surface_small | hybrid | 7 | 4 | 0.609 |
| perfect5 | random | 8 | 4 | 0.469 |
| perfect5 | witness | 7 | 4 | 0.406 |
| perfect5 | multifidelity | 7 | 4 | 0.719 |
| perfect5 | hybrid | 7 | 4 | 0.609 |

Points can repeat across strategy runs. Every positive is an independently checked ideal-boundary extraction detector-model certificate, not a complete physical-memory certificate. The witness-policy label denotes the new optional mutation policy, not a matched historical-optimizer baseline. All four labels found positives; these small results establish no superior strategy.

## Positive and frontier retention

Fixed pool: 6 independently certified target2 positives; 6 retained; 0 false rejections; 0 lost certified resource-Pareto points. Certification calls 8→6 (25% reduction). Baseline CPU 0.562500 s; screening/simulation/certification policy CPU 0.703125 s. CPU saving -0.140625 s: **no CPU saving demonstrated**.

The policy deliberately includes Monte Carlo while the baseline certifies directly. The benchmark tests actual end-to-end overhead on this small pool; it does not establish target3 safety, true resource–LER frontier retention, independent family generalization or cloud performance. Larger matched-positive pools and cost allocation are the next research step.

## Reproduction

`python scripts/benchmark.py`, `python scripts/retention_audit.py`, `python scripts/population_throughput.py`. Each prospectively records its own source/input/settings and retains raw outcomes. Do not overwrite existing epochs when changing source.
