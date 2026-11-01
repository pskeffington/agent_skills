# Quality gates

- G0: Locked build, lint, tests and diff integrity.
- G1: Golden synthetic mono/stereo PCM/FLAC/WAV, malformed input, nonzero output, frame and format integrity.
- G2: Queue/transport state-table regression and cold-start persistence.
- G3: Error handling for missing files, empty queues, output changes, sleep and resume.
- G4: Measured callback P50/P95/P99 and underruns; no callback allocation/blocking.
- G5: Supported host audio backends actually tested; Mac signed app verified when relevant.
- G6: Loopback or documented listening on real playback fixtures; mark NOT RUN without hardware.
- G7: Release note, measurements, open risks, rollback.

Verdicts PASS/FAIL/NOT RUN per gate. No production promotion based solely on successful build or audible synthetic tone.
