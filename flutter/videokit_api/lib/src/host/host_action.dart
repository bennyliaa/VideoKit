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

/// Icon of a host action (04 §7, 04A N9): a built-in VideoKit icon key or a
/// host resource reference.
@immutable
sealed class HostIcon {
  const HostIcon();

  /// A built-in icon resolved by `VkIcons` (e.g. `favorite`, `tag`).
  const factory HostIcon.builtIn(String iconKey) = HostIconBuiltIn;

  /// A host resource (Kotlin `HostIcon.Resource`; native hosts).
  const factory HostIcon.resource(String resourceRef) = HostIconResource;
}

/// Built-in icon key (Kotlin `HostIcon.BuiltIn`).
final class HostIconBuiltIn extends HostIcon {
  /// Creates a built-in icon reference.
  const HostIconBuiltIn(this.iconKey);

  /// Icon key.
  final String iconKey;

  @override
  bool operator ==(Object other) =>
      other is HostIconBuiltIn && other.iconKey == iconKey;

  @override
  int get hashCode => Object.hash(HostIconBuiltIn, iconKey);

  @override
  String toString() => 'HostIcon.builtIn($iconKey)';
}

/// Opaque host resource reference (Kotlin `HostIcon.Resource`).
final class HostIconResource extends HostIcon {
  /// Creates a resource icon reference.
  const HostIconResource(this.resourceRef);

  /// Resource reference.
  final String resourceRef;

  @override
  bool operator ==(Object other) =>
      other is HostIconResource && other.resourceRef == resourceRef;

  @override
  int get hashCode => Object.hash(HostIconResource, resourceRef);

  @override
  String toString() => 'HostIcon.resource($resourceRef)';
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
/// reported by the host plus VideoKit's pending/last-result tracking
/// (04A S1).
@immutable
final class HostActionState {
  /// Creates a host action state; [pending] defaults to the host's flag.
  HostActionState({
    required this.action,
    bool? pending,
    this.lastStatus,
    this.lastError,
  }) : pending = pending ?? action.pending;

  /// The action.
  final VideoKitHostAction action;

  /// A request is in flight or the host reported PENDING; repeats return
  /// `Superseded` and the UI shows a pending ring.
  final bool pending;

  /// Status of the last host answer, if any.
  final HostActionStatus? lastStatus;

  /// Error of the last failed/timed-out request, cleared on next success.
  final VideoKitStableError? lastError;

  /// Same as [pending] (kept for readability in UI code).
  bool get isPending => pending;

  /// Returns a copy with the given fields replaced.
  HostActionState copyWith({
    VideoKitHostAction? action,
    bool? pending,
    Object? lastStatus = undefined,
    Object? lastError = undefined,
  }) => HostActionState(
    action: action ?? this.action,
    pending: pending ?? this.pending,
    lastStatus: pick<HostActionStatus?>(lastStatus, this.lastStatus),
    lastError: pick<VideoKitStableError?>(lastError, this.lastError),
  );

  @override
  bool operator ==(Object other) =>
      other is HostActionState &&
      other.action == action &&
      other.pending == pending &&
      other.lastStatus == lastStatus &&
      other.lastError == lastError;

  @override
  int get hashCode => Object.hash(action, pending, lastStatus, lastError);

  @override
  String toString() =>
      'HostActionState(${action.actionId}, pending: $pending, '
      'last: ${lastStatus?.name}, error: ${lastError?.code.name})';
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
  failed,

  /// Host or user cancelled the action (no error shown).
  cancelled;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [failed].
  static HostActionStatus fromName(String? name) =>
      enumFromName(values, name, failed);
}

/// Host answer to [HostActionRequest] (04 §8, 04A V3).
@immutable
final class HostActionResult {
  /// Creates a result.
  const HostActionResult({
    required this.status,
    this.updatedAction,
    this.messageKey,
  });

  /// Completed, optionally with the action's new state.
  const HostActionResult.completed([this.updatedAction, this.messageKey])
    : status = HostActionStatus.completed;

  /// Pending, optionally with the action's new state.
  const HostActionResult.pending([this.updatedAction, this.messageKey])
    : status = HostActionStatus.pending;

  /// Failed; [messageKey] is an optional host string key for the notice.
  const HostActionResult.failed([this.messageKey])
    : status = HostActionStatus.failed,
      updatedAction = null;

  /// Cancelled.
  const HostActionResult.cancelled()
    : status = HostActionStatus.cancelled,
      updatedAction = null,
      messageKey = null;

  /// Status.
  final HostActionStatus status;

  /// New state of the action (selected/pending/badge), if changed.
  final VideoKitHostAction? updatedAction;

  /// Optional host string key for a transient notice.
  final String? messageKey;

  /// Returns a copy with the given fields replaced.
  HostActionResult copyWith({
    HostActionStatus? status,
    Object? updatedAction = undefined,
    Object? messageKey = undefined,
  }) => HostActionResult(
    status: status ?? this.status,
    updatedAction: pick<VideoKitHostAction?>(updatedAction, this.updatedAction),
    messageKey: pick<String?>(messageKey, this.messageKey),
  );

  @override
  bool operator ==(Object other) =>
      other is HostActionResult &&
      other.status == status &&
      other.updatedAction == updatedAction &&
      other.messageKey == messageKey;

  @override
  int get hashCode => Object.hash(status, updatedAction, messageKey);

  @override
  String toString() =>
      'HostActionResult(${status.name}, updated: $updatedAction, '
      'message: $messageKey)';
}
