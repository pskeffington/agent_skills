# Phased engineering roadmap

| Phase | Deliverable | Gate | Initial status |
| --- | --- | --- | --- |
| P0 Foundation | Standards matrix, ADR, repository policy, threat model | G0 | In scaffold |
| P1 Schema/index | Canonical directories, scaffold command, metadata validation, deterministic catalog | G1 | In scaffold |
| P2 Security | Adversarial fixtures, script provenance, least-privilege review, dependency audit | G2 | Pending |
| P3 Evaluations | Positive/negative triggers; repeatability and failure-case fixtures per skill | G3 | Pending |
| P4 Portability | Smoke tests in target Codex/ChatGPT/other supported clients; package verification | G4 | Pending |
| P5 Distribution | Versioned bundles, signed manifest/provenance, reviewed release and rollback | G5 | Pending |

## Next-agent task queue (in priority order)

1. Complete P0/P1 local verification and CI evidence. Do not treat workflow presence as proof a job ran.
2. Implement fixture corpus (`evals/<name>/cases.json`) with expected triggers, non-triggers, invalid inputs, and unsafe tool-call refusals. Distinguish deterministic lint from model behavior evaluation.
3. Add `scripts/evaluate.py` as a **read-only** harness with recorded expected/observed results, no undeclared external API calls.
4. Build a versioned `scripts/package_skill.py` that exports one audited skill and checks archive path traversal/size, then verify using at least one target client.
5. Develop `repo-indexing` as the next example only after its specific triggers and boundary are defined. Keep cross-repository actions permission-gated.
6. Promote with explicit G2–G5 evidence; update status, limitations, provenance, and rollback notes.

Every pass: inspect changes -> implement smallest phase item -> run validation/tests -> record results -> draft PR. If blocked, preserve the blocker and do not advance the gate or weaken checks.

## P6 Research-guided adaptive agent operation (planning only)

1. Define feedback provenance and held-out splits before attempting neural optimization.
2. Benchmark selected model tiers using deterministic task-family datasets and calibrated judges.
3. Implement offline skill prompt optimization and critique; preserve baselines and rollback.
4. Shadow-test routers and feedback loops without external side effects.
5. Admit canaries only after G2-G5 and objective quality/cost/safety thresholds are met.

Read `docs/FEEDBACK_MODEL_SELECTION.md` and `data/literature_matrix.json` before implementing this phase.

## P7 — Standalone full skill-library build campaign

Read `docs/SKILL_LIBRARY_PLAN.md` and `data/skill_build_matrix.json`. Construct 24 independent skills in four waves, first establishing evaluation fixtures and offline admission evidence. Keep all source and runtime dependencies within `agent_skills`; no sibling-repo coupling. These are **planned** tasks, not implemented skills. Build the earliest eligible priority and record executed checks and blockers on each pass. G2-G5 remain mandatory.
