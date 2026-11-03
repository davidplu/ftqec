# Reproducibility and execution

Every run binds source bytes, input/signs, configuration, seed and Git commit. Every task binds circuit bytes, code identity, noise, decoder, source and limits. Checkpoint resume rejects identity changes. Each content-addressed task receipt is retained; failed and UNKNOWN results remain evidence.

Local evaluation uses bounded populations and independently monitored subprocesses. Admission reserves host memory; each process has sampled RSS, CPU and wall safeguards. Sampling may overshoot and is not a kernel-enforced memory quota. Cancellation files are checked between generations and by active supervisors; per-task safeguards remain in force. Whole-process CPU uses the last live sample and may omit one polling interval at exit; exact timed evaluation-body CPU is recorded separately. Ctrl+C preserves the checkpoint. A future remote controller must use the same task identity and idempotent artifact publication.

`ftqec worker task.json answer.json` is a working stateless task interface for an already provisioned worker with identical source. This is portability, not a deployed cloud backend. No cloud credentials or infrastructure were provisioned, and no cloud deployment is claimed.

Private migration audit and raw development logs are under `.private/`, excluded from Git. Public provenance contains only scientific component hashes and the source commit. The historical hardware code and experiments remain in the original repository; none are copied into the new core.

Run `python scripts/benchmark.py` for a declared finite development comparison and false-rejection audit. Run `pytest` for scientific regression and integration tests. Benchmark quality is not claimed from software tests alone.
