"""Detached approval signature verification for fail-closed release admission."""
from __future__ import annotations

import base64
import binascii
import json
import os
import pathlib
import shutil
import stat
import subprocess
import tempfile
from typing import Any

APPROVAL_FIELDS = (
    "evidence_ref", "subject_commit", "artifact_sha256", "invocation_id",
    "decision", "approver_id", "authority_ref", "signature_algorithm",
)
MAX_TRUST_STORE_BYTES = 1_000_000
MAX_PUBLIC_KEY_BYTES = 16_384
MAX_SIGNATURE_BYTES = 16_384


def canonical_approval_payload(approval: dict[str, Any]) -> bytes:
    """Return the exact canonical bytes that an approver signs."""
    if not isinstance(approval, dict):
        raise ValueError("approval must be an object")
    allowed = set(APPROVAL_FIELDS) | {"signature"}
    if not set(APPROVAL_FIELDS) <= set(approval) or set(approval) - allowed:
        raise ValueError("approval payload has missing or unknown fields")
    payload = {field: approval.get(field) for field in APPROVAL_FIELDS}
    if any(not isinstance(value, str) or not value.strip() for value in payload.values()):
        raise ValueError("approval signature payload is incomplete")
    if payload["decision"] != "APPROVE" or payload["signature_algorithm"] != "openssl-dgst-sha256":
        raise ValueError("unsupported approval decision or signature algorithm")
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_trust_store(path: str | pathlib.Path) -> dict[str, dict[str, str]]:
    """Load an operator-managed, bounded public-key allowlist from a regular file."""
    target = pathlib.Path(path).expanduser()
    if not hasattr(os, "O_NOFOLLOW"):
        raise ValueError("safe approval trust store loading requires O_NOFOLLOW support")
    descriptor = os.open(target, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_TRUST_STORE_BYTES:
            raise ValueError("approval trust store must be a regular file under 1 MB")
        if metadata.st_mode & 0o022:
            raise ValueError("approval trust store must not be group or world writable")
        chunks = []
        remaining = MAX_TRUST_STORE_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        if len(raw) > MAX_TRUST_STORE_BYTES:
            raise ValueError("approval trust store exceeds 1 MB")
    finally:
        os.close(descriptor)
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate trust store key: {key}")
            result[key] = value
        return result

    document = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs)
    if not isinstance(document, dict) or set(document) != {"schema_version", "approvers"} or document.get("schema_version") != "1.0.0":
        raise ValueError("invalid approval trust store structure")
    approvers = document.get("approvers")
    if not isinstance(approvers, dict) or not approvers:
        raise ValueError("approval trust store must contain authorized approvers")
    normalized: dict[str, dict[str, str]] = {}
    for approver_id, record in approvers.items():
        if not isinstance(approver_id, str) or len(approver_id.strip()) < 3 or not isinstance(record, dict) or set(record) != {"authority_ref", "public_key_pem"}:
            raise ValueError("invalid approval trust store approver record")
        authority_ref, public_key = record.get("authority_ref"), record.get("public_key_pem")
        if not isinstance(authority_ref, str) or len(authority_ref.strip()) < 3:
            raise ValueError("invalid approval authority reference")
        if not isinstance(public_key, str) or len(public_key.encode("utf-8")) > MAX_PUBLIC_KEY_BYTES or "-----BEGIN PUBLIC KEY-----" not in public_key:
            raise ValueError("invalid or oversized approval public key")
        normalized[approver_id] = {"authority_ref": authority_ref, "public_key_pem": public_key}
    return normalized


def make_openssl_approval_verifier(approvers: dict[str, dict[str, str]], *, openssl: str | None = None):
    """Create a verifier. Returns None from the callback when OpenSSL is unavailable."""
    executable = openssl or shutil.which("openssl")

    def verify(approval: dict[str, Any], subject_commit: str, artifact_sha256: str) -> bool | None:
        if not executable:
            return None
        if not isinstance(approval, dict):
            return False
        approver_id = approval.get("approver_id")
        trusted = approvers.get(approver_id) if isinstance(approver_id, str) else None
        if not isinstance(trusted, dict) or trusted.get("authority_ref") != approval.get("authority_ref"):
            return False
        if approval.get("subject_commit") != subject_commit or approval.get("artifact_sha256") != artifact_sha256:
            return False
        try:
            payload = canonical_approval_payload(approval)
            encoded = approval.get("signature")
            if not isinstance(encoded, str) or len(encoded) > 4 * ((MAX_SIGNATURE_BYTES + 2) // 3):
                return False
            signature = base64.b64decode(encoded, validate=True)
            if not signature or len(signature) > MAX_SIGNATURE_BYTES:
                return False
        except (ValueError, binascii.Error):
            return False
        try:
            with tempfile.TemporaryDirectory(prefix="agent-toolset-approval-") as directory:
                root = pathlib.Path(directory)
                public_key_path = root / "approver.pem"
                signature_path = root / "approval.sig"
                payload_path = root / "approval.json"
                for path, data in (
                    (public_key_path, trusted["public_key_pem"].encode("utf-8")),
                    (signature_path, signature),
                    (payload_path, payload),
                ):
                    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(descriptor, "wb") as stream:
                        stream.write(data)
                result = subprocess.run(
                    [executable, "dgst", "-sha256", "-verify", str(public_key_path), "-signature", str(signature_path), str(payload_path)],
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=False, timeout=5, check=False, env={"PATH": str(pathlib.Path(executable).parent), "LC_ALL": "C"},
                )
            return result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return None

    return verify
