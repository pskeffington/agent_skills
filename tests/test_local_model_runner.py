"""Offline runner-contract tests: no real local model required."""
import json
import unittest

from agent_toolset.local_inference import LocalModelError
from agent_toolset.runners.local_model import LocalModelProposalRunner


def task():
    return {
        "schema_version": "1.0.0",
        "task_id": "LM-TEST-01",
        "repository": "example/repo",
        "base_commit": "a" * 40,
        "objective": "Propose a bounded implementation plan.",
        "scope": {"include": ["src/example.py"], "exclude": []},
        "acceptance": ["tests pass locally"],
        "risk": "low",
        "owner_role": "implementer",
        "status": "ready",
    }


class FakeClient:
    model_id = "local-model"
    def __init__(self, content=None, truncated=False):
        self.content = content if content is not None else json.dumps({
            "summary": "Plan only", "steps": ["Review source"], "risks": []})
        self.truncated = truncated
        self.calls = 0

    def propose(self, messages, *, max_tokens):
        self.calls += 1
        return {"model_id": self.model_id, "content": self.content,
                "truncated": self.truncated, "executed_tools": False}


class RunnerTests(unittest.TestCase):
    def test_success_is_untrusted_proposal_not_execution(self):
        client = FakeClient()
        result = LocalModelProposalRunner(client).execute(task(), {})
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.provenance["proposal"]["summary"], "Plan only")
        self.assertFalse(result.provenance["tools_executed"])
        self.assertEqual(client.calls, 1)

    def test_invalid_task_never_calls_model(self):
        client = FakeClient()
        item = task()
        item["base_commit"] = "bad"
        result = LocalModelProposalRunner(client).execute(item, {})
        self.assertEqual(result.status, "BLOCKED")
        self.assertEqual(client.calls, 0)

    def test_deny_write_and_tool_requests(self):
        client = FakeClient()
        for key in ("allow_tools", "allow_writes"):
            self.assertEqual(LocalModelProposalRunner(client).execute(task(), {key: True}).status, "BLOCKED")
        self.assertEqual(client.calls, 0)

    def test_reject_malformed_output(self):
        for content in ('not json', '{"summary":"x","steps":[],"risks":[]}',
                        '{"summary":"ok","steps":["x"],"risks":[],"tool":"run"}'):
            result = LocalModelProposalRunner(FakeClient(content)).execute(task(), {})
            self.assertEqual(result.status, "BLOCKED")

    def test_reject_truncation_and_high_risk(self):
        self.assertEqual(LocalModelProposalRunner(FakeClient(truncated=True)).execute(task(), {}).status, "BLOCKED")
        client = FakeClient()
        item = task()
        item["risk"] = "critical"
        self.assertEqual(LocalModelProposalRunner(client).execute(item, {}).status, "BLOCKED")
        self.assertEqual(client.calls, 0)

    def test_cancel_is_not_false_success(self):
        result = LocalModelProposalRunner(FakeClient()).cancel("run-1")
        self.assertEqual(result.status, "BLOCKED")


if __name__ == "__main__":
    unittest.main()
