# Acceptance gates (G0–G6)

All gate outcomes must be **PASS**, **FAIL**, **BLOCKED**, or **NOT_APPLICABLE** with a reason. Only PASS or justified, approved NOT_APPLICABLE admits a candidate. No invented success or bypass based on missing tooling.

| Gate | Owner | Minimum evidence |
| --- | --- | --- |
| G0 intake | Orchestrator | repository, baseline SHA, objective, allowed scope, risk |
| G1 plan/design | Planner + architect | task DAG, interfaces, acceptance tests, rollback and changes |
| G2 implementation | Implementer | bounded diff, code ownership, no unexpected dependencies |
| G3 integration | Integrator | reproducible build, lockfile and compatibility outcomes |
| G4 independent quality | Verifier + code reviewer | unit/integration/regression commands, defects and review decision |
| G5 security/documentation | Security + documenter | threat/dependency/license checks and updated operator docs |
| G6 release readiness | Release controller + human | full evidence packet, artifact digests, rollback, explicit approval signed by an allowlisted approver key |

## Fail closed
- `BLOCKED`: required tool/fixture/permission unavailable; log precise blocker and next action.
- `FAIL`: check ran and found an unacceptable defect; return to owning stage.
- `NOT_APPLICABLE`: require a documented rationale; cannot disguise unrun mandatory checks.
- On new commit, re-evaluate affected downstream evidence.
- Approval signatures are checked against an operator-managed public-key trust store and bind the approver, authority reference, invocation, decision, exact source commit, and artifact digest. A signature does not authenticate external CI, review, security, or staging references.
- Deployment, migration, external publication and irreversible changes require a separate, explicit human authorization. A green documentation check does not constitute authorization.

## Example checkpoint
```text
Task: DEV-001 | Base: <sha> | Head: <sha>
G0 PASS | G1 PASS | G2 PASS | G3 PASS
G4 BLOCKED (platform fixture unavailable)
G5 PASS | G6 BLOCKED (depends on G4)
Next: provision fixture, rerun G4, then reassess G6
```
