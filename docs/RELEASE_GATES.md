# Release acceptance gates

Each gate needs artifact evidence, not just a written claim. A later gate cannot compensate for an earlier failed gate.

| Gate | Criteria | Evidence | State at bootstrap |
| --- | --- | --- | --- |
| G0 — Source/index foundation | Repo layout, source links, dated evidence matrix, policy, threat model | README; docs; data | Implemented; review required |
| G1 — Structural integrity | Every skill passes name/frontmatter/link/size checks; catalog generation is deterministic; unit tests pass | `validate_skills.py`; `index_skills.py --check`; tests; CI run | Local validation targeted |
| G2 — Safety | Provenance checked; code-reviewed scripts; prompt-injection and least-privilege cases pass; secrets review | documented review and attack fixtures | Blocked: fixtures/review missing |
| G3 — Behavioral quality | Realistic positive/negative trigger evals and failure-handling evals pass; baseline recorded | eval results per skill | Blocked: harness missing |
| G4 — Client compatibility | Package opens and runs in each **claimed** target client; assumptions documented | per-client smoke-test logs | Blocked: not tested |
| G5 — Distribution | Pinned version, license review, archive integrity, approvals, rollback instructions | release manifest, reviewer approval | Blocked: not released |

**Failure rules:** Index drift, invalid metadata, broken local references, test failure, unauthorized outbound side effect, unexplained tool calls, or missing evidence block promotion. No automatic merges or production publication. CI green covers only what CI actually checks; it is not a substitute for G2–G5.
