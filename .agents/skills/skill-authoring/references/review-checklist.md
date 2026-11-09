# Skill authoring review checklist

## Scope

- Trigger and non-trigger examples are concrete; a false positive would be detectable.
- Inputs, outputs, side effects, and required tools are explicit.
- There is no overlapping skill with the same name or an indistinguishable trigger.

## Architecture

- Entry point is concise with `name` and `description` YAML; detailed context is optional and on demand.
- Local references resolve; vendor-specific instructions are isolated from portable behavior.
- Scripts are justified, reviewed, deterministic, and tested where possible.

## Safety and assurance

- Untrusted content cannot silently authorize tool use, credential access, or network egress.
- Consequential actions require user permission, and no tool capability is invented.
- Static validation, behavior evaluation, client compatibility, and release approval are **different evidence types**.
- Report skipped tests and blockers without upgrading the release state.
