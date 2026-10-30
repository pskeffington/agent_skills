# Operator manual

The local toolset is invoked with `python3 -m agent_toolset`. It is a local control plane, not a deployed autonomous service. The default runner is side-effect-free; the Codex adapter only probes its version and cannot launch work.

## Commands

- `doctor`: report Python, journal and runner capabilities.
- `inventory --repo PATH`: list repository files, manifests, instructions, tests, HEAD, and deterministic inventory digest. Ignores `.git`, virtual environments, `node_modules`, and bytecode caches.
- `search --repo PATH --query TEXT [--limit N] [--cache DIR]`: offline lexical search over local text. `--cache` opts into a content-addressed cache; without it, the index is built fresh. Each returned hit includes a path, line and SHA256, and is reverified against the source before output. Retrieved text remains untrusted data.
- `plan contracts.json --state PATH`: validate and add a JSON array of task contracts to the event journal, then report ready tasks. Contract IDs must be new and dependencies must resolve.
- `run task.json`: validate a task and return a deterministic dry-run record. It does not execute task commands.
- `status --state PATH`: reconstruct task and lease state from the journal.
- `verify evidence.json --commit SHA`: validate evidence, fail stale source commits and non-PASS checks.
- `evidence PATH`: parse and print a validated evidence contract.
- `replay --state PATH`: verify the event hash chain and print events.
- `release-check dossier.json`: evaluate G0-G6 and required review, staging, rollback, provenance, and approval references. This is read-only and does not deploy.
- `export --state PATH`: export the verified journal event stream as JSON.

Exit codes: `0` successful command/PASS, `1` verified FAIL, `2` BLOCKED or malformed input. Output is JSON for automation. Journal events are append-only and hash chained; preserve the journal file as evidence. A trailing incomplete record is ignored during replay and truncated before a subsequent append. Journal appends serialize through a POSIX advisory file lock before deriving sequence numbers; on platforms without `flock`, only same-instance thread serialization is guaranteed. Keep journal files in a trusted local directory; hash chaining detects edits but is not a digital signature or protection against an attacker who can rewrite the entire journal.
- `ci-ingest run.json --commit SHA [--required-check NAME]`: classify an exported GitHub Actions workflow run for the exact commit. This is offline ingestion; it does not fetch GitHub. Missing, incomplete or stale runs do not pass.
- `security-summary findings.json [--fail-on high]`: summarize an exported `{ "findings": [...] }` document. Missing or malformed exports are BLOCKED; findings at or above the configured threshold fail.

Release dossier format: each `G0`–`G6` gate is `{ "status": "PASS", "evidence_ref": "...", "reason": "..." }`. `independent_review`, `security_review`, `staging`, and `approval` are objects that each include `evidence_ref`, `subject_commit`, `artifact_sha256`, and `invocation_id`. Each subject must match the dossier commit and artifact digest. Reviewer and security invocations must differ from the approver. Also provide `target_environment`, `rollback_ref`, and nonempty `check_provenance`. This validates linkage and presence; it cannot cryptographically authenticate an external reference. Operators must verify referenced evidence in its authoritative system.

## Build a standalone artifact

Run `python3 scripts/build_zipapp.py /path/to/agent-toolset.pyz`. The builder uses only Python's standard library, includes only `agent_toolset` source modules, and writes stable archive timestamps and ordering for reproducible output. Verify with `python3 /path/to/agent-toolset.pyz doctor` and calculate SHA256 with `sha256sum` (or the platform equivalent). Preserve the exact artifact and its digest in the release dossier. Do not publish or deploy it from this command.
