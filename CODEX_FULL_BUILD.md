# Codex master build instruction — software-development agent toolset

## Mission
Build a working, local-first, auditable **engineering agent toolset** from the current policy/skill scaffold. Continue task-by-task to a production-*ready* release candidate, not an unauthorized deployment. Use a single coordinating Codex session and delegated specialists only when the installed Codex runtime actually supports them.

## Preflight (mandatory, before edits)
1. Read `AGENTS.md`, `CODEX_KICKOFF.md`, `docs/CODEX_IMPLEMENTATION.md`, `docs/RELEASE_GATES.md`, `docs/SECURITY.md`, `ROADMAP.md`, `docs/TOOLSET_BLUEPRINT.md` and `docs/IMPLEMENTATION_QUEUE.md`.
2. Identify local branch and HEAD, worktree changes, Python version, `codex --version` if present, active CI status, existing GitHub PR, available network permissions and executable build tooling. Do not assume capabilities.
3. Run baseline: `python3 scripts/validate.py`; `python3 -m unittest discover -s tests -v`; `python3 scripts/codex_preflight.py --repo .`. Preserve actual exit codes. `release_gate.py --example` must exit 2 because its synthetic dossier is blocked.
4. If any existing test fails, fix that deterministic defect before implementing new modules. If tooling or CI is missing, mark the specific gate BLOCKED; continue unrelated safe tasks.
5. Use feature branch and small task-scoped commits. Never overwrite user edits, amend unrelated history, merge the PR or modify production.

## Build plan
Execute **F0–F8** in dependency order as documented in `docs/IMPLEMENTATION_QUEUE.md`. Each phase: inspect → design contract → implement → unit tests → integration tests → independent review → documentation → checkpoint. Complete only tasks with satisfied dependencies. Commit a bounded pass; update the queue with evidence and blockers. Do not endlessly repeat work.

### Architectural baseline
- Keep standard-library-only Python as default for the initial executable local engine. Rust adapter may be added later behind an optional interface; no new mandatory external dependency without approval.
- A deterministic orchestrator manages a JSON task DAG, role router, artifacts, state machine, append-only journal and recoverable leases. Specialist skill text is loaded lazily.
- Do not confuse skills with processes. Provide an explicit `AgentRunner` interface and a safe `DryRunRunner`; an actual Codex SDK/CLI runner must be opt-in, capability-checked, and version-tested.
- Never embed shells, eval, dynamic imports or arbitrary code in task-contract data. Paths must be restricted to a configured checkout.
- Structured `PASS/FAIL/BLOCKED` outcomes, commands and artifact provenance must survive restart without changing prior decisions.
- Any role requiring independence must have distinct invocation identity from the implementer. Shared model instance with separate prompt is not sufficient for an approval claim.

## Core tooling to implement
1. **Discovery/index:** repository tree, manifests, tests, instructions, owners, dependency inventory, freshness stamps.
2. **Planning:** atomic task contracts, DAG builder, scoped resource chain, priority and blockers.
3. **Delegation:** role registry, capability matrix, task routing, concurrency quotas, leases and cancellation.
4. **Code work:** bounded patch proposal, diff inspection, allowlisted writes, isolated worktree integration.
5. **Verification:** test command registry, immutable evidence, reproducibility and reviewer separation.
6. **Security:** trust boundaries, secrets redaction, dependency/source review and tool permission policy.
7. **CI:** GitHub workflow check classification, logs, retry policy, required check admission.
8. **Release:** artifact digest, staging dossier, rollback, explicit approval, signed/recorded promotion request.
9. **Operator UX:** status/queue/log/inspect/replay/export CLI with machine-readable JSON output.

## Definition of done
- CLI supports `doctor`, `inventory`, `plan`, `run --dry-run`, `status`, `verify`, `evidence`, `replay`, `release-check`, `export`, and `help`, with documented flags and stable exit statuses.
- Real `run` must not be enabled until a tested, permissioned runner exists. All default runs are side-effect-free or explicitly documented local writes.
- Simulate crashed processes and replay to verify task/lease recovery and no duplicate write scheduling.
- Test malicious paths, cycles, malformed contracts, stale SHA, failed CI, absent reviewer, invalid approval, and tool timeout.
- CI must execute offline fixture tests and validators; no simulated result may be presented as an actual field validation.
- Produce `docs/OPERATOR_MANUAL.md`, `docs/THREAT_MODEL.md`, `docs/RELEASE_RUNBOOK.md`, `docs/TEST_MATRIX.md` and a real evidence report.
- Confirm independent review and owner approval before any staging/production deployment; build a release candidate even if those approvals remain BLOCKED.

## Checkpoint format
For every engineering pass, output: phase/task ID, base/head commit SHA, paths changed, commands plus exit codes, regression outcomes, G0–G6 state, unresolved risk, next unblocked task and whether a production action occurred (default no).

## Error recovery
Retry at most three **targeted** repairs per distinct root cause. Never bypass failing tests, weaken checks, forge evidence, reset user work, change permissions, or add external dependencies as a workaround. Mark external/unavailable gates BLOCKED and proceed only on unrelated work.

Begin F0 immediately after preflight; continue the queue in order within the available Codex execution session. Do not claim indefinite background execution or auto-production deployment.
