# AE Agent Owners

| ID | Accountable role | Artifact |
|---|---|---|
| AE-00 | Audio Lead / coordinator | Reproduction, dispatch and incident decision |
| AE-01 | Codec & Media Engineer | File-header, demux/decode frame counts and checksum |
| AE-02 | PCM & DSP Engineer | Resampling, channel map, clipping, silence/level metrics |
| AE-03 | Real-time Playback Engineer | Callback deadlines, ring-buffer capacity, underrun trace |
| AE-04 | Platform Backend Engineer | CoreAudio, PipeWire/ALSA, WASAPI device and stream trace |
| AE-05 | Library, Queue & UX Engineer | Import, playlist, playback state machine, UI consistency |
| AE-06 | Test & Integration Engineer | Synthetic fixtures, regression and CI evidence |
| AE-07 | Acoustic Validation Engineer | Physical/loopback output, level, channel, latency validation |
| AE-08 | Release & Observability Engineer | Bundle, logging, crash recovery, release and rollback |

AE-00 assigns exactly one primary per incident. Parallel agents own disjoint files. AE-06 may verify only tests actually run; AE-07 owns claims of physically audible output. Logs use a session_id and redacted track/device identifiers. Commit scope and reproducibility are mandatory.
