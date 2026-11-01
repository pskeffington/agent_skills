# Board Engineering Pass 02 — KD-55X80K
Date: 2026-10-31. This is evidence research, not circuit characterization on the unit.

## New findings
- Sony OSS source index has KD-55X80K family entries across software releases; version-specific source archive includes bravia-kernel.tar.bz2. Those archives can establish source-level kernel/driver information only after matching device build and verifying actual contents.
- BM5A board replacement listings caution against cross-variant assumptions; some revisions differ in populated CN1601 and associated part identifiers. Verify labels and populated connectors on the owned device before applying pinout or ROM decisions.
- X80K service-parts documentation lists BM5A CN4200 -> TCON, CN3801 -> WLAN/BT, CN1200 -> HT2 and CN3550 speaker assembly. Connector pin counts are not electrical protocol evidence.

## Pass tasks
B02-01 map Sony official source releases to observed Android build; record sources, archive hashes, licenses and source availability.
B02-02 obtain/inspect GPL archive in a separate offline safe workspace; index Kconfig, DTS/DTB, relevant platform driver folders. No proprietary files committed.
B02-03 create read-only ADB metadata collector extensions: ro.hardware, ro.board.platform, cpu ABI, meminfo, storage transport, kernel build and USB bus. Redact IDs.
B02-04 inspect panel, main-board part label, and auxiliary connectors only if safe power-disconnected physical access becomes available.
B02-05 map component -> kernel module -> firmware -> Android HAL -> acceptance fixture, using dependency_graph.json.
B02-06 build independent component-level test matrix for standby, input switching, eARC, audio, display, remote, USB and networking.
B02-07 document unresolved bootloader and recovery; keep physical custom-ROM flashing BLOCKED unless independently verified.

## Evidence and cautions
Do not infer actual SoC identity from X1 marketing name; do not infer service UART from RS-232 control. Some service-parts materials cover multiple regional variants. Connector count is not pinout. Never probe live power boards or open mains sections.
Sources:
https://oss.sony.net/Products/Linux/TV/category02.html
https://oss.sony.net/Products/Linux/TV/XR-65A95K_USA_Ver65771.html
https://www.manualslib.com/manual/3364482/Sony-Kd-43x80k.html
https://www.tvparts.ca/tvdetail.php?id=20212

## Codex kickoff
Read dependency_graph.json and implement B02-03 plus test fixtures first. Then build source archive index B02-01 / B02-02. Require stable source citations, statuses PASS/FAIL/SKIPPED/UNKNOWN and evidence references. Do not change live TV packages or firmware.
