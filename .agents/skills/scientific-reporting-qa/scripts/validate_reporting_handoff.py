#!/usr/bin/env python3
"""Validate a study-neutral reporting handoff envelope; never certify its claims."""
import argparse
import json
import re
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
GATES = tuple(f"E{i}" for i in range(1, 9))
STATUSES = frozenset(("PASS", "FAIL", "BLOCKED"))


def evaluate(data):
    issues = []
    if not isinstance(data, dict):
        return {"status": "BLOCKED", "issues": ["dossier must be an object"]}
    if data.get("schema_version") != "1.0.0":
        issues.append("unsupported schema_version")
    for key in ("task_id", "source_repository", "reviewer_role"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            issues.append(f"missing {key}")
    if data.get("reviewer_role") != "scientific-reporting-reviewer":
        issues.append("reviewer_role is not scientific-reporting-reviewer")
    if data.get("reviewer_independent") is not True:
        issues.append("independent review not attested")
    commit = data.get("source_commit")
    if not isinstance(commit, str) or not HEX40.fullmatch(commit):
        issues.append("invalid source_commit")
    artifact = data.get("artifact_sha256")
    if artifact is not None and (not isinstance(artifact, str) or not HEX64.fullmatch(artifact)):
        issues.append("invalid artifact_sha256")
    if data.get("release_recommendation") not in ("PASS", "BLOCKED"):
        issues.append("invalid release_recommendation")
    open_issues = data.get("open_issues")
    if not isinstance(open_issues, list) or any(not isinstance(x, str) for x in open_issues):
        issues.append("open_issues must be string array")
        open_issues = []
    gates = data.get("gates")
    if not isinstance(gates, dict):
        gates = {}
        issues.append("gates must be an object")
    if set(gates) != set(GATES):
        issues.append("expected exactly E1-E8 gates")
    all_pass = True
    for key in GATES:
        row = gates.get(key)
        if not isinstance(row, dict):
            issues.append(f"{key}: gate missing or malformed")
            all_pass = False
            continue
        status = row.get("status")
        if status not in STATUSES:
            issues.append(f"{key}: invalid status")
            all_pass = False
        if status != "PASS":
            all_pass = False
            if not isinstance(row.get("reason"), str) or not row["reason"].strip():
                issues.append(f"{key}: non-PASS gate requires a reason")
        else:
            if not isinstance(row.get("evidence_ref"), str) or not row["evidence_ref"].strip():
                issues.append(f"{key}: PASS requires evidence_ref")
            if not isinstance(row.get("method"), str) or not row["method"].strip():
                issues.append(f"{key}: PASS requires method")
        if row.get("source_commit") != commit:
            issues.append(f"{key}: source revision mismatch")
        if status == "PASS" and key in ("E6", "E7", "E8"):
            if not isinstance(artifact, str) or not HEX64.fullmatch(artifact):
                issues.append(f"{key}: compiled artifact digest required")
            if row.get("artifact_sha256") != artifact:
                issues.append(f"{key}: artifact digest mismatch")
    eligible = all_pass and not open_issues and data.get("reviewer_independent") is True
    if data.get("release_recommendation") == "PASS" and not eligible:
        issues.append("PASS recommendation contradicts required gate evidence")
    if data.get("release_recommendation") == "BLOCKED" and eligible:
        issues.append("BLOCKED recommendation contradicts completed gate state")
    return {"status": "PASS" if not issues and eligible else "BLOCKED",
            "issues": issues, "all_gates_pass": all_pass,
            "release_authorized": False,
            "note": "Evidence-reference format only; external checks and human approval remain independent."}


def unique_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dossier", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.dossier.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
        result = evaluate(data)
    except (OSError, ValueError, TypeError) as exc:
        result = {"status": "BLOCKED", "issues": [str(exc)], "release_authorized": False}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
