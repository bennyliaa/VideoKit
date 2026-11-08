// TEST-R4 in the App: R4-02 (recent projects empty text without an edit
// engine), page 14 (the multi-view uses the shared chrome), O-4 (the first
// video starts with the audio), R4-03 (200 %: nothing pushed off screen).
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_app/pages/multi_view_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'app_test.dart' show pickDemo;
import 'm4_app_test.dart' show openRecent;
import 'r3_app_test.dart' show noEditing;
import 'support.dart';

void main() {
  testWidgets('R4-02: without an edit engine the empty "最近工程" says '
      'editing is coming', (tester) async {
    final rig = AppRig.create(backend: noEditing());
    await rig.pump(tester);
    await openRecent(tester);
    await settle(tester, 2);
    expect(find.text('编辑功能即将提供，届时这里会显示保存的工程。'), findsOneWidget);
    expect(find.textContaining('拼接为一个视频'), findsNothing);
    await unmount(tester);
  });

  testWidgets('R4-02: with an edit engine the empty text is unchanged', (
    tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    await openRecent(tester);
    await settle(tester, 2);
    expect(find.textContaining('还没有保存的工程'), findsOneWidget);
    await unmount(tester);
  });

  Future<MultiViewPageState> openMulti(
    WidgetTester tester, {
    double textScale = 1.0,
  }) async {
    final rig = AppRig.create();
    await rig.pump(tester, textScale: textScale);
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    await pickDemo(tester, ['山谷黄昏.mkv', '家庭录像.avi']);
    await tapText(tester, '在多画面中打开');
    await settle(tester, 8);
    return tester.state<MultiViewPageState>(find.byType(MultiViewPage));
  }

  testWidgets('page 14: the App multi-view has the count, the layout menu, '
      'the hint and "全部静音"; the first video has the audio', (tester) async {
    final page = await openMulti(tester);
    expect(find.byType(VideoKitMultiViewScaffold), findsOneWidget);
    expect(find.text('2 / 12'), findsOneWidget);
    expect(find.bySemanticsLabel('布局'), findsOneWidget);
    expect(find.text('点按画面切换声音来源，同一时间只有一路发声'), findsOneWidget);
    expect(find.widgetWithText(VkButton, '全部静音'), findsOneWidget);
    final first = page.sessions.values.first;
    expect(page.activeAudio, first.sessionId, reason: 'O-4: first video');
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    await unmount(tester);
  });

  testWidgets('R4-03: at 200 % the actions are in "更多" and nothing '
      'overflows', (tester) async {
    await openMulti(tester, textScale: 2);
    expect(tester.takeException(), isNull);
    expect(find.widgetWithText(VkButton, '全部静音'), findsNothing);
    await tester.tap(find.bySemanticsLabel('更多'));
    await settle(tester, 2);
    expect(find.text('全部静音'), findsOneWidget);
    expect(find.text('2×2'), findsOneWidget);
    await tester.tap(find.text('2×2'));
    await settle(tester, 2);
    expect(tester.takeException(), isNull);
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    await unmount(tester);
  });
}
