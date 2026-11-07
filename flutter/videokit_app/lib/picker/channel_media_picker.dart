import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';

import 'media_picker.dart';

/// Platform channel contract of the App's document access (M2 implements
/// the Android side; M0 defines it only, REQ-APP-01/02/03).
///
/// Method channel [documents] (standard codec):
///
/// | method | arguments | result |
/// | --- | --- | --- |
/// | `openDocuments` | `{mimeTypes: List<String>, multiple: bool}` | `List<Map>` of picked documents (`ACTION_OPEN_DOCUMENT`, then `takePersistableUriPermission` for each) |
/// | `reselect` | `{uri: String, mimeTypes: List<String>}` | one document map or null |
/// | `checkAccess` | `{uri: String}` | `"OK"` / `"MISSING"` / `"REVOKED"` |
/// | `releaseAccess` | `{uri: String}` | null (`releasePersistableUriPermission`) |
/// | `createDocument` | `{suggestedName: String, mimeType: String}` | target URI or null (`ACTION_CREATE_DOCUMENT`, export "另存为") |
///
/// Document map: `{uri, displayName, mimeType, sizeBytes?, persistable}`.
///
/// Event channel [incoming]: one `List<Map>` per `ACTION_VIEW` /
/// `ACTION_SEND` / `ACTION_SEND_MULTIPLE` intent (cold start included);
/// `persistable` is false when only a temporary grant was given.
abstract final class AppDocumentChannels {
  /// Method channel name.
  static const String documents = 'com.videokit.app/documents';

  /// Event channel name.
  static const String incoming = 'com.videokit.app/incoming';

  /// MIME filters per kind.
  static const String videoMime = 'video/*';

  /// Image MIME filter.
  static const String imageMime = 'image/*';
}

/// [MediaPickerService] over [AppDocumentChannels] (native side: M2).
final class ChannelMediaPicker implements MediaPickerService {
  /// Creates the picker.
  const ChannelMediaPicker({
    this.methods = const MethodChannel(AppDocumentChannels.documents),
    this.events = const EventChannel(AppDocumentChannels.incoming),
  });

  /// Method channel.
  final MethodChannel methods;

  /// Event channel.
  final EventChannel events;

  static List<String> _mimes(Set<MediaKind> kinds) => [
    if (kinds.contains(MediaKind.video)) AppDocumentChannels.videoMime,
    if (kinds.any((k) => k.isImage)) AppDocumentChannels.imageMime,
  ];

  /// Parses a document map from the platform side.
  static PickedMedia fromMap(Map<Object?, Object?> m) {
    final mime = m['mimeType'] as String?;
    return PickedMedia(
      uri: m['uri']! as String,
      displayName: m['displayName'] as String? ?? '',
      kind: mime == null
          ? MediaKind.imageUnknown
          : (mime.startsWith('video/')
                ? MediaKind.video
                : (mime == 'image/gif' || mime == 'image/webp'
                      ? MediaKind.imageUnknown
                      : MediaKind.imageStatic)),
      mimeType: mime,
      sizeBytes: (m['sizeBytes'] as num?)?.toInt(),
      persistable: m['persistable'] as bool? ?? false,
    );
  }

  @override
  Future<List<PickedMedia>> pick(
    BuildContext context, {
    bool multiple = true,
    Set<MediaKind> kinds = const {MediaKind.video, MediaKind.imageStatic},
  }) async {
    final r = await methods.invokeListMethod<Map<Object?, Object?>>(
      'openDocuments',
      {'mimeTypes': _mimes(kinds), 'multiple': multiple},
    );
    return [for (final m in r ?? const <Map<Object?, Object?>>[]) fromMap(m)];
  }

  @override
  Future<PickedMedia?> reselect(
    BuildContext context,
    PickedMedia previous,
  ) async {
    final r = await methods.invokeMapMethod<Object?, Object?>('reselect', {
      'uri': previous.uri,
      'mimeTypes': _mimes({previous.kind}),
    });
    return r == null ? null : fromMap(r);
  }

  @override
  Future<MediaAccess> checkAccess(String uri) async {
    final r = await methods.invokeMethod<String>('checkAccess', {'uri': uri});
    return switch (r) {
      'OK' => MediaAccess.ok,
      'MISSING' => MediaAccess.missing,
      _ => MediaAccess.revoked,
    };
  }

  @override
  Future<void> releaseAccess(String uri) =>
      methods.invokeMethod<void>('releaseAccess', {'uri': uri});

  @override
  Stream<List<PickedMedia>> get incoming => events.receiveBroadcastStream().map(
    (e) => [
      for (final m in (e as List<Object?>).cast<Map<Object?, Object?>>())
        fromMap(m),
    ],
  );
}
