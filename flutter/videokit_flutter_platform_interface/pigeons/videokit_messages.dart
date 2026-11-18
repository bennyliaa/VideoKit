// Pigeon definition of the VideoKit Flutter channel (14 §8.2, protocol rules 14 §8.3).
//
// Regenerate (from flutter/videokit_flutter_platform_interface):
//   dart run pigeon --input pigeons/videokit_messages.dart && dart format lib/src/gen pigeons
// Generated files are committed (13 §2.1): lib/src/gen/messages.g.dart and
// ../videokit_flutter_android/android/src/main/kotlin/com/videokit/flutter/gen/Messages.g.kt.
//
// Conventions:
// - One host method per command (14 §8.1); a new command is a new method (minor protocol version).
// - Enum-like values that may grow (error codes, stages, reasons, visibilities, …) travel as their Kotlin
//   wire names (UPPER_SNAKE, 04A §1.3) in Strings, so that an older peer maps unknown values to the
//   documented fallback instead of failing to decode. Closed state-machine enums are Pigeon enums.
// - All ids are opaque strings; times are microseconds; coordinates are normalized doubles.
// ignore_for_file: one_member_abstracts

import 'package:pigeon/pigeon.dart';

@ConfigurePigeon(
  PigeonOptions(
    dartOut: 'lib/src/gen/messages.g.dart',
    dartPackageName: 'videokit_flutter_platform_interface',
    kotlinOut: '../videokit_flutter_android/android/src/main/kotlin/com/videokit/flutter/gen/Messages.g.kt',
    kotlinOptions: KotlinOptions(package: 'com.videokit.flutter.gen'),
    copyrightHeader: 'pigeons/copyright_header.txt',
  ),
)
// ---------------------------------------------------------------- handshake
/// Sent first by the Dart side (14 §8.3).
class HandshakeRequest {
  HandshakeRequest({
    required this.protocolVersion,
    required this.dartPackageVersion,
    required this.hostActionTimeoutMs,
    required this.navigationTimeoutMs,
    required this.recoveryDecisionTimeoutMs,
    required this.notificationTimeoutMs,
    this.featureGateTimeoutMs,
    this.features,
  });

  /// Channel protocol version of the Dart side (`kChannelProtocolVersion`).
  int protocolVersion;

  /// Version of the Dart plugin package.
  String dartPackageVersion;

  /// `VideoKitConfig.callbackTimeouts` of the Dart host (04A I8); applied by the native runtime.
  int hostActionTimeoutMs;
  int navigationTimeoutMs;
  int recoveryDecisionTimeoutMs;
  int notificationTimeoutMs;

  /// `HostCallbackTimeouts.featureGate` (REQ-API-10); null = the native default (30 s).
  int? featureGateTimeoutMs;

  /// `VideoKitConfig.features` (REQ-API-10): `VideoKitFeature` wire name → `FeatureMode` wire name. Null or missing
  /// entries = ENABLED; unknown names are ignored, unknown modes read as ENABLED. Applied at the first handshake only
  /// (the engine's Kit is created once).
  Map<String, String>? features;
}

/// Answer of the native side.
class HandshakeResponse {
  HandshakeResponse({
    required this.protocolVersion,
    required this.nativeKitVersion,
    required this.apiVersion,
    required this.demoBackend,
  });

  /// Channel protocol version of the native side.
  int protocolVersion;

  /// Version of the native Kit artifacts.
  String nativeKitVersion;

  /// Public API version (`major.minor.patch`).
  String apiVersion;

  /// Whether the native backend is the Fake (UI shows the demo badge).
  bool demoBackend;
}

// ---------------------------------------------------------------- closed enums

enum MediaKindMsg { video, imageStatic, imageAnimated, imageUnknown }

enum SessionPhaseMsg {
  created,
  binding,
  ready,
  playing,
  paused,
  buffering,
  ended,
  errorRecoverable,
  errorFatal,
  releasing,
  released,
}

enum SeekModeMsg { preview, closestSync, exact }

enum CommandResultKind {
  executed,
  rejected,
  superseded,
  unsupported,
  sessionReleased,
}

enum EditPhaseMsg {
  created,
  preparing,
  ready,
  tracking,
  exporting,
  completed,
  failed,
  cancelling,
  cancelled,
  releasing,
  released,
}

enum EditResultKind { applied, rejected, unsupported, projectReleased }

