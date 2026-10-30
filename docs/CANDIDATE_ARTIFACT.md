# Local candidate artifact record

This is local build evidence for a reproducible executable candidate. It is not a staging or production release attestation.

- Source commit: `bba113d28e43a0223612b7e055c7cb77f906e050`
- Build command: `python3 scripts/build_zipapp.py dist/agent-toolset.pyz`
- Artifact: `dist/agent-toolset.pyz`
- SHA256: `c6422afbcd61f98caa1dd08fad9210a874f5ea789390b4a3f746d34799485942`
- Environment: Python 3.15.2, macOS local workspace
- Reproducibility: two independently written artifacts had the same SHA256
- Smoke check: `python3 dist/agent-toolset.pyz doctor` returned exit 0 and `status=PASS`
- Negative release check: `python3 dist/agent-toolset.pyz release-check examples/feature-evidence.json` returned exit 2 and `status=BLOCKED`

The artifact is kept in ignored `dist/` output and is not committed. The zipapp includes only the `agent_toolset` Python sources and uses the standard library. Its Codex adapter remains capability-probe-only; no agent execution or deployment is enabled. Rebuild after any change to `agent_toolset/` and record the new source commit and digest before using it as a candidate.
