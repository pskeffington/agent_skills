# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `a7d5bb9214130532001f04106f0b31879f753673`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Reproducibility: three independent builds were byte-identical (SHA256 `1becc8dc4e660bf43ffd1288ff8dc963edc0ccbd841d6ae4938ae6621cbc8e91`)
- Artifact size: 37,852 bytes
- `doctor`: PASS; Codex execution is disabled by default
- Matching artifact digest check: PASS; stale all-zero digest correctly failed (exit 1)
- GitHub Actions structural check run `41157145868`: success for source commit `a7d5bb9214130532001f04106f0b31879f753673`
- Release example remains BLOCKED; no staging, deployment, or production action was performed.

The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only `agent_toolset` Python sources and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
