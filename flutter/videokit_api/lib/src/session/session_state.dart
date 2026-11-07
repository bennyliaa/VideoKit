import 'package:flutter/foundation.dart';

import '../error/stable_error.dart';
import '../host/host_action.dart';
import '../media/media_kind.dart';
import '../media/track_info.dart';
import '../media/transform.dart';
import '../util/collections.dart';
import '../util/enum_codec.dart';
import '../util/undefined.dart';

/// Session state machine phase (04 §3.1).
///
/// State-machine enums intentionally have no "unknown" value: a protocol
/// mismatch fails initialisation instead (14 §3.1). [fromName] therefore
/// throws on unknown names.
enum SessionPhase {
  created,
  binding,
  ready,
  playing,
  paused,
  buffering,
  ended,
  errorRecoverable,
  errorFatal,
  releasing,
  released;

  /// Whether a media item is bound and usable for playback commands.
  bool get isBound =>
      this == ready ||
      this == playing ||
      this == paused ||
      this == buffering ||
      this == ended;

  /// Whether this is an error phase.
  bool get isError => this == errorRecoverable || this == errorFatal;

  /// Whether the session is releasing or released.
  bool get isReleasingOrReleased => this == releasing || this == released;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; throws [ArgumentError] when unknown.
  static SessionPhase fromName(String name) {
    for (final v in values) {
      if (v.name == name || v.wireName == name) return v;
    }
    throw ArgumentError.value(name, 'name', 'Unknown SessionPhase');
  }
}

/// Visibility of a session's output, set by the host (04 §4.1 `SetVisibility`,
/// 06 §4.2, 07).
///
/// Named `SessionVisibility` (Kotlin: `Visibility`) to avoid clashing with
/// Flutter's `Visibility` widget.
enum SessionVisibility {
  visible,
  offscreen,
  background;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [offscreen]
  /// (conservative: not audible-visible).
  static SessionVisibility fromName(String? name) =>
      enumFromName(values, name, offscreen);
}

/// Requested orientation policy (06 §4).
enum OrientationRequest {
  auto,
  portrait,
  landscape,
  locked;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [auto].
  static OrientationRequest fromName(String? name) =>
      enumFromName(values, name, auto);
}

/// Natural orientation of the displayed picture.
enum MediaOrientation {
  portrait,
  landscape,
  square,
  unknown;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [unknown].
  static MediaOrientation fromName(String? name) =>
      enumFromName(values, name, unknown);
}

/// Orientation and fullscreen state (04 §3.1 `orientation`).
@immutable
final class OrientationState {
  /// Creates an orientation state.
  const OrientationState({
    this.request = OrientationRequest.auto,
    this.contentOrientation = MediaOrientation.unknown,
    this.fullscreen = false,
  });

  /// Default state.
  static const OrientationState initial = OrientationState();

  /// Last accepted `SetOrientation` request.
  final OrientationRequest request;

  /// Orientation of the bound content (unknown without metadata).
  final MediaOrientation contentOrientation;

  /// Whether fullscreen was requested via `SetFullscreen`.
  final bool fullscreen;

  /// Returns a copy with the given fields replaced.
  OrientationState copyWith({
    OrientationRequest? request,
    MediaOrientation? contentOrientation,
    bool? fullscreen,
  }) => OrientationState(
    request: request ?? this.request,
    contentOrientation: contentOrientation ?? this.contentOrientation,
    fullscreen: fullscreen ?? this.fullscreen,
  );

  @override
  bool operator ==(Object other) =>
      other is OrientationState &&
      other.request == request &&
      other.contentOrientation == contentOrientation &&
      other.fullscreen == fullscreen;

  @override
  int get hashCode => Object.hash(request, contentOrientation, fullscreen);

  @override
  String toString() =>
      'OrientationState(${request.name}, content: ${contentOrientation.name}, '
      'fullscreen: $fullscreen)';
}

/// Full session state snapshot (04 §3.1 + 14 §3.2).
///
/// The native session is the single source of truth; UI never keeps a
/// second state machine.
@immutable
final class VideoKitSessionState {
  /// Creates a state snapshot.
  VideoKitSessionState({
    required this.phase,
    this.mediaKind,
    this.positionUs = 0,
    this.durationUs,
    this.bufferedUs,
    this.seekingToUs,
    this.playWhenReady = false,
    this.speed = 1.0,
    this.volume = 1.0,
    this.muted = false,
    List<TrackInfo> audioTracks = const [],
    List<TrackInfo> subtitleTracks = const [],
    this.selectedAudioTrackId,
    this.selectedSubtitleTrackId,
    this.transform = MediaTransform.identity,
    this.orientation = OrientationState.initial,
    this.visibility = SessionVisibility.visible,
    this.activeAudio = false,
    this.controlsVisible = true,
    this.hiddenForLock = false,
    this.error,
    this.resourcesHeld = false,
    List<HostActionState> hostActions = const [],
    this.looping = false,
    this.imageDetails,
  }) : audioTracks = frozenList(audioTracks),
       subtitleTracks = frozenList(subtitleTracks),
       hostActions = frozenList(hostActions);

