#!/usr/bin/env python3
"""Read-only preflight: report repository identity, cleanliness and local checks."""
import argparse
import json
import pathlib
import subprocess
import sys

def cmd(directory, *args):
    try:
        r = subprocess.run(["git", "-C", str(directory), *args], capture_output=True, text=True, timeout=12, check=False)
        return {"status": "PASS" if r.returncode == 0 else "FAIL", "code": r.returncode,
                "stdout": r.stdout.strip()[:4000], "stderr": r.stderr.strip()[:1000]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "BLOCKED", "error": str(exc)}

def preflight(repo):
    root = pathlib.Path(repo).resolve()
    results = {"repository": str(root), "exists": root.is_dir()}
    if not root.is_dir():
        results["result"] = "BLOCKED"
        return results
    for name, args in {"head": ("rev-parse", "HEAD"), "branch": ("branch", "--show-current"),
                       "status": ("status", "--porcelain"), "root": ("rev-parse", "--show-toplevel")}.items():
        results[name] = cmd(root, *args)
    results["instructions_present"] = (root / "AGENTS.md").exists()
    results["result"] = "PASS" if all(results[x]["status"] == "PASS" for x in ("head","branch","status","root")) else "BLOCKED"
    results["clean"] = results["status"].get("stdout", "<unknown>") == "" if results["status"]["status"] == "PASS" else None
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()
    out = preflight(args.repo)
    print(json.dumps(out, indent=2))
    sys.exit(0 if out["result"] == "PASS" else 2)
