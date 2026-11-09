# F5 containment verifier review — 2026-10-30

**Result: PASS**  
**Reviewer:** independent security assurance agent  
**Subject:** pending commit for task `F5-CONTAINMENT-VERIFIER`  
**Review scope:** `agent_toolset/runners/codex_cli.py`, `tests/test_runners_assurance.py`, and `docs/OPERATOR_MANUAL.md`

The runner fails closed without both an injected verifier and structured attestation. It requires the verifier to return the exact boolean `True`, translates verifier exceptions into a blocked preparation result, and checks task ID, run ID, resolved worktree, and base commit before process launch. The former caller-controlled boolean/reference assertion no longer qualifies. Tests cover missing verifier, rejected verifier, verifier exception, misbound base commit, and synthetic verifier acceptance. Documentation states that synthetic callbacks test routing only and do not establish real process containment.

Usability note: callers should provide an explicit run ID and bind the attestation to that ID. `prepare()` and `execute()` validate their own attestations; `cancel()` uses the execution run ID. The operator manual now describes this requirement.

The review does not establish actual OS/container containment or real model invocation. These remain external F5 runtime-admission blockers.
