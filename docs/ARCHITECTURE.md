# Architecture: role-based engineering hierarchy

## Governing design
Distinguish (a) agent *role*, (b) reusable *skill*, (c) executable *runtime*, and (d) external *resource*. This repository defines (a), (b), and contracts for (d); it does **not** install (c). Do not claim that an `SKILL.md` launches another process.

| Level | Owner(s) | Authority | Evidence |
| --- | --- | --- | --- |
| L0 | Human / repository owner | Goals, access grants, release approval | Approval link |
| L1 | Orchestrator | Routing, prioritization, blocking | Task & status |
| L2 | Researcher, planner, architect | Read and propose design | Inventory, task plan, ADR |
| L3 | Implementer, integrator, documenter | Scoped branch changes | Patch, build, docs |
| L4 | Verifier, security reviewer, code reviewer | Independent critique (no self-approval) | PASS/FAIL/BLOCKED evidence |
| L5 | Release controller | Admit/reject candidate; request approval | Release decision |

The release controller may recommend deployment; only a configured executor with an explicit human authorization may act.

## Routing
Use `catalog/roles.json` as the authority map. Assign one accountable owner and a bounded write set. Delegate only when it reduces complexity or supplies required independence. Research, threat modeling and review may run in parallel *after their dependencies exist*. Avoid agent-to-agent loops and unlimited recursive delegation.

## Isolation
- Parallel implementation tasks must use separate branches or worktrees and non-overlapping file ownership; integration rebases/merges in a single accountable lane.
- Subagents receive only task-relevant inputs and tool rights; third-party text is lower-trust.
- All check results are tied to source commit and artifact digest. Any change to the source commit invalidates stale evidence for impacted checks.
- No role can assert another role's check without observing the actual tool execution or an auditable signed/provenanced report.

## Interop
Store portable skills under `.agents/skills/<name>/SKILL.md`. Project-wide Codex conventions live in `AGENTS.md`; GitHub Copilot also supports project skills at `.agents/skills/`. Support for runtime tool limits, subagents and approvals varies; implement these limits in the runtime as well.

See [resource chain](RESOURCE_CHAIN.md), [gates](RELEASE_GATES.md), [security](SECURITY.md).
