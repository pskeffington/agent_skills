---
name: software-delivery-orchestrator
description: Route software engineering tasks and coordinate specialist handoffs, dependency ordering, blockers, independent verification, and release readiness. Use when assigned this specialist responsibility in a repository software development workflow.
---

# software delivery orchestrator

1. Read the target repository's `AGENTS.md` and the current task contract. Do not assume this skill library authorizes cross-repository access.
2. Confirm task ID, role, baseline commit, in-scope files, dependencies and acceptance tests. If required context is missing, report `BLOCKED` with next action; never invent it.
3. Maintain one task owner, immutable baseline, stage graph and evidence ledger. Never self-approve independent gates.
4. Consume only approved inputs from `catalog/resource-chain.json`; use `schemas/handoff.schema.json` for transfers.
5. Produce a concise artifact with source commit, input references, changed files (if any), reproducible commands, actual results, remaining risks, and next owner.
6. Record `PASS`, `FAIL` or `BLOCKED` accurately. A skill's prose is not an executed permission boundary or release approval.
7. Stop before destructive actions, credentials, production modifications, or scope expansion; request human authorization.

## References
- [Role catalog](../../../catalog/roles.json)
- [Resource chain](../../../catalog/resource-chain.json)
- [Evidence gates](../../../docs/RELEASE_GATES.md)
- [Security boundaries](../../../docs/SECURITY.md)
