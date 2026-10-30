# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `fcf7bcf06f6dcd52089472e2b1f95090ec14d203`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Artifact: `dist/agent-toolset.pyz`
- SHA256: `e98df925d6bb6f6a7d8b362b376b9286378ae921f0bd22959cd92eb3106ac1a4`
- Environment: Python 3.15.2, macOS local workspace
- Reproducibility: three independently written artifacts had the same SHA256
- Smoke check: `python3 dist/agent-toolset.pyz doctor` returned exit 0 and `status=PASS`
- Negative release check: `python3 dist/agent-toolset.pyz release-check examples/feature-evidence.json` returned exit 2 and `status=BLOCKED`
- Artifact integrity: matching digest returned exit 0 and `status=PASS`; stale all-zero digest returned exit 1 and `status=FAIL`

Codex capability note: `doctor` reports `codex_execution=disabled`; direct adapter execution requires an external containment attestation that this library does not itself verify.

Standalone cache smoke check: two `search --cache` runs reported a miss then a hit for the same source fingerprint. Standalone `release-check examples/release-dossier.json` remains BLOCKED with exit 2, while stale attestation evidence returns FAIL with exit 1. The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only the `agent_toolset` Python sources (including RAG search, cache, release approval, artifact verification, and the opt-in Codex adapter) and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. No real agent invocation, staging, or deployment was performed. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
