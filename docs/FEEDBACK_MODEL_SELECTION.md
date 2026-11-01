# Research implementation plan: feedback and model routing

## Distinguish mechanisms

- **Skill revision:** edits to SKILL.md and references; no change to model weights.
- **Inference-time feedback:** bounded critique/revise and episodic memory; no change to weights.
- **Preference optimization:** DPO/RLHF/RLAIF using curated comparison data and an explicitly separate training pipeline; version weights, datasets and reward assumptions.
- **Adaptive routing:** per-task choice among approved models; no silent deployment of candidate models.

## Minimal measurable feedback record

`case_id, skill_digest, prompt_digest, task_family, model_id, model_snapshot, candidate_ids, rubric_version, preference_label, annotator_type, judge_id, uncertainty, split, safe_to_train, recorded_at`.

Exclude raw credentials, regulated personal information, and unauthorized user content. Require immutable dataset and policy snapshots. Store only necessary training-approved records.

## Router acceptance experiment

A baseline routes all eligible examples to the approved strong model. Candidate router must satisfy a predefined noninferiority quality margin, calibrated uncertainty, safe escalation, per-task floor, p95 latency and budget thresholds. Evaluate on untouched holdouts, distribution shifts, adversarial inputs, and withheld tool outputs. Report confidence intervals and paired comparisons; do not use winning examples from tuning for final acceptance.

## Feedback loop acceptance experiment

Compare one-pass baseline, bounded self-critique, and independent critique. Score grounded correctness with executable or human-reviewed outcomes, not only judge preference. Cap loop iterations and total budget. Detect reward hacking, verbosity bias, unsafe tool suggestions and repeated-error loops.

## Production boundary

No silent weight updates, self-modifying skills, unreviewed cross-repo writes or unrestricted external APIs. Shadow -> canary -> promoted deployment with version pins, owner sign-off, rollback and observation windows.