enum ExportResultKind { succeeded, failed, cancelled }

// ---------------------------------------------------------------- common values

/// `VideoKitStableError` (04 §9.1, 04A I4). Enum values are wire names.
class StableErrorMsg {
  StableErrorMsg({
    required this.code,
    required this.stage,
    required this.retryable,
    required this.suggestedAction,
    this.diagnostic,
    required this.params,
  });

  String code;
  String stage;
  bool retryable;
  String suggestedAction;
  String? diagnostic;
  Map<String, String> params;
}

class CommandResultMsg {
  CommandResultMsg({required this.kind, this.error, this.unsupportedReason});

  CommandResultKind kind;
  StableErrorMsg? error;

  /// `UnsupportedReason` wire name when [kind] is unsupported.
  String? unsupportedReason;
}

class TrackInfoMsg {
  TrackInfoMsg({
    required this.id,
    this.language,
    this.label,
    this.codec,
    required this.supported,
    this.channelCount,
  });

  String id;
  String? language;
  String? label;
  String? codec;
  bool supported;

  /// Audio channels; audio tracks only, null when unknown (04A C1).
  int? channelCount;
}

class TransformMsg {
  TransformMsg({
    required this.scale,
    required this.panX,
    required this.panY,
    required this.rotationDeg,
    required this.fitMode,
  });

  double scale;
  double panX;
  double panY;
  int rotationDeg;

  /// `FitMode` wire name.
  String fitMode;
}

class OrientationStateMsg {
  OrientationStateMsg({
    required this.request,
    required this.contentOrientation,
    required this.fullscreen,
  });

  /// `OrientationRequest` wire name.
  String request;

  /// `MediaOrientation` wire name.
  String contentOrientation;
  bool fullscreen;
}

/// `HostIcon`: exactly one of the two fields is set (04A N9).
class HostIconMsg {
  HostIconMsg({this.builtInKey, this.resourceRef});

  String? builtInKey;
  String? resourceRef;
}

class HostActionMsg {
  HostActionMsg({
    required this.actionId,
    required this.labelKey,
    required this.contentDescriptionKey,
    required this.icon,
    required this.enabled,
    required this.selected,
    required this.pending,
    this.badgeText,
    required this.displayPriority,
    required this.placement,
  });

  String actionId;
  String labelKey;
  String contentDescriptionKey;
  HostIconMsg icon;
  bool enabled;
  bool selected;
  bool pending;
  String? badgeText;
  int displayPriority;

  /// `ActionPlacement` wire name.
  String placement;
}

class HostActionStateMsg {
  HostActionStateMsg({
    required this.action,
    required this.pending,
    this.lastStatus,
    this.lastError,
  });

  HostActionMsg action;
  bool pending;

  /// `HostActionStatus` wire name.
  String? lastStatus;
  StableErrorMsg? lastError;
}

// ---------------------------------------------------------------- sessions

class SessionConfigMsg {
  SessionConfigMsg({
    required this.purpose,
    required this.priority,
    required this.initialVisibility,
    required this.initialActiveAudio,
    this.debugTag,
  });

  /// `SessionPurpose` wire name.
  String purpose;

  /// `ResourcePriority` wire name.
  String priority;

  /// `SessionVisibility` wire name.
  String initialVisibility;
  bool initialActiveAudio;
  String? debugTag;
}

/// Media parameters (04A P2); every field optional.
class MediaInfoMsg {
  MediaInfoMsg({
    this.container,
    this.videoCodec,
    this.audioCodec,
    this.width,
    this.height,
    this.frameRate,
    this.bitrateBps,
    this.rotationDeg,
    this.durationUs,
    this.fileSizeBytes,
  });

  String? container;
  String? videoCodec;
  String? audioCodec;
  int? width;
  int? height;
  double? frameRate;
  int? bitrateBps;
  int? rotationDeg;
  int? durationUs;
  int? fileSizeBytes;
}

/// Thumbnail (04A P1): [bytes] with size and type, or [error].
class ThumbnailResultMsg {
  ThumbnailResultMsg({
    this.bytes,
    this.width,
    this.height,
    this.mimeType,
    this.error,
  });

  Uint8List? bytes;
  int? width;
  int? height;
  String? mimeType;
  StableErrorMsg? error;
}

