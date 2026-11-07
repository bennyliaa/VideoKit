import 'package:flutter/foundation.dart';

import '../error/unsupported_reason.dart';
import '../media/media_source.dart';
import '../media/video_size.dart';
import '../util/collections.dart';
import '../util/enum_codec.dart';
import '../util/undefined.dart';

/// Feature keys for [VideoKitCapabilities.unavailableReasons] (04 §9.2).
enum FeatureKey {
  videoPlayback,
  imageStatic,
  imageAnimated,
  largeImageTiling,
  subtitles,
  multipleAudioTracks,
  speedControl,
  exactSeek,
  singleVideoEdit,
  multiInputConcat,
  fastConcat,
  mosaicMask,
  blurMask,
  faceTracking,
  objectTracking,
  export,
  unknown;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [unknown].
  static FeatureKey fromName(String? name) =>
      enumFromName(values, name, unknown);
}

/// Support level of a container × codec combination.
enum SupportLevel {
  supported,
  partial,
  unsupported;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [unsupported].
  static SupportLevel fromName(String? name) =>
      enumFromName(values, name, unsupported);
}

/// State of an optional module (tracking).
enum ModuleState {
  available,
  unavailable,
  notInstalled,
  degraded;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [unavailable].
  static ModuleState fromName(String? name) =>
      enumFromName(values, name, unavailable);
}

/// One decoder/encoder.
@immutable
final class CodecInfo {
  /// Creates a codec entry.
  const CodecInfo({
    required this.mimeType,
    this.hardwareAccelerated = false,
    this.maxResolution,
    this.maxInstances,
  });

  /// MIME type (e.g. `video/avc`).
  final String mimeType;

  /// Hardware accelerated.
  final bool hardwareAccelerated;

  /// Max resolution.
  final VideoSize? maxResolution;

  /// Declared max instances (upper-bound hint only, 07 §2).
  final int? maxInstances;

  /// Returns a copy with the given fields replaced.
  CodecInfo copyWith({
    String? mimeType,
    bool? hardwareAccelerated,
    Object? maxResolution = undefined,
    Object? maxInstances = undefined,
  }) => CodecInfo(
    mimeType: mimeType ?? this.mimeType,
    hardwareAccelerated: hardwareAccelerated ?? this.hardwareAccelerated,
    maxResolution: pick<VideoSize?>(maxResolution, this.maxResolution),
    maxInstances: pick<int?>(maxInstances, this.maxInstances),
  );

  @override
  bool operator ==(Object other) =>
      other is CodecInfo &&
      other.mimeType == mimeType &&
      other.hardwareAccelerated == hardwareAccelerated &&
      other.maxResolution == maxResolution &&
      other.maxInstances == maxInstances;

  @override
  int get hashCode =>
      Object.hash(mimeType, hardwareAccelerated, maxResolution, maxInstances);

  @override
  String toString() =>
      'CodecInfo($mimeType, hw: $hardwareAccelerated, max: $maxResolution, '
      'instances: $maxInstances)';
}

/// Decoder summary (04 §9.2).
@immutable
final class DecoderSummary {
  /// Creates a summary.
  DecoderSummary({
    List<CodecInfo> video = const [],
    List<CodecInfo> audio = const [],
  }) : video = frozenList(video),
       audio = frozenList(audio);

  /// Video decoders.
  final List<CodecInfo> video;

  /// Audio decoders.
  final List<CodecInfo> audio;

  /// Returns a copy with the given fields replaced.
  DecoderSummary copyWith({List<CodecInfo>? video, List<CodecInfo>? audio}) =>
      DecoderSummary(video: video ?? this.video, audio: audio ?? this.audio);

  @override
  bool operator ==(Object other) =>
      other is DecoderSummary &&
      listEquals(other.video, video) &&
      listEquals(other.audio, audio);

  @override
  int get hashCode => Object.hash(hashList(video), hashList(audio));

  @override
  String toString() => 'DecoderSummary(video: $video, audio: $audio)';
}

