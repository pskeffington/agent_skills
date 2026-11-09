"""Fail-closed normalization for machine-readable security findings."""
from __future__ import annotations
from typing import Any

_SEVERITY={"critical":4,"high":3,"moderate":2,"medium":2,"low":1,"info":0,"informational":0}

def summarize_findings(document: Any, *, fail_on: str = "high") -> dict[str, Any]:
    threshold=_SEVERITY.get(fail_on.lower())
    if threshold is None:
        return {"status":"FAIL","issues":["unknown fail_on severity"]}
    if not isinstance(document,dict) or not isinstance(document.get("findings"),list):
        return {"status":"BLOCKED","issues":["security findings export must contain a findings array"],"counts":{}}
    counts={key:0 for key in ("critical","high","moderate","low","info","unknown")}
    issues=[]
    for index,finding in enumerate(document["findings"]):
        if not isinstance(finding,dict) or not isinstance(finding.get("severity"),str):
            issues.append(f"finding {index} is malformed"); counts["unknown"]+=1; continue
        severity=finding["severity"].lower()
        normalized="moderate" if severity=="medium" else ("info" if severity=="informational" else severity)
        if normalized not in counts: normalized="unknown"
        counts[normalized]+=1
        score=_SEVERITY.get(severity,99 if normalized=="unknown" else 0)
        if score>=threshold:
            issues.append(f"finding {index} meets fail threshold ({severity})")
    status="FAIL" if issues else "PASS"
    return {"status":status,"issues":issues,"counts":counts}
