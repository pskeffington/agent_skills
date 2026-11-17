# RF engineering methods and validation plan

## Evidence states
`SOURCE_REVIEWED` confirms public documentation only; `PACKAGE_RESOLVED` means target `pacman -Si`; `SIMULATED_PASS` requires recorded deterministic fixtures; `HOST_PASS` requires reproducible log; `HARDWARE_PASS` requires connected real device and provenance. Never infer one from another.

## Deployment methodology
1. Inventory architecture, OS, kernel, USB VID:PID, audio devices and available package metadata.
2. Resolve versioned package and runtime dependency graph; mark packages as pacman candidates versus AUR/manual. Do not treat an upstream install command for Ubuntu or Fedora as Arch-compatible.
3. Conduct safe `--plan` and `--download` runs; no package writes during plan and no AUR installs.
4. Install via explicit, full-upgrade transactions and verify idempotency on second run.
5. Test synthetic IQ, AFSK, Codec2 and audio routing offline, with expected SHA-256/metrics; record sample rates and errors.
6. For real hardware, use device-specific model and vendor drivers; confirm permission and kernel driver conflicts without blindly blacklisting modules.
7. Test GUI and service configuration under the real user with rollback. Keep services user-scoped and off by default.
8. Independently verify field power budget, regulatory authorization and transmit chain; never enable PTT/TX from normal deployment.

## Methodology by agent
| Agent | Quantitative/technical evidence | Failure gate |
|---|---|---|
| Spectrum Architect | signal PSD, EVM, alias attenuation, sample-rate ratios | wrong units/clipping/resampling |
| Signal Systems Steward | pinned ABI, compile matrix, architecture decision | incompatible GNU Radio/OOT module |
| Mesh Link Integrator | firmware/API schema, RSSI/SNR provenance, loss | wrong region or mutable radio state |
| Packet Frame Engineer | AX.25 CRC and packet error rate vs controlled SNR | unverified frames or unintended beacon |
| Voice Codec Researcher | bitrate, algorithmic delay, controlled speech quality | ungrounded quality claims |
| Digital Voice Integrator | device routing, latency, underruns and accessibility | accidental PTT or wrong audio device |
| Field Linux Builder | dry-run manifest closure and 2nd-run idempotency | partial upgrade or unreviewed AUR |
| Portable Signal Operator | power load, duty-cycle estimates, UTC accuracy | no field measurement or authorization |
| Receiver Validation Engineer | actual USB ID, IQ hash, drop count, FFT peak | mistaken device/driver/GUI acceptance |

## Technical source boundary
Primary references: https://wiki.gnuradio.org/index.php/Tutorials , https://wiki.archlinux.org/title/GNU_Radio , https://github.com/wb2osz/direwolf , https://freedv.org/getting-started/ , https://github.com/km4ack/73Linux , https://meshtastic.org/docs/ . 73Linux documents Mint/Ubuntu compatibility, **not Arch**. FreeDV officially documents Ubuntu/Fedora support; Arch requires separate acceptance.

## Unexecuted validation
The matrices are design and source review, not a passing software build or verified hardware inventory. Target host tests and repo validators remain pending until run with recorded results.
