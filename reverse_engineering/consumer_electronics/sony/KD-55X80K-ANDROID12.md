# KD-55X80K Android 12 — revised implementation track
Captured on-device About screen (2026-10-31):
- Physical model: KD-55X80K, device model label BRAVIA 4K VH21
- Android TV OS: 12; patch: 2025-09-01
- Kernel: 4.19.260-ab681561; compile 2025-10-28
- Build ID: BRAVIA_VH21_UC-user 12 STT2.230505.001.S88 681561 release-keys
- Current Sony firmware package version: NOT VERIFIED (build suffix is not automatically Sony public version)
- Device network IP/MAC: NOT VERIFIED
No serials or raw private screenshots in repo.

## Architecture decision
Prioritize Android 12 application-level independence; DO NOT initiate full-ROM development without explicit new feasibility evidence. A production release-keys image does not prove bootloader unlockability.

A12-000: identify device IP from TV itself, record HDMI/eARC/Bose integration, save package inventory and backup launch settings.
A12-010: read-only Android Debug Bridge inventory after user-authorized debugging. Collect getprop, package lists, active home and disabled package statuses; redact identifiers.
A12-020: develop own simple Rust-hosted controller or Android launcher with Android TV navigation, captions, media player and accessible large-text settings. Initial proof: sideload and manual launch, without disabling anything.
A12-030: test local-only playback / HDMI switching / remote / standby / TV input / accessibility, network disconnected; record acceptance.
A12-040: reversible launcher promotion only after alternative HOME launches correctly, persists after reboot, and ADB rollback remains verified. Use actual discovered stock launcher package; never guess.
A12-050: optional per-package debloat: dependency review and disable-user only, one package at a time, exact journal and enable rollback; never blanket-disable Sony/MediaTek TV, input, accessibility, system UI, settings, audio or CEC services.
A12-060: UniFi DNS/network restrictions staged from monitor to block, confirm local playback and update behavior, and protect OS security update route.
A12-070: synthetic Android TV/ADB adapters, automated CI fixtures, signed APK pipeline and release docs.
A12-080: only if later justified, continue earlier bootloader / firmware feasibility track without flashing production device.

## Read-only commands (run only after TV-side approval)
adb devices -l
adb shell getprop ro.build.fingerprint
adb shell getprop ro.build.version.release
adb shell cmd package list packages
adb shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.HOME
adb shell pm list packages -d
These may vary by Android build; record errors as SKIPPED rather than assuming success.

## References
Android AOSP package management: https://source.android.com/docs/devices/admin/multi-user-testing
Community research, not Sony-specific validation: https://github.com/parth-nikam/cleanyourtv
Do not apply community launcher disable package names unless inventory verifies exact device and alternative home is confirmed.
