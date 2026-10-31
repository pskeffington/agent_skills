#!/usr/bin/env python3
"""Compare deterministic RAG search against a recorded Git revision."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import pathlib
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _module(name: str, source: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module source: {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _timed(search, index, query: str, limit: int) -> tuple[float, list[dict]]:
    started = time.perf_counter_ns()
    result = search(index, query, limit=limit)
    return (time.perf_counter_ns() - started) / 1_000_000, result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path, default=ROOT)
    parser.add_argument("--baseline", default="HEAD")
    parser.add_argument("--query", action="append", help="query to benchmark (repeat for multiple cases)")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--repetitions", type=int, default=15)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100 or not 3 <= args.repetitions <= 101:
        parser.error("limit must be 1..100 and repetitions 3..101")
    root = args.repo.resolve(strict=True)
    baseline_source = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{args.baseline}:agent_toolset/rag.py"],
        capture_output=True,
        check=True,
    ).stdout
    candidate_source = (ROOT / "agent_toolset/rag.py").read_bytes()
    with tempfile.TemporaryDirectory(prefix="rag-search-compare-") as temp:
        temp_path = pathlib.Path(temp)
        baseline_path = temp_path / "baseline.py"
        candidate_path = temp_path / "candidate.py"
        baseline_path.write_bytes(baseline_source)
        candidate_path.write_bytes(candidate_source)
        baseline = _module("rag_search_baseline", baseline_path)
        candidate = _module("rag_search_candidate", candidate_path)
        index = candidate.build_index(root)
        queries = args.query or ["release readiness task journal lease", "agent", "no_such_rag_token_928374"]
        measurements = []
        for query in queries:
            expected = baseline.search(index, query, limit=args.limit)
            actual = candidate.search(index, query, limit=args.limit)
            if expected != actual:
                raise RuntimeError(f"candidate search results differ from baseline for query {query!r}")
            baseline_samples = []
            candidate_samples = []
            for repetition in range(args.repetitions):
                ordered = ((baseline, baseline_samples), (candidate, candidate_samples))
                if repetition % 2:
                    ordered = tuple(reversed(ordered))
                for module, samples in ordered:
                    elapsed, result = _timed(module.search, index, query, args.limit)
                    if result != expected:
                        raise RuntimeError(f"search output changed during timing for query {query!r}")
                    samples.append(elapsed)
            measurements.append({
                "query": query,
                "exact_results_equal": True,
                "baseline": {"samples_ms": [round(x, 4) for x in baseline_samples], "median_latency_ms": round(statistics.median(baseline_samples), 4)},
                "candidate": {"samples_ms": [round(x, 4) for x in candidate_samples], "median_latency_ms": round(statistics.median(candidate_samples), 4)},
            })
        fingerprint, _, records = candidate.cache_fingerprint(root)
    print(json.dumps({
        "scope": "paired uninstrumented local search latency; exact result equality required; no cross-machine claim",
        "baseline_revision": args.baseline,
        "baseline_source_sha256": hashlib.sha256(baseline_source).hexdigest(),
        "candidate_source_sha256": hashlib.sha256(candidate_source).hexdigest(),
        "corpus_root": str(root),
        "corpus_fingerprint": fingerprint,
        "source_files": len(records),
        "indexed_lines": len(index["documents"]),
        "limit": args.limit,
        "queries": measurements,
        "repetitions": args.repetitions,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
