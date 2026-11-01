# Reverse Engineering Tool / Evidence Matrix
Review date: 2026-10-31. This is an upstream capability index, not an installation or validation record.
| Tool | Upstream | Function | Integration target | Evidence / acceptance |
|---|---|---|---|---|
| Ghidra | https://github.com/NationalSecurityAgency/ghidra | static binaries/decompilation | RE-100 headless export | fixture function + address concordance |
| Rizin | https://github.com/rizinorg/rizin | scriptable binary inspection | RE-100 JSON adapter | compare sections/functions |
| Cutter | https://github.com/rizinorg/cutter | review UI | RE-100 human review | manual annotation export |
| angr | https://github.com/angr/angr | symbolic / CFG analysis | RE-500 opt-in | bounded synthetic path fixtures |
| Binwalk | https://github.com/ReFirmLabs/binwalk | firmware signatures/carving | RE-200 | offset and nested file validation |
| EMBA | https://github.com/e-m-b-a/emba | embedded firmware security analysis | RE-200 | isolated image and repeatable report |
| FACT | https://github.com/fkie-cad/FACT_core | firmware analysis framework | RE-200 | compare extraction findings |
| LIEF | https://github.com/lief-project/LIEF | executable metadata | RE-100 | PE/ELF/Mach-O fixtures |
| Kaitai Struct | https://github.com/kaitai-io/kaitai_struct | binary format schema | RE-400 | valid + malformed fixture parsing |
| ImHex | https://github.com/WerWolv/ImHex | hex-pattern investigation | RE-100 | peer-review offset evidence |
| Frida | https://github.com/frida/frida | dynamic instrumentation | RE-500 | owned synthetic app only |
| OpenOCD | https://github.com/openocd-org/openocd | on-device debugging | RE-300 | simulator first; human hardware approval |
| sigrok | https://sigrok.org/ | signal acquisition | RE-300 | synthetic trace decoding |
| Wireshark | https://www.wireshark.org/ | protocol decoding | RE-400 | synthetic pcap comparison |
| Scapy | https://github.com/secdev/scapy | packet parsing/generation | RE-400 | offline synthetic fixtures |
| AFL++ | https://github.com/AFLplusplus/AFLplusplus | parser fuzzing | RE-700 | bounded local fuzz smoke test |
| Syft | https://github.com/anchore/syft | SBOM | RE-700 | SBOM schema validation |
| Grype | https://github.com/anchore/grype | vulnerability inventory | RE-700 | provenance pinned and reviewed |

Research method: record upstream documentation, license, latest release/tag and platform support with retrieval date before integration. Separate verified capabilities, inferred claims and experiments. Avoid importing external repositories wholesale; pin exact versions and retain license notices.
Priority: Ghidra + Rizin + Binwalk + LIEF + Kaitai + Wireshark, then isolated dynamic tools, then hardware adapters.
