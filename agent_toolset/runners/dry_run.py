"""Side-effect-free runner that records the requested task without executing it."""
from __future__ import annotations
import hashlib
import json
from typing import Any
from .base import RunnerResult

class DryRunRunner:
    name = "dry-run"
    def prepare(self, task: dict[str, Any], capabilities: dict[str, Any]) -> RunnerResult:
        task_hash = hashlib.sha256(json.dumps(task, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return RunnerResult("PASS", "dry:" + task_hash[:16], self.name, 0, {"task_sha256": task_hash, "capabilities": sorted(capabilities)}, "Task accepted for dry run; no tools were executed.")
    def execute(self, task: dict[str, Any], sandbox: dict[str, Any]) -> RunnerResult:
        prepared = self.prepare(task, sandbox.get("capabilities", {}))
        return RunnerResult("BLOCKED", prepared.run_id, self.name, None, prepared.provenance, "Dry-run mode never executes agent work.")
    def cancel(self, run_id: str) -> RunnerResult:
        return RunnerResult("PASS", run_id, self.name, 0, {}, "No running process exists in dry-run mode.")
