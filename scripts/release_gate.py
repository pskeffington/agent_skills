#!/usr/bin/env python3
"""Local dry-run release dossier evaluator; cannot deploy."""
import argparse
import json
import pathlib
import re
import sys

REQUIRED = ("G0", "G1", "G2", "G3", "G4", "G5", "G6")
SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")

def evaluate(doc):
    issues = []
    if not SHA.fullmatch(str(doc.get("commit", ""))):
        issues.append("missing valid immutable commit")
    if not DIGEST.fullmatch(str(doc.get("artifact_sha256", ""))):
        issues.append("missing artifact SHA256")
    gates = doc.get("gates")
    if not isinstance(gates, dict):
        gates = {}
        issues.append("gates must be a mapping")
    for gate in REQUIRED:
        if gates.get(gate) != "PASS":
            issues.append(gate + " is not PASS")
    if not doc.get("independent_review_ref"):
        issues.append("independent review missing")
    if not doc.get("security_review_ref"):
        issues.append("security review missing")
    if not doc.get("rollback_ref"):
        issues.append("rollback plan missing")
    if not doc.get("staging_evidence_ref"):
        issues.append("staging evidence missing")
    if not doc.get("approval_ref"):
        issues.append("explicit human production approval missing")
    if not doc.get("target_environment"):
        issues.append("target environment missing")
    if not doc.get("check_provenance"):
        issues.append("checks lack provenance")
    return {"release_ready": not issues, "status": "PASS" if not issues else "BLOCKED", "issues": issues,
            "notice": "Read-only evaluation. No deployment performed."}

def example():
    return {"commit": "0"*40, "artifact_sha256":"0"*64, "target_environment":"example",
            "gates":{g:"BLOCKED" for g in REQUIRED},
            "independent_review_ref":None, "security_review_ref":None,
            "rollback_ref":None, "staging_evidence_ref":None,"approval_ref":None,"check_provenance":[]}

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--example", action="store_true")
    group.add_argument("--evidence")
    a=parser.parse_args()
    try:
        data=example() if a.example else json.loads(pathlib.Path(a.evidence).read_text(encoding="utf-8"))
        result=evaluate(data)
    except (ValueError,OSError,TypeError) as e:
        result={"status":"BLOCKED","release_ready":False,"issues":[str(e)]}
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["release_ready"] else 2)
