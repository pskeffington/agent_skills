"""Operator CLI for local task control, evidence, and release checks."""
from __future__ import annotations
import argparse
import json
import pathlib
import sys
from typing import Any
from .assurance.evidence import assess_evidence
from .assurance.ci import classify_github_run
from .assurance.security import summarize_findings
from .contracts import ContractError, load_contract
from .inventory import inventory
from .journal import Journal, JournalError
from .runners.dry_run import DryRunRunner
from .scheduler import ScheduleError, Scheduler

EXIT = {"PASS": 0, "FAIL": 1, "BLOCKED": 2}

def _json(value: Any) -> None:
    print(json.dumps(value, sort_keys=True, indent=2))

def _unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ValueError(f"duplicate release dossier key: {key}")
        result[key]=value
    return result

def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="agent-toolset",description="Local-first engineering task control plane")
    sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("doctor",help="check runtime and repository capabilities")
    inv=sub.add_parser("inventory",help="list repository files and manifests"); inv.add_argument("--repo",default=".")
    search=sub.add_parser("search",help="search local repository text with verified source provenance"); search.add_argument("--repo",default="."); search.add_argument("--query",required=True); search.add_argument("--limit",type=int,default=8); search.add_argument("--cache",help="opt in to a local content-addressed index cache")
    plan=sub.add_parser("plan",help="validate and plan a JSON array of task contracts"); plan.add_argument("contracts"); plan.add_argument("--state",default=".agent-toolset/events.jsonl")
    run=sub.add_parser("run",help="execute a safe dry run"); run.add_argument("task")
    status=sub.add_parser("status",help="show journal-derived task state"); status.add_argument("--state",default=".agent-toolset/events.jsonl")
    verify=sub.add_parser("verify",help="validate evidence against a source commit"); verify.add_argument("evidence"); verify.add_argument("--commit",required=True)
    evidence=sub.add_parser("evidence",help="validate and print an evidence contract"); evidence.add_argument("path")
    replay=sub.add_parser("replay",help="verify and display the event journal"); replay.add_argument("--state",default=".agent-toolset/events.jsonl")
    ci=sub.add_parser("ci-ingest",help="classify a saved GitHub Actions run export"); ci.add_argument("path"); ci.add_argument("--commit",required=True); ci.add_argument("--required-check",action="append",default=[])
    sec=sub.add_parser("security-summary",help="summarize a saved security findings export"); sec.add_argument("path"); sec.add_argument("--fail-on",default="high")
    release=sub.add_parser("release-check",help="evaluate a release dossier and artifact without deploying"); release.add_argument("evidence"); release.add_argument("--artifact",required=True,help="exact regular-file artifact whose digest must match the dossier"); release.add_argument("--approval-trust-store",help="operator-managed JSON allowlist of authorized approver public keys")
    approval=sub.add_parser("approval-payload",help="emit canonical approval bytes for offline detached signing"); approval.add_argument("dossier")
    artifact=sub.add_parser("artifact-check",help="verify candidate artifact bytes against a SHA256 digest"); artifact.add_argument("path"); artifact.add_argument("--sha256",required=True)
    export=sub.add_parser("export",help="export journal-derived state as JSON"); export.add_argument("--state",default=".agent-toolset/events.jsonl")
    return p

