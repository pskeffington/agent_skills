"""Evidence freshness and reviewer independence checks."""
from __future__ import annotations
from typing import Any
from ..contracts import ContractError, validate_evidence

def assess_evidence(document: dict[str, Any], *, subject_commit: str) -> dict[str, Any]:
    try:
        validate_evidence(document)
    except ContractError as exc:
        return {"status": "FAIL", "issues": [str(exc)]}
    issues = []
    if document["source_commit"] != subject_commit:
        issues.append("evidence source commit is stale")
    if document["result"] != "PASS":
        issues.append(f"evidence result is {document['result']}")
    failed = [c["name"] for c in document["checks"] if c["result"] != "PASS"]
    if failed:
        issues.append("non-passing checks: " + ", ".join(failed))
    return {"status": "PASS" if not issues else "FAIL", "issues": issues}

def reviewer_independence(*, author_invocation: str, reviewer_invocation: str, author_role: str, reviewer_role: str) -> dict[str, Any]:
    issues=[]
    if not author_invocation or not reviewer_invocation or author_invocation == reviewer_invocation:
        issues.append("reviewer invocation must differ from author invocation")
    if reviewer_role not in {"reviewer", "verifier", "security"}:
        issues.append("reviewer role is not an assurance role")
    return {"status": "PASS" if not issues else "FAIL", "issues": issues}
