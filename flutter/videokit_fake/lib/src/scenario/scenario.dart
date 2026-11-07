import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

/// Which part of the media is unsupported in [Scenario.unsupported].
enum UnsupportedPart {
  container,
  videoCodec,
  audioCodec;

  /// Corresponding stable code.
  ErrorCode get errorCode => switch (this) {
    container => ErrorCode.unsupportedContainer,
    videoCodec => ErrorCode.unsupportedVideoCodec,
    audioCodec => ErrorCode.unsupportedAudioCodec,
  };
}

/// A buffering window `[atUs, atUs + forDuration)`.
@immutable
final class BufferingWindow {
  /// Creates a window.
  const BufferingWindow(this.at, this.duration);

  /// Media position where buffering starts.
  final Duration at;

  /// How long (clock time) it lasts.
  final Duration duration;

  @override
  bool operator ==(Object other) =>
      other is BufferingWindow && other.at == at && other.duration == duration;

  @override
  int get hashCode => Object.hash(at, duration);
}

/// A media-time range.
@immutable
final class TimeRange {
  /// Creates `[start, end)`.
  const TimeRange(this.start, this.end);

  /// Start.
  final Duration start;

  /// End.
  final Duration end;

  @override
  bool operator ==(Object other) =>
      other is TimeRange && other.start == start && other.end == end;

  @override
  int get hashCode => Object.hash(start, end);

  @override
  String toString() => 'TimeRange($start, $end)';
}

/// Export failure injection.
@immutable
final class ExportFailure {
  /// Fails when [stage] is reached with [code].
  const ExportFailure(this.stage, this.code);

  /// Stage.
  final ExportStage stage;

  /// Code.
  final ErrorCode code;

  @override
  bool operator ==(Object other) =>
      other is ExportFailure && other.stage == stage && other.code == code;

  @override
  int get hashCode => Object.hash(stage, code);
}

/// Declarative, composable Fake script (14 §11.1).
///
/// ```dart
/// Scenario.slowLoad(const Duration(seconds: 3))
///     .and(Scenario.buffering(at: const Duration(seconds: 20),
///                             duration: const Duration(seconds: 2)));
/// ```
///
/// Later scenarios win for single-valued settings; list settings are
/// concatenated.
@immutable
final class Scenario {
  const Scenario._({
    this.name = 'normal',
    this.loadDelay = const Duration(milliseconds: 300),
    this.seekLatency = const Duration(milliseconds: 120),
    this.bufferingWindows = const [],
    this.unsupportedPart,
    this.corruptAt,
    this.disconnectAt,
    this.resourceExhausted = false,
    this.hostActionTimeouts = const {},
    this.trackingLostRanges = const [],
    this.exportFailure,
    this.exportCancelSlow = false,
    this.fastConcatRejected = false,
    this.openBuffering,
  });

  /// Everything works.
  const Scenario.normal() : this._();

  /// Bind takes [delay].
  const Scenario.slowLoad([Duration delay = const Duration(seconds: 3)])
    : this._(name: 'slowLoad', loadDelay: delay);

  /// Buffering at media position [at] for [duration].
  Scenario.buffering({
    Duration at = const Duration(seconds: 20),
    Duration duration = const Duration(seconds: 2),
  }) : this._(
         name: 'buffering',
         bufferingWindows: [BufferingWindow(at, duration)],
       );

  /// 04A B1: bind succeeds once the tracks are known, then the session
  /// keeps buffering for [duration] before the first frame is ready.
  const Scenario.openBuffering([Duration duration = const Duration(seconds: 3)])
    : this._(name: 'openBuffering', openBuffering: duration);

  /// Bind fails with an `UNSUPPORTED_*` code (fatal).
  const Scenario.unsupported([
    UnsupportedPart part = UnsupportedPart.videoCodec,
  ]) : this._(name: 'unsupported', unsupportedPart: part);

  /// Playback fails with `CORRUPT_MEDIA` at media position [at] (fatal).
  const Scenario.corrupt({Duration at = const Duration(seconds: 45)})
    : this._(name: 'corrupt', corruptAt: at);

  /// Playback fails with `SOURCE_DISCONNECTED` at [at] (recoverable once).
  const Scenario.disconnect({Duration at = const Duration(seconds: 30)})
    : this._(name: 'disconnect', disconnectAt: at);

  /// Bind fails with `DECODER_RESOURCE_EXHAUSTED` (recoverable).
  const Scenario.resourceExhausted()
    : this._(name: 'resourceExhausted', resourceExhausted: true);

  /// The host callback for [actionId] never answers → 10 s timeout →
  /// `HOST_CALLBACK_FAILED`.
  Scenario.hostActionTimeout([String actionId = 'delete'])
    : this._(name: 'hostActionTimeout', hostActionTimeouts: {actionId});

  /// Tracking reports LOST in [ranges] (output timeline).
  const Scenario.trackingLost([
    List<TimeRange> ranges = const [
      TimeRange(Duration(seconds: 4), Duration(seconds: 6)),
    ],
  ]) : this._(name: 'trackingLost', trackingLostRanges: ranges);

  /// Export fails at [stage] with [code].
  Scenario.exportFails({
    ExportStage stage = ExportStage.encoding,
    ErrorCode code = ErrorCode.outputSpaceInsufficient,
  }) : this._(name: 'exportFails', exportFailure: ExportFailure(stage, code));

  /// Export cancellation takes 2 s in `cancelling`.
  const Scenario.exportCancelSlow()
    : this._(name: 'exportCancelSlow', exportCancelSlow: true);

  /// The engine refuses fast (remux) concatenation even though the inputs
  /// match (M4): `checkExport` warns `fast_concat_rejected` and the export
  /// transcodes.
  const Scenario.fastConcatRejected()
    : this._(name: 'fastConcatRejected', fastConcatRejected: true);

