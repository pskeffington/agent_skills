# Firmware reverse engineering tool and literature matrix

Reviewed 2026-10-31. Tools are external projects to evaluate, **not bundled dependencies or installed capabilities**.

| Tool | Repository | Intended stage | Advantage | Caveat |
|---|---|---|---|---|
| Ghidra | https://github.com/NationalSecurityAgency/ghidra | static disassembly/decompilation | Multi-architecture graphical analysis and scripting | Decompiled pseudocode must be independently checked |
| Binwalk | https://github.com/ReFirmLabs/binwalk | firmware container inspection/extraction | Finds embedded filesystems and signatures | Untrusted images; parser/extractor attack surface |
| EMBA | https://github.com/e-m-b-a/emba | embedded firmware vulnerability/component analysis | Aggregated automated assessment and reporting | Heavy dependencies; findings require human review |
| FirmAE | https://github.com/pr0v3rbs/FirmAE | Linux firmware emulation | Dynamic rehosting for supported images | Boot success/behavior not guaranteed |
| Rizin | https://github.com/rizinorg/rizin | CLI binary RE | Scriptable analysis | Analyst expertise required |
| radare2 | https://github.com/radareorg/radare2 | CLI binary RE | Broad formats, inspection workflow | Alternative to Rizin, do not assume output equivalence |
| angr | https://github.com/angr/angr | symbolic execution | Path-condition analysis | State explosion, environment modeling |
| QEMU | https://www.qemu.org/ | emulation | CPU/system execution in sandbox | Peripheral models and firmware state may be missing |
| Wireshark | https://www.wireshark.org/ | local protocol captures | Passive traffic observation | Encrypted traffic and no capture consent limitations |

## Research papers
- Li et al. (2026), *SoK: A Large-Scale Empirical Study of Emulation-Based Dynamic Analysis Research for ARM Cortex-M Firmware* https://arxiv.org/abs/2609.38872 — warns about low coverage and fragile emulation-based claims.
- Shen et al. (2026), *FirmPilot: Evidence-Guided Multi-Agent Environment Recovery for IoT Firmware Rehosting* https://arxiv.org/abs/2607.14903 — evidence-guided environment recovery; evaluate independently before adopting.
- Gao et al. (2025), *DecompileBench* https://arxiv.org/abs/2505.11340 — decompiler readability != functional fidelity.
- Jiang et al. (2024), *BinPRE* https://arxiv.org/abs/2409.01994 — evidence-based protocol field inference.

## Local project integration
- https://github.com/pskeffington/network_security — smart-TV and Bose feasibility, DNS allow/deny rules. Follow its hardware-specific documentation; do not infer a supported flash pathway.
- Future reuse across Rust-based device tools requires separate implementation and tests. This skill supplies agent procedure, not executable firmware extraction or flashing code.

## Selection principle
Use the least invasive tool capable of answering the question. Start with file identity + hashes, then isolated extraction and static analysis. Only move to dynamic emulation on a proven-safe image in a sandbox. Hardware flashing is a separate, manually authorized activity.
