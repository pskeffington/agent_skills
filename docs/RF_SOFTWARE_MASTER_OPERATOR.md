# RF software master operator — routing and deployment contract

The RF master operator is a **dispatcher and evidence aggregator**, not an autonomous privileged agent. Its machine-readable registry is `catalog/rf-software-master-operator.json`, with structural contract `schemas/rf-software-master-operator.schema.json`. It coordinates existing generic orchestrator/reviewer roles and the nine specialized RF skills. No source operator/real person is impersonated.

## Graph
```text
Human authorization
    |
Software-delivery orchestrator (existing repo authority)
    |
RF software master operator [scope + catalog resolution]
    +-- Field Linux Builder: pacman profiles, KDE, user timers
    +-- Signal Systems Steward: ABI, releases, compatible components
    +-- Spectrum Architect: IQ DSP topology and simulation
    +-- Receiver Validator: RX device inventory, driver and FFT
    +-- Packet Frame Engineer: soundcard AX.25/APRS fixtures
    +-- Codec Researcher: Codec 2 evaluation
    +-- Digital Voice Integrator: FreeDV audio/CAT (read-only)
    +-- Mesh Link Integrator: LoRa/serial/API (read-only)
    +-- Portable Signal Operator: digital modes, power and timing
    |
Independent test-verification / security review / human release gate
```

## Data relationships
- `agent.id` points to an existing `.agents/skills/<id>/SKILL.md`.
- `component.owner` and `component.reviewer` must point to different agents.
- `component.profile` must exist in `profiles`.
- `component.dependencies` are component IDs or explicitly named external test-fixture tokens (currently `synthetic-iq`).
- `component.hardware_adapters` references normalized IDs; the original human-readable hardware inventory remains `data/rf_hardware_deployments.tsv`.
- `component.installation_policy` explicitly separates pacman candidates, OS-provided services, isolated Python and manual/AUR reviews.
- `acceptance_record: null` prohibits claiming installed or tested status.

## State and permissions
Use `DISCOVERED -> SOURCE_REVIEWED -> PACKAGE_RESOLVED -> PLAN_APPROVED -> DOWNLOADED -> INSTALLED -> SIMULATED_PASS -> HOST_PASS -> HARDWARE_PASS` as *possible* evidence milestones, **not** an unconditional linear pipeline. A simulation can pass without hardware; hardware acceptance does not imply TX permission. `BLOCKED` and `FAILED` may occur at any stage.

The default dispatch is read-only. Only approved `linux_config` workflows can install host software; scripts in this repo do not execute package managers. Never grant unreviewed third-party install scripts privilege. Radio TX, PTT, firmware flashes, kernel changes and privileged service changes remain independently gated.

## Operator input
```json
{
  "target_repository": "pskeffington/linux_config",
  "requested_profile": "sdr-rx",
  "target_os": "Garuda Linux",
  "host_arch": "x86_64",
  "approved_operations": ["plan"],
  "acceptance_tests": ["package-resolution", "synthetic-iq"]
}
```

## Operator output
Return a task contract with source commit, profile closure, package candidates, assigned builder and **different** reviewer, hardware adapters, approval requirements, test commands, expected evidence and blocked states. Do not assert physical inventory without a device record.

## Deployment profile mapping
The master operator expresses **capabilities** whereas `linux_config` currently exposes package manifests `core`, `sdr`, `ham`, `desktop`. Use this mapping only as a proposal pending `linux_config` implementation:

| Master capability | Current linux_config profile | Additional work |
|---|---|---|
| core | core | Existing |
| core-dsp / desktop-dsp | sdr + desktop | Split DSP UI packages from SDR drivers |
| sdr-rx | sdr | Confirm vendor-specific adapter packages |
| packet-rx | ham | Split Dire Wolf / soundcard package group |
| digital-voice | ham / manual | Add Codec 2 and FreeDV verified packaging |
| mesh | manual | Add isolated Meshtastic CLI installer |
| field-digital | ham / manual | Review WSJT-X, JS8Call and time-sync |

No implicit cross-repository mutation is authorized by this mapping.

## Acceptance
Run `python3 scripts/validate_rf_operator.py`, `python3 scripts/index_skills.py --check` and existing repository validators. The first command checks schema-level identities, ownership, uniqueness, dependency closure, policy and the two deployment matrices without installing packages. Full integration acceptance requires a real checkout with recorded logs, and hardware testing remains a later gate.
