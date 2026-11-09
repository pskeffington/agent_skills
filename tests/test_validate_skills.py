"""Small fixture-driven tests for fail-closed metadata and index behavior."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from index_skills import build_catalog, parse_skill, render_catalog
from new_skill import new_skill
from validate_skills import validate


class SkillTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "templates" / "skill" / "agents").mkdir(parents=True)
        original = Path(__file__).resolve().parents[1] / "templates" / "skill"
        for f in original.rglob("*.tmpl"):
            dest = self.root / "templates" / "skill" / f.relative_to(original)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
        (self.root / "data").mkdir()
        (self.root / "data" / "literature_matrix.json").write_text(json.dumps({
            "schema_version": 1,
            "sources": [{"id": "x", "title": "Sample", "type": "standard", "url": "https://example.org",
                         "finding": "example", "engineering_implication": "example", "status": "test", "verified_on": "2026-10-29"}]
        }), encoding="utf-8")

    def add_good(self):
        new_skill(self.root, "test-thing", "Handle a well-defined test thing when asked to do so.")
        p = self.root / "catalog" / "skills.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(render_catalog(self.root), encoding="utf-8")
        return self.root / ".agents" / "skills" / "test-thing" / "SKILL.md"

    def test_good_scaffold_and_catalog(self):
        skill = self.add_good()
        self.assertEqual(parse_skill(skill)["name"], "test-thing")
        self.assertEqual(len(build_catalog(self.root)["skills"]), 1)
        self.assertEqual(validate(self.root), [])

    def test_reject_name_mismatch(self):
        skill = self.add_good()
        skill.write_text(skill.read_text().replace("name: test-thing", "name: other"), encoding="utf-8")
        self.assertTrue(validate(self.root))

    def test_reject_broken_relative_reference(self):
        skill = self.add_good()
        with skill.open("a", encoding="utf-8") as out:
            out.write("\n[missing](references/missing.md)\n")
        self.assertTrue(validate(self.root))

    def test_reject_catalog_drift(self):
        self.add_good()
        (self.root / "catalog" / "skills.json").write_text("{}", encoding="utf-8")
        self.assertTrue(validate(self.root))

    def test_reject_duplicate_evidence(self):
        self.add_good()
        p = self.root / "data" / "literature_matrix.json"
        records = json.loads(p.read_text(encoding="utf-8"))
        records["sources"].append(dict(records["sources"][0]))
        p.write_text(json.dumps(records), encoding="utf-8")
        self.assertTrue(validate(self.root))

    def test_reject_non_object_literature_records_without_exception(self):
        self.add_good()
        p = self.root / "data" / "literature_matrix.json"
        p.write_text(json.dumps({"schema_version": 1, "sources": [None, {"id": ["unhashable"]}]}), encoding="utf-8")
        self.assertTrue(any("literature record must be an object" in error for error in validate(self.root)))

    def test_reject_non_object_literature_matrix_without_exception(self):
        self.add_good()
        p = self.root / "data" / "literature_matrix.json"
        p.write_text(json.dumps([]), encoding="utf-8")
        self.assertTrue(any("invalid literature matrix schema" in error for error in validate(self.root)))

    def test_quoted_description_round_trip(self):
        desc = 'Process repo: narrow "task" and value.'
        new_skill(self.root, "quoted-test", desc)
        self.assertEqual(parse_skill(self.root / ".agents" / "skills" / "quoted-test" / "SKILL.md")["description"], desc)

    def test_refuse_symlink_in_skill(self):
        self.add_good()
        (self.root / ".agents" / "skills" / "test-thing" / "symlink").symlink_to(self.root / "data" / "literature_matrix.json")
        self.assertTrue(validate(self.root))

    def test_refuse_symlinked_skill_directory(self):
        skills_root = self.root / ".agents" / "skills"
        skills_root.mkdir(parents=True)
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside)
        external_skill = outside / "test-thing"
        external_skill.mkdir()
        (external_skill / "SKILL.md").write_text(
            "---\nname: test-thing\ndescription: Use this test skill for a narrowly defined task.\n---\n\n# Instructions\nProcess the supplied input.\n",
            encoding="utf-8",
        )
        (skills_root / "test-thing").symlink_to(external_skill, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symbolic links are not allowed"):
            build_catalog(self.root)

    def test_refuse_symlinked_skills_root(self):
        agents_root = self.root / ".agents"
        agents_root.mkdir()
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside)
        (outside / "test-thing").mkdir()
        (agents_root / "skills").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symbolic links are not allowed in skills root"):
            build_catalog(self.root)

    def test_refuse_symlinked_agents_parent(self):
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside)
        skills_root = outside / "skills"
        skill = skills_root / "test-thing"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: test-thing\ndescription: Use this test skill for a narrowly defined task.\n---\n\n# Instructions\nProcess the supplied input.\n",
            encoding="utf-8",
        )
        (self.root / ".agents").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symbolic links are not allowed in repository instructions"):
            build_catalog(self.root)

    def test_refuse_overwrite(self):
        self.add_good()
        with self.assertRaises(FileExistsError):
            new_skill(self.root, "test-thing", "Same description")

    def test_reject_path_traversal_name(self):
        with self.assertRaises(ValueError):
            new_skill(self.root, "../bad", "Bad")


if __name__ == "__main__":
    unittest.main()
