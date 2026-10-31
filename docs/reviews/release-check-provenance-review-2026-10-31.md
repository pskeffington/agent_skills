# Independent review: structured release check provenance

**Result: PASS**  
**Reviewer:** independent code/security reviewer  
**Baseline:** `83fed955abbae0a6f5c5c7c06b2202158942ac7a`  
**Task:** `F8-STRUCTURED-CHECK-PROVENANCE`

The release evaluator requires a nonempty provenance list, rejects malformed records and non-PASS outcomes, and marks commit or artifact subject mismatches as contradictions. Empty lists remain schema-valid for synthetic blocked dossiers, while the evaluator still blocks them. The breaking provenance shape advances the dossier version to `3.0.0`, and the approval binding continues to cover provenance changes. Documentation correctly says these fields do not authenticate external CI output.

No release-admission bypass was found. Focused release/approval tests passed 17/17 and repository structural validation passed during review. Full suite after the final test addition passed 104/104. No external CI, staging, or deployment evidence is implied by this review.

**Remaining limitation:** evidence references and output digests are subject-bound metadata; operators must still retrieve and authenticate external CI/check outputs in their source systems.
