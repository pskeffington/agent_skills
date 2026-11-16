"""Study-neutral contract tests for the optional reporting review branch."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ScientificReportingChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chain = json.loads((ROOT / "catalog/scientific-reporting-chain.json").read_text())
        cls.general = json.loads((ROOT / "catalog/resource-chain.json").read_text())
        cls.roles = json.loads((ROOT / "catalog/roles.json").read_text())["roles"]

    def test_opt_in_scope(self):
        self.assertEqual(self.chain["owner_role"], "scientific-reporting-reviewer")
        self.assertIn("Only when", self.chain["trigger"])

    def test_topological_dependencies(self):
        seen = set()
        for stage in self.chain["stages"]:
            self.assertTrue(set(stage["depends_on"]).issubset(seen))
            self.assertNotIn(stage["id"], seen)
            seen.add(stage["id"])

    def test_evidence_gate_completeness(self):
        keys = [s["evidence_key"] for s in self.chain["stages"]]
        self.assertEqual(keys, [f"E{i}" for i in range(1, 9)])

    def test_role_is_registered(self):
        roles = {r["id"] for r in self.roles}
        self.assertTrue(all(s["owner"] in roles for s in self.chain["stages"]))

    def test_general_software_release_not_replaced(self):
        general_stages = {s["id"] for s in self.general["stages"]}
        self.assertIn("release", general_stages)
        self.assertNotIn("reporting-handoff", general_stages)
        self.assertEqual(
            self.chain["release_interlock"]["software_release_graph"],
            "unchanged; this is an opt-in specialized branch",
        )

    def test_artifact_and_human_approval_binding(self):
        guard = self.chain["release_interlock"]
        self.assertIn("SHA-256", guard["pass_condition"])
        self.assertIn("Human", guard["human_approval"])


if __name__ == "__main__":
    unittest.main()