/// Container × codec support (04 §9.2).
@immutable
final class FormatSupport {
  /// Creates an entry.
  const FormatSupport({
    required this.container,
    required this.level,
    this.videoCodec,
    this.audioCodec,
    this.reason,
  });

  /// Container (e.g. `mp4`).
  final String container;

  /// Video codec.
  final String? videoCodec;

  /// Audio codec.
  final String? audioCodec;

  /// Level.
  final SupportLevel level;

  /// Reason when not fully supported.
  final UnsupportedReason? reason;

  /// Returns a copy with the given fields replaced.
  FormatSupport copyWith({
    String? container,
    Object? videoCodec = undefined,
    Object? audioCodec = undefined,
    SupportLevel? level,
    Object? reason = undefined,
  }) => FormatSupport(
    container: container ?? this.container,
    videoCodec: pick<String?>(videoCodec, this.videoCodec),
    audioCodec: pick<String?>(audioCodec, this.audioCodec),
    level: level ?? this.level,
    reason: pick<UnsupportedReason?>(reason, this.reason),
  );

  @override
  bool operator ==(Object other) =>
      other is FormatSupport &&
      other.container == container &&
      other.videoCodec == videoCodec &&
      other.audioCodec == audioCodec &&
      other.level == level &&
      other.reason == reason;

  @override
  int get hashCode =>
      Object.hash(container, videoCodec, audioCodec, level, reason);

  @override
  String toString() =>
      'FormatSupport($container/$videoCodec/$audioCodec: ${level.name}'
      '${reason == null ? '' : ', ${reason!.name}'})';
}

/// Playback features (04 §9.2).
@immutable
final class PlaybackFeatures {
  /// Creates features.
  PlaybackFeatures({
    this.subtitles = false,
    this.multipleAudioTracks = false,
    this.speedControl = false,
    this.exactSeek = false,
    List<double> speeds = const [0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
  }) : speeds = frozenList(speeds);

  /// Subtitle tracks.
  final bool subtitles;

  /// Multiple audio tracks.
  final bool multipleAudioTracks;

  /// Speed control.
  final bool speedControl;

  /// Frame-exact seek.
  final bool exactSeek;

  /// Offered speed steps (14 §12).
  final List<double> speeds;

  /// Returns a copy with the given fields replaced.
  PlaybackFeatures copyWith({
    bool? subtitles,
    bool? multipleAudioTracks,
    bool? speedControl,
    bool? exactSeek,
    List<double>? speeds,
  }) => PlaybackFeatures(
    subtitles: subtitles ?? this.subtitles,
    multipleAudioTracks: multipleAudioTracks ?? this.multipleAudioTracks,
    speedControl: speedControl ?? this.speedControl,
    exactSeek: exactSeek ?? this.exactSeek,
    speeds: speeds ?? this.speeds,
  );

  @override
  bool operator ==(Object other) =>
      other is PlaybackFeatures &&
      other.subtitles == subtitles &&
      other.multipleAudioTracks == multipleAudioTracks &&
      other.speedControl == speedControl &&
      other.exactSeek == exactSeek &&
      listEquals(other.speeds, speeds);

  @override
  int get hashCode => Object.hash(
    subtitles,
    multipleAudioTracks,
    speedControl,
    exactSeek,
    hashList(speeds),
  );

  @override
  String toString() =>
      'PlaybackFeatures(subs: $subtitles, audio: $multipleAudioTracks, '
      'speed: $speedControl, exact: $exactSeek, speeds: $speeds)';
}

/// Image features (04 §9.2).
@immutable
final class ImageFeatures {
  /// Creates features.
  ImageFeatures({
    this.staticImages = false,
    this.animatedImages = false,
    this.largeImageTiling = false,
    List<String> formats = const [],
  }) : formats = frozenList(formats);

  /// Static images.
  final bool staticImages;

  /// GIF/WebP animation.
  final bool animatedImages;

  /// Tiled large images.
  final bool largeImageTiling;

  /// Supported formats (MIME).
  final List<String> formats;

