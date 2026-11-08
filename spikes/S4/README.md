# S4 — export worker process with FD-proxied input/output and fault injection (15 §4, §1.5, §2.8)

Spike, not part of the Kit build. The main process plays a video through the Kit; each task binds the export worker
(`ExportWorkerService`) that runs Media3 Transformer (8 s clip, 360p, H.264/AAC).

- **Process (attempt 5, option c1, user decision 2026-11-08):** the worker runs in the separate, non-isolated `:export`
  process of the app uid (`bindService`). The main process kills it after every task (`killProcess`), so each task gets
  a fresh process; a hung worker is detected by the watchdog (5 s without progress) and killed the same way.
  Attempts 1–4 used an `isolatedProcess`; it cannot reach any system media service or codec (hwbinder is denied to
  `isolated_app`), see reports\S4 §0.1–§0.5.
- input: `BrokerDataSource` → binder `InputBroker` in the main process (stands in for the host `readAt`; ≤ 64 KiB per
  call; callers are told apart by pid: the main process is refused, the first other caller is pinned; revoked at the end);
- output: a `ParcelFileDescriptor` the main process opened in its cache dir; the worker's muxer (`FdMuxerFactory`,
  after D1 `FdOutputMuxer`) writes to it and gets no path; the main process validates (duration, audio/video, PTS) or
  deletes it.
- demux in the worker (`LOADER`): `EXO` (default from attempt 5) = Media3 ExoPlayer asset loader over the broker;
  `JAVA` = pure-Java Media3 extractors (`JavaExtractorAssetLoader`, attempt 4); `EXTRACTOR` = platform `MediaExtractor`
  (attempt 3).
- decode probe (`DecodeProbe`, attempt 4; off by default, `PROBE=true` runs it in the first task): Java demux of 30 video
  samples, then MediaCodec decoding to ByteBuffers and to an `ImageReader` surface, each step bounded (4 s) and reported.

Faults after the first written video sample: NONE, CANCEL, SIGSEGV (`Process.sendSignal`), OOM, LOOP (busy loop on the
muxer thread; main watchdog: 5 s without progress = hung), KILL (SIGKILL of itself, as by the low-memory killer).
Per task: outcome, detection time, cancel time, kill time, output check, residue, broker reads, main pid unchanged,
longest main playback stall. `process_log.txt` collects how the system handled the worker's crashes.

Reference (read only): D1 d1c14 (`test-workspace\D1`); measured again here, not counted as S4 results.
Build: `./gradlew publishKitMaven` at the root, then `./gradlew -p spikes/S4 :app:assembleDebug`.
Run (emulator-5556 only): `spikes/S4/run_s4.sh <out-dir> <export-input> <playback-sample>`.
Emulator figures do not replace device measurements.
