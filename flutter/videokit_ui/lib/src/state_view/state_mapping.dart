import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

/// What the state view shows (UI-09).
enum StateViewKind { loading, buffering, ended, error, released, locked }

/// Action offered by the state view; handled by the owning component via
/// `onStateAction` (14 §5.9).
enum StateAction {
  retry,
  replay,
  chooseOtherTrack,
  reduceQuality,
  freeSpace,
  checkPermission,
  reconnectSource,
  closeOtherSessions,
  correctTracking,
  chooseOtherSource,

  /// J4: opens the read-only capability page (UI only; the host routes it).
  showCapabilities;

  /// The API suggested action this corresponds to, if any.
  SuggestedAction? get suggested => switch (this) {
    retry => SuggestedAction.retry,
    replay => null,
    chooseOtherTrack => SuggestedAction.chooseOtherTrack,
    reduceQuality => SuggestedAction.reduceQuality,
    freeSpace => SuggestedAction.freeSpace,
    checkPermission => SuggestedAction.checkPermission,
    reconnectSource => SuggestedAction.reconnectSource,
    closeOtherSessions => SuggestedAction.closeOtherSessions,
    correctTracking => SuggestedAction.correctTracking,
    chooseOtherSource => SuggestedAction.chooseOtherSource,
    showCapabilities => null,
  };

  /// Action for a suggested action (none → null).
  static StateAction? fromSuggested(SuggestedAction a) => switch (a) {
    SuggestedAction.none => null,
    SuggestedAction.retry => retry,
    SuggestedAction.chooseOtherTrack => chooseOtherTrack,
    SuggestedAction.reduceQuality => reduceQuality,
    SuggestedAction.freeSpace => freeSpace,
    SuggestedAction.checkPermission => checkPermission,
    SuggestedAction.reconnectSource => reconnectSource,
    SuggestedAction.closeOtherSessions => closeOtherSessions,
    SuggestedAction.correctTracking => correctTracking,
    SuggestedAction.chooseOtherSource => chooseOtherSource,
  };
}

/// Detail text category (ARB `stateDetail*`).
enum StateDetail {
  loading,
  connection,
  permission,
  unsupported,
  corrupt,
  resources,
  trackingLost,
  space,
  generic,
}

/// Pure view model of a state (14 §5.9), testable and overridable.
@immutable
final class StateViewModel {
  /// Creates a model.
  StateViewModel({
    required this.kind,
    required this.iconName,
    this.error,
    this.detail,
    List<StateAction> actions = const [],
    this.titleText,
    this.detailText,
  }) : actions = List.unmodifiable(actions);

  /// Kind.
  final StateViewKind kind;

  /// Icon name (`VkIcons`), e.g. `warning`.
  final String iconName;

  /// Error whose code gives the title (error kind only).
  final VideoKitStableError? error;

  /// Detail text category.
  final StateDetail? detail;

  /// Actions; empty = explanation only, never dead buttons.
  final List<StateAction> actions;

  /// Host-provided, already localized title (e.g. the App's startup
  /// error page); overrides the kind/error title.
  final String? titleText;

  /// Host-provided, already localized detail; overrides [detail].
  final String? detailText;

  /// Whether the picture stays visible underneath (buffering).
  bool get keepsPicture => kind == StateViewKind.buffering;

  @override
  bool operator ==(Object other) =>
      other is StateViewModel &&
      other.kind == kind &&
      other.iconName == iconName &&
      other.error == error &&
      other.detail == detail &&
      other.titleText == titleText &&
      other.detailText == detailText &&
      listEquals(other.actions, actions);

  @override
  int get hashCode => Object.hash(
    kind,
    iconName,
    error,
    detail,
    titleText,
    detailText,
    Object.hashAll(actions),
  );

  @override
  String toString() =>
      'StateViewModel(${kind.name}, ${error?.code.name}, ${detail?.name}, '
      '$actions)';
}

