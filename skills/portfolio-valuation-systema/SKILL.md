---
name: portfolio-valuation-systema
description: Scan authorized GitHub repositories for engineering and commercial evidence, estimate defensible valuation ranges and update only the private valuation records in pskeffington/Portfolio. Use for portfolio valuation audits, economic maturity assessments, evidence refreshes and cross-repository double-counting reviews.
---

# Portfolio Valuation Systema

## Absolute isolation rule

Source repositories are **read-only evidence sources**. Never write valuations, monetary estimates, financial scores, valuation rankings, financial reports, or valuation-system links to a scanned repository, including its README, issues, pull requests, comments, labels, workflows, release notes and commit messages.

Only `pskeffington/Portfolio` may store valuation outputs, confined to its private valuation system. Public portfolio pages and public AI assistant contexts must never expose private assessments.

## Execution

1. Authenticate and inventory authorized repositories with stable IDs, default branch, exact head SHA, visibility and family membership.
2. Read `pskeffington/Portfolio` README, Valuation Systema dashboard documentation and current schema before updates. Preserve established valuation semantics.
3. Perform read-only inspections: source provenance, licensing/IP ownership signals, reproducible builds, tests/CI, dependency and security state, releases, deployments, maintainability, adoption and evidenced customer or revenue traction.
4. Label each evidence claim observed/reported/inferred/unverified with source URL, timestamp and commit SHA. Unknown is distinct from failed.
5. Score engineering maturity, evidence strength, commercial readiness and maintainability separately, each 0–5 or null when unknown. Attach confidence low/medium/high.
6. Estimate low/base/high financial scenarios only with documented dollar assumptions. Triangulate replacement cost, supported income projections and legitimate market comparables. Use null values when meaningful pricing is unsupported.
7. Create a dependency/family graph: shared code, products, data and infrastructure must not be counted twice. Attribute a shared asset to a single canonical family or explicitly allocate fractions.
8. Validate identity, source SHA, evidence provenance, scenario ordering, allocation fractions, and reviewer gate. Default to dry-run.
9. Update **only** the central Portfolio private valuation records on a proposed reviewed branch. No source-repository writes. No automatic public website edits.
10. Produce an audit summary: repositories scanned, unknowns, evidence changes, valuation scenario sensitivity, overlapping families and reviewer decisions.

## Model

Engineering maturity: 0 idea, 1 prototype, 2 reproducible development, 3 integrated validated release candidate, 4 supported production, 5 mature operating system.

Evidence strength: 0 none, 1 self-report, 2 source-linked, 3 reproducibly validated, 4 independently verified, 5 longitudinally corroborated.

Commercial readiness: 0 no market thesis, 1 thesis, 2 discovery, 3 viable packaging, 4 verified adoption/contracting, 5 verified recurring demand.

Maintainability: 0 unavailable, 1 undocumented, 2 buildable, 3 tested/owned, 4 monitored/security maintained, 5 predictable support costs.

These scores **never directly convert to dollars**. Portfolio economic ranges must state currency, as-of date, method, assumptions, confidence, allocation and non-overlap. Never use stars, commits or LOC as proxies for cash valuation; never claim a financial appraisal or audited value.

## Permission and publication gates

Prefer separate GitHub read-only scanner credentials and Portfolio-only writer credentials. Forbid any mutation in scanned repository endpoints. Keep privately held source and credentials outside any public dashboard payload. Require human review of material estimate changes. The Portfolio repository itself is excluded as an independently valued asset unless explicitly approved.

## Deliverables

- Repository evidence packets with source URLs and head SHAs.
- Private Portfolio valuation updates with low/base/high or null, method and assumptions.
- Non-overlap asset-family reconciliation.
- Audit log with scan timestamp and proposed/approved status.

The distributable skill bundle additionally contains a JSON Schema, methodology reference and a deterministic packet validator.