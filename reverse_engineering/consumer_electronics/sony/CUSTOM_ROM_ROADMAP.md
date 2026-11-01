# Sony KD-55X80K — custom ROM research and build program
Date: 2026-10-31. Priority pivot: AOSP-derived device-specific ROM, subject to boot and recovery feasibility. Existing Android 12 launcher track remains a reversible fallback and useful test harness.

## Observed baseline
KD-55X80K; BRAVIA 4K VH21; Android TV 12; security patch 2025-09-01; kernel 4.19.260-ab681561; build BRAVIA_VH21_UC-user 12 STT2.230505.001.S88 681561 release-keys. Sony PKG version and actual board SoC remain unverified. Production release-keys DOES NOT show bootloader unlock.

## Primary evidence
Sony model downloads https://www.sony.com/electronics/support/product/kd-55x80k/downloads
Sony North America OTA v6.8224: https://www.sony.com/electronics/support/lcd-tvs-android-x85k_x86k_x89k_85x80k-series/kd-75x85k/software/00355755
Sony source distribution Americas lists KD-55X80K across versions: https://oss.sony.net/Products/Linux/TV/category02.html
Sony source sample for Japan KJ-55X80K family includes bravia-kernel.tar.bz2: https://oss.sony.net/Products/Linux/TV/KJ-75X80K_Jap_Ver65948.html
Sony Xperia unlock instructions: https://www.sony.com/electronics/support/articles/SX150401 (Xperia-only; NOT evidence of TV unlock support).

## Engineering milestones
ROM-000 (P0) capture sanitized and authorized ADB inventory, precise build, supported ABIs, partition naming, product/device/vendor identifiers, board features, update package version. Do not take dump of protected personal data.
ROM-010 (P0) download Sony-distributed GPL components and OTA to controlled evidence storage; record license, URLs, hashes and tag/firmware correspondence; do not commit copyrighted binaries.
ROM-020 (P0) statically inspect official OTA container and source compatibility, update metadata, boot image format, AVB and dynamic partition indicators. No repacking/flashing.
ROM-030 (P0 decision) establish legitimate write and recovery route: manufacturer unlock support, writable development board or known spare board, OEM service documentation, verified rescue/restore. If missing, mark PHYSICAL_ROM_BLOCKED and continue emulator-only.
ROM-040 (P1) construct minimal AOSP Android TV build for emulator on supported Linux host; pin toolchain and reproducible build instructions; no hardware-specific claims.
ROM-050 (P1) define device tree/BoardConfig, vendor HAL dependencies, DTB, graphics/audio/video/tuner/HDMI-CEC/eARC/Wi-Fi/Bluetooth/remote/captions support matrix. Closed-source libraries may require authorized reuse; never assume generic AOSP will work.
ROM-060 (P1) develop isolated device-compatibility shims, own launcher and local settings, without disabling built-in security updates on deployed stock device.
ROM-070 (P1) emulator and development-board validation: bootloop handling, watchdogs, power/standby, video, audio, remote, accessible captions, local network and deterministic acceptance fixtures.
ROM-080 (P2 blocked by ROM-030) physical ROM installation only with model/revision match, verified image signature/unlock policy, complete recovery, owner approval and acceptance ticket. Never auto-flash.
ROM-090 (P2) burn-in, recovery regression, rollbacks, documented unsupported features and secure update lifecycle.
ROM-100 (P2) publish model-specific skill, SBOM, reproducible build manifest and release gating. Exclude proprietary image contents.

## Feasibility decision
- Sony official firmware can be installed by Sony's supported USB path; this is not custom-ROM authorization.
- Source code archives are promising for kernel analysis but do not establish unlocked bootloader, full drivers or redistributable vendor blobs.
- No established public KD-55X80K flashable custom ROM identified in this research pass.
- Do not apply Sony Xperia unlock instructions to BRAVIA.

## Codex assignment
Begin ROM-000/010/020 in parallel with read-only device profile and AOSP emulator build manifest. Add machine-readable ROM gate report with statuses PASS, FAIL, UNKNOWN, BLOCKED. Pin exact OTA/source archive after verifying checksums. Avoid privileged device changes or flash commands. Report what actually runs versus planned adapters.
