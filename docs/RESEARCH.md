# Research notes and design provenance (2026-10-30)

1. **Agent Skills open specification:** `SKILL.md` with name/description, optional `scripts/`, `references/`, `assets/`; progressive loading avoids a universal mega-prompt. https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx
2. **GitHub Copilot:** recognizes project skills under `.agents/skills`, `.github/skills`, or `.claude/skills`; custom agents are distinct from skills. https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills
3. **OpenAI Agents SDK:** manager-as-tools vs specialist handoff differs in who owns the response; keep a manager in charge for bounded engineering work. https://developers.openai.com/api/docs/guides/agents/orchestration
4. **OpenAI guardrails:** validation and human approval are different mechanisms; explicit approval is needed for side-effecting actions. https://developers.openai.com/api/docs/guides/agents/guardrails-approvals
5. **Codex AGENTS.md:** instructions persist at repository scope; workflows/gates can be separate approved artifacts. https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex
6. **NIST SP 800-218 (SSDF 1.1):** secure development belongs throughout the lifecycle; use security review and evidence at release. https://csrc.nist.gov/pubs/sp/800/218/final
7. **NIST SP 800-218 Rev. 1:** version 1.2 was an *initial public draft* as of the cited NIST listing; do not mislabel it the final baseline. https://csrc.nist.gov/pubs/sp/800/218/r1/ipd

## Interpretation / design choices
- Skills are portable role instructions, not guaranteed concurrent agent processes.
- Keep manager ownership of state; use explicit handoffs and per-role write permissions.
- Create machine-readable catalogs and task/evidence contracts to reduce ambiguous delegation.
- Preserve zero mandatory third-party Python packages in the validator.
- Record desired enforcement separately from implemented enforcement; runtime integration and deployment are future gates.

Revalidate upstream documentation before adding runtime-specific adapters.
