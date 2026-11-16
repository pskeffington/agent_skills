---
name: scientific-reporting-qa
description: Coordinate evidence-grounded scientific report editing, APA-aware impersonal grammar, R Markdown/Quarto and LaTeX presentation, table and figure QA, compilation, and final page-by-page acceptance. Use when creating, refining, checking, or releasing scientific and biomedical reports, including code-visible knitted statistical analyses and research manuscripts.
---

# Scientific Reporting QA

Use the canonical [R Markdown PDF acceptance workflow](https://github.com/pskeffington/pauls_notes/blob/main/02_biomedical_coding/RMARKDOWN_PDF_PRESENTATION_ACCEPTANCE.md) and [acceptance matrix](references/acceptance-matrix.md). This skill is study-neutral; do not import findings, report text, figures, participant counts, or datasets from individual studies.

## Reporting agent responsibilities

1. **Evidence steward:** Verify exact sources, claim lineage, estimates, denominators and bibliographic attribution. Preserve legitimate citations and data identifiers, but never add unrelated personal identifiers to authored prose.
2. **Methods reviewer:** Check design, independent unit, estimand, model assumptions, multiplicity, reference arm, effect size, intervals and scientific limitations; separate statistical significance from clinical meaning.
3. **Scientific editor:** Apply the Author Grammar contract. No authorial first person or standalone forbidden transition; use APA 7-aware statistical language, impersonal prose, and grammatically appropriate semicolons.
4. **Typesetting engineer:** Keep R chunks and visible code intact; align LaTeX hypotheses, break wide equations, keep tables complete, and control figure placement only where the intended PDF supports the required packages.
5. **Acceptance reviewer:** Distinguish structural lint, actual R execution, successful knit, and rendered-page inspection. Never infer one pass from another.

Compose with installed specialist skills where available: **scientific-narrative** for evidence-backed manuscript construction, **author-grammar** for prose and /grammar, **biomedical-r-wizard** for R/statistics, and **pdfs** for rendered artifact inspection.

## Sequence

1. Retrieve the latest source and intended output; do not mistake a stale PDF for the final knit.
2. Confirm reporting genre, evidence classification, expected code visibility, data permission, and target convention.
3. Run source-level checks, including chunk labels, fences, LaTeX delimiter pairs and obvious presentation regressions.
4. Verify scientific fidelity, then revise prose, tables, equations, figure positioning, and page boundaries.
5. Run R/Quarto with authorized data when possible; record command, versions, warnings, and artifact.
6. Render and inspect every final PDF page for clipping, table splits, orphan headings, displaced figures and reference balance.
7. Re-knit after the final source edit; mark each acceptance gate as passed, failed, or not run with evidence.

## Rules

- Never invent numerical results, citations, peer review, clinical efficacy or successful execution.
- Do not print p = 0.000; distinguish adjusted and unadjusted p-values, individual and simultaneous intervals, and association versus causation.
- Preserve source calculations; format wide tables at display time. Avoid publishing patient-level data.
- If code is meant to appear in a report, do not hide it to shorten pagination. Wrap valid expressions and check actual pages.
- Raw LaTeX page breaks and figure floats require a fresh knit and visual review; a source edit alone is not release acceptance.

## Git ownership and output

The canonical source for this skill is the dedicated `agent_skills` repository, under `.agents/skills/scientific-reporting-qa/`. Do not maintain competing copies in study repositories or methods notebooks. Version all changes through Git; regenerate the repository skill catalog and run its dedicated skill admission tests before labeling a new version accepted. Keep Paul's Notes as the external methods reference, not the skill's authoritative code home.

## Output

Report the modified files, exact observed checks, code execution and knit state, affected pages, remaining issues, and commit/release identifiers when available.