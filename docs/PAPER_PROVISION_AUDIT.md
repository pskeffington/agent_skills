# Paper-to-skill provision audit

Scope: authoritative abstracts and publication metadata; not independent experimental replication. Source-backed findings are distinct from proposed engineering controls.

| ID | Supported finding | Proposed provision | Caveat and test |
|---|---|---|---|
| ML-013 | SFT demonstrations, preference rankings, then RLHF | Separate demonstrations and preference pairs, record annotator criteria | Model training, not a SKILL.md capability; assess held-out human preference |
| ML-014 | DPO optimizes chosen/rejected data against a reference policy | Version pairs, reference model and training objective | Requires weight optimization and curated preferences; assess blind win rate |
| ML-015 | Constitutional critique, revision and AI preference training | Version principles, critiques, preference source and human audits | AI feedback may reinforce errors; assess human adjudication |
| ML-016 | Generate-critique-revise without changing weights | Bound retries, enforce independent correctness checks | Critique is not guaranteed to improve output; assess task correctness vs one-pass |
| ML-017 | Verbal feedback stored as episodic memory | Version and expire reflections, run no-memory baseline | Memory is not neural reinforcement learning; assess recovery rate |
| ML-018 | Optimize LM programs against declared metrics | Version prompts and demonstrations, keep untouched holdout | Proxy optimization may overfit; assess held-out metric |
| ML-019 | Cascades trade cost against answer quality | Compare strong-only baseline against bounded cascade | Published savings are workload-specific; assess quality, p95 latency, cost |
| ML-020 | Preference-trained model router chooses between model tiers | Calibrate routing, log confidence and escalation | Transfer results not a new-provider guarantee; assess regret, quality floor, cost |
| ML-021 | LLM judges show order and verbosity biases | Use order swaps, blinded human audit, judge disagreement | Judge ratings are not ground truth; assess human agreement |
| ML-022 | Reward model evaluation uses chosen/rejected contrasts | Include hard negatives and safety/reasoning subsets | Reward scores can be gamed; assess pairwise accuracy by domain |
| ML-023 | Repository issues can be evaluated with executable tests | Isolate patch cases and run regression and repair tests | Benchmark passes do not equal deployment readiness; assess pass-to-pass and fail-to-pass |
| ML-024 | Long-context extraction degrades at some positions | Test instruction position and progressive loading | Sensitivity varies by task/model; assess position-stratified success |

## Corrections

ML-019 is published in TMLR (2024), ML-020 in ICLR (2025), and ML-022 in Findings of NAACL (2025). Earlier records had classified these by preprint date.

## Admission contract

A skill file alone does not train weights. Keep offline RLHF/DPO/RLAIF apart from inference-time prompt revision, skill editing, model routing, and memory. Enforce data provenance, train/test isolation, human review, permission boundaries, no silent learning, bounded iteration, model fallback, shadow evaluation and rollback. Report confidence intervals and failed cases; never generalize paper benchmarks into deployment guarantees.
