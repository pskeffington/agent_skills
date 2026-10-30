# Codex execution queue — F0 to F8

**Status meaning:** TODO; ACTIVE; PASS (test evidence attached); FAIL; BLOCKED. Never change TODO directly to PASS without evidence.

| ID | Dependency | Owner | Deliverables | Hard acceptance | State / evidence |
| --- | --- | --- | --- | --- | --- |
| F0 baseline | None | integrator | fix scaffold defects; CI admitted | stdlib validation, tests, preflight PASS; observed CI | PASS: baseline `11906d5b5517ca8c1fa5dc31d2ec9502a8503803`; `scripts/validate.py` exit 0; 6 unittest cases exit 0; preflight exit 0; GitHub Actions run `41118580669` success (PR #2) |
| F1 contracts | F0 | architect + implementer | task, handoff, evidence parser and validators; dangerous path rejection | schema fixtures, malformed input and traversal tests | PASS: 4 contract tests; strict stdlib validation, supplied examples, role checks, traversal defenses |
| F2 journal | F1 | implementer | append-only atomic JSONL journal, checkpoint and replay | restart/replay, hash-integrity and interrupted-write fixtures | PASS: 3 journal tests; restart, hash chain, tamper detection, checkpoint, incomplete tail recovery |
| F3 scheduler | F2 | implementer | dependency graph, task ownership, leases, bounded retries, cancellation | cycles rejected; no duplicate active writer; blocked dependencies respected | PASS: 4 scheduler tests cover missing dependencies/cycles, ready gating, lease conflict/expiry/ownership, retry ceiling and cancellation |
| F4 toolbox | F3 | implementer + security | safe read-only Git/filesystem inventory, test execution adapter | traversal, symlink escape, command injection and timeout tests | TODO |
| F5 runners | F4 | integrator | dry-run runner, opt-in Codex CLI adapter and capability detection | no Codex required for offline tests; real runner never launches silently | TODO |
| F6 assurance | F5 | verifier + security | independent review identity, CI evidence ingestion and security summaries | missing/failed evidence and stale commit fail closed | TODO |
| F7 operator CLI | F6 | integrator + documenter | doctor/inventory/plan/status/run-dry-run/verify/replay/export | e2e offline fixture verifies exit codes and JSON schemas | TODO |
| F8 release | F7 | release controller + human | staging dossier, rollback runbook, artifact validation, deployment request boundary | synthetic and real checks differentiated; no unauthorized deployment | TODO |

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
