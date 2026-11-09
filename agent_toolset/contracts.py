"""Strict, dependency-free parsers for task, handoff, and evidence contracts."""
from __future__ import annotations

import json
import pathlib
import re
from typing import Any, Mapping

SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
TASK_ID = re.compile(r"^[A-Z][A-Z0-9-]{2,64}$")
STATUSES = {"queued", "ready", "running", "blocked", "review", "done"}
RISKS = {"low", "medium", "high", "critical"}
RESULTS = {"PASS", "FAIL", "BLOCKED"}


class ContractError(ValueError):
    """A contract is malformed or violates a safety constraint."""


def _object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{name} must be an object")
    return value


def _keys(doc: Mapping[str, Any], required: set[str], optional: set[str], name: str) -> None:
    missing = required - doc.keys()
    extra = doc.keys() - required - optional
    if missing:
        raise ContractError(f"{name} missing fields: {', '.join(sorted(missing))}")
    if extra:
        raise ContractError(f"{name} has unknown fields: {', '.join(sorted(extra))}")


def _string(value: Any, name: str, minimum: int = 1) -> str:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise ContractError(f"{name} must be a string with at least {minimum} characters")
    return value


def _list(value: Any, name: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (nonempty and not value):
        raise ContractError(f"{name} must be {'a non-empty' if nonempty else 'an'} array")
    return value


def _version(doc: Mapping[str, Any]) -> None:
    if doc.get("schema_version") != "1.0.0":
        raise ContractError("schema_version must be 1.0.0")


def validate_task(value: Any, *, roles: set[str] | None = None) -> dict[str, Any]:
    doc = _object(value, "task")
    required = {"schema_version", "task_id", "repository", "base_commit", "objective", "scope", "acceptance", "risk", "owner_role", "status"}
    optional = {"depends_on", "evidence_refs", "blocker", "approval_ref"}
    _keys(doc, required, optional, "task")
    _version(doc)
    if not isinstance(doc["task_id"], str) or not TASK_ID.fullmatch(doc["task_id"]):
        raise ContractError("task_id has invalid format")
    _string(doc["repository"], "repository", 3)
    if not isinstance(doc["base_commit"], str) or not SHA.fullmatch(doc["base_commit"]):
        raise ContractError("base_commit must be a lowercase 40-character commit SHA")
    _string(doc["objective"], "objective", 10)
    scope = _object(doc["scope"], "scope")
    _keys(scope, {"include", "exclude"}, set(), "scope")
    include = _list(scope["include"], "scope.include", nonempty=True)
    exclude = _list(scope["exclude"], "scope.exclude")
    for path in include + exclude:
        validate_repo_path(path)
    if not all(isinstance(x, str) and len(x.strip()) >= 5 for x in _list(doc["acceptance"], "acceptance", nonempty=True)):
        raise ContractError("acceptance items must be strings with at least 5 characters")
    if doc["risk"] not in RISKS:
        raise ContractError("risk is unknown")
    role = _string(doc["owner_role"], "owner_role")
    if roles is not None and role not in roles:
        raise ContractError(f"unknown owner_role: {role}")
    if doc["status"] not in STATUSES:
        raise ContractError("status is unknown")
    for key in ("depends_on", "evidence_refs"):
        if key in doc:
            values = _list(doc[key], key)
            if not all(isinstance(x, str) and x.strip() for x in values):
                raise ContractError(f"{key} entries must be non-empty strings")
            if key == "depends_on" and len(values) != len(set(values)):
                raise ContractError("depends_on entries must be unique")
    if "blocker" in doc and doc["blocker"] is not None and not isinstance(doc["blocker"], str):
        raise ContractError("blocker must be a string or null")
    if "approval_ref" in doc and doc["approval_ref"] is not None and not isinstance(doc["approval_ref"], str):
        raise ContractError("approval_ref must be a string or null")
    return doc


def validate_handoff(value: Any) -> dict[str, Any]:
    doc = _object(value, "handoff")
    required = {"schema_version", "task_id", "from_role", "to_role", "input_refs", "output_refs", "status", "decision", "open_risks"}
    optional = {"source_commit", "evidence_refs"}
    _keys(doc, required, optional, "handoff")
    _version(doc)
    for key in ("task_id", "from_role", "to_role"):
        _string(doc[key], key)
    for key in ("input_refs", "output_refs", "open_risks", "evidence_refs"):
        if key in doc and not all(isinstance(x, str) and x.strip() for x in _list(doc[key], key)):
            raise ContractError(f"{key} entries must be non-empty strings")
    if doc["status"] not in {"READY", *RESULTS}:
        raise ContractError("handoff status is unknown")
    _string(doc["decision"], "decision", 5)
    if "source_commit" in doc and (not isinstance(doc["source_commit"], str) or not SHA.fullmatch(doc["source_commit"])):
        raise ContractError("source_commit must be a lowercase 40-character commit SHA")
    return doc


def validate_evidence(value: Any) -> dict[str, Any]:
    doc = _object(value, "evidence")
    required = {"schema_version", "task_id", "stage", "source_commit", "result", "checks", "artifacts"}
    optional = {"blocker", "approval_ref"}
    _keys(doc, required, optional, "evidence")
    _version(doc)
    _string(doc["task_id"], "task_id")
    _string(doc["stage"], "stage")
    if not isinstance(doc["source_commit"], str) or not SHA.fullmatch(doc["source_commit"]):
        raise ContractError("source_commit must be a lowercase 40-character commit SHA")
    if doc["result"] not in RESULTS:
        raise ContractError("evidence result is unknown")
    checks = _list(doc["checks"], "checks", nonempty=True)
    for i, raw in enumerate(checks):
        check = _object(raw, f"checks[{i}]")
        _keys(check, {"name", "result", "provenance"}, {"details"}, f"checks[{i}]")
        _string(check["name"], "check.name")
        if check["result"] not in RESULTS:
            raise ContractError("check result is unknown")
        _string(check["provenance"], "check.provenance", 4)
        if "details" in check and not isinstance(check["details"], str):
            raise ContractError("check.details must be a string")
    for i, raw in enumerate(_list(doc["artifacts"], "artifacts")):
        artifact = _object(raw, f"artifacts[{i}]")
        _keys(artifact, {"path", "sha256"}, set(), f"artifacts[{i}]")
        validate_repo_path(artifact["path"])
        if not isinstance(artifact["sha256"], str) or not DIGEST.fullmatch(artifact["sha256"]):
            raise ContractError("artifact sha256 must be a lowercase 64-character digest")
    return doc


def validate_repo_path(value: Any) -> str:
    """Reject absolute, traversal, drive, control-character, and empty paths."""
    path = _string(value, "repository path")
    if "\\" in path or any(ord(ch) < 32 for ch in path):
        raise ContractError(f"unsafe repository path: {path!r}")
    pure = pathlib.PurePosixPath(path)
    if pure.is_absolute() or path.startswith("~") or re.match(r"^[A-Za-z]:", path):
        raise ContractError(f"absolute repository path is not allowed: {path!r}")
    if any(part in {"", ".", ".."} for part in path.split("/")):
        raise ContractError(f"path traversal is not allowed: {path!r}")
    return path


def load_contract(source: str | pathlib.Path | Mapping[str, Any], kind: str) -> dict[str, Any]:
    """Load and validate JSON data or a JSON file for the selected contract kind."""
    if isinstance(source, Mapping):
        value = dict(source)
    else:
        try:
            value = json.loads(pathlib.Path(source).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ContractError(f"cannot load {kind} contract: {exc}") from exc
    validators = {"task": validate_task, "handoff": validate_handoff, "evidence": validate_evidence}
    try:
        validator = validators[kind]
    except KeyError as exc:
        raise ContractError(f"unknown contract kind: {kind}") from exc
    return validator(value)
