# Indexed Codex Implementation Roadmap — RE Division
Objective: a reusable, local-first, reproducible RE pipeline for lawful device repair, protocol interoperability, firmware inventory, and clean-room compatibility.

## P0: foundation
- [ ] RE-001 validate index.json with JSON Schema; enforce unique IDs, required IO, gates and forward-only dependencies.
- [ ] RE-002 implement typed manifest models (Rust preferred; JSON interoperable); canonical SHA-256 and UTC timestamps.
- [ ] RE-003 create safe CLI: `re-toolkit case init|hash|triage|report|validate`. Hash only, no execution.
- [ ] RE-004 synthetic fixture suite: ELF/PE/Mach-O headers, fabricated firmware container, benign pcap and corrupted cases.
- [ ] RE-005 GitHub Actions gate: format, lint, unit, schema, fixtures, dependency license and secret scan.

## P1: analysis adapters
- [ ] RE-101 Ghidra headless adapter, installed-tool discovery, explicit version, JSON export, timeout, no host networking.
- [ ] RE-102 Rizin and LIEF read-only extraction, normalize section and symbol schema.
- [ ] RE-201 Binwalk signature and offset inventory, safe extraction with decompression limits and path traversal checks.
- [ ] RE-401 Wireshark/tshark and Kaitai offline synthetic protocol parsers.
- [ ] RE-701 cross-tool concordance with confidence and provenance.

## P2: advanced / isolated
- [ ] RE-501 LLDB/GDB/Frida/angr harness limited to synthetic owned test programs, opt-in execution, fixed budgets.
- [ ] RE-301 hardware bench procedures and simulator adapters; no automatic flashing.
- [ ] RE-601 clean-room interface specification + independent implementation tests.
- [ ] RE-801 searchable redacted evidence index, chunking by function/offset, citation-first retrieval, small-model JSON prompts.

## Acceptance
Every completed task adds: machine-readable output schema; synthetic positive/negative tests; reproduction commands; version and platform matrix; failure behavior; threat/abuse review; docs. Distinguish PASS, FAIL, SKIPPED (unavailable tool), BLOCKED (approval). Zero real artifacts in CI. Do not merge while any P0 test fails.

## First Codex instruction
Read `reverse_engineering/AGENTS.md`, `index.json` and this roadmap. Implement RE-001 then RE-002 and RE-003 on a new implementation branch, adding deterministic fixtures and tests. Keep all inspection read-only and offline. Run tests and report exact statuses; do not misrepresent uninstalled external tools as validated. Open a PR against main after checks pass.

## Target integration
- Rust Boy / Pip-Boy: receive-only firmware and binary compatibility assessments.
- rust_music / rust_tv: media format and playback interface interoperability analysis.
- Bose and smart-TV repair: authorized firmware acquisition, recovery feasibility, documented device-specific risk assessment prior to hardware activity.
- rust_tak / FIDES: documented messaging, wire-format and protocol behavior tests with synthetic traffic.