  /// Returns a copy with the given fields replaced.
  ImageFeatures copyWith({
    bool? staticImages,
    bool? animatedImages,
    bool? largeImageTiling,
    List<String>? formats,
  }) => ImageFeatures(
    staticImages: staticImages ?? this.staticImages,
    animatedImages: animatedImages ?? this.animatedImages,
    largeImageTiling: largeImageTiling ?? this.largeImageTiling,
    formats: formats ?? this.formats,
  );

  @override
  bool operator ==(Object other) =>
      other is ImageFeatures &&
      other.staticImages == staticImages &&
      other.animatedImages == animatedImages &&
      other.largeImageTiling == largeImageTiling &&
      listEquals(other.formats, formats);

  @override
  int get hashCode => Object.hash(
    staticImages,
    animatedImages,
    largeImageTiling,
    hashList(formats),
  );

  @override
  String toString() =>
      'ImageFeatures(static: $staticImages, animated: $animatedImages, '
      'tiling: $largeImageTiling, $formats)';
}

/// Edit features (04 §9.2).
@immutable
final class EditFeatures {
  /// Creates features.
  const EditFeatures({
    this.singleVideoClips = false,
    this.multiInputConcat = false,
    this.fastConcat = false,
    this.masks = false,
  });

  /// Single-video clip editing.
  final bool singleVideoClips;

  /// Multi-input concatenation.
  final bool multiInputConcat;

  /// Fast (remux) concatenation.
  final bool fastConcat;

  /// Manual masks.
  final bool masks;

  /// Returns a copy with the given fields replaced.
  EditFeatures copyWith({
    bool? singleVideoClips,
    bool? multiInputConcat,
    bool? fastConcat,
    bool? masks,
  }) => EditFeatures(
    singleVideoClips: singleVideoClips ?? this.singleVideoClips,
    multiInputConcat: multiInputConcat ?? this.multiInputConcat,
    fastConcat: fastConcat ?? this.fastConcat,
    masks: masks ?? this.masks,
  );

  @override
  bool operator ==(Object other) =>
      other is EditFeatures &&
      other.singleVideoClips == singleVideoClips &&
      other.multiInputConcat == multiInputConcat &&
      other.fastConcat == fastConcat &&
      other.masks == masks;

  @override
  int get hashCode =>
      Object.hash(singleVideoClips, multiInputConcat, fastConcat, masks);

  @override
  String toString() =>
      'EditFeatures(single: $singleVideoClips, concat: $multiInputConcat, '
      'fast: $fastConcat, masks: $masks)';
}

/// Output format / preset availability (04 §9.2, 08 §8).
@immutable
final class OutputFormat {
  /// Creates an entry.
  const OutputFormat({
    required this.presetId,
    required this.container,
    required this.videoCodec,
    this.audioCodec,
    this.maxLongEdge,
    this.available = true,
    this.reason,
  });

  /// Preset ID.
  final String presetId;

  /// Container.
  final String container;

  /// Video codec.
  final String videoCodec;

  /// Audio codec.
  final String? audioCodec;

  /// Long edge limit; null = same as source.
  final int? maxLongEdge;

  /// Available on this device.
  final bool available;

  /// Reason when unavailable.
  final UnsupportedReason? reason;

  /// Returns a copy with the given fields replaced.
  OutputFormat copyWith({
    String? presetId,
    String? container,
    String? videoCodec,
    Object? audioCodec = undefined,
    Object? maxLongEdge = undefined,
    bool? available,
    Object? reason = undefined,
  }) => OutputFormat(
    presetId: presetId ?? this.presetId,
    container: container ?? this.container,
    videoCodec: videoCodec ?? this.videoCodec,
    audioCodec: pick<String?>(audioCodec, this.audioCodec),
    maxLongEdge: pick<int?>(maxLongEdge, this.maxLongEdge),
    available: available ?? this.available,
    reason: pick<UnsupportedReason?>(reason, this.reason),
  );

  @override
  bool operator ==(Object other) =>
      other is OutputFormat &&
      other.presetId == presetId &&
      other.container == container &&
      other.videoCodec == videoCodec &&
      other.audioCodec == audioCodec &&
      other.maxLongEdge == maxLongEdge &&
      other.available == available &&
      other.reason == reason;

