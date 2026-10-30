"""Read-only artifact digest verification for release candidate admission."""
from __future__ import annotations

import hashlib
import hmac
import os
import pathlib
import re
import stat
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")


def verify_artifact(path: str | pathlib.Path, expected_sha256: str) -> dict[str, Any]:
    """Hash a regular, no-follow-opened artifact and compare its exact bytes."""
    if not isinstance(expected_sha256, str) or not SHA256.fullmatch(expected_sha256):
        return {"status": "BLOCKED", "issues": ["expected SHA256 must be 64 lowercase hexadecimal characters"]}
    if not hasattr(os, "O_NOFOLLOW"):
        return {"status": "BLOCKED", "issues": ["safe artifact verification requires O_NOFOLLOW support"]}
    target = pathlib.Path(path).expanduser()
    if not target.is_absolute():
        target = pathlib.Path.cwd() / target
    if ".." in target.parts:
        return {"status": "BLOCKED", "issues": ["artifact path must not contain parent traversal"]}
    if not hasattr(os, "O_DIRECTORY") or os.open not in os.supports_dir_fd:
        return {"status": "BLOCKED", "issues": ["safe artifact verification requires directory-relative open support"]}
    directory_fd = None
    try:
        directory_fd = os.open(target.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0))
        for component in target.parts[1:-1]:
            next_fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0), dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        descriptor = os.open(target.name, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0), dir_fd=directory_fd)
    except OSError as exc:
        return {"status": "BLOCKED", "issues": [f"artifact cannot be opened safely: {exc}"]}
    finally:
        if directory_fd is not None:
            os.close(directory_fd)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            return {"status": "BLOCKED", "issues": ["artifact must be a regular file"]}
        digest = hashlib.sha256()
        size = 0
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
        after = os.fstat(descriptor)
        stable_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
        stable_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
        if stable_before != stable_after or size != after.st_size:
            return {"status": "BLOCKED", "issues": ["artifact changed while its digest was being computed"], "bytes_read": size}
    except OSError as exc:
        return {"status": "BLOCKED", "issues": [f"artifact could not be read completely: {exc}"]}
    finally:
        os.close(descriptor)
    actual = digest.hexdigest()
    matched = hmac.compare_digest(actual, expected_sha256)
    return {
        "status": "PASS" if matched else "FAIL",
        "artifact": str(target),
        "expected_sha256": expected_sha256,
        "actual_sha256": actual,
        "bytes_read": size,
        "issues": [] if matched else ["artifact SHA256 does not match expected digest"],
        "notice": "Read-only verification of the bytes opened during this command; no artifact was changed.",
    }
