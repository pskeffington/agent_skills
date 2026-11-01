---
name: audio-ui-engineering
description: Build, debug, skin and validate modular Winamp-inspired desktop audio interfaces. Use for player/playlist/equalizer/library/visualizer windows, user-created themes, classic WSZ import, sprite atlases, docking, scalable hit testing, cross-platform Rust UIs and skin-security reviews.
---

# Audio UI Engineering
Delegate to the AUI specialist matrix in [agents.md](references/agents.md). Keep skin appearance separate from audio transport and media-library state. Establish a default original skin first, then switch/preview skin components at runtime without interrupting playback. Use [skin format](references/skin-contract.md), [Winamp evidence](references/winamp-literature.md), and [acceptance gates](references/acceptance.md).

## Workflow
1. Inventory the application's existing toolkit and layout ownership; record baseline screenshots and keyboard behavior.
2. Establish a panel registry: player, EQ, playlist, library, visualizer, mini player, skin manager.
3. Implement a versioned, declarative native skin manifest and normalized logical coordinate system. Missing resources fall back to originals.
4. Implement import/validation and non-executable preview first. Add classic WSZ sprite support as a compatibility adapter; keep modern WAL/Wasabi/MAKI out of initial scope.
5. Permit users to replace each segment independently and save a coherent theme bundle. Do not couple theme switching to audio stream ownership.
6. Implement pixel snapping, scaling, pointer-to-skin coordinate conversion, window snapping and keyboard fallback.
7. Test hostile archives, missing assets, tiny/huge windows, multi-monitor/DPI, light/dark, accessibility and screenshots.
8. Report exact passes, screenshots, regressions, remaining compatibility gaps, and source licensing. Do not bundle copyrighted Winamp skins.

Coordinate with audio-systems-engineering AE-05 (queue), AE-03 (transport) and AE-06 (regression) using narrow interfaces. Do not rewrite the decoder in a UI pass.
