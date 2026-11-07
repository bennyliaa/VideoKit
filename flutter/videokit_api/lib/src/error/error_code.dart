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
  internalErrorRedacted;

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
  retry,
  chooseOtherTrack,
  reduceQuality,
  freeSpace,
  grantPermission,
  correctTracking,
  chooseOtherSource,
  none;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [none].
  static SuggestedAction fromName(String? name) =>
      enumFromName(values, name, none);
}
