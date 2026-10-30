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

    def test_fully_supported_dossier_classifies_ready_only(self):
        packet=example()
        packet.update(commit="a"*40, artifact_sha256="b"*64,
          gates={g:"PASS" for g in REQUIRED},
          independent_review_ref="review:1",security_review_ref="security:1",
          rollback_ref="runbook:1",staging_evidence_ref="stage:1",approval_ref="approval:1",
          check_provenance=["ci:123"])
        self.assertTrue(evaluate(packet)["release_ready"])

    def test_nonexistent_repo_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(preflight(pathlib.Path(d)/"not-here")["result"],"BLOCKED")

if __name__=="__main__":
    unittest.main()