/// Image facts (04A L2); every field optional.
class ImageDetailsMsg {
  ImageDetailsMsg({this.frameCount, this.decodedBytes, this.sampleSize});

  int? frameCount;
  int? decodedBytes;
  int? sampleSize;
}

class SessionStateMsg {
  SessionStateMsg({
    required this.phase,
    this.mediaKind,
    required this.positionUs,
    this.durationUs,
    this.bufferedUs,
    required this.playWhenReady,
    required this.speed,
    required this.volume,
    required this.muted,
    required this.audioTracks,
    required this.subtitleTracks,
    this.selectedAudioTrackId,
    this.selectedSubtitleTrackId,
    required this.transform,
    required this.orientation,
    required this.visibility,
    required this.activeAudio,
    required this.controlsVisible,
    this.error,
    required this.resourcesHeld,
    this.seekingToUs,
    required this.hostActions,
    this.videoWidth,
    this.videoHeight,
    required this.hiddenForLock,
    required this.looping,
    this.imageDetails,
    this.mediaInfo,
  });

  SessionPhaseMsg phase;
  MediaKindMsg? mediaKind;
  int positionUs;
  int? durationUs;
  int? bufferedUs;
  bool playWhenReady;
  double speed;
  double volume;
  bool muted;
  List<TrackInfoMsg> audioTracks;
  List<TrackInfoMsg> subtitleTracks;
  String? selectedAudioTrackId;
  String? selectedSubtitleTrackId;
  TransformMsg transform;
  OrientationStateMsg orientation;

  /// `SessionVisibility` wire name.
  String visibility;
  bool activeAudio;
  bool controlsVisible;
  StableErrorMsg? error;
  bool resourcesHeld;
  int? seekingToUs;
  List<HostActionStateMsg> hostActions;
  int? videoWidth;
  int? videoHeight;
  bool hiddenForLock;

  /// 04A L1.
  bool looping;

  /// 04A L2; null for videos.
  ImageDetailsMsg? imageDetails;

  /// 04A P2.
  MediaInfoMsg? mediaInfo;
}

/// `VideoKitPlaybackState` snapshot (05 §3, 04A I7/I9).
class PlaybackStateMsg {
  PlaybackStateMsg({
    required this.schemaVersion,
    this.sessionId,
    this.mediaToken,
    required this.zoom,
    required this.panX,
    required this.panY,
    required this.rotationDeg,
    required this.fitMode,
    required this.preferredOrientation,
    required this.fullscreen,
    this.positionUs,
    this.speed,
    this.volume,
    this.muted,
    this.subtitleTrackId,
    this.subtitlesEnabled,
    this.audioTrackId,
    this.lastViewedAtEpochMs,
    this.looping,
  });

  int schemaVersion;
  String? sessionId;
  String? mediaToken;
  double zoom;
  double panX;
  double panY;
  int rotationDeg;
  String fitMode;
  String preferredOrientation;
  bool fullscreen;
  int? positionUs;
  double? speed;
  double? volume;
  bool? muted;
  String? subtitleTrackId;
  bool? subtitlesEnabled;
  String? audioTrackId;
  int? lastViewedAtEpochMs;

  /// 04A L3; null = default of the media kind.
  bool? looping;
}

/// One-off session event (14 §3.2). [type] is the event name, for example `SOURCE_RELEASED`.
class EventMsg {
  EventMsg({
    required this.type,
    this.actionId,
    this.error,
    this.noticeCode,
    this.mediaToken,
  });

  String type;
  String? actionId;
  StableErrorMsg? error;
  String? noticeCode;
  String? mediaToken;
}

/// One message of the session update stream (14 §8.1): a full state snapshot and/or one event.
class SessionUpdateMessage {
  SessionUpdateMessage({
    required this.sessionId,
    required this.seq,
    this.state,
    this.event,
  });

  String sessionId;

  /// Monotonic per session; the Dart side drops messages with a seq not greater than the last one (14 §8.3).
  int seq;
  SessionStateMsg? state;
  EventMsg? event;
}

/// Media source descriptor; bytes never cross the channel (14 §8.3).
class MediaSourceMsg {
  MediaSourceMsg({
    required this.mediaToken,
    required this.mediaKind,
    this.displayName,
    this.knownLength,
    this.mimeType,
    this.extension,
    required this.randomAccess,
    required this.sourceRef,
    this.latencyHint,
  });

