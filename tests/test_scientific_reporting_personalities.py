"""Study-neutral consistency checks for scientific reporting role profiles."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/scientific-reporting-qa"
EXPECTED = {
    "evidence-steward": "Evidence Steward",
    "methods-reviewer": "Methods Reviewer",
    "scientific-editor": "Scientific Editor",
    "typesetting-engineer": "Typesetting Engineer",
    "acceptance-reviewer": "Acceptance Reviewer",
}


class ReportingPersonalityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = (SKILL / "references/role-personalities.md").read_text()
        cls.chain = json.loads((ROOT / "catalog/scientific-reporting-chain.json").read_text())
        cls.roles = json.loads((ROOT / "catalog/roles.json").read_text())["roles"]
        cls.skill = (SKILL / "SKILL.md").read_text()

    def test_five_profiles_are_defined(self):
        for role, heading in EXPECTED.items():
            with self.subTest(role=role):
                self.assertIn(heading, self.profile)
        self.assertIn("not fictional identities", self.profile)

    def test_each_stage_has_a_known_persona(self):
        assigned = [stage["persona"] for stage in self.chain["stages"]]
        self.assertTrue(all(name in EXPECTED for name in assigned))
        self.assertEqual(set(assigned), set(EXPECTED))

    def test_registered_role_links_profile(self):
        reviewer = next(x for x in self.roles if x["id"] == "scientific-reporting-reviewer")
        self.assertEqual(reviewer["personality_profile"],
                         ".agents/skills/scientific-reporting-qa/references/role-personalities.md")

    def test_skill_links_to_profiles(self):
        self.assertIn("references/role-personalities.md", self.skill)

    def test_independence_boundary_preserved(self):
        self.assertIn("not to claim independent sign-off", self.skill)
        self.assertIn("same-instance rechecking alone is not independent review",
                      self.profile)


if __name__ == "__main__":
    unittest.main()