  @override
  int get hashCode => Object.hash(
    presetId,
    container,
    videoCodec,
    audioCodec,
    maxLongEdge,
    available,
    reason,
  );

  @override
  String toString() =>
      'OutputFormat($presetId, $container/$videoCodec/$audioCodec, '
      'long: $maxLongEdge, available: $available)';
}

/// Tracking module status (04 §9.2).
@immutable
final class TrackingStatus {
  /// Creates a status.
  const TrackingStatus({
    this.face = ModuleState.unavailable,
    this.object = ModuleState.unavailable,
    this.suggestedAnalysisLongEdge,
    this.maxConcurrentTargets = 0,
  });

  /// Face module.
  final ModuleState face;

  /// Object module.
  final ModuleState object;

  /// Suggested analysis resolution (long edge).
  final int? suggestedAnalysisLongEdge;

  /// Concurrent targets.
  final int maxConcurrentTargets;

  /// Returns a copy with the given fields replaced.
  TrackingStatus copyWith({
    ModuleState? face,
    ModuleState? object,
    Object? suggestedAnalysisLongEdge = undefined,
    int? maxConcurrentTargets,
  }) => TrackingStatus(
    face: face ?? this.face,
    object: object ?? this.object,
    suggestedAnalysisLongEdge: pick<int?>(
      suggestedAnalysisLongEdge,
      this.suggestedAnalysisLongEdge,
    ),
    maxConcurrentTargets: maxConcurrentTargets ?? this.maxConcurrentTargets,
  );

  @override
  bool operator ==(Object other) =>
      other is TrackingStatus &&
      other.face == face &&
      other.object == object &&
      other.suggestedAnalysisLongEdge == suggestedAnalysisLongEdge &&
      other.maxConcurrentTargets == maxConcurrentTargets;

  @override
  int get hashCode => Object.hash(
    face,
    object,
    suggestedAnalysisLongEdge,
    maxConcurrentTargets,
  );

  @override
  String toString() =>
      'TrackingStatus(face: ${face.name}, object: ${object.name}, '
      'analysis: $suggestedAnalysisLongEdge, targets: $maxConcurrentTargets)';
}

/// What sinks must provide (08 §5).
@immutable
final class SinkRequirements {
  /// Creates requirements.
  const SinkRequirements({
    this.mp4NeedsRandomWriteOrFd = true,
    this.sequentialFallback = false,
  });

  /// MP4 muxing needs random writes or a file descriptor.
  final bool mp4NeedsRandomWriteOrFd;

  /// A sequential-only sink is supported via fMP4/private cache (M4).
  final bool sequentialFallback;

  /// Returns a copy with the given fields replaced.
  SinkRequirements copyWith({
    bool? mp4NeedsRandomWriteOrFd,
    bool? sequentialFallback,
  }) => SinkRequirements(
    mp4NeedsRandomWriteOrFd:
        mp4NeedsRandomWriteOrFd ?? this.mp4NeedsRandomWriteOrFd,
    sequentialFallback: sequentialFallback ?? this.sequentialFallback,
  );

  @override
  bool operator ==(Object other) =>
      other is SinkRequirements &&
      other.mp4NeedsRandomWriteOrFd == mp4NeedsRandomWriteOrFd &&
      other.sequentialFallback == sequentialFallback;

  @override
  int get hashCode => Object.hash(mp4NeedsRandomWriteOrFd, sequentialFallback);

  @override
  String toString() =>
      'SinkRequirements(randomOrFd: $mp4NeedsRandomWriteOrFd, '
      'seqFallback: $sequentialFallback)';
}

/// Per-media probe answer when [CapabilityRequest.source] is set. Playable
/// does not imply encodable or losslessly concatenable (original §5.2).
@immutable
final class MediaProbeCapability {
  /// Creates a probe answer.
  const MediaProbeCapability({
    required this.playable,
    this.fastConcatEligible = false,
    this.reason,
  });

  /// Can be played.
  final bool playable;

  /// Can be concatenated without re-encoding.
  final bool fastConcatEligible;

