import 'package:flutter/foundation.dart';

import '../error/stable_error.dart';
import '../util/enum_codec.dart';
import '../util/undefined.dart';

/// Where a host action is laid out (04 §7).
enum ActionPlacement {
  primaryBar,
  secondaryBar,
  overflow;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [overflow].
  static ActionPlacement fromName(String? name) =>
      enumFromName(values, name, overflow);
}

/// Icon of a host action: a built-in VideoKit icon key or a host resource
/// (04 §7).
@immutable
sealed class HostIcon {
  const HostIcon();

  /// A built-in icon resolved by `VideoKitIcons` (e.g. `favorite`, `tag`).
  const factory HostIcon.builtin(String iconKey) = BuiltinHostIcon;

  /// A host drawable resource ID (native hosts).
  const factory HostIcon.hostResource(int resourceId) = HostResourceIcon;
}

/// Built-in icon key.
final class BuiltinHostIcon extends HostIcon {
  /// Creates a built-in icon reference.
  const BuiltinHostIcon(this.iconKey);

  /// Icon key.
  final String iconKey;

  @override
  bool operator ==(Object other) =>
      other is BuiltinHostIcon && other.iconKey == iconKey;

  @override
  int get hashCode => Object.hash(BuiltinHostIcon, iconKey);

  @override
  String toString() => 'HostIcon.builtin($iconKey)';
}

/// Host drawable resource ID.
final class HostResourceIcon extends HostIcon {
  /// Creates a resource icon reference.
  const HostResourceIcon(this.resourceId);

  /// Resource ID.
  final int resourceId;

  @override
  bool operator ==(Object other) =>
      other is HostResourceIcon && other.resourceId == resourceId;

  @override
  int get hashCode => Object.hash(HostResourceIcon, resourceId);

  @override
  String toString() => 'HostIcon.hostResource($resourceId)';
}

/// A host-defined action shown by VideoKit (04 §7, original §9).
@immutable
final class VideoKitHostAction {
  /// Creates a host action.
  const VideoKitHostAction({
    required this.actionId,
    required this.labelKey,
    required this.contentDescriptionKey,
    required this.icon,
    required this.placement,
    this.enabled = true,
    this.selected = false,
    this.pending = false,
    this.badgeText,
    this.displayPriority = 0,
  });

  /// Opaque action ID.
  final String actionId;

  /// Host string key or literal text (resolved by the host resolver).
  final String labelKey;

  /// Host string key or literal text for screen readers.
  final String contentDescriptionKey;

  /// Icon.
  final HostIcon icon;

  /// Whether the action can be triggered.
  final bool enabled;

  /// Toggle state (e.g. favourite).
  final bool selected;

  /// Host-reported pending state.
  final bool pending;

  /// Badge (≤ 3 chars displayed).
  final String? badgeText;

  /// Higher first.
  final int displayPriority;

  /// Placement.
  final ActionPlacement placement;

  /// Returns a copy with the given fields replaced.
  VideoKitHostAction copyWith({
    String? actionId,
    String? labelKey,
    String? contentDescriptionKey,
    HostIcon? icon,
    bool? enabled,
    bool? selected,
    bool? pending,
    Object? badgeText = undefined,
    int? displayPriority,
    ActionPlacement? placement,
  }) => VideoKitHostAction(
    actionId: actionId ?? this.actionId,
    labelKey: labelKey ?? this.labelKey,
    contentDescriptionKey: contentDescriptionKey ?? this.contentDescriptionKey,
    icon: icon ?? this.icon,
    enabled: enabled ?? this.enabled,
    selected: selected ?? this.selected,
    pending: pending ?? this.pending,
    badgeText: pick<String?>(badgeText, this.badgeText),
    displayPriority: displayPriority ?? this.displayPriority,
    placement: placement ?? this.placement,
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitHostAction &&
      other.actionId == actionId &&
      other.labelKey == labelKey &&
      other.contentDescriptionKey == contentDescriptionKey &&
      other.icon == icon &&
      other.enabled == enabled &&
      other.selected == selected &&
      other.pending == pending &&
      other.badgeText == badgeText &&
      other.displayPriority == displayPriority &&
      other.placement == placement;

  @override
  int get hashCode => Object.hash(
    actionId,
    labelKey,
    contentDescriptionKey,
    icon,
    enabled,
    selected,
    pending,
    badgeText,
    displayPriority,
    placement,
  );

  @override
  String toString() =>
      'VideoKitHostAction($actionId, ${placement.name}, enabled: $enabled, '
      'selected: $selected, pending: $pending, badge: $badgeText, '
      'priority: $displayPriority)';
}

/// Session-maintained state of one host action (14 §3.2): the action as last
/// reported by the host plus VideoKit's own in-flight/failure tracking.
@immutable
final class HostActionState {
  /// Creates a host action state.
  const HostActionState({
    required this.action,
    this.inFlight = false,
    this.lastError,
  });

