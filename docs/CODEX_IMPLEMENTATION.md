# Codex implementation and deployment operating procedure

This is a **reference adapter** for Codex, not an installed autonomous deployment system. Official Codex surfaces include CLI interactive work, bounded `codex exec`, SDK, and app-server. Choose one runtime before scheduling agent work.

## Optimization rules
1. **Single coordinator for ordered work.** Do not fan out tasks when each task depends on the previous patch.
2. **Parallelize read-only investigation** (architecture audit, tests gap review, security threat review) when supported. Separate mutable work via independent Git worktrees, disjoint files and integration owner.
3. **Lean instructions.** Keep `AGENTS.md` general. Load an individual `SKILL.md` only for the assigned role, then its references on demand.
4. **No duplicate effort.** Cache repository inventory keyed by commit SHA; invalidate when HEAD changes. Reuse test evidence only for the exact applicable commit.
5. **Bounded recovery.** Identify failing command, classify failure, apply smallest in-scope patch, rerun impacted checks. Maximum 3 distinct repair attempts per blocker, then BLOCKED with reproducible evidence.
6. **Check before promotion.** Missing CI, absent fixtures, unavailable network or unsupported platform is BLOCKED, not PASS.
7. **Human-owned release.** Generate a release dossier and proposed commands; never execute production deployment until separate, explicit authorization with target environment and artifact SHA.

## Codex entry procedure
- Read `AGENTS.md`, `docs/CODEX_IMPLEMENTATION.md`, `ROADMAP.md` and the target repo instructions.
- Run baseline checks: `git status --short`, `git rev-parse HEAD`, `git branch --show-current`, inspect manifest, build scripts, and required check status.
- Select next task with prerequisites satisfied; maintain a task contract and a small file ownership set.
- During implementation, run the **narrowest fast deterministic test** first, then the full repository gate as the change stabilizes.
- Ask for independent tests/review before marking release ready. Recheck if the commit changes.
- If blocked, write blocker, source, failure, action needed, and next unblocked task. Do not spin indefinitely or silently override policy.

## Operational commands
Inside this library, verify with:

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/codex_preflight.py --repo .
python3 scripts/release_gate.py --example
```

To inspect a target repository using the **read-only** preflight:

```sh
python3 scripts/codex_preflight.py --repo /path/to/target
```

To evaluate a real evidence packet with no network or deployment side effects:

```sh
python3 scripts/release_gate.py --evidence /path/to/release-evidence.json --artifact /path/to/candidate.pyz
```

## Suggested handoff prompt
> Read AGENTS.md and docs/CODEX_IMPLEMENTATION.md. Inspect the current checkout first. Select the first unblocked task from ROADMAP.md, create a task contract with exact file scope, implement on a feature branch, run the narrow and full checks, then request independent review. Classify failed or unavailable checks honestly; do not auto-merge, deploy, overwrite credentials, or weaken release gates. End with changed paths, commit SHA, command evidence, unresolved blockers, and next unblocked task.

## Runtime distinction
Do not assume an agent skill creates a subagent. A Codex CLI/SDK/app-server integration has to provide orchestration and tools. Prefer `codex exec` for single bounded noninteractive jobs; SDK for controlled programmatic workflow; app-server for a long-lived interactive integration. Sandbox/tool policy is configured in the harness, not guaranteed by this Markdown.

## Deployment protocol
1. Integration candidate with immutable commit and build artifact digest.
2. Passing independent validation, review, security, documentation.
3. Staging deploy via an approved executor and explicit authorization; verify health, logs and rollback.
4. Production promotion requires a **second** explicit release authorization referencing the same candidate and target.
5. Post-deploy observation and rollback decision; report outcomes with audit references.

Never substitute agent preference for operator authorization.
