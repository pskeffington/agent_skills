import json
import tempfile
import unittest
from pathlib import Path
from agent_toolset.catalog_validator import validate

class CatalogValidationTests(unittest.TestCase):
    def fixture(self, root):
        (root / "catalog").mkdir()
        (root / ".agents/skills/demo/agents").mkdir(parents=True)
        (root / ".agents/skills/demo/SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\n")
        (root / ".agents/skills/demo/agents/openai.yaml").write_text("interface: {}")
        roles = {"human_authority": "human", "roles": [{"id": "worker", "skill": "demo", "reports_to": "human"}]}
        chain = {"resources": ["input", "output"], "stages": [{"id": "one", "role": "worker", "depends_on": [], "consumes": ["input"], "produces": ["output"]}]}
        (root / "catalog/roles.json").write_text(json.dumps(roles))
        (root / "catalog/resource-chain.json").write_text(json.dumps(chain))
        return chain

    def test_valid_and_missing_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            self.assertEqual(validate(root)["status"], "PASS")
            (root / ".agents/skills/demo/SKILL.md").unlink()
            self.assertEqual(validate(root)["status"], "FAIL")

    def test_cycle_and_unknown_resource(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chain = self.fixture(root)
            chain["stages"][0]["depends_on"] = ["one"]
            chain["stages"][0]["consumes"] = ["unknown"]
            (root / "catalog/resource-chain.json").write_text(json.dumps(chain))
            result = validate(root)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("cycle" in message for message in result["errors"]))

    def test_missing_catalog_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(validate(tmp)["status"], "FAIL")
