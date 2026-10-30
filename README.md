# Software Development Agent Skills

A repository-local, portable hierarchy of specialized software-development **skills**, a resource/dependency chain, and evidence-first release gates. Skills are instructions—not automatically running background agents. The chosen runtime (Codex, Copilot, or an explicitly configured agent SDK) must implement delegation, tools, isolation, and approvals.

## Start here

1. Read [AGENTS.md](AGENTS.md) for repository-wide rules.
2. Consult [architecture](docs/ARCHITECTURE.md), [resource chain](docs/RESOURCE_CHAIN.md), and [acceptance gates](docs/RELEASE_GATES.md).
3. Select a role from [catalog/roles.json](catalog/roles.json). Portable skills live in [`.agents/skills/`](.agents/skills).
4. Create a bounded task using [task-contract schema](schemas/task-contract.schema.json). Record handoffs and evidence with their schemas.
5. Run `python3 scripts/validate.py` and `python3 -m unittest discover -s tests -v` after editing (Python standard library only).

## Delivery model

**Human authority (L0)** → **Orchestrator (L1)** → **Research / planning / architecture (L2)** → **Implementation / integration / documentation (L3)** → **Independent verification / review / security (L4)** → **Release-readiness controller (L5)** → **explicit human authorization for production**.

Small jobs may combine analysis and implementation in one session; independent gates remain separate. See [ROADMAP](ROADMAP.md) for adoption work and [RESEARCH](docs/RESEARCH.md) for standards and provenance.

## Non-goals

No daemon, scheduler, autonomous repository-wide deployment, privileged agent runtime, third-party dependency installer, or implicit right to access another repository is created by these files. They provide enforceable-by-validation contracts and human-readable operating policy; external execution must be configured separately.

License: see [LICENSE](LICENSE).
