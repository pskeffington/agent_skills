# Standalone Agent Skills build matrix and engineering program

This plan governs Codex construction of 24 **planned** skills in four implementation waves. The existing `skill-authoring` skill is already scaffolded and must remain operational. Planned entries are a queue, **not** a claim that the skills exist or passed tests.

## Design requirements
- One narrow task per skill, with strong positive triggers and explicit negatives.
- Offline-first instructions, local fixtures and optional stdlib scripts. No dependency on other repositories, checked-out projects, downloaded implementations, network-only APIs or hosted model platforms.
- Research claims must cite an entry in `data/literature_matrix.json`; further research is allowed as an authoring activity but results must be saved in a local dated bibliography, licensing respected.
- Agent intelligence is supplied by the host. No assertion that a skill is a neural model, or that its markdown trains weights.
- Any API integration is opt-in and must declare capabilities, permission, failure/timeout behavior and a fully usable offline path.
- No skill may silently execute network requests, modify unrelated repositories, exfiltrate data, perform self-installation or change production configuration.

## Implementation waves
| Wave | Focus | Skills |
| --- | --- | --- |
| 1 | Research, indexing, planning and tests | research-synthesis, evidence-audit, literature-matrix, repository-indexing, task-planning, test-design |
| 2 | Quality, security and release operations | code-review, debugging-triage, release-readiness, security-threat-model, prompt-injection-audit, data-quality-audit |
| 3 | Agent evaluations, feedback and model selection | agent-evaluation, feedback-curation, model-benchmarking, model-routing, prompt-optimization, critique-and-revision, episodic-feedback |
| 4 | Experiments, documentation, incidents and dependency checks | experiment-analysis, documentation-authoring, handoff-checkpoint, incident-triage, dependency-audit |

Each item has a research ID, description, priority and implementation path in `data/skill_build_matrix.json`. Codex must work phase-by-phase and record blockers without claiming release acceptance. First build `research-synthesis`, then `evidence-audit` and `literature-matrix`. Prioritize reusable evaluation infrastructure before adaptive model skills.

## Per-skill deliverable contract
1. `SKILL.md`: portable frontmatter and constrained executable instructions.
2. `references/methods.md`: cited methodology, limits, source versions and why the skill uses each method.
3. `references/examples.md`: two typical uses, negative trigger, one ambiguous case and one failure.
4. `evals/<name>/cases.json`: positive, negative, adversarial, unsupported-tool, malformed, long-context and error-recovery fixtures.
5. Local tests if scripts exist; scripts must be deterministic, bounded and sandbox-friendly.
6. `evidence/<name>/admission.md`: executed commands, environment, failures, assessed gates, and reviewers.
7. Generated catalog and any package manifest checked for deterministic output.

## Research mapping
The matrix includes academic feedback / model selection sources ML-013 through ML-024 and standards/security sources AS-001, OA-003, OA-009 and NIST-011. For specific extracted controls, see `docs/PAPER_PROVISION_AUDIT.md` and `data/paper_provisions.json`. Treat derived recommendations as hypotheses until task-specific validation.

## Blockers and non-goals
- No autonomous cross-repository mutations or external deployments.
- No training or tuning neural weights during this library campaign.
- No claim that offline tests validate client-specific skill loading or inference quality.
- No fabricated tests, paper replications, publisher quotes or benchmark scores.
- No forced external model access to validate the offline contracts.

## Validation and promotion
Run:
```sh
python3 scripts/validate_skills.py
python3 scripts/index_skills.py --check
python3 -m unittest discover -s tests -v
```
Build deterministic evaluation and packaging scripts before advancing G2-G5. Require evidence per gate and pause when external client smoke tests are unavailable.
