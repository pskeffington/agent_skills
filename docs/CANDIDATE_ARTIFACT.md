# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `9d3d48774760655da30c02c73ad624a8228745f4`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Reproducibility: three independent builds were byte-identical (SHA256 `d3eabeceafd7104155f49b55f7009fad2763f19ddf2f0db2812bf6886f28d3da`)
- Artifact size: 37,138 bytes
- `doctor`: PASS; Codex execution is disabled by default
- Matching artifact digest check: PASS; stale digest rejection not repeated during this refresh
- Synthetic release dossier: not rerun during this refresh; prior matching-digest candidate remained BLOCKED for absent release evidence
- CI: GitHub Actions run `41156229024` succeeded for the source commit
- No staging, deployment, or production action was performed.

The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only `agent_toolset` Python sources and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
