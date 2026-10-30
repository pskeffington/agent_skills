# agent_skills

Reusable, reviewable Agent Skills with deterministic indexes and admission gates. This repository holds **skills**, not a running autonomous agent or an MCP server.

## Quick start

Requirements: Python 3.10+ and Git. No PyPI packages, remote installer scripts, or third-party Actions are required for local validation.

```sh
python3 scripts/validate_skills.py
python3 scripts/index_skills.py --check
python3 -m unittest discover -s tests -v
```

Create a new skill:

```sh
python3 scripts/new_skill.py example-task --description "Do one repeatable task. Use when a request explicitly asks for that task."
python3 scripts/index_skills.py --write
python3 scripts/validate_skills.py
```

Place portable skills in `.agents/skills/<name>/SKILL.md`. Each skill has a focused trigger description and optional `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`. The catalog at `catalog/skills.json` is **generated**, not hand-maintained. Do not duplicate skills in provider-specific folders; use packaging/adapters when needed.

## Source of truth

- [Architecture](docs/ARCHITECTURE.md): canonical paths, packaging, and portability decisions.
- [Literature matrix](docs/LITERATURE_MATRIX.md) and [machine-readable evidence](data/literature_matrix.json): standards versus engineering interpretations.
- [Roadmap](docs/ROADMAP.md) and [release gates](docs/RELEASE_GATES.md): build sequence and required verification.
- [Threat model](docs/THREAT_MODEL.md) and [security policy](SECURITY.md): injection and tool-execution boundaries.
- [Agent instructions](AGENTS.md): Codex and coding-agent operating contract.

## Status

Bootstrap stage: one reference skill (`skill-authoring`), standard-library tooling, local tests, and a GitHub Actions validation workflow. **No skill is automatically installed in other repositories; no external services are deployed.** Admission to production/distribution requires documented evaluation, security review, and explicit approval.

MIT licensed; verify additional licensing before importing third-party materials.