  String mediaToken;
  MediaKindMsg mediaKind;
  String? displayName;
  int? knownLength;
  String? mimeType;
  String? extension;
  bool randomAccess;

  /// Native source reference: `uri:<uri>`, `registered:<id>` or `demo:<scenarioId>` (04A I15, B9).
  String sourceRef;

  /// `SourceLatency` wire name, `LOCAL` or `SLOW` (04A P6); null or unknown is `LOCAL`.
  String? latencyHint;
}

// ---------------------------------------------------------------- capabilities

class CapabilityRequestMsg {
  CapabilityRequestMsg({this.source});

  MediaSourceMsg? source;
}

class MediaProbeMsg {
  MediaProbeMsg({
    required this.mediaToken,
    required this.playable,
    required this.editable,
    this.fastConcatEligible,
    this.durationUs,
    this.width,
    this.height,
    this.error,
  });

  String mediaToken;

  /// `SupportLevel` wire names.
  String playable;
  String editable;
  bool? fastConcatEligible;
  int? durationUs;
  int? width;
  int? height;
  StableErrorMsg? error;
}

/// Capability summary used by the UI (04 §9.2). Codec and format lists are not carried in protocol 1.
class CapabilitiesMsg {
  CapabilitiesMsg({
    required this.schemaVersion,
    required this.isDemo,
    required this.suggestedHardwareVideoSessions,
    required this.maxWidth,
    required this.maxHeight,
    required this.maxFrameRate,
    required this.subtitles,
    required this.audioTrackSelection,
    required this.speeds,
    required this.exactSeek,
    required this.staticImages,
    required this.animatedImages,
    required this.largeImageTiling,
    required this.singleVideoClips,
    required this.multiInputConcat,
    required this.manualMasks,
    required this.faceTracking,
    required this.objectTracking,
    required this.unavailableReasons,
    this.mediaProbe,
    this.hiddenFeatures,
  });

  int schemaVersion;
  bool isDemo;
  int suggestedHardwareVideoSessions;
  int maxWidth;
  int maxHeight;
  int maxFrameRate;

  /// `SupportLevel` wire name.
  String subtitles;
  bool audioTrackSelection;
  List<double> speeds;
  bool exactSeek;
  bool staticImages;
  bool animatedImages;
  bool largeImageTiling;
  bool singleVideoClips;
  bool multiInputConcat;
  bool manualMasks;

  /// `TrackingModuleStatus` wire names.
  String faceTracking;
  String objectTracking;

  /// `FeatureKey` wire name → `UnsupportedReason` wire name.
  Map<String, String> unavailableReasons;
  MediaProbeMsg? mediaProbe;

  /// `VideoKitCapabilities.hiddenFeatures` (REQ-API-10): `VideoKitFeature` wire names; null = none.
  List<String>? hiddenFeatures;
}

/// Answer of the Dart host's feature gate (REQ-API-10, `FeatureAccess`).
class FeatureAccessMsg {
  FeatureAccessMsg({required this.access, this.badge});

  /// `ALLOWED` or `DENIED`; anything else counts as DENIED.
  String access;

  /// `FeatureBadge` wire name (LOCK, TRIAL) or null.
  String? badge;
}

// ---------------------------------------------------------------- host callbacks

class HostActionRequestMsg {
  HostActionRequestMsg({
    required this.actionId,
    required this.sessionId,
    required this.mediaToken,
  });

  String actionId;
  String sessionId;
  String mediaToken;
}

class HostActionResultMsg {
  HostActionResultMsg({
    required this.status,
    this.updatedAction,
    this.messageKey,
  });

  /// `HostActionStatus` wire name.
  String status;
  HostActionMsg? updatedAction;
  String? messageKey;
}

class NavigationRequestMsg {
  NavigationRequestMsg({
    required this.sessionId,
    this.mediaToken,
    required this.direction,
  });

  String sessionId;
  String? mediaToken;

  /// `NavigationDirection` wire name.
  String direction;
}

/// `VideoKitPlaybackEvent` (06 §4.1). [type] is the event name, for example `POSITION_TICK`.
class PlaybackEventMsg {
  PlaybackEventMsg({
    required this.sessionId,
    required this.type,
    this.positionUs,
    this.fromUs,
    this.toUs,
    this.durationUs,
    this.deltaUs,
    this.phase,
    this.playWhenReady,
    this.visibility,
    this.foreground,
    this.mediaToken,
  });

