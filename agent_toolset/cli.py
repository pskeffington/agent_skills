"""Operator CLI for local task control, evidence, and release checks."""
from __future__ import annotations
import argparse
import json
import pathlib
import sys
from typing import Any
from .assurance.evidence import assess_evidence
from .contracts import ContractError, load_contract
from .inventory import inventory
from .journal import Journal, JournalError
from .runners.dry_run import DryRunRunner
from .scheduler import ScheduleError, Scheduler

EXIT = {"PASS": 0, "FAIL": 1, "BLOCKED": 2}

def _json(value: Any) -> None:
    print(json.dumps(value, sort_keys=True, indent=2))

def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="agent-toolset",description="Local-first engineering task control plane")
    sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("doctor",help="check runtime and repository capabilities")
    inv=sub.add_parser("inventory",help="list repository files and manifests"); inv.add_argument("--repo",default=".")
    plan=sub.add_parser("plan",help="validate and plan a JSON array of task contracts"); plan.add_argument("contracts"); plan.add_argument("--state",default=".agent-toolset/events.jsonl")
    run=sub.add_parser("run",help="execute a safe dry run"); run.add_argument("task")
    status=sub.add_parser("status",help="show journal-derived task state"); status.add_argument("--state",default=".agent-toolset/events.jsonl")
    verify=sub.add_parser("verify",help="validate evidence against a source commit"); verify.add_argument("evidence"); verify.add_argument("--commit",required=True)
    evidence=sub.add_parser("evidence",help="validate and print an evidence contract"); evidence.add_argument("path")
    replay=sub.add_parser("replay",help="verify and display the event journal"); replay.add_argument("--state",default=".agent-toolset/events.jsonl")
    release=sub.add_parser("release-check",help="evaluate a release dossier without deploying"); release.add_argument("evidence")
    export=sub.add_parser("export",help="export journal-derived state as JSON"); export.add_argument("--state",default=".agent-toolset/events.jsonl")
    return p

def main(argv: list[str] | None = None) -> int:
    args=parser().parse_args(argv)
    try:
        if args.command == "doctor":
            _json({"status":"PASS","python":sys.version.split()[0],"journal":"available","runner":"dry-run","codex_execution":"disabled"}); return 0
        if args.command == "inventory":
            value=inventory(args.repo); _json({"status":"PASS",**value}); return 0
        if args.command == "run":
            task=load_contract(args.task,"task")
            result=DryRunRunner().prepare(task,{"mode":"dry-run"})
            _json({"status":result.status,"run_id":result.run_id,"runner":result.runner,"message":result.message,"provenance":result.provenance}); return 0
        if args.command == "evidence":
            doc=load_contract(args.path,"evidence"); _json({"status":"PASS","evidence":doc}); return 0
        if args.command == "verify":
            doc=load_contract(args.evidence,"evidence"); result=assess_evidence(doc,subject_commit=args.commit); _json(result)
            return 2 if doc["result"] == "BLOCKED" and result["status"] == "FAIL" else EXIT[result["status"]]
        if args.command == "release-check":
            from scripts.release_gate import evaluate
            doc=json.loads(pathlib.Path(args.evidence).read_text(encoding="utf-8")); result=evaluate(doc); _json(result); return 0 if result["release_ready"] else 2
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
