import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

/// One "最近播放" record (REQ-APP-07). Stores metadata and the module's
/// playback snapshot only — never media content (REQ-APP-08).
@immutable
final class HistoryEntry {
  /// Creates an entry.
  const HistoryEntry({
    required this.id,
    required this.uri,
    required this.displayName,
    required this.kind,
    required this.lastOpenedAtEpochMs,
    this.mimeType,
    this.durationUs,
    this.width,
    this.height,
    this.videoCodec,
    this.lastPositionUs,
    this.playbackState,
    this.thumbnailPath,
    this.persistable = true,
    this.unavailable = false,
    this.favorite = false,
    this.tags = const [],
  });

  /// Stable record ID.
  final String id;

  /// Document URI (`content://…`; `demo:…` in M0).
  final String uri;

  /// File name as reported by the provider.
  final String displayName;

  /// Video or image kind.
  final MediaKind kind;

  /// Last opened (epoch ms).
  final int lastOpenedAtEpochMs;

  /// MIME type.
  final String? mimeType;

  /// Video duration (µs).
  final int? durationUs;

  /// Pixel width.
  final int? width;

  /// Pixel height.
  final int? height;

  /// Video codec (MIME).
  final String? videoCodec;

  /// Last playback position (µs).
  final int? lastPositionUs;

  /// `captureState()` snapshot, passed back as `initialState` (01 §4.13).
  final VideoKitPlaybackState? playbackState;

  /// Small thumbnail file in the app-private directory.
  final String? thumbnailPath;

  /// Long-term access was granted (`takePersistableUriPermission`); false
  /// for entries opened through "打开方式" with a temporary grant.
  final bool persistable;

  /// File moved, deleted or permission lost (shown as "无法打开").
  final bool unavailable;

  /// Favourite (App host action, M2; stored only in the App).
  final bool favorite;

  /// User tags (App host action, M2), in the order added.
  final List<String> tags;

  /// Whether this is an image record.
  bool get isImage => kind.isImage;

  /// Returns a copy with the given fields replaced.
  HistoryEntry copyWith({
    String? uri,
    String? displayName,
    MediaKind? kind,
    int? lastOpenedAtEpochMs,
    String? mimeType,
    int? durationUs,
    int? width,
    int? height,
    String? videoCodec,
    int? lastPositionUs,
    VideoKitPlaybackState? playbackState,
    bool clearPlayback = false,
    String? thumbnailPath,
    bool? persistable,
    bool? unavailable,
    bool? favorite,
    List<String>? tags,
  }) => HistoryEntry(
    id: id,
    uri: uri ?? this.uri,
    displayName: displayName ?? this.displayName,
    kind: kind ?? this.kind,
    lastOpenedAtEpochMs: lastOpenedAtEpochMs ?? this.lastOpenedAtEpochMs,
    mimeType: mimeType ?? this.mimeType,
    durationUs: durationUs ?? this.durationUs,
    width: width ?? this.width,
    height: height ?? this.height,
    videoCodec: videoCodec ?? this.videoCodec,
    lastPositionUs: clearPlayback
        ? null
        : (lastPositionUs ?? this.lastPositionUs),
    playbackState: clearPlayback ? null : (playbackState ?? this.playbackState),
    thumbnailPath: thumbnailPath ?? this.thumbnailPath,
    persistable: persistable ?? this.persistable,
    unavailable: unavailable ?? this.unavailable,
    favorite: favorite ?? this.favorite,
    tags: tags ?? this.tags,
  );

  /// JSON form (schema 1).
  Map<String, Object?> toJson() => {
    'id': id,
    'uri': uri,
    'displayName': displayName,
    'kind': kind.wireName,
    'lastOpenedAtEpochMs': lastOpenedAtEpochMs,
    'mimeType': ?mimeType,
    'durationUs': ?durationUs,
    'width': ?width,
    'height': ?height,
    'videoCodec': ?videoCodec,
    'lastPositionUs': ?lastPositionUs,
    if (playbackState != null) 'playbackState': playbackState!.toJson(),
    'thumbnailPath': ?thumbnailPath,
    'persistable': persistable,
    'unavailable': unavailable,
    if (favorite) 'favorite': true,
    if (tags.isNotEmpty) 'tags': tags,
  };

  /// Parses [json]; unknown or broken snapshots are dropped, never fatal.
  static HistoryEntry fromJson(Map<String, Object?> json) {
    VideoKitPlaybackState? state;
    final raw = json['playbackState'];
    if (raw is Map<String, Object?>) {
      try {
        state = VideoKitPlaybackState.fromJson(raw);
      } on Object {
        state = null;
      }
    }
    return HistoryEntry(
      id: json['id']! as String,
      uri: json['uri']! as String,
      displayName: json['displayName']! as String,
      kind: MediaKind.fromName(json['kind'] as String?),
      lastOpenedAtEpochMs: (json['lastOpenedAtEpochMs']! as num).toInt(),
      mimeType: json['mimeType'] as String?,
      durationUs: (json['durationUs'] as num?)?.toInt(),
      width: (json['width'] as num?)?.toInt(),
      height: (json['height'] as num?)?.toInt(),
      videoCodec: json['videoCodec'] as String?,
      lastPositionUs: (json['lastPositionUs'] as num?)?.toInt(),
      playbackState: state,
      thumbnailPath: json['thumbnailPath'] as String?,
      persistable: json['persistable'] as bool? ?? true,
      unavailable: json['unavailable'] as bool? ?? false,
      favorite: json['favorite'] as bool? ?? false,
      tags: [
        for (final t in json['tags'] as List<Object?>? ?? const [])
          if (t is String) t,
      ],
    );
  }

  @override
  bool operator ==(Object other) =>
      other is HistoryEntry &&
      other.id == id &&
      other.uri == uri &&
      other.displayName == displayName &&
      other.kind == kind &&
      other.lastOpenedAtEpochMs == lastOpenedAtEpochMs &&
      other.mimeType == mimeType &&
      other.durationUs == durationUs &&
      other.width == width &&
      other.height == height &&
      other.videoCodec == videoCodec &&
      other.lastPositionUs == lastPositionUs &&
      other.playbackState == playbackState &&
      other.thumbnailPath == thumbnailPath &&
      other.persistable == persistable &&
      other.unavailable == unavailable &&
      other.favorite == favorite &&
      listEquals(other.tags, tags);

  @override
  int get hashCode => Object.hash(
    id,
    uri,
    displayName,
    kind,
    lastOpenedAtEpochMs,
    mimeType,
    durationUs,
    width,
    height,
    videoCodec,
    lastPositionUs,
    playbackState,
    thumbnailPath,
    persistable,
    unavailable,
    favorite,
    Object.hashAll(tags),
  );

  @override
  String toString() =>
      'HistoryEntry($id, $displayName, ${kind.name}, pos: $lastPositionUs, '
      'unavailable: $unavailable)';
}
