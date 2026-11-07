// M4-A1: UI-06 over the project API — chosen concat path in the editor and
// the export panel, engine refusal of fast concat, export failure/cancel,
// undo/redo through the project.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_example/editor/edit_demo_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  Future<VideoKitEditorState> pumpEditor(
    WidgetTester tester, {
    EditDemoScenario scenario = EditDemoScenario.normal,
  }) async {
    setViewSize(tester, expandedSize);
    await tester.pumpWidget(
      testApp(
        EditDemoPage(initialScenario: scenario, showScenarioPicker: false),
      ),
    );
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

  Future<void> unmount(WidgetTester tester) async {
    await tester.pumpWidget(const SizedBox());
    for (var i = 0; i < 5; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
  }

  testWidgets('matching inputs: editor and export panel show fast concat', (
    tester,
  ) async {
    final e = await pumpEditor(tester);
    expect(
      find.textContaining('快速拼接可用'),
      findsWidgets,
      reason: 'estimate line',
    );
    e.openExport();
    await settle(tester);
    expect(
      find.descendant(
        of: find.byType(ExportPanel),
        matching: find.text('拼接方式：快速拼接（不重新编码）'),
      ),
      findsOneWidget,
    );
    await unmount(tester);
  });

  testWidgets(
    'engine refuses fast concat: export page says transcode and why',
    (tester) async {
      final e = await pumpEditor(
        tester,
        scenario: EditDemoScenario.fastConcatRejected,
      );
      e.openExport();
      await settle(tester);
      final panel = find.byType(ExportPanel);
      expect(
        find.descendant(of: panel, matching: find.text('拼接方式：统一转码')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: panel, matching: find.text('导出检查未通过快速拼接，已改为统一转码')),
        findsOneWidget,
      );
      await unmount(tester);
    },
  );

  testWidgets('undo / redo go through the project; removing a clip updates '
      'the path', (tester) async {
    final e = await pumpEditor(tester);
    final c = e.controller;
    final before = c.state.timeline.clips.length;
    c.selectClip(c.state.timeline.clips.last.clipId);
    await c.removeSelected();
    await settle(tester);
    expect(c.state.timeline.clips, hasLength(before - 1));
    expect(c.state.canUndo, isTrue);
    await c.undo();
    await settle(tester);
    expect(c.state.timeline.clips, hasLength(before));
    expect(c.state.canRedo, isTrue);
    await c.redo();
    await settle(tester);
    expect(c.state.timeline.clips, hasLength(before - 1));
    await unmount(tester);
  });
}
