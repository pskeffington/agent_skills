# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `ff0b9cd766b5451929a9bdb56cd4ca8651533618`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Artifact: `dist/agent-toolset.pyz`
- SHA256: `cbab15f6c626ab460b42c6fc40ee0a4e95b6712762e8c03494051530c06ae844`
- Environment: Python 3.15.2, macOS local workspace
- Reproducibility: three independently written artifacts had the same SHA256
- Smoke check: `python3 dist/agent-toolset.pyz doctor` returned exit 0 and `status=PASS`
- Negative release check: `python3 dist/agent-toolset.pyz release-check examples/feature-evidence.json` returned exit 2 and `status=BLOCKED`
- Artifact integrity: `python3 dist/agent-toolset.pyz artifact-check dist/agent-toolset.pyz --sha256 cbab15f6c626ab460b42c6fc40ee0a4e95b6712762e8c03494051530c06ae844` returned exit 0 and `status=PASS`; stale prior digest returned exit 1 and `status=FAIL`

Standalone cache smoke check: two `search --cache` runs reported a miss then a hit for the same source fingerprint. Standalone `release-check examples/release-dossier.json` remains BLOCKED with exit 2, while stale attestation evidence returns FAIL with exit 1. The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only the `agent_toolset` Python sources (including RAG search, cache, release approval, and artifact verification) and uses the standard library; release signature verification additionally requires system OpenSSL. Its Codex adapter remains capability-probe-only; no agent execution or deployment is enabled. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
