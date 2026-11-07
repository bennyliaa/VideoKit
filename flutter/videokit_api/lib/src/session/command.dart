import 'package:flutter/foundation.dart';

import '../media/transform.dart';
import '../util/enum_codec.dart';
import '../util/undefined.dart';
import 'session_state.dart';

/// Seek precision (04 §4.3).
enum SeekMode {
  /// Cheap preview while dragging.
  preview,

  /// Nearest sync frame (default on release of a drag).
  closestSync,

  /// Frame-exact.
  exact;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [closestSync].
  static SeekMode fromName(String? name) =>
      enumFromName(values, name, closestSync);
}

/// Session command (04 §4.1, original §15.5).
///
/// Exhaustive `switch` over this sealed type is how adapters map commands to
/// channel methods; adding a command is a minor version change.
@immutable
sealed class VideoKitCommand {
  const VideoKitCommand();

  /// Stable command kind name, used for de-duplication and diagnostics.
  String get kind;
}

/// Start/resume playback.
final class Play extends VideoKitCommand {
  /// Creates the command.
  const Play();

  @override
  String get kind => 'play';

  @override
  bool operator ==(Object other) => other is Play;

  @override
  int get hashCode => (Play).hashCode;

  @override
  String toString() => 'Play()';
}

/// Pause playback.
final class Pause extends VideoKitCommand {
  /// Creates the command.
  const Pause();

  @override
  String get kind => 'pause';

  @override
  bool operator ==(Object other) => other is Pause;

  @override
  int get hashCode => (Pause).hashCode;

  @override
  String toString() => 'Pause()';
}

/// Seek to [positionUs].
final class SeekTo extends VideoKitCommand {
  /// Creates the command.
  const SeekTo(this.positionUs, {this.mode = SeekMode.closestSync});

  /// Target (µs); clamped by the session to `[0, duration]`.
  final int positionUs;

  /// Precision.
  final SeekMode mode;

  @override
  String get kind => 'seekTo';

  /// Returns a copy with the given fields replaced.
  SeekTo copyWith({int? positionUs, SeekMode? mode}) =>
      SeekTo(positionUs ?? this.positionUs, mode: mode ?? this.mode);

  @override
  bool operator ==(Object other) =>
      other is SeekTo && other.positionUs == positionUs && other.mode == mode;

  @override
  int get hashCode => Object.hash(SeekTo, positionUs, mode);

  @override
  String toString() => 'SeekTo($positionUs, ${mode.name})';
}

/// Set playback speed.
final class SetSpeed extends VideoKitCommand {
  /// Creates the command.
  const SetSpeed(this.speed);

  /// Speed factor.
  final double speed;

  @override
  String get kind => 'setSpeed';

  /// Returns a copy with the given fields replaced.
  SetSpeed copyWith({double? speed}) => SetSpeed(speed ?? this.speed);

  @override
  bool operator ==(Object other) => other is SetSpeed && other.speed == speed;

  @override
  int get hashCode => Object.hash(SetSpeed, speed);

  @override
  String toString() => 'SetSpeed($speed)';
}

/// Mute/unmute the session.
final class SetMuted extends VideoKitCommand {
  /// Creates the command.
  const SetMuted(this.muted);

  /// Muted.
  final bool muted;

  @override
  String get kind => 'setMuted';

  /// Returns a copy with the given fields replaced.
  SetMuted copyWith({bool? muted}) => SetMuted(muted ?? this.muted);

  @override
  bool operator ==(Object other) => other is SetMuted && other.muted == muted;

  @override
  int get hashCode => Object.hash(SetMuted, muted);

  @override
  String toString() => 'SetMuted($muted)';
}

/// Set session volume (0–1).
final class SetVolume extends VideoKitCommand {
  /// Creates the command.
  const SetVolume(this.volume);

  /// Volume 0–1.
  final double volume;

  @override
  String get kind => 'setVolume';

  /// Returns a copy with the given fields replaced.
  SetVolume copyWith({double? volume}) => SetVolume(volume ?? this.volume);

  @override
  bool operator ==(Object other) =>
      other is SetVolume && other.volume == volume;

  @override
  int get hashCode => Object.hash(SetVolume, volume);

  @override
  String toString() => 'SetVolume($volume)';
}

/// Select an audio track (null = default).
final class SelectAudioTrack extends VideoKitCommand {
  /// Creates the command.
  const SelectAudioTrack(this.trackId);

  /// Track ID or null.
  final String? trackId;

  @override
  String get kind => 'selectAudioTrack';

  /// Returns a copy with the given fields replaced.
  SelectAudioTrack copyWith({Object? trackId = undefined}) =>
      SelectAudioTrack(pick<String?>(trackId, this.trackId));

  @override
  bool operator ==(Object other) =>
      other is SelectAudioTrack && other.trackId == trackId;

  @override
  int get hashCode => Object.hash(SelectAudioTrack, trackId);

  @override
  String toString() => 'SelectAudioTrack($trackId)';
}

/// Select a subtitle track (null = subtitles off).
final class SelectSubtitleTrack extends VideoKitCommand {
  /// Creates the command.
  const SelectSubtitleTrack(this.trackId);

  /// Track ID or null for off.
  final String? trackId;

  @override
  String get kind => 'selectSubtitleTrack';

  /// Returns a copy with the given fields replaced.
  SelectSubtitleTrack copyWith({Object? trackId = undefined}) =>
      SelectSubtitleTrack(pick<String?>(trackId, this.trackId));

  @override
  bool operator ==(Object other) =>
      other is SelectSubtitleTrack && other.trackId == trackId;

  @override
  int get hashCode => Object.hash(SelectSubtitleTrack, trackId);

