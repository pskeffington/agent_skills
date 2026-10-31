# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `dae099ce739f9b6733cc89c8f53bc971f19c0e74`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Reproducibility: three independent builds were byte-identical (SHA256 `12f6f61e9c698200930a8d6d745b0a0092ece607784395c1b1b7436f2520f6ab`)
- Artifact size: 38,661 bytes
- `doctor`: PASS; Codex execution is disabled by default
- Matching digest check: PASS; standalone RAG search returned eight citations with `unverified_hits: 0`
- Bound release evaluation: artifact integrity PASS against `examples/candidate-artifact-release-dossier.json`; overall readiness BLOCKED (exit 2) on missing G0-G6, attestations, rollback, and provenance. Structured evidence: `examples/candidate-artifact-release-evaluation-evidence.json`.
- GitHub Actions run `41160395720`: success for source commit `dae099ce739f9b6733cc89c8f53bc971f19c0e74`; structural validation, 103 unit tests, and Codex preflight passed (one informational Ubuntu runner image migration notice)
- Synthetic release dossier remains BLOCKED (exit 2) on missing release/staging evidence
- No staging, deployment, or production action was performed.

The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only `agent_toolset` Python sources and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
