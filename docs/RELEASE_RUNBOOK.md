# Release runbook

This repository toolset only prepares and evaluates evidence. It has no deployment command.

1. Freeze a candidate commit and calculate the artifact digest from the exact build output.
2. Run offline validators and tests; preserve command, exit status, environment, commit and output references.
3. Obtain independent reviewer and security review evidence for that exact commit. The author cannot attest to their own independent review.
4. Prepare a staging dossier with environment, health checks, logs, rollback procedure, and rollback drill evidence.
5. Run `python3 -m agent_toolset release-check evidence.json`; resolve every missing or stale gate. Synthetic examples are never staging evidence.
6. An authorized operator separately approves any staging or production action, naming target and candidate digest. This tool does not record implicit consent or perform the action.
7. After an authorized deployment, record actual result, monitoring window and rollback decision in the external deployment system and link immutable evidence back to the dossier.

A failed or unavailable gate remains FAIL or BLOCKED. Do not replace real evidence with fixture success. Rollback must identify the prior immutable artifact and exact operator procedure before a release can be considered ready.
