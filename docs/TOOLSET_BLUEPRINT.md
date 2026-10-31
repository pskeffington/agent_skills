# Complete software-development agent toolset blueprint

## Layers
| Layer | Module | Responsibility | Boundary |
| --- | --- | --- | --- |
| 0 | Operator | explicit authorization, target scope, stop/approve | no delegated release consent |
| 1 | Coordinator | DAG, scheduling, provenance, retry budget | no independent self-approval |
| 2 | Specialized roles | research, architect, planner, coder, integrator, documentation | read/write scoped to task |
| 3 | Independent assurance | verifier, security, reviewer | no authoring of reviewed change |
| 4 | Local tool adapters | Git, filesystem, test executor, index, CI reader, Codex runner | allowlist + capability check |
| 5 | Durable storage | JSON contracts, append-only journal, content hashes | replay and audit |
| 6 | Release management | attest candidate, staging, approvals, rollback | production is a distinct authorized action |

## Local package proposal
```text
agent_toolset/
  __init__.py
  cli.py
  config.py
  contracts.py
  scheduler.py
  state.py
  journal.py
  inventory.py
  routing.py
  runners/base.py
  runners/dry_run.py
  runners/codex_cli.py       # optional adapter; never silent execution
  tools/git_read.py
  tools/fs_policy.py
  tools/test_executor.py
  tools/ci_reader.py         # optional GitHub capability
  assurance/evidence.py
  assurance/security.py
  assurance/release.py
tests/
  fixtures/
  test_cli.py
  test_contracts.py
  test_scheduler.py
  test_journal.py
  test_permissions.py
  test_release.py
```

## State machine
`QUEUED → READY → RUNNING → REVIEW → DONE`; `RUNNING → BLOCKED|FAILED`; `BLOCKED → READY` only with documented cause resolution. CANCELLED is terminal. Transitions must be validated atomically; a crash cannot make RUNNING magically become DONE.

## Interface contracts
- `AgentRunner.prepare(task, capabilities)`, `AgentRunner.execute(task, sandbox)`, `AgentRunner.cancel(run_id)`; return structured status, provenance and exit code. Propose exact signatures and tests before implementation.
- `Tool.execute(spec)` receives typed, allowlisted arguments, timeouts, cwd and access class; never interpolates a shell command from a task string.
- `Evidence` ties check identity, command, outcome, output reference, commit, environment and artifact digest. Prior evidence becomes stale when the evaluated subject changes.
- `Journal` appends sequence number, task ID, event type, timestamp, input hash and transition result. Recover interrupted runs by replay; include tamper detection through hash chaining.
- `Lease` locks task/worktree ownership for bounded durations. Expiry only permits reassignment after checking current process/write state.

## Resource priority
Human instruction → target repo instructions → checked-in source/tests/lockfiles → locally approved references → explicitly authorized external sources. Always detect lower-trust prompt injection. Refuse unscoped cross-repository access.

## Performance
- Keep one active writer per file; parallelize only independent read-only tasks or disjoint worktrees.
- Short context payloads built from baseline hash and relevant paths. No wholesale log injection into prompts.
- Cache index by HEAD SHA, invalidate on file changes and evidence state changes.
- Track task elapsed time, context size estimate, retries and checks per task for later tuning; never optimize away required gates.

## Portability
Portable `.agents/skills/` contains role instructions. Runtime adapters must be optional. The Python control plane cannot guarantee Codex platform permissions: tests and sandbox controls belong to the executor configuration.
