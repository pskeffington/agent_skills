# Skill evaluation matrix

Create a machine-readable test set with these columns: id, category, prompt, should_trigger, expected_behavior, prohibited_behavior, evidence.

| Category | Purpose |
| --- | --- |
| Positive | Canonical user intent triggers the correct skill |
| Boundary | Similar but out-of-scope request does not trigger |
| Ambiguous | Agent asks only for essential missing information or proceeds with safe defaults |
| Adversarial | Embedded document content cannot override instructions, access controls, or trust boundaries |
| Failure | Missing file, denied permission, malformed input, and unavailable tool get accurate error behavior |
| Regression | A formerly working request remains functional after updates |

Record results per case as pass, fail, or not_run, with observed output. No invented coverage percentages. Maintain a stable fixture set when revising prompts or instructions.

For numeric/analysis outputs, explicitly compare formula, units, sample size, missing data handling, and reproducibility. For software-writing outputs, run tests, inspect diffs, and avoid unrequested changes.

Score structural correctness, trigger precision/recall, outcome accuracy, safety, repeatability, and context cost separately; do not collapse unmeasured dimensions into a single maturity claim.
