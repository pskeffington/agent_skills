#!/usr/bin/env python3
"""Compatibility entry point for the packaged read-only release evaluator."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from agent_toolset.assurance.release import REQUIRED, evaluate, example

def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--example",action="store_true")
    group.add_argument("--evidence")
    args=parser.parse_args(argv)
    try:
        data=example() if args.example else json.loads(pathlib.Path(args.evidence).read_text(encoding="utf-8"))
        result=evaluate(data)
    except (ValueError,OSError,TypeError) as exc:
        result={"status":"BLOCKED","release_ready":False,"issues":[str(exc)],"notice":"Read-only evaluation. No deployment performed."}
    print(json.dumps(result,indent=2))
    return {"PASS":0,"FAIL":1,"BLOCKED":2}[result["status"]]

if __name__ == "__main__":
    raise SystemExit(main())
