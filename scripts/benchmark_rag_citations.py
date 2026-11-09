#!/usr/bin/env python3
"""Compare per-hit and batched source verification for local RAG citations."""
from __future__ import annotations
import argparse
import json
import pathlib
import platform
import statistics
import subprocess
import sys
import time

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agent_toolset.rag import build_index,cache_fingerprint,search,verify_hit,verify_hits

QUERIES=(
    "release readiness task journal lease",
    "Codex runner containment attestation",
    "cache fingerprint validation",
)

def run_benchmark(root: pathlib.Path, repetitions: int=20, *, exclude_paths: tuple[pathlib.Path,...]=()) -> dict:
    if not 1<=repetitions<=100:
        raise ValueError("repetitions must be between 1 and 100")
    root=root.resolve(strict=True)
    index=build_index(root,exclude_paths=exclude_paths)
    fingerprint,_,_=cache_fingerprint(root,exclude_paths=exclude_paths)
    results=[]
    for query in QUERIES:
        hits=search(index,query,limit=8)
        expected=[verify_hit(root,hit) for hit in hits]
        if verify_hits(root,hits)!=expected:
            raise ValueError("batched citation verification changed validity results")
        timings={"per_hit":[],"batched":[]}
        for repetition in range(repetitions):
            order=("per_hit","batched") if repetition%2==0 else ("batched","per_hit")
            for method in order:
                start=time.perf_counter_ns()
                actual=([verify_hit(root,hit) for hit in hits] if method=="per_hit" else verify_hits(root,hits))
                elapsed=(time.perf_counter_ns()-start)/1_000_000
                if actual!=expected:
                    raise ValueError(f"{method} verification changed results")
                timings[method].append(round(elapsed,6))
        old=statistics.median(timings["per_hit"])
        new=statistics.median(timings["batched"])
        results.append({"query":query,"hit_count":len(hits),"distinct_sources":len({hit["path"] for hit in hits}),
                        "per_hit_samples_ms":timings["per_hit"],"batched_samples_ms":timings["batched"],
                        "per_hit_median_ms":old,"batched_median_ms":new,
                        "median_change_percent":round((new/old-1)*100,2) if old else 0.0,
                        "validity_results_equal":True})
    try:
        commit=subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],capture_output=True,text=True,timeout=3,check=False)
        source_commit=commit.stdout.strip() if commit.returncode==0 else None
        state=subprocess.run(["git","-C",str(root),"status","--porcelain","--untracked-files=all"],capture_output=True,text=True,timeout=3,check=False)
        worktree_clean=state.returncode==0 and not state.stdout.strip()
    except (OSError,subprocess.TimeoutExpired):
        source_commit=None; worktree_clean=None
    return {"status":"PASS","scope":"local citation verification only; observational timings; exact validity equality required",
            "environment":{"python":sys.version.split()[0],"platform":platform.platform(),"source_commit":source_commit,
                           "worktree_clean":worktree_clean,"corpus_root":str(root),"corpus_fingerprint":fingerprint,
                           "repetitions_per_method_per_query":repetitions,"measurement":"untraced wall time, alternating method order"},
            "results":results}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",type=pathlib.Path,default=ROOT)
    parser.add_argument("--repetitions",type=int,default=20)
    parser.add_argument("--output",type=pathlib.Path)
    args=parser.parse_args()
    try:
        excluded=(args.output.expanduser().absolute(),) if args.output else ()
        result=run_benchmark(args.repo,args.repetitions,exclude_paths=excluded)
        encoded=json.dumps(result,indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(encoded+"\n",encoding="utf-8")
        print(encoded)
    except (OSError,ValueError) as exc:
        print(json.dumps({"status":"BLOCKED","error":str(exc)},indent=2)); raise SystemExit(2)
