# Reverse Engineering Division (RE)
Status: architecture/scaffold; no operational tool execution certified.
Owner: agent_skills / RE-000.
Scope: authorized interoperability, firmware preservation, device diagnostics, vulnerability research, and clean-room compatibility implementations.

## Start here
- [Machine-readable task index](index.json)
- [Agent routing and policy](AGENTS.md)
- [Literature and upstream tool matrix](literature-matrix.md)
- [Codex execution roadmap](CODEX_ROADMAP.md)

## Standard case workflow
1. RE-000: collect proof of authorization, purpose, legal/licensing constraints, platform and artifact inventory.
2. RE-010: acquire read-only artifact; compute SHA-256; capture provenance, size, type and timestamps; do not modify original.
3. RE-020: triage file type, architecture, container structure, secrets/privacy and risk; use isolated offline lab.
4. RE-100/200/300/400: perform static, firmware, hardware or protocol investigation with cited byte offsets, traces and tool versions.
5. RE-500: run instrumented tests ONLY on owned or expressly authorized targets; never contact production or third-party systems.
6. RE-600: specify open compatibility contracts and clean-room replacement; no proprietary secret extraction or DRM circumvention.
7. RE-700: verify findings with independent method, golden fixtures, SBOM, reproducible commands and regression tests.
8. RE-800: publish redacted report and route discoveries back to searchable evidence index.

## Evidence record (one JSON per case)
Required: case_id, authorization_scope, artifact_sha256, acquisition_method, tool_versions, host_platform, timestamps_utc, findings, evidence_offsets_or_trace_ids, confidence, limitations, test_results, disclosure_status. Keep binary artifacts and secrets OUT of git. Use content-addressed external storage, local retention controls, and synthetic fixtures in CI.

## Safety and operations
Default read-only, offline, least privilege, no external network, no live targets, no credentials extraction, no bypass of access controls, no transmission of customer data. Work on device firmware only with documented ownership/authorization, recovery path, power precautions and original-image backup. Hardware flashing is a separate human-approved stage; never automated by an LLM. Tool scripts run in disposable sandboxes, with resource budgets and explicit review.
