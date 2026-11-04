---
name: audio-systems-engineering
description: Coordinate specialist agents to diagnose, implement, test and release audio applications. Use for Rust/C/C++/Swift audio work, FLAC/WAV/AIFF issues, silent playback, queue and UI state defects, DSP, device routing, real-time audio underruns, CoreAudio, ALSA/PipeWire and WASAPI.
---

# Audio Systems Engineering
Use an evidence-driven specialist team. First capture commit, platform, device, real fixture and reproducible symptom. Assign a single accountable primary owner. Instrument the path file -> demux -> decode -> PCM conversion -> DSP -> queue -> callback -> backend -> physical output. Never treat a successful decoder or audible test tone as proof that imported tracks play.

Read [agents](references/agents.md), [diagnostics](references/diagnostic-matrix.md), [gates](references/quality-gates.md) and [Codex contract](references/task-contract.md). For Rust Music use [acceptance plan](references/rust-music-acceptance.md).

## Execution rules
1. Reproduce the failure with a real fixture and a generated control PCM tone through the same backend.
2. Record bytes read, decoded frames, nonzero decoded frames, submitted frames, consumed frames and underruns, along with output sample format and device.
3. Distinguish I/O, decode, format conversion, audio focus, queue, host rendering and UI-state failures.
4. Write a failing regression test if feasible, patch one layer, then repeat the same experiment.
5. Keep real-time callbacks nonblocking and free of allocation, filesystem access and logging.
6. Validate unit, integration, state transition, device lifecycle and real-device tests. Mark unexecuted tests NOT RUN.
7. Produce a report with root-cause evidence, changed paths, test outputs, residual risks and rollback. Do not claim hardware audio was heard without physical validation.

## Invariants
Separate library indexing, queue ordering, transport state, decoder state and output device state. A single transport owns host audio focus unless mixing is explicitly enabled. Never show Playing after a terminal output failure. Handle device changes and incompatible sample rates explicitly. Prefer distributable, original synthetic audio fixtures for CI.
