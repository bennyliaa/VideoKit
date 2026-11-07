import '../util/enum_codec.dart';

/// Why a command or feature is not supported (04 §4.2, §9.2).
///
/// `Unsupported` is a capability answer, not a state error: the UI greys the
/// control out and shows the reason (14 §4.3).
enum UnsupportedReason {
  /// The command does not apply to the bound media kind (e.g. speed on an
  /// image).
  notApplicableToMediaKind,

  /// The source cannot seek (sequential-only).
  sourceNotSeekable,

  /// The device lacks the required decoder/encoder/feature.
  notSupportedByDevice,

  /// The feature is not implemented by this backend/version.
  notImplemented,

  /// A required optional module (e.g. tracking model) is not installed.
  moduleUnavailable,

  /// An argument is outside the supported range (speed, volume, …).
  valueOutOfRange,

  /// Referenced track does not exist in the bound media.
  trackNotFound,

  /// Referenced host action is unknown or disabled.
  hostActionUnavailable,

  /// Content is hidden for lock; playback commands are refused.
  contentLocked,

  /// Fallback for reasons added by a newer native Kit.
  unknown;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [unknown].
  static UnsupportedReason fromName(String? name) =>
      enumFromName(values, name, unknown);
}
