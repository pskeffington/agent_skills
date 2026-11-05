# Codex development agent instructions

## Central agent-skills doctrine (Codex development)

**Mandatory for every Codex development task in this repository.** The canonical reusable agent and skill catalog is [pskeffington/agent_skills](https://github.com/pskeffington/agent_skills). The central registry is the source of reusable procedures; this repository's own AGENTS.md, security controls, ownership boundaries, release gates, and task-specific acceptance criteria remain authoritative and must not be weakened.

1. **Discover before editing.** Identify the repository's active task and read its local AGENTS.md, applicable nested instructions, task tracker, and existing tests. Resolve relevant registered skills/agent roles from `agent_skills` before planning or changing code. Record the registry commit SHA and the exact skill paths/revisions used. Do not assume an unverified skill path exists.
2. **Plan with agents.** Assign appropriate architecture, implementation, testing, and independent-review roles based on task complexity. Use specialized skills (Rust, audio, biomedical, GIS, security, etc.) when applicable; do not substitute a generic coding pass where a registered specialist exists.
3. **Execute with evidence.** Use isolated branches/worktrees, bounded tasks, reproducible commands, and truthful evidence. In PR descriptions record task ID, skills/roles invoked, registry revision, validation commands/results, failures and blockers. Merely mentioning a skill is not proof of executing it.
4. **Validate independently.** Run applicable unit/integration/security/CI checks. Have a separate review role check the implementation against acceptance criteria. A missing tool, unavailable skill or unrun test is a documented BLOCKED state, never a claimed pass.
5. **Learn without weakening controls.** Feed sanitized, reproducible failures and repairs into the FACTORY-002 learning process in `agent_skills`. Proposed skill improvements require independent evaluation and review. Do not transmit private code, credentials, operational secrets, protected research data or sensitive personal information to a public registry.
6. **Fail closed on agent noncompliance.** If required skill resolution or execution is unavailable, record BLOCKED-AGENT and do not claim an agent-compliant release. Once FACTORY-003's trusted `agent-compliance` check and branch protections are deployed, treat that check as a mandatory merge gate. Until then, these instructions are policy, not proof that technical enforcement is enabled.

**Precedence:** immutable safety/authorization boundaries and repository-specific security/acceptance gates take precedence over generic central guidance. Central skills augment, not replace, domain-specific controls. Agents must not relax approvals, branch protection, CI, or deployment policy to finish a task.

References: [FACTORY-002 learning](https://github.com/pskeffington/agent_skills/issues/14) and [FACTORY-003 enforcement](https://github.com/pskeffington/agent_skills/issues/15).
