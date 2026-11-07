import 'package:flutter/foundation.dart';

import '../error/stable_error.dart';
import 'session_state.dart';

/// One-shot session event for UI hints (14 §3.2). UI never rebuilds state
/// from events.
@immutable
sealed class VideoKitEvent {
  const VideoKitEvent();
}

/// Playback reached the end.
final class PlaybackEnded extends VideoKitEvent {
  /// Creates the event.
  const PlaybackEnded();

  @override
  bool operator ==(Object other) => other is PlaybackEnded;

  @override
  int get hashCode => (PlaybackEnded).hashCode;

  @override
  String toString() => 'PlaybackEnded()';
}

/// All handles for [mediaToken] are closed (05 §4).
final class SourceReleased extends VideoKitEvent {
  /// Creates the event.
  const SourceReleased(this.mediaToken);

  /// Released media token.
  final String mediaToken;

  @override
  bool operator ==(Object other) =>
      other is SourceReleased && other.mediaToken == mediaToken;

  @override
  int get hashCode => Object.hash(SourceReleased, mediaToken);

  @override
  String toString() => 'SourceReleased($mediaToken)';
}

/// A host action request failed or timed out.
final class HostActionFailed extends VideoKitEvent {
  /// Creates the event.
  const HostActionFailed(this.actionId, this.error);

  /// Action ID.
  final String actionId;

  /// Error (`HOST_CALLBACK_FAILED` on timeout/exception).
  final VideoKitStableError error;

  @override
  bool operator ==(Object other) =>
      other is HostActionFailed &&
      other.actionId == actionId &&
      other.error == error;

  @override
  int get hashCode => Object.hash(HostActionFailed, actionId, error);

  @override
  String toString() => 'HostActionFailed($actionId, $error)';
}

/// Short-lived notice identified by a stable [code] (UI resolves text).
final class TransientNotice extends VideoKitEvent {
  /// Creates the event.
  const TransientNotice(this.code);

  /// Notice code, see [NoticeCodes].
  final String code;

  @override
  bool operator ==(Object other) =>
      other is TransientNotice && other.code == code;

  @override
  int get hashCode => Object.hash(TransientNotice, code);

  @override
  String toString() => 'TransientNotice($code)';
}

/// An error was raised (also reflected in state).
final class ErrorRaised extends VideoKitEvent {
  /// Creates the event.
  const ErrorRaised(this.error);

  /// Error.
  final VideoKitStableError error;

  @override
  bool operator ==(Object other) =>
      other is ErrorRaised && other.error == error;

  @override
  int get hashCode => Object.hash(ErrorRaised, error);

  @override
  String toString() => 'ErrorRaised($error)';
}

/// Known [TransientNotice] codes.
abstract final class NoticeCodes {
  /// Seek target was clamped to the media bounds.
  static const String seekClamped = 'seek_clamped';

  /// Session was degraded to free resources.
  static const String resourceDegraded = 'resource_degraded';

  /// Navigation target unavailable.
  static const String navigationUnavailable = 'navigation_unavailable';
}

/// Playback event delivered to the host callback `onPlaybackEvent`
/// (06 §4.1). Carries only opaque IDs.
@immutable
sealed class VideoKitPlaybackEvent {
  const VideoKitPlaybackEvent(this.sessionId);

  /// Session ID.
  final String sessionId;
}

/// Sampled position.
final class PositionTick extends VideoKitPlaybackEvent {
  /// Creates the event.
  const PositionTick(super.sessionId, this.positionUs);

  /// Position (µs).
  final int positionUs;

  @override
  bool operator ==(Object other) =>
      other is PositionTick &&
      other.sessionId == sessionId &&
      other.positionUs == positionUs;

  @override
  int get hashCode => Object.hash(PositionTick, sessionId, positionUs);

  @override
  String toString() => 'PositionTick($sessionId, $positionUs)';
}

/// Phase changed.
final class PlayStateChanged extends VideoKitPlaybackEvent {
  /// Creates the event.
  const PlayStateChanged(super.sessionId, this.phase);

  /// New phase.
  final SessionPhase phase;

