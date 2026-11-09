# Audio task contract

Use the repository's canonical task contract and validate it against [`schemas/task-contract.schema.json`](../../../../schemas/task-contract.schema.json). This audio example uses only schema-supported fields; replace the placeholders and confirm the repository, paths, and 40-character base commit before execution.

```json
{
  "schema_version": "1.0.0",
  "task_id": "AE-01-001",
  "repository": "owner/repository",
  "base_commit": "0000000000000000000000000000000000000000",
  "objective": "Reproduce and diagnose silent playback for an identified audio fixture.",
  "scope": {
    "include": ["src/audio/**", "tests/audio/**"],
    "exclude": ["release", "device firmware", "unrelated UI"]
  },
  "acceptance": [
    "Record fixture provenance and a reproducible command.",
    "Capture decoded, enqueued, submitted, and consumed frame counts.",
    "Run the relevant regression tests and report physical-output validation as PASS or NOT RUN."
  ],
  "risk": "medium",
  "owner_role": "audio-engineer",
  "status": "queued",
  "depends_on": [],
  "evidence_refs": [],
  "blocker": null,
  "approval_ref": null
}
```

Keep additional diagnostic measurements in evidence artifacts referenced by `evidence_refs`; do not add unsupported fields to the canonical contract. Use `blocked` and record the concrete next action when required fixtures, devices, or approvals are unavailable.
