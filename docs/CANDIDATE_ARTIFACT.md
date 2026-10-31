# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `b1dd1561979ce5d4793be39118ec6196aa69a089`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Reproducibility: three independent builds were byte-identical (SHA256 `10fa476f819d02cf5a383a08e72967ad73e65b5d947c52b9e5b0a44ab24e9e3b`)
- Artifact size: 38,484 bytes
- `doctor`: PASS; Codex execution is disabled by default
- Matching digest check: PASS; standalone RAG search returned eight citations with `unverified_hits: 0`
- GitHub Actions run `41158864929`: success for source commit `b1dd1561979ce5d4793be39118ec6196aa69a089`
- Synthetic release dossier remains BLOCKED (exit 2) on missing release/staging evidence
- No staging, deployment, or production action was performed.

The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only `agent_toolset` Python sources and uses the standard library; release signature verification additionally requires system OpenSSL. Codex execution remains disabled by default and blocked without externally verified process containment. The current artifact was rebuilt from source commit `b1dd156`; the subsequent `059688e` commit only updates evidence documentation. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
