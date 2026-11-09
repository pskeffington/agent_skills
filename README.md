# Agent Skills

Reusable, evidence-driven agent workflows for engineering research, software delivery, and reproducible validation.

This repository is the **shared skill library**, not a deployment system or an authorization to modify other repositories. Each skill defines its own scope, inputs, outputs, safety boundaries, and tests.

## Available skills

| Skill | Purpose | Validation |
| --- | --- | --- |
| [Firmware reverse engineering](skills/firmware-reverse-engineering/SKILL.md) | Authorized offline firmware and protocol research with recovery gates | Python unit tests, tool-manifest validation, dedicated CI |
| [Portfolio Valuation Systema](skills/portfolio-valuation-systema/SKILL.md) | Read-only source-repository evidence gathering and private portfolio valuation | Evidence and methodology review; see skill-specific gates |

Skills are invoked when the task matches the description in each `SKILL.md`; they do not confer GitHub permissions or bypass review.

## Repository conventions

- [AGENTS.md](AGENTS.md) is the root instruction entrypoint for coding agents working **in this repository**.
- Each skill lives at `skills/<slug>/SKILL.md` with YAML frontmatter (`name`, `description`) and task-specific instructions.
- Store longer knowledge in `references/`, deterministic automation in `scripts/`, checks in `tests/`, and optional agent metadata in `agents/openai.yaml`.
- See [Agent operating model](docs/agent-operating-model.md) for routing, evidence handling, blocker decisions, CI gates, and cross-repository adoption.

## Development workflow

1. Read this README, root [AGENTS.md](AGENTS.md), and the selected skill's `SKILL.md`.
2. Inventory inputs, authorized repositories, affected files, current branch, and any open blockers. Preserve existing work.
3. Make narrowly scoped changes on a feature branch and update documentation/tests with behavior changes.
4. Run applicable deterministic local tests and validators; capture exact commands and outcomes.
5. Open a pull request with the evidence, test results, unresolved risks, and rollback plan. Do not claim deployment or correctness solely from agent output.

### Current local checks

```sh
python -m unittest discover -s skills/firmware-reverse-engineering/tests -v
python skills/firmware-reverse-engineering/scripts/re_suite.py validate-tools skills/firmware-reverse-engineering/references/tool-suite.json
```

The existing [firmware validation workflow](.github/workflows/firmware-re-validation.yml) runs these checks on relevant changes. Other skills must declare their own validation commands before automated pass/fail claims.

## Adoption by other repositories

A project can explicitly reference a versioned skill and add a project-local `AGENTS.md` specifying which tasks invoke it. **No automatic synchronization or enforcement is supplied by this repository today.** For enforceable gates, add branch protection, required checks, and project-specific workflows in the consuming repository; instructions alone are not enforcement.

## Security and evidence

Never commit secrets, proprietary binaries, regulated data, or private valuation outputs. Respect least-privilege credentials, user authorization, tool restrictions, license obligations, and review gates. Separate observed facts from hypotheses and report incomplete validation as incomplete.
