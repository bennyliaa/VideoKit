// M3-A1: UI-05 over the session contract — per-slot bind/release, single
// slot faults, single audio with epochs (07 §4), visibility (07 §5.3),
// resource placeholders without retry loops (07 §3), audio preemption.
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/multiview/multi_view_demo_page.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

/// Session that logs its audio commands into a shared, ordered log.
final class LoggedSession extends RecordingSession {
  LoggedSession(super.inner, this.name, this.log);

  final String name;
  final List<String> log;

  @override
  Future<VideoKitCommandResult> execute(VideoKitCommand command) async {
    final r = await super.execute(command);
    if (command case SetActiveAudio(:final active, :final audioEpoch)) {
      log.add('$name:${active ? 'on' : 'off'}@$audioEpoch');
    }
    return r;
  }
}

Future<List<LoggedSession>> sessions(FakeVideoKit kit, List<String> log) async {
  final out = <LoggedSession>[];
  for (final n in ['a', 'b', 'c']) {
    final s = LoggedSession(
      await kit.createSession(const VideoKitSessionConfig()),
      n,
      log,
    );
    final f = s.bind(
      VideoKitMediaSource(
        mediaToken: n,
        mediaKind: MediaKind.video,
        sourceRef: const DemoSourceRef('normal'),
      ),
    );
    await kit.clock.advance(const Duration(seconds: 1));
    await f;
    out.add(s);
  }
  return out;
}

