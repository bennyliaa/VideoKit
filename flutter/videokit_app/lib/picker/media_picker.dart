import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';

/// A document the user picked (REQ-APP-01) or opened with "打开方式"
/// (REQ-APP-02).
@immutable
final class PickedMedia {
  /// Creates an entry.
  const PickedMedia({
    required this.uri,
    required this.displayName,
    required this.kind,
    this.mimeType,
    this.sizeBytes,
    this.persistable = true,
  });

  /// Document URI.
  final String uri;

  /// Display name.
  final String displayName;

  /// Video or image.
  final MediaKind kind;

  /// MIME type.
  final String? mimeType;

  /// Size, if the provider reports it.
  final int? sizeBytes;

  /// Long-term permission taken (false for temporary "打开方式" grants).
  final bool persistable;

  @override
  bool operator ==(Object other) =>
      other is PickedMedia &&
      other.uri == uri &&
      other.displayName == displayName &&
      other.kind == kind &&
      other.mimeType == mimeType &&
      other.sizeBytes == sizeBytes &&
      other.persistable == persistable;

  @override
  int get hashCode =>
      Object.hash(uri, displayName, kind, mimeType, sizeBytes, persistable);

  @override
  String toString() => 'PickedMedia($displayName, $uri)';
}

/// Whether a recorded URI can still be opened.
enum MediaAccess {
  /// Readable.
  ok,

  /// Moved or deleted.
  missing,

  /// Permission lost or never persisted.
  revoked,
}

/// Opening media in the App (REQ-APP-01/02/03). M0: demo list
/// (`DemoMediaPicker`); M2: system document picker through
/// `ChannelMediaPicker` (`ACTION_OPEN_DOCUMENT` + persistable permission,
/// `ACTION_VIEW` / `ACTION_SEND`).
abstract interface class MediaPickerService {
  /// Lets the user pick one or more videos/images. Empty when cancelled.
  Future<List<PickedMedia>> pick(
    BuildContext context, {
    bool multiple = true,
    Set<MediaKind> kinds = const {MediaKind.video, MediaKind.imageStatic},
  });

  /// Lets the user locate a moved/revoked file again ("重新选择").
  Future<PickedMedia?> reselect(BuildContext context, PickedMedia previous);

  /// Whether [uri] can still be opened.
  Future<MediaAccess> checkAccess(String uri);

  /// Releases the long-term permission of [uri] (record deleted, evicted
  /// past the 200 limit, or history cleared).
  Future<void> releaseAccess(String uri);

  /// Media handed over by other apps ("用 VideoKit 打开"), as they arrive.
  Stream<List<PickedMedia>> get incoming;
}