  /// Initial state of a freshly created session.
  factory VideoKitSessionState.initial() =>
      VideoKitSessionState(phase: SessionPhase.created);

  /// Phase.
  final SessionPhase phase;

  /// Bound media kind, null before bind.
  final MediaKind? mediaKind;

  /// Position (µs).
  final int positionUs;

  /// Duration (µs), null when unknown or static image.
  final int? durationUs;

  /// Buffered position (µs), null when unknown.
  final int? bufferedUs;

  /// Target of the seek in progress (µs), null when none.
  final int? seekingToUs;

  /// Whether playback proceeds when ready.
  final bool playWhenReady;

  /// Playback speed.
  final double speed;

  /// Session volume 0–1.
  final double volume;

  /// Muted.
  final bool muted;

  /// Audio tracks (empty for images).
  final List<TrackInfo> audioTracks;

  /// Subtitle tracks (empty for images).
  final List<TrackInfo> subtitleTracks;

  /// Selected audio track ID.
  final String? selectedAudioTrackId;

  /// Selected subtitle track ID; null = subtitles off.
  final String? selectedSubtitleTrackId;

  /// Current transform.
  final MediaTransform transform;

  /// Orientation/fullscreen.
  final OrientationState orientation;

  /// Visibility.
  final SessionVisibility visibility;

  /// Whether this session is the active audio source (07 §4).
  final bool activeAudio;

  /// Whether VideoKit controls are visible (written back by the UI layer).
  final bool controlsVisible;

  /// Whether content is hidden by `HideContentForLock` (04A N5).
  final bool hiddenForLock;

  /// Current error, if any.
  final VideoKitStableError? error;

  /// Whether decoder/handles/leases are still held (04 §3.1).
  final bool resourcesHeld;

  /// Whether playback loops (04A L1); set from the media kind at bind
  /// (animated images true, videos false).
  final bool looping;

  /// Image facts the engine knows (04A L2); always null for videos.
  final ImageDetails? imageDetails;

  /// Host actions with pending/result state (14 §3.2).
  final List<HostActionState> hostActions;

  /// Whether playback is effectively running.
  bool get isPlaying => phase == SessionPhase.playing;

