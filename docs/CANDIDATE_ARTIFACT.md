# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `1c3c7a4af9f2ae13089349086eaab2dc97ec73a2`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Artifact: `dist/agent-toolset.pyz`
- SHA256: `4027ba406ef3e1d13aa30c20cbb6cbfb02cc1f875607030babf20a4af8a1a4de`
- Environment: Python 3.15.2, macOS local workspace
- Reproducibility: two independently written artifacts had the same SHA256
- Smoke check: `python3 dist/agent-toolset.pyz doctor` returned exit 0 and `status=PASS`
- Negative release check: `python3 dist/agent-toolset.pyz release-check examples/feature-evidence.json` returned exit 2 and `status=BLOCKED`

Standalone cache smoke check: two `search --cache` runs reported a miss then a hit for the same source fingerprint. The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only the `agent_toolset` Python sources (including RAG search, cache, and release evaluation) and uses the standard library. Its Codex adapter remains capability-probe-only; no agent execution or deployment is enabled. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
