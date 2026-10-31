# RAG optimization roadmap — O0–O6

Status: **PLANNED**. Baseline evidence is from `docs/benchmarks/rag-benchmark-2026-10-30.json`, source commit `d3afa371af75a98e812e716e6794e7c984b5d2c1` (five macOS arm64/Python 3.15.2 trials; 97 files, 3,482 indexed lines). No optimization passes may be claimed until rerun and evidenced.

## Baseline and diagnosis
- Cold index: median **81.9008 ms**, Python peak **3,203,953 B**.
- Warm cache: median **192.9025 ms**, Python peak **7,677,718 B**.
- Warm lexical search: median **8.7332 ms**.
- Cache/cold ratio **2.355x** (cache slower); memory ratio **2.396x**.
- **Observed code path:** `load_or_build_cache` calls `cache_fingerprint`; `_source_records` traverses and rereads/rehashes all eligible content even on a warm hit. Then warm hit reads entire JSON envelope, performs JSON decode, canonical JSON reserialization + SHA-256, and validates all cached documents. This is an architectural double-work hypothesis, *not yet a measured per-stage attribution*.
- Security invariants: no symlink traversal, no secret indexing, source provenance SHA256, corrupted cache fail-closed, changed-source invalidation, explicit opt-in caching, no external network or new dependencies, no stale result accepted as verified.

## Optimization phases and ownership

| ID | Dependency | Owner / files | Task | Admission evidence |
| --- | --- | --- | --- | --- |
| O0 | none | performance agent: new `scripts/profile_rag_cache.py`, `tests/test_profile_rag_cache.py` | Instrument end-to-end and stage timings: traversal, bytes read/hash, tokenization, JSON encode/decode, digest verification, schema checks, hit verification, memory; benchmark 1x, 10x, 100x corpora, changed-file, warm/cold, 15+ paired repetitions | Reproducible JSON, environment/HEAD, median/p95, memory, source counts; no claim from a single trial |
| O1 | O0 | cache implementer: `agent_toolset/rag.py`, `tests/test_rag_cache.py` | Design explicit **trusted unchanged-worktree** fast path using file manifest metadata; strict source-digest mode remains default unless an operator knowingly enables relaxed metadata precheck. Record limitations: same-size, restored-mtime edits and concurrent changes; verify every returned hit against current bytes | Both modes tested with adversarial same-size/mtime mutation, deletion, symlink swap, stale index; strict mode remains fully SHA-based |
| O2 | O0 | storage implementer, separate branch or serialized ownership of `rag.py` | Reduce JSON materialization/duplicate structures: profile parser, minimize repeated canonicalization, consider compact versioned data layout and bounded streaming only if standard library allows; retain envelope integrity and fail closed | Measured memory reduction; legacy cache safely invalidated/migrated; corrupt/truncated/oversized fixture coverage |
| O3 | O1,O2 | index implementer: `rag.py`, `tests/test_rag.py` | Move to file-level incremental re-tokenization: hash changed files, reuse unchanged source documents by digest, atomic index replacement; account for removals, rename, mixed changes | Identical canonical search hits and citations to full rebuild; no changed source survives; crash/restart safety |
| O4 | O3 | retrieval implementer: `rag.py` plus retrieval fixtures | Profile query scaling; optional inverted postings/term document frequencies for sparse scoring, bounded candidate-set and deterministic ties | Strict rank parity or documented rank change with separate relevance evaluation; no quality decline on held-out labels |
| O5 | O2,O3,O4 | verifier (independent) + security reviewer | Run adversarial cache suite, no-follow filesystem escape, malformed JSON, oversized file, concurrent writer, interrupted fsync/rename, tainted-index and prompt injection fixtures | Reviewer distinct from author; exact commands, commit, OS, all exit codes and findings |
| O6 | O5 | performance agent + integrator | Benchmark versus frozen baseline under same controlled environment; choose policy thresholds and create release dossier | Three clean repeated benchmark batches, raw timings, no regressions, CI PASS, separate owner release approval |

### Performance targets (targets, NOT results)
1. Strict warm cache: first **break even** with full rebuild on reference corpus, then target <=0.80x cold-build median **without weaker freshness semantics**; reject if no demonstrated gain.
2. Opt-in trusted metadata mode (only if security review accepts tradeoff): target <=0.50x cold-build median, but never claim strong change detection from stat metadata alone.
3. Peak Python allocation <=1.25x cold-build baseline for warm cache on the representative corpus, with longer-term target <=1.0x.
4. Larger corpora: demonstrate positive amortization and determine break-even file/line counts; p95 warm query <=1.2x baseline, precision@k/recall@k unchanged, 0 stale/unsafe citations in security tests.
5. If optimized cache cannot beat rebuilding for small corpora, **disable cache by heuristic** for small trees and record this decision instead of forcing the cache.

## Benchmark protocol
- Isolate measurement harness instrumentation from the implementation under test. Run clean checkout, pinned Python, same filesystem, fixed fixture seeds and corpus SHA; record dirty state.
- Separate scan/stat, full rehash, index generation, cache parse+validation and query from end-to-end measurements. Exclude test-fixture generation and first-time cache creation from warm metrics.
- Report distributions including median, p95, memory, repetitions and paired percent deltas; include a no-cache control. Run functional parity before timing comparisons.
- Re-evaluate at three corpus scales, both warm process and fresh process, and following one-file modification, same-length edit with restored mtime, deletion and symlink substitution.
- Keep full-source hash verification and hit-level verification as explicit distinctions. A fast metadata check cannot prove file contents unchanged; prohibit presenting metadata-mode results as strict-validity results.

## Concurrent Codex coordination
- O0 profiling is read-only/new-files and may run concurrently with existing work.
- O1/O2/O3/O4 all require changes to `agent_toolset/rag.py`: **one owner at a time**, serialized merges, separate dependent branches. Avoid PR #3/#4 consolidation conflicts.
- Codex should begin O0 and produce actual stage breakdown before choosing an O1 or O2 design. No preemptive dependency additions or switch to embeddings/vector DB.
- Implement one phase per small commit; update this table with run IDs and hashes. Unverified is BLOCKED, never PASS.
- Production publication, credentials, or cross-repository access require separate human approval.

## Codex execution entrypoint
Read `AGENTS.md`, `docs/IMPLEMENTATION_QUEUE.md`, `docs/RAG_VALIDATION_OPTIMIZATION.md`, and this roadmap. Record HEAD and working-tree state; run current unit tests and validator. Implement O0 only, create offline stage timing fixtures and tests, measure strict path, report bottleneck percentages and exact evidence. Proceed to O1/O2 only if separate file ownership and authorization remain clear; no merge/deploy.