/// Maps session state to a [StateViewModel] (14 §5.9 table); null when no
/// state view is needed (ready/playing/paused).
StateViewModel? mapSessionState({
  required SessionPhase phase,
  VideoKitStableError? error,
  MediaKind? mediaKind,
  bool hiddenForLock = false,
  bool capabilityHelp = false,
}) {
  if (phase == SessionPhase.releasing || phase == SessionPhase.released) {
    return StateViewModel(kind: StateViewKind.released, iconName: 'close');
  }
  if (hiddenForLock) {
    return StateViewModel(kind: StateViewKind.locked, iconName: 'lock');
  }
  switch (phase) {
    case SessionPhase.created || SessionPhase.binding:
      return StateViewModel(
        kind: StateViewKind.loading,
        iconName: 'retry',
        detail: StateDetail.loading,
      );
    case SessionPhase.buffering:
      return StateViewModel(kind: StateViewKind.buffering, iconName: 'retry');
    case SessionPhase.ended:
      return StateViewModel(
        kind: StateViewKind.ended,
        iconName: 'retry',
        actions: const [StateAction.replay],
      );
    case SessionPhase.errorRecoverable || SessionPhase.errorFatal:
      return mapError(
        error ??
            VideoKitStableError.internal(
              stage: ErrorStage.playback,
              diagnostic: 'missing_error_${phase.wireName}',
            ),
        fatal: phase == SessionPhase.errorFatal,
        capabilityHelp: capabilityHelp,
      );
    case SessionPhase.ready || SessionPhase.playing || SessionPhase.paused:
      return null;
    case SessionPhase.releasing || SessionPhase.released:
      return null; // handled above
  }
}

/// Error part of the mapping: title from the code, detail by category,
/// actions from the suggested action plus retry when retryable (and not
/// fatal).
StateViewModel mapError(
  VideoKitStableError error, {
  bool fatal = false,
  bool capabilityHelp = false,
}) {
  final (StateDetail detail, String icon) = switch (error.code) {
    ErrorCode.sourceDisconnected ||
    ErrorCode.sourceTimeout => (StateDetail.connection, 'warning'),
    ErrorCode.sourcePermissionDenied ||
    ErrorCode.outputPermissionDenied => (StateDetail.permission, 'lock'),
    ErrorCode.unsupportedContainer ||
    ErrorCode.unsupportedVideoCodec ||
    ErrorCode.unsupportedAudioCodec ||
    ErrorCode.decoderUnavailable ||
    ErrorCode.encoderUnavailable ||
    ErrorCode.seekUnsupported ||
    ErrorCode.outputCapabilityUnsupported => (StateDetail.unsupported, 'error'),
    ErrorCode.corruptMedia => (StateDetail.corrupt, 'error'),
    ErrorCode.decoderResourceExhausted => (StateDetail.resources, 'info'),
    ErrorCode.trackingLost ||
    ErrorCode.trackingModelUnavailable => (StateDetail.trackingLost, 'warning'),
    ErrorCode.outputSpaceInsufficient => (StateDetail.space, 'warning'),
    _ => (StateDetail.generic, 'warning'),
  };
  final actions = <StateAction>[];
  final suggested = StateAction.fromSuggested(error.suggestedAction);
  if (suggested != null && !(fatal && suggested == StateAction.retry)) {
    actions.add(suggested);
  }
  if (error.retryable && !fatal && !actions.contains(StateAction.retry)) {
    actions.add(StateAction.retry);
  }
  if (error.code == ErrorCode.outputSpaceInsufficient &&
      !actions.contains(StateAction.reduceQuality)) {
    actions.add(StateAction.reduceQuality);
  }
  // J4 (design page 12): unsupported media points to the capability page
  // when the host can show it.
  if (capabilityHelp && isUnsupportedMedia(error.code)) {
    actions.add(StateAction.showCapabilities);
  }
  return StateViewModel(
    kind: StateViewKind.error,
    iconName: icon,
    error: error,
    detail: detail,
    actions: actions,
  );
}

/// Whether [code] means the device cannot play this media's format
/// (short title "格式不支持", J4).
bool isUnsupportedMedia(ErrorCode code) =>
    code == ErrorCode.unsupportedContainer ||
    code == ErrorCode.unsupportedVideoCodec ||
    code == ErrorCode.unsupportedAudioCodec;
