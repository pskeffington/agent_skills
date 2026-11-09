"""Tests for deterministic packaging of canonical skills."""
import pathlib
import os
import tempfile
import unittest
import zipfile
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_skill import MAX_SKILL_FILES, _archive_member, _validate_member_collisions, package_skill


class PackageSkillTests(unittest.TestCase):
    def _root(self, base):
        root = pathlib.Path(base) / "repo"
        skill = root / ".agents" / "skills" / "example-skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: example-skill\ndescription: Use for one defined example workflow and reject unrelated requests.\n---\n\nInspect the input and verify the result.\n",
            encoding="utf-8",
        )
        (skill / "agents").mkdir()
        (skill / "agents" / "openai.yaml").write_text("interface:\n  display_name: Example\n", encoding="utf-8")
        (root / "catalog").mkdir()
        (root / "catalog" / "skills.json").write_text("{}\n", encoding="utf-8")
        return root

    def test_deterministic_and_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            out = pathlib.Path(tmp) / "one.zip"
            package_skill(root, "example-skill", out)
            first = out.read_bytes()
            out.unlink()
            package_skill(root, "example-skill", out)
            self.assertEqual(first, out.read_bytes())
            with zipfile.ZipFile(out) as archive:
                self.assertEqual(archive.namelist(), [
                    "example-skill/SKILL.md", "example-skill/agents/openai.yaml"])

    def test_refuses_existing_output_and_repo_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            out = pathlib.Path(tmp) / "exists.zip"
            out.write_bytes(b"keep")
            with self.assertRaises(FileExistsError):
                package_skill(root, "example-skill", out)
            with self.assertRaises(ValueError):
                package_skill(root, "example-skill", root / "skill.zip")
            self.assertEqual(out.read_bytes(), b"keep")

    def test_rejects_backslash_traversal_archive_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            skill = root / ".agents" / "skills" / "example-skill"
            (skill / "..\\..\\escape.txt").write_text("outside", encoding="utf-8")
            with self.assertRaises(ValueError):
                package_skill(root, "example-skill", pathlib.Path(tmp) / "out.zip")

    def test_rejects_windows_device_names(self):
        for name in ("CON", "CONIN$", "CONOUT$", "COM1", "COM¹", "COM²", "COM³",
                     "LPT1", "LPT¹", "LPT²", "LPT³"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                _archive_member("example-skill", pathlib.Path(name))

    def test_rejects_windows_forbidden_characters(self):
        for char in '<>"|?*':
            with self.subTest(char=char), self.assertRaises(ValueError):
                _archive_member("example-skill", pathlib.Path(f"bad{char}.md"))

    def test_rejects_file_count_over_limit_during_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            skill = root / ".agents" / "skills" / "example-skill"
            for index in range(MAX_SKILL_FILES):
                (skill / f"extra-{index:04}.txt").touch()
            with self.assertRaisesRegex(ValueError, "too many entries"):
                package_skill(root, "example-skill", pathlib.Path(tmp) / "out.zip")

    def test_rejects_case_colliding_archive_paths(self):
        with self.assertRaises(ValueError):
            _validate_member_collisions(["example-skill/Guide.md", "example-skill/guide.md"])

    def test_rejects_skill_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(tmp)
            skill = root / ".agents" / "skills" / "example-skill"
            external = pathlib.Path(tmp) / "external.txt"
            external.write_text("outside", encoding="utf-8")
            (skill / "external.txt").symlink_to(external)
            with self.assertRaises(ValueError):
                package_skill(root, "example-skill", pathlib.Path(tmp) / "out.zip")

    @unittest.skipUnless(os.name == "posix", "secure descriptor-relative packaging is POSIX-only")
    def test_rejects_symlinked_canonical_ancestor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            root.mkdir()
            outside = pathlib.Path(tmp) / "outside"
            (outside / "example-skill").mkdir(parents=True)
            (outside / "example-skill" / "SKILL.md").write_text(
                "---\nname: example-skill\ndescription: Use for one defined example workflow and reject unrelated requests.\n---\n\nInspect the input and verify the result.\n",
                encoding="utf-8",
            )
            (root / ".agents").mkdir()
            (root / ".agents" / "skills").symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "canonical ancestors"):
                package_skill(root, "example-skill", pathlib.Path(tmp) / "out.zip")


if __name__ == "__main__":
    unittest.main()
