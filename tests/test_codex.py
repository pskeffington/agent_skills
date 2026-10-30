import pathlib
import sys
import tempfile
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from release_gate import evaluate,example,REQUIRED
from codex_preflight import preflight

class CodexTests(unittest.TestCase):
    def test_default_dossier_fails_closed(self):
        result=evaluate(example())
        self.assertFalse(result["release_ready"])
        self.assertIn("G6 is not PASS",result["issues"])

    def packet(self):
        commit="a"*40; digest="b"*64
        attestation=lambda ref, invocation: {"evidence_ref":ref,"subject_commit":commit,"artifact_sha256":digest,"invocation_id":invocation}
        return {"commit":commit,"artifact_sha256":digest,"target_environment":"staging",
          "gates":{g:{"status":"PASS","evidence_ref":f"evidence:{g}","reason":"required checks passed"} for g in REQUIRED},
          "implementation":attestation("implementation:12","implementer-run"),
          "independent_review":attestation("review:12","reviewer-run"),
          "security_review":attestation("security:12","security-run"),
          "staging":attestation("stage:12","stage-run"),
          "approval":{**attestation("approval:12","approver-run"),"decision":"APPROVE","approver_id":"operator-42","authority_ref":"change-control:42"},
          "rollback_ref":"runbook:12","check_provenance":["ci:123"]}

    def test_structured_exact_subject_dossier_classifies_ready_only(self):
        self.assertFalse(evaluate(self.packet())["release_ready"])
        self.assertIn("approval authenticity verifier unavailable",evaluate(self.packet())["issues"])
        verifier=lambda approval, commit, digest: approval["decision"] == "APPROVE" and approval["subject_commit"] == commit and approval["artifact_sha256"] == digest
        self.assertTrue(evaluate(self.packet(),approval_verifier=verifier)["release_ready"])

    def test_approval_requires_explicit_decision_and_verification(self):
        packet=self.packet(); packet["approval"]["decision"]="REJECT"
        self.assertEqual("FAIL",evaluate(packet,approval_verifier=lambda *_: True)["status"])
        packet=self.packet()
        self.assertEqual("FAIL",evaluate(packet,approval_verifier=lambda *_: False)["status"])
        self.assertEqual("BLOCKED",evaluate(packet,approval_verifier=lambda *_: None)["status"])

    def test_stale_or_unstructured_attestation_blocked(self):
        packet=self.packet(); packet["staging"]["subject_commit"]="c"*40
        result=evaluate(packet)
        self.assertFalse(result["release_ready"])
        self.assertIn("staging is for a different commit",result["issues"])
        self.assertEqual("FAIL",result["status"])
        packet=self.packet(); packet["independent_review"]="review:12"
        result=evaluate(packet)
        self.assertFalse(result["release_ready"])
        self.assertEqual("BLOCKED",result["status"])

    def test_same_invocation_cannot_review_or_secure_approval(self):
        packet=self.packet(); packet["independent_review"]["invocation_id"]="implementer-run"
        self.assertEqual("FAIL",evaluate(packet)["status"])
        packet=self.packet(); packet["security_review"]["invocation_id"]="implementer-run"
        self.assertEqual("FAIL",evaluate(packet)["status"])
        packet=self.packet(); packet["approval"]["invocation_id"]="reviewer-run"
        self.assertIn("reviewer must be independent from approver",evaluate(packet)["issues"])
        packet=self.packet(); packet["approval"]["invocation_id"]="security-run"
        self.assertIn("security reviewer must be independent from approver",evaluate(packet)["issues"])

    def test_nonexistent_repo_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(preflight(pathlib.Path(d)/"not-here")["result"],"BLOCKED")

if __name__=="__main__": unittest.main()
