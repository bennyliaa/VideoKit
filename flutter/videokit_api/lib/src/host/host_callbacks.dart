import 'package:flutter/foundation.dart';

import '../error/stable_error.dart';
import '../feature/feature.dart';
import '../media/media_source.dart' show VideoKitSourceFactory;
import '../session/event.dart';
import '../session/playback_state.dart';
import '../util/enum_codec.dart';
import 'host_action.dart';
import 'navigation.dart';

/// Host decision for a recoverable error (04 §8).
enum RecoveryDecision {
  /// VideoKit retries (re-binds) automatically.
  retry,

  /// Stay in the error state; the UI offers retry.
  keepError,

  /// Release the session; the host may fall back to another player.
  release;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [keepError].
  static RecoveryDecision fromName(String? name) =>
      enumFromName(values, name, keepError);
}

/// Host callbacks (04 §8). Every call has a timeout; timeouts or exceptions
/// are recorded as `HOST_CALLBACK_FAILED` and never block the session.
abstract interface class VideoKitHostCallbacks {
  /// A host action was clicked.
  Future<HostActionResult> onHostActionRequested(HostActionRequest request);

  /// Previous/next requested.
  Future<NavigationResult> onNavigationRequested(NavigationRequest request);

  /// Stable playback snapshot (after changes settle and on release); the
  /// snapshot carries `sessionId` and `mediaToken` (04A I7).
  Future<void> onPlaybackSnapshot(VideoKitPlaybackState snapshot);

  /// Playback statistics event.
  Future<void> onPlaybackEvent(VideoKitPlaybackEvent event);

  /// Controls shown/hidden.
  Future<void> onControlsVisibilityChanged(String sessionId, bool visible);

  /// All handles for [mediaToken] closed.
  Future<void> onSourceReleased(String sessionId, String mediaToken);

  /// A recoverable error occurred.
  Future<RecoveryDecision> onRecoverableError(
    String sessionId,
    VideoKitStableError error,
  );

  /// A fatal session error occurred.
  Future<void> onFatalSessionError(String sessionId, VideoKitStableError error);

  /// The Kit needs the transparent PNG stored under [avatarToken] for
  /// preview or export (REQ-ED-07, 04A E5 1 / E6 2): return a readable
  /// source, or null when it is gone (that range then falls back to mosaic
  /// with a warning). `builtin:N` tokens never reach the host.
  Future<VideoKitSourceFactory?> openAvatar(String avatarToken);

  /// Dynamic feature gate (REQ-API-10 ②): asked before an entry of
  /// [feature] opens (UI) and by the feature's API entry points; [sessionId]
  /// names the session or project when there is one. A host may show its
  /// own page (e.g. a paywall) before answering. A throw or a timeout
  /// ([HostCallbackTimeouts.featureGate]) counts as denied without a
  /// marker. [NoopHostCallbacks] allows everything.
  Future<FeatureAccess> checkFeature(VideoKitFeature feature, String? sessionId);
}

/// Callbacks that do nothing; extend and override what you need.
class NoopHostCallbacks implements VideoKitHostCallbacks {
  /// Creates no-op callbacks.
  const NoopHostCallbacks();

  @override
  Future<HostActionResult> onHostActionRequested(
    HostActionRequest request,
  ) async => const HostActionResult.completed();

  @override
  Future<NavigationResult> onNavigationRequested(
    NavigationRequest request,
  ) async => NavigationResult.unavailable;

  @override
  Future<void> onPlaybackSnapshot(VideoKitPlaybackState snapshot) async {}

  @override
  Future<void> onPlaybackEvent(VideoKitPlaybackEvent event) async {}

  @override
  Future<void> onControlsVisibilityChanged(
    String sessionId,
    bool visible,
  ) async {}

  @override
  Future<void> onSourceReleased(String sessionId, String mediaToken) async {}

  @override
  Future<RecoveryDecision> onRecoverableError(
    String sessionId,
    VideoKitStableError error,
  ) async => RecoveryDecision.keepError;

  @override
  Future<void> onFatalSessionError(
    String sessionId,
    VideoKitStableError error,
  ) async {}

  @override
  Future<VideoKitSourceFactory?> openAvatar(String avatarToken) async => null;

  /// Allows everything: a host without a gate behaves as before (FT01B-03).
  @override
  Future<FeatureAccess> checkFeature(
    VideoKitFeature feature,
    String? sessionId,
  ) async => FeatureAccess.allowed;
}

/// Callback timeouts (04A I8, 14 §12; host-configurable).
@immutable
final class HostCallbackTimeouts {
  /// Creates timeouts.
  const HostCallbackTimeouts({
    this.hostAction = const Duration(seconds: 10),
    this.navigation = const Duration(seconds: 3),
    this.recoveryDecision = const Duration(seconds: 3),
    this.notification = const Duration(seconds: 2),
    this.featureGate = const Duration(seconds: 30),
  });

  /// `checkFeature` (REQ-API-10): long enough for a host paywall shown
  /// before it answers; a timeout counts as denied.
  final Duration featureGate;

  /// Host action (pending meanwhile).
  final Duration hostAction;

  /// Navigation request.
  final Duration navigation;

  /// `onRecoverableError` decision.
  final Duration recoveryDecision;

  /// Other notification-style callbacks.
  final Duration notification;

  /// Returns a copy with the given fields replaced.
  HostCallbackTimeouts copyWith({
    Duration? hostAction,
    Duration? navigation,
    Duration? recoveryDecision,
    Duration? notification,
    Duration? featureGate,
  }) => HostCallbackTimeouts(
    hostAction: hostAction ?? this.hostAction,
    navigation: navigation ?? this.navigation,
    recoveryDecision: recoveryDecision ?? this.recoveryDecision,
    notification: notification ?? this.notification,
    featureGate: featureGate ?? this.featureGate,
  );

  @override
  bool operator ==(Object other) =>
      other is HostCallbackTimeouts &&
      other.hostAction == hostAction &&
      other.navigation == navigation &&
      other.recoveryDecision == recoveryDecision &&
      other.notification == notification &&
      other.featureGate == featureGate;

  @override
  int get hashCode => Object.hash(
    hostAction,
    navigation,
    recoveryDecision,
    notification,
    featureGate,
  );

  @override
  String toString() =>
      'HostCallbackTimeouts(action: $hostAction, nav: $navigation, '
      'recovery: $recoveryDecision, notify: $notification)';
}
