# F5 process-bound containment review — 2026-10-31

**Result: BLOCKED for runtime admission**  
**Reviewer:** independent containment-boundary reviewer  
**Subject:** Codex CLI adapter at commit `12f98fd3f12a829ca19bfdca4d3d2281bad2cd21`  
**Review scope:** `agent_toolset/runners/codex_cli.py`, `tests/test_runners_assurance.py`, `docs/OPERATOR_MANUAL.md`, and F5 task/evidence records

## Finding

**High — attestation does not bind the launched process to containment.** `_validate_workspace()` calls an injected boolean verifier on task ID, run ID, resolved worktree, and base commit before execution. `execute()` later starts Codex directly with `subprocess.Popen()`. The verifier is not given the resulting PID or a containment handle, and the adapter does not delegate process creation or tree termination to a trusted containment executor. The attestation therefore proves only that a caller-supplied pre-launch record was accepted; it does not prove that this Codex process entered a kernel-enforced boundary.

Codex `--sandbox workspace-write` and POSIX process-group termination provide useful controls, but do not establish external OS/container containment. The Windows termination branch handles only the leader process. Existing synthetic verifier tests exercise routing and fail-closed behavior; they do not prove platform containment, as the existing docs correctly state.

## Evidence

- Source: `agent_toolset/runners/codex_cli.py` lines 150–163 verify the attestation; lines 243–245 launch directly with `Popen`; lines 422–460 handle process termination.
- Tests: `tests/test_runners_assurance.py` inject synthetic verifier callbacks, including callbacks that return `True`; these tests do not launch a real model or platform sandbox.
- Host probe: `docker info` exited 1 because `/Users/null/.docker/run/docker.sock` was absent. `sandbox-exec` exited 71 with `sandbox_apply: Operation not permitted`.
- No real Codex model invocation or containment measurement was performed.

## Required next action

An authorized host-runtime integrator must provide a trusted containment executor that starts Codex inside the platform boundary and returns a handle/evidence bound to the actual launched process or container/job object. The executor must also terminate and verify the complete contained process tree on timeout/cancel. Add platform integration tests that verify boundary enforcement and lifecycle behavior. Keep F5 runtime admission BLOCKED until those tests and real host evidence pass.

No source code was changed by this review. No credentials, host settings, staging, or deployment actions were used.
