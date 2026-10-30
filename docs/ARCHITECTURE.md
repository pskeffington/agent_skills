# Architecture and decisions

## Boundaries

`AGENTS.md` contains durable repository engineering policy. `.agents/skills/<name>/SKILL.md` contains narrowly scoped, independently invocable tasks. `agents/openai.yaml` is optional provider presentation metadata, not part of the portable core. `references/` provides conditional context; `scripts/` only stores reviewed deterministic code; `assets/` holds templates and output resources.

`data/literature_matrix.json` is the source-evidence record. `docs/LITERATURE_MATRIX.md` is its readable engineering synthesis. `catalog/skills.json` is generated from skill metadata with `scripts/index_skills.py`; the validator rejects stale indexes. The repository is not an MCP host, agent runtime, policy enforcement server, or service deployment.

## Compatibility decision ADR-001 (2026-10-29)

Use `.agents/skills/` as the canonical tree for repository-local Codex discovery and for portable skill folder export. Other clients may use different discovery folders. Adapt **at packaging or installation time** rather than maintaining divergent copies. Do not assume identical discovery semantics for ChatGPT web, Codex, VS Code, Claude, or MCP-served skills.

Minimum skill contract: directory name equals YAML `name`; meaningful YAML `description`; concise Markdown body; explicit side effects and error paths; safe, relative resource links; optional `agents/openai.yaml` for OpenAI display metadata. The local validator implements a deliberately narrow YAML subset (single-line `name` and `description` fields) and is not a general YAML or semantic security parser. Broader YAML handling should use a pinned audited parser and a compatibility test suite before admission.

## Data flow

Input request -> skill discovery (`name`/`description`) -> activation (`SKILL.md`) -> optional references/scripts -> output and evidence. No step elevates external text into user/host authority. Approval precedes consequential writes or outbound tool calls.

## Non-goals for bootstrap

No multi-agent dispatcher, background job scheduler, installer that executes third-party code, live secrets, SaaS deployment, automatic publish, or cross-repository writes. These require separately approved architecture and testing.
