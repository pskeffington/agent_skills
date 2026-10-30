"""Offline CI run ingestion and classification for GitHub Actions exports."""
from __future__ import annotations
from typing import Any
from ..contracts import ContractError, SHA

_COMPLETED = {"success": "PASS", "failure": "FAIL", "cancelled": "FAIL", "timed_out": "FAIL", "action_required": "BLOCKED", "neutral": "BLOCKED", "skipped": "BLOCKED", "stale": "BLOCKED", "startup_failure": "BLOCKED", "queued": "BLOCKED", "in_progress": "BLOCKED", "waiting": "BLOCKED", "requested": "BLOCKED", "pending": "BLOCKED"}

def classify_github_run(document: dict[str, Any], *, expected_commit: str, required_checks: set[str] | None = None) -> dict[str, Any]:
    issues=[]
    if not isinstance(document, dict):
        return {"status":"FAIL","issues":["workflow run export must be an object"]}
    head=document.get("head_sha")
    if not isinstance(head,str) or not SHA.fullmatch(head):
        issues.append("workflow run has no valid head SHA")
    elif head != expected_commit:
        issues.append("workflow run is for a stale commit")
    conclusion=document.get("conclusion")
    if conclusion not in _COMPLETED:
        issues.append("workflow run has an unknown or missing conclusion")
        run_status="BLOCKED"
    else:
        run_status=_COMPLETED[conclusion]
        if run_status != "PASS": issues.append(f"workflow conclusion is {conclusion}")
    jobs=document.get("jobs", [])
    if not isinstance(jobs,list):
        issues.append("workflow jobs must be an array"); jobs=[]
    seen=set()
    for job in jobs:
        if not isinstance(job,dict) or not isinstance(job.get("name"),str):
            issues.append("workflow contains malformed job"); continue
        name=job["name"]; seen.add(name)
        job_result=_COMPLETED.get(job.get("conclusion"),"BLOCKED")
        if job_result != "PASS": issues.append(f"job {name} is {job.get('conclusion') or 'incomplete'}")
    missing=(required_checks or set())-seen
    if missing: issues.append("required checks missing: " + ", ".join(sorted(missing)))
    status="PASS" if not issues and run_status == "PASS" else ("BLOCKED" if run_status == "BLOCKED" and not any("stale" in x for x in issues) else "FAIL")
    return {"status":status,"issues":issues,"head_sha":head,"run_id":document.get("id"),"conclusion":conclusion,"checks":sorted(seen)}
