---
name: ai-skill-architect
description: Create, revise, audit, and package portable Agent Skills with explicit activation boundaries, concise instructions, modular references, deterministic scripts, and measurable evaluations. Use when designing a new SKILL.md, building a skill template, migrating a skill across ChatGPT/Codex and other Agent Skills hosts, or diagnosing skill trigger, validation, and quality failures.
---

# AI Skill Architect

Build reusable, inspectable skills with the smallest complete instruction set.

## Workflow

1. Define three concrete representative requests: a normal request, an edge case, and a non-trigger. Record expected inputs, outputs, tools, safety constraints, and failure behavior.
2. Select a narrow capability and a lowercase hyphenated name. Do not encode a generic persona in place of actionable procedures.
3. Scaffold from [the master template](../../templates/ai-skill-master/SKILL.md.tmpl). Replace all template markers before release.
4. Write YAML frontmatter with only `name` and `description`. Front-load positive trigger situations and explicitly describe exclusions to reduce false activation.
5. Put a short operational algorithm in SKILL.md. Store optional technical material under `references/`, deterministic code under `scripts/`, and output ingredients under `assets/`. Do not duplicate reference content in the entrypoint.
6. Specify entry conditions, preconditions, tool choices, failure/rollback behavior, expected output contract, and hard stop conditions. Never assume access to external credentials, networks, or tools.
7. Create reproducible evaluations using [the evaluation matrix](references/evaluation-matrix.md). Include positive, negative, ambiguous, adversarial, and regression cases.
8. Run the repository validator: `python3 scripts/validate_skill.py <skill-directory>`. Then execute each included script and smoke-test representative inputs.
9. Review evidence, revise and repeat. Do not claim pass without observed test output. Package or publish only after checks complete.

## Quality gates

- Correctly matches relevant requests and rejects unrelated requests.
- Delivers specified outputs without inventing tool results, external facts, or completion.
- Has no unresolved template markers or broken relative resource links.
- Avoids unneeded dependencies, instruction bloat, and nested reference chains.
- Does not place credentials, secrets, private user data, or destructive default commands in bundled files.
- Preserves user-provided data and original files unless changes are expressly requested.
- Keeps host-specific capabilities optional; document deviations in `references/`.

## Portability

Follow the Agent Skills core format. The optional `agents/openai.yaml` config is OpenAI host metadata, not a portable instruction requirement. Runtime permissions and host availability are checked at execution time. Never assume that every host implements the same tool surface.

## Reporting

Report files changed, validation commands and observed outcomes, remaining limits, and the exact branch/commit or artifact path if created. Distinguish structural validation from behavioral evaluation.
