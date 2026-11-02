# AI Skill Master Template — v1.0

Canonical architect: `skills/ai-skill-architect/SKILL.md`.
Reusable entrypoint: `templates/ai-skill-master/SKILL.md.tmpl`.
OpenAI metadata example: `templates/ai-skill-master/agents/openai.yaml.tmpl`.
Evaluation seeds: `templates/ai-skill-master/evals.json`.

## Release protocol

1. Copy the template into a lowercase-hyphenated skill directory and substitute every marker.
2. Write a narrowly scoped trigger description and a concrete failure policy.
3. Add only required scripts, references, and assets.
4. Run `python3 scripts/validate_skill.py path/to/skill`.
5. Run `python3 -m unittest discover -s tests -v`.
6. Execute relevant skill scripts and behavioral eval fixtures in the target host.
7. Record observed evidence, review diffs, and publish through a PR.

The structural validator intentionally does not claim runtime capability, host compatibility, trigger accuracy, or security certification.

## Research anchors

- https://agentskills.io/specification
- https://github.com/openai/skills/tree/main/skills/.system/skill-creator
- https://developers.openai.com/api/docs/guides/tools-skills
- https://github.com/anthropics/skills

## Next iteration

Add JSON evaluation runner and CI gate; test activation quality on a seeded prompt corpus; measure token cost and execution reproducibility; export a generated skill archive for each release.
