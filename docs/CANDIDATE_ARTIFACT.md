# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `d3afa371af75a98e812e716e6794e7c984b5d2c1`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Artifact: `dist/agent-toolset.pyz`
- SHA256: `516bccd688af46c880bb60c6201fc810b1e47adbf9ab462040f880b431ab918f`
- Environment: Python 3.15.2, macOS local workspace
- Reproducibility: two independently written artifacts had the same SHA256
- Smoke check: `python3 dist/agent-toolset.pyz doctor` returned exit 0 and `status=PASS`
- Negative release check: `python3 dist/agent-toolset.pyz release-check examples/feature-evidence.json` returned exit 2 and `status=BLOCKED`

Standalone cache smoke check: two `search --cache` runs reported a miss then a hit for the same source fingerprint. Standalone `release-check examples/release-dossier.json` remains BLOCKED with exit 2, while stale attestation evidence returns FAIL with exit 1. The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only the `agent_toolset` Python sources (including RAG search, cache, and release evaluation) and uses the standard library. Its Codex adapter remains capability-probe-only; no agent execution or deployment is enabled. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
