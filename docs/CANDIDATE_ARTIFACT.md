# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `9abbdd45e92a4d75f9ab2fe5853cd7a53b5fab4f`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Reproducibility: three independent builds were byte-identical (SHA256 `96067b1e6f845b66d8e954ebb2dcdf138a0669297b854134fa28d0e42be3fd0c`)
- Artifact size: 37,930 bytes
- `doctor`: PASS; Codex execution is disabled by default
- Matching digest check: PASS; a synthetic dossier using this exact digest passed artifact integrity but remained BLOCKED (exit 2) on missing release evidence
- GitHub Actions run `41157417446`: success for source commit `9abbdd45e92a4d75f9ab2fe5853cd7a53b5fab4f`
- No staging, deployment, or production action was performed.

The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only `agent_toolset` Python sources and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
