// UI-AUDIT-A3: editor autosave (design page 15) — 2 s debounce, "正在保存…",
// "已自动保存", "未保存" with retry.
import 'dart:async';
import 'dart:io';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/editor/edit_demo_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  Future<VideoKitEditorState> pumpEditor(WidgetTester tester) async {
    setViewSize(tester, expandedSize);
    await tester.pumpWidget(testApp(const EditDemoPage()));
    for (var i = 0; i < 15; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
    return tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
  }

  Future<void> wait(WidgetTester tester, Duration d) async {
    final steps = d.inMilliseconds ~/ 100;
    for (var i = 0; i < steps; i++) {
      await tester.pump(const Duration(milliseconds: 100));
    }
  }

  testWidgets('04A P6: a slow source drags with the time bubble only, no '
      'preview frames', (tester) async {
    setViewSize(tester, expandedSize);
    final rig = await PlayerRig.create('slowSource');
    addTearDown(rig.dispose);
    await tester.pumpWidget(
      testApp(demoPlayer(rig.session, latencyHint: SourceLatency.slow)),
    );
    await rig.advance(tester, const Duration(seconds: 3));
    final bar = find.byType(VkSeekBar);
    final g = await tester.startGesture(tester.getCenter(bar));
    for (var i = 0; i < 20; i++) {
      await g.moveBy(const Offset(15, 0));
      await tester.pump(const Duration(milliseconds: 16));
    }
    expect(rig.session.thumbnailRequests, isEmpty);
    expect(find.byKey(const ValueKey('vk-seek-preview-frame')), findsNothing);
    await g.up();
    await tester.pump(const Duration(milliseconds: 100));
  });

  test('04A P6: SourceLatency defaults to local; wire names', () {
    const src = VideoKitMediaSource(
      mediaToken: 't',
      mediaKind: MediaKind.video,
      sourceRef: DemoSourceRef('slowSource'),
    );
    expect(src.latencyHint, SourceLatency.local);
    expect(
      src.copyWith(latencyHint: SourceLatency.slow).latencyHint,
      SourceLatency.slow,
    );
    expect(SourceLatency.slow.wireName, 'SLOW');
    expect(SourceLatency.fromName('SLOW'), SourceLatency.slow);
    expect(SourceLatency.fromName('???'), SourceLatency.local);
    expect(src == src.copyWith(latencyHint: SourceLatency.slow), isFalse);
  });

  testWidgets('an edit shows "正在保存…", then "已自动保存" 2 s later', (tester) async {
    final e = await pumpEditor(tester);
    await wait(tester, const Duration(seconds: 3));
    final auto = e.autosave!;
    final c = e.controller;
    expect(c.state.canUndo, isTrue, reason: 'the demo built its timeline');
    unawaited(c.undo());
    await tester.pump();
    expect(auto.status, AutosaveStatus.saving);
    expect(find.text('正在保存…'), findsOneWidget);
    await wait(tester, const Duration(seconds: 1));
    expect(auto.status, AutosaveStatus.saving, reason: 'debounce');
    await wait(tester, const Duration(milliseconds: 1500));
    expect(auto.status, AutosaveStatus.saved);
    expect(find.text('已自动保存'), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
    await tester.pump(const Duration(seconds: 3));
  });

  testWidgets('edits inside the debounce save once; a failure shows '
      '"未保存" and retry saves', (tester) async {
    final e = await pumpEditor(tester);
    await wait(tester, const Duration(seconds: 3));
    var calls = 0;
    var fail = true;
    final auto = EditorAutosave(
      project: e.widget.project,
      save: () async {
        calls++;
        if (fail) throw const FileSystemException('disk full');
      },
    );
    addTearDown(auto.dispose);
    final c = e.controller;
    unawaited(c.undo());
    await wait(tester, const Duration(milliseconds: 500));
    unawaited(c.redo());
    await wait(tester, const Duration(milliseconds: 2500));
    expect(calls, 1, reason: 'one save after the last edit');
    expect(auto.status, AutosaveStatus.failed);
    fail = false;
    await auto.saveNow();
    expect(calls, 2);
    expect(auto.status, AutosaveStatus.saved);
    await tester.pumpWidget(const SizedBox());
    await tester.pump(const Duration(seconds: 3));
  });
}
