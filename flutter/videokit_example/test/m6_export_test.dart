// M6-A1 (VK-M6, UI-08): the write mode in the export check; only the final
// result counts as done (15 §2.8 constraint 4).
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/editor/edit_demo_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  Future<VideoKitEditorState> pumpEditor(
    WidgetTester tester, {
    EditDemoScenario scenario = EditDemoScenario.normal,
  }) async {
    setViewSize(tester, expandedSize);
    await tester.pumpWidget(testApp(EditDemoPage(initialScenario: scenario)));
    for (var i = 0; i < 15; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
    return tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
  }

  Future<void> settle(WidgetTester tester, [int n = 4]) async {
    for (var i = 0; i < n; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
  }

  testWidgets('the export check shows the write mode', (tester) async {
    final e = await pumpEditor(tester);
    e.openExport();
    await settle(tester);
    expect(find.text('写入方式'), findsOneWidget);
    expect(find.text('直接写入'), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
  });

  testWidgets('X1-1: the encoding stage reads 处理（解码 · 合成 · 编码）', (
    tester,
  ) async {
    final e = await pumpEditor(tester);
    final c = e.controller;
    e.openExport();
    await settle(tester);
    await tester.tap(find.text('开始导出'));
    var seen = false;
    for (var i = 0; i < 80 && c.state.phase != EditPhase.completed; i++) {
      await tester.pump(const Duration(milliseconds: 250));
      if (find.text('处理（解码 · 合成 · 编码）').evaluate().isNotEmpty) seen = true;
    }
    expect(seen, isTrue);
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
  });

  testWidgets('X1-3: a killed export worker has its own reason text', (
    tester,
  ) async {
    final e = await pumpEditor(
      tester,
      scenario: EditDemoScenario.workerKilled,
    );
    final c = e.controller;
    e.openExport();
    await settle(tester);
    await tester.tap(find.text('开始导出'));
    for (var i = 0; i < 80 && c.state.phase != EditPhase.failed; i++) {
      await tester.pump(const Duration(milliseconds: 250));
    }
    await settle(tester, 2);
    expect(find.text('导出失败'), findsOneWidget);
    expect(find.text('导出进程被系统结束，可能是内存不足'), findsOneWidget);
    expect(find.text('错误代码 EXPORT_FAILED'), findsOneWidget);
    expect(find.text('原视频未受影响'), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
  });

  testWidgets('X1-2: 正在清理… then 清理时间较长… after 5 s, then the result', (
    tester,
  ) async {
    final e = await pumpEditor(tester, scenario: EditDemoScenario.cleanupSlow);
    final c = e.controller;
    e.openExport();
    await settle(tester);
    await tester.tap(find.text('开始导出'));
    await settle(tester, 3);
    await tester.tap(find.text('取消导出'));
    await tester.pump(const Duration(milliseconds: 300));
    expect(c.state.phase, EditPhase.cancelling);
    expect(find.text('正在清理…'), findsOneWidget);
    expect(find.text('清理时间较长…'), findsNothing);
    await settle(tester, 25); // 5 s
    expect(find.text('清理时间较长…'), findsOneWidget);
    for (var i = 0; i < 40 && c.state.phase != EditPhase.cancelled; i++) {
      await tester.pump(const Duration(milliseconds: 250));
    }
    await settle(tester, 2);
    expect(find.text('清理时间较长…'), findsNothing);
    expect(find.text('已取消，未生成文件'), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
  });

  testWidgets('progress reaching the end is not success: a refused result '
      'shows the failure page', (tester) async {
    final e = await pumpEditor(
      tester,
      scenario: EditDemoScenario.failsAfterDone,
    );
    final c = e.controller;
    e.openExport();
    await settle(tester);
    await tester.tap(find.text('开始导出'));
    var sawWriting = false;
    for (var i = 0; i < 120 && c.state.phase != EditPhase.failed; i++) {
      await tester.pump(const Duration(milliseconds: 250));
      if (c.state.export?.stage == ExportStage.writing) sawWriting = true;
      expect(find.text('导出完成'), findsNothing, reason: 'never shown early');
    }
    expect(sawWriting, isTrue, reason: 'the last stage was reached');
    await settle(tester, 2);
    expect(c.state.phase, EditPhase.failed);
    expect(find.text('导出完成'), findsNothing);
    expect(find.text('导出失败'), findsOneWidget);
    expect(find.text('错误代码 EXPORT_FAILED'), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
  });
}
