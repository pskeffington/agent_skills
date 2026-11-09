# Codex adapter provenance (2026-10-30)

Primary sources:
- [Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform): CLI exec for bounded jobs, SDK for application control, app-server for persistent orchestration; host owns permission and approval policy.
- [Codex reusable skills and CI](https://developers.openai.com/blog/skills-agents-sdk): repository AGENTS.md, skills in .agents/skills, and automated tests/verification.
- [Iterating development workflows with Codex](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex): project-specific AGENTS.md and staged execution conventions.
- [Multi-agent](https://developers.openai.com/api/docs/guides/agents-api/multi-agent): separate independent subagents with bounded instructions; shared-file editing needs coordination.
- [Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals): tool policy and human approval are enforced by runtime, not merely by prompts.

Design decision: policy-only DAG with audited stage contracts, lightweight read-only preflight, fail-closed release dossier and separate runtime adapters. No CLI flags are assumed without version verification.
