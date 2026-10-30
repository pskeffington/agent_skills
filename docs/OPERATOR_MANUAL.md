# Operator manual

The local toolset is invoked with `python3 -m agent_toolset`. It is a local control plane, not a deployed autonomous service. The default runner is side-effect-free; the Codex adapter only probes its version and cannot launch work.

## Commands

- `doctor`: report Python, journal and runner capabilities.
- `inventory --repo PATH`: list repository files, manifests, instructions, tests, HEAD, and deterministic inventory digest. Ignores `.git`, virtual environments, `node_modules`, and bytecode caches.
- `plan contracts.json --state PATH`: validate and add a JSON array of task contracts to the event journal, then report ready tasks. Contract IDs must be new and dependencies must resolve.
- `run task.json`: validate a task and return a deterministic dry-run record. It does not execute task commands.
- `status --state PATH`: reconstruct task and lease state from the journal.
- `verify evidence.json --commit SHA`: validate evidence, fail stale source commits and non-PASS checks.
- `evidence PATH`: parse and print a validated evidence contract.
- `replay --state PATH`: verify the event hash chain and print events.
- `release-check dossier.json`: evaluate G0-G6 and required review, staging, rollback, provenance, and approval references. This is read-only and does not deploy.
- `export --state PATH`: export the verified journal event stream as JSON.

Exit codes: `0` successful command/PASS, `1` verified FAIL, `2` BLOCKED or malformed input. Output is JSON for automation. Journal events are append-only and hash chained; preserve the journal file as evidence. A trailing incomplete record is ignored during replay and truncated before a subsequent append. Keep journal files in a trusted local directory; hash chaining detects edits but is not a digital signature or protection against an attacker who can rewrite the entire journal.
