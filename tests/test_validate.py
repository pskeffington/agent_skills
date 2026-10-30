import json
import pathlib
import sys
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import validate

class ControlPlaneTests(unittest.TestCase):
    def test_catalog(self):
        self.assertEqual([], validate())

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
