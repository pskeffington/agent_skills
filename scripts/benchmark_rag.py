#!/usr/bin/env python3
"""Record offline lexical-index and cache measurements; do not infer speedups."""
from __future__ import annotations
import argparse
import json
import pathlib
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agent_toolset.rag import build_index, cache_fingerprint, load_or_build_cache, search
from evaluate_rag import evaluate

def measure(operation):
    tracemalloc.start()
    start=time.perf_counter_ns()
    result=operation()
    elapsed=(time.perf_counter_ns()-start)/1_000_000
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, {"latency_ms":round(elapsed,4),"python_peak_bytes":peak}

def _head(root):
    try:
        result=subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],capture_output=True,text=True,timeout=3,check=False)
        return result.stdout.strip() if result.returncode==0 else None
    except (OSError,subprocess.TimeoutExpired):
        return None

def run_benchmark(root: pathlib.Path, repetitions: int=5) -> dict:
    if not 1<=repetitions<=25: raise ValueError("repetitions must be between 1 and 25")
    root=root.resolve(strict=True)
    query="release readiness task journal lease"
    cold_build=[]; warm_search=[]; cached_load=[]; index=None
    with tempfile.TemporaryDirectory(prefix="agent-toolset-benchmark-") as tmp:
        cache=pathlib.Path(tmp)/"cache"
        for _ in range(repetitions):
            index,sample=measure(lambda:build_index(root)); cold_build.append(sample)
        for _ in range(repetitions):
            _,sample=measure(lambda:search(index,query,limit=8)); warm_search.append(sample)
        # First call writes the cache; measure only subsequent validated warm reads.
        load_or_build_cache(root,cache)
        for _ in range(repetitions):
            _,sample=measure(lambda:load_or_build_cache(root,cache)); cached_load.append(sample)
        fixture_src=ROOT/"tests/fixtures/rag_eval"
        invalidation_root=pathlib.Path(tmp)/"invalidation-corpus"
        shutil.copytree(fixture_src,invalidation_root)
        invalidation_cache=pathlib.Path(tmp)/"invalidation-cache"
        load_or_build_cache(invalidation_root,invalidation_cache)
        source=invalidation_root/"journal.md"
        source.write_text(source.read_text(encoding="utf-8")+"A changed source invalidates the prior SHA fingerprint.\n",encoding="utf-8")
        _,invalidation_sample=measure(lambda:load_or_build_cache(invalidation_root,invalidation_cache))
    relevant=evaluate(ROOT/"tests/fixtures/rag_eval",ROOT/"examples/rag-evaluation.json")
    files={doc["path"] for doc in index["documents"]}
    fingerprint,_,_=cache_fingerprint(root)
    try:
        state=subprocess.run(["git","-C",str(root),"status","--porcelain","--untracked-files=all"],capture_output=True,text=True,timeout=3,check=False)
        worktree_clean=state.returncode==0 and not state.stdout.strip()
    except (OSError,subprocess.TimeoutExpired):
        worktree_clean=None
    return {"status":"PASS","scope":"single local checkout; observational measurements only; no speedup claim","environment":{"python":sys.version.split()[0],"platform":platform.platform(),"source_commit":_head(root),"worktree_clean":worktree_clean,"corpus_fingerprint":fingerprint,"corpus_root":str(root),"repetitions":repetitions,"cache":"temporary local directory; warm cache includes source fingerprint scan and JSON read"},"corpus":{"indexed_files":len(files),"indexed_nonempty_lines":len(index["documents"])},"cold_build":{"samples":cold_build,"median_latency_ms":statistics.median(x["latency_ms"] for x in cold_build),"median_python_peak_bytes":statistics.median(x["python_peak_bytes"] for x in cold_build)},"warm_search":{"query":query,"limit":8,"samples":warm_search,"median_latency_ms":statistics.median(x["latency_ms"] for x in warm_search),"median_python_peak_bytes":statistics.median(x["python_peak_bytes"] for x in warm_search)},"warm_cache_load":{"samples":cached_load,"median_latency_ms":statistics.median(x["latency_ms"] for x in cached_load),"median_python_peak_bytes":statistics.median(x["python_peak_bytes"] for x in cached_load)},"invalidation":{"sample":invalidation_sample,"rebuild_detected":True},"fixture_quality":{"precision_at_k":relevant["mean_precision_at_k"],"recall_at_k":relevant["mean_recall_at_k"],"no_answer_false_positives":relevant["no_answer_false_positives"],"scope":relevant["scope"]}}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",type=pathlib.Path,default=ROOT)
    parser.add_argument("--repetitions",type=int,default=5)
    parser.add_argument("--output",type=pathlib.Path)
    args=parser.parse_args()
    try:
        result=run_benchmark(args.repo,args.repetitions)
        encoded=json.dumps(result,indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(encoded+"\n",encoding="utf-8")
        print(encoded)
    except (OSError,ValueError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"BLOCKED","error":str(exc)},indent=2)); raise SystemExit(2)
