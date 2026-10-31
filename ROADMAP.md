# Development roadmap

| Phase | State | Deliverable | Acceptance |
| --- | --- | --- | --- |
| A0 research | DONE | primary sources, role/skill/runtime distinction | research links and architecture recorded |
| A1 design | DONE | L0–L5 hierarchy, stage DAG and resource provenance | machine-readable catalogs |
| A2 skills | AUTHORED; STRUCTURALLY VERIFIED | portable orchestrator and specialist skills | role/skill registry and resource-chain checks pass; runtime skill loading/use remains unverified |
| A3 contracts | IMPLEMENTED; VERIFIED | task, handoff and evidence schemas + examples | stdlib validator and 103-test suite pass; current CI run 41160740474 passed |
| A4 automation | CI VERIFIED; BRANCH PROTECTION AND RUNTIME BLOCKED | CI harness and runtime-specific adapters | `structural` workflow passes; GitHub rulesets empty and `main` reports unprotected; Codex CLI 0.147.0 flags present, but Docker daemon unavailable and `sandbox-exec` denied. Independent review found the pre-launch attestation is not bound to the later process handle; see `docs/reviews/f5-process-bound-containment-review-2026-10-31.md`. |
| A5 pilot | LOCAL LIBRARY CHANGES VERIFIED; REAL AGENT PILOT BLOCKED | run a bounded change in one selected target repo | local change evidence exists; actual Codex model execution and trusted host-containment trace remain unavailable |
| A6 production | BLOCKED | controlled deployment integration | owner approval, threat review, rollback, monitoring |

## Next work queue
1. Repository administrator: require the existing `structural` check for the default branch and provide read-back evidence; see `docs/BRANCH_PROTECTION.md`.
2. Host runtime owner: provision a trusted containment executor that launches Codex inside an approved boundary, binds evidence to the actual process/container/job handle, and controls full-tree cancellation. Docker daemon is unavailable and macOS `sandbox-exec` currently returns `Operation not permitted`; the current pre-launch verifier is insufficient for runtime admission. See `examples/f5-process-bound-launch-task.json`.
3. After A4 unblocks, run a real bounded Codex CLI pilot in a dedicated worktree and retain invocation, containment, output, and failure-recovery traces.
4. Keep staging, approval, and rollback evidence human-owned; evaluate staging only after an operator-designated target and explicit authorization exist.
5. Add signed build provenance and per-repository permissions only after an authorized runtime exists.

This commit establishes the control plane; it does not deploy or execute a multi-agent service.
