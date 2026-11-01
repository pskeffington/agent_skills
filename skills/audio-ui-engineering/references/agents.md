# AUI-00–11 Agent ownership

| ID | Specialist | Deliverable |
|---|---|---|
| AUI-00 | Lead Audio UI Architect | Component contracts, routing, acceptance |
| AUI-01 | Winamp Interaction Analyst | Layout/behavior matrix and usability benchmarks |
| AUI-02 | Skin Format & Import Engineer | Declarative manifest parser and WSZ converter |
| AUI-03 | Sprite Atlas/Renderer Engineer | Image crop, UV, bitmap font, hit-map and cache |
| AUI-04 | Modular Window/Docking Engineer | Snapping, persistence, resize and multi-monitor |
| AUI-05 | Skin Editor Engineer | Per-panel image replacement, undo, previews and export |
| AUI-06 | Library/Playlist UX Engineer | Import, scan, selection, double-click play, drag reorder |
| AUI-07 | EQ/Visualization Engineer | UI telemetry, 10 bands, spectrum with bounded updates |
| AUI-08 | Accessibility/Scaling Engineer | Screen-reader semantics, contrast, keyboard, HiDPI |
| AUI-09 | Visual Regression Engineer | Golden screenshots, input maps, automated UI checks |
| AUI-10 | Cross-platform Integration Engineer | App windowing on macOS, Windows, Linux, Rust Boy |
| AUI-11 | Skin Security/Compatibility Engineer | Archive defenses, permissions, provenance, fallback |

AUI-00 assigns one file owner per task. AE agents own playback engine; AUI agents own UI state and rendering. Any asynchronous skin load must be cancellable and preserve the active skin on failure.
