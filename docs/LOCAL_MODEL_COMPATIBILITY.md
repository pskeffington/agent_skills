# Local LLM/SLM compatibility — Qwen, GLM and OpenAI-compatible servers

**Status:** DESIGN / INTEGRATION TASKING. This document does not assert that a local model has been installed, queried, or validated. The only implemented execution adapter at this checkpoint is the opt-in Codex CLI adapter, whose real host process-containment gate remains BLOCKED.

## Target and terminology

- **Qwen:** model family, not a transport. Select an exact model/checkpoint and quantify context/tool/structured-output behavior on the serving stack.
- **GLM:** ambiguous family label. **ChatGLM2 / GLM-2** is an older, separately packaged model family; **GLM-4.x and later** are distinct checkpoints with potentially different chat templates and tool support. Never silently reinterpret `GLM2` as a newer GLM model. Require an exact local model identifier before claiming compatibility.
- **Similar models:** Llama, Mistral, Gemma, DeepSeek, Phi, and coding-tuned local checkpoints are eligible only after fixture testing, not by name alone.
- **Serving backends:** Ollama, llama.cpp, LM Studio, vLLM, SGLang, or a compatible offline HTTP service. Transport compatibility is not functional equivalence.
- **Primary transport:** configurable OpenAI-compatible `/v1/chat/completions` and `/v1/models`, localhost by default. A native backend adapter may be needed for older ChatGLM2 or unsupported chat templates. Do not assume tool calls or reasoning output conform to one shared schema.

## Contract boundary

`agent_toolset.runners.base.AgentRunner` defines `prepare(task, capabilities)`, `execute(task, sandbox)`, `cancel(run_id)`. A new `local_inference` adapter must preserve `RunnerResult` and existing task/evidence schemas. Do not embed model-specific instructions inside trusted task contracts.

Separation:
1. **Model:** outputs proposed text, JSON action, or patch; untrusted.
2. **Policy/controller:** validates requested operation against permissions, path scope, task DAG, allowed tools, output schema and budgets.
3. **Execution sandbox:** performs any authorized filesystem/test operation inside a dedicated worktree, subject to F5 process-bound containment and cancellation.
4. **Verifier:** validates evidence, tests and provenance independently of the producing model.

A local inference HTTP response **must never** be directly executed as shell code or Git mutations. Phase L0/L1 permits read-only structured proposals; L2 enables bounded tool use only after containment admission.

## Configuration / discovery

Use `catalog/local-model-profiles.json` as non-authoritative **examples**, not proof of installed models. Per-target operator config supplies:
- `model_id` (exact server-reported ID), `endpoint` (loopback URL), `transport`, `backend`, `checkpoint_revision` and optional `quantization`
- measured `context_tokens`, `max_output_tokens`, `supports_tools`, `supports_json_schema`, `supports_system_role`, `supports_reasoning_separation` (all measured, never inferred from model name)
- `hardware`, `memory_budget_mb`, `deadline_seconds`, `max_parallel`, `temperature` and fixed evaluation seed where supported
- `trust_level`, `allowed_tasks`, `network_policy` and `local_only` (enforced, not just prompt assertions)

No default key or remote endpoint. Reject URLs outside loopback unless the operator explicitly approves a network allowlist. Avoid following redirects to remote hosts. Never log auth tokens or prompt secrets. Avoid auto-downloading model weights.

## Model evaluation gates

| Gate | Check | Minimum requirement |
| --- | --- | --- |
| LM0 discovery | API, exact model ID, template, revision, quantization | Inference server available, stable identity and no silent fallback |
| LM1 parsing | strict JSON proposals, invalid JSON, extra fields, tool call variants | Fail closed on malformed actions and unsupported capabilities |
| LM2 grounding | citation-to-source verification, stale and injected snippets | No source text promoted to policy or commands |
| LM3 coding | bounded patch + unit/integration fixtures; measured success and regressions | No unauthorized paths; full test evidence |
| LM4 budgets | token/VRAM/RAM/timeout/cancel/parallel pressure | Hard ceilings respected and process tree reaped |
| LM5 safety | SSRF/redirect, shell injection, scope escape, malicious tool output | Isolation tests and independent review PASS |
| LM6 parity | compare identical tasks across Qwen, GLM and baseline | Measured accuracy/correctness, speed, memory, failure mode; no brand-based PASS |

A model can be approved for read-only research/doc extraction while coding or tool execution remains BLOCKED. Select routing by *observed competency*, not parameter count. On failure return `BLOCKED`/`FAIL` with provenance; do not silently use cloud fallbacks.

## Roadmap and dependencies

| ID | Priority | Implementation | Acceptance |
| --- | --- | --- | --- |
| LM-00 | P0 | Inventory local backends, checkpoint IDs and hardware; register capabilities | `/v1/models` verified or native discovery probe, no implicit downloads |
| LM-01 | P0 | Implement stdlib client transport and response envelope without running commands | Tests for timeouts, redirects, malformed output, model mismatch, streaming/nonstreaming |
| LM-02 | P1 | Implement runner adapter producing structured **read-only proposals** | RunnerResult contracts, fixture replay, zero write side effects |
| LM-03 | P1 | Qwen profile fixtures via selected Ollama/vLLM/llama.cpp | Real model + parser/template version evidenced; tool/JSON capabilities measured |
| LM-04 | P1 | Exact ChatGLM2 or named newer GLM profile via supported runtime | No automatic GLM-family substitution; feature gaps documented |
| LM-05 | P1 | Eval/routing matrix: Qwen/GLM/other; code, RAG, tests, latency and RAM | Repeated comparisons on identical tasks and budgets; error bars and environment captured |
| LM-06 | P1 | Integrate policy-based tool dispatch and offline fallback | **Depends on F5 containment**, independent security review and negative tests |
| LM-07 | P2 | Operator runbook and pilot one target repo | Reproducible setup, no secret leakage, signed handoff/release boundaries |

Parallel work: LM-00, read-only LM-01, LM-03 fixture design, LM-04 research, and LM-05 benchmark harness may proceed without F5; actual local inference requires an accessible model server. LM-06 cannot advance to executable tools until F5. Never broaden the `agent_skills` scope to unrelated repositories without a separate task contract.

## Operator examples (examples only)

Ollama-compatible:
```
MODEL_ENDPOINT=http://127.0.0.1:11434/v1
MODEL_ID=<exact model reported by /v1/models>
```

vLLM-compatible:
```
MODEL_ENDPOINT=http://127.0.0.1:8000/v1
MODEL_ID=<exact served checkpoint alias>
```

A particular checkpoint may require a model-specific chat template and tool parser. For example, Qwen3 tool calling on vLLM is documented with explicit parser configuration. Probe the deployed version instead of copying flags blindly.

## Vendor docs

- Qwen deployment: https://qwen.readthedocs.io/en/latest/deployment/vllm.html
- vLLM tool parsers: https://docs.vllm.ai/en/latest/features/tool_calling/
- Qwen function calling: https://qwen.readthedocs.io/en/v2.5/framework/function_call.html
