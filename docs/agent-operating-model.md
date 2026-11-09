# Agent operating model

## Routing and boundaries
The root `AGENTS.md` applies to work on this library. At the start of a task, select the specific skill by its frontmatter description, load its `SKILL.md`, and inspect referenced resources. If multiple skills apply, define their division of responsibility and preserve the most restrictive safety rule. Do not treat documentation as authorization to operate on another repository or device.

## Reusable work order
Record these fields in a task or PR:
- **Objective:** measurable outcome, task owner, and non-goals
- **Inputs:** source locations, revisions, hashes, licenses and access permissions
- **Outputs:** exact files/artifacts and expected formats
- **Dependencies:** required approvals, data, tools, hardware and upstream work
- **Execution:** ordered steps with smallest permitted mutation scope
- **Acceptance:** deterministic test commands and observable success criteria
- **Evidence:** URLs, commit SHAs, command logs, timestamps and confidence levels
- **Rollback:** how to restore previous known-good state
- **Status:** PLANNED, IN_PROGRESS, PASS, FAIL, BLOCKED or NOT_RUN

## Development cycle
1. Inventory the exact repository state and existing work before edits.
2. Build a dependency graph and prioritize unblocked, high-value tasks.
3. Implement on an isolated branch; keep checkpoints and avoid unnecessary refactors.
4. Run test fixtures, validation, static checks, failure paths and security gates.
5. Compare observed results with acceptance criteria; document uncertainty rather than upgrading a hypothesis to fact.
6. Submit a draft PR for incomplete or gated work. Promote only after required checks and reviews.
7. After a failure, produce a concise failure record (symptom, reproduction, root cause or hypothesis, remediation, regression check) so later work improves without weakening controls.

## Evidence hierarchy
Use `observed` for directly inspected artifacts or executed tests; `reported` for third-party claims; `inferred` for reasoned interpretations; and `unverified` when evidence is missing. Include a source reference for material claims. For tests, use `PASS`, `FAIL`, `NOT_RUN`, or `BLOCKED` with commands and context. Do not turn a self-report into an independent verification.

## Automated enforcement (not installed globally)
A consuming repository must opt in through a project-local `AGENTS.md`, pinned skill revision, CI configuration and required status checks. Suggested gates: skill/frontmatter validation; path/link checks; deterministic skill tests; secret scanning; license checks; protected branches; and human review for high-risk changes. Do not claim that Codex or other agents are forcibly bound by prose alone.

## Current skill-specific gates
- **Firmware reverse engineering:** offline-first authorized acquisition, provenance manifest, untrusted extraction isolation, evidence classification, and exact-device recovery/rollback review before any flash operations. Existing Python tests and tool-manifest validator are CI-backed.
- **Portfolio Valuation Systema:** source-repo inspection is read-only; private valuation output is isolated to the designated Portfolio repository; no unreviewed financial publication, monetization assumptions, or cross-family double counting.

## Release and maintenance
Version substantial instruction changes through Git history and PRs. Keep descriptions short enough for routing and long procedures in references. Require every new executable to have a documented run command, deterministic sample inputs, and meaningful tests. Maintain a concise changelog in PR descriptions; do not make unsupported claims of production readiness.
