# VideoKit Flutter channel protocol — version 1

Copy of the channel protocol (13 §2.1, 14 §8). The normative message definition is
`flutter/videokit_flutter_platform_interface/pigeons/videokit_messages.dart`; `videokit_messages.pigeon.dart`
in this directory is a byte-identical copy, checked by the Gradle task `checkChannelSpec` (part of `check`).
Pigeon 29.1.1 generates the Dart (`videokit_flutter_platform_interface/lib/src/gen/messages.g.dart`) and the Kotlin
(`videokit_flutter_android/android/src/main/kotlin/com/videokit/flutter/gen/Messages.g.kt`) code; both are committed.

## Handshake

- `handshake(HandshakeRequest)` must be the first call of an engine. It carries `protocolVersion` (= 1), the Dart
  package version and the four host callback timeouts in milliseconds (04A I8). Every other call before the
  handshake fails with `FlutterError("VIDEOKIT_NOT_INITIALIZED")`.
- The response carries the native `protocolVersion`, the native Kit version, the API version and `demoBackend`.
  A different protocol version makes `FlutterVideoKit.connect` fail with `VideoKitInitFailure.protocolMismatch`;
  no other call is made.
- No backend (release build without `VideoKitFlutter.setBackend`, 14 §11.4): `FlutterError("VIDEOKIT_NO_BACKEND")`,
  reported in Dart as `VideoKitInitFailure.noBackend`. Debug builds fall back to the testkit Fake
  (`demoBackend = true`; the UI shows the demo badge).

## Calls and results

- One HostApi method per command. Kit results are values, never channel errors: `CommandResultMsg`,
  `EditResultMsg`, `CreateResultMsg(id | error)`, `PrecheckMsg`, `ExportResultMsg` (sealed: SUCCEEDED / FAILED /
  CANCELLED), `CandidateResultMsg`.
- Unknown session id → `SESSION_RELEASED` (late calls after release are normal); unknown project id →
  `PROJECT_RELEASED`. Unexpected native failures → `rejected(INTERNAL_ERROR_REDACTED)` (13 §3.1, no paths or
  content in diagnostics). Only protocol errors are thrown as `FlutterError`.
- Native work runs on `Dispatchers.Default` (never I/O on the platform thread); replies, events and
  FlutterApi calls are sent on the platform thread.

## Wire names

- Open enums (error codes, stages, reasons, visibilities, orientations, presets, features, …) travel as the Kotlin
  UPPER_SNAKE names (04A §1.3). Unknown values map to a documented fallback on the receiving side
  (`INTERNAL_ERROR_REDACTED`, `ErrorStage.UNKNOWN`, `UnsupportedReason.UNKNOWN`, `NavigationResult.FAILED`, …);
  unknown event types are dropped; unknown edit command kinds are rejected with `INVALID_ARGUMENT`.
- Closed protocol enums (result kinds, phases, media kinds, seek modes) are Pigeon enums.
- Integers are 64-bit; durations and positions are microseconds; regions are normalized 0..1.

## Media sources and sinks

- `MediaSourceMsg.sourceRef`: `uri:<content or file uri>`, `registered:<id>` (registered natively with
  `VideoKitFlutter.registerSource`), `demo:<scenarioId>` (Fake backend only). Dart `readAt` sources are not carried
  by protocol 1 (`Unsupported(NOT_IMPLEMENTED)`). Unknown schemes → `rejected(INVALID_ARGUMENT)`.
- `MediaSourceMsg.latencyHint` (04A P6): `SourceLatency` wire name `LOCAL` or `SLOW`; null or an unknown name is
  `LOCAL`. It applies to every reference kind (the native side sets it on the resolved source). An optional field
  added at the end: protocol version stays 1.
- Avatars (04A E5/E6, M4-B2): edit command kind `SetMaskAvatar` with `maskId` and `avatar` (`MaskAvatarMsg`:
  `avatarToken`, `scale`, `offsetX`, `offsetY`, `followRotation`); `MaskTrackMsg.avatar` (null unless style `IMAGE`);
  `MaskTrackMsg.style` may be `IMAGE`; `MaskKeyframeMsg.rollDeg` (null when unknown). Optional fields added at the
  end: protocol version stays 1. Before VK-M5A the native side answers `SetMaskAvatar` and `SetMaskStyle(IMAGE)` with
  `Unsupported(NOT_IMPLEMENTED)`; an unknown style name on the native side reads as MOSAIC.
