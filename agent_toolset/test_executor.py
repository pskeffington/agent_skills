"""Allowlisted, shell-free command execution with bounded output capture."""
from __future__ import annotations

import os
import pathlib
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Sequence

from .inventory import confined_path

@dataclass(frozen=True)
class TestResult:
    command: list[str]
    cwd: str
    exit_code: int | None
    outcome: str
    duration_seconds: float
    stdout: str
    stderr: str
    stdout_truncated: bool = False
    stderr_truncated: bool = False


def _drain_bounded(stream, limit: int) -> tuple[bytes, bool]:
    """Drain a pipe without retaining more than limit bytes in memory."""
    captured = bytearray()
    truncated = False
    while True:
        try:
            chunk = stream.read(4096)
        except OSError:
            break
        if not chunk:
            break
        available = max(0, limit - len(captured))
        if available:
            captured.extend(chunk[:available])
        if len(chunk) > available:
            truncated = True
    return bytes(captured), truncated


class TestExecutor:
    def __init__(self, root: str | pathlib.Path, *, timeout: float = 120.0, output_limit: int = 200_000):
        self.root = pathlib.Path(root).resolve(strict=True)
        self.timeout = timeout
        self.output_limit = output_limit
        if timeout <= 0 or output_limit <= 0 or isinstance(output_limit, bool):
            raise ValueError("timeout and output_limit must be positive")
        self.commands = {
            "python-unittest": ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"],
            "pytest": ["python3", "-m", "pytest", "-q"],
            "validate": ["python3", "scripts/validate.py"],
        }

    def run(self, name: str, *, args: Sequence[str] = (), cwd: str = ".") -> TestResult:
        if name not in self.commands:
            raise ValueError(f"command is not allowlisted: {name}")
        if args:
            raise ValueError("additional command arguments are not supported")
        workdir = confined_path(self.root, cwd) if cwd != "." else self.root
        if not workdir.is_dir():
            raise ValueError("command cwd must be a directory")
        command = self.commands[name]
        env = {"PATH": os.defpath, "HOME": str(self.root), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1", "GIT_OPTIONAL_LOCKS": "0"}
        start = time.monotonic()
        proc = None
        out = err = b""
        out_truncated = err_truncated = False
        outcome, code = "BLOCKED", None
        try:
            proc = subprocess.Popen(
                command,
                cwd=workdir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                close_fds=True,
                start_new_session=(os.name == "posix"),
                creationflags=(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0),
            )
            result_box: dict[str, tuple[bytes, bool]] = {}
            readers = [
                threading.Thread(target=lambda: result_box.setdefault("stdout", _drain_bounded(proc.stdout, self.output_limit)), daemon=True),
                threading.Thread(target=lambda: result_box.setdefault("stderr", _drain_bounded(proc.stderr, self.output_limit)), daemon=True),
            ]
            for reader in readers:
                reader.start()
            try:
                code = proc.wait(timeout=self.timeout)
                outcome = "PASS" if code == 0 else "FAIL"
            except subprocess.TimeoutExpired:
                self._kill_process_tree(proc)
                proc.wait()
                code, outcome = None, "BLOCKED"
                err = b"command timed out\n"
            for reader in readers:
                reader.join(timeout=1.0)
            if any(reader.is_alive() for reader in readers):
                # A child retained the output pipe after the main process exited.
                self._kill_process_tree(proc)
                code, outcome = None, "BLOCKED"
                err = (err + b"child process kept output pipe open\n")[: self.output_limit]
                for reader in readers:
                    reader.join(timeout=0.5)
            for stream in (proc.stdout, proc.stderr):
                if stream is not None:
                    stream.close()
            out, out_truncated = result_box.get("stdout", (b"", False))
            captured_err, err_truncated = result_box.get("stderr", (b"", False))
            err = (err + captured_err)[: self.output_limit]
            if len(err) >= self.output_limit and captured_err:
                err_truncated = True
        except OSError as exc:
            err = str(exc).encode("utf-8", "replace")[: self.output_limit]
            outcome, code = "BLOCKED", None
        return TestResult(
            command,
            str(workdir),
            code,
            outcome,
            round(time.monotonic() - start, 6),
            _as_text(out),
            _as_text(err),
            out_truncated,
            err_truncated,
        )

    @staticmethod
    def _kill_process_tree(proc: subprocess.Popen) -> None:
        if proc.poll() is not None and os.name != "posix":
            return
        try:
            if os.name == "posix":
                os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()
        except (OSError, ProcessLookupError):
            pass


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", "replace") if isinstance(value, bytes) else value
