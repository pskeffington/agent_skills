#!/usr/bin/env python3
"""Local fail-closed release dossier evaluator; cannot deploy."""
import argparse
import json
import pathlib
import re
import sys
from .artifact import verify_artifact
from .approval import dossier_binding_sha256

REQUIRED = ("G0", "G1", "G2", "G3", "G4", "G5", "G6")
DOSSIER_SCHEMA_VERSION = "2.0.0"
SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
ATTESTATIONS = ("implementation", "independent_review", "security_review", "staging", "approval")

def _pointer(value):
    return isinstance(value, str) and len(value.strip()) >= 3

def _evaluate_dossier(doc, approval_verifier=None):
    if not isinstance(doc, dict):
        return {"release_ready":False,"status":"BLOCKED","issues":["dossier must be an object"],"notice":"Read-only evaluation. No deployment performed."}
    issues=[]
    contradictions=False
    if doc.get("schema_version") != DOSSIER_SCHEMA_VERSION:
        issues.append(f"unsupported release dossier schema version (expected {DOSSIER_SCHEMA_VERSION})")
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
        try:
            expected_dossier_digest=dossier_binding_sha256(doc)
        except (TypeError,ValueError) as exc:
            expected_dossier_digest=None
            issues.append("release dossier approval binding could not be computed: " + str(exc))
        approval_dossier_digest=approval.get("dossier_sha256")
        if not isinstance(approval_dossier_digest,str) or not DIGEST.fullmatch(approval_dossier_digest):
            issues.append("approval dossier content digest missing or invalid")
        elif expected_dossier_digest is not None and approval_dossier_digest != expected_dossier_digest:
            issues.append("approval does not bind the current release dossier contents")
            contradictions=True
        if approval.get("decision") != "APPROVE":
            issues.append("approval decision must explicitly be APPROVE")
            contradictions = contradictions or approval.get("decision") in ("REJECT", "DENY")
        if not _pointer(approval.get("approver_id")):
            issues.append("approval approver identity missing")
        if not _pointer(approval.get("authority_ref")):
            issues.append("approval authority reference missing")
        if approval_verifier is None:
            issues.append("approval authenticity verifier unavailable")
        else:
            try:
                verified = approval_verifier(approval, commit, digest)
            except Exception as exc:
                verified = None
                issues.append("approval verifier error: " + type(exc).__name__)
            if verified is True:
                pass
            elif verified is False:
                issues.append("approval authenticity verification failed")
                contradictions = True
            elif verified is None:
                issues.append("approval authenticity verification unavailable")
            else:
                issues.append("approval verifier returned invalid result")
                contradictions = True
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

def evaluate(doc, approval_verifier=None, *, artifact_path=None):
    """Return release readiness only after verifying the candidate artifact bytes."""
    result=_evaluate_dossier(doc,approval_verifier=approval_verifier)
    if not artifact_path:
        result["release_ready"]=False
        result["status"]="FAIL" if result["status"]=="FAIL" else "BLOCKED"
        result["issues"].append("candidate artifact path is required")
        result["artifact_integrity"]={"status":"BLOCKED","issues":["candidate artifact path is required"]}
        return result
    expected_digest=doc.get("artifact_sha256") if isinstance(doc,dict) else None
    integrity=verify_artifact(artifact_path,expected_digest)
    result["artifact_integrity"]={key:value for key,value in integrity.items() if key != "notice"}
    if integrity["status"] != "PASS":
        result["release_ready"]=False
        result["issues"].append("candidate artifact integrity verification " + integrity["status"].lower())
        if integrity["status"] == "FAIL":
            result["status"]="FAIL"
        elif result["status"] != "FAIL":
            result["status"]="BLOCKED"
    return result

def example():
    return {"schema_version":DOSSIER_SCHEMA_VERSION,"commit":"0"*40,"artifact_sha256":"0"*64,"target_environment":"example",
            "gates":{g:{"status":"BLOCKED","evidence_ref":None,"reason":"synthetic example"} for g in REQUIRED},
            "independent_review":None,"security_review":None,"staging":None,"approval":None,"rollback_ref":None,"check_provenance":[]}

