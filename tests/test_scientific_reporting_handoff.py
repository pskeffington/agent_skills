"""Synthetic, study-neutral tests for the reporting release interlock."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".agents/skills/scientific-reporting-qa/scripts/validate_reporting_handoff.py"
SPEC = importlib.util.spec_from_file_location("reporting_handoff", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def clean_dossier():
    commit = "a" * 40
    artifact = "b" * 64
    return {
        "schema_version": "1.0.0",
        "task_id": "REPORT-001",
        "source_repository": "example/research",
        "source_commit": commit,
        "artifact_sha256": artifact,
        "reviewer_role": "scientific-reporting-reviewer",
        "reviewer_independent": True,
        "release_recommendation": "PASS",
        "open_issues": [],
        "gates": {
            f"E{n}": {
                "status": "PASS",
                "source_commit": commit,
                "evidence_ref": f"artifact/evidence-{n}.json",
                "method": "Independent recorded review",
                **({"artifact_sha256": artifact} if n >= 6 else {})
            }
            for n in range(1, 9)
        }
    }


class ReportingHandoffTests(unittest.TestCase):
    def test_complete_dossier_structurally_passes(self):
        result = MODULE.evaluate(clean_dossier())
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["release_authorized"])

    def test_missing_gate_fails_closed(self):
        dossier = clean_dossier()
        del dossier["gates"]["E7"]
        self.assertEqual(MODULE.evaluate(dossier)["status"], "BLOCKED")

    def test_unrun_gate_blocks_release(self):
        dossier = clean_dossier()
        dossier["gates"]["E6"].update(status="BLOCKED", reason="No approved runtime")
        self.assertEqual(MODULE.evaluate(dossier)["status"], "BLOCKED")

    def test_mismatched_source_commit_blocks(self):
        dossier = clean_dossier()
        dossier["gates"]["E5"]["source_commit"] = "c" * 40
        self.assertEqual(MODULE.evaluate(dossier)["status"], "BLOCKED")

    def test_mismatched_artifact_blocks(self):
        dossier = clean_dossier()
        dossier["gates"]["E7"]["artifact_sha256"] = "c" * 64
        self.assertEqual(MODULE.evaluate(dossier)["status"], "BLOCKED")

    def test_missing_evidence_blocks(self):
        dossier = clean_dossier()
        dossier["gates"]["E2"]["evidence_ref"] = ""
        self.assertEqual(MODULE.evaluate(dossier)["status"], "BLOCKED")

    def test_review_self_approval_blocks(self):
        dossier = clean_dossier()
        dossier["reviewer_independent"] = False
        self.assertEqual(MODULE.evaluate(dossier)["status"], "BLOCKED")

    def test_open_issues_block(self):
        dossier = clean_dossier()
        dossier["open_issues"] = ["Unresolved source/PDF mismatch"]
        self.assertEqual(MODULE.evaluate(dossier)["status"], "BLOCKED")

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.unique_keys([("task_id", "x"), ("task_id", "y")])


if __name__ == "__main__":
    unittest.main()
