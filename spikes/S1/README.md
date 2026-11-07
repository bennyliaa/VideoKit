# S1 — host readAt → HostDataSource → Media3 (15 §4)

Spike, not part of the Kit build. Plays samples through the real Kit (CoreVideoKit + PlaybackSession +
Media3PlaybackEngine + HostDataSource) from a simulated host `readAt` (`SimulatedHostSource`: local file with injected
latency and throughput limit).

- Conditions: `local`, `lat20`, `lat50`, `lat100`, `throttle4MBps` (20 ms + 4 MB/s).
- Read-ahead sizes compared: 64 KiB, 256 KiB (Kit default), 1 MiB.
- Per run: bind (open + parse), start of playback, rebuffers over 8 s and after seeks, seeks at 25/50/90 % and near the
  end (EXACT), five rapid seeks (Superseded), release time, release 300 ms into an open (cancel), open handles after
  release, host reads/bytes/max read time, PSS before/peak; thumbnail at 30 s through MediaMetadataRetriever.

Build: `./gradlew publishKitMaven` at the root, then `./gradlew -p spikes/S1 :app:assembleDebug`.
Run (emulator-5556 only): `spikes/S1/run_s1.sh <out-dir> <sample>...`.
Emulator figures do not replace device measurements.