  /// Reason when not playable.
  final UnsupportedReason? reason;

  /// Returns a copy with the given fields replaced.
  MediaProbeCapability copyWith({
    bool? playable,
    bool? fastConcatEligible,
    Object? reason = undefined,
  }) => MediaProbeCapability(
    playable: playable ?? this.playable,
    fastConcatEligible: fastConcatEligible ?? this.fastConcatEligible,
    reason: pick<UnsupportedReason?>(reason, this.reason),
  );

  @override
  bool operator ==(Object other) =>
      other is MediaProbeCapability &&
      other.playable == playable &&
      other.fastConcatEligible == fastConcatEligible &&
      other.reason == reason;

  @override
  int get hashCode => Object.hash(playable, fastConcatEligible, reason);

  @override
  String toString() =>
      'MediaProbeCapability(playable: $playable, fast: $fastConcatEligible, '
      'reason: ${reason?.name})';
}

/// Capability query (04 §9.2).
@immutable
final class CapabilityRequest {
  /// Creates a request; [source] asks for a media-specific probe.
  const CapabilityRequest({this.source});

  /// Device-wide request.
  static const CapabilityRequest device = CapabilityRequest();

  /// Media to probe, if any.
  final VideoKitMediaSource? source;

  /// Returns a copy with the given fields replaced.
  CapabilityRequest copyWith({Object? source = undefined}) => CapabilityRequest(
    source: pick<VideoKitMediaSource?>(source, this.source),
  );

  @override
  bool operator ==(Object other) =>
      other is CapabilityRequest && other.source == source;

  @override
  int get hashCode => source.hashCode;

  @override
  String toString() => 'CapabilityRequest($source)';
}

/// Capability report (04 §9.2, original §19.4).
@immutable
final class VideoKitCapabilities {
  /// Creates a report.
  VideoKitCapabilities({
    this.schemaVersion = currentSchemaVersion,
    DecoderSummary? decoders,
    List<FormatSupport> containerCodecSupport = const [],
    this.suggestedHardwareVideoSessions = 0,
    this.maxSuggestedResolution = const VideoSize(0, 0),
    this.maxSuggestedFrameRate = 0,
    PlaybackFeatures? playbackFeatures,
    ImageFeatures? imageFeatures,
    this.editFeatures = const EditFeatures(),
    List<CodecInfo> encoders = const [],
    List<OutputFormat> outputFormats = const [],
    this.tracking = const TrackingStatus(),
    this.sinkRequirements = const SinkRequirements(),
    Map<FeatureKey, UnsupportedReason> unavailableReasons = const {},
    this.mediaProbe,
    this.isDemo = false,
  }) : decoders = decoders ?? DecoderSummary(),
       containerCodecSupport = frozenList(containerCodecSupport),
       playbackFeatures = playbackFeatures ?? PlaybackFeatures(),
       imageFeatures = imageFeatures ?? ImageFeatures(),
       encoders = frozenList(encoders),
       outputFormats = frozenList(outputFormats),
       unavailableReasons = frozenMap(unavailableReasons);

  /// Current report schema version.
  static const int currentSchemaVersion = 1;

  /// Schema version.
  final int schemaVersion;

  /// Decoders.
  final DecoderSummary decoders;

  /// Container × codec support.
  final List<FormatSupport> containerCodecSupport;

  /// Suggested concurrent hardware video sessions.
  final int suggestedHardwareVideoSessions;

  /// Suggested max resolution.
  final VideoSize maxSuggestedResolution;

  /// Suggested max frame rate.
  final int maxSuggestedFrameRate;

  /// Playback features.
  final PlaybackFeatures playbackFeatures;

  /// Image features.
  final ImageFeatures imageFeatures;

  /// Edit features.
  final EditFeatures editFeatures;

  /// Encoders.
  final List<CodecInfo> encoders;

  /// Output formats.
  final List<OutputFormat> outputFormats;

  /// Tracking.
  final TrackingStatus tracking;

  /// Sink requirements.
  final SinkRequirements sinkRequirements;

