# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `ea24956c3910e21f67ba51600157a8516af9edda`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Reproducibility: three independent builds were byte-identical (SHA256 `f524b17a14110ddaca61cabe6be68492dac841f18504b84bcc24b24807ad660f`)
- Artifact size: 37,424 bytes
- `doctor`: PASS; Codex execution is disabled by default
- Matching artifact digest check: PASS; stale all-zero digest correctly failed (exit 1)
- Standalone RAG search: cache miss then hit; both returned the same verified citation and zero unverified hits
- GitHub Actions run `41156636091`: success for source commit `ea24956c3910e21f67ba51600157a8516af9edda`
- No staging, deployment, or production action was performed.

The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only `agent_toolset` Python sources and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
