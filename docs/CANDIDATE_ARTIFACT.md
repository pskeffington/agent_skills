# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `0438e2f4c6ac075c8fdc963c6d0649c1166c3d1f`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Reproducibility: three independent builds were byte-identical (SHA256 `75133db22d9a919fd39225fa6c5cdb4aea87a5874607516ca1a3d3271dd334ae`)
- Artifact size: 38,653 bytes
- `doctor`: PASS; Codex execution is disabled by default
- Matching digest check: PASS; standalone RAG search returned eight citations with `unverified_hits: 0`
- GitHub Actions run `41160150104`: success for source commit `0438e2f4c6ac075c8fdc963c6d0649c1166c3d1f`; structural validation, 103 unit tests, and Codex preflight passed (one informational Ubuntu runner image migration notice)
- Synthetic release dossier remains BLOCKED (exit 2) on missing release/staging evidence
- No staging, deployment, or production action was performed.

The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only `agent_toolset` Python sources and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