  String sessionId;
  String type;
  int? positionUs;
  int? fromUs;
  int? toUs;
  int? durationUs;
  int? deltaUs;
  SessionPhaseMsg? phase;
  bool? playWhenReady;
  String? visibility;
  bool? foreground;
  String? mediaToken;
}

// ---------------------------------------------------------------- edit projects

class EditProjectConfigMsg {
  EditProjectConfigMsg({
    required this.allowedPresets,
    required this.trackingAllowed,
    this.initialPositionUs,
  });

  /// `ExportPreset` wire names; empty = all.
  List<String> allowedPresets;
  bool trackingAllowed;
  int? initialPositionUs;
}

class MaskRegionMsg {
  MaskRegionMsg({
    required this.x,
    required this.y,
    required this.width,
    required this.height,
    required this.rotationDeg,
  });

  double x;
  double y;
  double width;
  double height;
  double rotationDeg;
}

/// One edit command (14 §8.2: kind + optional fields). [kind] is the Kotlin class name, e.g. `AddClip`.
class EditCommandMsg {
  EditCommandMsg({
    required this.kind,
    this.sourceId,
    this.clipId,
    this.maskId,
    this.inUs,
    this.outUs,
    this.atUs,
    this.index,
    this.toIndex,
    this.maskType,
    this.region,
    this.startUs,
    this.endUs,
    this.style,
    this.strength,
    this.enabled,
    this.trackingKind,
    this.targetId,
    this.avatar,
  });

  String kind;
  String? sourceId;
  String? clipId;
  String? maskId;
  int? inUs;
  int? outUs;
  int? atUs;
  int? index;
  int? toIndex;
  String? maskType;
  MaskRegionMsg? region;
  int? startUs;
  int? endUs;
  String? style;
  double? strength;
  bool? enabled;

  /// `StartTracking.kind` wire name (FACE / OBJECT); the seed region travels in [region] (04A S4).
  String? trackingKind;
  String? targetId;

  /// `SetMaskAvatar.avatar` (04A E6, M4-B2; kind `SetMaskAvatar`).
  MaskAvatarMsg? avatar;
}

class EditResultMsg {
  EditResultMsg({
    required this.kind,
    this.revision,
    this.createdId,
    this.error,
    this.unsupportedReason,
  });

  EditResultKind kind;
  int? revision;
  String? createdId;
  StableErrorMsg? error;
  String? unsupportedReason;
}

class SourceProbeMsg {
  SourceProbeMsg({
    required this.durationUs,
    required this.width,
    required this.height,
    required this.rotationDeg,
    this.frameRate,
    this.videoCodec,
    this.audioCodec,
    required this.hasAudio,
  });

  int durationUs;
  int width;
  int height;
  int rotationDeg;
  double? frameRate;
  String? videoCodec;
  String? audioCodec;
  bool hasAudio;
}

class EditSourceMsg {
  EditSourceMsg({
    required this.sourceId,
    required this.mediaToken,
    this.displayName,
    this.probe,
    required this.mismatch,
  });

  String sourceId;
  String mediaToken;
  String? displayName;
  SourceProbeMsg? probe;
  bool mismatch;
}

class ClipMsg {
  ClipMsg({
    required this.clipId,
    required this.sourceId,
    required this.inUs,
    required this.outUs,
  });

  String clipId;
  String sourceId;
  int inUs;
  int outUs;
}

class MaskKeyframeMsg {
  MaskKeyframeMsg({
    required this.atUs,
    required this.region,
    required this.source,
    this.quality,
    this.rollDeg,
  });

  int atUs;
  MaskRegionMsg region;

  /// `KeyframeSource` / `CoverageQuality` wire names.
  String source;
  String? quality;

  /// Head roll in degrees for `MaskAvatar.followRotation`; null when unknown (04A E5, M4-B2).
  double? rollDeg;
}

/// `MaskAvatar` (04A E5/E6, M4-B2): the PNG stays with the host, opened by [avatarToken].
class MaskAvatarMsg {
  MaskAvatarMsg({
    required this.avatarToken,
    required this.scale,
    required this.offsetX,
    required this.offsetY,
    required this.followRotation,
  });

  String avatarToken;
  double scale;
  double offsetX;
  double offsetY;
  bool followRotation;
}

