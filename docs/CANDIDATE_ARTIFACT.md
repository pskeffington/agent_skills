# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `2e03e056fdb4c35fcb95aad52fc376eaf836ceec`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Reproducibility: three independent builds were byte-identical (SHA256 `c69fbb2b4d8e03f89356ee4c6f5214db9a79a49b08db11ee4b9debe23a8d5218`)
- Artifact size: 37,960 bytes
- `doctor`: PASS; Codex execution is disabled by default
- Matching digest check: PASS; matching-digest v2 synthetic dossier passed artifact integrity but remained BLOCKED (exit 2) on absent release evidence
- GitHub Actions run `41157657279`: success for source commit `2e03e056fdb4c35fcb95aad52fc376eaf836ceec`
- No staging, deployment, or production action was performed.

The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only `agent_toolset` Python sources and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
