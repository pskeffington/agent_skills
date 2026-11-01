# Evidence and readiness schema

## Required evidence record
- `id`: unique immutable evidence ID
- `device`: manufacturer + exact model + board/firmware revision, or `unknown`
- `question`: falsifiable proposition
- `source`: official URL, repository commit, local file hash or trace ID
- `method`: reproducible command, tool/version, and environment
- `observation`: directly observed facts
- `inference`: interpretation distinct from observation
- `confidence`: low / medium / high with explanation
- `limitations`: failure modes and missing inputs
- `reviewer`, `date`, `status`: proposed / reproduced / disputed / rejected

## Gate table
| Gate | Requirement |
|---|---|
| RE-G0 | authorization and target identity recorded |
| RE-G1 | immutable SHA-256 provenance; input treated as hostile |
| RE-G2 | extraction verified; files/scripts never trusted automatically |
| RE-G3 | important static claims independently corroborated |
| RE-G4 | emulation confined to isolated environment with measured coverage |
| RE-G5 | local commands replayed safely on a test device, if authorized |
| RE-G6 | flash blocked until backup, compatibility, signed image/boot constraints, and demonstrated recovery are documented |

## Bose / TV-specific acceptance
Do not conflate offline official firmware updates with custom firmware support. Test whether HDMI-CEC or IR permits local operation without cloud services. Preserve accessibility, audio, DRM, software updates, and recovery. No universal TV or Bose firmware image should be recommended without exact model/board support.
