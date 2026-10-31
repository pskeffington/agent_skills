"""Read-only repository inventory with root and symlink confinement."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
from typing import Any

from .contracts import ContractError, validate_repo_path

MANIFESTS = {"pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "Pipfile", "package.json", "Cargo.toml", "go.mod", "pom.xml", "build.gradle"}


def confined_path(root: str | pathlib.Path, relative: str, *, allow_missing: bool = False) -> pathlib.Path:
    base = pathlib.Path(root).resolve(strict=True)
    validate_repo_path(relative)
    candidate = base / relative
    try:
        resolved = candidate.resolve(strict=not allow_missing)
    except OSError as exc:
        raise ContractError(f"path cannot be resolved: {relative}: {exc}") from exc
    if not resolved.is_relative_to(base):
        raise ContractError(f"path escapes configured repository: {relative}")
    return resolved


def inventory(root: str | pathlib.Path, *, max_files: int = 10000) -> dict[str, Any]:
    base = pathlib.Path(root).resolve(strict=True)
    if not base.is_dir():
        raise ValueError("repository root must be a directory")
    files: list[str] = []
    manifests: list[str] = []
    instructions: list[str] = []
    tests: list[str] = []
    digest = hashlib.sha256()
    for current, dirs, names in os.walk(base, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in {".git", ".venv", "venv", "node_modules", "__pycache__"})
        for name in sorted(names):
            path = pathlib.Path(current) / name
            rel = path.relative_to(base).as_posix()
            try:
                if not path.resolve(strict=True).is_relative_to(base):
                    continue
            except OSError:
                continue
            files.append(rel)
            if len(files) > max_files:
                raise ValueError(f"inventory exceeds file limit ({max_files})")
            digest.update(rel.encode("utf-8") + b"\0")
            if name in MANIFESTS:
                manifests.append(rel)
            if name == "AGENTS.md" or name == "SKILL.md":
                instructions.append(rel)
            if "test" in path.parts or name.startswith("test_") or name.endswith("_test.py"):
                tests.append(rel)
    files.sort()
    return {"root": str(base), "files": files, "manifests": sorted(manifests), "instructions": sorted(instructions), "tests": sorted(tests), "head_sha": _git_head(base), "inventory_sha256": digest.hexdigest()}


def _git_head(root: pathlib.Path) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=3, env={"PATH": os.defpath, "GIT_OPTIONAL_LOCKS": "0"}, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def read_file(root: str | pathlib.Path, relative: str, *, limit: int = 1_000_000) -> str:
    path = confined_path(root, relative)
    if not path.is_file():
        raise ValueError("requested path is not a regular file")
    data = path.read_bytes()
    if len(data) > limit:
        raise ValueError(f"file exceeds read limit ({limit} bytes)")
    return data.decode("utf-8")
