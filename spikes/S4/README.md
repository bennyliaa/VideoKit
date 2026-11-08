# S4 — isolated export with FD-proxied input/output and fault injection (15 §4, §2.8)

Spike, not part of the Kit build. The main process plays a video through the Kit; each task binds its own
`isolatedProcess` worker (`ExportWorkerService`, `bindIsolatedService`) that runs Media3 Transformer (8 s clip, 360p,
H.264/AAC):

- input: `BrokerDataSource` → binder `InputBroker` in the main process (stands in for the host `readAt`; ≤ 64 KiB per
  call; only the worker uid is served; revoked at the end);
- output: a `ParcelFileDescriptor` the main process opened in its cache dir; the worker's muxer (`FdMuxerFactory`,
  after D1 `FdOutputMuxer`) writes to it and can open no file itself; the main process validates or deletes it.
- demux in the worker (`LOADER`): `JAVA` (default, attempt 4) = pure-Java Media3 extractors (`JavaExtractorAssetLoader`),
  no system service; `EXTRACTOR` = platform `MediaExtractor` (attempt 3, blocks on `media.extractor`); `EXO` =
  ExoPlayer asset loader (attempt 2, blocks on `media.audio_flinger`). Isolated processes reach no ServiceManager media
  service.
- decode probe (`DecodeProbe`, first task only, `PROBE=false` to skip): Java demux of 30 video samples, then MediaCodec
  decoding to ByteBuffers and to an `ImageReader` surface, each step bounded (4 s) and reported.

Faults after the first written video sample: NONE, CANCEL, SIGSEGV (`Process.sendSignal`), OOM, LOOP (busy loop on the
muxer thread; main watchdog: 5 s without progress = hung), KILL (SIGKILL of itself, as by the low-memory killer).
Per task: outcome, detection time, cancel time, output valid/aborted, residue, broker reads, main pid unchanged, longest
main playback stall.

Reference (read only): D1 d1c14 (`test-workspace\D1`); measured again here, not counted as S4 results.
Build: `./gradlew publishKitMaven` at the root, then `./gradlew -p spikes/S4 :app:assembleDebug`.
Run (emulator-5556 only): `spikes/S4/run_s4.sh <out-dir> <export-input> <playback-sample>`.
Emulator figures do not replace device measurements.
