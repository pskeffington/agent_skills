import pathlib
import tempfile
import unittest
import zipfile
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from package_skill import package_skill

class PackageTests(unittest.TestCase):
    def test_package_deterministic_and_complete(self):
        with tempfile.TemporaryDirectory() as root:
            root = pathlib.Path(root)
            folder = root / "example-agent"
            folder.mkdir()
            (folder / "SKILL.md").write_text("---\nname: example-agent\ndescription: Use for converting example inputs into validated outputs; exclude unrelated requests.\n---\n\nPerform the conversion and verify results.\n")
            output = root / "skill.zip"
            package_skill(folder, output)
            first = output.read_bytes()
            package_skill(folder, output)
            self.assertEqual(first, output.read_bytes())
            with zipfile.ZipFile(output) as z:
                self.assertIn("example-agent/SKILL.md", z.namelist())
    def test_reject_invalid_skill(self):
        with tempfile.TemporaryDirectory() as root:
            folder = pathlib.Path(root) / "broken"
            folder.mkdir()
            with self.assertRaises(ValueError):
                package_skill(folder, pathlib.Path(root) / "skill.zip")
if __name__ == "__main__":
    unittest.main()
