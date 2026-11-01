# Engineering roadmap (CE series)

| Pass | Work | Mandatory deliverable | Acceptance |
|---|---|---|---|
| CE-000 | Inventory & model fingerprint | device.yaml, photos/board identifiers (private), capabilities | exact model/board provenance |
| CE-010 | Source/literature review | cited evidence registry | upstream + date + limitations |
| CE-020 | Read-only firmware/file inspection | SHA-256 manifest, SBOM | immutable originals, isolated extraction |
| CE-030 | Local protocol observation | redacted synthetic traces, protocol map | authorized LAN only |
| CE-040 | Account-free control applications | Rust local daemon/UI and tests | power/volume/input offline where supported |
| CE-050 | Boot architecture research | boot map, partitions, recovery feasibility | independent corroboration |
| CE-060 | Drivers / HAL feasibility | hardware compatibility matrix | video/audio/power functions accounted |
| CE-070 | Lab firmware prototype | bootable emulator or dev board | deterministic unit/integration gates |
| CE-080 | Device flashing | approved deployment ticket | backup, known recovery and user approval |
| CE-090 | Stress and reliability | regression suite | cold boot, A/V, volume, standby, update rollback |
| CE-100 | Package skill | model-scoped release manifest | docs, provenance, recovery and maintenance |

## Workstreams
SONY: identify model/OS; evaluate external HDMI playback, ADB-supported configuration and Sony local IP interfaces by model; only then bootability assessment. Avoid assuming generic Android TV custom ROM compatibility.

BOSE: identify SoundTouch vs Smart Soundbar model. For SoundTouch, test documented Web API against owned local device, HTTP 8090 / WS 8080 only if supported; otherwise evaluate native remote, HDMI-CEC, optical and Bluetooth. Restore core functionality first; defer invasive firmware work.

GENERIC: prioritize products with published board maps, community-supported firmware and a tested recovery path. Capture supported/unsupported features and hardware-revision drift.

## Agent ownership
RE-000 orchestration; RE-010 acquisition; RE-020 triage; RE-100 static; RE-200 firmware; RE-300 hardware; RE-400 protocol; RE-500 isolated runtime; RE-600 clean-room interoperability; RE-700 validation; RE-800 evidence index.
P0: CE-000/010/030/040. P1: CE-020/050/060. P2: CE-070/080 only after gate clearance.

## Codex initial execution
Implement CE schema and validation fixtures. Build passive local controller interface with simulated Sony/Bose device backends; DO NOT attempt discovery or modification of third-party devices. Add exact model capability gates, timeout/retry handling, network-offline tests and evidence provenance. Next implement device-specific adapters behind feature flags after real model identification. Commit focused diffs, test and report PASS/FAIL/SKIPPED.
