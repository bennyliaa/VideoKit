import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/editor/edit_demo_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

Future<void> tapText(WidgetTester tester, String text) async {
  final f = find.text(text).last;
  await tester.ensureVisible(f);
  await tester.pump();
  await tester.tap(f);
}

void main() {
  Future<VideoKitEditorState> pumpEditor(
    WidgetTester tester, {
    Size size = expandedSize,
    EditDemoScenario scenario = EditDemoScenario.normal,
  }) async {
    setViewSize(tester, size);
    await tester.pumpWidget(testApp(EditDemoPage(initialScenario: scenario)));
    for (var i = 0; i < 15; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
    return tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
  }

  Future<void> settle(WidgetTester tester, [int frames = 4]) async {
    for (var i = 0; i < frames; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
  }

  Future<void> unmount(WidgetTester tester) async {
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
  }

  Offset clipCenter(WidgetTester tester, EditorController c, int index) {
    final box = tester.getTopLeft(find.byType(TimelineView));
    final starts = c.clipStarts();
    final clip = c.state.timeline.clips[index];
    final x = c.scale.xForUs(starts[index] + clip.durationUs ~/ 2);
    final d = VkTheme.of(tester.element(find.byType(TimelineView))).dimensions;
    return box + Offset(x, d.spacing24 + d.spacing4 + d.timelineClipRow / 2);
  }

  group('UI-06 editor', () {
    testWidgets('select, split, undo/redo; properties and estimate', (
      tester,
    ) async {
      final e = await pumpEditor(tester);
      final c = e.controller;
      expect(c.state.timeline.clips, hasLength(3));
      expect(find.textContaining('预计 01:00'), findsOneWidget);
      expect(find.text('快速拼接可用'), findsWidgets);
      await tester.tapAt(clipCenter(tester, c, 1));
      await settle(tester);
      expect(c.selectedClipId, c.state.timeline.clips[1].clipId);
      expect(find.text('片段 2 属性'), findsOneWidget);
      expect(find.text('00:00.000'), findsOneWidget, reason: 'in point');
      expect(find.text('20 秒'), findsOneWidget);
      // Tapping the clip moved the playhead into it: split there.
      await tester.tap(find.bySemanticsLabel('分割').first);
      await settle(tester);
      expect(c.state.timeline.clips, hasLength(4));
      expect(c.state.canUndo, isTrue);
      await tester.tap(find.bySemanticsLabel('撤销'));
      await settle(tester);
      expect(c.state.timeline.clips, hasLength(3));
      await tester.tap(find.bySemanticsLabel('重做'));
      await settle(tester);
      expect(c.state.timeline.clips, hasLength(4));
      await unmount(tester);
    });

    testWidgets('trim drag commits one TrimClip at the end', (tester) async {
      final e = await pumpEditor(tester);
      final c = e.controller;
      c.selectClip(c.state.timeline.clips[0].clipId);
      await settle(tester, 1);
      final rev = c.state.revision;
      final box = tester.getTopLeft(find.byType(TimelineView));
      final d = VkTheme.of(tester.element(find.byType(TimelineView)))
          .dimensions;
      final clip = c.state.timeline.clips[0];
      final endX = c.scale.xForUs(clip.durationUs);
      final g = await tester.startGesture(
        box + Offset(endX - 2, d.spacing24 + d.spacing4 + d.spacing16),
      );
      for (var i = 0; i < 10; i++) {
        await g.moveBy(const Offset(-8, 0));
        await tester.pump(const Duration(milliseconds: 16));
      }
      expect(c.state.revision, rev, reason: 'nothing committed mid-drag');
      await g.up();
      await settle(tester);
      expect(c.state.revision, rev + 1, reason: 'exactly one command');
      expect(c.state.timeline.clips[0].outUs, lessThan(clip.outUs));
      await unmount(tester);
    });

    testWidgets('long-press drag reorders with one MoveClip', (tester) async {
      final e = await pumpEditor(tester);
      final c = e.controller;
      final first = c.state.timeline.clips[0].clipId;
      final rev = c.state.revision;
      final from = clipCenter(tester, c, 0);
      final to = clipCenter(tester, c, 2) + const Offset(20, 0);
      final g = await tester.startGesture(from);
      await tester.pump(const Duration(milliseconds: 700));
      for (var i = 1; i <= 10; i++) {
        await g.moveTo(Offset.lerp(from, to, i / 10)!);
        await tester.pump(const Duration(milliseconds: 16));
      }
      await g.up();
      await settle(tester);
      expect(c.state.revision, rev + 1);
      expect(c.state.timeline.clips.last.clipId, first);
      await unmount(tester);
    });

    testWidgets('zoom buttons keep 10–400 px/s; order sheet lists clips', (
      tester,
    ) async {
      final e = await pumpEditor(tester);
      final c = e.controller;
      final before = c.scale.pxPerSecond;
      await tester.tap(find.bySemanticsLabel('放大时间线'));
      await tester.pump();
      expect(c.scale.pxPerSecond, closeTo(before * 1.5, 0.01));
      for (var i = 0; i < 20; i++) {
        await tester.tap(find.bySemanticsLabel('放大时间线'));
      }
      await tester.pump();
      expect(c.scale.pxPerSecond, TimelineScale.maxPxPerSecond);
      await tapText(tester, '排序');
      await settle(tester, 2);
      expect(find.text('多视频拼接'), findsOneWidget);
      expect(find.text('3 个视频'), findsOneWidget);
      expect(find.text('参数一致，可快速拼接'), findsOneWidget);
      await tester.tap(find.text('添加视频').last);
      await settle(tester, 4);
      expect(c.state.timeline.clips, hasLength(4));
      await unmount(tester);
    });

    testWidgets('compact: bottom navigation and selected clip card', (
      tester,
    ) async {
      final e = await pumpEditor(tester, size: compactSize);
      final c = e.controller;
      expect(find.text('点按时间线上的片段进行编辑'), findsOneWidget);
      await tester.tapAt(clipCenter(tester, c, 0));
      await settle(tester);
      expect(find.text('片段 1 · 20 秒'), findsOneWidget);
      for (final l in ['剪辑', '添加', '打码', '跟踪', '导出']) {
        expect(find.bySemanticsLabel(l), findsWidgets, reason: l);
      }
      await tester.tap(find.bySemanticsLabel('导出').last);
      await settle(tester);
      expect(c.mode, EditorMode.export);
      expect(find.text('导出预设'), findsOneWidget);
      await unmount(tester);
    });
  });

  group('UI-07 masks', () {
    testWidgets('manual mask: add, drag box → keyframe, style, toggle', (
      tester,
    ) async {
      final e = await pumpEditor(tester);
      final c = e.controller;
      e.openMasks(MaskEditorTab.manual);
      await settle(tester);
      await tester.tap(find.bySemanticsLabel('添加遮罩'));
      await settle(tester);
      expect(c.state.masks, hasLength(1));
      final m = c.state.masks.single;
      expect(find.text('遮罩 1 · 手动'), findsOneWidget);
      // Move the playhead inside the mask, then drag the box once.
      unawaited(c.seek(m.startUs + 2000000));
      await settle(tester, 2);
      final rev = c.state.revision;
      final boxFinder = find.bySemanticsLabel('遮罩 1');
      final center = tester.getCenter(boxFinder);
      final g = await tester.startGesture(center);
      for (var i = 0; i < 8; i++) {
        await g.moveBy(const Offset(6, 3));
        await tester.pump(const Duration(milliseconds: 16));
      }
      await g.up();
      await settle(tester);
      expect(c.state.revision, rev + 1);
      expect(c.state.masks.single.keyframes, hasLength(2));
      await tapText(tester, '模糊');
      await settle(tester);
      expect(c.state.masks.single.style, MaskStyle.blur);
      await tester.tap(find.byWidgetPredicate((w) => w is VkSwitch && w.value));
      await settle(tester);
      expect(c.state.masks.single.enabled, isFalse);
      await unmount(tester);
    });

    testWidgets('faces: detect, choose target, progress, cancel, coverage', (
      tester,
    ) async {
      final e = await pumpEditor(tester);
      final c = e.controller;
      e.openMasks(MaskEditorTab.tracking);
      await settle(tester);
      expect(find.text('本机处理 · 不上传'), findsOneWidget);
      await tapText(tester, '检测人脸');
      await settle(tester);
      final cands = e.maskEditor!.candidates!;
      expect(cands, isNotEmpty);
      expect(find.textContaining('检测到'), findsOneWidget);
      await tester.tap(find.bySemanticsLabel('人脸 1').first);
      await settle(tester, 2);
      final auto = c.state.masks.where((m) => m.type == MaskType.face);
      expect(auto, hasLength(1));
      expect(
        c.state.tracking[auto.single.maskId]?.status,
        TrackingRunStatus.running,
      );
      expect(find.text('跟踪中'), findsWidgets);
      await tapText(tester, '取消跟踪');
      await settle(tester);
      expect(
        c.state.tracking[auto.single.maskId]?.status,
        TrackingRunStatus.cancelled,
      );
      expect(find.byType(CoverageStrip), findsOneWidget);
      expect(find.byType(CoverageLegend), findsOneWidget);
      await unmount(tester);
    });

    testWidgets('lost range → 纠正 → draw box → CorrectTracking', (tester) async {
      final e = await pumpEditor(
        tester,
        scenario: EditDemoScenario.trackingLost,
      );
      final c = e.controller;
      e.openMasks(MaskEditorTab.tracking);
      await settle(tester);
      await tapText(tester, '检测人脸');
      await settle(tester);
      await tester.tap(find.bySemanticsLabel('人脸 1').first);
      // Let tracking finish (wall time ≈ duration / speed).
      for (var i = 0; i < 80; i++) {
        await tester.pump(const Duration(milliseconds: 250));
        final run = c.state.tracking.values.firstOrNull;
        if (run?.status == TrackingRunStatus.completed) break;
      }
      final run = c.state.tracking.values.single;
      expect(run.status, TrackingRunStatus.completed);
      expect(run.coverage.blockingSegments, isNotEmpty);
      expect(find.text('丢失，00:04 – 00:06'), findsOneWidget);
      await tester.tap(find.text('纠正').first);
      await settle(tester, 2);
      expect(e.maskEditor!.correcting, isNotNull);
      final rev = c.state.revision;
      final preview = find.byType(MaskOverlay);
      final r = tester.getRect(preview);
      final g = await tester.startGesture(r.center - const Offset(40, 30));
      for (var i = 0; i < 8; i++) {
        await g.moveBy(const Offset(10, 8));
        await tester.pump(const Duration(milliseconds: 16));
      }
      await g.up();
      await settle(tester);
      expect(c.state.revision, rev + 1);
      expect(
        c.state.tracking.values.single.status,
        TrackingRunStatus.running,
        reason: 'recomputed from the correction point',
      );
      expect(find.text('待重新计算'), findsOneWidget);
      await unmount(tester);
    });
  });

  group('UI-08 export', () {
    Future<void> waitPhase(
      WidgetTester tester,
      EditorController c,
      bool Function(EditPhase) done, {
      int max = 120,
    }) async {
      for (var i = 0; i < max; i++) {
        await tester.pump(const Duration(milliseconds: 250));
        if (done(c.state.phase)) return;
      }
    }

    testWidgets('precheck passes, stages, success summary + demo notice', (
      tester,
    ) async {
      final e = await pumpEditor(tester, size: compactSize);
      final c = e.controller;
      e.openExport();
      await settle(tester);
      expect(find.text('原始'), findsOneWidget);
      expect(find.text('格式 MP4 · H.264 · AAC'), findsOneWidget);
      expect(find.text('编码器可用'), findsOneWidget);
      expect(find.text('由宿主提供'), findsOneWidget);
      expect(find.textContaining('可用 12.4 GB'), findsOneWidget);
      expect(find.text('没有自动跟踪遮罩'), findsOneWidget);
      await tapText(tester, '开始导出');
      await tester.pump(const Duration(milliseconds: 300));
      expect(c.state.phase, EditPhase.exporting);
      expect(find.text('正在导出'), findsOneWidget);
      expect(find.text('准备'), findsOneWidget);
      expect(find.text('写入宿主位置'), findsOneWidget);
      expect(
        find.descendant(
          of: find.byType(ExportPanel),
          matching: find.text('跟踪'),
        ),
        findsNothing,
        reason: 'no tracking stage',
      );
      await waitPhase(tester, c, (p) => p == EditPhase.completed);
      await settle(tester, 2);
      expect(find.text('导出完成'), findsOneWidget);
      expect(find.text('演示模式：未生成真实媒体文件'), findsOneWidget);
      expect(find.text('MP4 · H.264 · AAC'), findsOneWidget);
      expect(find.text('打开'), findsOneWidget, reason: 'host action');
      await unmount(tester);
    });

    testWidgets('failure: reason, impact, code, smaller preset', (
      tester,
    ) async {
      final e = await pumpEditor(
        tester,
        size: compactSize,
        scenario: EditDemoScenario.exportFails,
      );
      final c = e.controller;
      e.openExport();
      await settle(tester);
      await tapText(tester, '开始导出');
      await waitPhase(tester, c, (p) => p == EditPhase.failed);
      await settle(tester, 2);
      expect(
        find.descendant(
          of: find.byType(ExportPanel),
          matching: find.text('导出失败'),
        ),
        findsOneWidget,
      );
      expect(find.text('原视频未受影响'), findsOneWidget);
      expect(find.text('未完成的输出已丢弃'), findsOneWidget);
      expect(find.text('错误代码 OUTPUT_SPACE_INSUFFICIENT'), findsOneWidget);
      await tapText(tester, '改用 1080p 重新导出');
      await settle(tester);
      expect(e.exportPanel!.presetId, ExportPresets.p1080);
      expect(find.text('开始导出'), findsOneWidget);
      await unmount(tester);
    });

    testWidgets('cancel: cancelling then cancelled, no file', (tester) async {
      final e = await pumpEditor(
        tester,
        size: compactSize,
        scenario: EditDemoScenario.cancelSlow,
      );
      final c = e.controller;
      e.openExport();
      await settle(tester);
      await tapText(tester, '开始导出');
      await settle(tester, 3);
      await tapText(tester, '取消导出');
      await tester.pump(const Duration(milliseconds: 300));
      expect(c.state.phase, EditPhase.cancelling);
      expect(find.text('正在取消…'), findsOneWidget);
      await waitPhase(tester, c, (p) => p == EditPhase.cancelled);
      await settle(tester, 2);
      expect(find.text('已取消，未生成文件'), findsOneWidget);
      await unmount(tester);
    });

    testWidgets('uncovered ranges: check sheet, force export is marked', (
      tester,
    ) async {
      final e = await pumpEditor(
        tester,
        scenario: EditDemoScenario.trackingLost,
      );
      final c = e.controller;
      e.openMasks(MaskEditorTab.tracking);
      await settle(tester);
      await tapText(tester, '检测人脸');
      await settle(tester);
      await tester.tap(find.bySemanticsLabel('人脸 1').first);
      for (var i = 0; i < 80; i++) {
        await tester.pump(const Duration(milliseconds: 250));
        if (c.state.tracking.values.firstOrNull?.status ==
            TrackingRunStatus.completed) {
          break;
        }
      }
      e.openExport();
      await settle(tester);
      expect(find.text('有 1 个未覆盖区间'), findsOneWidget);
      expect(find.text('开始导出'), findsNothing);
      await tapText(tester, '查看未覆盖区间');
      await settle(tester, 2);
      expect(find.text('发现 1 个未覆盖区间'), findsOneWidget);
      expect(find.text('目标 A · 00:04 – 00:06'), findsOneWidget);
      await tapText(tester, '仍要导出（结果将标记为“打码不完整”）');
      await waitPhase(tester, c, (p) => p == EditPhase.completed);
      await settle(tester, 2);
      expect(find.text('导出完成'), findsOneWidget);
      expect(find.textContaining('打码不完整'), findsOneWidget);
      await unmount(tester);
    });

    testWidgets('full-frame mask resolves the uncovered range', (tester) async {
      final e = await pumpEditor(
        tester,
        scenario: EditDemoScenario.trackingLost,
      );
      final c = e.controller;
      e.openMasks(MaskEditorTab.tracking);
      await settle(tester);
      await tapText(tester, '检测人脸');
      await settle(tester);
      await tester.tap(find.bySemanticsLabel('人脸 1').first);
      for (var i = 0; i < 80; i++) {
        await tester.pump(const Duration(milliseconds: 250));
        if (c.state.tracking.values.firstOrNull?.status ==
            TrackingRunStatus.completed) {
          break;
        }
      }
      e.openExport();
      await settle(tester);
      await tapText(tester, '查看未覆盖区间');
      await settle(tester, 2);
      await tapText(tester, '全画面打码');
      await settle(tester, 4);
      expect(
        c.state.masks.where(
          (m) =>
              m.type == MaskType.manual && m.keyframes.first.region.width == 1,
        ),
        hasLength(1),
      );
      expect(find.text('全部目标已覆盖'), findsOneWidget);
      expect(find.text('开始导出'), findsOneWidget);
      await unmount(tester);
    });
  });
}
