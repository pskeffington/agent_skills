# AGENTS.md — agent_skills repository

## Mission and scope
Maintain a reusable library of auditable skills. This file governs contributions **to this repository**. Follow the specific `skills/<name>/SKILL.md` for domain execution; this document does not override skill-level authorization, privacy, safety, or review gates.

## Startup protocol
1. Read `README.md`, this file, and the target `SKILL.md`; load supporting references only as needed.
2. Inspect repository state, existing work, task requirements, permitted tools, and the smallest affected path set.
3. State acceptance criteria and identify the authoritative evidence for each. Distinguish **observed**, **reported**, **inferred**, and **unverified**.
4. Choose a reviewable feature branch. Do not overwrite unrelated edits, force-push, merge, publish, or deploy without authorization.

## Execution contract
- **Plan:** define the task, input/output artifacts, dependencies, implementation order, explicit exclusions, and verification gates.
- **Implement:** prefer deterministic scripts and narrow edits over broad prose or sweeping refactors. Make procedures reproducible and idempotent where feasible.
- **Validate:** run all applicable skill tests plus syntax/schema checks and negative tests. Record exact commands, environment constraints, and observed output. An unexecuted test is `NOT_RUN`, never `PASS`.
- **Review:** report security/privacy, license, provenance, reproducibility, failure recovery, and scope boundaries. Supply diffs and evidence in a pull request.
- **Handoff:** specify changed paths, branch/commit, verification status, remaining blockers, and next actionable task. Never invent CI results or claim human approvals.

## Agent roles (logical, not automatically provisioned)
- **Orchestrator:** task decomposition, ordering, scope and cross-agent reconciliation.
- **Research/evidence:** source inventory, authoritative reference selection, claim provenance.
- **Builder:** smallest implementation consistent with task contract.
- **Verifier:** independent tests, regression checks, adversarial/negative cases, explicit pass/fail.
- **Security/governance:** secrets, privacy, licensing, authorization, rollback and stop/go gates.
- **Documentation:** keep README, instructions, examples, change notes and acceptance criteria aligned.

An agent may perform multiple roles when resources are limited, but must not imply independent verification that did not occur. Skill-specific reviewers retain their own vetoes.

## Blocking and escalation
Classify blocked steps as `BLOCKED_ACCESS`, `BLOCKED_INPUT`, `BLOCKED_ENVIRONMENT`, `BLOCKED_DEPENDENCY`, `BLOCKED_SECURITY`, or `BLOCKED_REVIEW`. Record cause, evidence, safe fallback, next action and responsible decision maker. Work on independent authorized steps may continue; never silently bypass a gate.

When a script or build fails: preserve logs, reproduce, isolate cause, propose the minimal fix, rerun the failing check and relevant regressions, then document the outcome. Record reusable lessons in the relevant skill or reference; do not self-modify protections or relax passing criteria solely to make CI green.

## Repository integrity
- Keep skill names lowercase, path slugs stable, and YAML frontmatter limited to `name` and `description`.
- Skills should carry precise trigger descriptions, scoped instructions, supporting references, executable checks when needed, and optional `agents/openai.yaml`.
- Keep root documentation about shared governance. Do not duplicate extensive skill-specific directions here.
- No secrets, credentials, personal data, unauthorized firmware images, or private valuation output in commits.
- Source repositories scanned by portfolio valuation are read-only; private valuation records belong only in the authorized Portfolio location.
- Firmware flashing requires exact-device recovery and authorization gates; no skill or agent may infer clearance.

## Change acceptance
A PR is ready for review when its purpose and scope are explicit; changed instructions point to existing paths; relevant automated checks pass or are transparently blocked; security and provenance implications are reviewed; and rollback is feasible. Require human review for material governance, publication, or valuation changes. Instructions alone do not enforce Codex behavior: repository CI and branch rules provide technical gates.
