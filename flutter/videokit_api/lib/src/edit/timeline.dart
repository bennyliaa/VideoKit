import 'package:flutter/foundation.dart';

import '../util/collections.dart';
import '../util/undefined.dart';

/// Probe result of an edit source (08 §2.1).
@immutable
final class SourceProbe {
  /// Creates a probe result.
  const SourceProbe({
    required this.durationUs,
    required this.width,
    required this.height,
    required this.videoCodec,
    this.rotationDeg = 0,
    this.fps,
    this.audioCodec,
    this.hasAudio = false,
  });

  /// Duration (µs).
  final int durationUs;

  /// Coded width.
  final int width;

  /// Coded height.
  final int height;

  /// Rotation metadata (degrees).
  final int rotationDeg;

  /// Frame rate, if constant/known.
  final double? fps;

  /// Video codec.
  final String videoCodec;

  /// Audio codec.
  final String? audioCodec;

  /// Has an audio track.
  final bool hasAudio;

  /// Returns a copy with the given fields replaced.
  SourceProbe copyWith({
    int? durationUs,
    int? width,
    int? height,
    int? rotationDeg,
    Object? fps = undefined,
    String? videoCodec,
    Object? audioCodec = undefined,
    bool? hasAudio,
  }) => SourceProbe(
    durationUs: durationUs ?? this.durationUs,
    width: width ?? this.width,
    height: height ?? this.height,
    rotationDeg: rotationDeg ?? this.rotationDeg,
    fps: pick<double?>(fps, this.fps),
    videoCodec: videoCodec ?? this.videoCodec,
    audioCodec: pick<String?>(audioCodec, this.audioCodec),
    hasAudio: hasAudio ?? this.hasAudio,
  );

  @override
  bool operator ==(Object other) =>
      other is SourceProbe &&
      other.durationUs == durationUs &&
      other.width == width &&
      other.height == height &&
      other.rotationDeg == rotationDeg &&
      other.fps == fps &&
      other.videoCodec == videoCodec &&
      other.audioCodec == audioCodec &&
      other.hasAudio == hasAudio;

  @override
  int get hashCode => Object.hash(
    durationUs,
    width,
    height,
    rotationDeg,
    fps,
    videoCodec,
    audioCodec,
    hasAudio,
  );

  @override
  String toString() =>
      'SourceProbe($durationUs µs, ${width}x$height, rot: $rotationDeg, '
      'fps: $fps, $videoCodec/$audioCodec, audio: $hasAudio)';
}

/// An input of the edit project (08 §2.1).
@immutable
final class EditSource {
  /// Creates an edit source.
  const EditSource({
    required this.sourceId,
    required this.mediaToken,
    required this.probe,
    this.displayName,
    this.mismatch = false,
  });

  /// Project-local source ID.
  final String sourceId;

  /// Host media token.
  final String mediaToken;

  /// Display name.
  final String? displayName;

  /// Probe result.
  final SourceProbe probe;

  /// Probe differs from the restored project record (needs user confirm).
  final bool mismatch;

  /// Returns a copy with the given fields replaced.
  EditSource copyWith({
    String? sourceId,
    String? mediaToken,
    Object? displayName = undefined,
    SourceProbe? probe,
    bool? mismatch,
  }) => EditSource(
    sourceId: sourceId ?? this.sourceId,
    mediaToken: mediaToken ?? this.mediaToken,
    displayName: pick<String?>(displayName, this.displayName),
    probe: probe ?? this.probe,
    mismatch: mismatch ?? this.mismatch,
  );

  @override
  bool operator ==(Object other) =>
      other is EditSource &&
      other.sourceId == sourceId &&
      other.mediaToken == mediaToken &&
      other.displayName == displayName &&
      other.probe == probe &&
      other.mismatch == mismatch;

  @override
  int get hashCode =>
      Object.hash(sourceId, mediaToken, displayName, probe, mismatch);

  @override
  String toString() =>
      'EditSource($sourceId, $mediaToken, $probe, mismatch: $mismatch)';
}

/// A clip on the timeline: `[inUs, outUs)` of a source (08 §2.1).
@immutable
final class EditClip {
  /// Creates a clip.
  const EditClip({
    required this.clipId,
    required this.sourceId,
    required this.inUs,
    required this.outUs,
  });

  /// Clip ID.
  final String clipId;

  /// Source ID.
  final String sourceId;

  /// In point in the source (µs).
  final int inUs;

  /// Out point in the source (µs, exclusive).
  final int outUs;

  /// Clip duration (µs).
  int get durationUs => outUs - inUs;

  /// Returns a copy with the given fields replaced.
  EditClip copyWith({
    String? clipId,
    String? sourceId,
    int? inUs,
    int? outUs,
  }) => EditClip(
    clipId: clipId ?? this.clipId,
    sourceId: sourceId ?? this.sourceId,
    inUs: inUs ?? this.inUs,
    outUs: outUs ?? this.outUs,
  );

  @override
  bool operator ==(Object other) =>
      other is EditClip &&
      other.clipId == clipId &&
      other.sourceId == sourceId &&
      other.inUs == inUs &&
      other.outUs == outUs;

  @override
  int get hashCode => Object.hash(clipId, sourceId, inUs, outUs);

  @override
  String toString() => 'EditClip($clipId, $sourceId, $inUs–$outUs)';
}

/// Timeline: inputs and ordered clips (08 §2.1). Order is playback order;
/// no transitions in V1.0.
@immutable
final class Timeline {
  /// Creates a timeline.
  Timeline({
    List<EditSource> sources = const [],
    List<EditClip> clips = const [],
  }) : sources = frozenList(sources),
       clips = frozenList(clips);

  /// Empty timeline.
  factory Timeline.empty() => Timeline();

  /// Inputs.
  final List<EditSource> sources;

  /// Clips in playback order.
  final List<EditClip> clips;

  /// Total output duration (µs) = sum of clip durations.
  int get durationUs => clips.fold(0, (sum, c) => sum + c.durationUs);

  /// Start of [clipId] on the output timeline (µs), or null.
  int? clipStartUs(String clipId) {
    var t = 0;
    for (final c in clips) {
      if (c.clipId == clipId) return t;
      t += c.durationUs;
    }
    return null;
  }

  /// Source by ID, or null.
  EditSource? sourceById(String sourceId) {
    for (final s in sources) {
      if (s.sourceId == sourceId) return s;
    }
    return null;
  }

  /// Returns a copy with the given fields replaced.
  Timeline copyWith({List<EditSource>? sources, List<EditClip>? clips}) =>
      Timeline(sources: sources ?? this.sources, clips: clips ?? this.clips);

  @override
  bool operator ==(Object other) =>
      other is Timeline &&
      listEquals(other.sources, sources) &&
      listEquals(other.clips, clips);

  @override
  int get hashCode => Object.hash(hashList(sources), hashList(clips));

  @override
  String toString() =>
      'Timeline(${sources.length} sources, ${clips.length} clips, '
      '$durationUs µs)';
}