  /// Display name (joined with `+` when combined).
  final String name;

  /// Bind latency.
  final Duration loadDelay;

  /// Seek completion latency (preview seeks take half).
  final Duration seekLatency;

  /// Buffering windows.
  final List<BufferingWindow> bufferingWindows;

  /// Unsupported part, if bind should fail.
  final UnsupportedPart? unsupportedPart;

  /// Corrupt position.
  final Duration? corruptAt;

  /// Disconnect position.
  final Duration? disconnectAt;

  /// Bind fails with resource exhaustion.
  final bool resourceExhausted;

  /// Host actions whose callback times out.
  final Set<String> hostActionTimeouts;

  /// LOST ranges for tracking.
  final List<TimeRange> trackingLostRanges;

  /// Export failure.
  final ExportFailure? exportFailure;

  /// Slow cancellation.
  final bool exportCancelSlow;

  /// Fast concatenation refused by the engine.
  final bool fastConcatRejected;

  /// Buffering right after a successful bind (04A B1), if any.
  final Duration? openBuffering;

  /// Bind-time error, if any.
  VideoKitStableError? get bindError {
    if (unsupportedPart != null) {
      return VideoKitStableError(
        code: unsupportedPart!.errorCode,
        stage: ErrorStage.probe,
        suggestedAction: unsupportedPart == UnsupportedPart.audioCodec
            ? SuggestedAction.chooseOtherTrack
            : SuggestedAction.chooseOtherSource,
      );
    }
    if (resourceExhausted) {
      return const VideoKitStableError(
        code: ErrorCode.decoderResourceExhausted,
        stage: ErrorStage.decode,
        retryable: true,
        suggestedAction: SuggestedAction.retry,
      );
    }
    return null;
  }

  /// Combines [other] into this scenario.
  Scenario and(Scenario other) => Scenario._(
    name: other.name == 'normal'
        ? name
        : (name == 'normal' ? other.name : '$name+${other.name}'),
    loadDelay: other.loadDelay != const Scenario.normal().loadDelay
        ? other.loadDelay
        : loadDelay,
    seekLatency: other.seekLatency,
    bufferingWindows: [...bufferingWindows, ...other.bufferingWindows],
    unsupportedPart: other.unsupportedPart ?? unsupportedPart,
    corruptAt: other.corruptAt ?? corruptAt,
    disconnectAt: other.disconnectAt ?? disconnectAt,
    resourceExhausted: resourceExhausted || other.resourceExhausted,
    hostActionTimeouts: {...hostActionTimeouts, ...other.hostActionTimeouts},
    trackingLostRanges: [...trackingLostRanges, ...other.trackingLostRanges],
    exportFailure: other.exportFailure ?? exportFailure,
    exportCancelSlow: exportCancelSlow || other.exportCancelSlow,
    fastConcatRejected: fastConcatRejected || other.fastConcatRejected,
    openBuffering: other.openBuffering ?? openBuffering,
  );

  /// Same as [and].
  Scenario operator +(Scenario other) => and(other);

  @override
  bool operator ==(Object other) =>
      other is Scenario &&
      other.name == name &&
      other.loadDelay == loadDelay &&
      other.seekLatency == seekLatency &&
      listEquals(other.bufferingWindows, bufferingWindows) &&
      other.unsupportedPart == unsupportedPart &&
      other.corruptAt == corruptAt &&
      other.disconnectAt == disconnectAt &&
      other.resourceExhausted == resourceExhausted &&
      setEquals(other.hostActionTimeouts, hostActionTimeouts) &&
      listEquals(other.trackingLostRanges, trackingLostRanges) &&
      other.exportFailure == exportFailure &&
      other.exportCancelSlow == exportCancelSlow &&
      other.fastConcatRejected == fastConcatRejected &&
      other.openBuffering == openBuffering;

  @override
  int get hashCode => Object.hash(
    name,
    loadDelay,
    seekLatency,
    Object.hashAll(bufferingWindows),
    unsupportedPart,
    corruptAt,
    disconnectAt,
    resourceExhausted,
    Object.hashAllUnordered(hostActionTimeouts),
    Object.hashAll(trackingLostRanges),
    exportFailure,
    exportCancelSlow,
    fastConcatRejected,
    openBuffering,
  );

  @override
  String toString() => 'Scenario($name)';
}

/// Named scenario catalogue used by `DemoSourceRef(scenarioId)` and the
/// example app's scenario panel.
abstract final class Scenarios {
  /// ID → scenario for every scenario listed in 14 §11.1.
  static final Map<String, Scenario> catalog = Map.unmodifiable({
    'normal': const Scenario.normal(),
    'slowLoad': const Scenario.slowLoad(),
    'openBuffering': const Scenario.openBuffering(),
    'buffering': Scenario.buffering(),
    'unsupported': const Scenario.unsupported(),
    'unsupportedContainer': const Scenario.unsupported(
      UnsupportedPart.container,
    ),
    'unsupportedAudio': const Scenario.unsupported(UnsupportedPart.audioCodec),
    'corrupt': const Scenario.corrupt(),
    'disconnect': const Scenario.disconnect(),
    'resourceExhausted': const Scenario.resourceExhausted(),
    'hostActionTimeout': Scenario.hostActionTimeout(),
    'trackingLost': const Scenario.trackingLost(),
    'exportFails': Scenario.exportFails(),
    'exportCancelSlow': const Scenario.exportCancelSlow(),
    'fastConcatRejected': const Scenario.fastConcatRejected(),
  });

  /// Looks up [id], falling back to [Scenario.normal].
  static Scenario byId(String id) => catalog[id] ?? const Scenario.normal();
}
