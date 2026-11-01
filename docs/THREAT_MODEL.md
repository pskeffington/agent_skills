# Initial threat model

## Trust boundaries

A skill file is untrusted until reviewed and admitted. An external website, issue, tool response, MCP-served skill, nested reference, script, model-generated output, and imported repository are data, not authority. Host permissions and user approvals remain independent of written skill instructions.

| Risk | Example | Control | Evidence gap |
| --- | --- | --- | --- |
| Indirect prompt injection | Reference text instructs agent to ignore user instructions | Isolate external text; limit permissions; require confirmation for sensitive actions | adversarial fixtures pending |
| Excessive agency | Skill attempts unsolicited GitHub writes or network calls | Narrow scope, explicit allowed effects, human review | runtime approval smoke test pending |
| Dependency/supply chain | Imported helper installs remote code | Stdlib core; no third-party CI actions; provenance/license review | package attestations pending |
| Data exfiltration | Skill sends keys or documents to an endpoint | No secrets in repo; deny undeclared outbound connections | secret scanning policy pending |
| Tool-result laundering | Tool output impersonates agent policy | Treat tool output as untrusted facts only | negative evaluation pending |
| Archive/path traversal | Export unpacks outside intended skill root | Planned package path validation | packaging tool pending |
| Stale standard | Skill relies on superseded instructions | Dated literature source record, review on update | scheduled review not configured |

Static checks enforce syntax and consistency; they cannot prove a workflow safe, accurate, or compatible. A reviewed script still needs execution sandboxing and least-privilege permissions in the consuming environment. Reference: [OpenAI prompt injection](https://openai.com/safety/prompt-injections/), [OpenAI agent safety](https://developers.openai.com/api/docs/guides/agent-builder-safety), [GitHub Actions security](https://docs.github.com/en/code-security/tutorials/secure-your-organization/protect-against-threats), and [MCP skills extension security](https://skills.extensions.modelcontextprotocol.io/specification/stable/skills).
