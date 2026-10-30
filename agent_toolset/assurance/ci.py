"""Offline CI run ingestion and classification for GitHub Actions exports."""
from __future__ import annotations
from typing import Any
from ..contracts import ContractError, SHA

_COMPLETED = {"success": "PASS", "failure": "FAIL", "cancelled": "FAIL", "timed_out": "FAIL", "action_required": "BLOCKED", "neutral": "BLOCKED", "skipped": "BLOCKED", "stale": "BLOCKED", "startup_failure": "BLOCKED", "queued": "BLOCKED", "in_progress": "BLOCKED", "waiting": "BLOCKED", "requested": "BLOCKED", "pending": "BLOCKED"}

def classify_github_run(document: dict[str, Any], *, expected_commit: str, required_checks: set[str] | None = None) -> dict[str, Any]:
    issues=[]
    if not isinstance(document, dict):
        return {"status":"BLOCKED","issues":["workflow run export must be an object"]}
    if not isinstance(expected_commit, str) or not SHA.fullmatch(expected_commit):
        return {"status":"BLOCKED","issues":["expected commit must be a valid lowercase SHA"]}
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
    jobs=document.get("jobs")
    if not isinstance(jobs,list) or not jobs:
        issues.append("workflow run has no complete job evidence")
        jobs=[]
    seen=set()
    failed=False
    for job in jobs:
        if not isinstance(job,dict) or not isinstance(job.get("name"),str) or not job["name"].strip() or not isinstance(job.get("conclusion"),str):
            issues.append("workflow contains malformed or incomplete job evidence")
            continue
        name=job["name"]
        if name in seen:
            issues.append(f"workflow contains duplicate job evidence: {name}")
            continue
        seen.add(name)
        job_result=_COMPLETED.get(job["conclusion"],"BLOCKED")
        if job_result == "FAIL":
            issues.append(f"job {name} is {job['conclusion']}")
            failed=True
        elif job_result == "BLOCKED":
            issues.append(f"job {name} is {job['conclusion']}")
    if not isinstance(required_checks,set) or not required_checks or not all(isinstance(name,str) and name.strip() for name in required_checks):
        issues.append("required check names must be configured")
        required_checks=set()
    missing=required_checks-seen
    if missing: issues.append("required checks missing: " + ", ".join(sorted(missing)))
    stale=any("stale" in issue for issue in issues)
    failed = failed or run_status == "FAIL"
    status="PASS" if not issues and run_status == "PASS" else ("FAIL" if stale or failed else "BLOCKED")
    return {"status":status,"issues":issues,"head_sha":head,"run_id":document.get("id"),"conclusion":conclusion,"checks":sorted(seen)}
