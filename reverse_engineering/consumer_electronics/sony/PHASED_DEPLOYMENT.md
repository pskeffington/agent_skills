# Sony KD-55X80K — gated phased liberation deployment
Date: 2026-10-31. Hardware: KD-55X80K (BRAVIA 4K VH21), Android TV 12, patch 2025-09-01, kernel 4.19.260-ab681561. Android build: STT2.230505.001.S88. Sony public firmware version not yet verified.

Goal: preserve display/tuner/HDMI/audio/CEC/captions/security updates while enabling locally controlled and account-independent features. No stock package modifications before a working rollback.

## Phase 00: baseline (partially complete)
Record physically verified model and on-device OS build. IP, MAC, actual firmware package version and feature baseline remain unknown.
Gate: device profile distinguishes observed from inferred.

## Phase 01: authorized inventory (P0)
Codex: build read-only ADB inventory parser, JSON schema, sanitized report, synthetic fixtures; user enables debugging via TV UI, pairs with Mac and authorizes. Inventory packages, launcher resolution, capabilities, permissions, accessibility and HDMI-CEC.
Gate: reproducible report; no package changes or credentials saved.

## Phase 02: parallel launcher MVP (P0)
Codex: implement Android TV compatible APK (Kotlin/Java UI as appropriate; Rust backend optional), D-pad focus, local app grid, system settings shortcut, captions, fallback HOME. Install and manually launch; leave stock HOME intact.
Gate: TV boots normally; manual test works; uninstall returns to baseline.

## Phase 03: offline acceptance (P0)
Codex: app settings/local storage, playable local media paths, startup behavior and explicit network-offline test profiles. Do not claim Google account can be removed until tests prove required apps continue to work.
Gate: core chosen use cases pass offline and with account signed out; document any feature tradeoffs.

## Phase 04: reversible cleanup (P1)
Codex: propose package-by-package dependency matrix from actual on-device inventory. Require manual signoff before each disable-user action; log undo commands. Never blanket-disable system UI, settings, accessibility, tuner, HDMI, audio or update services.
Gate: cold boot, safe remote access, captions and restore procedure pass following EACH change.

## Phase 05: local controls (P1)
Codex: Sony retail-compatible IP / Android control feasibility; UniFi monitoring; Bose soundbar HDMI-CEC/eARC and optical tests; no inference that professional BRAVIA APIs are supported.
Gate: locally controlled power, input, volume, audio routing and standby all independently verified or explicitly marked unsupported.

## Phase 06: reliability/security (P1)
Run reboot cycles, standby/resume, HDMI/source swaps, captions, Wi-Fi down, Ethernet, unattended startup, update compatibility and rollback exercises. Keep Sony security update route available.
Gate: test matrix PASS/FAIL/SKIPPED with log evidence; no unresolved critical regression.

## Phase 07: release (P1)
Codex: signed APK, pinned build toolchain, hash, SBOM, install/uninstall and recovery docs, A/B rollout via spare test device or same-device reversible trial.
Gate: reproducible release artifacts, documented rollback and manual acceptance.

## Phase 08: optional firmware research (P2, gated)
Only if application-level independence fails to achieve goals: inspect official image read-only, SoC/bootloader drivers and recovery. Do not assume Android 12 enables arbitrary image flashing. Separate human-approved hardware modification project.
Gate: independent recovery feasibility and board compatibility, with no live flash until specifically approved.

## Codex handoff
Start Phase 01: create inventory schema, redaction rules, synthetic ADB outputs, tests, and a read-only Mac collection script with explicit opt-in. Then Phase 02 in a separate feature branch. Never connect to a live IP inferred from UniFi without confirmation. Do not overwrite earlier model-specific roadmap; link this phased guide from it in next documentation maintenance pass.
