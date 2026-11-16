# Scientific reporting evidence handoff contract

This is a study-neutral reporting quality contract. The canonical optional workflow is [scientific reporting chain](https://github.com/pskeffington/agent_skills/blob/main/catalog/scientific-reporting-chain.json). Do not include study data, case findings, source text, identifying participant information, or copyrighted material in this skill library.

## Handoff envelope

The reporting reviewer produces one machine-readable JSON dossier with:

- `schema_version`: `1.0.0`
- `task_id`: stable task reference
- `source_repository`: repository path or URL, not implicit permission to access it
- `source_commit`: exact 40-character source Git commit
- `artifact_sha256`: lowercase 64-character PDF/HTML artifact SHA-256 when compiled
- `gates`: E1–E8, each with `status`, `source_commit`, `evidence_ref`, `method`, and `reason`
- `open_issues`: unresolved findings
- `reviewer_role`: `scientific-reporting-reviewer`
- `reviewer_independent`: Boolean attestation that this reviewer is not self-approving a release
- `release_recommendation`: `PASS` or `BLOCKED`

Each gate status must be `PASS`, `FAIL`, or `BLOCKED`. Omitted or unrun mandatory gates are `BLOCKED`. For `PASS`, a nonblank evidence reference and method are mandatory; the gate's source commit must match the envelope. For a PDF/HTML output, E6 (compile), E7 (visual), and E8 (handoff) must point to the exact output artifact digest. Without a compiled artifact, those gates remain blocked. Every upstream gate must pass for an affirmative reporting release recommendation. Findings and evidence refs remain in the task repository or authorized evidence system, not in this reusable library.

## Isolation from software release gates

The reporting branch is opt-in for reporting deliverables. It feeds independent review evidence to the orchestrator and release controller; it does not replace G0–G6 software release controls, grant authorization, sign release approvals, or deploy/publish artifacts. A green reporting dossier is *necessary but not sufficient* for release when the reporting branch applies. A reviewer cannot use its own attestation as external human approval.

## Local acceptance command

`python3 .agents/skills/scientific-reporting-qa/scripts/validate_reporting_handoff.py path/to/dossier.json`

Exit 0 means the reporting dossier is structurally complete and its stated PASS gates are evidence-linked. It does **not** prove the external evidence references are valid, confirm the statistics, reproduce the knit, verify page images, or authorize release. Exit nonzero is a blocked/failing reporting handoff. Review source revision concordance and evidence independently.