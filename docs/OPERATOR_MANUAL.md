# Operator manual

The local toolset is invoked with `python3 -m agent_toolset`. It is a local control plane, not a deployed autonomous service. The default runner is side-effect-free; the Codex adapter only probes its version and cannot launch work.

## Commands

- `doctor`: report Python, journal and runner capabilities.
- `inventory --repo PATH`: list repository files, manifests, instructions, tests, HEAD, and deterministic inventory digest. Ignores `.git`, virtual environments, `node_modules`, and bytecode caches.
- `search --repo PATH --query TEXT [--limit N] [--cache DIR]`: offline lexical search over local text. `--cache` opts into a content-addressed cache; without it, the index is built fresh. Each returned hit includes a path, line and SHA256, and is reverified against the source before output. Retrieved text remains untrusted data.
- `plan contracts.json --state PATH`: validate and add a JSON array of task contracts to the event journal, then report ready tasks. Contract IDs must be new and dependencies must resolve.
- `run task.json`: validate a task and return a deterministic dry-run record. It does not execute task commands.
- `status --state PATH`: reconstruct task and lease state from the journal.
- Cancelling a task with an active lease requires the execution adapter to verify that its worker has stopped; the scheduler does not terminate workers itself.
- `verify evidence.json --commit SHA`: validate evidence, fail stale source commits and non-PASS checks.
- `evidence PATH`: parse and print a validated evidence contract.
- `replay --state PATH`: verify the event hash chain and print events.
- `release-check dossier.json [--approval-trust-store PATH]`: evaluate G0-G6 and required review, staging, rollback, provenance, and approval evidence. This is read-only and does not deploy. Without a trusted approval key store, an otherwise complete dossier remains BLOCKED.
- `approval-payload dossier.json`: emit the canonical approval fields as raw UTF-8 bytes for offline detached signing. It never reads a private key or changes the dossier.
- `export --state PATH`: export the verified journal event stream as JSON.

Exit codes: `0` successful command/PASS, `1` verified FAIL (including stale or contradictory release attestations), `2` BLOCKED or malformed/missing prerequisites. Output is JSON for automation. Journal events are append-only and hash chained; preserve the journal file as evidence. A trailing incomplete record is ignored during replay and truncated before a subsequent append. Journal appends serialize through an advisory file lock before deriving sequence numbers. Keep journal files in a trusted local directory; hash chaining detects edits but is not a digital signature or protection against an attacker who can rewrite the entire journal.
- `ci-ingest run.json --commit SHA [--required-check NAME]`: classify an exported GitHub Actions workflow run for the exact commit. This is offline ingestion; it does not fetch GitHub. Missing, incomplete or stale runs do not pass.
- `security-summary findings.json [--fail-on high]`: summarize an exported `{ "findings": [...] }` document. Missing or malformed exports are BLOCKED; findings at or above the configured threshold fail.

Release dossier format: each `G0`–`G6` gate is `{ "status": "PASS", "evidence_ref": "...", "reason": "..." }`. `implementation`, `independent_review`, `security_review`, `staging`, and `approval` are objects that each include `evidence_ref`, `subject_commit`, `artifact_sha256`, and `invocation_id`. Approval additionally requires `decision: "APPROVE"`, `approver_id`, `authority_ref`, `signature_algorithm: "openssl-dgst-sha256"`, and a base64 `signature`. Each subject must match the dossier commit and artifact digest. Reviewer and security invocations must differ from the implementer and the approver. Also provide `target_environment`, `rollback_ref`, and nonempty `check_provenance`.

The optional trust store is an operator-managed JSON file outside the repository with mode not writable by group or others:

```json
{"schema_version":"1.0.0","approvers":{"operator-42":{"authority_ref":"change-control:42","public_key_pem":"-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n"}}}
```

The signer signs the UTF-8 canonical JSON object containing all approval fields except `signature` (sorted keys, compact separators), using SHA-256 and the private key corresponding to that allowlisted public key. Accepted keys are RSA with at least 2048 bits or ECDSA on prime256v1/P-256, secp384r1/P-384, or secp521r1/P-521. Generate the exact bytes with `python3 -m agent_toolset approval-payload dossier.json > approval-payload.json`; sign those bytes offline with `openssl dgst -sha256 -sign approver-private.pem -out approval.sig approval-payload.json`, then base64-encode the signature into the dossier's `approval.signature`. Never put the private key in the repository or passphrase on a command line. Pass the trust store with `--approval-trust-store`; the evaluator checks signer identity, authority reference, key policy, signature, commit, and artifact digest. Keep the trust store and key authorization process under release-operator control. OpenSSL and OS `O_NOFOLLOW` support must be available; if either is unavailable, verification is BLOCKED. This verifies the local signature against the configured allowlist; operators still need to validate the allowlist's authority and all referenced CI, review, staging, and security evidence in their source systems.

## Build a standalone artifact

Run `python3 scripts/build_zipapp.py /path/to/agent-toolset.pyz`. The builder uses only Python's standard library, includes only `agent_toolset` source modules, and writes stable archive timestamps and ordering for reproducible output. Verify with `python3 /path/to/agent-toolset.pyz doctor` and calculate SHA256 with `sha256sum` (or the platform equivalent). Preserve the exact artifact and its digest in the release dossier. Do not publish or deploy it from this command.

## Retrieval evaluation and benchmark

Run `python3 scripts/evaluate_rag.py` for labeled fixture metrics. Run `python3 scripts/benchmark_rag.py --repetitions 5 --output PATH` to record cold index build, warm retrieval, validated cache load, SHA invalidation, and Python allocation peaks. The benchmark is observational, not a pass/fail performance claim; compare only reports with matching environment and corpus fingerprint.
