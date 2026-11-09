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
    parser.add_argument("--artifact",help="exact candidate artifact to hash against the dossier")
    parser.add_argument("--approval-trust-store",help="operator-managed JSON allowlist of authorized approver public keys")
    args=parser.parse_args(argv)
    try:
        def unique_pairs(pairs):
            result={}
            for key,value in pairs:
                if key in result: raise ValueError(f"duplicate release dossier key: {key}")
                result[key]=value
            return result
        data=example() if args.example else json.loads(pathlib.Path(args.evidence).read_text(encoding="utf-8"),object_pairs_hook=unique_pairs)
        verifier=None
        if args.approval_trust_store:
            from agent_toolset.assurance.approval import load_trust_store, make_openssl_approval_verifier
            verifier=make_openssl_approval_verifier(load_trust_store(args.approval_trust_store))
        result=evaluate(data,approval_verifier=verifier,artifact_path=args.artifact)
    except (ValueError,OSError,TypeError) as exc:
        result={"status":"BLOCKED","release_ready":False,"issues":[str(exc)],"notice":"Read-only evaluation. No deployment performed."}
    print(json.dumps(result,indent=2))
    return {"PASS":0,"FAIL":1,"BLOCKED":2}[result["status"]]

if __name__ == "__main__":
    raise SystemExit(main())
