# Independent security review: release dossier schema version 2.0.0

**Result: PASS**

Reviewed R14 changes based on `b2ad00d210494be3048aa2c10a03d37624df4765`.

The dossier schema and checked-in example now use `2.0.0`, matching the new required signed dossier digest. The evaluator requires exactly `2.0.0`; obsolete and unknown versions remain blocked. The generated example uses the same constant, and the repository validator derives each example's expected version from its registered schema rather than hardcoding `1.0.0`.

The regression test now supplies a matching artifact and passing verifier, recalculates the dossier binding after changing the version to `1.0.0`, and asserts that the unsupported schema version is the sole blocker. No version-related admission bypass was found.

Verification:

- `python3 -m unittest tests.test_codex tests.test_release_approval tests.test_cli -q`: PASS, 24 tests.
- `python3 scripts/validate.py`: PASS.
- `python3 -m unittest discover -s tests -q`: PASS, 89 tests.
- `python3 scripts/codex_preflight.py --repo .`: PASS; worktree was dirty during candidate verification.
- `python3 scripts/release_gate.py --example`: BLOCKED, exit 2 as expected.
- `git diff --check`: PASS.

Reviewed independently by `/root/security_assurance_review` on 2026-10-30. No files were changed by the reviewer.
