"""Offline fixtures for local model read-only transport."""
import io
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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
                "http://127.0.0.1:8000/v1?x=1", "http://u:p@127.0.0.1:8000/v1",
                "http://127.0.0.1:99999/v1", "http://[broken/v1")
        for url in urls:
            with self.subTest(url=url), self.assertRaises(LocalModelError):
                LocalInferenceClient(url, "model")

    def test_discovery_completion(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", "24")
                self.end_headers()
                self.wfile.write(b'{"data":[{"id":"qwen"}]}')
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                self.assertions.append(body)
                self.send_response(200)
                body = b'{"model":"qwen","choices":[{"finish_reason":"stop","message":{"content":"ok"}}]}'
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            assertions = []
            def log_message(self, *_args): pass

        server = self._serve(Handler)
        address, port = server.server_address
        client = LocalInferenceClient(f"http://{address}:{port}/v1", "qwen")
        result = client.propose([{"role": "user", "content": "hello"}])
        self.assertEqual(result["content"], "ok")
        self.assertFalse(result["executed_tools"])
        self.assertEqual(Handler.assertions[0]["tool_choice"], "none")

    def test_model_mismatch(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", "25")
                self.end_headers()
                self.wfile.write(b'{"data":[{"id":"other"}]}')
            def log_message(self, *_args): pass
        server = self._serve(Handler)
        address, port = server.server_address
        client = LocalInferenceClient(f"http://{address}:{port}/v1", "expected")
        with self.assertRaises(LocalModelError): client.discover()

    def test_reject_tool_calls(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", "21")
                self.end_headers()
                self.wfile.write(b'{"data":[{"id":"m"}]}')
            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                self.send_response(200)
                body = b'{"model":"m","choices":[{"finish_reason":"tool_calls","message":{"content":"","tool_calls":[{}]}}]}'
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            def log_message(self, *_args): pass
        server = self._serve(Handler)
        address, port = server.server_address
        client = LocalInferenceClient(f"http://{address}:{port}/v1", "m")
        with self.assertRaises(LocalModelError): client.propose([{"role": "user", "content": "hi"}])

    def test_response_size_limit(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", "21")
                self.end_headers()
                self.wfile.write(b'{"data":[{"id":"m"}]}')
            def log_message(self, *_args): pass
        server = self._serve(Handler)
        address, port = server.server_address
        client = LocalInferenceClient(f"http://{address}:{port}/v1", "m", max_response_bytes=20)
        with self.assertRaises(LocalModelError): client.discover()

    def _serve(self, handler):
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.addCleanup(thread.join, 2)
        return server

    def test_proxy_environment_is_ignored(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", "21")
                self.end_headers()
                self.wfile.write(b'{"data":[{"id":"m"}]}')
            def log_message(self, *_args): pass

        server = self._serve(Handler)
        address, port = server.server_address
        env = {"http_proxy": "http://127.0.0.1:1", "HTTP_PROXY": "http://127.0.0.1:1",
               "no_proxy": "", "NO_PROXY": ""}
        with patch.dict(os.environ, env):
            client = LocalInferenceClient(f"http://{address}:{port}/v1", "m")
            self.assertTrue(client.discover()["verified"])

    def test_rejects_malformed_status_and_length_framing(self):
        responses = (b"NOTHTTP 200 OK\r\nContent-Type: application/json\r\nContent-Length: 21\r\n\r\n{\"data\":[{\"id\":\"m\"}]}",
                     b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 999\r\n\r\n{\"data\":[{\"id\":\"m\"}]}",
                     b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 999\r\n\r\n",
                     b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 21\r\nContent-Length: 21\r\n\r\n{\"data\":[{\"id\":\"m\"}]}",
                     b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 21\r\nContent-Length: 999\r\n\r\n{\"data\":[{\"id\":\"m\"}]}",
                     b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: +21\r\n\r\n{\"data\":[{\"id\":\"m\"}]}",
                     b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + b"9" * 5000 + b"\r\n\r\n")
        for response in responses:
            with self.subTest(response=response[:20]):
                class RawHandler(BaseHTTPRequestHandler):
                    def do_GET(self):
                        self.connection.sendall(response)
                    def log_message(self, *_args): pass
                server = self._serve(RawHandler)
                address, port = server.server_address
                client = LocalInferenceClient(f"http://{address}:{port}/v1", "m", timeout=0.5)
                with self.assertRaises(LocalModelError): client.discover()

    def test_accepts_leading_zero_content_length(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body = b'{"data":[{"id":"m"}]}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", "000" + str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            def log_message(self, *_args): pass
        server = self._serve(Handler)
        address, port = server.server_address
        client = LocalInferenceClient(f"http://{address}:{port}/v1", "m")
        self.assertTrue(client.discover()["verified"])

    def test_slow_trickle_headers_cannot_extend_total_deadline(self):
        class SlowHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                try:
                    for byte in b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 21\r\n\r\n":
                        self.wfile.write(bytes([byte]))
                        self.wfile.flush()
                        time.sleep(0.01)
                    self.wfile.write(b'{"data":[{"id":"m"}]}')
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    pass
            def log_message(self, *_args): pass

        server = self._serve(SlowHandler)
        address, port = server.server_address
        client = LocalInferenceClient(f"http://{address}:{port}/v1", "m", timeout=0.12)
        started = time.monotonic()
        with self.assertRaises(LocalModelError):
            client.discover()
        self.assertLess(time.monotonic() - started, 0.6)

    def test_redirect_is_rejected_before_following_target(self):
        followed = []
        class TargetHandler(BaseHTTPRequestHandler):
            def do_GET(self): followed.append(self.path)
            def log_message(self, *_args): pass
        target = self._serve(TargetHandler)
        target_address, target_port = target.server_address

        class RedirectHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header("Location", f"http://{target_address}:{target_port}/v1/models")
                self.end_headers()
            def log_message(self, *_args): pass
        redirect = self._serve(RedirectHandler)
        address, port = redirect.server_address
        client = LocalInferenceClient(f"http://{address}:{port}/v1", "m")
        with self.assertRaises(LocalModelError):
            client.discover()
        self.assertEqual(followed, [])

if __name__ == "__main__":
    unittest.main()
