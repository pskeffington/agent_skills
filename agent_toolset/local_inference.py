"""Bounded read-only HTTP transport for local OpenAI-compatible model servers."""
from __future__ import annotations
import ipaddress
import json
import math
import http.client
import io
import socket
import time
import urllib.parse
from typing import Any

class LocalModelError(ValueError):
    """Local transport or protocol validation failure."""

class LocalInferenceClient:
    """No tools, cloud fallback, DNS, credential inheritance or model downloads."""
    def __init__(self, base_url: str, model_id: str, *, timeout: float = 10.0, max_response_bytes: int = 1048576):
        if not isinstance(base_url, str):
            raise LocalModelError("expected plain loopback HTTP /v1 endpoint")
        try:
            p = urllib.parse.urlsplit(base_url)
            hostname = p.hostname
            port = p.port
        except ValueError as exc:
            raise LocalModelError("invalid endpoint URL") from exc
        if p.scheme != "http" or not hostname or p.username or p.password or p.query or p.fragment or p.path not in ("/v1", "/v1/"):
            raise LocalModelError("expected plain loopback HTTP /v1 endpoint")
        if "%" in hostname:
            raise LocalModelError("scoped or escaped address forbidden")
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError as exc:
            raise LocalModelError("numeric loopback IP required; DNS forbidden") from exc
        if not address.is_loopback or port is None or not 1 <= port <= 65535:
            raise LocalModelError("explicit loopback address and port required")
        if not isinstance(model_id, str) or not model_id.strip() or model_id != model_id.strip() or len(model_id) > 256:
            raise LocalModelError("exact model ID required")
        if (not isinstance(timeout, (int, float)) or isinstance(timeout, bool)
                or not 0 < timeout <= 120 or not math.isfinite(timeout)
                or not isinstance(max_response_bytes, int) or isinstance(max_response_bytes, bool)
                or not 0 < max_response_bytes <= 8388608):
            raise LocalModelError("invalid resource limit")
        self.base_url = base_url.rstrip("/")
        self._host = hostname
        self._port = port
        self.model_id = model_id
        self.timeout = timeout
        self.max_response_bytes = max_response_bytes

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers = {"Accept": "application/json", "Connection": "close"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        deadline = time.monotonic() + self.timeout
        conn = http.client.HTTPConnection(self._host, self._port, timeout=self.timeout)
        try:
            conn.connect()
            if conn.sock is None:
                raise LocalModelError("local endpoint unavailable")
            conn.sock.settimeout(max(0.001, deadline - time.monotonic()))
            conn.putrequest(method, "/v1" + path)
            for name, value in headers.items():
                conn.putheader(name, value)
            if data is not None:
                conn.putheader("Content-Length", str(len(data)))
            conn.endheaders(data)

            # Parse bounded header lines directly so a trickling header cannot
            # extend the caller's total deadline via http.client's buffered read.
            header_data = bytearray()
            while not header_data.endswith(b"\r\n\r\n") and not header_data.endswith(b"\n\n"):
                budget = deadline - time.monotonic()
                if budget <= 0:
                    raise LocalModelError("total response deadline exceeded")
                conn.sock.settimeout(budget)
                part = conn.sock.recv(1)
                if time.monotonic() >= deadline:
                    raise LocalModelError("total response deadline exceeded")
                if not part or len(header_data) >= 32768:
                    raise LocalModelError("invalid or oversized HTTP headers")
                header_data.extend(part)
            header_lines = header_data.replace(b"\r\n", b"\n").split(b"\n")[:-2]
            try:
                status_line = header_lines.pop(0).decode("ascii").rstrip("\r").split(" ", 2)
                if (len(status_line) < 2 or status_line[0] not in ("HTTP/1.0", "HTTP/1.1")
                        or len(status_line[1]) != 3 or not status_line[1].isdigit()):
                    raise LocalModelError("invalid HTTP status line")
                status = int(status_line[1])
                response_headers = http.client.parse_headers(io.BytesIO(b"\n".join(header_lines) + b"\n\n"))
            except (ValueError, IndexError, UnicodeDecodeError, http.client.HTTPException) as exc:
                raise LocalModelError("invalid HTTP response headers") from exc
            if 300 <= status < 400:
                raise LocalModelError("redirect forbidden")
            if status != 200 or "application/json" not in response_headers.get("Content-Type", "").lower():
                raise LocalModelError("invalid HTTP response")
            length_values = response_headers.get_all("Content-Length", [])
            if len(length_values) != 1:
                raise LocalModelError("exactly one content length required")
            content_length = length_values[0]
            if response_headers.get_all("Transfer-Encoding", []):
                raise LocalModelError("unsupported transfer encoding")
            if response_headers.get("Transfer-Encoding", "").lower() not in ("", "identity"):
                raise LocalModelError("unsupported transfer encoding")
            if content_length is None:
                raise LocalModelError("content length required")
            if not content_length.isascii() or not content_length.isdigit():
                raise LocalModelError("invalid response length")
            normalized_length = content_length.lstrip("0") or "0"
            if len(normalized_length) > len(str(self.max_response_bytes)):
                raise LocalModelError("response size limit exceeded")
            declared_size = int(normalized_length)
            if declared_size > self.max_response_bytes:
                raise LocalModelError("response size limit exceeded")
            remaining = declared_size
            chunks = []
            while remaining:
                budget = deadline - time.monotonic()
                if budget <= 0:
                    raise LocalModelError("total response deadline exceeded")
                conn.sock.settimeout(budget)
                chunk = conn.sock.recv(min(65536, remaining))
                if time.monotonic() >= deadline:
                    raise LocalModelError("total response deadline exceeded")
                if not chunk:
                    raise LocalModelError("truncated HTTP response body")
                chunks.append(chunk)
                remaining -= len(chunk)
            raw = b"".join(chunks)
            if len(raw) > self.max_response_bytes:
                raise LocalModelError("response size limit exceeded")
        except LocalModelError:
            raise
        except (TimeoutError, socket.timeout, OSError, http.client.HTTPException) as exc:
            if time.monotonic() >= deadline:
                raise LocalModelError("total response deadline exceeded") from exc
            raise LocalModelError("local endpoint unavailable: " + type(exc).__name__) from exc
        finally:
            conn.close()
        try:
            result = json.loads(raw)
        except (ValueError, UnicodeDecodeError, RecursionError) as exc:
            raise LocalModelError("invalid JSON") from exc
        if not isinstance(result, dict):
            raise LocalModelError("expected JSON object")
        return result

    def discover(self) -> dict[str, Any]:
        response = self._request("GET", "/models")
        models = response.get("data")
        if not isinstance(models, list) or not all(isinstance(m, dict) and isinstance(m.get("id"), str) for m in models):
            raise LocalModelError("malformed model inventory")
        ids = [m["id"] for m in models]
        if self.model_id not in ids:
            raise LocalModelError("configured model not advertised")
        return {"model_id": self.model_id, "available_models": ids, "verified": True}

    def propose(self, messages: list[dict[str, str]], *, max_tokens: int = 512) -> dict[str, Any]:
        if not isinstance(max_tokens, int) or isinstance(max_tokens, bool) or not 1 <= max_tokens <= 4096:
            raise LocalModelError("invalid token budget")
        if not isinstance(messages, list) or not 1 <= len(messages) <= 32:
            raise LocalModelError("invalid message count")
        if any(not isinstance(m, dict) or set(m) != {"role", "content"} or m["role"] not in ("system", "user", "assistant") or not isinstance(m["content"], str) or len(m["content"]) > 16384 for m in messages):
            raise LocalModelError("unsupported messages")
        self.discover()
        response = self._request("POST", "/chat/completions", {"model": self.model_id, "messages": messages, "stream": False, "temperature": 0, "max_tokens": max_tokens, "tool_choice": "none"})
        if response.get("model") != self.model_id:
            raise LocalModelError("model identity mismatch")
        choices = response.get("choices")
        if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
            raise LocalModelError("invalid completion choices")
        message = choices[0].get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str) or message.get("tool_calls"):
            raise LocalModelError("invalid content or tool call")
        if choices[0].get("finish_reason") not in ("stop", "length"):
            raise LocalModelError("unsupported finish reason")
        return {"model_id": self.model_id, "content": message["content"], "truncated": choices[0]["finish_reason"] == "length", "executed_tools": False}
