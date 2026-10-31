"""Bounded read-only HTTP transport for local OpenAI-compatible model servers."""
from __future__ import annotations
import ipaddress
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

class LocalModelError(ValueError):
    """Local transport or protocol validation failure."""

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise LocalModelError("redirect forbidden")

class LocalInferenceClient:
    """No tools, cloud fallback, DNS, credential inheritance or model downloads."""
    def __init__(self, base_url: str, model_id: str, *, timeout: float = 10.0, max_response_bytes: int = 1048576):
        p = urllib.parse.urlsplit(base_url)
        if p.scheme != "http" or not p.hostname or p.username or p.password or p.query or p.fragment or p.path.rstrip("/") != "/v1":
            raise LocalModelError("expected plain loopback HTTP /v1 endpoint")
        try:
            address = ipaddress.ip_address(p.hostname)
        except ValueError as exc:
            raise LocalModelError("numeric loopback IP required; DNS forbidden") from exc
        if not address.is_loopback or p.port is None:
            raise LocalModelError("explicit loopback address and port required")
        if not isinstance(model_id, str) or not model_id.strip() or len(model_id) > 256:
            raise LocalModelError("exact model ID required")
        if not 0 < timeout <= 120 or not 0 < max_response_bytes <= 8388608:
            raise LocalModelError("invalid resource limit")
        self.base_url = base_url.rstrip("/")
        self.model_id = model_id
        self.timeout = timeout
        self.max_response_bytes = max_response_bytes
        self._opener = urllib.request.build_opener(_NoRedirect(), urllib.request.ProxyHandler({}))

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(self.base_url + path, data=data, headers=headers, method=method)
        try:
            with self._opener.open(req, timeout=self.timeout) as resp:
                if resp.status != 200 or "application/json" not in resp.headers.get("Content-Type", ""):
                    raise LocalModelError("invalid HTTP response")
                raw = resp.read(self.max_response_bytes + 1)
                if len(raw) > self.max_response_bytes:
                    raise LocalModelError("response size limit exceeded")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise LocalModelError("local endpoint unavailable: " + type(exc).__name__) from exc
        try:
            result = json.loads(raw)
        except (ValueError, UnicodeDecodeError) as exc:
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