void main() {
  slotComponentTests();
  group('VideoKitAudioCoordinator (07 §4)', () {
    test('old source muted and confirmed before the new one unmutes', () async {
      final kit = FakeVideoKit();
      final log = <String>[];
      final [a, b, _] = await sessions(kit, log);
      final c = VideoKitAudioCoordinator();
      expect(await c.activate(a), isTrue);
      expect(await c.activate(b), isTrue);
      expect(log, ['a:on@1', 'a:off@2', 'b:on@2']);
      expect(a.state.value.activeAudio, isFalse);
      expect(a.state.value.muted, isTrue);
      expect(b.state.value.activeAudio, isTrue);
      expect(b.state.value.muted, isFalse);
      expect(c.active, b.sessionId);
      await kit.close();
    });

    test('a later switch supersedes one still in flight', () async {
      final kit = FakeVideoKit();
      final log = <String>[];
      final [a, b, cc] = await sessions(kit, log);
      final c = VideoKitAudioCoordinator();
      await c.activate(a);
      final first = c.activate(b);
      final second = c.activate(cc);
      expect(await first, isFalse, reason: 'superseded');
      expect(await second, isTrue);
      expect(c.active, cc.sessionId);
      expect(b.state.value.activeAudio, isFalse);
      expect(
        [
          for (final s in [a, b, cc]) s.state.value.activeAudio,
        ],
        [false, false, true],
        reason: 'exactly one source',
      );
      await kit.close();
    });

    test('target released during the switch → all muted', () async {
      final kit = FakeVideoKit();
      final log = <String>[];
      final [a, b, _] = await sessions(kit, log);
      final c = VideoKitAudioCoordinator();
      await c.activate(a);
      await b.release();
      expect(await c.activate(b), isFalse);
      expect(c.active, isNull);
      expect(a.state.value.activeAudio, isFalse);
      await kit.close();
    });

    test('source released or preempted → all muted; muteAll', () async {
      final kit = FakeVideoKit();
      final log = <String>[];
      final [a, b, _] = await sessions(kit, log);
      final c = VideoKitAudioCoordinator();
      await c.activate(a);
      c.onReleased(a.sessionId);
      expect(c.active, isNull);
      await c.activate(b);
      c.onAudioLost(b.sessionId);
      expect(c.active, isNull);
      await c.activate(b);
      await c.muteAll();
      expect(c.active, isNull);
      expect(b.state.value.activeAudio, isFalse);
      expect(b.state.value.muted, isTrue);
      // Epochs only grow.
      final epochs = [for (final l in log) int.parse(l.split('@').last)];
      final sorted = [...epochs]..sort();
      expect(epochs, sorted);
      await kit.close();
    });
  });

  group('UI-05 demo host', () {
    final key = GlobalKey<MultiViewDemoPageState>();

    Future<void> pumpPage(
      WidgetTester tester, {
      Size size = expandedSize,
      int? count,
    }) async {
      setViewSize(tester, size);
      await tester.pumpWidget(
        testApp(MultiViewDemoPage(key: key, initialCount: count)),
      );
      for (var i = 0; i < 12; i++) {
        await tester.pump(const Duration(milliseconds: 200));
      }
    }

    Future<void> settle(WidgetTester tester, [int n = 4]) async {
      for (var i = 0; i < n; i++) {
        await tester.pump(const Duration(milliseconds: 200));
      }
    }

    Future<void> unmount(WidgetTester tester) async {
      await tester.pumpWidget(const SizedBox());
      for (var i = 0; i < 5; i++) {
        await tester.pump(const Duration(milliseconds: 100));
      }
    }

    for (final n in [1, 4, 9, 12]) {
      testWidgets('$n slots: each binds and releases its own session', (
        tester,
      ) async {
        await pumpPage(tester, count: n);
        final st = key.currentState!;
        final kit = st.kit;
        expect(st.slots, hasLength(n));
        expect(kit.sessions, hasLength(n));
        expect({for (final s in st.slots) s.session.sessionId}, hasLength(n));
        for (final s in st.slots) {
          expect(s.session.state.value.phase, isNot(SessionPhase.created));
        }
        await unmount(tester);
        expect(kit.sessions, isEmpty, reason: 'all released with the page');
      });
    }

    testWidgets('single-slot fault: only that slot shows the error', (
      tester,
    ) async {
      await pumpPage(tester, count: 4);
      final st = key.currentState!;
      final target = st.kit.sessions.firstWhere(
        (s) => s.sessionId == st.slots[1].session.sessionId,
      );
      final before = find.text('仅此格受影响').evaluate().length;
      target.injectFault(
        const VideoKitStableError(
          code: ErrorCode.decoderUnavailable,
          stage: ErrorStage.playback,
        ),
      );
      await settle(tester);
      expect(find.text('仅此格受影响'), findsNWidgets(before + 1));
      for (final (i, s) in st.slots.indexed) {
        if (i == 1) {
          expect(s.session.state.value.phase, SessionPhase.errorFatal);
        } else if (s.kind == DemoSlotKind.video) {
          expect(s.session.state.value.error, isNull, reason: 'slot ${i + 1}');
        }
      }
      await unmount(tester);
    });

    testWidgets('tap a slot: it becomes the only audio source', (tester) async {
      await pumpPage(tester, count: 4);
      final st = key.currentState!;
      expect(st.activeAudio, st.slots.first.session.sessionId);
      await tester.tap(find.byType(VideoKitSlot).at(1));
      await settle(tester);
      expect(st.activeAudio, st.slots[1].session.sessionId);
      final audible = [
        for (final s in st.slots) s.session.state.value.activeAudio,
      ];
      expect(audible.where((a) => a), hasLength(1));
      expect(audible[1], isTrue);
      expect(find.text('发声'), findsOneWidget);
      await unmount(tester);
    });

    testWidgets('no decoder left → placeholder, no retry loop; freed decoder '
        'gives one more try', (tester) async {
      await pumpPage(tester, count: 12);
      final st = key.currentState!;
      final waiting = st.slots.where((s) => s.placeholder).toList();
      expect(waiting, isNotEmpty, reason: 'beyond the decoder budget');
      expect(find.text('资源不足 · 未播放'), findsWidgets);
      final sessionsBefore = st.kit.sessions.length;
      final phases = [for (final s in waiting) s.session.state.value.phase];
      await settle(tester, 50); // 10 s
      expect(st.kit.sessions.length, sessionsBefore, reason: 'no re-creation');
      expect(
        [for (final s in waiting) s.session.state.value.phase],
        phases,
        reason: 'no automatic rebinding',
      );
      // Removing a playing video frees its decoder: one placeholder retries.
      final victim = st.slots.firstWhere(
        (s) => s.kind == DemoSlotKind.video && !s.placeholder,
      );
      st.remove(victim);
      await settle(tester, 25);
      expect(waiting.first.placeholder, isFalse);
      expect(waiting.first.session.state.value.phase.isBound, isTrue);
      await unmount(tester);
    });

    testWidgets('audio preemption: muted, notice shown, nothing audible', (
      tester,
    ) async {
      await pumpPage(tester, count: 4);
      final st = key.currentState!;
      expect(st.activeAudio, isNotNull);
      st.kit.preemptAudio();
      await settle(tester, 2);
      expect(st.activeAudio, isNull);
      expect(find.text('其他应用正在播放声音，已静音'), findsOneWidget);
      expect(st.slots.where((s) => s.session.state.value.activeAudio), isEmpty);
      expect(find.text('发声'), findsNothing);
      await unmount(tester);
    });

    testWidgets('visibility: scrolled out, covered, background', (
      tester,
    ) async {
      // A short phone screen with 12 slots scrolls the grid.
      await pumpPage(tester, size: const Size(360, 520), count: 12);
      final st = key.currentState!;
      VideoKitSessionState last() => st.slots.last.session.state.value;
      VideoKitSessionState first() => st.slots.first.session.state.value;
      expect(first().visibility, SessionVisibility.visible);
      expect(last().visibility, SessionVisibility.offscreen);
      // Cover the page with a new route.
      final nav = tester.state<NavigatorState>(find.byType(Navigator));
      unawaited(
        nav.push(
          MaterialPageRoute<void>(builder: (_) => const SizedBox.expand()),
        ),
      );
      await settle(tester);
      expect(first().visibility, SessionVisibility.offscreen);
      nav.pop();
      await settle(tester);
      expect(first().visibility, SessionVisibility.visible);
      tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.paused);
      await settle(tester);
      expect(first().visibility, SessionVisibility.background);
      tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.resumed);
      await settle(tester);
      expect(first().visibility, SessionVisibility.visible);
      await unmount(tester);
    });
  });
}

