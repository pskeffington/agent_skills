# Independent security review: release dossier signature binding

**Result: PASS**

Reviewed changes based on `d27ab2906c4b71d4c58204ffeefbdf1802706971` across the approval signer, release evaluator, CLI, release dossier schema, tests, and operator/security documentation.

The approval payload now signs `dossier_sha256`. The digest covers canonical dossier content while excluding only `approval.signature` and `approval.dossier_sha256`, avoiding a circular digest while binding gate statuses/evidence, target environment, rollback reference, attestations, provenance, and all other approval fields. The evaluator recomputes and compares this digest before release admission. Missing, invalid, or mismatched binding cannot produce PASS; mismatches are FAIL. Duplicate keys are rejected by both approval-payload and release-check CLI JSON parsing. The schema and runbook document the field and re-signing requirement. No actionable bypass or correctness issue was found.

The tests cover mutations to target environment, gate evidence, and rollback reference, plus duplicate JSON keys. No review edits were made.

Reviewed independently by `/root/security_assurance_review` on 2026-10-30.
