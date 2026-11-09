# Acceptance and Codex passes

AUI-G0 baseline: screenshot inventory, current branch, toolkit, existing UI actions.
AUI-G1 7 panels functional with original skin; library state survives skin switch.
AUI-G2 user replaces Player/EQ/Playlist images independently, previews, applies, saves and exports .rskin.
AUI-G3 .wsz fixtures (authorized), invalid archives, missing sprites and fallback verified.
AUI-G4 resize/HiDPI/pixel snapping/input hit tests across macOS/Windows/Linux where claimed.
AUI-G5 keyboard, semantic control names, readable override/high-contrast and screen-reader audit.
AUI-G6 snapshot diffs for multiple skins, transport interaction tests, no audio interruption on hot swap.
AUI-G7 installer/import attack tests, memory limits, error recovery.
AUI-G8 real host bundle verification, documented user testing, rollback.

Task order: AUI-00-001 architectural contract; AUI-01-001 Winamp behavior matrix; AUI-02-001 manifest validator; AUI-03-001 sprite atlas; AUI-04-001 window docking; AUI-05-001 editor; AUI-06-001 library UX; AUI-09-001 visual tests; AUI-11-001 security review. Keep tasks scoped to independent files and require evidence for PASS/FAIL/NOT RUN.

Rust Music first: make macOS main player and queue operable before visual skin polishing. Keep actual FLAC playback acceptance owned by AE suite. A skinned button must exercise the same transport command as native UI.
