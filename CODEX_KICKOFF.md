# Codex kickoff — engineering continuation

Goal: optimize and pilot the repository agent hierarchy for real Codex task execution without weakening release safeguards.

Read: `AGENTS.md`, `docs/CODEX_IMPLEMENTATION.md`, `docs/CODEX_RESOURCE_POLICY.md`, `docs/RELEASE_GATES.md`, `ROADMAP.md`.

Steps:
1. Inspect checkout baseline, `git status`, Git version and `codex --version` if installed.
2. Run `python3 scripts/validate.py`, `python3 -m unittest discover -s tests -v`, and `python3 scripts/codex_preflight.py --repo .`. Report actual results; fix in-scope deterministic test failures first.
3. Verify .github workflow admission with a real PR check. A workflow absent or startup failure is BLOCKED, never fabricated PASS.
4. Choose one isolated, non-production pilot; write task contract; implement small diff; verify and request separate review.
5. Evaluate release dossier with `python3 scripts/release_gate.py --evidence <path> --artifact <candidate-path>`; do not deploy unless separate production authorization exists.
6. Keep branch and PR updated with commits, test evidence, blocker list and next safe tasks. Do not auto-merge.

Failure strategy: maximum 3 distinct targeted repair attempts for each blocker; stop and report when externally blocked. Never add external repo/actions or tokens without approval.
