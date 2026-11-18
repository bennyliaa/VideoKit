// UI-AUDIT-A4 (TEST-PLAN-6 §3, design pages 7–24): loading view, the
// unsupported view, timeline media, keyframe range bar, editor bar and
// failed-export close.
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/editor/edit_demo_page.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  Future<void> frames(WidgetTester tester, [int n = 4]) async {
    for (var i = 0; i < n; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
  }

  Future<void> unmount(WidgetTester tester) async {
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
  }

  group('page 12', () {
    testWidgets('loading: back, title and spinner; no "more" yet; bottom '
        'controls disabled', (tester) async {
      setViewSize(tester, compactSize);
      final rig = await PlayerRig.create('slowLoad');
      addTearDown(rig.dispose);
      await tester.pumpWidget(testApp(demoPlayer(rig.session)));
      await tester.pump(const Duration(milliseconds: 300));
      expect(rig.session.state.value.phase.isBound, isFalse);
      expect(find.bySemanticsLabel('返回'), findsOneWidget);
      expect(find.text('演示视频'), findsOneWidget);
      expect(find.bySemanticsLabel('更多'), findsNothing);
      // The bottom controls stay, disabled (no enabled play key).
      final play = find.byWidgetPredicate(
        (w) => w is VkIconButton && w.icon == Icons.play_arrow_rounded,
      );
      for (final b in tester.widgetList<VkIconButton>(play)) {
        expect(b.onPressed, isNull, reason: 'disabled look');
      }
      await rig.advance(tester, const Duration(seconds: 4));
      expect(find.bySemanticsLabel('更多'), findsOneWidget);
      await unmount(tester);
    });

    testWidgets('unsupported: film icon and "无法播放此视频"', (tester) async {
      setViewSize(tester, compactSize);
      final rig = await PlayerRig.create('unsupported');
      addTearDown(rig.dispose);
      await tester.pumpWidget(testApp(demoPlayer(rig.session)));
      await rig.advance(tester, const Duration(seconds: 1));
      expect(find.text('无法播放此视频'), findsOneWidget);
      expect(find.byIcon(Icons.theaters_outlined), findsOneWidget);
      // 04A X2: the Fake's params name the reason.
      expect(find.text('本设备不支持 HEVC 10-bit 解码'), findsOneWidget);
      await unmount(tester);
    });

    testWidgets('X2: reasonDetail and params give the specific reason; '
        'unknown or incomplete falls back', (tester) async {
      Future<void> show(ErrorCode code, Map<String, String> params) async {
        await tester.pumpWidget(
          testApp(
            Scaffold(
              body: VideoKitStateView(
                model: mapError(
                  VideoKitStableError(
                    code: code,
                    stage: ErrorStage.probe,
                    params: params,
                  ),
                  fatal: true,
                ),
              ),
            ),
          ),
        );
        await tester.pump();
      }

      await show(ErrorCode.unsupportedVideoCodec, const {
        'codec': 'video/hevc',
        'profile': 'Main 10',
        'reasonDetail': 'EXCEEDS_CAPABILITIES',
      });
      expect(find.text('本设备不支持 HEVC Main 10 解码'), findsOneWidget);
      await show(ErrorCode.unsupportedVideoCodec, const {
        'codec': 'video/hevc',
        'profile': 'hvc1.2.4.L120',
        'reasonDetail': 'EXCEEDS_CAPABILITIES',
      });
      expect(find.text('本设备不支持 HEVC 解码'), findsOneWidget);
      await show(ErrorCode.unsupportedAudioCodec, const {
        'codec': 'audio/eac3',
        'reasonDetail': 'FORMAT_UNSUPPORTED',
      });
      expect(find.text('本设备没有 E-AC-3 解码器'), findsOneWidget);
      await show(ErrorCode.unsupportedContainer, const {
        'container': 'video/x-matroska',
        'reasonDetail': 'CONTAINER_UNSUPPORTED',
      });
      expect(find.text('本设备不支持 MKV 文件格式'), findsOneWidget);
      await show(ErrorCode.unsupportedVideoCodec, const {
        'codec': 'video/hevc',
        'reasonDetail': 'SOMETHING_NEW',
      });
      expect(find.text('本设备不支持此视频编码'), findsOneWidget);
      await show(ErrorCode.unsupportedContainer, const {
        'reasonDetail': 'CONTAINER_UNSUPPORTED',
      });
      expect(find.text('本设备不支持此文件格式'), findsOneWidget);
      await unmount(tester);
    });

    test('an unsupported image gets its own title', () {
      final m = mapSessionState(
        phase: SessionPhase.errorFatal,
        error: const VideoKitStableError(
          code: ErrorCode.unsupportedContainer,
          stage: ErrorStage.probe,
        ),
        mediaKind: MediaKind.imageStatic,
      )!;
      expect(m.iconName, 'film');
      expect(m.mediaKind, MediaKind.imageStatic);
    });
  });

  group('editor', () {
    Future<VideoKitEditorState> pumpEditor(
      WidgetTester tester, {
      Size size = expandedSize,
      EditDemoScenario scenario = EditDemoScenario.normal,
    }) async {
      setViewSize(tester, size);
      await tester.pumpWidget(
        testApp(EditDemoPage(initialScenario: scenario)),
      );
      await frames(tester, 15);
      return tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
    }

    testWidgets('page 15: "添加片段" in the toolbar; the timeline asks the '
        'project for thumbnails and waveforms', (tester) async {
      final e = await pumpEditor(tester);
      expect(find.text('添加片段'), findsOneWidget);
      expect(e.controller.project, isA<VideoKitEditMediaPreview>());
      await unmount(tester);
    });

    test('X2: thumbnails every 500 ms (local) / 2 s (slow), frozen', () {
      expect(TimelineView.thumbStepFor(SourceLatency.local), 500000);
      expect(TimelineView.thumbStepFor(SourceLatency.slow), 2000000);
    });

    testWidgets('X2: the editor passes the host latency to the controller', (
      tester,
    ) async {
      setViewSize(tester, expandedSize);
      final kit = FakeVideoKit();
      final p = (await tester.runAsync(
        () => kit.createEditProject(EditProjectConfig()),
      ))!;
      await tester.pumpWidget(
        testApp(
          VideoKitEditor(
            project: p,
            sink: const VideoKitOutputSink(sinkRef: 'demo:none'),
            sourceLatency: (id) =>
                id == 'slow' ? SourceLatency.slow : SourceLatency.local,
          ),
        ),
      );
      await frames(tester, 3);
      final c = tester
          .state<VideoKitEditorState>(find.byType(VideoKitEditor))
          .controller;
      expect(c.latencyOf('slow'), SourceLatency.slow);
      expect(c.latencyOf('other'), SourceLatency.local);
      await unmount(tester);
    });

    testWidgets('page 16: phone "导出" is a small pill', (tester) async {
      await pumpEditor(tester, size: compactSize);
      final export = tester.widget<VkButton>(
        find.widgetWithText(VkButton, '导出'),
      );
      expect(export.small, isTrue);
      await unmount(tester);
    });

    testWidgets('page 17: the keyframe card shows the range bar', (
      tester,
    ) async {
      final e = await pumpEditor(tester);
      e.openMasks(MaskEditorTab.manual);
      await frames(tester);
      unawaited(e.maskEditor!.addManualMask());
      await frames(tester);
      final bar = find.byWidgetPredicate(
        (w) => w is CustomPaint && w.painter is KeyframeRangePainter,
      );
      expect(bar, findsOneWidget);
      final p = tester.widget<CustomPaint>(bar).painter! as KeyframeRangePainter;
      final m = e.controller.state.maskById(e.controller.selectedMaskId!)!;
      expect((p.startUs, p.endUs), (m.startUs, m.endUs));
      expect(p.keyframesUs, isNotEmpty);
      await unmount(tester);
    });

    testWidgets('page 21: a failed export closes with "×"', (tester) async {
      final e = await pumpEditor(
        tester,
        size: compactSize,
        scenario: EditDemoScenario.exportFails,
      );
      final c = e.controller;
      e.openExport();
      await frames(tester);
      await tester.tap(find.text('开始导出'));
      for (var i = 0; i < 120 && c.state.phase != EditPhase.failed; i++) {
        await tester.pump(const Duration(milliseconds: 250));
      }
      await frames(tester, 2);
      expect(c.state.phase, EditPhase.failed);
      expect(find.bySemanticsLabel('关闭'), findsWidgets);
      expect(find.bySemanticsLabel('返回'), findsNothing);
      await unmount(tester);
    });
  });
}
