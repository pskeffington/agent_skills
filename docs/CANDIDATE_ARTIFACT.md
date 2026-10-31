# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `4fdd21aceb51e0bd39387fef27ef81bbb710a2b1`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Artifact: `dist/agent-toolset.pyz`
- SHA256: `95098ab205bac9afebeba863467feea1319b84c01f69c6b9ee834b3dfe06f881`
- Environment: Python 3.15.2, macOS local workspace
- Reproducibility: three independently written artifacts had the same SHA256 (`95098ab205bac9afebeba863467feea1319b84c01f69c6b9ee834b3dfe06f881`)
- Smoke check: `python3 dist/agent-toolset.pyz doctor` returned exit 0 and `status=PASS`
- Negative release check: a synthetic dossier with the matching candidate digest passed artifact integrity but remained `BLOCKED` (exit 2) on missing gates; the compatibility example `python3 scripts/release_gate.py --example` also remained `BLOCKED` (exit 2)
- Artifact integrity: matching digest returned exit 0 and `status=PASS`; stale all-zero digest returned exit 1 and `status=FAIL`

Codex capability note: `doctor` reports `codex_execution=disabled`; direct adapter execution requires an external containment attestation that this library does not itself verify.

Artifact-binding check: `python3 dist/agent-toolset.pyz artifact-check dist/agent-toolset.pyz --sha256 95098ab205bac9afebeba863467feea1319b84c01f69c6b9ee834b3dfe06f881` returned PASS; a stale all-zero digest returned FAIL (exit 1). A matching synthetic `release-check` returned BLOCKED (exit 2) because required release evidence is absent. The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only the `agent_toolset` Python sources (including RAG search, cache, release approval, artifact verification, and the opt-in Codex adapter) and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. No real agent invocation, staging, or deployment was performed. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
