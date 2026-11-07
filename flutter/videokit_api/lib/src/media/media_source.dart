import 'package:flutter/foundation.dart';

import '../error/error_code.dart';
import '../util/undefined.dart';
import 'media_kind.dart';

/// Read handle for a Dart-implemented source (04 §5).
///
/// Every read crosses the platform channel when used with the native Kit, so
/// it is only meant for low-bandwidth sources (04 §12.3).
abstract interface class VideoKitReadHandle {
  /// Total length in bytes, or null when unknown.
  int? get length;

  /// Reads up to [length] bytes at [offset] into [target] starting at
  /// [targetOffset]. Returns the number of bytes read, or -1 at EOF.
  /// Short reads are normal.
  Future<int> readAt(
    int offset,
    Uint8List target,
    int targetOffset,
    int length,
  );

  /// Closes the handle. Idempotent.
  Future<void> close();
}

/// Opens read handles for a Dart-implemented source (04 §5).
abstract interface class VideoKitSourceFactory {
  /// Opens a handle for [purpose]. May throw [VideoKitSourceException].
  Future<VideoKitReadHandle> open(OpenPurpose purpose);
}

/// Thrown by host source code to report a typed failure (04 §5).
final class VideoKitSourceException implements Exception {
  /// Creates the exception. [code] should be one of the `SOURCE_*` codes.
  const VideoKitSourceException(this.code, [this.diagnostic]);

  /// Stable code.
  final ErrorCode code;

  /// Redacted summary.
  final String? diagnostic;

  @override
  String toString() => 'VideoKitSourceException(${code.wireName})';
}

/// Where the bytes of a media source come from (04 §12.3, 14 §8.3
/// `MediaSourceMsg.sourceRef`).
///
/// Media bytes never travel through Dart for native-backed refs.
@immutable
sealed class VideoKitSourceRef {
  const VideoKitSourceRef();

  /// The textual form used on the channel (`uri:…`, `registered:…`,
  /// `demo:…`, `dart:`).
  String get wireRef;
}

/// A URI the native side can open directly (file or content URI).
final class UriSourceRef extends VideoKitSourceRef {
  /// Creates a URI ref.
  const UriSourceRef(this.uri);

  /// The URI.
  final String uri;

  @override
  String get wireRef => 'uri:$uri';

  @override
  bool operator ==(Object other) => other is UriSourceRef && other.uri == uri;

  @override
  int get hashCode => Object.hash(UriSourceRef, uri);

  @override
  String toString() => 'UriSourceRef(<redacted>)';
}

/// A source factory the host registered on the native side under [id].
final class RegisteredSourceRef extends VideoKitSourceRef {
  /// Creates a registered ref.
  const RegisteredSourceRef(this.id);

  /// Registration ID.
  final String id;

  @override
  String get wireRef => 'registered:$id';

  @override
  bool operator ==(Object other) =>
      other is RegisteredSourceRef && other.id == id;

  @override
  int get hashCode => Object.hash(RegisteredSourceRef, id);

  @override
  String toString() => 'RegisteredSourceRef($id)';
}

/// Demo/Fake content identified by a scenario ID; never decodes real media.
final class DemoSourceRef extends VideoKitSourceRef {
  /// Creates a demo ref.
  const DemoSourceRef(this.scenarioId);

  /// Scenario ID understood by the Fake backends.
  final String scenarioId;

  @override
  String get wireRef => 'demo:$scenarioId';

  @override
  bool operator ==(Object other) =>
      other is DemoSourceRef && other.scenarioId == scenarioId;

  @override
  int get hashCode => Object.hash(DemoSourceRef, scenarioId);

  @override
  String toString() => 'DemoSourceRef($scenarioId)';
}

/// A source whose `readAt` is implemented in Dart (low bandwidth only).
final class DartSourceRef extends VideoKitSourceRef {
  /// Wraps [factory].
  const DartSourceRef(this.factory);

  /// The Dart factory.
  final VideoKitSourceFactory factory;

  @override
  String get wireRef => 'dart:';

  @override
  bool operator ==(Object other) =>
      other is DartSourceRef && identical(other.factory, factory);

  @override
  int get hashCode => Object.hash(DartSourceRef, identityHashCode(factory));

  @override
  String toString() => 'DartSourceRef(${factory.runtimeType})';
}

/// Media input description (04 §5).
///
/// Carries an opaque [mediaToken] only; never host paths or credentials.
@immutable
final class VideoKitMediaSource {
  /// Creates a media source description.
  const VideoKitMediaSource({
    required this.mediaToken,
    required this.mediaKind,
    required this.sourceRef,
    this.displayName,
    this.knownLength,
    this.mimeType,
    this.extension,
    this.seekability = Seekability.randomAccess,
  });

  /// Opaque host token for this media.
  final String mediaToken;

  /// Media kind.
  final MediaKind mediaKind;

  /// Display-only name.
  final String? displayName;

  /// Length in bytes when known.
  final int? knownLength;

  /// MIME hint (not authoritative).
  final String? mimeType;

  /// Extension hint (not authoritative).
  final String? extension;

  /// Seekability.
  final Seekability seekability;

  /// Where bytes come from (Dart counterpart of `sourceFactory`).
  final VideoKitSourceRef sourceRef;

  /// Returns a copy with the given fields replaced.
  VideoKitMediaSource copyWith({
    String? mediaToken,
    MediaKind? mediaKind,
    VideoKitSourceRef? sourceRef,
    Object? displayName = undefined,
    Object? knownLength = undefined,
    Object? mimeType = undefined,
    Object? extension = undefined,
    Seekability? seekability,
  }) => VideoKitMediaSource(
    mediaToken: mediaToken ?? this.mediaToken,
    mediaKind: mediaKind ?? this.mediaKind,
    sourceRef: sourceRef ?? this.sourceRef,
    displayName: pick<String?>(displayName, this.displayName),
    knownLength: pick<int?>(knownLength, this.knownLength),
    mimeType: pick<String?>(mimeType, this.mimeType),
    extension: pick<String?>(extension, this.extension),
    seekability: seekability ?? this.seekability,
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitMediaSource &&
      other.mediaToken == mediaToken &&
      other.mediaKind == mediaKind &&
      other.sourceRef == sourceRef &&
      other.displayName == displayName &&
      other.knownLength == knownLength &&
      other.mimeType == mimeType &&
      other.extension == extension &&
      other.seekability == seekability;

  @override
  int get hashCode => Object.hash(
    mediaToken,
    mediaKind,
    sourceRef,
    displayName,
    knownLength,
    mimeType,
    extension,
    seekability,
  );

  @override
  String toString() =>
      'VideoKitMediaSource($mediaToken, ${mediaKind.name}, $sourceRef, '
      '${seekability.name})';
}
