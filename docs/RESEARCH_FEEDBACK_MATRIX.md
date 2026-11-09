# Feedback, model selection, and agent optimization research

**Scope:** Research-to-engineering interpretation, 2026-10-29. Literature is not a claim that skill files themselves train neural weights. Feedback loops may optimize prompts, routing, or model parameters; record the actual mechanism.

| ID | Principal authors | Model / method | Skill-library application |
|---|---|---|---|
| ML-013 | Long Ouyang, John Schulman, Paul Christiano et al. | [Training language models to follow instructions with human feedback](https://papers.neurips.cc/paper_files/paper/2022/hash/b1efde53be364a73914f58805a001731-Abstract-Conference.html) (2022, peer-reviewed) | Specify supervised feedback and preference datasets independently of skill files; version annotator rubrics. |
| ML-014 | Rafael Rafailov, Chelsea Finn, Christopher Manning et al. | [Direct Preference Optimization](https://papers.neurips.cc/paper_files/paper/2023/hash/a85b405ed65c6477a4fe8302b5e06ce7-Abstract-Conference.html) (2023, peer-reviewed) | Treat DPO as an optional model-training workflow, not a property of a markdown skill. |
| ML-015 | Yuntao Bai, Amanda Askell et al. | [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) (2022, preprint) | Store policy version, critique provenance and human auditing for AI-generated feedback. |
| ML-016 | Aman Madaan, Niket Tandon, Sean Welleck et al. | [Self-Refine: Iterative Refinement with Self-Feedback](https://papers.nips.cc/paper/2023/hash/91edff07232fb1b55a505a9e9f6c0ff3-Abstract-Conference.html) (2023, peer-reviewed) | Add bounded generate-critique-revise loop with external acceptance tests and stopping rules. |
| ML-017 | Noah Shinn, Shunyu Yao, Karthik Narasimhan et al. | [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) (2023, preprint) | Use scoped, expiring memory records and measure retries against a no-memory baseline. |
| ML-018 | Omar Khattab, Matei Zaharia, Christopher Potts et al. | [DSPy: Compiling Declarative Language Model Calls](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html) (2024, peer-reviewed) | Separate skill behavior contracts from optimizable prompt variants; evaluate before promotion. |
| ML-019 | Lingjiao Chen, Matei Zaharia, James Zou | [FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance](https://arxiv.org/abs/2305.05176) (2023, preprint) | Benchmark candidate model tiers and escalation against quality, latency and cost ceilings. |
| ML-020 | Isaac Ong, Amjad Almahairi, Ion Stoica et al. | [RouteLLM: Learning to Route LLMs with Preference Data](https://sky.cs.berkeley.edu/project/routellm/) (2024, preprint) | Log router decisions and confidence; compare against a fixed strong-model baseline. |
| ML-021 | Lianmin Zheng, Wei-Lin Chiang, Ion Stoica et al. | [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) (2023, preprint) | Randomize response order; use blinded human calibration and independent judge models. |
| ML-022 | Nathan Lambert, Valentina Pyatkin, Hannaneh Hajishirzi et al. | [RewardBench: Evaluating Reward Models for Language Modeling](https://arxiv.org/abs/2403.13787) (2024, preprint) | Test preference judges on hard negatives and out-of-domain cases before use. |
| ML-023 | Carlos E. Jimenez, John Yang, Karthik Narasimhan et al. | [SWE-bench: Can Language Models Resolve Real-world Github Issues?](https://proceedings.iclr.cc/paper_files/paper/2024/hash/edac78c3e300629acfe6cbe9ca88fb84-Abstract-Conference.html) (2024, peer-reviewed) | Use isolated fixtures with fail-to-pass and pass-to-pass checks; do not equate benchmark score with production safety. |
| ML-024 | Nelson F. Liu, Percy Liang et al. | [Lost in the Middle: How Language Models Use Long Contexts](https://aclanthology.org/2024.tacl-1.9/) (2024, peer-reviewed) | Keep skill entrypoints short and test critical instructions at multiple context positions. |

## Engineering synthesis

1. **Separate three learning layers:** (a) deterministic skill instructions and test cases, (b) inference-time critique and routing, (c) offline weight training using RLHF, RLAIF or DPO. Never claim a prompt edit is weight training.
2. **Feedback data contract:** immutable prompt and skill versions, model version, candidate outputs, preference winner/loser or scalar rating, rubric, judge identity, provenance, consent/privacy class, timestamps, and held-out split.
3. **Model selection:** establish task-family benchmarks, quality floor, token/cost budget, timeout, retry limits, fallback, abstention, and unknown-model behavior. Evaluate selection separately from generation.
4. **Neural evaluation:** use human-labeled holdouts; randomized pairwise judge comparisons, judge-model disagreement, calibration, and blinded adjudication. Do not let training examples leak into test sets.
5. **Operational deployment:** offline fixtures -> read-only shadow scoring -> bounded canary with rollback -> permission-gated production. Capture regressions, latency tails, cost, unsafe tool proposals, and distribution shift.
6. **Skill-specific testing:** test triggering and negative triggering, reference retrieval, execution determinism, tool scopes, failure recovery, and user-facing output. Evidence-backed gates take precedence over model preference rankings.

## Suggested next implementation artifacts

- `schemas/feedback_record.schema.json` plus a privacy-respecting, synthetic example corpus.
- `evals/model_selection/` with model capability registry, offline test prompts, and routing thresholds.
- `evals/skill_authoring/` trigger, counterexample, instruction-position, and prompt-injection fixtures.
- `docs/FEEDBACK_TRAINING.md` covering the distinction between preference tuning and prompt optimization.
- `docs/MODEL_ROUTING.md` covering cost/latency/quality and human escalation.

**Source-status rule:** peer-reviewed and preprint denote publication channel, not proof of universal effectiveness. Validate every result for its intended model, task distribution, and runtime.
