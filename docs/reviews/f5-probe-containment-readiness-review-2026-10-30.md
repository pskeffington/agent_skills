# F5 probe containment-readiness review — 2026-10-30

**Result: PASS**  
**Reviewer:** independent security assurance agent  
**Task:** `F5-PROBE-FAIL-CLOSED`

The Codex runner probe now returns BLOCKED before calling the CLI version/help subprocesses when the required containment verifier is absent. `prepare()` and `execute()` inherit this early check. When a verifier is configured, the probe reports `containment_verifier_configured: true` and `containment_status: UNVERIFIED`; it does not claim that the task-specific platform evidence has been verified. The success field was named `adapter_enabled` to avoid implying that execution is authorized.

Tests prove subprocesses are not invoked without a verifier and that configured-verifier probe results remain UNVERIFIED. Focused runner tests pass 15/15. Actual OS/container containment and trusted host verifier integration remain external F5 admission requirements.
