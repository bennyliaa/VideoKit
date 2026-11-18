import '../util/enum_codec.dart';

/// Why a command or feature is not supported (04 §4.2, §9.2; values per
/// 04A V1).
///
/// `Unsupported` is a capability answer, not a state error: the UI greys the
/// control out and shows the reason (14 §4.3).
enum UnsupportedReason {
  /// Not implemented by this backend/version.
  notImplemented,

  /// The device lacks the decoder/encoder/feature.
  deviceCapability,

  /// The media format does not allow it.
  format,

  /// Does not apply to the bound media kind (e.g. speed on an image).
  mediaKind,

  /// The source can only be read sequentially (no seeking).
  sourceSequentialOnly,

  /// The host disabled the feature or action.
  hostDisabled,

  /// An optional module (e.g. tracking model) is not installed.
  moduleNotInstalled,

  /// A value is outside the supported range.
  valueOutOfRange,

  /// The referenced track does not exist.
  trackNotFound,

  /// Content is hidden for lock.
  contentLocked,

  /// The feature is hidden by the host configuration (REQ-API-10 ①).
  featureDisabled,

  /// The host's feature gate did not allow it (REQ-API-10 ②).
  featureDenied,

  /// Fallback for reasons added by a newer native Kit.
  unknown;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [unknown].
  static UnsupportedReason fromName(String? name) =>
      enumFromName(values, name, unknown);
}
