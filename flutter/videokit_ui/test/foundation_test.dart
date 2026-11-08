import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/src/foundation/auto_hide.dart';
import 'package:videokit_ui/src/foundation/command_dispatcher.dart';
import 'package:videokit_ui/src/foundation/selector.dart';
import 'package:videokit_ui/videokit_ui.dart';

/// Executor whose results the test completes manually.
class _Exec {
  final List<VideoKitCommand> sent = [];
  final List<Completer<VideoKitCommandResult>> pending = [];
  Object? throwOnNext;

  Future<VideoKitCommandResult> call(VideoKitCommand c) {
    sent.add(c);
    if (throwOnNext != null) {
      final e = throwOnNext!;
      throwOnNext = null;
      return Future.error(e);
    }
    final completer = Completer<VideoKitCommandResult>();
    pending.add(completer);
    return completer.future;
  }

  void completeAll([VideoKitCommandResult r = const Executed()]) {
    for (final c in List.of(pending)) {
      if (!c.isCompleted) c.complete(r);
    }
    pending.clear();
  }
}

const _err = VideoKitStableError(
  code: ErrorCode.corruptMedia,
  stage: ErrorStage.playback,
);

void main() {
  group('VkLayoutClass', () {
    test('thresholds 600 / 840 on the component width', () {
      expect(VkLayoutClass.fromWidth(0), VkLayoutClass.compact);
      expect(VkLayoutClass.fromWidth(599.9), VkLayoutClass.compact);
      expect(VkLayoutClass.fromWidth(600), VkLayoutClass.medium);
      expect(VkLayoutClass.fromWidth(839.9), VkLayoutClass.medium);
      expect(VkLayoutClass.fromWidth(840), VkLayoutClass.expanded);
      expect(
        VkLayoutClass.of(const BoxConstraints(maxWidth: 700)),
        VkLayoutClass.medium,
      );
      expect(VkLayoutClass.of(const BoxConstraints()), VkLayoutClass.expanded);
    });

    test('text scale above 1.3 collapses secondary controls', () {
      expect(VkLayoutClass.collapseSecondary(TextScaler.noScaling), isFalse);
      expect(
        VkLayoutClass.collapseSecondary(const TextScaler.linear(1.3)),
        isFalse,
      );
      expect(
        VkLayoutClass.collapseSecondary(const TextScaler.linear(2)),
        isTrue,
      );
    });

    testWidgets('VkLayoutBuilder uses its own constraints', (tester) async {
      final seen = <VkLayoutClass>[];
      await tester.pumpWidget(
        Directionality(
          textDirection: TextDirection.ltr,
          child: Column(
            children: [
              SizedBox(
                width: 300,
                child: VkLayoutBuilder(
                  builder: (_, c, _) {
                    seen.add(c);
                    return const SizedBox();
                  },
                ),
              ),
              SizedBox(
                width: 650,
                child: VkLayoutBuilder(
                  builder: (_, c, _) {
                    seen.add(c);
                    return const SizedBox();
                  },
                ),
              ),
            ],
          ),
        ),
      );
      expect(seen, [VkLayoutClass.compact, VkLayoutClass.medium]);
    });
  });

  group('VkSelector', () {
    testWidgets('rebuilds only when the selected slice changes', (
      tester,
    ) async {
      final state = ValueNotifier(
        VideoKitSessionState(phase: SessionPhase.playing, positionUs: 0),
      );
      var builds = 0;
      await tester.pumpWidget(
        Directionality(
          textDirection: TextDirection.ltr,
          child: VkSelector<VideoKitSessionState, SessionPhase>(
            listenable: state,
            select: (s) => s.phase,
            builder: (context, phase) {
              builds++;
              return Text(phase.name);
            },
          ),
        ),
      );
      expect(builds, 1);
      for (var i = 1; i <= 10; i++) {
        state.value = state.value.copyWith(positionUs: i * 250000);
        await tester.pump();
      }
      expect(builds, 1, reason: 'position updates do not rebuild');
      state.value = state.value.copyWith(phase: SessionPhase.paused);
      await tester.pump();
      expect(builds, 2);
      expect(find.text('paused'), findsOneWidget);
      state.dispose();
    });

    testWidgets('custom equals and listenable swap', (tester) async {
      final a = ValueNotifier<int>(1);
      final b = ValueNotifier<int>(10);
      var builds = 0;
      Widget sel(ValueNotifier<int> n) => Directionality(
        textDirection: TextDirection.ltr,
        child: VkSelector<int, int>(
          listenable: n,
          select: (v) => v,
          equals: (x, y) => x ~/ 10 == y ~/ 10,
          builder: (context, v) {
            builds++;
            return Text('$v');
          },
        ),
      );
      await tester.pumpWidget(sel(a));
      a.value = 5; // same bucket
      await tester.pump();
      expect(builds, 1);
      await tester.pumpWidget(sel(b));
      expect(find.text('10'), findsOneWidget);
      a.value = 50; // old listenable no longer observed
      await tester.pump();
      expect(find.text('10'), findsOneWidget);
      b.value = 20;
      await tester.pump();
      expect(find.text('20'), findsOneWidget);
      a.dispose();
      b.dispose();
    });
  });

  group('CommandDispatcher (14 §4.3)', () {
    late _Exec exec;
    late List<DispatchFeedback> feedback;
    late CommandDispatcher d;

    setUp(() {
      exec = _Exec();
      feedback = [];
      d = CommandDispatcher(execute: exec.call, onFeedback: feedback.add);
    });

    tearDown(() {
      exec.completeAll();
    });

    test('play/pause: last intent wins while one is in flight', () async {
      final first = d.setPlaying(true);
      expect(await d.setPlaying(false), isNull);
      expect(await d.setPlaying(true), isNull);
      expect(await d.setPlaying(false), isNull);
      expect(exec.sent, [const Play()]);
      exec.completeAll();
      await Future<void>.delayed(Duration.zero);
      expect(exec.sent, [const Play(), const Pause()]);
      exec.completeAll();
      expect(await first, const Executed());
    });

    test('play/pause: pending equal to the sent intent is dropped', () async {
      final first = d.setPlaying(true);
      unawaited(d.setPlaying(false));
      unawaited(d.setPlaying(true));
      exec.completeAll();
      await first;
      expect(exec.sent, [const Play()]);
    });

    test('other kinds: repeat while in flight is ignored', () async {
      final a = d.dispatch(const SetMuted(true));
      expect(await d.dispatch(const SetMuted(false)), isNull);
      expect(exec.sent, [const SetMuted(true)]);
      exec.completeAll();
      await a;
      unawaited(d.dispatch(const SetMuted(false)));
      expect(exec.sent.last, const SetMuted(false));
    });

    test('Rejected / Unsupported / Superseded feedback', () async {
      final r = d.dispatch(const SetSpeed(9));
      exec.completeAll(const Rejected(_err));
      expect(await r, const Rejected(_err));
      expect((feedback.single as RejectedFeedback).error, _err);

      var notified = 0;
      d.addListener(() => notified++);
      final u = d.dispatch(const SelectAudioTrack('x'));
      exec.completeAll(const Unsupported(UnsupportedReason.trackNotFound));
      await u;
      expect(d.isUnsupported('selectAudioTrack'), isTrue);
      expect(
        d.unsupportedReason('selectAudioTrack'),
        UnsupportedReason.trackNotFound,
      );
      expect(feedback.last, isA<UnsupportedFeedback>());
      expect(notified, 1);

      final s = d.dispatch(const SeekTo(1));
      exec.completeAll(const Superseded());
      await s;
      expect(feedback, hasLength(2), reason: 'Superseded is silent');
    });

    test('host actions: repeat in flight ignored, Superseded silent', () async {
      final calls = <String>[];
      final completers = <Completer<VideoKitCommandResult>>[];
      final hd = CommandDispatcher(
        execute: exec.call,
        onFeedback: feedback.add,
        requestHostAction: (id) {
          calls.add(id);
          final c = Completer<VideoKitCommandResult>();
          completers.add(c);
          return c.future;
        },
      );
      final first = hd.requestHostAction('fav');
      expect(await hd.requestHostAction('fav'), isNull);
      unawaited(hd.requestHostAction('tag'));
      expect(calls, ['fav', 'tag']);
      completers[0].complete(const Superseded());
      completers[1].complete(const Unsupported(UnsupportedReason.hostDisabled));
      expect(await first, const Superseded());
      await Future<void>.delayed(Duration.zero);
      expect(feedback.single, isA<UnsupportedFeedback>());
      expect(feedback.single.kind, CommandDispatcher.hostActionKind('tag'));
      expect(hd.isUnsupported('hostAction:tag'), isTrue);
      hd.dispose();
    });

    test('SessionReleased makes the dispatcher read-only', () async {
      final r = d.dispatch(const Play());
      exec.completeAll(const SessionReleased());
      await r;
      expect(d.readOnly, isTrue);
      expect(feedback.single, isA<SessionReleasedFeedback>());
      expect(await d.dispatch(const SetMuted(true)), const SessionReleased());
      expect(exec.sent, hasLength(1), reason: 'nothing sent after release');
    });

    test('exceptions become INTERNAL_ERROR_REDACTED, never rethrown', () async {
      exec.throwOnNext = StateError('boom');
      final r = await d.dispatch(const SetVolume(0.5));
      expect(r, isA<Rejected>());
      expect((r! as Rejected).error.code, ErrorCode.internalErrorRedacted);
      expect(
        (feedback.single as RejectedFeedback).error.code,
        ErrorCode.internalErrorRedacted,
      );
    });

    test('results after dispose are dropped', () async {
      final r = d.dispatch(const SetMuted(true));
      d.dispose();
      exec.completeAll(const Rejected(_err));
      expect(await r, isNull);
      expect(feedback, isEmpty);
      expect(await d.dispatch(const Play()), isNull);
    });

    testWidgets('drag seek: ≥100 ms previews, trailing value, final seek', (
      tester,
    ) async {
      final e = _Exec();
      final fb = <DispatchFeedback>[];
      final disp = CommandDispatcher(execute: e.call, onFeedback: fb.add);
      // 60 drag updates over 600 ms (every 10 ms).
      for (var i = 0; i < 60; i++) {
        disp.seekDrag(i * 100000);
        await tester.pump(const Duration(milliseconds: 10));
      }
      final previews = e.sent.whereType<SeekTo>().toList();
      expect(previews.every((s) => s.mode == SeekMode.preview), isTrue);
      expect(previews.length, inInclusiveRange(6, 7));
      // Superseded previews are silent.
      e.completeAll(const Superseded());
      await tester.pump();
      expect(fb, isEmpty);
      // Release: pending trailing preview cancelled, one closestSync seek.
      disp.seekDrag(7000000);
      final end = disp.seekEnd(7100000);
      await tester.pump(const Duration(milliseconds: 500));
      final after = e.sent.skip(previews.length).toList();
      expect(after.last, const SeekTo(7100000));
      expect(
        after.whereType<SeekTo>().where((s) => s.mode == SeekMode.preview),
        hasLength(lessThanOrEqualTo(1)),
      );
      e.completeAll();
      expect(await end, const Executed());
      disp.dispose();
    });
  });

  test('R5-01b: AutoHidePolicy.setTouching pauses the timer without showing '
      'or refusing a hide', () async {
    final p = AutoHidePolicy(delay: const Duration(milliseconds: 50));
    addTearDown(p.dispose);
    p.setTouching(true);
    await Future<void>.delayed(const Duration(milliseconds: 120));
    expect(p.visible, isTrue, reason: 'timer paused');
    expect(p.hide(), isTrue, reason: 'a tap may still hide');
    p.setTouching(false);
    expect(p.visible, isFalse, reason: 'touching does not show');
    p.show();
    p
      ..setTouching(true)
      ..setTouching(false);
    await Future<void>.delayed(const Duration(milliseconds: 120));
    expect(p.visible, isFalse, reason: 'timer restarted on release');
  });
}
