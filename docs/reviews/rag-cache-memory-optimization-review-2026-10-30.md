# RAG cache memory optimization investigation — 2026-10-30

**Result: PASS for the benchmark/tooling change; memory optimization rejected**  
**Reviewer:** independent code review agent  
**Task:** `RAG-CACHE-PEAK-MEM-OPT`

The comparison harness now records warm-hit and cold-miss latency, peak traced Python allocation, environment, matching source manifests, and excluded corpus paths. The optional `exclude_paths` argument to `load_or_build_cache` preserves default behavior and lets benchmarks omit their own report file. Tests verify that cache misses and hits each perform one source fingerprint scan and that changing an excluded report does not change the cache fingerprint.

The first candidate avoided retaining raw file bytes during the fingerprint pass. It reduced measured warm-hit peak allocation by about 3.8%, but increased cold-miss median latency by 8.5% locally and 12.2% on the 500-file corpus. That approach was removed. A second candidate dropped retained records immediately before parsing a verified cache entry; paired measurements showed no peak-allocation reduction. That approach was removed as well.

The final baseline/candidate comparisons show near-identical timings and candidate peak allocations 1,249 bytes higher locally and 817 bytes higher on the scale corpus. The reviewer approved the benchmark and API changes and confirmed the conclusion: **no memory optimization is shipped**. The comparison is observational and local to the recorded corpus/environment.
