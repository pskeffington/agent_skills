#!/usr/bin/env python3
"""Smoke tests for the offline RE intake harness."""
import importlib.util
import json
import pathlib
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "re_suite.py"
spec = importlib.util.spec_from_file_location("re_suite", SCRIPT)
suite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(suite)

class TestSuite(unittest.TestCase):
    def test_intake_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            fw = root / "example.bin"
            fw.write_bytes(b"example firmware")
            out = root / "manifest.json"
            record = suite.intake(fw, out)
            self.assertEqual(len(record["sha256"]), 64)
            self.assertFalse(record["flash_authorized"])
            self.assertEqual(json.loads(out.read_text())["size_bytes"], 16)
            with self.assertRaises(FileExistsError):
                suite.intake(fw, out)
    def test_manifest(self):
        manifest = HERE.parent / "references" / "tool-suite.json"
        self.assertGreaterEqual(suite.validate_manifest(manifest), 10)
if __name__ == "__main__":
    unittest.main()
