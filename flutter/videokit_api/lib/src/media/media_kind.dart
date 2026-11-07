import '../util/enum_codec.dart';

/// Kind of bound media (04 §5).
enum MediaKind {
  video,
  imageStatic,
  imageAnimated,

  /// Image whose static/animated nature is not yet known; also the fallback
  /// for kinds added by a newer native Kit.
  imageUnknown;

  /// Whether this is any image kind.
  bool get isImage => this != video;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [imageUnknown].
  static MediaKind fromName(String? name) =>
      enumFromName(values, name, imageUnknown);
}

/// Whether the source supports random access reads (04 §5).
enum Seekability {
  randomAccess,
  sequentialOnly;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [sequentialOnly]
  /// (the conservative choice).
  static Seekability fromName(String? name) =>
      enumFromName(values, name, sequentialOnly);
}

/// Why a source handle is opened (04 §5).
enum OpenPurpose {
  probe,
  playback,
  edit,
  export;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [probe].
  static OpenPurpose fromName(String? name) =>
      enumFromName(values, name, probe);
}