/// Component tests of `VideoKitSlot` (M3 additions).
void slotComponentTests() {
  Future<RecordingSession> bound(WidgetTester tester, FakeVideoKit kit) async {
    final s = RecordingSession(
      await kit.createSession(const VideoKitSessionConfig()),
    );
    unawaited(
      s.bind(
        const VideoKitMediaSource(
          mediaToken: 'v',
          mediaKind: MediaKind.video,
          sourceRef: DemoSourceRef('normal'),
        ),
      ),
    );
    var done = false;
    unawaited(
      kit.clock
          .advance(const Duration(seconds: 1))
          .whenComplete(() => done = true),
    );
    while (!done) {
      await tester.pump(Duration.zero);
    }
    return s;
  }

  testWidgets('placeholder: cover with title/detail, wins over the error', (
    tester,
  ) async {
    setViewSize(tester, const Size(400, 300));
    final kit = FakeVideoKit(videoDecoderBudget: 0);
    final s = await bound(tester, kit);
    expect(s.state.value.phase, SessionPhase.errorRecoverable);
    var taps = 0;
    await tester.pumpWidget(
      testApp(
        VideoKitSlot(
          session: s,
          index: 1,
          title: '画面 1',
          degradation: SlotDegradation.placeholder,
          onTap: () => taps++,
        ),
      ),
    );
    expect(find.text('资源不足 · 未播放'), findsOneWidget);
    expect(find.text('减少画面数量后点按重试'), findsOneWidget);
    expect(find.text('仅此格受影响'), findsNothing, reason: 'no error card');
    await tester.tap(find.text('资源不足 · 未播放'));
    expect(taps, 1);
    // Small cells use the short text.
    setViewSize(tester, const Size(120, 90));
    await tester.pump();
    expect(find.text('未播放'), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
    unawaited(kit.close());
    await tester.pump(Duration.zero);
  });

  testWidgets('reportVisibility: false sends no SetVisibility', (tester) async {
    setViewSize(tester, const Size(400, 300));
    final kit = FakeVideoKit();
    final s = await bound(tester, kit);
    Widget slot(bool report) => testApp(
      SingleChildScrollView(
        child: Column(
          children: [
            const SizedBox(height: 2000),
            SizedBox(
              height: 200,
              child: VideoKitSlot(session: s, reportVisibility: report),
            ),
          ],
        ),
      ),
    );
    await tester.pumpWidget(slot(false));
    await tester.pump();
    expect(s.commands.whereType<SetVisibility>(), isEmpty);
    await tester.pumpWidget(slot(true));
    await tester.pump();
    await tester.pump();
    expect(s.commands.whereType<SetVisibility>().map((c) => c.visibility), [
      SessionVisibility.offscreen,
    ]);
    await tester.pumpWidget(const SizedBox());
    unawaited(kit.close());
    await tester.pump(Duration.zero);
  });
}
