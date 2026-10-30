#!/usr/bin/env python3
"""Validate skill structures, literature evidence, and generated catalog."""
import json
import sys
from datetime import date
from pathlib import Path

from index_skills import ROOT, build_catalog, render_catalog


def validate(root=ROOT):
    errors = []
    try:
        catalog = build_catalog(root)
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
        catalog = None
    path = root / "catalog" / "skills.json"
    if catalog is not None:
        if not catalog["skills"]:
            errors.append("no skills in canonical directory")
        if not path.is_file() or path.read_text(encoding="utf-8") != render_catalog(root):
            errors.append("generated skill catalog is missing or stale")
    evidence = root / "data" / "literature_matrix.json"
    try:
        data = json.loads(evidence.read_text(encoding="utf-8"))
        if data.get("schema_version") != 1 or not isinstance(data.get("sources"), list):
            errors.append("invalid literature matrix schema")
        else:
            ids = set()
            for source in data["sources"]:
                sid = source.get("id", "")
                required = ("title", "type", "url", "finding", "engineering_implication", "status", "verified_on")
                if not sid or sid in ids:
                    errors.append(f"missing or duplicate evidence ID: {sid}")
                ids.add(sid)
                if any(not isinstance(source.get(k), str) or not source[k].strip() for k in required):
                    errors.append(f"incomplete literature record: {sid}")
                if not source.get("url", "").startswith("https://"):
                    errors.append(f"non-HTTPS source URL: {sid}")
                try:
                    date.fromisoformat(source.get("verified_on", ""))
                except (ValueError, TypeError):
                    errors.append(f"invalid verification date: {sid}")
    except (OSError, ValueError, TypeError) as exc:
        errors.append(f"cannot load evidence matrix: {exc}")
    return errors


def main():
    issues = validate()
    if issues:
        for issue in issues:
            print("FAIL:", issue, file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS: metadata, links, size, literature and catalog ({len(build_catalog()['skills'])} skills)")


if __name__ == "__main__":
    main()
