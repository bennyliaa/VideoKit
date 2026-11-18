import '../util/enum_codec.dart';

/// Stable error codes (04 §9.1). Wire names are SCREAMING_SNAKE_CASE.
///
/// New codes are a minor-version change; unknown codes received from a newer
/// native Kit map to [internalErrorRedacted] via [ErrorCode.fromName].
enum ErrorCode {
  sourceNotFound,
  sourcePermissionDenied,
  sourceDisconnected,
  sourceTimeout,
  unsupportedContainer,
  unsupportedVideoCodec,
  unsupportedAudioCodec,
  decoderUnavailable,
  decoderResourceExhausted,
  corruptMedia,
  seekUnsupported,
  outputPermissionDenied,
  outputSpaceInsufficient,
  outputCapabilityUnsupported,
  encoderUnavailable,
  exportFailed,
  trackingModelUnavailable,
  trackingLost,
  cancelled,
  hostCallbackFailed,
  sessionReleased,
  internalErrorRedacted,

  /// Illegal state transition (04A V7).
  invalidState,

  /// Argument out of range or malformed (04A V7).
  invalidArgument,

  /// Snapshot or project schema version not supported (04A V7).
  unsupportedSnapshotVersion,

  /// No usable face in the avatar image (REQ-ED-07, 04A E6, M4-B2).
  avatarNoFace,

  /// The avatar image cannot be decoded or is too large, also a host PNG
  /// (REQ-ED-07, 04A E6, M4-B2).
  avatarImageUnsupported,

  /// The feature is hidden by the host configuration (REQ-API-10 ①,
  /// VK-A2); `params.feature` names it.
  featureDisabled,

  /// The host's feature gate did not allow it, or failed / timed out
  /// (REQ-API-10 ②); `params.feature`, optional `params.badge`.
  featureDenied;

  /// SCREAMING_SNAKE_CASE name shared with Kotlin (`SOURCE_NOT_FOUND`).
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [internalErrorRedacted].
  static ErrorCode fromName(String? name) =>
      enumFromName(values, name, internalErrorRedacted);
}

/// Where an error happened (04 §9.1).
enum ErrorStage {
  probe,
  bind,
  playback,
  decode,
  edit,
  tracking,
  export,
  sink,
  callback,

  /// Dart-side fallback for stages added by a newer native Kit.
  unknown;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [unknown].
  static ErrorStage fromName(String? name) =>
      enumFromName(values, name, unknown);
}

/// Next step the UI may offer for an error (04 §9.1).
enum SuggestedAction {
  none,
  retry,
  chooseOtherTrack,
  reduceQuality,
  freeSpace,
  checkPermission,
  reconnectSource,
  closeOtherSessions,
  correctTracking,
  chooseOtherSource;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [none].
  static SuggestedAction fromName(String? name) =>
      enumFromName(values, name, none);
}