  @override
  String toString() => 'SelectSubtitleTrack($trackId)';
}

/// Store a new transform (UI computes it from gestures).
final class SetTransform extends VideoKitCommand {
  /// Creates the command.
  const SetTransform(this.transform);

  /// Transform.
  final MediaTransform transform;

  @override
  String get kind => 'setTransform';

  /// Returns a copy with the given fields replaced.
  SetTransform copyWith({MediaTransform? transform}) =>
      SetTransform(transform ?? this.transform);

  @override
  bool operator ==(Object other) =>
      other is SetTransform && other.transform == transform;

  @override
  int get hashCode => Object.hash(SetTransform, transform);

  @override
  String toString() => 'SetTransform($transform)';
}

/// Request an orientation policy.
final class SetOrientation extends VideoKitCommand {
  /// Creates the command.
  const SetOrientation(this.request);

  /// Policy.
  final OrientationRequest request;

  @override
  String get kind => 'setOrientation';

  /// Returns a copy with the given fields replaced.
  SetOrientation copyWith({OrientationRequest? request}) =>
      SetOrientation(request ?? this.request);

  @override
  bool operator ==(Object other) =>
      other is SetOrientation && other.request == request;

  @override
  int get hashCode => Object.hash(SetOrientation, request);

  @override
  String toString() => 'SetOrientation(${request.name})';
}

/// Record fullscreen intent (the host performs the actual window change).
final class SetFullscreen extends VideoKitCommand {
  /// Creates the command.
  const SetFullscreen(this.fullscreen);

  /// Fullscreen.
  final bool fullscreen;

  @override
  String get kind => 'setFullscreen';

  /// Returns a copy with the given fields replaced.
  SetFullscreen copyWith({bool? fullscreen}) =>
      SetFullscreen(fullscreen ?? this.fullscreen);

  @override
  bool operator ==(Object other) =>
      other is SetFullscreen && other.fullscreen == fullscreen;

  @override
  int get hashCode => Object.hash(SetFullscreen, fullscreen);

  @override
  String toString() => 'SetFullscreen($fullscreen)';
}

/// Report visibility of the session output.
final class SetVisibility extends VideoKitCommand {
  /// Creates the command.
  const SetVisibility(this.visibility);

  /// Visibility.
  final SessionVisibility visibility;

  @override
  String get kind => 'setVisibility';

  /// Returns a copy with the given fields replaced.
  SetVisibility copyWith({SessionVisibility? visibility}) =>
      SetVisibility(visibility ?? this.visibility);

  @override
  bool operator ==(Object other) =>
      other is SetVisibility && other.visibility == visibility;

  @override
  int get hashCode => Object.hash(SetVisibility, visibility);

  @override
  String toString() => 'SetVisibility(${visibility.name})';
}

/// Make this session the (non-)active audio source; commands with an
/// [audioEpoch] lower than the last accepted one are stale (07 §4).
final class SetActiveAudio extends VideoKitCommand {
  /// Creates the command.
  const SetActiveAudio(this.active, this.audioEpoch);

  /// Active.
  final bool active;

  /// Host-maintained monotonically increasing epoch.
  final int audioEpoch;

  @override
  String get kind => 'setActiveAudio';

  /// Returns a copy with the given fields replaced.
  SetActiveAudio copyWith({bool? active, int? audioEpoch}) =>
      SetActiveAudio(active ?? this.active, audioEpoch ?? this.audioEpoch);

  @override
  bool operator ==(Object other) =>
      other is SetActiveAudio &&
      other.active == active &&
      other.audioEpoch == audioEpoch;

  @override
  int get hashCode => Object.hash(SetActiveAudio, active, audioEpoch);

  @override
  String toString() => 'SetActiveAudio($active, epoch: $audioEpoch)';
}

/// Hide/show content for app lock; lock wins over other commands (06 §4.2).
final class HideContentForLock extends VideoKitCommand {
  /// Creates the command.
  const HideContentForLock(this.hidden);

  /// Hidden.
  final bool hidden;

  @override
  String get kind => 'hideContentForLock';

  /// Returns a copy with the given fields replaced.
  HideContentForLock copyWith({bool? hidden}) =>
      HideContentForLock(hidden ?? this.hidden);

  @override
  bool operator ==(Object other) =>
      other is HideContentForLock && other.hidden == hidden;

  @override
  int get hashCode => Object.hash(HideContentForLock, hidden);

  @override
  String toString() => 'HideContentForLock($hidden)';
}

/// Trigger a host action (Dart addition, see report): VideoKit calls the
/// host's `onHostActionRequested`; duplicate clicks while one is in flight
/// are merged (04 §7).
final class InvokeHostAction extends VideoKitCommand {
  /// Creates the command.
  const InvokeHostAction(this.actionId);

  /// Action ID.
  final String actionId;

  @override
  String get kind => 'invokeHostAction';

  /// Returns a copy with the given fields replaced.
  InvokeHostAction copyWith({String? actionId}) =>
      InvokeHostAction(actionId ?? this.actionId);

  @override
  bool operator ==(Object other) =>
      other is InvokeHostAction && other.actionId == actionId;

  @override
  int get hashCode => Object.hash(InvokeHostAction, actionId);

  @override
  String toString() => 'InvokeHostAction($actionId)';
}

/// Release the session (same as `VideoKitSession.release`).
final class Release extends VideoKitCommand {
  /// Creates the command.
  const Release();

  @override
  String get kind => 'release';

  @override
  bool operator ==(Object other) => other is Release;

  @override
  int get hashCode => (Release).hashCode;

  @override
  String toString() => 'Release()';
}
