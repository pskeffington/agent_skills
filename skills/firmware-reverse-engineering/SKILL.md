---
name: firmware-reverse-engineering
description: Analyze firmware images and embedded-device protocols in an evidence-first, reproducible way. Use for user-owned smart TVs, soundbars, IoT devices, binary formats, firmware update archives, boot chains, local control discovery, and safe offline reverse-engineering research.
---

# Firmware reverse engineering

## Intake
1. Record device manufacturer, exact model, hardware revision, SoC, bootloader/firmware version, interfaces, recovery path, and user-authorized scope. Unknown values remain explicitly unknown.
2. Acquire firmware only through lawful, authorized sources. Store source URL, capture date, SHA-256 hash, size, license status, and chain of custody. Never commit proprietary blobs, credentials, serials, or secrets.
3. Treat images as untrusted inputs. Prefer isolated disposable analysis environments, offline tooling, no outbound connections, and restricted privileges.

## Analysis workflow
1. **Triage:** identify container, compression, architecture, entropy, filesystem markers, signatures, and update structure. Use multiple independent tools; record each result as an observation, inference, or hypothesis.
2. **Extract:** use Binwalk, file-format readers or manual offsets only with reproducible commands and hashes. Verify recovered contents; guard against path traversal, decompression bombs, and executable post-extraction hooks.
3. **Static:** select Ghidra or Rizin/radare2 according to architecture and task. Export function/strings/service inventories and pseudocode with analyst confidence levels; do not equate compilable-looking output to functional correctness.
4. **Firmware ecosystem:** consider EMBA for firmware-component risk analysis. Use FirmAE/QEMU only after image/sandbox compatibility review. Treat emulation success as an experiment, not proof of safe hardware behavior.
5. **Protocol:** inspect passive IR, HDMI-CEC, Bluetooth, USB, or network traces as supported by the exact device. Map reproducible commands; do not assume published protocols apply across firmware versions.
6. **Correlate:** write evidence-linked maps for boot chain, processes, update logic, account dependencies, audio pipeline, OTA, and recoverability. Track unanswered questions.
7. **Bench gates:** require exact-model recovery evidence, backups and rollback before discussing flash installation. Default to reversible external control or supported software configuration.

## Deliverables
Produce `artifacts/firmware_manifest.json`, `reports/triage.md`, `reports/evidence_matrix.md`, `reports/control_protocol.md`, and `reports/flash_gate.md` as applicable. Distinguish complete, partial, blocked and untested. Validate against references/evidence-schema.md.

## Agent division
- Intake agent: provenance and target identification.
- Binary triage agent: format, filesystem, SBOM indicators.
- Static RE agent: functions, architecture and component dependencies.
- Protocol agent: passive traces and local control.
- Verification agent: reproduction, competing hypotheses and negative tests.
- Recovery/safety agent: stop/go authorization and rollback procedures.
No agent may override recovery gates based on a model-generated assertion.

Read references/tool-matrix.md for tool choice and references/evidence-schema.md for review gates.
