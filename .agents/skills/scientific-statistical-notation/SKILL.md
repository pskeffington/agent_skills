---
name: scientific-statistical-notation
description: Standardize statistical notation, biomedical test symbols, effect estimates, confidence intervals, p-values, LaTeX and manuscript typography. Use for R Markdown, scientific manuscripts, statistical tables and figures; not just decimal-to-power-of-ten conversions.
---

# Scientific Statistical Notation

Read the current [Paul's Notes notation and reporting standard](https://github.com/pskeffington/pauls_notes/blob/main/03_learning/bio_stats/SCIENTIFIC_STATISTICAL_REPORTING_STANDARDS.md#1a--statistical-notation-and-mathematical-typography) before substantive edits. This is the authority for test-by-test notation and formatting; do not duplicate its full matrix here. Coordinate with scientific-reporting-qa for manuscript and PDF acceptance, and biomedical-r-wizard for actual modeling and R computations.

1. Define study design, population, independent unit, variable scale, estimand, reference and contrast direction before presenting statistics. Keep group denominators and exclusions explicit.
2. Distinguish population parameters (μ, β, π) from estimators (x̄, β̂, p̂); SD from SE; confidence from credible intervals; risk, odds, incidence-rate, and hazard ratios.
3. Use italic Latin symbols for *t*, *F*, *r*, *p*, *n* where publication style supports it; correctly typeset χ² and subscripts. Welch degrees of freedom may be fractional. Use p = .042 or p < .001, never p = .000; identify adjusted p, multiplicity and CI family.
4. Match symbols, units, estimate direction, reference arm, event class, time scale and CI to the verified computational objects. Do not generate missing effects or scientific conclusions from formatting alone.
5. Apply APA 7 as a default, subject to the journal or rubric. Distinguish CONSORT, STROBE, STARD, TRIPOD+AI, REMARK and PRISMA study-design requirements.
6. Maintain concise evidence-led prose, human-readable R code comments, and correct LaTeX math. Preserve Paul's Notes coursework R quantile type 2 when applicable. Treat syntax inspection, computation, knit and visual verification as separate statuses.

Do not copy patient-level data, source report text or study findings into this portable skill. Report exact edited files and actual observed tests; do not claim deployed ChatGPT installation merely because GitHub changed.
