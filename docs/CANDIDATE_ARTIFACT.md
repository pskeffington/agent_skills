# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `9a42f18486b1fbbf4d9fcadc69ee04037b0bdbd6`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Reproducibility: three independent builds were byte-identical (SHA256 `000d2900ae119ffdb34815fdcb0f06e99e063ac3f964edb0187e9e02003ebed5`)
- Artifact size: 38,652 bytes
- `doctor`: PASS; Codex execution is disabled by default
- Matching digest check: PASS; standalone RAG search returned eight citations with `unverified_hits: 0`
- GitHub Actions run `41160011453`: success for source commit `9a42f18486b1fbbf4d9fcadc69ee04037b0bdbd6`; structural validation, 102 unit tests, and Codex preflight passed; no annotations were returned
- Synthetic release dossier remains BLOCKED (exit 2) on missing release/staging evidence
- No staging, deployment, or production action was performed.

The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only `agent_toolset` Python sources and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
