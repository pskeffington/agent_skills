"""Allowlisted, shell-free deterministic command execution."""
from __future__ import annotations

import os
import pathlib
import subprocess
import time
from dataclasses import asdict, dataclass
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

class TestExecutor:
    def __init__(self, root: str | pathlib.Path, *, timeout: float = 120.0, output_limit: int = 200_000):
        self.root = pathlib.Path(root).resolve(strict=True)
        self.timeout = timeout
        self.output_limit = output_limit
        if timeout <= 0 or output_limit <= 0:
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
        try:
            proc = subprocess.run(command, cwd=workdir, env=env, capture_output=True, text=True, timeout=self.timeout, shell=False, check=False)
            out, err = proc.stdout, proc.stderr
            outcome = "PASS" if proc.returncode == 0 else "FAIL"
            code = proc.returncode
        except subprocess.TimeoutExpired as exc:
            out = _as_text(exc.stdout)
            err = _as_text(exc.stderr) + "\ncommand timed out"
            outcome, code = "BLOCKED", None
        except OSError as exc:
            out, err, outcome, code = "", str(exc), "BLOCKED", None
        return TestResult(command, str(workdir), code, outcome, round(time.monotonic()-start, 6), out[-self.output_limit:], err[-self.output_limit:])


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", "replace") if isinstance(value, bytes) else value
