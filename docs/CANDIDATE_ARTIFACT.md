# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `6ec0e4e1a978d7b105e31fe49821d0f914b8043a`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Artifact: `dist/agent-toolset.pyz`
- SHA256: `6efc812441e63afccb856b60b653425af2c58b4d42441f3f6084c0cca599bf2c`
- Environment: Python 3.15.2, macOS local workspace
- Reproducibility: two independently written artifacts had the same SHA256
- Smoke check: `python3 dist/agent-toolset.pyz doctor` returned exit 0 and `status=PASS`
- Negative release check: `python3 dist/agent-toolset.pyz release-check examples/feature-evidence.json` returned exit 2 and `status=BLOCKED`

Standalone cache smoke check: two `search --cache` runs reported a miss then a hit for the same source fingerprint. Standalone `release-check examples/release-dossier.json` remains BLOCKED with exit 2, while stale attestation evidence returns FAIL with exit 1. The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only the `agent_toolset` Python sources (including RAG search, cache, and release evaluation) and uses the standard library. Its Codex adapter remains capability-probe-only; no agent execution or deployment is enabled. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
