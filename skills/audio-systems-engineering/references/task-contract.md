# Codex task envelope

```yaml
task_id: AE-01-001
primary_agent: AE-01
reviewer: AE-06
repo: owner/repo
base_commit: commit-sha
symptom: observable failure
reproduction:
  command: exact reproducible command
  fixture: path and sha256 plus license/provenance
  expected: measurable outcome
instrumentation: [frames_decoded, frames_enqueued, frames_consumed]
allowed_paths: [explicit file ownership]
constraints: [no realtime callback allocations, preserve public API]
acceptance_gates: [G0, G1, G2]
required_evidence: [logs, tests, before_after, rollback]
status: queued
```

Valid status: queued, assigned, reproduced, patched, validated, blocked, merged. Blocked requires concrete dependency. Do not merge unvalidated code.
