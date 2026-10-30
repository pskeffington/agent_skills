import pathlib
import sys
import tempfile
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agent_toolset.contracts import ContractError
from agent_toolset.inventory import confined_path, inventory, read_file
from agent_toolset.test_executor import TestExecutor

class ToolboxTests(unittest.TestCase):
    def test_inventory_and_confined_read(self):
        result=inventory(ROOT)
        self.assertIn("AGENTS.md", result["instructions"])
        self.assertIn("tests/test_toolbox.py", result["tests"])
        self.assertIn("agent_toolset/contracts.py", result["files"])
        self.assertIn("Repository instructions", read_file(ROOT,"AGENTS.md"))

    def test_traversal_and_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root=pathlib.Path(tmp)
            (root/"link").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ContractError): confined_path(root,"../etc/passwd")
            with self.assertRaises(ContractError): confined_path(root,"link/secret")

    def test_executor_allowlist_shell_injection_and_timeout(self):
        with self.assertRaises(ValueError): TestExecutor(ROOT).run("python-unittest", args=["; touch /tmp/no"])
        with self.assertRaises(ValueError): TestExecutor(ROOT).run("unknown")
        result=TestExecutor(ROOT,timeout=30).run("validate")
        self.assertEqual("PASS",result.outcome)
        self.assertEqual(0,result.exit_code)

    def test_invalid_cwd_rejected(self):
        with self.assertRaises(ContractError): TestExecutor(ROOT).run("validate",cwd="../")

if __name__=="__main__": unittest.main()