class TimeRangeMsg {
  TimeRangeMsg({required this.startUs, required this.endUs});

  int startUs;
  int endUs;
}

class MaskTrackMsg {
  MaskTrackMsg({
    required this.maskId,
    required this.type,
    required this.style,
    required this.strength,
    required this.enabled,
    required this.range,
    required this.keyframes,
    required this.acceptedRanges,
    this.avatar,
  });

  String maskId;
  String type;

  /// `MaskStyle` wire name: MOSAIC, BLUR or IMAGE (M4-B2).
  String style;
  double strength;
  bool enabled;
  TimeRangeMsg range;
  List<MaskKeyframeMsg> keyframes;
  List<TimeRangeMsg> acceptedRanges;

  /// Avatar of style IMAGE (M4-B2).
  MaskAvatarMsg? avatar;
}

class CoverageRangeMsg {
  CoverageRangeMsg({required this.range, required this.quality, this.maskId});

  TimeRangeMsg range;
  String quality;

  /// Set in `PrecheckMsg.uncoveredRanges` (04A T2).
  String? maskId;
}

class TrackingRunMsg {
  TrackingRunMsg({
    required this.maskId,
    required this.status,
    this.progress,
    required this.coverage,
    this.error,
  });

  String maskId;
  String status;
  double? progress;

  /// Empty when there is no coverage report yet.
  List<CoverageRangeMsg> coverage;
  StableErrorMsg? error;
}

class ExportProgressMsg {
  ExportProgressMsg({
    required this.exportId,
    required this.stage,
    this.fraction,
    required this.processedUs,
    this.processedFrames,
    required this.outputBytes,
    this.remainingEstimateUs,
    required this.cancellable,
  });

  String exportId;
  String stage;
  double? fraction;
  int processedUs;
  int? processedFrames;
  int outputBytes;
  int? remainingEstimateUs;
  bool cancellable;
}

class EditStateMsg {
  EditStateMsg({
    required this.phase,
    required this.revision,
    required this.sources,
    required this.clips,
    required this.masks,
    required this.tracking,
    this.exportProgress,
    required this.canUndo,
    required this.canRedo,
    required this.estimateDurationUs,
    this.estimateSizeBytes,
    this.error,
  });

  EditPhaseMsg phase;
  int revision;
  List<EditSourceMsg> sources;
  List<ClipMsg> clips;
  List<MaskTrackMsg> masks;
  List<TrackingRunMsg> tracking;
  ExportProgressMsg? exportProgress;
  bool canUndo;
  bool canRedo;
  int estimateDurationUs;
  int? estimateSizeBytes;
  StableErrorMsg? error;
}

/// Edit project event. [type] is the event name, for example `EXPORT_STAGE_CHANGED`.
class EditEventMsg {
  EditEventMsg({
    required this.type,
    this.sourceId,
    this.maskId,
    this.exportId,
    this.stage,
    this.range,
    this.error,
    this.code,
  });

  String type;
  String? sourceId;
  String? maskId;
  String? exportId;
  String? stage;
  TimeRangeMsg? range;
  StableErrorMsg? error;
  String? code;
}

class EditUpdateMessage {
  EditUpdateMessage({
    required this.projectId,
    required this.seq,
    this.state,
    this.event,
  });

  String projectId;
  int seq;
  EditStateMsg? state;
  EditEventMsg? event;
}

class SerializedProjectMsg {
  SerializedProjectMsg({required this.schemaVersion, required this.json});

  int schemaVersion;
  String json;
}

/// Export request with a reference to a native sink (04A I16): `registered:<id>` or `demo:memory`.
class ExportRequestMsg {
  ExportRequestMsg({
    required this.exportId,
    required this.preset,
    this.fileNameHint,
    required this.sinkRef,
  });

  String exportId;
  String preset;
  String? fileNameHint;
  String sinkRef;
}

class PrecheckMsg {
  PrecheckMsg({
    required this.ok,
    this.writeMode,
    required this.estimateDurationUs,
    this.estimateSizeBytes,
    required this.problems,
    required this.warnings,
    required this.uncoveredRanges,
  });

  bool ok;
  String? writeMode;
  int estimateDurationUs;
  int? estimateSizeBytes;
  List<StableErrorMsg> problems;
  List<String> warnings;

  /// 04A T2: tracked-mask ranges without usable tracking, each with `maskId`.
  List<CoverageRangeMsg> uncoveredRanges;
}

