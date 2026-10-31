#!/usr/bin/env python3
"""Compare warm-hit and cold-miss cache costs against a recorded Git revision."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import pathlib
import platform
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path, default=ROOT)
    parser.add_argument("--baseline", default="HEAD", help="Git revision supplying baseline rag.py")
    parser.add_argument("--repetitions", type=int, default=7)
    parser.add_argument("--exclude", action="append", default=[], help="repository path to exclude from the comparison corpus (repeatable)")
    args = parser.parse_args()
    if not 3 <= args.repetitions <= 25:
        parser.error("--repetitions must be between 3 and 25")
    root = args.repo.resolve(strict=True)
    requested_excludes=tuple((root / item).resolve(strict=False) if not pathlib.Path(item).is_absolute() else pathlib.Path(item).resolve(strict=False) for item in args.exclude)
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
        baseline_source_records=baseline_module._source_records
        def baseline_records_with_exclusions(source_root,suffixes,exclude_paths=()):
            return baseline_source_records(source_root,suffixes,tuple(exclude_paths)+requested_excludes)
        baseline_module._source_records=baseline_records_with_exclusions
        baseline_cache = temp_path / "baseline-cache"
        candidate_cache = temp_path / "candidate-cache"
        baseline_module.load_or_build_cache(root, baseline_cache)
        candidate_module.load_or_build_cache(root, candidate_cache,exclude_paths=requested_excludes)
        samples = {"baseline": [], "candidate": []}
        cold_samples = {"baseline": [], "candidate": []}
        operations = {
            "baseline": (baseline_module, baseline_cache),
            "candidate": (candidate_module, candidate_cache),
        }
        for repetition in range(args.repetitions):
            order = ("baseline", "candidate") if repetition % 2 == 0 else ("candidate", "baseline")
            for label in order:
                module, cache = operations[label]
                started = time.perf_counter_ns()
                (module.load_or_build_cache(root,cache) if label=="baseline" else module.load_or_build_cache(root,cache,exclude_paths=requested_excludes))
                samples[label].append((time.perf_counter_ns() - started) / 1_000_000)
            order=("baseline","candidate") if repetition%2==0 else ("candidate","baseline")
            for label in order:
                module,_=operations[label]
                cold_cache=temp_path/f"cold-{label}-{repetition}"
                started=time.perf_counter_ns()
                (module.load_or_build_cache(root,cold_cache) if label=="baseline" else module.load_or_build_cache(root,cold_cache,exclude_paths=requested_excludes))
                cold_samples[label].append((time.perf_counter_ns()-started)/1_000_000)
        results = {}
        for label, (module, cache) in operations.items():
            # Measure allocation separately so tracemalloc overhead does not
            # distort latency comparisons.
            tracemalloc.start()
            (module.load_or_build_cache(root,cache) if label=="baseline" else module.load_or_build_cache(root,cache,exclude_paths=requested_excludes))
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            results[label] = {
                "samples_ms": [round(sample, 4) for sample in samples[label]],
                "median_latency_ms": round(statistics.median(samples[label]), 4),
                "cold_cache_samples_ms": [round(sample,4) for sample in cold_samples[label]],
                "cold_cache_median_latency_ms": round(statistics.median(cold_samples[label]),4),
                "traced_python_peak_bytes": peak,
            }
        baseline_fingerprint, _, baseline_records = baseline_module.cache_fingerprint(root,exclude_paths=requested_excludes)
        fingerprint, _, candidate_records = candidate_module.cache_fingerprint(root,exclude_paths=requested_excludes)
        baseline_manifest = [(path, digest) for path, _, digest in baseline_records]
        candidate_manifest = [(path, digest) for path, _, digest in candidate_records]
        if baseline_manifest != candidate_manifest or baseline_fingerprint != fingerprint:
            raise RuntimeError("baseline and candidate source manifests differ")
    print(json.dumps({
        "scope": "paired local warm-hit and cold-miss cache comparison with peak Python allocation; observational; no cross-machine claim",
        "baseline_revision": args.baseline,
        "baseline_source_sha256": hashlib.sha256(baseline).hexdigest(),
        "candidate_source_sha256": hashlib.sha256(candidate).hexdigest(),
        "corpus_root": str(root),
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "excluded_paths": [str(path) for path in requested_excludes],
        "corpus_fingerprint": fingerprint,
        "source_files": len(candidate_records),
        "source_manifest_equal": True,
        "repetitions": args.repetitions,
        "results": results,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
