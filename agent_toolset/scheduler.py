"""Deterministic task DAG scheduling, state transitions, leases, and retries."""
from __future__ import annotations

import hashlib
import json
import pathlib
import time
from typing import Any, Iterable

from .contracts import ContractError, validate_task
from .journal import Journal

TERMINAL = {"done", "failed", "cancelled"}
TRANSITIONS = {
    "queued": {"ready", "blocked", "cancelled"},
    "ready": {"running", "blocked", "cancelled"},
    "running": {"review", "blocked", "failed", "cancelled"},
    "review": {"done", "ready", "blocked", "failed"},
    "blocked": {"ready", "cancelled"},
    "failed": set(),
    "done": set(),
    "cancelled": set(),
}


class ScheduleError(ValueError):
    """The task graph or requested transition is invalid."""


class Scheduler:
    def __init__(self, journal: Journal, *, lease_seconds: int = 300, max_retries: int = 3):
        if lease_seconds <= 0 or max_retries < 0:
            raise ValueError("lease_seconds must be positive and max_retries non-negative")
        self.journal = journal
        self.lease_seconds = lease_seconds
        self.max_retries = max_retries

    def _state(self) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        tasks: dict[str, dict[str, Any]] = {}
        leases: dict[str, dict[str, Any]] = {}
        for event in self.journal.replay():
            typ, payload, task_id = event["event_type"], event["payload"], event["task_id"]
            if typ == "TASK_CREATED":
                tasks[task_id] = payload["task"]
            elif typ == "TASK_STATE":
                tasks[task_id] = {**tasks[task_id], "status": payload["status"], "blocker": payload.get("blocker")}
            elif typ == "LEASE_ACQUIRED":
                leases[task_id] = payload
            elif typ in {"LEASE_RELEASED", "TASK_CANCELLED"}:
                leases.pop(task_id, None)
        return tasks, leases

    def add_tasks(self, contracts: Iterable[dict[str, Any]], *, roles: set[str] | None = None) -> list[str]:
        tasks, _ = self._state()
        proposed = dict(tasks)
        added: list[str] = []
        for raw in contracts:
            task = validate_task(raw, roles=roles)
            task_id = task["task_id"]
            if task_id in proposed:
                raise ScheduleError(f"duplicate task_id: {task_id}")
            proposed[task_id] = task
            added.append(task_id)
        self._validate_graph(proposed)
        for task_id in added:
            task = proposed[task_id]
            self.journal.append(task_id, "TASK_CREATED", {"task": task})
        return added

    @staticmethod
    def _validate_graph(tasks: dict[str, dict[str, Any]]) -> None:
        for task_id, task in tasks.items():
            for dependency in task.get("depends_on", []):
                if dependency not in tasks:
                    raise ScheduleError(f"{task_id} depends on unknown task {dependency}")
        visiting: set[str] = set()
        visited: set[str] = set()
        def visit(node: str) -> None:
            if node in visiting:
                raise ScheduleError(f"dependency cycle at {node}")
            if node in visited:
                return
            visiting.add(node)
            for dep in tasks[node].get("depends_on", []):
                visit(dep)
            visiting.remove(node)
            visited.add(node)
        for node in tasks:
            visit(node)

    def plan(self) -> list[str]:
        tasks, _ = self._state()
        self._validate_graph(tasks)
        ready = [tid for tid, task in tasks.items() if task["status"] in {"queued", "ready"} and all(tasks[d]["status"] == "done" for d in task.get("depends_on", []))]
        return sorted(ready)

    def status(self) -> dict[str, Any]:
        tasks, leases = self._state()
        return {"tasks": tasks, "leases": leases, "ready": self.plan()}

    def transition(self, task_id: str, new_status: str, *, blocker: str | None = None) -> None:
        tasks, _ = self._state()
        if task_id not in tasks:
            raise ScheduleError(f"unknown task: {task_id}")
        current = tasks[task_id]["status"]
        if new_status not in TRANSITIONS.get(current, set()):
            raise ScheduleError(f"invalid transition {current} -> {new_status}")
        if new_status == "ready" and any(tasks[d]["status"] != "done" for d in tasks[task_id].get("depends_on", [])):
            raise ScheduleError("task dependencies are not complete")
        if new_status == "blocked" and not blocker:
            raise ScheduleError("blocked transition requires a documented blocker")
        if new_status != "blocked" and blocker is not None:
            raise ScheduleError("blocker is only valid for blocked status")
        self.journal.append(task_id, "TASK_STATE", {"status": new_status, "blocker": blocker})

    def acquire(self, task_id: str, owner: str, *, now: float | None = None, worktree: str = "") -> dict[str, Any]:
        now = time.time() if now is None else now
        if not owner.strip():
            raise ScheduleError("lease owner must be non-empty")
        tasks, leases = self._state()
        if task_id not in tasks or any(tasks[d]["status"] != "done" for d in tasks[task_id].get("depends_on", [])):
            raise ScheduleError("task is unknown or dependencies are not complete")
        if tasks[task_id]["status"] not in {"queued", "ready", "running"}:
            raise ScheduleError("task is not in a schedulable state")
        current = leases.get(task_id)
        if current and current["expires_at"] > now:
            raise ScheduleError(f"task already leased by {current['owner']}")
        # An expired lease is reclaimable only after its timeout; each acquisition has a unique token.
        token = hashlib.sha256(f"{task_id}:{owner}:{now}:{len(self.journal.replay())}".encode()).hexdigest()
        lease = {"owner": owner, "worktree": worktree, "acquired_at": now, "expires_at": now + self.lease_seconds, "token": token}
        self.journal.append(task_id, "LEASE_ACQUIRED", lease)
        if tasks[task_id]["status"] == "queued":
            self.transition(task_id, "ready")
        if tasks[task_id]["status"] in {"queued", "ready"}:
            self.transition(task_id, "running")
        return lease

    def release(self, task_id: str, owner: str, token: str) -> None:
        _, leases = self._state()
        lease = leases.get(task_id)
        if not lease or lease["owner"] != owner or lease["token"] != token:
            raise ScheduleError("lease owner or token mismatch")
        self.journal.append(task_id, "LEASE_RELEASED", {"owner": owner, "token": token})

    def cancel(self, task_id: str, reason: str) -> None:
        if not reason.strip():
            raise ScheduleError("cancellation requires a reason")
        self.transition(task_id, "cancelled")
        self.journal.append(task_id, "TASK_CANCELLED", {"reason": reason})

    def retry(self, task_id: str, root_cause: str) -> int:
        if not root_cause.strip():
            raise ScheduleError("retry requires a root cause")
        events = self.journal.replay()
        count = sum(1 for e in events if e["task_id"] == task_id and e["event_type"] == "RETRY" and e["payload"].get("root_cause") == root_cause)
        if count >= self.max_retries:
            raise ScheduleError(f"retry budget exhausted for root cause: {root_cause}")
        next_count = count + 1
        self.journal.append(task_id, "RETRY", {"root_cause": root_cause, "attempt": next_count})
        return next_count
