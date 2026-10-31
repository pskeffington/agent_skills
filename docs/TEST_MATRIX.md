# Engineering toolset acceptance test matrix

| Area | Positive case | Negative / adversarial case |
| --- | --- | --- |
| Contracts | valid minimal task and handoff | malformed JSON, extra fields, unknown role, null risk |
| DAG | independent parallel tasks | cycle, missing parent, blocked ancestor |
| Storage | replay valid journal | truncation, tamper, duplicate seq, interrupted append |
| Leases | acquire/release ownership | duplicate writer, expired-but-live lease, cross-worktree collision |
| Filesystem | confined read inside checkout | ../ traversal, absolute escape, symlink escape |
| Commands | allowlisted subprocess invocation | shell metacharacters, env leakage, timeout |
| Codex runner | fake CLI with supported version/flags completes in a clean linked worktree and only changes declared paths; configured verifier is reported separately from attestation status | missing verifier blocks before CLI subprocess, unverified/misbound/rejected attestation, primary/dirty worktree, wrong base, symlink path, ignored/out-of-scope file, timeout, duplicate run ID, cancellation, detached descendant; actual model/runtime containment remains BLOCKED until independently verified |
| Independent review | reviewer evidence for exact SHA | same identity as author, stale SHA, missing CI |
| Release | complete signed-off staging dossier with a valid detached approver signature against the configured trust store | absent trust store/OpenSSL/signature, unauthorized approver, signature mutation, wrong commit or artifact digest, dossier bytes mismatching supplied release artifact, malformed path input, symlinked artifact, missing rollback, synthetic fixture |
| CLI | JSON machine output and stable exit | bad args and corrupted state fail closed |
| RAG citation provenance | batch verification matches per-hit validity and reads each distinct source once | stale text/hash, bool line number, traversal path, symlink swap, unreadable source |
| RAG cache memory benchmark | baseline/candidate source manifests match; warm-hit memory and cold-miss latency are both recorded | output report accidentally enters the measured corpus or benchmark omits cold-miss cost |

Record test name, exact command, exit code and host environment. Mark unrun test BLOCKED, not PASS.
