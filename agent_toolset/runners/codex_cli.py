"""Opt-in Codex CLI capability probe. Never launches task execution."""
from __future__ import annotations
import os
import re
import shutil
import subprocess
from typing import Any
from .base import RunnerResult

_VERSION = re.compile(r"codex-cli\s+(\d+)\.(\d+)\.(\d+)")

class CodexCLIAdapter:
    def __init__(self, *, enabled: bool = False, minimum_version: tuple[int, int, int] = (0, 1, 0)):
        self.enabled = enabled
        self.minimum_version = minimum_version
    def probe(self) -> dict[str, Any]:
        binary = shutil.which("codex") if self.enabled else None
        if not self.enabled:
            return {"available": False, "status": "BLOCKED", "reason": "Codex CLI adapter is not enabled"}
        if not binary:
            return {"available": False, "status": "BLOCKED", "reason": "codex executable not found"}
        try:
            result = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=5, shell=False, env={"PATH": os.defpath, "LANG": "C.UTF-8"})
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"available": False, "status": "BLOCKED", "reason": f"version probe failed: {exc}"}
        match = _VERSION.search(result.stdout + result.stderr)
        if result.returncode != 0 or not match:
            return {"available": False, "status": "BLOCKED", "reason": "unrecognized Codex CLI version response"}
        version = tuple(int(v) for v in match.groups())
        if version < self.minimum_version:
            return {"available": False, "status": "BLOCKED", "reason": "Codex CLI version is below configured minimum", "version": version}
        return {"available": True, "status": "PASS", "binary": binary, "version": version, "execution_enabled": False}
    def prepare(self, task: dict[str, Any], capabilities: dict[str, Any]) -> RunnerResult:
        probe = self.probe()
        status = "PASS" if probe["available"] else "BLOCKED"
        return RunnerResult(status, "codex-probe", "codex-cli", 0 if status == "PASS" else None, probe, "Capability probe only; task execution is not implemented.")
    def execute(self, task: dict[str, Any], sandbox: dict[str, Any]) -> RunnerResult:
        probe = self.probe()
        return RunnerResult("BLOCKED", "codex-execution-disabled", "codex-cli", None, probe, "Real task execution is disabled until permission and sandbox integration is implemented and verified.")
    def cancel(self, run_id: str) -> RunnerResult:
        return RunnerResult("BLOCKED", run_id, "codex-cli", None, {}, "No Codex process was started by this adapter.")
