"""Hash-chained JSONL event journal with crash-tolerant append and replay."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import tempfile
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

GENESIS = "0" * 64


class JournalError(ValueError):
    """Journal is malformed, truncated, or tampered with."""


def _canonical(doc: dict[str, Any]) -> bytes:
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _event_hash(doc: dict[str, Any]) -> str:
    unsigned = {k: v for k, v in doc.items() if k != "hash"}
    return hashlib.sha256(_canonical(unsigned)).hexdigest()


class JournalTransaction:
    """An append interface protected by the journal's cross-process transaction lock."""

    def __init__(self, journal: "Journal", journal_fd: int):
        self.journal = journal
        self.journal_fd = journal_fd

    def append(self, task_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(task_id, str) or not task_id.strip() or not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("task_id and event_type must be non-empty strings")
        if not isinstance(payload, dict):
            raise TypeError("payload must be an object")
        fd = self.journal_fd
        # The lock is acquired before this read-modify-write sequence. lseek/read
        # are used instead of pread for portability to Windows.
        size = os.fstat(fd).st_size
        os.lseek(fd, 0, os.SEEK_SET)
        chunks=[]
        remaining=size
        while remaining:
            chunk=os.read(fd,min(remaining,1024*1024))
            if not chunk:
                break
            chunks.append(chunk); remaining-=len(chunk)
        raw=b"".join(chunks)
        if raw and not raw.endswith(b"\n"):
            cut=raw.rfind(b"\n")+1
            os.ftruncate(fd,cut)
        events=self.journal.read()
        previous=events[-1]["hash"] if events else GENESIS
        event: dict[str,Any]={
            "sequence":len(events)+1,
            "timestamp":datetime.now(timezone.utc).isoformat(),
            "task_id":task_id,
            "event_type":event_type,
            "payload":payload,
            "previous_hash":previous,
        }
        event["hash"]=_event_hash(event)
        encoded=_canonical(event)+b"\n"
        # The descriptor is O_APPEND; a single write minimizes partial records.
        written=os.write(fd,encoded)
        if written!=len(encoded):
            raise OSError("short journal append")
        os.fsync(fd)
        return event


class Journal:
    """Append-only local event store. A trailing incomplete record is ignored on replay."""

    def __init__(self, path: str | pathlib.Path):
        self.path=pathlib.Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self._lock=threading.RLock()
        self.lock_path=self.path.with_name(self.path.name+".lock")

    @contextmanager
    def transaction(self) -> Iterator[JournalTransaction]:
        """Serialize a state read/check/multi-event append across processes."""
        with self._lock:
            nofollow=getattr(os,"O_NOFOLLOW",0)
            lock_fd=os.open(self.lock_path,os.O_RDWR|os.O_CREAT|nofollow,0o600)
            locked=False
            try:
                if os.name=="nt":
                    import msvcrt
                    if os.fstat(lock_fd).st_size==0:
                        os.write(lock_fd,b"0")
                        os.fsync(lock_fd)
                    os.lseek(lock_fd,0,os.SEEK_SET)
                    msvcrt.locking(lock_fd,msvcrt.LK_LOCK,1)
                    locked=True
                else:
                    import fcntl
                    fcntl.flock(lock_fd,fcntl.LOCK_EX)
                    locked=True
                fd=os.open(self.path,os.O_RDWR|os.O_CREAT|os.O_APPEND|nofollow,0o600)
                try:
                    yield JournalTransaction(self,fd)
                finally:
                    os.close(fd)
            finally:
                if locked:
                    if os.name=="nt":
                        import msvcrt
                        os.lseek(lock_fd,0,os.SEEK_SET)
                        msvcrt.locking(lock_fd,msvcrt.LK_UNLCK,1)
                    else:
                        import fcntl
                        fcntl.flock(lock_fd,fcntl.LOCK_UN)
                os.close(lock_fd)

    def append(self, task_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self.transaction() as transaction:
            return transaction.append(task_id,event_type,payload)

    def read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        raw=self.path.read_bytes()
        lines=raw.splitlines(keepends=True)
        if lines and not lines[-1].endswith(b"\n"):
            lines=lines[:-1]
        else:
            lines=[line for line in lines if line.endswith(b"\n")]
        events: list[dict[str,Any]]=[]
        prior_hash=GENESIS
        for expected,line in enumerate(lines,1):
            try:
                event=json.loads(line)
            except (json.JSONDecodeError,UnicodeDecodeError) as exc:
                raise JournalError(f"invalid record at sequence {expected}: {exc}") from exc
            if not isinstance(event,dict):
                raise JournalError(f"record {expected} is not an object")
            if event.get("sequence")!=expected:
                raise JournalError(f"sequence mismatch at record {expected}")
            if event.get("previous_hash")!=prior_hash:
                raise JournalError(f"hash chain mismatch at record {expected}")
            actual=_event_hash(event)
            if event.get("hash")!=actual:
                raise JournalError(f"content hash mismatch at record {expected}")
            prior_hash=actual
            events.append(event)
        return events

    def checkpoint(self, path: str | pathlib.Path) -> pathlib.Path:
        """Atomically write a snapshot pointer containing journal head and sequence."""
        events=self.read()
        snapshot={"sequence":len(events),"head_hash":events[-1]["hash"] if events else GENESIS}
        target=pathlib.Path(path)
        target.parent.mkdir(parents=True,exist_ok=True)
        fd,temp_name=tempfile.mkstemp(prefix=f".{target.name}.",dir=target.parent)
        try:
            with os.fdopen(fd,"wb") as stream:
                stream.write(_canonical(snapshot)+b"\n")
                stream.flush(); os.fsync(stream.fileno())
            os.replace(temp_name,target)
        except BaseException:
            try: os.unlink(temp_name)
            except FileNotFoundError: pass
            raise
        return target

    def replay(self) -> list[dict[str, Any]]:
        """Return verified events in order; consumers reconstruct state without mutation."""
        return self.read()
