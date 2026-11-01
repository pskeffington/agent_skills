# KD-55X80K board engineering and I/O matrix — Pass 01
Board family candidate: Sony BM5A; variant-specific. Mainboard candidate A-5042-741-A, power 1-004-422-22, T-CON 1-014-107-12, WLAN/BT 1-005-419-32. Service manuals show region/variant differences, so none is asserted physically verified. See `hardware.json`.

## Evidence
- Sony US specifications: https://www.sony.com/electronics/support/televisions-projectors-lcd-tvs-android-/kd-55x80k/specifications
- X80K service parts and interconnect descriptions: https://www.manualslib.com/manual/3364482/Sony-Kd-43x80k.html
- Aftermarket corroboration and caveat on board revisions: https://www.shopjimmy.com/sony-xr-55x80k-complete-led-tv-repair-parts-kit/
- Existing user observation: KD-55X80K Android 12, VH21, kernel 4.19.260.

## ROM-critical unknowns
1. Actual SoC package identity and architecture, BootROM/U-Boot/other loader, AVB state, OEM unlock support and real recovery mechanism.
2. DRAM configuration and eMMC/UFS chip, protected partitions and dynamic partition layout.
3. Display panel exact ID, BM5A→T-CON electrical protocol and panel/backlight power sequencing.
4. Graphics/video DRM and codec HALs, HDMI input/CEC/eARC routing, audio codec/amplifier, tuner IC, Wi-Fi/BT firmware.
5. Actual board revision, variants and regulatory differences.

## Safe investigation gates
B01 use user-approved, read-only ADB to retrieve build props, cpuinfo, /proc/meminfo, /proc/partitions (metadata only), /proc/device-tree/model where readable, driver names and USB sysfs. Do not capture userdata or device secret identifiers.
B02 obtain official service documentation and OSS source matching build, register SHA256/provenance and annotate license.
B03 generate an annotated cable inventory from service illustrations; never guess pin assignments/voltages.
B04 map Android HALs using packages, service metadata and proprietary component dependencies without uploading vendor binaries.
B05 decide ROM feasibility only once recovery path and hardware driver matrix are evidenced.
B06 advanced physical teardown, if needed, only by qualified person with device disconnected; do not open mains PSU shielding or measure live circuitry.

## Tool alignment
RE-010 evidence; RE-100 binaries; RE-200 firmware; RE-300 connector/board inventory; RE-400 protocol and ports; RE-600 AOSP HAL compatibility; RE-700 tests; RE-800 citations. Each machine-readable record marks physical verification separately.
