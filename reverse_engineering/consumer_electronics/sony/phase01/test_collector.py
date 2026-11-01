import unittest
from unittest.mock import patch
import collector

class InventoryTests(unittest.TestCase):
    def test_parse_packages(self):
        self.assertEqual(collector.parse_packages("package:com.sony.tv\npackage:com.android.tv\npackage:com.sony.tv\n"),
                         ["com.android.tv", "com.sony.tv"])

    def test_reject_shell_injection_serial(self):
        with self.assertRaises(ValueError):
            collector.collect("adb", "127.0.0.1; rm -rf /", 3)

    @patch("collector.run")
    def test_read_only_inventory(self, mock_run):
        mock_run.return_value = "package:com.example.tv"
        out = collector.collect("adb", "emulator-5554", 3)
        self.assertEqual(out["collection_mode"], "adb_read_only")
        self.assertEqual(out["observations"]["packages"], ["com.example.tv"])
        self.assertFalse(out["identity_confirmed"])
        self.assertEqual(out["errors"], {})
        for call in mock_run.call_args_list:
            self.assertIn(call.args[2][0], ("shell",))

    @patch("collector.run", side_effect=RuntimeError("redacted"))
    def test_command_failure_redacted(self, mock_run):
        out = collector.collect("adb", "emulator-5554", 3)
        self.assertEqual(out["errors"]["model"], "RuntimeError")
        self.assertNotIn("redacted", str(out))

if __name__ == "__main__":
    unittest.main()
