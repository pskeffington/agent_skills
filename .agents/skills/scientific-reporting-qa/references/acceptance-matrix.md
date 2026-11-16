# Scientific reporting acceptance matrix

A methods-only checklist; no example study findings belong here.

| Gate | Required evidence | Typical failure |
| --- | --- | --- |
| E0 Scope | Document purpose, intended readership, canonical source revision and authorized data | Reviewing the wrong version |
| E1 Evidence | Claims and numbers matched to source, design and uncertainty | Invented or inflated inference |
| E2 Editorial | Impersonal voice, APA-aware statistics, citation reconciliation, valid punctuation | Unnecessary first person or malformed p-value |
| E3 Structure | Unique R chunk labels, balanced fences and displayed mathematics | Broken Rmd or LaTeX |
| E4 Execution | Actual R/Quarto run, exact command, exit code, dependencies and data approval | Lint mislabeled a successful analysis |
| E5 Knit | PDF/HTML generated from the final source and warnings inspected | Stale artifact treated as current |
| E6 Visual | Full page-image review for figures, tables, equations, sections and references | Clipped graphic or orphaned heading |
| E7 Release | Commit, artifact checksums, open risks and sign-off | Unverified publication readiness |

## Layout rules

Use aligned math for multi-line hypotheses and estimators; avoid single-line equations that overrun the text area. Add justified vertical spacing, rather than shrinking all notation. Keep R source and its plot together where practical; optional PDF float controls need the matching LaTeX packages. Use a single-backslash raw TeX command in the actual Rmd; source serialization may need additional escaping when files are generated programmatically. Compact tables at display time, not in model objects. Mark whether a confidence interval is individual or simultaneously adjusted. Render every page after a final source edit. Prefer impersonal scientific prose, semicolons between related independent clauses, and explicit uncertainty.

## Handoff

Record source SHA, changes, scientific methods reviewed, executed tests, compilation result, page count, page-image checks, limitations and final acceptance state. A not-run gate must remain not run.