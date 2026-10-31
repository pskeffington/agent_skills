# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `2ede0defc41449e0bb62d44723b798bb3399a8d4`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Reproducibility: three independent builds were byte-identical (SHA256 `d374c39967cdaa830926ccc440ae996d68db948dcea3a2fdfc77c2899a21b6a4`)
- Artifact size: 38,578 bytes
- `doctor`: PASS; Codex execution is disabled by default
- Matching digest check: PASS; standalone RAG search returned eight citations with `unverified_hits: 0`
- GitHub Actions run `41159283025`: success for source commit `2ede0defc41449e0bb62d44723b798bb3399a8d4` (one informational Ubuntu runner-image migration notice)
- Synthetic release dossier remains BLOCKED (exit 2) on missing release/staging evidence
- No staging, deployment, or production action was performed.

The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only `agent_toolset` Python sources and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. The current artifact was rebuilt from source commit `2ede0de`. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
