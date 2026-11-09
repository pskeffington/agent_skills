# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `33039d975675172693f164e5a25927ac17350dc5`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Reproducibility: three independent builds were byte-identical (SHA256 `72acf0d8384f59245a1c3bc85388edb3d6a1aa39d125ae759105ce966b6c3775`)
- Artifact size: 38,979 bytes
- `doctor`: PASS; Codex execution is disabled by default
- Matching digest check: PASS. Source and zipapp RAG search returned identical eight citations with `unverified_hits: 0`.
- Bound release evaluation: source and zipapp results are identical; artifact integrity PASS and overall readiness BLOCKED (exit 2) on 14 missing requirements, including signed release evidence, staging, rollback, and check provenance. Structured evidence: `examples/candidate-artifact-release-evaluation-evidence.json`.
- Previous candidate `12f6f61e…f6ab` was verified against source commit `dae099ce739f9b6733cc89c8f53bc971f19c0e74`; its historical check is recorded in GitHub Actions run `41160395720`.
- No staging, deployment, or production action was performed.

The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only `agent_toolset` Python sources and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
