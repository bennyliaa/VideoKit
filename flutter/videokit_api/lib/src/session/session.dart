import 'package:flutter/foundation.dart';

import '../host/host_action.dart';
import '../host/navigation.dart';
import '../media/media_source.dart';
import '../media/video_size.dart';
import '../resource/resource_budget.dart';
import '../util/undefined.dart';
import 'command.dart';
import 'command_result.dart';
import 'event.dart';
import 'playback_state.dart';
import 'session_state.dart';

/// Session creation options (04 §2 `VideoKitSessionConfig`).
@immutable
final class VideoKitSessionConfig {
  /// Creates a config.
  const VideoKitSessionConfig({
    this.debugLabel,
    this.priority = ResourcePriority.visible,
    this.initialVisibility = SessionVisibility.visible,
  });

  /// Label for diagnostics (never logged in release).
  final String? debugLabel;

  /// Initial resource priority.
  final ResourcePriority priority;

  /// Initial visibility.
  final SessionVisibility initialVisibility;

  /// Returns a copy with the given fields replaced.
  VideoKitSessionConfig copyWith({
    Object? debugLabel = undefined,
    ResourcePriority? priority,
    SessionVisibility? initialVisibility,
  }) => VideoKitSessionConfig(
    debugLabel: pick<String?>(debugLabel, this.debugLabel),
    priority: priority ?? this.priority,
    initialVisibility: initialVisibility ?? this.initialVisibility,
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitSessionConfig &&
      other.debugLabel == debugLabel &&
      other.priority == priority &&
      other.initialVisibility == initialVisibility;

  @override
  int get hashCode => Object.hash(debugLabel, priority, initialVisibility);

  @override
  String toString() =>
      'VideoKitSessionConfig($debugLabel, ${priority.name}, '
      '${initialVisibility.name})';
}

/// Texture lease (04A S7): keeps the session texture alive while a view
/// shows it. Adapters reference-count leases and dispose the texture 2 s
/// after the last release (14 §8.5). Fakes report a null [textureId].
abstract interface class VideoKitTextureLease {
  /// Texture ID (null while unavailable or for Fakes).
  ValueListenable<int?> get textureId;

  /// Releases the lease. Idempotent.
  void release();
}

/// A playback/image session (04 §3, §12.2, 14 §3.2).
///
/// One session binds at most one media at a time; re-binding releases the
/// previous source first and emits [SourceReleased].
abstract interface class VideoKitSession {
  /// Opaque session ID.
  String get sessionId;

  /// Current state; the single source of truth for the UI.
  /// Use `asStream()` for a [Stream] view.
  ValueListenable<VideoKitSessionState> get state;

  /// One-shot events (bounded, sampled).
  Stream<VideoKitEvent> get events;

  /// Texture ID for `Texture(textureId)`; null for the Dart Fake (UI shows
  /// the demo picture). May change when the surface is recreated.
  ValueListenable<int?> get textureId;

  /// Acquires a texture lease for displaying the session (04A S7).
  VideoKitTextureLease acquireTexture();

  /// Orientation-corrected picture size, null when unknown.
  ValueListenable<VideoSize?> get videoSize;

  /// Whether this session is driven by demo/fake data (UI shows the demo
  /// badge permanently).
  bool get isDemo;

  /// Binds [source]. Optionally applies [initialState] and sets
  /// [hostActions].
  Future<VideoKitCommandResult> bind(
    VideoKitMediaSource source, {
    VideoKitPlaybackState? initialState,
    List<VideoKitHostAction> hostActions = const [],
  });

  /// Executes [command].
  Future<VideoKitCommandResult> execute(VideoKitCommand command);

  /// Replaces the host actions.
  Future<void> updateHostActions(List<VideoKitHostAction> actions);

  /// Asks the host to perform host action [actionId] (04A I1). Returns
  /// `Executed` once the request is sent; a repeat while the same action is
  /// pending returns `Superseded` and does not call the host again; an
  /// unknown or disabled action returns `Unsupported(HOST_DISABLED)`. The
  /// host result is reflected in [VideoKitSessionState.hostActions] and
  /// failures in a `HostActionFailed` event.
  Future<VideoKitCommandResult> requestHostAction(String actionId);

  /// Asks the host to move to the previous/next media (04A I2). Host
  /// failures and timeouts yield [NavigationResult.failed].
  Future<NavigationResult> requestNavigation(NavigationDirection direction);

  /// Writes UI controls visibility into
  /// [VideoKitSessionState.controlsVisible] and forwards it to the host
  /// (04A I3).
  void setControlsVisible(bool visible);

  /// Captures the current persistable snapshot.
  Future<VideoKitPlaybackState> captureState();

  /// Releases the session. Idempotent; returns the last snapshot.
  Future<VideoKitPlaybackState> release();

  /// Same as [release] without awaiting the snapshot. Idempotent.
  Future<void> close();
}
