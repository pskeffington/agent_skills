"""Hash-chained JSONL event journal with crash-tolerant append and replay."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import tempfile
import threading
from datetime import datetime, timezone
from typing import Any, Iterable

GENESIS = "0" * 64


class JournalError(ValueError):
    """Journal is malformed, truncated, or tampered with."""


def _canonical(doc: dict[str, Any]) -> bytes:
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _event_hash(doc: dict[str, Any]) -> str:
    unsigned = {k: v for k, v in doc.items() if k != "hash"}
    return hashlib.sha256(_canonical(unsigned)).hexdigest()


class Journal:
    """Append-only local event store. A trailing incomplete record is ignored on replay."""

    def __init__(self, path: str | pathlib.Path):
        self.path = pathlib.Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        raw = self.path.read_bytes()
        lines = raw.splitlines(keepends=True)
        complete = [line for line in lines if line.endswith(b"\n")]
        # A final line without newline indicates an interrupted append; only discard that tail.
        if lines and not lines[-1].endswith(b"\n"):
            lines = complete
        else:
            lines = complete
        events: list[dict[str, Any]] = []
        prior_hash = GENESIS
        for expected, line in enumerate(lines, 1):
            try:
                event = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise JournalError(f"invalid record at sequence {expected}: {exc}") from exc
            if not isinstance(event, dict):
                raise JournalError(f"record {expected} is not an object")
            if event.get("sequence") != expected:
                raise JournalError(f"sequence mismatch at record {expected}")
            if event.get("previous_hash") != prior_hash:
                raise JournalError(f"hash chain mismatch at record {expected}")
            actual = _event_hash(event)
            if event.get("hash") != actual:
                raise JournalError(f"content hash mismatch at record {expected}")
            prior_hash = actual
            events.append(event)
        return events

    def append(self, task_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(task_id, str) or not task_id.strip() or not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("task_id and event_type must be non-empty strings")
        if not isinstance(payload, dict):
            raise TypeError("payload must be an object")
        with self._lock:
            fd = os.open(self.path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600)
            try:
                try:
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_EX)
                except ImportError:
                    # On platforms without flock, only the per-instance thread lock is available.
                    pass
                # Read the tail only after taking the process-level lock so sequence and
                # previous_hash are derived from the record immediately preceding this append.
                size = os.fstat(fd).st_size
                raw = os.pread(fd, size, 0)
                if raw and not raw.endswith(b"\n"):
                    cut = raw.rfind(b"\n") + 1
                    os.ftruncate(fd, cut)
                events = self.read()
                previous = events[-1]["hash"] if events else GENESIS
                event: dict[str, Any] = {
                    "sequence": len(events) + 1,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "task_id": task_id,
                    "event_type": event_type,
                    "payload": payload,
                    "previous_hash": previous,
                }
                event["hash"] = _event_hash(event)
                encoded = _canonical(event) + b"\n"
                written = os.write(fd, encoded)
                if written != len(encoded):
                    raise OSError("short journal append")
                os.fsync(fd)
                return event
            finally:
                os.close(fd)

    def checkpoint(self, path: str | pathlib.Path) -> pathlib.Path:
        """Atomically write a snapshot pointer containing journal head and sequence."""
        events = self.read()
        snapshot = {"sequence": len(events), "head_hash": events[-1]["hash"] if events else GENESIS}
        target = pathlib.Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(_canonical(snapshot) + b"\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, target)
        except BaseException:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
            raise
        return target

    def replay(self) -> list[dict[str, Any]]:
        """Return verified events in order; consumers reconstruct state without mutation."""
        return self.read()
