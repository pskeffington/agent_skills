#!/usr/bin/env python3
"""Local fail-closed release dossier evaluator; cannot deploy."""
import argparse
import json
import pathlib
import re
import sys

REQUIRED = ("G0", "G1", "G2", "G3", "G4", "G5", "G6")
SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
ATTESTATIONS = ("implementation", "independent_review", "security_review", "staging", "approval")

def _pointer(value):
    return isinstance(value, str) and len(value.strip()) >= 3

def evaluate(doc):
    if not isinstance(doc, dict):
        return {"release_ready":False,"status":"BLOCKED","issues":["dossier must be an object"],"notice":"Read-only evaluation. No deployment performed."}
    issues=[]
    contradictions=False
    commit=doc.get("commit")
    digest=doc.get("artifact_sha256")
    if not isinstance(commit,str) or not SHA.fullmatch(commit): issues.append("missing valid immutable commit")
    if not isinstance(digest,str) or not DIGEST.fullmatch(digest): issues.append("missing artifact SHA256")
    gates=doc.get("gates")
    if not isinstance(gates,dict):
        gates={}; issues.append("gates must be a mapping")
    else:
        for gate in REQUIRED:
            record=gates.get(gate)
            if not isinstance(record,dict):
                issues.append(gate + " evidence missing")
            elif record.get("status") != "PASS":
                issues.append(gate + " is not PASS")
                contradictions = contradictions or record.get("status") == "FAIL"
            if isinstance(record,dict) and (not _pointer(record.get("evidence_ref")) or not _pointer(record.get("reason"))):
                issues.append(gate + " evidence pointer or reason missing")
    for key in ATTESTATIONS:
        record=doc.get(key)
        if not isinstance(record,dict):
            issues.append(key.replace("_"," ") + " attestation missing")
            continue
        for field in ("evidence_ref","subject_commit","artifact_sha256","invocation_id"):
            if not _pointer(record.get(field)): issues.append(f"{key} {field} missing")
        if isinstance(commit,str) and record.get("subject_commit") != commit:
            issues.append(f"{key} is for a different commit")
            contradictions=True
        if isinstance(digest,str) and record.get("artifact_sha256") != digest:
            issues.append(f"{key} is for a different artifact")
            contradictions=True
    implementation=doc.get("implementation")
    review=doc.get("independent_review")
    approval=doc.get("approval")
    security=doc.get("security_review")
    if isinstance(implementation,dict) and isinstance(review,dict) and implementation.get("invocation_id") == review.get("invocation_id"):
        issues.append("reviewer must be independent from implementer")
        contradictions=True
    if isinstance(implementation,dict) and isinstance(security,dict) and implementation.get("invocation_id") == security.get("invocation_id"):
        issues.append("security reviewer must be independent from implementer")
        contradictions=True
    if isinstance(approval,dict):
        for name,attestation in (("implementer",implementation),("reviewer",review),("security reviewer",security)):
            if isinstance(attestation,dict) and attestation.get("invocation_id") == approval.get("invocation_id"):
                issues.append(f"{name} must be independent from approver")
                contradictions=True
    if not _pointer(doc.get("rollback_ref")): issues.append("rollback plan missing")
    if not _pointer(doc.get("target_environment")): issues.append("target environment missing")
    provenance=doc.get("check_provenance")
    if not isinstance(provenance,list) or not provenance or not all(_pointer(item) for item in provenance):
        issues.append("checks lack provenance")
    release_ready=not issues
    status="PASS" if release_ready else ("FAIL" if contradictions else "BLOCKED")
    return {"release_ready":release_ready,"status":status,"issues":issues,"notice":"Read-only evaluation. No deployment performed."}

def example():
    return {"commit":"0"*40,"artifact_sha256":"0"*64,"target_environment":"example",
            "gates":{g:{"status":"BLOCKED","evidence_ref":None,"reason":"synthetic example"} for g in REQUIRED},
            "independent_review":None,"security_review":None,"staging":None,"approval":None,"rollback_ref":None,"check_provenance":[]}

