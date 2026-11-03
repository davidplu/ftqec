# Population storage

A single-controller SQLite database stores candidate metadata, compressed exact circuit payloads, source-bound task requests/results, ancestry, selection decisions, and evaluation history. Payloads have SHA-256 content bindings. The controller uses the existing run lock. SQLite uses WAL and FULL synchronous commits.

Circuits are stored once per exact candidate identity. Updating screening or simulation does not rewrite all circuits. Task intents are committed before launch and results are committed as the bounded supervisor returns them. An interrupted unfinished task remains queued and may be retried under the same scientific identity; completed cached outcomes are checked before reuse. Resource-limited outcomes remain UNKNOWN.

The lightweight checkpoint points to the database and records input/configuration/source identity and aggregate progress. It does not serialize every circuit or historical task. Export resolves one candidate directly from the database, preserving the public bundle and schedule formats. The previous JSON storage path remains supported.

Selection uses lightweight resource metadata and loads only a bounded parent/evaluation working set. Exact skyline calculation groups identical resource tuples while retaining every physical tie. Certified lower-qubit alternatives remain archived.

Do not copy an active SQLite database alone while it has a live WAL. Close the run or use SQLite's backup API for a consistent snapshot. Final delivery must preserve the closed database, exact source, protocol, and integrity manifest.
