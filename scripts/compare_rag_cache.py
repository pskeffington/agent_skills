#!/usr/bin/env python3
"""Compare warm-cache validation against a recorded Git revision."""
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
import tracemalloc


ROOT = pathlib.Path(__file__).resolve().parents[1]


def _module(name: str, source: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module source: {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _measure(module, root: pathlib.Path, cache: pathlib.Path, repetitions: int) -> dict:
    module.load_or_build_cache(root, cache)
    samples = []
    peaks = []
    for _ in range(repetitions):
        tracemalloc.start()
        started = time.perf_counter_ns()
        module.load_or_build_cache(root, cache)
        samples.append((time.perf_counter_ns() - started) / 1_000_000)
        peaks.append(tracemalloc.get_traced_memory()[1])
        tracemalloc.stop()
    return {
        "samples_ms": [round(sample, 4) for sample in samples],
        "median_latency_ms": round(statistics.median(samples), 4),
        "median_python_peak_bytes": int(statistics.median(peaks)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path, default=ROOT)
    parser.add_argument("--baseline", default="HEAD", help="Git revision supplying baseline rag.py")
    parser.add_argument("--repetitions", type=int, default=7)
    args = parser.parse_args()
    if not 3 <= args.repetitions <= 25:
        parser.error("--repetitions must be between 3 and 25")
    root = args.repo.resolve(strict=True)
    baseline = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{args.baseline}:agent_toolset/rag.py"],
        capture_output=True,
        check=True,
    ).stdout
    candidate = (ROOT / "agent_toolset/rag.py").read_bytes()
    with tempfile.TemporaryDirectory(prefix="rag-cache-compare-") as temp:
        temp_path = pathlib.Path(temp)
        baseline_path = temp_path / "baseline.py"
        candidate_path = temp_path / "candidate.py"
        baseline_path.write_bytes(baseline)
        candidate_path.write_bytes(candidate)
        baseline_module = _module("rag_baseline", baseline_path)
        candidate_module = _module("rag_candidate", candidate_path)
        baseline_cache = temp_path / "baseline-cache"
        candidate_cache = temp_path / "candidate-cache"
        results = {
            "baseline": _measure(baseline_module, root, baseline_cache, args.repetitions),
            "candidate": _measure(candidate_module, root, candidate_cache, args.repetitions),
        }
        fingerprint, _, records = candidate_module.cache_fingerprint(root)
    print(json.dumps({
        "scope": "paired local warm-cache validation comparison; observational; no cross-machine claim",
        "baseline_revision": args.baseline,
        "baseline_source_sha256": hashlib.sha256(baseline).hexdigest(),
        "candidate_source_sha256": hashlib.sha256(candidate).hexdigest(),
        "corpus_root": str(root),
        "corpus_fingerprint": fingerprint,
        "source_files": len(records),
        "repetitions": args.repetitions,
        "results": results,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
