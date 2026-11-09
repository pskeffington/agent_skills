---
name: skill-authoring
description: Create or review a focused, portable Agent Skill in this repository. Use when asked to scaffold a new SKILL.md workflow, refine skill triggers, audit a skill, or prepare skill admission checks.
---

# Skill authoring

Produce a single-purpose, auditable skill that follows the local architecture and release gates. Keep planning artifacts distinct from runtime capabilities.

1. Capture two positive trigger requests, two negative requests, the expected inputs and outputs, allowed tools, and any side effects. Ask only if these are truly unknowable from the task and repository context.
2. When working in this repository, read `AGENTS.md` and the architecture, threat model, and release-gate documents. In other repositories, honor the host policy and apply this workflow without assuming these files exist. Search for a duplicate or overlapping skill first.
3. Create a narrowly named directory under `.agents/skills/`; use this repository's `scripts/new_skill.py` when available, otherwise scaffold a minimal `SKILL.md` manually. Never overwrite an existing skill. Put name and trigger-focused description in YAML frontmatter.
4. Write imperative, bounded, sequential instructions. Prefer instructions to executable scripts. Put detailed references in `references/` only when needed; keep links relative and local.
5. Specify failure handling, untrusted-input boundaries, tool limitations, and explicit confirmation before consequential operations. Never assume a skill grants tool permissions or authorizes secrets/network use.
6. Add positive, negative, and adversarial evaluation fixtures when a harness exists. In this repository run `scripts/index_skills.py --write`, `scripts/validate_skills.py`, and unit tests; otherwise use available validators and tests. Review every generated change.
7. Report exactly which gates passed, which are blocked, the changed paths, and target-client tests actually performed. Do not claim portable runtime support without a client smoke test.

Read [review checklist](references/review-checklist.md) for admission review. Consult the repository standards matrix for source analysis; repo-wide docs are governance, not portable skill resources.