class ExportedMediaMsg {
  ExportedMediaMsg({
    required this.outputToken,
    required this.container,
    required this.extension,
    this.videoCodec,
    this.audioCodec,
    required this.width,
    required this.height,
    required this.rotationDeg,
    required this.durationUs,
    required this.sizeBytes,
    this.frameRate,
    required this.audioPresent,
    required this.createdAtEpochMs,
    required this.sourceTokens,
    required this.editProjectId,
    required this.exportPreset,
    required this.warnings,
    required this.isDemo,
  });

  String outputToken;
  String container;
  String extension;
  String? videoCodec;
  String? audioCodec;
  int width;
  int height;
  int rotationDeg;
  int durationUs;
  int sizeBytes;
  double? frameRate;
  bool audioPresent;
  int createdAtEpochMs;
  List<String> sourceTokens;
  String editProjectId;
  String exportPreset;
  List<String> warnings;
  bool isDemo;
}

class ExportResultMsg {
  ExportResultMsg({
    required this.kind,
    required this.exportId,
    this.media,
    this.error,
    this.stage,
    this.partialOutputRemoved,
  });

  ExportResultKind kind;
  String exportId;
  ExportedMediaMsg? media;
  StableErrorMsg? error;
  String? stage;
  bool? partialOutputRemoved;
}

class TrackingCandidateMsg {
  TrackingCandidateMsg({
    required this.candidateId,
    required this.kind,
    required this.region,
    this.confidence,
  });

  String candidateId;
  String kind;
  MaskRegionMsg region;
  double? confidence;
}

class CandidateResultMsg {
  CandidateResultMsg({required this.candidates, this.error});

  List<TrackingCandidateMsg> candidates;
  StableErrorMsg? error;
}

/// Result of a call that creates an object: [id] on success, otherwise [error].
class CreateResultMsg {
  CreateResultMsg({this.id, this.error});

  String? id;
  StableErrorMsg? error;
}

// ---------------------------------------------------------------- APIs

/// Dart → native (14 §8.2). Unknown session or project ids answer `sessionReleased` / `projectReleased`.
@HostApi()
abstract class VideoKitHostApi {
  HandshakeResponse handshake(HandshakeRequest request);

  @async
  CapabilitiesMsg capabilities(CapabilityRequestMsg request);

  // Sessions
  CreateResultMsg createSession(SessionConfigMsg config);

  /// Observes a session the native host shared (`VideoKitFlutter.shareSession`, add-to-app 14 §9.1). The host keeps
  /// ownership: [release] then only stops observing it. Not shared or released → `error` SESSION_RELEASED.
  CreateResultMsg adoptSession(String sessionId);

  @async
  CommandResultMsg bind(
    String sessionId,
    MediaSourceMsg source,
    PlaybackStateMsg? initial,
    List<HostActionMsg> actions,
  );

  @async
  CommandResultMsg play(String sessionId);

  @async
  CommandResultMsg pause(String sessionId);

  @async
  CommandResultMsg seekTo(String sessionId, int positionUs, SeekModeMsg mode);

  @async
  CommandResultMsg setSpeed(String sessionId, double speed);

  @async
  CommandResultMsg setMuted(String sessionId, bool muted);

  @async
  CommandResultMsg setVolume(String sessionId, double volume);

  @async
  CommandResultMsg selectAudioTrack(String sessionId, String? trackId);

  @async
  CommandResultMsg selectSubtitleTrack(String sessionId, String? trackId);

  @async
  CommandResultMsg setTransform(String sessionId, TransformMsg transform);

  @async
  CommandResultMsg setOrientation(String sessionId, String request);

  @async
  CommandResultMsg setFullscreen(String sessionId, bool fullscreen);

  @async
  CommandResultMsg setVisibility(String sessionId, String visibility);

  @async
  CommandResultMsg setActiveAudio(
    String sessionId,
    bool active,
    int audioEpoch,
  );

  @async
  CommandResultMsg hideContentForLock(String sessionId, bool hidden);

  /// 04A L1; static images answer `unsupported(MEDIA_KIND)`.
  @async
  CommandResultMsg setLooping(String sessionId, bool looping);

