import pathlib
import tempfile
import unittest
import sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from create_skill import scaffold
from validate_skill import validate

class GeneratorTests(unittest.TestCase):
    def test_scaffold_and_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp) / "example-agent"
            scaffold("example-agent", "Use for converting example inputs into validated outputs; exclude unrelated requests.", folder)
            self.assertTrue((folder / "agents" / "openai.yaml").exists())
            self.assertEqual(validate(folder), [])
            with self.assertRaises(FileExistsError):
                scaffold("example-agent", "Use for converting example inputs into validated outputs; exclude unrelated requests.", folder)
    def test_reject_bad_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                scaffold("Invalid_Name", "Use for converting example inputs into validated outputs; exclude unrelated requests.", pathlib.Path(tmp) / "Invalid_Name")
if __name__ == "__main__":
    unittest.main()
