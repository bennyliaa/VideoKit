# sample-host — 14 §9.3 measurements

Method and scripts for the three M0 add-to-app metrics. They need a device (11 device matrix: at least one
mid-range phone) and, for the embedded numbers, the Flutter module AAR. Results go to the M0 test report and the
capability notes. Scripts are Windows PowerShell 5.1 (the development machine); they only call `gradlew`, `flutter`,
`adb` and optionally `bundletool`.

| Script | Metric | Output |
| --- | --- | --- |
| `build_embed_aar.ps1` | Builds the Flutter module AAR (`flutter build aar`) that the embedded flavor packages | `flutter/videokit_embed/build/host/outputs/repo` |
| `measure_size.ps1` | Package size increase: engine vs embedded release, per ABI APK and AAB download size | `results/size.csv` |
| `measure_first_frame.ps1` | First frame of the embedded player, prewarmed vs cold, N runs each, median and P90 | `results/first_frame.csv` |
| `measure_memory.ps1` | PSS of four embed engines (2×2) vs one engine showing four sessions | `results/memory.csv` |

## Prerequisites

1. `flutter pub get` in `flutter/`, then `build_embed_aar.ps1` (writes the local Maven repo of the module; version
   `1.0.0-dev.1`, coordinates `com.videokit.embed:flutter_debug|flutter_release`).
2. Every Gradle call of the scripts passes `-Pvideokit.embedAar=true`, which adds that repository (settings.gradle.kts)
   and the AAR dependency (sample-host/build.gradle.kts). The first time, the AAR and the Flutter engine artifacts it
   brings must be registered in `gradle/dependency-locks` / `gradle/verification-metadata.xml` (`--write-locks
   --write-verification-metadata sha256`) and reviewed like any new dependency (13 §2).
3. Install the variant under test with `adb install` (the scripts install what they build).

## Package size (`measure_size.ps1`)

- Builds `assembleEngineRelease`, `assembleEmbeddedRelease`, `bundleEngineRelease`, `bundleEmbeddedRelease`.
- APKs are split per ABI (arm64-v8a, armeabi-v7a, x86_64; sample-host/build.gradle.kts `splits.abi`); the script
  reports each APK size and the embedded − engine difference per ABI.
- AAB download size: with `BUNDLETOOL_JAR` set, `bundletool build-apks` + `get-size total` for both bundles
  (otherwise the column is `NOT_RUN`).
- Release builds are unsigned for this purpose; size is unaffected by the signature block within a few KB.
- The release builds never contain the Kotlin Fake (14 §11.4), so size is measured on what ships.

## First frame (`measure_first_frame.ps1`)

- Per run: `am force-stop`, clear logcat, cold start `MainActivity` with `--ez prewarm <true|false> --es open embed
  --el openDelayMs 3000` (the delay lets the prewarm finish before the player is requested), then wait for the
  `VideoKitMetrics first_frame kind=PLAYER ms=<n> prewarmed=<b>` logcat line.
- `ms` is measured in-process from `VideoKitPlayerFragment.newInstance` to the first Flutter frame
  (`FlutterUiDisplayListener.onFlutterUiDisplayed` of the embed engine), as 14 §9.3 specifies.
- Default 20 runs per mode; reports median and P90 (nearest-rank).

## Multi-instance memory (`measure_memory.ps1`)

- Modes: `multiview4` (four `VideoKitFlutterView`s, one embed engine each, 2×2) and `multiview1` (one
  `VideoKitFlutterView` with four sessions in one engine).
- Per run: force-stop, start with `--es open <mode>`, wait for `VideoKitMetrics multiview_ready`, settle 5 s, read
  `dumpsys meminfo <package>` TOTAL PSS. Default 5 runs per mode; reports median.
- The single-engine side uses `VideoKitSlotGrid` (UI-05) with one `VideoKitSlot` per session, so the grid's own
  cost is part of the comparison.

## Limits in M0

- In M0 the only engine is the debug-only Kotlin Fake, so first-frame and memory runs use **debug** builds
  (`embeddedDebug`: debug Flutter engine, JIT). They verify the method and give relative numbers (prewarmed vs cold,
  four engines vs one); absolute numbers for the capability notes need release builds with the real engine (VK-M1).
- Package size uses release builds and is representative already.
