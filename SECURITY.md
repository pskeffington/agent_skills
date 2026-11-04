# Security policy and responsible disclosure

Do not commit credentials, user data, proprietary instructions, or unreviewed remote scripts. A `SKILL.md` is an instruction surface, not an authorization grant. Script execution and outbound requests require normal host permissions and task-appropriate user approval.

For a suspected vulnerability, use the GitHub repository's private vulnerability reporting facility if enabled; otherwise contact the maintainer privately. Do not publish exploit payloads or secret values in issues. This repository intentionally runs validation without network calls or deployment secrets.

Controls and gaps are tracked in [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md). Static lint is only a structural guard and **does not prove a skill safe**.
