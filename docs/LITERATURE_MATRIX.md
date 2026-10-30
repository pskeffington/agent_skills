# Literature and standards matrix

**Verified:** 2026-10-29. Source of truth: `data/literature_matrix.json`. These are short engineering interpretations, not quotations or compatibility certifications.

| ID | Source | Engineering decision | Status |
| --- | --- | --- | --- |
| AS-001 | [Agent Skills format specification](https://agentskills.io/specification) | Validate directory/name/description and references; distinguish strict format from policy | primary |
| OA-002 | [OpenAI Build Skills](https://learn.chatgpt.com/docs/build-skills) | Require trigger and negative-trigger examples; retain optional OpenAI metadata | primary |
| OA-003 | [OpenAI Codex customization](https://learn.chatgpt.com/docs/customization/overview) | Use repo policy separately from the skill entrypoint | primary |
| OA-004 | [OpenAI Plugins Skills](https://developers.openai.com/plugins/concepts/skills) | Do not confuse repository skills with connectors or remote execution | primary |
| VS-005 | [VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills) | Use canonical .agents/skills; validate client-specific installation instead of assuming equivalence | primary |
| OA-006 | [OpenAI Codex engineering workflows](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex) | Keep acceptance gates and phased planning versioned | supporting |
| OA-007 | [OpenAI Skills old catalog README](https://github.com/openai/skills/blob/main/README.md) | Do not base current installations on obsolete catalog instructions | legacy |
| OA-008 | [OpenAI prompt injection safety](https://openai.com/safety/prompt-injections/) | Constrain scopes, obtain confirmation, and avoid broad tool authority | primary |
| OA-009 | [OpenAI agent builder safety](https://developers.openai.com/api/docs/guides/agent-builder-safety) | Add adversarial and side-effect tests before release | primary |
| GH-010 | [GitHub secure your organization](https://docs.github.com/en/code-security/tutorials/secure-your-organization/protect-against-threats) | Use read-only permission and no external Actions in bootstrap CI | primary |
| NIST-011 | [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) | Map assurance gates to governance, measurement, and risk response | supporting |
| MCP-012 | [MCP Skills Extension specification](https://skills.extensions.modelcontextprotocol.io/specification/stable/skills) | Do not assume remotely supplied skills grant execution authority | primary |

## Synthesis

- **Normative format vs vendor behavior:** AS-001 is the cross-client format reference; OpenAI and VS Code docs are implementation/usage guidance and need separate compatibility testing.
- **Instructions vs tools:** An `AGENTS.md` file provides repository governance; `SKILL.md` supplies a task-specific workflow; MCP or external connectors provide live capabilities subject to approval.
- **Progressive loading:** keep trigger metadata crisp, the entrypoint compact, and detail in references that can be loaded only when relevant.
- **Threat boundary:** security guidance motivates least privilege, untrusted-data isolation, human confirmation, and attack-case evaluation; a YAML linter alone is not a security control.
- **Legacy warning:** the old `openai/skills` README explicitly identifies that catalog as deprecated; do not treat its installation examples as current authoritative guidance.

## Maintenance rule

When any primary source materially changes, update the JSON record with verification date, adjust architecture or gates, and add regression tests for the affected assumption. Do not replace a standards claim with an untested vendor inference.
