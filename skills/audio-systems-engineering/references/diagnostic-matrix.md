# Audio Diagnostic Matrix

| Symptom | Check | Owner |
|---|---|---|
| Tone audible, FLAC silent | Real path, access, decoded count, nonzero PCM and output format | AE-01 |
| Decoder outputs frames but silent | Frames enqueued/consumed, volume, device, focus | AE-03, AE-04 |
| UI Playing, no audio | State error propagation, callback/underruns | AE-05 |
| CLI works, GUI silent | Backend divergence, lifecycle, bundle and route | AE-04 |
| Clicks/gaps | Callback P95/P99, blocking, underrun count, FIFO fill | AE-03 |
| Speed/pitch incorrect | Sample rate/ratio and sample format | AE-02 |
| Wrong channel / phase | Interleaving and channel map | AE-02 |
| Queue import cumbersome | Scanner, ordering, selection-vs-playback transition | AE-05 |
| Device disconnect failure | Device callback, stream rebuild, state recovery | AE-04 |

Required counters: bytes_read, frames_decoded, frames_nonzero, frames_enqueued, frames_submitted, frames_consumed, underrun_count, output_rate, output_channels, backend_state. Sampling an output callback is not proof that a physical speaker produced sound.
