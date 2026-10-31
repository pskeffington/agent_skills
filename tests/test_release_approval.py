import base64
import copy
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

from agent_toolset.assurance.approval import (
    canonical_approval_payload,
    dossier_binding_sha256,
    load_trust_store,
    make_openssl_approval_verifier,
)
from agent_toolset.assurance.release import REQUIRED, evaluate


OPENSSL = shutil.which("openssl")
ROOT = pathlib.Path(__file__).resolve().parents[1]


@unittest.skipUnless(OPENSSL, "OpenSSL is required for detached signature tests")
class ReleaseApprovalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.private = self.root / "approver-private.pem"
        self.public = self.root / "approver-public.pem"
        subprocess.run(
            [OPENSSL, "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(self.private)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            [OPENSSL, "pkey", "-in", str(self.private), "-pubout", "-out", str(self.public)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        self.approvers = {"operator-42": {
            "authority_ref": "change-control:42",
            "public_key_pem": self.public.read_text(encoding="ascii"),
        }}

    def tearDown(self):
        self.temp.cleanup()

    def approval(self):
        return {
            "evidence_ref": "approval:request-42",
            "subject_commit": "a" * 40,
            "artifact_sha256": "b" * 64,
            "dossier_sha256": "c" * 64,
            "invocation_id": "approval-run-42",
            "decision": "APPROVE",
            "approver_id": "operator-42",
            "authority_ref": "change-control:42",
            "signature_algorithm": "openssl-dgst-sha256",
        }

    def sign(self, approval):
        payload_path = self.root / "approval.json"
        signature_path = self.root / "approval.sig"
        payload_path.write_bytes(canonical_approval_payload(approval))
        subprocess.run(
            [OPENSSL, "dgst", "-sha256", "-sign", str(self.private), "-out", str(signature_path), str(payload_path)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        approval["signature"] = base64.b64encode(signature_path.read_bytes()).decode("ascii")
        return approval

    def test_signature_authenticates_identity_commit_and_artifact(self):
        approval = self.sign(self.approval())
        verifier = make_openssl_approval_verifier(self.approvers, openssl=OPENSSL)
        self.assertIs(verifier(approval, "a" * 40, "b" * 64), True)
        self.assertIs(verifier(approval, "c" * 40, "b" * 64), False)
        self.assertIs(verifier(approval, "a" * 40, "d" * 64), False)
        forged = dict(approval, approver_id="operator-99")
        self.assertIs(verifier(forged, "a" * 40, "b" * 64), False)
        altered = dict(approval, authority_ref="change-control:other")
        self.assertIs(verifier(altered, "a" * 40, "b" * 64), False)
        altered = dict(approval, evidence_ref="approval:substituted")
        self.assertIs(verifier(altered, "a" * 40, "b" * 64), False)

    def test_signed_approval_allows_ready_classification_only_with_trusted_key(self):
        commit = "a" * 40
        artifact_path = (self.root / "signed-candidate.pyz").resolve()
        artifact_path.write_bytes(b"release-approved artifact bytes")
        artifact = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        attestation = lambda ref, run: {
            "evidence_ref": ref, "subject_commit": commit,
            "artifact_sha256": artifact, "invocation_id": run,
        }
        approval = {**attestation("approval:request-42", "approver-run"),
            "dossier_sha256": "0" * 64, "decision": "APPROVE", "approver_id": "operator-42",
            "authority_ref": "change-control:42", "signature_algorithm": "openssl-dgst-sha256"}
        dossier = {
            "schema_version": "2.0.0", "commit": commit, "artifact_sha256": artifact, "target_environment": "staging",
            "gates": {gate: {"status": "PASS", "evidence_ref": f"check:{gate}", "reason": "actual recorded pass"} for gate in REQUIRED},
            "implementation": attestation("implementation:42", "implementer-run"),
            "independent_review": attestation("review:42", "review-run"),
            "security_review": attestation("security:42", "security-run"),
            "staging": attestation("staging:42", "staging-run"),
            "approval": approval, "rollback_ref": "rollback:42", "check_provenance": ["ci:run-42"],
        }
        approval["dossier_sha256"] = dossier_binding_sha256(dossier)
        dossier["approval"] = self.sign(approval)
        verifier = make_openssl_approval_verifier(self.approvers, openssl=OPENSSL)
        self.assertEqual("BLOCKED", evaluate(dossier)["status"])
        self.assertEqual("PASS", evaluate(dossier, approval_verifier=verifier, artifact_path=artifact_path)["status"])
        not_applicable = copy.deepcopy(dossier)
        not_applicable["gates"]["G5"] = {
            "status": "NOT_APPLICABLE",
            "evidence_ref": "decision:g5-na-42",
            "reason": "this candidate has no G5-specific change",
        }
        na_approval = dict(not_applicable["approval"])
        na_approval.pop("signature", None)
        na_approval["invocation_id"] = "approver-na-run"
        not_applicable["approval"] = na_approval
        na_approval["dossier_sha256"] = dossier_binding_sha256(not_applicable)
        not_applicable["approval"] = self.sign(na_approval)
        self.assertEqual("PASS", evaluate(not_applicable, approval_verifier=verifier, artifact_path=artifact_path)["status"])
        incomplete_na = copy.deepcopy(not_applicable)
        incomplete_na["gates"]["G5"]["reason"] = ""
        incomplete_approval = dict(incomplete_na["approval"])
        incomplete_approval.pop("signature", None)
        incomplete_approval["invocation_id"] = "approver-na-incomplete-run"
        incomplete_na["approval"] = incomplete_approval
        incomplete_approval["dossier_sha256"] = dossier_binding_sha256(incomplete_na)
        incomplete_na["approval"] = self.sign(incomplete_approval)
        self.assertEqual("BLOCKED", evaluate(incomplete_na, approval_verifier=verifier, artifact_path=artifact_path)["status"])
        altered_dossier = copy.deepcopy(dossier)
        altered_dossier["target_environment"] = "production"
        self.assertEqual("FAIL", evaluate(altered_dossier, approval_verifier=verifier, artifact_path=artifact_path)["status"])
        altered_dossier = copy.deepcopy(dossier)
        altered_dossier["gates"]["G0"]["evidence_ref"] = "check:substituted"
        self.assertEqual("FAIL", evaluate(altered_dossier, approval_verifier=verifier, artifact_path=artifact_path)["status"])
        altered_dossier = copy.deepcopy(dossier)
        altered_dossier["rollback_ref"] = "rollback:other"
        self.assertEqual("FAIL", evaluate(altered_dossier, approval_verifier=verifier, artifact_path=artifact_path)["status"])
        dossier["artifact_sha256"] = "c" * 64
        self.assertEqual("FAIL", evaluate(dossier, approval_verifier=verifier, artifact_path=artifact_path)["status"])

    def test_release_cli_verifies_trust_store_and_detached_signature(self):
        commit = "a" * 40
        artifact_path = (self.root / "candidate.pyz").resolve()
        artifact_path.write_bytes(b"exact candidate artifact bytes")
        artifact = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        attestation = lambda ref, run: {
            "evidence_ref": ref, "subject_commit": commit,
            "artifact_sha256": artifact, "invocation_id": run,
        }
        approval = {**attestation("approval:request-42", "approver-run"),
            "dossier_sha256": "0" * 64, "decision": "APPROVE", "approver_id": "operator-42",
            "authority_ref": "change-control:42", "signature_algorithm": "openssl-dgst-sha256"}
        dossier = {
            "schema_version": "2.0.0", "commit": commit, "artifact_sha256": artifact, "target_environment": "staging",
            "gates": {gate: {"status": "PASS", "evidence_ref": f"check:{gate}", "reason": "actual recorded pass"} for gate in REQUIRED},
            "implementation": attestation("implementation:42", "implementer-run"),
            "independent_review": attestation("review:42", "review-run"),
            "security_review": attestation("security:42", "security-run"),
            "staging": attestation("staging:42", "staging-run"),
            "approval": approval, "rollback_ref": "rollback:42", "check_provenance": ["ci:run-42"],
        }
        approval["dossier_sha256"] = dossier_binding_sha256(dossier)
        dossier["approval"] = self.sign(approval)
        dossier_path = self.root / "release.json"
        dossier_path.write_text(json.dumps(dossier), encoding="utf-8")
        trust_path = self.root / "trust.json"
        trust_path.write_text(json.dumps({"schema_version": "1.0.0", "approvers": self.approvers}), encoding="utf-8")
        trust_path.chmod(0o600)
        env = {"PATH": str(pathlib.Path(OPENSSL).parent) + os.pathsep + "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "agent_toolset", "release-check", str(dossier_path), "--artifact", str(artifact_path), "--approval-trust-store", str(trust_path)],
            cwd=ROOT, env=env, capture_output=True, text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("PASS", json.loads(result.stdout)["status"])
        compatibility = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "release_gate.py"), "--evidence", str(dossier_path), "--approval-trust-store", str(trust_path)],
            cwd=ROOT, env=env, capture_output=True, text=True,
        )
        self.assertEqual(2, compatibility.returncode, compatibility.stdout)
        self.assertEqual("BLOCKED", json.loads(compatibility.stdout)["status"])
        compatibility = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "release_gate.py"), "--evidence", str(dossier_path), "--artifact", str(artifact_path), "--approval-trust-store", str(trust_path)],
            cwd=ROOT, env=env, capture_output=True, text=True,
        )
        self.assertEqual(0, compatibility.returncode, compatibility.stdout + compatibility.stderr)
        self.assertEqual("PASS", json.loads(compatibility.stdout)["status"])

    def test_trust_store_loading_rejects_writable_and_symlinked_store(self):
        store = self.root / "trust.json"
        store.write_text(json.dumps({"schema_version": "1.0.0", "approvers": {
            "operator-42": {"authority_ref": "change-control:42", "public_key_pem": self.approvers["operator-42"]["public_key_pem"]},
        }}), encoding="utf-8")
        store.chmod(0o600)
        self.assertEqual(self.approvers, load_trust_store(store))
        store.chmod(0o666)
        with self.assertRaises(ValueError):
            load_trust_store(store)
        alias = self.root / "trust-link.json"
        alias.symlink_to(store)
        with self.assertRaises(OSError):
            load_trust_store(alias)

    def test_trust_store_rejects_duplicate_identity_keys(self):
        record = json.dumps({"authority_ref": "change-control:42", "public_key_pem": self.approvers["operator-42"]["public_key_pem"]})
        store = self.root / "duplicate-trust.json"
        store.write_text('{"schema_version":"1.0.0","approvers":{"operator-42":' + record + ',"operator-42":' + record + '}}', encoding="utf-8")
        store.chmod(0o600)
        with self.assertRaisesRegex(ValueError, "duplicate trust store key"):
            load_trust_store(store)

    def test_unavailable_openssl_is_unknown_not_success(self):
        verifier = make_openssl_approval_verifier(self.approvers, openssl="/missing/openssl")
        self.assertIsNone(verifier(self.sign(self.approval()), "a" * 40, "b" * 64))

    def test_key_policy_accepts_p256_and_rejects_ed25519(self):
        ec_private, ec_public = self.root / "ec-private.pem", self.root / "ec-public.pem"
        subprocess.run([OPENSSL, "genpkey", "-algorithm", "EC", "-pkeyopt", "ec_paramgen_curve:P-256", "-out", str(ec_private)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([OPENSSL, "pkey", "-in", str(ec_private), "-pubout", "-out", str(ec_public)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        approval = self.approval()
        payload_path, signature_path = self.root / "ec-approval.json", self.root / "ec-approval.sig"
        payload_path.write_bytes(canonical_approval_payload(approval))
        subprocess.run([OPENSSL, "dgst", "-sha256", "-sign", str(ec_private), "-out", str(signature_path), str(payload_path)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        approval["signature"] = base64.b64encode(signature_path.read_bytes()).decode("ascii")
        ec_verifier = make_openssl_approval_verifier({"operator-42": {"authority_ref": "change-control:42", "public_key_pem": ec_public.read_text(encoding="ascii")}}, openssl=OPENSSL)
        self.assertIs(ec_verifier(approval, "a" * 40, "b" * 64), True)

        ed_private, ed_public = self.root / "ed-private.pem", self.root / "ed-public.pem"
        subprocess.run([OPENSSL, "genpkey", "-algorithm", "ED25519", "-out", str(ed_private)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([OPENSSL, "pkey", "-in", str(ed_private), "-pubout", "-out", str(ed_public)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ed_verifier = make_openssl_approval_verifier({"operator-42": {"authority_ref": "change-control:42", "public_key_pem": ed_public.read_text(encoding="ascii")}}, openssl=OPENSSL)
        self.assertIs(ed_verifier(approval, "a" * 40, "b" * 64), False)

        small_private, small_public = self.root / "small-private.pem", self.root / "small-public.pem"
        subprocess.run([OPENSSL, "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:1024", "-out", str(small_private)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([OPENSSL, "pkey", "-in", str(small_private), "-pubout", "-out", str(small_public)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        small_verifier = make_openssl_approval_verifier({"operator-42": {"authority_ref": "change-control:42", "public_key_pem": small_public.read_text(encoding="ascii")}}, openssl=OPENSSL)
        self.assertIs(small_verifier(approval, "a" * 40, "b" * 64), False)


if __name__ == "__main__":
    unittest.main()
