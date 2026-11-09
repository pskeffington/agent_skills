# RAG candidate memory optimization review — 2026-10-30

- Task: `RAG-SEARCH-CANDIDATE-MEMORY`
- Baseline: `a7d4e37084cb4aefb456876e9d9e48c20958214b`
- Candidate: `agent_toolset/rag.py`
- Result: **PASS**

The running total uses integer addition in the same document order as the former lengths list, preserving the computed average. Converting each document's matched-term list to a tuple preserves its term iteration order. IDF remains computed once per query term, and document frequency continues counting key presence, including zero-frequency entries.

Focused RAG tests pass. Independent differential checking compared the candidate with the committed scorer on 3,000 randomized indexes across three result limits each; all ordered results matched exactly. No correctness, mutation, or ordering regression was found.

On the deterministic 20,000-line corpus, the candidate reduced peak traced allocation by about 16.8% for the measured multi-term query. Query latency remained within approximately 2.2% of baseline. Repository-sized query timings improved by about 2–3% in this local run. These are observational measurements, not cross-machine guarantees. No release or deployment approval is implied.
