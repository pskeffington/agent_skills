# Rust Music first acceptance case

Historical reported failures, subject to verification on current commit: generated tones work but imported FLAC is silent; import-to-queue is difficult; CLI and macOS app may behave differently. A literal placeholder path such as /full/path/to/file.flac is not a fixture.

- RM-A1: Instrument open -> decode -> enqueue -> consume -> CoreAudio for synthetic legal FLAC and actual user-owned track.
- RM-A2: A/B CLI vs GUI on identical file, route and output format.
- RM-A3: Implement explicit Idle/Loading/Ready/Playing/Paused/Stopping/Error transitions with user-visible errors.
- RM-A4: Import folder, scan progress, search, add-to-queue, persistent playlist, double-click play and explicit Stop.
- RM-A5: Measure underruns, callback tail latency and output-change recovery; perform listening/loopback before release.

Never infer present implementation from older notes; cite exact commit and commands.
