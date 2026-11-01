#!/usr/bin/env python3
"""Read-only Android TV ADB inventory. Requires explicit --serial; no discovery scan."""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys

COMMANDS = {
    "model": ["shell", "getprop", "ro.product.model"],
    "android": ["shell", "getprop", "ro.build.version.release"],
    "patch": ["shell", "getprop", "ro.build.version.security_patch"],
    "build": ["shell", "getprop", "ro.build.id"],
    "kernel": ["shell", "uname", "-r"],
    "packages": ["shell", "pm", "list", "packages"],
    "disabled": ["shell", "pm", "list", "packages", "-d"],
}
PACKAGE = re.compile(r"^package:([a-zA-Z0-9_.]+)$")
SERIAL = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")

def parse_packages(text):
    return sorted(set(m.group(1) for line in text.splitlines()
                      if (m := PACKAGE.fullmatch(line.strip()))))

def run(adb, serial, args, timeout):
    p = subprocess.run([adb, "-s", serial, *args], capture_output=True,
                       text=True, timeout=timeout, check=False)
    if p.returncode:
        raise RuntimeError("ADB command failed: " + " ".join(args))
    return p.stdout.strip()

def collect(adb, serial, timeout):
    if not SERIAL.fullmatch(serial):
        raise ValueError("Invalid ADB serial")
    results, errors = {}, {}
    for key, command in COMMANDS.items():
        try:
            output = run(adb, serial, command, timeout)
            results[key] = parse_packages(output) if key in ("packages", "disabled") else output
        except (OSError, subprocess.TimeoutExpired, RuntimeError) as exc:
            errors[key] = type(exc).__name__
    return {
        "schema_version": "1.0.0",
        "asset_id": "CE-SONY-01",
        "captured_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "collection_mode": "adb_read_only",
        "identity_confirmed": False,
        "observations": results,
        "errors": errors,
        "validation": "not_run"
    }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--serial", required=True, help="ADB device serial explicitly authorized on TV")
    ap.add_argument("--adb", default="adb")
    ap.add_argument("--timeout", type=int, default=8)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    if args.timeout < 1 or args.timeout > 60:
        ap.error("timeout must be 1..60")
    try:
        data = collect(args.adb, args.serial, args.timeout)
        with open(args.output, "x", encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)
            file.write("\n")
    except (OSError, ValueError) as exc:
        ap.error(str(exc))
    print("Inventory saved; verify target identity and redact before sharing.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
