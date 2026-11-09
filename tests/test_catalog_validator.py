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

    def test_malformed_catalog_values_fail_without_raising(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "catalog").mkdir()
            (root / "catalog/roles.json").write_text(json.dumps({"roles": [None, {"id": []}]}))
            (root / "catalog/resource-chain.json").write_text(json.dumps({
                "resources": [{}], "stages": [None, {"id": "stage", "depends_on": None, "consumes": [[]]}]
            }))
            result = validate(root)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(result["errors"])

    def test_symlinked_skill_roots_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            self.fixture(root)
            skills = root / ".agents/skills"
            saved = root / "saved-skills"
            skills.rename(saved)
            skills.symlink_to(outside, target_is_directory=True)
            result = validate(root)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("unsafe SKILL.md" in message for message in result["errors"]))

    def test_symlinked_catalog_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            self.fixture(root)
            roles = root / "catalog/roles.json"
            external = Path(outside) / "roles.json"
            external.write_text(roles.read_text())
            roles.unlink()
            roles.symlink_to(external)
            result = validate(root)
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["errors"], ["catalog files are missing or unsafe"])

    def test_long_acyclic_graph_does_not_recurse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chain = self.fixture(root)
            chain["stages"] = [
                {"id": f"stage-{index}", "role": "worker",
                 "depends_on": [f"stage-{index - 1}"] if index else [],
                 "consumes": ["input"], "produces": ["output"]}
                for index in reversed(range(2000))
            ]
            (root / "catalog/resource-chain.json").write_text(json.dumps(chain))
            self.assertEqual(validate(root)["status"], "PASS")
