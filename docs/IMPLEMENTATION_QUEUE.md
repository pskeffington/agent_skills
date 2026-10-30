# Codex execution queue — F0 to F8

**Status meaning:** TODO; ACTIVE; PASS (test evidence attached); FAIL; BLOCKED. Never change TODO directly to PASS without evidence.

| ID | Dependency | Owner | Deliverables | Hard acceptance | State / evidence |
| --- | --- | --- | --- | --- | --- |
| F0 baseline | None | integrator | fix scaffold defects; CI admitted | stdlib validation, tests, preflight PASS; observed CI | PASS: baseline `11906d5b5517ca8c1fa5dc31d2ec9502a8503803`; `scripts/validate.py` exit 0; 6 unittest cases exit 0; preflight exit 0; GitHub Actions run `41118580669` success (PR #2) |
| F1 contracts | F0 | architect + implementer | task, handoff, evidence parser and validators; dangerous path rejection | schema fixtures, malformed input and traversal tests | PASS: 4 contract tests; strict stdlib validation, supplied examples, role checks, traversal defenses |
| F2 journal | F1 | implementer | append-only atomic JSONL journal, checkpoint and replay | restart/replay, hash-integrity and interrupted-write fixtures | PASS: 3 journal tests; restart, hash chain, tamper detection, checkpoint, incomplete tail recovery |
| F3 scheduler | F2 | implementer | dependency graph, task ownership, leases, bounded retries, cancellation | cycles rejected; no duplicate active writer; blocked dependencies respected | PASS: 4 scheduler tests cover missing dependencies/cycles, ready gating, lease conflict/expiry/ownership, retry ceiling and cancellation |
| F4 toolbox | F3 | implementer + security | safe read-only Git/filesystem inventory, test execution adapter | traversal, symlink escape, command injection and timeout tests | PASS: 4 toolbox tests cover inventory, confined reads, traversal/symlink escapes, command allowlist and runner output |
| F5 runners | F4 | integrator | dry-run runner, opt-in Codex CLI adapter and capability detection | offline fake-CLI tests; isolated worktree; scope, timeout, output and cancellation controls | ACTIVE/BLOCKED for runtime admission: opt-in `codex exec` adapter implemented on the current worktree with linked-worktree, scope, timeout, output, cancellation and POSIX process-group controls. It now requires an external process-containment attestation; the library does not create a container/cgroup/Windows Job Object. Independent code and security reviews PASS for commit `19cc04c`; detached descendants fail closed when process-tree stop cannot be verified. CI run `41126463087` passed for `19cc04c`. Actual containment/runtime integration and Windows process-tree control remain unverified. Real model invocation is not enabled by default. |
| F6 assurance | F5 | verifier + security | independent review identity, CI evidence ingestion and security summaries | missing/failed evidence and stale commit fail closed | PASS: 7 assurance tests; stale commit, failed/unknown CI, missing checks, malformed findings, severity threshold, same invocation and non-assurance reviewer fail closed; offline GitHub Actions export ingestion added |
| F7 operator CLI | F6 | integrator + documenter | doctor/inventory/plan/status/run-dry-run/verify/replay/export | e2e offline fixture verifies exit codes and JSON schemas | PASS: CLI integration tests cover JSON output, valid/blocked/failed exits, corrupted journal, task planning/replay/export, verified RAG search and cache reuse; operator manual added |
| F8 release | F7 | release controller + human | staging dossier, rollback runbook, artifact validation, deployment request boundary | synthetic and real checks differentiated; no unauthorized deployment | PASS (local readiness tooling): structured G0-G6 evidence and exact commit/artifact-bound review, security, staging and approval attestations required; deterministic standalone zipapp for source commit `1c3c7a4` built and recorded in `docs/CANDIDATE_ARTIFACT.md`; artifact smoke passes and synthetic example exits 2; no staging evidence or deployment performed, so release candidate G6 remains BLOCKED |

## Task handoff discipline
For each row, create task ID `F<n>-<workstream>`, scope include/exclude files, baseline SHA, owner, fixture, tested acceptance, exact exit code, blocked reason and reviewer. Commit each phase separately.

### F0 must check existing scaffold issues
- Validate skill frontmatter, source paths, role registry and graph resource references.
- Detect old examples that are intentionally placeholders (all-zero SHAs) and never use these as actual evidence.
- Review GitHub workflow trigger semantics and checkout of PR merge refs; avoid declaring CI operational without seeing a run.
- Check the release evaluator against malformed input, stale attestation and synthetic evidence.
- Document any packaging gap between the skill library and installable runtime.

### Parallel work guidelines
Research, design and security investigation may run concurrently after F0. Only one stage mutates a shared file. Reviews of changed code must happen after an identifiable candidate commit.

### Release acceptance
F8 is a **release-readiness** target, not permission to deploy. For production require operator-designated environment, immutable artifact digest, passing CI and staging, independent signoff, rollback drill and explicit approval. If any absent, state BLOCKED and preserve the candidate.

## Security hardening follow-up (2026-10-30)

Task contract: `examples/security-hardening-task.json`, completed on source commit `6ec0e4e1a978d7b105e31fe49821d0f914b8043a` from base `3de8560005c75d3bdc75b3c3a9bf4f836cadab6f`. This closes review findings across F2/F3/F4/F6/F8. Local evidence: 62 unit tests PASS; structural validator PASS; Codex preflight PASS; synthetic release dossier BLOCKED with exit 2 as required; observational benchmark `docs/benchmarks/rag-benchmark-security-hardening-2026-10-30.json` recorded (99 files, 4,081 lines; median cold build 91.2 ms, warm search 10.8 ms, warm cache validation/load 212.6 ms; no speedup claim). GitHub Actions run `41121581800` passed for earlier commit `3de8560005c75d3bdc75b3c3a9bf4f836cadab6f`; run `41122761580` is the commit's code-validation run, still queued. Independent code review and security follow-up reviews PASS for the reviewed fixes. At that checkpoint the CLI lacked a configured approval verifier; the F8 signed-verification follow-up below addresses the integration, while real staging and approval evidence remain absent. No staging or production action occurred.

## F8 signed-approval verification follow-up (2026-10-30)

Task contract: `examples/release-approval-verifier-task.json`, implemented by `e0d2140` and hardened by `97d0d11`. Offline SHA-256 detached signatures are checked against an operator-managed public-key allowlist; accepted keys are RSA >=2048 or approved ECDSA curves. Missing OpenSSL or trust store remains BLOCKED. Signatures bind identity, authority reference, evidence ref, invocation, decision, candidate commit, and artifact digest. Local crypto and CLI tests pass; independent code and security reviews PASS; GitHub run `41123812623` passed for `97d0d11`. External evidence and trust-store governance remain operator-verified. Staging acceptance remains required; no deployment occurred.

## F8 artifact digest verification follow-up (2026-10-30)

Task contract: `examples/artifact-digest-task.json`, implemented on `3927da1` and symlink-hardened on `ff0b9cd`. Local validation: 71 tests pass, validator/preflight pass, synthetic release check remains BLOCKED (exit 2). Independent code and security reviews PASS for parent-component symlink handling. Three zipapp builds are byte-identical with SHA256 `cbab15f6c626ab460b42c6fc40ee0a4e95b6712762e8c03494051530c06ae844`; doctor and correct-digest artifact-check pass. A stale expected digest correctly failed before rerunning with the current digest. GitHub CI run `41124333344` passed for `ff0b9cd`; the follow-up documentation record is pending its CI run. No artifact transfer or deployment occurred.

## Retrieval optimization queue (R1–R6)

| ID | Dependency | Deliverable | Status / evidence |
| --- | --- | --- | --- |
| R1 | F4 | Local lexical index with line/hash provenance and stale-hit verification | PASS: RAG tests from remote commits `a80684e`–`3ad179e`; included in 40-test suite |
| R2 | R1 | Operator CLI search command with JSON, root checks and stable exits | PASS: CLI verifies every path/line/hash before returning hits; no-answer returns empty JSON; invalid limit/root return BLOCKED exit 2; cache remains explicit opt-in |
| R3 | R2 | Persisted content-addressed index with atomic writes and corruption/symlink rejection | PASS: 3 cache tests cover reuse, content SHA invalidation, malformed payload with recomputed checksum, and symlinked directory/entry rejection; atomic replace and fsync; CLI integration confirms opt-in cache reuse |
| R4 | R3 | Labeled offline evaluation fixtures for precision/recall/no-answer/injection | PASS: 5 labeled cases; `scripts/evaluate_rag.py` reports file-level precision@2 1.0, recall@2 1.0 across answerable queries, and zero no-answer false positives; fixture-only metric scope is explicit |
| R5 | R2 | Extend validation across schemas, skills, cross-references, release evidence | PASS: validator checks skill registry/metadata presence, role/resource-chain references, schema structure and required/property consistency, and validates all registered examples against their schema; release dossier example remains semantically BLOCKED |
| R6 | R4/R5 | Reproducible baseline/optimized benchmarks and independent review | BLOCKED for release completion: clean-checkout five-trial report is preserved in `docs/benchmarks/rag-benchmark-2026-10-30.json`; 97 files, 3,482 lines; cold build 81.9 ms / 3.20 MB, warm cache 192.9 ms / 7.68 MB, warm search 8.73 ms; no speedup claim. Independent review on the security-hardening batch passed; retrieval generalization remains fixture-only and cache loading is slower than cold indexing in the recorded benchmark. |


## F5 Codex CLI execution follow-up (2026-10-30)

Task contract: `examples/codex-runner-task.json`, based on `55f5f4e4c214a56899fc8fdf0854d8646ab944fb`. Adapter now has explicit opt-in execution using the installed Codex CLI's `exec --json --ephemeral --ignore-user-config --sandbox workspace-write --cd <worktree> --output-last-message <temp> -` interface. It requires a clean dedicated Git worktree at the exact task base commit, validates contract paths, bounds prompt/output/runtime, terminates process groups on timeout/cancel, and checks changed paths against `scope.include`. Offline fake-CLI coverage is being extended for containment and duplicate run IDs; latest focused tests pass 12/12 and the full suite 79/79; validator and preflight pass; synthetic release check is BLOCKED (exit 2) as required. Current installed CLI is 0.147.0; documented global flags were cross-checked against the [Codex CLI reference](https://developers.openai.com/codex/cli/reference). Independent reviews identified detached-session escape and Windows process-tree containment gaps; execution now fails closed without externally verified process containment. Security review passes with external containment explicitly unverified; independent code review is pending final current-tree confirmation. Repository tests pass 79/79; validator/preflight pass; synthetic release remains BLOCKED (exit 2). No real model invocation, staging, or deployment was performed. Scope enforcement is post-run inside the disposable worktree; callers must discard a worktree after a scope violation.
