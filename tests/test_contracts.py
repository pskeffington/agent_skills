import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_toolset.contracts import ContractError, load_contract, validate_evidence, validate_handoff, validate_task

class ContractTests(unittest.TestCase):
    def read(self, name):
        return json.loads((ROOT / "examples" / name).read_text())

    def test_valid_examples(self):
        self.assertEqual("DEV-001", validate_task(self.read("feature-task.json"))["task_id"])
        self.assertEqual("READY", validate_handoff(self.read("feature-handoff.json"))["status"])
        self.assertEqual("BLOCKED", validate_evidence(self.read("feature-evidence.json"))["result"])

    def test_malformed_and_unknown_fields_rejected(self):
        task = self.read("feature-task.json")
        task["risk"] = None
        with self.assertRaises(ContractError):
            validate_task(task)
        task = self.read("feature-task.json")
        task["surprise"] = True
        with self.assertRaises(ContractError):
            validate_task(task)

    def test_dangerous_paths_rejected(self):
        for path in ("../secret", "/etc/passwd", "~/file", "C:/secret", "a\\..\\secret", "src/../secret"):
            task = self.read("feature-task.json")
            task["scope"]["include"] = [path]
            with self.subTest(path=path), self.assertRaises(ContractError):
                validate_task(task)

    def test_role_and_json_file_validation(self):
        task = self.read("feature-task.json")
        with self.assertRaises(ContractError):
            validate_task(task, roles={"verifier"})
        self.assertEqual("DEV-001", load_contract(ROOT / "examples/feature-task.json", "task")["task_id"])