  /// The action.
  final VideoKitHostAction action;

  /// A request is in flight (duplicate clicks are merged meanwhile).
  final bool inFlight;

  /// Error of the last failed/timed-out request, cleared on next success.
  final VideoKitStableError? lastError;

  /// Whether the UI should show a pending indicator.
  bool get isPending => inFlight || action.pending;

  /// Returns a copy with the given fields replaced.
  HostActionState copyWith({
    VideoKitHostAction? action,
    bool? inFlight,
    Object? lastError = undefined,
  }) => HostActionState(
    action: action ?? this.action,
    inFlight: inFlight ?? this.inFlight,
    lastError: pick<VideoKitStableError?>(lastError, this.lastError),
  );

  @override
  bool operator ==(Object other) =>
      other is HostActionState &&
      other.action == action &&
      other.inFlight == inFlight &&
      other.lastError == lastError;

  @override
  int get hashCode => Object.hash(action, inFlight, lastError);

  @override
  String toString() =>
      'HostActionState(${action.actionId}, inFlight: $inFlight, '
      'lastError: ${lastError?.code.name})';
}

/// Request sent to the host when a host action is clicked (04 §7).
@immutable
final class HostActionRequest {
  /// Creates a request.
  const HostActionRequest({
    required this.actionId,
    required this.sessionId,
    required this.mediaToken,
  });

  /// Action ID.
  final String actionId;

  /// Session ID.
  final String sessionId;

  /// Media token bound to the session.
  final String mediaToken;

  /// Returns a copy with the given fields replaced.
  HostActionRequest copyWith({
    String? actionId,
    String? sessionId,
    String? mediaToken,
  }) => HostActionRequest(
    actionId: actionId ?? this.actionId,
    sessionId: sessionId ?? this.sessionId,
    mediaToken: mediaToken ?? this.mediaToken,
  );

  @override
  bool operator ==(Object other) =>
      other is HostActionRequest &&
      other.actionId == actionId &&
      other.sessionId == sessionId &&
      other.mediaToken == mediaToken;

  @override
  int get hashCode => Object.hash(actionId, sessionId, mediaToken);

  @override
  String toString() =>
      'HostActionRequest($actionId, session: $sessionId, media: $mediaToken)';
}

/// Outcome status of a host action request.
enum HostActionStatus {
  /// Host completed the action.
  completed,

  /// Host accepted and continues asynchronously (e.g. queued tag change).
  pending,

  /// Host failed the action.
  failed;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [failed].
  static HostActionStatus fromName(String? name) =>
      enumFromName(values, name, failed);
}

/// Host answer to [HostActionRequest] (04 §8, 05 §5).
@immutable
final class HostActionResult {
  /// Creates a result.
  const HostActionResult({
    required this.status,
    this.updatedAction,
    this.error,
  });

  /// Completed, optionally with the action's new state.
  const HostActionResult.completed([this.updatedAction])
    : status = HostActionStatus.completed,
      error = null;

  /// Pending, optionally with the action's new state.
  const HostActionResult.pending([this.updatedAction])
    : status = HostActionStatus.pending,
      error = null;

  /// Failed with [error].
  const HostActionResult.failed(VideoKitStableError this.error)
    : status = HostActionStatus.failed,
      updatedAction = null;

  /// Status.
  final HostActionStatus status;

  /// New state of the action (selected/pending/badge), if changed.
  final VideoKitHostAction? updatedAction;

  /// Error when [status] is failed.
  final VideoKitStableError? error;

  /// Returns a copy with the given fields replaced.
  HostActionResult copyWith({
    HostActionStatus? status,
    Object? updatedAction = undefined,
    Object? error = undefined,
  }) => HostActionResult(
    status: status ?? this.status,
    updatedAction: pick<VideoKitHostAction?>(updatedAction, this.updatedAction),
    error: pick<VideoKitStableError?>(error, this.error),
  );

  @override
  bool operator ==(Object other) =>
      other is HostActionResult &&
      other.status == status &&
      other.updatedAction == updatedAction &&
      other.error == error;

  @override
  int get hashCode => Object.hash(status, updatedAction, error);

  @override
  String toString() =>
      'HostActionResult(${status.name}, updated: $updatedAction, '
      'error: $error)';
}