def main(argv: list[str] | None = None) -> int:
    args=parser().parse_args(argv)
    try:
        if args.command == "doctor":
            _json({"status":"PASS","python":sys.version.split()[0],"journal":"available","runner":"dry-run","codex_execution":"disabled"}); return 0
        if args.command == "inventory":
            value=inventory(args.repo); _json({"status":"PASS",**value}); return 0
        if args.command == "search":
            from .rag import build_index, load_or_build_cache, search as rag_search, verify_hits
            root=pathlib.Path(args.repo).resolve(strict=True)
            if not root.is_dir(): raise ValueError("repository root must be a directory")
            if args.cache:
                index,fingerprint,cache_hit=load_or_build_cache(root,args.cache)
            else:
                index=build_index(root); fingerprint=None; cache_hit=False
            hits=rag_search(index,args.query,limit=args.limit)
            hit_validity=verify_hits(root,hits)
            verified=[hit for hit,valid in zip(hits,hit_validity) if valid]
            _json({"status":"PASS","root":str(root),"query":args.query,"hits":verified,"unverified_hits":len(hits)-len(verified),"cache_fingerprint":fingerprint,"cache_hit":cache_hit})
            return 0
        if args.command == "run":
            task=load_contract(args.task,"task")
            result=DryRunRunner().prepare(task,{"mode":"dry-run"})
            _json({"status":result.status,"run_id":result.run_id,"runner":result.runner,"message":result.message,"provenance":result.provenance}); return 0
        if args.command == "evidence":
            doc=load_contract(args.path,"evidence"); _json({"status":"PASS","evidence":doc}); return 0
        if args.command == "verify":
            doc=load_contract(args.evidence,"evidence"); result=assess_evidence(doc,subject_commit=args.commit); _json(result)
            return 2 if doc["result"] == "BLOCKED" and result["status"] == "FAIL" else EXIT[result["status"]]
        if args.command == "ci-ingest":
            doc=json.loads(pathlib.Path(args.path).read_text(encoding="utf-8")); result=classify_github_run(doc,expected_commit=args.commit,required_checks=set(args.required_check)); _json(result); return {"PASS":0,"FAIL":1,"BLOCKED":2}[result["status"]]
        if args.command == "security-summary":
            doc=json.loads(pathlib.Path(args.path).read_text(encoding="utf-8")); result=summarize_findings(doc,fail_on=args.fail_on); _json(result); return {"PASS":0,"FAIL":1,"BLOCKED":2}[result["status"]]
        if args.command == "release-check":
            from .assurance.release import evaluate
            from .assurance.approval import load_trust_store, make_openssl_approval_verifier
            doc=json.loads(pathlib.Path(args.evidence).read_text(encoding="utf-8"),object_pairs_hook=_unique_object)
            verifier=None
            if args.approval_trust_store:
                verifier=make_openssl_approval_verifier(load_trust_store(args.approval_trust_store))
            result=evaluate(doc,approval_verifier=verifier,artifact_path=args.artifact)
            _json(result); return {"PASS":0,"FAIL":1,"BLOCKED":2}[result["status"]]
        if args.command == "approval-payload":
            from .assurance.approval import approval_payload_for_dossier
            doc=json.loads(pathlib.Path(args.dossier).read_text(encoding="utf-8"),object_pairs_hook=_unique_object)
            try:
                payload=approval_payload_for_dossier(doc)
            except ValueError as exc:
                print(json.dumps({"status":"BLOCKED","error":str(exc)}),file=sys.stderr); return 2
            sys.stdout.buffer.write(payload); return 0
        if args.command == "artifact-check":
            from .assurance.artifact import verify_artifact
            result=verify_artifact(args.path,args.sha256); _json(result); return {"PASS":0,"FAIL":1,"BLOCKED":2}[result["status"]]
        if args.command in {"status","replay","export"}:
            journal=Journal(args.state)
            if args.command == "replay":
                events=journal.replay(); _json({"status":"PASS","events":events}); return 0
            if args.command == "status":
                result=Scheduler(journal).status(); _json({"status":"PASS","state":result}); return 0
            events=journal.replay(); _json({"status":"PASS","events":events}); return 0
        if args.command == "plan":
            contracts=json.loads(pathlib.Path(args.contracts).read_text(encoding="utf-8"))
            if isinstance(contracts,dict): contracts=[contracts]
            if not isinstance(contracts,list): raise ContractError("task contracts file must contain an object or array")
            scheduler=Scheduler(Journal(args.state)); ids=scheduler.add_tasks(contracts)
            _json({"status":"PASS","added":ids,"ready":scheduler.plan()}); return 0
    except (OSError, ValueError, TypeError, ContractError, JournalError, ScheduleError) as exc:
        _json({"status":"BLOCKED","error":str(exc)}); return 2
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