  /// Returns a copy with the given fields replaced.
  VideoKitSessionState copyWith({
    SessionPhase? phase,
    Object? mediaKind = undefined,
    int? positionUs,
    Object? durationUs = undefined,
    Object? bufferedUs = undefined,
    Object? seekingToUs = undefined,
    bool? playWhenReady,
    double? speed,
    double? volume,
    bool? muted,
    List<TrackInfo>? audioTracks,
    List<TrackInfo>? subtitleTracks,
    Object? selectedAudioTrackId = undefined,
    Object? selectedSubtitleTrackId = undefined,
    MediaTransform? transform,
    OrientationState? orientation,
    SessionVisibility? visibility,
    bool? activeAudio,
    bool? controlsVisible,
    bool? hiddenForLock,
    Object? error = undefined,
    bool? resourcesHeld,
    List<HostActionState>? hostActions,
    bool? looping,
    Object? imageDetails = undefined,
  }) => VideoKitSessionState(
    phase: phase ?? this.phase,
    mediaKind: pick<MediaKind?>(mediaKind, this.mediaKind),
    positionUs: positionUs ?? this.positionUs,
    durationUs: pick<int?>(durationUs, this.durationUs),
    bufferedUs: pick<int?>(bufferedUs, this.bufferedUs),
    seekingToUs: pick<int?>(seekingToUs, this.seekingToUs),
    playWhenReady: playWhenReady ?? this.playWhenReady,
    speed: speed ?? this.speed,
    volume: volume ?? this.volume,
    muted: muted ?? this.muted,
    audioTracks: audioTracks ?? this.audioTracks,
    subtitleTracks: subtitleTracks ?? this.subtitleTracks,
    selectedAudioTrackId: pick<String?>(
      selectedAudioTrackId,
      this.selectedAudioTrackId,
    ),
    selectedSubtitleTrackId: pick<String?>(
      selectedSubtitleTrackId,
      this.selectedSubtitleTrackId,
    ),
    transform: transform ?? this.transform,
    orientation: orientation ?? this.orientation,
    visibility: visibility ?? this.visibility,
    activeAudio: activeAudio ?? this.activeAudio,
    controlsVisible: controlsVisible ?? this.controlsVisible,
    hiddenForLock: hiddenForLock ?? this.hiddenForLock,
    error: pick<VideoKitStableError?>(error, this.error),
    resourcesHeld: resourcesHeld ?? this.resourcesHeld,
    hostActions: hostActions ?? this.hostActions,
    looping: looping ?? this.looping,
    imageDetails: pick<ImageDetails?>(imageDetails, this.imageDetails),
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitSessionState &&
      other.phase == phase &&
      other.mediaKind == mediaKind &&
      other.positionUs == positionUs &&
      other.durationUs == durationUs &&
      other.bufferedUs == bufferedUs &&
      other.seekingToUs == seekingToUs &&
      other.playWhenReady == playWhenReady &&
      other.speed == speed &&
      other.volume == volume &&
      other.muted == muted &&
      listEquals(other.audioTracks, audioTracks) &&
      listEquals(other.subtitleTracks, subtitleTracks) &&
      other.selectedAudioTrackId == selectedAudioTrackId &&
      other.selectedSubtitleTrackId == selectedSubtitleTrackId &&
      other.transform == transform &&
      other.orientation == orientation &&
      other.visibility == visibility &&
      other.activeAudio == activeAudio &&
      other.controlsVisible == controlsVisible &&
      other.hiddenForLock == hiddenForLock &&
      other.error == error &&
      other.resourcesHeld == resourcesHeld &&
      listEquals(other.hostActions, hostActions) &&
      other.looping == looping &&
      other.imageDetails == imageDetails;

  @override
  int get hashCode => Object.hashAll([
    phase,
    mediaKind,
    positionUs,
    durationUs,
    bufferedUs,
    seekingToUs,
    playWhenReady,
    speed,
    volume,
    muted,
    hashList(audioTracks),
    hashList(subtitleTracks),
    selectedAudioTrackId,
    selectedSubtitleTrackId,
    transform,
    orientation,
    visibility,
    activeAudio,
    controlsVisible,
    hiddenForLock,
    error,
    resourcesHeld,
    hashList(hostActions),
    looping,
    imageDetails,
  ]);

  @override
  String toString() =>
      'VideoKitSessionState(${phase.name}, kind: ${mediaKind?.name}, '
      'pos: $positionUs/$durationUs, buf: $bufferedUs, seek: $seekingToUs, '
      'pwr: $playWhenReady, speed: $speed, vol: $volume, muted: $muted, '
      'audio: ${audioTracks.length}, subs: ${subtitleTracks.length}, '
      'activeAudio: $activeAudio, controls: $controlsVisible, '
      'locked: $hiddenForLock, error: ${error?.code.name}, '
      'held: $resourcesHeld, actions: ${hostActions.length}, '
      'looping: $looping, image: $imageDetails)';
}

/// Image facts for the details panel (04A L2). Every field is optional:
/// the engine fills what it knows and the UI shows only present values.
@immutable
final class ImageDetails {
  /// Creates details.
  const ImageDetails({this.frameCount, this.decodedBytes, this.sampleSize});

  /// Number of frames (1 for a static image), if known.
  final int? frameCount;

  /// Bytes of the decoded bitmap(s) currently held, if known.
  final int? decodedBytes;

  /// Decode subsampling factor (1 = full, 2 = half …), if known.
  final int? sampleSize;

  /// Returns a copy with the given fields replaced.
  ImageDetails copyWith({
    Object? frameCount = undefined,
    Object? decodedBytes = undefined,
    Object? sampleSize = undefined,
  }) => ImageDetails(
    frameCount: pick<int?>(frameCount, this.frameCount),
    decodedBytes: pick<int?>(decodedBytes, this.decodedBytes),
    sampleSize: pick<int?>(sampleSize, this.sampleSize),
  );

  @override
  bool operator ==(Object other) =>
      other is ImageDetails &&
      other.frameCount == frameCount &&
      other.decodedBytes == decodedBytes &&
      other.sampleSize == sampleSize;

  @override
  int get hashCode => Object.hash(frameCount, decodedBytes, sampleSize);

  @override
  String toString() =>
      'ImageDetails(frames: $frameCount, bytes: $decodedBytes, '
      'sample: $sampleSize)';
}
