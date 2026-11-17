"""Regression tests for RF master operator graph integrity."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_rf_operator", ROOT / "scripts/validate_rf_operator.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

class RFOperatorTests(unittest.TestCase):
    def test_catalog_integrity(self):
        self.assertEqual(MOD.check(ROOT), [])
    def test_number_of_specialists(self):
        import json
        catalog = json.loads((ROOT / "catalog/rf-software-master-operator.json").read_text())
        self.assertEqual(len(catalog["agents"]), 9)
        self.assertEqual(len(catalog["components"]), 15)
    def test_no_automatic_transmit_permission(self):
        import json
        catalog = json.loads((ROOT / "catalog/rf-software-master-operator.json").read_text())
        self.assertEqual(catalog["policy"]["default_radio_mode"], "rx_only")
        self.assertIn("radio-tx", catalog["operator"]["human_approval"])

if __name__ == "__main__":
    unittest.main()
