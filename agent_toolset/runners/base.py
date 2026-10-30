"""Typed runner contracts and capability model."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol

@dataclass(frozen=True)
class RunnerResult:
    status: str
    run_id: str
    runner: str
    exit_code: int | None
    provenance: dict[str, Any]
    message: str

class AgentRunner(Protocol):
    def prepare(self, task: dict[str, Any], capabilities: dict[str, Any]) -> RunnerResult: ...
    def execute(self, task: dict[str, Any], sandbox: dict[str, Any]) -> RunnerResult: ...
    def cancel(self, run_id: str) -> RunnerResult: ...