  @override
  bool operator ==(Object other) =>
      other is PlayStateChanged &&
      other.sessionId == sessionId &&
      other.phase == phase;

  @override
  int get hashCode => Object.hash(PlayStateChanged, sessionId, phase);

  @override
  String toString() => 'PlayStateChanged($sessionId, ${phase.name})';
}

/// Buffering started.
final class BufferingStarted extends VideoKitPlaybackEvent {
  /// Creates the event.
  const BufferingStarted(super.sessionId);

  @override
  bool operator ==(Object other) =>
      other is BufferingStarted && other.sessionId == sessionId;

  @override
  int get hashCode => Object.hash(BufferingStarted, sessionId);

  @override
  String toString() => 'BufferingStarted($sessionId)';
}

/// Buffering ended.
final class BufferingEnded extends VideoKitPlaybackEvent {
  /// Creates the event.
  const BufferingEnded(super.sessionId);

  @override
  bool operator ==(Object other) =>
      other is BufferingEnded && other.sessionId == sessionId;

  @override
  int get hashCode => Object.hash(BufferingEnded, sessionId);

  @override
  String toString() => 'BufferingEnded($sessionId)';
}

/// User-initiated seek (not counted as watch time).
final class UserSeek extends VideoKitPlaybackEvent {
  /// Creates the event.
  const UserSeek(super.sessionId, this.fromUs, this.toUs);

  /// From (µs).
  final int fromUs;

  /// To (µs).
  final int toUs;

  @override
  bool operator ==(Object other) =>
      other is UserSeek &&
      other.sessionId == sessionId &&
      other.fromUs == fromUs &&
      other.toUs == toUs;

  @override
  int get hashCode => Object.hash(UserSeek, sessionId, fromUs, toUs);

  @override
  String toString() => 'UserSeek($sessionId, $fromUs → $toUs)';
}

/// Visibility changed.
final class VisibilityChanged extends VideoKitPlaybackEvent {
  /// Creates the event.
  const VisibilityChanged(super.sessionId, this.visibility);

  /// New visibility.
  final SessionVisibility visibility;

  @override
  bool operator ==(Object other) =>
      other is VisibilityChanged &&
      other.sessionId == sessionId &&
      other.visibility == visibility;

  @override
  int get hashCode => Object.hash(VisibilityChanged, sessionId, visibility);

  @override
  String toString() => 'VisibilityChanged($sessionId, ${visibility.name})';
}

/// App foreground state changed.
final class ForegroundChanged extends VideoKitPlaybackEvent {
  /// Creates the event.
  const ForegroundChanged(super.sessionId, this.foreground);

  /// In foreground.
  final bool foreground;

  @override
  bool operator ==(Object other) =>
      other is ForegroundChanged &&
      other.sessionId == sessionId &&
      other.foreground == foreground;

  @override
  int get hashCode => Object.hash(ForegroundChanged, sessionId, foreground);

  @override
  String toString() => 'ForegroundChanged($sessionId, $foreground)';
}

/// Natural watch time accumulated while playing, visible and not buffering.
final class WatchTimeAccumulated extends VideoKitPlaybackEvent {
  /// Creates the event.
  const WatchTimeAccumulated(super.sessionId, this.deltaUs);

  /// Delta (µs).
  final int deltaUs;

  @override
  bool operator ==(Object other) =>
      other is WatchTimeAccumulated &&
      other.sessionId == sessionId &&
      other.deltaUs == deltaUs;

  @override
  int get hashCode => Object.hash(WatchTimeAccumulated, sessionId, deltaUs);

  @override
  String toString() => 'WatchTimeAccumulated($sessionId, $deltaUs)';
}

/// Session ended (released).
final class SessionEnded extends VideoKitPlaybackEvent {
  /// Creates the event.
  const SessionEnded(super.sessionId);

  @override
  bool operator ==(Object other) =>
      other is SessionEnded && other.sessionId == sessionId;

  @override
  int get hashCode => Object.hash(SessionEnded, sessionId);

  @override
  String toString() => 'SessionEnded($sessionId)';
}
