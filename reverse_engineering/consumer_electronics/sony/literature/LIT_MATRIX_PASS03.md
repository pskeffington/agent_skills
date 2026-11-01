# Community RE literature matrix — KD-55X80K
Reviewed 2026-10-31 via repository source and current README. Registry: `registry.json`.

| ID | Project | Technical signal | Reuse | Confidence |
|---|---|---|---|---|
| LR-001 | Gathin23/cleanyourtv | launcher_backup_restore | Analyze snapshots, per-package state, HOME guard; port tests not unchecked scripts | direct_source |
| LR-002 | Gathin23/cleanyourtv | android_build | minSdk26,targetSdk34,Java17; release uses debug signing: improve our artifact signing | direct_source |
| LR-003 | Gathin23/cleanyourtv | BRAVIA_VH21 | KD-65X85K/A80K are analogs; no KD-55X80K firmware support | community_test_report |
| LR-004 | udeshvirk/sony-bravia-launcher | sony_hdmi_cec | Study input menus, color-key passthrough and soundbar wake in synthetic harness | direct_readme |
| LR-005 | udeshvirk/sony-bravia-launcher | never_disable_allowlist | Never-disable TV/tuner/remote/settings/accessibility, verify local model | direct_readme |
| LR-006 | udeshvirk/sony-bravia-launcher | wifi_adb_client | Compare transport reliability with native adb on macOS; require explicit paired target | direct_readme |
| LR-007 | yurchornyi/tv-launcher | restorable_state | Persistent initial state per target and package; no overwrites after repeat passes | direct_source |
| LR-008 | yurchornyi/tv-launcher | release_signing | Keystore persistence; macOS Keychain; debug fallback unsuitable production | direct_source |
| LR-009 | yurchornyi/tv-launcher | offline_launcher | Low-resource Java D-pad launcher; explicit effects/performance gating | direct_source |
| LR-010 | Sony OSS | kernel_source | Match source archive to build; kernel source is not full ROM / bootloader unlock | manufacturer_index |
| LR-011 | Cross-project | namespace_collision | tv-launcher declares com.gathin.tvhome also used by cleanyourtv: inspect lineage and conflicts before reuse | direct_source |

## Source-critical distinctions
- CleanYourTV: actual `launcher/app/build.gradle` uses namespace `com.gathin.tvhome`, compile/target SDK 34, min SDK 26, Java 17; release variant signs with a debug signing key. It is an app, not a ROM.
- tv-launcher: same `com.gathin.tvhome` namespace/application ID; its Gradle script uses a persistent release keystore when present and otherwise a debug signature. Do not install or swap variants in place without signature/package-conflict analysis. This shared namespace and related design make independent corroboration weaker.
- sony-bravia-launcher: tested KD-55X80J (VH2), includes Sony-specific color-key passthrough, soundbar wake behavior and a never-disable list. Functional ideas apply to our A/V acceptance harness, but different device model.
- CleanYourTV lists VH21 sibling models, not our exact KD-55X80K; never transfer a sibling debloat list without on-device inventory.
- Sony OSS gives a possible kernel/driver research path, NOT complete proprietary HALs or a validated custom ROM.

## Required scholarly/engineering quality improvements
Separate direct source inspection from author statements and reproduced physical tests. Pin git commit SHA before adopting anything; retrieve licenses and third-party notices independently. Record mutation surfaces, service permissions, Android signature constraints, recovery paths, accepted hardware, and exact-version reproducibility. No hardware flash authorization is derived from any community launcher.

## Engineering action order
P0: link provenance and licenses; implement package state preservation, HOME guard, never-disable policy and test harness. P1: Sony input/CEC/soundbar integration and local launcher. P2: Sony OSS kernel source mapping and ROM feasibility. Do not copy third-party code into our repository until license review and attribution.
