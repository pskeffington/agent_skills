import pathlib
import tempfile
import unittest
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from validate_skill import validate

class ValidatorTests(unittest.TestCase):
    def test_valid(self):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "example-agent"
            p.mkdir()
            (p / "SKILL.md").write_text("---\nname: example-agent\ndescription: Use to transform specific example inputs into validated outputs, excluding unrelated tasks.\n---\n\n# Procedure\nProcess input and verify output.\n")
            self.assertEqual(validate(p), [])
    def test_marker_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "example-agent"
            p.mkdir()
            (p / "SKILL.md").write_text("---\nname: example-agent\ndescription: Use to transform specific example inputs into validated outputs, excluding unrelated tasks.\n---\n{{missing}}")
            self.assertTrue(any("marker" in e for e in validate(p)))

if __name__ == "__main__":
    unittest.main()