- Feature switches and gate (REQ-API-10, VK-A2): `HandshakeRequest.features` (`VideoKitFeature` → `FeatureMode` wire
  names, unknown names ignored, unknown modes ENABLED) and `featureGateTimeoutMs` (null = 30 s) configure the engine's
  Kit at its first handshake. The native runtime enforces both at the API entry points (one rule set, `FeatureGate`):
  a hidden feature answers `FEATURE_DISABLED` / `Unsupported(FEATURE_DISABLED)` without asking, a denied one
  `FEATURE_DENIED` / `Unsupported(FEATURE_DENIED)`. The gate is the Dart host: native calls
  `VideoKitCallbacksApi.checkFeature(feature, sessionId)` → `FeatureAccessMsg` (`ALLOWED` / `DENIED`, optional
  `badge`); a Dart error or timeout is denied, and an allowed answer is remembered per session or project. Entries in
  the Dart UI use the Dart `VideoKitFeatureGate` (no channel call). `CapabilitiesMsg.hiddenFeatures` mirrors
  `VideoKitCapabilities.hiddenFeatures`. New fields are optional and added at the end: protocol version stays 1
  (Dart and native ship together; an older Dart side sends no switches).
- `sinkRef`: `registered:<id>` or `demo:memory`. Unknown → precheck problem / export `FAILED(INVALID_ARGUMENT)`.

## Update streams

- `sessionUpdates` and `editUpdates` are Pigeon event channels shared by all objects of an engine; messages carry
  the object id and a per-object `seq` (strictly increasing). The Dart proxy drops messages whose `seq` is not
  greater than the last one (duplicates, reordering) and replaces its state as a whole.
- A new listener first receives the latest state of every live session.
- Sampling (14 §8.3): phase changes and all non-position changes are sent immediately; position-only changes are
  sampled at 15 Hz while seeking and 4 Hz while playing; the last state before RELEASED is always sent.

## Textures

- `createTexture(sessionId, width, height)` creates a `SurfaceProducer` texture and attaches its surface to the
  session; returns the texture id or `-1` (unknown session, no texture registry, surface rejected).
- Dart creates textures lazily through `VideoKitSession.acquireTexture()` leases (04A S7): the first lease creates
  the texture, the last released lease disposes it after 2 s; `resizeTexture` follows the content size.
- Surface recreation is reported with the FlutterApi `onTextureChanged(sessionId, textureId?)`.
- Releasing a session or detaching the engine disposes its textures on the platform thread.

## Host callbacks

- FlutterApi `VideoKitCallbacksApi` mirrors `VideoKitHostCallbacks` with the session id on every call. Timeouts are
  applied natively (04A I8); a missing Dart listener, a Dart exception or a timeout becomes `HOST_CALLBACK_FAILED`.

## Host-owned sessions (add-to-app)

- A native host shares a session with `VideoKitFlutter.shareSession` (bridge: `VideoKitFlutter.share`); Dart observes it
  with `adoptSession(sessionId)` (`FlutterVideoKit.adoptSession`). Not shared or released → `error` SESSION_RELEASED.
- The host keeps ownership: Dart `release` on an adopted session only stops observing it (answers its current state),
  and engine detach never releases it. With a host-owned backend (`VideoKitBackend.ownsKits = false`) every engine
  uses the host's VideoKit, which no engine closes; an engine releases only the sessions and projects it created.

## Embed channel (add-to-app, 14 §9.2)

Definition: `pigeons/embed_messages.dart` (copy: `embed_messages.pigeon.dart`), one channel per embedded engine,
embed protocol version 1. Generated Kotlin lives in `kit/android/videokit-ui-android` (`com.videokit.ui.android.gen`).

- Dart → native (`VideoKitEmbedHostApi`): `attach(dartProtocolVersion)` is the first call of `videokitEmbedMain` and
  returns the current content, theme and strings (pull, so content set before Dart listens is not lost);
  `onControlsVisibilityChanged(visible, animationMs)` (host panel container sync), `onNavigationRequested(direction)`
  → `NavigationResult` wire name, `onFullscreenRequested`, `onEditRequested`, `onContentDisplayed` (first frame).
- Native → Dart (`VideoKitEmbedFlutterApi`): `showContent`, `setTheme` (ARGB colors as unsigned 32-bit ints keyed by
  the Dart token key), `setStrings` (ARB keys); sent only after `attach`.
- Media never travels on this channel: the embedded UI adopts the host session through the plugin channel.

## Engines

- One plugin instance per Flutter engine (add-to-app multi-engine, 14 §8.4). Sessions, projects and textures belong
  to the engine that created them and are released when it detaches. The resource budget is process-wide.
