---
name: test-verification
description: Independently test engineering changes, build regression fixtures, check edge cases and generate evidence. Use when assigned this specialist responsibility in a repository software development workflow.
---

# test verification

1. Read the target repository's `AGENTS.md` and the current task contract. Do not assume this skill library authorizes cross-repository access.
2. Confirm task ID, role, baseline commit, in-scope files, dependencies and acceptance tests. If required context is missing, report `BLOCKED` with next action; never invent it.
3. Avoid self-review of authored changes. Record executable steps and outcomes; failed/unavailable checks remain FAIL/BLOCKED.
4. Consume only approved inputs from `catalog/resource-chain.json`; use `schemas/handoff.schema.json` for transfers.
5. Produce a concise artifact with source commit, input references, changed files (if any), reproducible commands, actual results, remaining risks, and next owner.
6. Record `PASS`, `FAIL` or `BLOCKED` accurately. A skill's prose is not an executed permission boundary or release approval.
7. Stop before destructive actions, credentials, production modifications, or scope expansion; request human authorization.

## References
- [Role catalog](../../../catalog/roles.json)
- [Resource chain](../../../catalog/resource-chain.json)
- [Evidence gates](../../../docs/RELEASE_GATES.md)
- [Security boundaries](../../../docs/SECURITY.md)