  /// Unavailable features and why.
  final Map<FeatureKey, UnsupportedReason> unavailableReasons;

  /// Media-specific probe when requested.
  final MediaProbeCapability? mediaProbe;

  /// Report produced by a demo backend (values are not measured).
  final bool isDemo;

  /// Returns a copy with the given fields replaced.
  VideoKitCapabilities copyWith({
    int? schemaVersion,
    DecoderSummary? decoders,
    List<FormatSupport>? containerCodecSupport,
    int? suggestedHardwareVideoSessions,
    VideoSize? maxSuggestedResolution,
    int? maxSuggestedFrameRate,
    PlaybackFeatures? playbackFeatures,
    ImageFeatures? imageFeatures,
    EditFeatures? editFeatures,
    List<CodecInfo>? encoders,
    List<OutputFormat>? outputFormats,
    TrackingStatus? tracking,
    SinkRequirements? sinkRequirements,
    Map<FeatureKey, UnsupportedReason>? unavailableReasons,
    Object? mediaProbe = undefined,
    bool? isDemo,
  }) => VideoKitCapabilities(
    schemaVersion: schemaVersion ?? this.schemaVersion,
    decoders: decoders ?? this.decoders,
    containerCodecSupport: containerCodecSupport ?? this.containerCodecSupport,
    suggestedHardwareVideoSessions:
        suggestedHardwareVideoSessions ?? this.suggestedHardwareVideoSessions,
    maxSuggestedResolution:
        maxSuggestedResolution ?? this.maxSuggestedResolution,
    maxSuggestedFrameRate: maxSuggestedFrameRate ?? this.maxSuggestedFrameRate,
    playbackFeatures: playbackFeatures ?? this.playbackFeatures,
    imageFeatures: imageFeatures ?? this.imageFeatures,
    editFeatures: editFeatures ?? this.editFeatures,
    encoders: encoders ?? this.encoders,
    outputFormats: outputFormats ?? this.outputFormats,
    tracking: tracking ?? this.tracking,
    sinkRequirements: sinkRequirements ?? this.sinkRequirements,
    unavailableReasons: unavailableReasons ?? this.unavailableReasons,
    mediaProbe: pick<MediaProbeCapability?>(mediaProbe, this.mediaProbe),
    isDemo: isDemo ?? this.isDemo,
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitCapabilities &&
      other.schemaVersion == schemaVersion &&
      other.decoders == decoders &&
      listEquals(other.containerCodecSupport, containerCodecSupport) &&
      other.suggestedHardwareVideoSessions == suggestedHardwareVideoSessions &&
      other.maxSuggestedResolution == maxSuggestedResolution &&
      other.maxSuggestedFrameRate == maxSuggestedFrameRate &&
      other.playbackFeatures == playbackFeatures &&
      other.imageFeatures == imageFeatures &&
      other.editFeatures == editFeatures &&
      listEquals(other.encoders, encoders) &&
      listEquals(other.outputFormats, outputFormats) &&
      other.tracking == tracking &&
      other.sinkRequirements == sinkRequirements &&
      mapEquals(other.unavailableReasons, unavailableReasons) &&
      other.mediaProbe == mediaProbe &&
      other.isDemo == isDemo;

  @override
  int get hashCode => Object.hashAll([
    schemaVersion,
    decoders,
    hashList(containerCodecSupport),
    suggestedHardwareVideoSessions,
    maxSuggestedResolution,
    maxSuggestedFrameRate,
    playbackFeatures,
    imageFeatures,
    editFeatures,
    hashList(encoders),
    hashList(outputFormats),
    tracking,
    sinkRequirements,
    hashMap(unavailableReasons),
    mediaProbe,
    isDemo,
  ]);

  @override
  String toString() =>
      'VideoKitCapabilities(v$schemaVersion, hwSessions: '
      '$suggestedHardwareVideoSessions, max: $maxSuggestedResolution@'
      '$maxSuggestedFrameRate, formats: ${outputFormats.length}, '
      'tracking: $tracking, unavailable: $unavailableReasons, '
      'probe: $mediaProbe, demo: $isDemo)';
}
