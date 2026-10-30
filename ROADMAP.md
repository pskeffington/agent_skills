# Development roadmap

| Phase | State | Deliverable | Acceptance |
| --- | --- | --- | --- |
| A0 research | DONE | primary sources, role/skill/runtime distinction | research links and architecture recorded |
| A1 design | DONE | L0–L5 hierarchy, stage DAG and resource provenance | machine-readable catalogs |
| A2 skills | IN PROGRESS | portable orchestrator and specialist skills | each has valid SKILL.md |
| A3 contracts | IN PROGRESS | task, handoff and evidence schemas + examples | stdlib validator and tests pass |
| A4 automation | PLANNED | CI harness and runtime-specific adapters | permissions, branch protection, no self-approval |
| A5 pilot | PLANNED | run a bounded change in one selected target repo | real traces, evidence, failure recovery |
| A6 production | BLOCKED | controlled deployment integration | owner approval, threat review, rollback, monitoring |

## Next work queue
1. Establish local checks as a required protected-branch check after CI is configured.
2. Add Codex/Copilot-specific role adapters without hardwiring proprietary syntax into portable skills.
3. Add transaction-safe event logging, a work-lease mechanism and handoff replay tests.
4. Pilot a small, non-production task and evaluate false PASS, missing evidence, duplicate handoffs, context load and cost.
5. Add signed build provenance and per-repository permissions only after an authorized runtime exists.

This commit establishes the control plane; it does not deploy or execute a multi-agent service.
