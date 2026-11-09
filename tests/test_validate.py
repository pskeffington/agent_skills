import json
import pathlib
import sys
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import validate, validate_document

class ControlPlaneTests(unittest.TestCase):
    def test_catalog(self):
        self.assertEqual([], validate())

    def test_schema_validation_rejects_nested_and_unknown_fields(self):
        schema={"type":"object","additionalProperties":False,"required":["count"],"properties":{"count":{"type":"integer","minimum":1}}}
        self.assertEqual([],validate_document({"count":2},schema))
        self.assertTrue(validate_document({"count":0,"extra":True},schema))
        self.assertTrue(validate_document({"count":True},schema))

    def test_release_example_is_schema_valid_but_semantically_blocked(self):
        from release_gate import evaluate
        doc=json.loads((ROOT/"examples/release-dossier.json").read_text())
        self.assertFalse(evaluate(doc)["release_ready"])

    def test_all_roles_have_skill(self):
        roles = json.loads((ROOT / "catalog/roles.json").read_text())["roles"]
        self.assertGreaterEqual(len(roles), 10)
        for role in roles:
            self.assertTrue((ROOT / ".agents" / "skills" / role["skill"] / "SKILL.md").is_file())

    def test_release_human_owned(self):
        stages = json.loads((ROOT / "catalog/resource-chain.json").read_text())["stages"]
        release = next(s for s in stages if s["id"] == "release")
        self.assertTrue({"verify", "security", "review", "document"} <= set(release["depends_on"]))

if __name__ == "__main__":
    unittest.main()
