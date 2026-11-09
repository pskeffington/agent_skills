# Contributing

Use one branch and one narrow PR per skill or validation change. Start from an observed repeatable workflow, with examples of intended and unintended triggers. Document the inputs, outputs, failure behavior, allowed tools, security boundary, and acceptance checks. Prefer instructions to new runtime dependencies.

Create via `python3 scripts/new_skill.py ...`, then refine `SKILL.md` and add any genuinely necessary references/scripts/tests. Run `python3 scripts/index_skills.py --write`, `python3 scripts/validate_skills.py`, and `python3 -m unittest discover -s tests -v` before opening a draft PR. Never hand-edit the generated catalog. If you add a source or revise a standard, update both `data/literature_matrix.json` and its readable summary in `docs/LITERATURE_MATRIX.md`.

A contributor must verify third-party licenses, redact personal data and tokens, inspect executable code, and record any platform-specific behavior as tested rather than assumed. G4/G5 admission requires evidence beyond metadata linting; see `docs/RELEASE_GATES.md`.
