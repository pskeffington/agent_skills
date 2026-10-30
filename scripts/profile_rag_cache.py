#!/usr/bin/env python3
"""O0 reproducible profiler: strict warm-cache stages and end-to-end baselines."""
from __future__ import annotations
import argparse
import cProfile
import io
import json
import pathlib
import pstats
import statistics
import sys
import tempfile
import time
import tracemalloc

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_toolset import rag

def _measure(fn):
    profiler = cProfile.Profile()
    tracemalloc.start()
    start = time.perf_counter_ns()
    try:
        profiler.enable()
        result = fn()
    finally:
        profiler.disable()
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    stats = pstats.Stats(profiler)
    top = sorted(
        ({"function": f"{filename}:{line}:{name}", "calls": calls,
          "self_seconds": round(self_time, 7), "cumulative_seconds": round(cum_time, 7)}
         for (filename, line, name), (calls, _, self_time, cum_time, _) in stats.stats.items()),
        key=lambda entry: (-entry["cumulative_seconds"], entry["function"])
    )[:30]
    return result, {"elapsed_ms": round(elapsed_ms, 4), "peak_bytes": peak, "top_functions": top}

def profile(root: pathlib.Path, repetitions: int = 5):
    if not 1 <= repetitions <= 25:
        raise ValueError("repetitions must be 1..25")
    root = root.resolve(strict=True)
    samples = {"cold_build": [], "strict_warm_cache": [], "warm_search": []}
    with tempfile.TemporaryDirectory(prefix="agent-rag-o0-") as tmp:
        cache = pathlib.Path(tmp) / "cache"
        # Setup is intentionally outside measurements.
        cached, _, created = rag.load_or_build_cache(root, cache)
        if created:
            raise ValueError("cache setup unexpectedly reported a warm hit")
        for _ in range(repetitions):
            _, metric = _measure(lambda: rag.build_index(root))
            samples["cold_build"].append(metric)
            index, _, hit = rag.load_or_build_cache(root, cache)
            if not hit:
                raise ValueError("strict warm cache failed to hit an unchanged corpus")
            # Record a second actual read, not a synthetic bypass.
            _, metric = _measure(lambda: rag.load_or_build_cache(root, cache))
            samples["strict_warm_cache"].append(metric)
            _, metric = _measure(lambda: rag.search(index, "release readiness task journal lease", limit=8))
            samples["warm_search"].append(metric)
        if not rag.verify_hit(root, rag.search(cached, "release", limit=1)[0]) if rag.search(cached, "release", limit=1) else False:
            raise ValueError("retrieval citation validation failed")
    summary = {}
    for name, series in samples.items():
        times = sorted(sample["elapsed_ms"] for sample in series)
        summary[name] = {
            "median_ms": statistics.median(times),
            "p95_ms": times[min(len(times)-1, max(0, int(.95*(len(times)-1))))],
            "median_peak_bytes": statistics.median(sample["peak_bytes"] for sample in series),
            "samples": series,
        }
    cold = summary["cold_build"]["median_ms"]
    summary["strict_warm_cache"]["relative_to_cold"] = round(summary["strict_warm_cache"]["median_ms"]/cold, 4) if cold else None
    return {"status": "PASS", "mode": "strict SHA-256", "corpus": str(root),
            "repetitions": repetitions, "profile_note": "cProfile adds overhead; do not compare to unprofiled historical timings",
            "operations": summary}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path, default=ROOT)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()
    try:
        outcome = profile(args.repo, args.repetitions)
        data = json.dumps(outcome, indent=2, sort_keys=True)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(data + "\n", encoding="utf-8")
        print(data)
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({"status": "BLOCKED", "error": str(error)}))
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
