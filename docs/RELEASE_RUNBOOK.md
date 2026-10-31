# Release runbook

This repository toolset only prepares and evaluates evidence. It has no deployment command.

1. Freeze a candidate commit and calculate the artifact digest from the exact build output.
2. Run offline validators and tests; preserve command, exit status, environment, commit and output references.
3. Run `python3 -m agent_toolset artifact-check dist/agent-toolset.pyz --sha256 <dossier artifact_sha256>` and preserve its JSON output. Keep the verified artifact immutable between this check, approval signing, transfer, and staging; this local check does not pin a later deployment read.
4. Obtain independent reviewer and security review evidence for that exact commit. The author cannot attest to their own independent review.
5. Prepare a staging dossier with environment, health checks, logs, rollback procedure, and rollback drill evidence.
6. Run `python3 -m agent_toolset release-check evidence.json --artifact dist/agent-toolset.pyz --approval-trust-store /secure/operator/approval-trust.json`; this rehashes the exact bytes during dossier evaluation and binds the check to its recorded digest. Resolve every missing or stale gate. Synthetic examples are never staging evidence. If OpenSSL or the configured trust store is unavailable, the evaluator remains BLOCKED.
7. An authorized operator separately approves any staging or production action, naming target and candidate digest. This tool does not record implicit consent or perform the action.
8. After an authorized deployment, record actual result, monitoring window and rollback decision in the external deployment system and link immutable evidence back to the dossier.

A contradicted gate or stale commit/artifact attestation is FAIL; missing or incomplete evidence is BLOCKED. Do not replace real evidence with fixture success. Rollback must identify the prior immutable artifact and exact operator procedure before a release can be considered ready.

## Evidence packet shape

For each gate include a status, reason, and evidence pointer. Implementation, review, security, staging, and approval attestations must bind their invocation identity, commit SHA and artifact SHA256. Approval must contain an explicit `APPROVE` decision, approver identity, authority reference, and a detached signature over its canonical fields. The configured trust store binds the approver identity and authority reference to an authorized public key; the verifier rejects stale subject bindings and reviewer/security invocations that match the implementer or approver. Use `ci-ingest` only for a saved, authoritative workflow export; its output must match the candidate SHA and required job names. Use `security-summary` on the security scanner's actual export. Preserve source records and verify their provenance in GitHub or the security system. The verifier authenticates the local approval signature only; it does not authenticate external evidence references or the trust-store governance process.

To prepare an approval signature, first record the exact candidate, target, decision, authorized approver identity, authority reference, and invocation in the dossier. Emit the signed bytes with `python3 -m agent_toolset approval-payload evidence.json > approval-payload.json`; have the authorized approver sign those bytes offline with the private key corresponding to the trust-store key. Encode the detached signature as base64 in `approval.signature`. Do not place private keys in the repository. Run release-check with the trusted public-key store and confirm PASS only after all remaining evidence gates also pass.
