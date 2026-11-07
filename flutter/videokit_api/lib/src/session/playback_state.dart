import 'package:flutter/foundation.dart';

import '../error/error_code.dart';
import '../error/stable_error.dart';
import '../media/transform.dart';
import '../util/undefined.dart';
import 'session_state.dart';

/// Persistable playback preferences snapshot (05 §3, MediaPlayHobby).
///
/// VideoKit never stores scope; it receives this at `bind` and returns the
/// latest value when stable and on `release`. Video-only fields are null in
/// image snapshots. Serialised form carries [schemaVersion] (04 §10).
@immutable
final class VideoKitPlaybackState {
  /// Creates a snapshot.
  const VideoKitPlaybackState({
    this.mediaToken,
    this.zoom = 1.0,
    this.panX = 0.0,
    this.panY = 0.0,
    this.rotationDeg = 0,
    this.fitMode = FitMode.fit,
    this.preferredOrientation = OrientationRequest.auto,
    this.fullscreen = false,
    this.positionUs,
    this.speed,
    this.volume,
    this.muted,
    this.subtitleTrackId,
    this.audioTrackId,
    this.lastViewedAt,
  });

  /// Current snapshot schema major version.
  static const int currentSchemaVersion = 1;

  /// Media token the snapshot belongs to.
  final String? mediaToken;

  /// Zoom factor.
  final double zoom;

  /// Normalised pan X.
  final double panX;

  /// Normalised pan Y.
  final double panY;

  /// Rotation degrees.
  final int rotationDeg;

  /// Fit mode.
  final FitMode fitMode;

  /// Preferred orientation.
  final OrientationRequest preferredOrientation;

  /// Fullscreen.
  final bool fullscreen;

  /// Position (µs); null for images.
  final int? positionUs;

  /// Speed; null for images.
  final double? speed;

  /// Volume; null for images.
  final double? volume;

  /// Muted; null for images.
  final bool? muted;

  /// Subtitle track ID; null = off/unknown.
  final String? subtitleTrackId;

  /// Audio track ID.
  final String? audioTrackId;

  /// When the media was last viewed (UTC).
  final DateTime? lastViewedAt;

  /// The transform part as a [MediaTransform].
  MediaTransform get transform => MediaTransform(
    scale: zoom,
    panX: panX,
    panY: panY,
    rotationDeg: rotationDeg,
    fitMode: fitMode,
  );

  /// Returns a copy with the given fields replaced.
  VideoKitPlaybackState copyWith({
    Object? mediaToken = undefined,
    double? zoom,
    double? panX,
    double? panY,
    int? rotationDeg,
    FitMode? fitMode,
    OrientationRequest? preferredOrientation,
    bool? fullscreen,
    Object? positionUs = undefined,
    Object? speed = undefined,
    Object? volume = undefined,
    Object? muted = undefined,
    Object? subtitleTrackId = undefined,
    Object? audioTrackId = undefined,
    Object? lastViewedAt = undefined,
  }) => VideoKitPlaybackState(
    mediaToken: pick<String?>(mediaToken, this.mediaToken),
    zoom: zoom ?? this.zoom,
    panX: panX ?? this.panX,
    panY: panY ?? this.panY,
    rotationDeg: rotationDeg ?? this.rotationDeg,
    fitMode: fitMode ?? this.fitMode,
    preferredOrientation: preferredOrientation ?? this.preferredOrientation,
    fullscreen: fullscreen ?? this.fullscreen,
    positionUs: pick<int?>(positionUs, this.positionUs),
    speed: pick<double?>(speed, this.speed),
    volume: pick<double?>(volume, this.volume),
    muted: pick<bool?>(muted, this.muted),
    subtitleTrackId: pick<String?>(subtitleTrackId, this.subtitleTrackId),
    audioTrackId: pick<String?>(audioTrackId, this.audioTrackId),
    lastViewedAt: pick<DateTime?>(lastViewedAt, this.lastViewedAt),
  );

  /// JSON form (stable keys, includes `schemaVersion`).
  Map<String, Object?> toJson() => {
    'schemaVersion': currentSchemaVersion,
    'mediaToken': mediaToken,
    'zoom': zoom,
    'panX': panX,
    'panY': panY,
    'rotation': rotationDeg,
    'fitMode': fitMode.wireName,
    'preferredOrientation': preferredOrientation.wireName,
    'fullscreen': fullscreen,
    'positionUs': positionUs,
    'speed': speed,
    'volume': volume,
    'muted': muted,
    'subtitleTrackId': subtitleTrackId,
    'audioTrackId': audioTrackId,
    'lastViewedAt': lastViewedAt?.toUtc().toIso8601String(),
  };

  /// Parses [json]. Older schema versions and missing optional fields use
  /// defaults; an unknown future major version is rejected with a
  /// [VideoKitException] (04 §10).
  static VideoKitPlaybackState fromJson(Map<String, Object?> json) {
    final version = json['schemaVersion'];
    if (version is! int || version > currentSchemaVersion || version < 1) {
      throw const VideoKitException(
        VideoKitStableError.internal(
          stage: ErrorStage.bind,
          diagnostic: 'playback_state_schema_unsupported',
        ),
      );
    }
    double? toDouble(Object? v) => v is num ? v.toDouble() : null;
    final lastViewed = json['lastViewedAt'];
    return VideoKitPlaybackState(
      mediaToken: json['mediaToken'] as String?,
      zoom: toDouble(json['zoom']) ?? 1.0,
      panX: toDouble(json['panX']) ?? 0.0,
      panY: toDouble(json['panY']) ?? 0.0,
      rotationDeg: (json['rotation'] as int?) ?? 0,
      fitMode: FitMode.fromName(json['fitMode'] as String?),
      preferredOrientation: OrientationRequest.fromName(
        json['preferredOrientation'] as String?,
      ),
      fullscreen: (json['fullscreen'] as bool?) ?? false,
      positionUs: json['positionUs'] as int?,
      speed: toDouble(json['speed']),
      volume: toDouble(json['volume']),
      muted: json['muted'] as bool?,
      subtitleTrackId: json['subtitleTrackId'] as String?,
      audioTrackId: json['audioTrackId'] as String?,
      lastViewedAt: lastViewed is String
          ? DateTime.tryParse(lastViewed)?.toUtc()
          : null,
    );
  }

  @override
  bool operator ==(Object other) =>
      other is VideoKitPlaybackState &&
      other.mediaToken == mediaToken &&
      other.zoom == zoom &&
      other.panX == panX &&
      other.panY == panY &&
      other.rotationDeg == rotationDeg &&
      other.fitMode == fitMode &&
      other.preferredOrientation == preferredOrientation &&
      other.fullscreen == fullscreen &&
      other.positionUs == positionUs &&
      other.speed == speed &&
      other.volume == volume &&
      other.muted == muted &&
      other.subtitleTrackId == subtitleTrackId &&
      other.audioTrackId == audioTrackId &&
      other.lastViewedAt == lastViewedAt;

  @override
  int get hashCode => Object.hash(
    mediaToken,
    zoom,
    panX,
    panY,
    rotationDeg,
    fitMode,
    preferredOrientation,
    fullscreen,
    positionUs,
    speed,
    volume,
    muted,
    subtitleTrackId,
    audioTrackId,
    lastViewedAt,
  );

  @override
  String toString() => 'VideoKitPlaybackState(${toJson()})';
}
