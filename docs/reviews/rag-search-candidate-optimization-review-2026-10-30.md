# RAG candidate-only search scoring review

- Task: `RAG-SEARCH-CANDIDATE-OPTIMIZATION`
- Baseline: `d851d408e5437a176ca1d1969ad31fd84ded4249`
- Candidate `agent_toolset/rag.py` SHA-256: `d92d2a5cc72d59a18f5d715c89c32c4c896c8950093b3b26e491e2099c20f99d`
- Result: **PASS after correction**
- Changed implementation: `agent_toolset/rag.py`
- Regression coverage: `tests/test_rag.py`
- Paired benchmark: `scripts/compare_rag_search.py`

The initial candidate review found that sorting query terms changed floating-point accumulation order and could alter rounded BM25 scores by `0.00000001`. It also found document-frequency behavior differed for zero-valued keys in manually supplied indexes. The implementation now preserves baseline set iteration order, counts document frequency on key presence, and scores only truthy matches in that order.

The exact-score regression dynamically constructs an order-sensitive fixture and passed in separate processes under 101 `PYTHONHASHSEED` values (0 through 100); the zero-frequency key-presence regression also passes. The independent reviewer confirmed no remaining parity findings. This hash-seed sweep covers the current Python/runtime only.

The paired benchmark asserts exact result equality on a shared candidate-built index. Across 6,244 indexed lines, 21 alternating uninstrumented samples report 50.25% lower median for the multi-term query, 27.74% lower for a common-term query, and 28.74% lower for a no-answer query. These local measurements do not establish cross-machine performance.

The parent run passed 85 repository tests, structural validation, Codex preflight and `git diff --check`; the synthetic release gate remained BLOCKED (exit 2). CI for this uncommitted candidate has not run. This review does not approve release or deployment.
