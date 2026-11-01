# Consumer Electronics Independence (CE) — Engineering Program
Scope: owned or authorized consumer hardware. Goal: reduce mandatory cloud-account dependence and preserve useful hardware through local control, replaceable applications and, when verified feasible, custom firmware.

## Four capability levels
L0 external independence: HDMI/optical/IR/local media.
L1 local protocols: documented LAN control and open remote UI.
L2 local software replacement or configuration where authorized.
L3 board-specific custom firmware with verified boot support, rollback and safe human-approved flashing.

Never conflate model families. Sony BRAVIA options vary by model, region and boot chain. Bose SoundTouch local Web API does not imply every Bose Smart Soundbar supports it. Always identify product model, board revision and installed firmware before selecting a path.

## Routing
CE-000 inventory -> CE-010 evidence -> CE-020 read-only inspection -> CE-030 protocol capability -> CE-040 account-free controls -> CE-050 boot/board study -> CE-060 drivers -> CE-070 lab-only firmware -> CE-080 explicitly approved hardware flash -> CE-090 stability -> CE-100 package/release.
Optionality: stop at the lowest working level. L0/L1 releases must not be blocked by speculative L3 firmware.

## Priority targets
- CE-SONY-01: Sony TV; validate exact model before using Android debugging or BRAVIA IP control.
- CE-BOSE-01: Bose soundbar; identify SoundTouch vs Smart Soundbar; prioritize optical/HDMI-CEC/local APIs where available.
- CE-GENERIC-01: router, smart plug, media player, audio device; use per-model compatibility profiles, OpenWrt where supported.

## Safety
Read-only analysis first. No credential collection, anti-rollback defeat, signature bypass, DRM circumvention, production network targeting or unauthorized device access. Keep vendor binaries, secrets and device identifiers out of repository and RAG. No automated flashing or guessed pinouts. Document recovery and hardware electrical safety.
