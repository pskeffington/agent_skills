"""Offline fixtures for local model read-only transport."""
import io
import json
import unittest
from unittest.mock import patch
from agent_toolset.local_inference import LocalInferenceClient, LocalModelError

class FakeResponse:
    status = 200
    headers = {"Content-Type": "application/json"}
    def __init__(self, data):
        self.data = io.BytesIO(json.dumps(data).encode())
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, count): return self.data.read(count)

class LocalModelTests(unittest.TestCase):
    def test_reject_unsafe_endpoints(self):
        urls = ("https://127.0.0.1:8000/v1", "http://example.com:8000/v1",
                "http://localhost:8000/v1", "http://127.0.0.1:8000/other",
                "http://127.0.0.1:8000/v1?x=1", "http://u:p@127.0.0.1:8000/v1")
        for url in urls:
            with self.subTest(url=url), self.assertRaises(LocalModelError):
                LocalInferenceClient(url, "model")

    def test_discovery_completion(self):
        client = LocalInferenceClient("http://127.0.0.1:8000/v1", "qwen")
        responses = [FakeResponse({"data": [{"id": "qwen"}]}),
                     FakeResponse({"model": "qwen", "choices": [{"finish_reason": "stop", "message": {"content": "ok"}}]})]
        with patch.object(client._opener, "open", side_effect=responses) as mocked:
            result = client.propose([{"role": "user", "content": "hello"}])
            self.assertEqual(result["content"], "ok")
            self.assertFalse(result["executed_tools"])
            self.assertEqual(json.loads(mocked.call_args.args[0].data)["tool_choice"], "none")

    def test_model_mismatch(self):
        client = LocalInferenceClient("http://127.0.0.1:8000/v1", "expected")
        with patch.object(client._opener, "open", return_value=FakeResponse({"data": [{"id": "other"}]})):
            with self.assertRaises(LocalModelError): client.discover()

    def test_reject_tool_calls(self):
        client = LocalInferenceClient("http://127.0.0.1:8000/v1", "m")
        responses = [FakeResponse({"data": [{"id": "m"}]}),
                     FakeResponse({"model": "m", "choices": [{"finish_reason": "tool_calls", "message": {"content": "", "tool_calls": [{}]}}]})]
        with patch.object(client._opener, "open", side_effect=responses):
            with self.assertRaises(LocalModelError):
                client.propose([{"role": "user", "content": "hi"}])

    def test_response_size_limit(self):
        client = LocalInferenceClient("http://127.0.0.1:8000/v1", "m", max_response_bytes=20)
        with patch.object(client._opener, "open", return_value=FakeResponse({"data": [{"id": "m"}]})):
            with self.assertRaises(LocalModelError): client.discover()

if __name__ == "__main__":
    unittest.main()
