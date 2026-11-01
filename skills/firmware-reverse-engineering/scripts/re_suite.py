#!/usr/bin/env python3
"""Offline, read-only firmware intake and manifest validator. Python stdlib only."""
import argparse
import hashlib
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

SHA_CHUNK = 1024 * 1024

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fd:
        for chunk in iter(lambda: fd.read(SHA_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()

def intake(path, out):
    source = pathlib.Path(path).resolve(strict=True)
    if not source.is_file():
        raise ValueError("input must be a regular file")
    if source.is_symlink():
        raise ValueError("symlink input rejected")
    record = {"schema_version": 1, "kind":"firmware-intake",
              "source_filename": source.name, "size_bytes":source.stat().st_size,
              "sha256":digest(source),
              "captured_utc":datetime.now(timezone.utc).isoformat(),
              "device_model":"unknown", "architecture":"unknown",
              "evidence_status":"unverified", "flash_authorized":False}
    target = pathlib.Path(out)
    if target.exists():
        raise FileExistsError("refuse overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as fp:
        json.dump(record, fp, indent=2, sort_keys=True)
        fp.write("\n")
    return record

def validate_manifest(path):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    tools = data.get("tools")
    if data.get("schema_version") != 1 or not isinstance(tools, list) or not tools:
        raise ValueError("invalid schema or empty tools")
    names = set()
    for entry in tools:
        name = entry["name"]
        url = entry["repository"]
        if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*", name):
            raise ValueError("bad name")
        if name in names:
            raise ValueError("duplicate tool: " + name)
        names.add(name)
        if not re.fullmatch(r"https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", url):
            raise ValueError("bad GitHub source for " + name)
        if entry.get("install_default") is not False or entry.get("hardware_write_allowed") is not False:
            raise ValueError("unsafe auto-enable: " + name)
    return len(names)

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("intake")
    i.add_argument("firmware")
    i.add_argument("--out", required=True)
    v = sub.add_parser("validate-tools")
    v.add_argument("manifest")
    args = parser.parse_args()
    try:
        if args.cmd == "intake":
            print(json.dumps(intake(args.firmware, args.out), indent=2))
        else:
            print("VALID tools:", validate_manifest(args.manifest))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as e:
        print("ERROR:", e, file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
