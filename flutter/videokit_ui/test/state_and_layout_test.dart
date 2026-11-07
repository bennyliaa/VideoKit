import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/src/foundation/auto_hide.dart';
import 'package:videokit_ui/videokit_ui.dart';

VideoKitHostAction _action(
  String id, {
  ActionPlacement placement = ActionPlacement.primaryBar,
  int priority = 0,
}) => VideoKitHostAction(
  actionId: id,
  labelKey: id,
  contentDescriptionKey: id,
  icon: HostIcon.builtIn(id),
  placement: placement,
  displayPriority: priority,
);

void main() {
  group('state mapping (14 §5.9)', () {
    test('phases', () {
      expect(mapSessionState(phase: SessionPhase.ready), isNull);
      expect(mapSessionState(phase: SessionPhase.playing), isNull);
      expect(
        mapSessionState(phase: SessionPhase.binding)!.kind,
        StateViewKind.loading,
      );
      expect(
        mapSessionState(phase: SessionPhase.created)!.detail,
        StateDetail.loading,
      );
      final b = mapSessionState(phase: SessionPhase.buffering)!;
      expect(b.kind, StateViewKind.buffering);
      expect(b.keepsPicture, isTrue);
      expect(mapSessionState(phase: SessionPhase.ended)!.actions, [
        StateAction.replay,
      ]);
      expect(
        mapSessionState(phase: SessionPhase.released)!.kind,
        StateViewKind.released,
      );
      expect(
        mapSessionState(phase: SessionPhase.playing, hiddenForLock: true)!.kind,
        StateViewKind.locked,
      );
    });

    test('every error code maps to a model with a title and detail', () {
      for (final code in ErrorCode.values) {
        final m = mapError(
          VideoKitStableError(code: code, stage: ErrorStage.playback),
        );
        expect(m.kind, StateViewKind.error);
        expect(m.detail, isNotNull, reason: code.name);
        expect(m.error!.code, code);
      }
    });

    test('table rows: actions only when meaningful', () {
      final disconnected = mapError(
        const VideoKitStableError(
          code: ErrorCode.sourceDisconnected,
          stage: ErrorStage.playback,
          retryable: true,
          suggestedAction: SuggestedAction.reconnectSource,
        ),
      );
      expect(disconnected.detail, StateDetail.connection);
      expect(disconnected.actions, [
        StateAction.reconnectSource,
        StateAction.retry,
      ]);
      final permission = mapError(
        const VideoKitStableError(
          code: ErrorCode.sourcePermissionDenied,
          stage: ErrorStage.bind,
          suggestedAction: SuggestedAction.checkPermission,
        ),
      );
      expect(permission.actions, [StateAction.checkPermission]);
      final corrupt = mapError(
        const VideoKitStableError(
          code: ErrorCode.corruptMedia,
          stage: ErrorStage.decode,
        ),
        fatal: true,
      );
      expect(corrupt.actions, isEmpty, reason: 'no dead buttons');
      final fatalRetry = mapError(
        const VideoKitStableError(
          code: ErrorCode.unsupportedVideoCodec,
          stage: ErrorStage.probe,
          retryable: true,
          suggestedAction: SuggestedAction.retry,
        ),
        fatal: true,
      );
      expect(fatalRetry.actions, isEmpty, reason: 'fatal errors cannot retry');
      final space = mapError(
        const VideoKitStableError(
          code: ErrorCode.outputSpaceInsufficient,
          stage: ErrorStage.sink,
          suggestedAction: SuggestedAction.freeSpace,
        ),
      );
      expect(space.actions, [StateAction.freeSpace, StateAction.reduceQuality]);
      expect(
        mapSessionState(phase: SessionPhase.errorFatal)!.error!.code,
        ErrorCode.internalErrorRedacted,
      );
    });

    test('state action labels exist for every action', () {
      final s = VkStrings.forLocale(const Locale('zh'));
      for (final a in StateAction.values) {
        expect(VideoKitStateView.actionLabel(s, a), isNotEmpty);
      }
      for (final d in StateDetail.values) {
        expect(
          VideoKitStateView.detail(
            s,
            StateViewModel(kind: StateViewKind.error, iconName: 'x', detail: d),
          ),
          isNotEmpty,
        );
      }
    });
  });

  group('host action layout (14 §5.4)', () {
    final actions = [
      HostActionState(action: _action('a', priority: 1)),
      HostActionState(action: _action('b', priority: 5)),
      HostActionState(
        action: _action(
          'c',
          placement: ActionPlacement.secondaryBar,
          priority: 1,
        ),
      ),
      HostActionState(
        action: _action('d', placement: ActionPlacement.overflow, priority: 9),
      ),
      HostActionState(action: _action('e', priority: 1)),
    ];
    List<String> ids(List<HostActionState> l) => [
      for (final a in l) a.action.actionId,
    ];

    test('sorted by priority, stable, OVERFLOW always in overflow', () {
      final l = layoutHostActions(actions, available: 1000, itemExtent: 50);
      expect(ids(l.visible), ['b', 'a', 'c', 'e']);
      expect(ids(l.overflow), ['d']);
    });

    test('limited space reserves one slot for the overflow button', () {
      final l = layoutHostActions(actions, available: 160, itemExtent: 50);
      expect(ids(l.visible), ['b', 'a']);
      expect(ids(l.overflow), ['d', 'c', 'e']);
    });

    test('collapseSecondary moves the whole SECONDARY_BAR group', () {
      final l = layoutHostActions(
        actions,
        available: 1000,
        itemExtent: 50,
        collapseSecondary: true,
      );
      expect(ids(l.visible), ['b', 'a', 'e']);
      expect(ids(l.overflow), ['d', 'c']);
    });

    test('everything fits without an overflow button', () {
      final l = layoutHostActions(
        actions.take(2).toList(),
        available: 100,
        itemExtent: 50,
      );
      expect(ids(l.visible), ['b', 'a']);
      expect(l.overflow, isEmpty);
    });
  });

  group('AutoHidePolicy (14 §4.4)', () {
    testWidgets('hides after the delay; blockers keep it visible', (
      tester,
    ) async {
      final p = AutoHidePolicy();
      expect(p.visible, isTrue);
      await tester.pump(const Duration(milliseconds: 2900));
      expect(p.visible, isTrue);
      await tester.pump(const Duration(milliseconds: 200));
      expect(p.visible, isFalse);
      p.kick();
      expect(p.visible, isTrue);
      p.setBlocker(AutoHideBlocker.focusInControls, true);
      await tester.pump(const Duration(seconds: 10));
      expect(p.visible, isTrue);
      expect(p.hide(), isFalse, reason: 'refused while blocked');
      p.setBlocker(AutoHideBlocker.focusInControls, false);
      await tester.pump(const Duration(seconds: 3));
      expect(p.visible, isFalse);
      p.toggle();
      expect(p.visible, isTrue);
      p.toggle();
      expect(p.visible, isFalse);
      for (final b in AutoHideBlocker.values) {
        p.setBlocker(b, true);
        expect(p.visible, isTrue, reason: b.name);
        p.setBlocker(b, false);
        await tester.pump(const Duration(seconds: 3));
        expect(p.visible, isFalse, reason: b.name);
      }
      // M2: "not playing" stops the timer but a tap may still hide.
      p
        ..kick()
        ..setBlocker(AutoHideBlocker.notPlaying, true);
      await tester.pump(const Duration(seconds: 10));
      expect(p.visible, isTrue, reason: 'no auto-hide while paused');
      expect(p.hide(), isTrue, reason: 'explicit tap hides');
      p
        ..kick()
        ..setBlocker(AutoHideBlocker.panelOpen, true);
      expect(p.hide(), isFalse, reason: 'a panel still refuses');
      p
        ..setBlocker(AutoHideBlocker.panelOpen, false)
        ..setBlocker(AutoHideBlocker.notPlaying, false);
      p.dispose();
    });
  });
}