  /// 04A P1: JPEG of the frame nearest to [atUs] fitting the size; failures in `ThumbnailResultMsg.error`.
  @async
  ThumbnailResultMsg captureThumbnail(
    String sessionId,
    int atUs,
    int maxWidth,
    int maxHeight,
  );

  @async
  CommandResultMsg requestHostAction(String sessionId, String actionId);

  /// Returns a `NavigationResult` wire name.
  @async
  String requestNavigation(String sessionId, String direction);

  void setControlsVisible(String sessionId, bool visible);

  @async
  void updateHostActions(String sessionId, List<HostActionMsg> actions);

  @async
  PlaybackStateMsg? captureState(String sessionId);

  @async
  PlaybackStateMsg? release(String sessionId);

  // Textures (14 §8.4)
  /// Creates the texture of [sessionId] and attaches its surface; returns the texture id, or -1 when unsupported.
  int createTexture(String sessionId, int width, int height);

  void resizeTexture(String sessionId, int width, int height);

  void disposeTexture(String sessionId);

  // Edit projects
  CreateResultMsg createEditProject(EditProjectConfigMsg config);

  @async
  CreateResultMsg restoreEditProject(
    SerializedProjectMsg serialized,
    EditProjectConfigMsg config,
  );

  /// Returns the source id in [CreateResultMsg.id], or the probe error.
  @async
  CreateResultMsg addSource(String projectId, MediaSourceMsg source);

  @async
  EditResultMsg applyEdit(String projectId, EditCommandMsg command);

  @async
  EditResultMsg undo(String projectId);

  @async
  EditResultMsg redo(String projectId);

  @async
  SerializedProjectMsg? snapshot(String projectId);

  /// Returns the session id of the project's preview session.
  CreateResultMsg previewSession(String projectId);

  @async
  PrecheckMsg checkExport(String projectId, ExportRequestMsg request);

  @async
  ExportResultMsg exportProject(String projectId, ExportRequestMsg request);

  @async
  void cancelExport(String projectId, String exportId);

  @async
  CandidateResultMsg detectCandidates(String projectId, int atUs);

  /// Timeline thumbnail of a project source (04A X2, `VideoKitEditMediaPreview`); null when not available. The
  /// native side answers within the thumbnail hard timeout (04A P5).
  @async
  Uint8List? sourceThumbnail(
    String projectId,
    String sourceId,
    int atUs,
    int maxWidth,
    int maxHeight,
  );

  /// Audio peaks (0–1) of a project source over `[inUs, outUs]` (04A X2); empty without audio or support.
  @async
  List<double> sourceWaveform(
    String projectId,
    String sourceId,
    int inUs,
    int outUs,
    int buckets,
  );

  @async
  void closeEditProject(String projectId);

  /// Releases every session and project created by this engine.
  @async
  void closeAll();
}

/// Native → Dart host callbacks (04 §8). The native side applies the timeouts (04A I8).
@FlutterApi()
abstract class VideoKitCallbacksApi {
  @async
  HostActionResultMsg onHostActionRequested(HostActionRequestMsg request);

  /// Returns a `NavigationResult` wire name.
  @async
  String onNavigationRequested(NavigationRequestMsg request);

  @async
  void onPlaybackSnapshot(PlaybackStateMsg snapshot);

  @async
  void onPlaybackEvent(PlaybackEventMsg event);

  @async
  void onControlsVisibilityChanged(String sessionId, bool visible);

  @async
  void onSourceReleased(String sessionId, String mediaToken);

  /// Returns a `RecoveryDecision` wire name.
  @async
  String onRecoverableError(String sessionId, StableErrorMsg error);

  @async
  void onFatalSessionError(String sessionId, StableErrorMsg error);

  /// `VideoKitHostCallbacks.checkFeature` (REQ-API-10). [feature] is a `VideoKitFeature` wire name; [sessionId] the
  /// session or edit project id, null before one exists. The native timeout is `featureGateTimeoutMs`; an error or
  /// timeout counts as denied.
  @async
  FeatureAccessMsg checkFeature(String feature, String? sessionId);

  /// The surface of [sessionId] was recycled or recreated (14 §8.4); null = no texture.
  void onTextureChanged(String sessionId, int? textureId);
}

/// Native → Dart update streams (14 §8.1). The Dart side dispatches by id.
@EventChannelApi()
abstract class VideoKitEventsApi {
  SessionUpdateMessage sessionUpdates();

  EditUpdateMessage editUpdates();
}
