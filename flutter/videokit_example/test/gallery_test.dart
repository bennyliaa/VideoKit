import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_example/app.dart';
import 'package:videokit_example/gallery/gallery_page.dart';
import 'package:videokit_example/gallery/gallery_settings.dart';
import 'package:videokit_ui/videokit_ui.dart';

VideoKitThemeData _theme(WidgetTester tester) =>
    VkTheme.of(tester.element(find.byType(GalleryPage)));

Future<void> _pumpApp(WidgetTester tester, GallerySettings s, Size size) async {
  tester.view.physicalSize = size;
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.reset);
  await tester.pumpWidget(VideoKitExampleApp(initial: s));
  await tester.pumpAndSettle();
}

void main() {
  test('example ARB: template zh only, keys documented and non-empty', () {
    final files = Directory('lib/l10n').listSync().whereType<File>().toList();
    expect(files.map((f) => f.uri.pathSegments.last), ['app_zh.arb']);
    final arb =
        jsonDecode(files.single.readAsStringSync()) as Map<String, Object?>;
    for (final k in arb.keys.where((k) => !k.startsWith('@'))) {
      expect((arb[k]! as String).trim(), isNotEmpty, reason: k);
      expect(arb['@$k'], isNotNull, reason: k);
    }
  });

  testWidgets('starts dark, Chinese, with the permanent demo badge', (
    tester,
  ) async {
    await _pumpApp(tester, const GallerySettings(), const Size(1200, 2400));
    expect(find.text('VideoKit 主题画廊'), findsOneWidget);
    expect(
      find.descendant(
        of: find.byType(GalleryDemoBadge),
        matching: find.text('演示模式 · 模拟数据'),
      ),
      findsOneWidget,
    );
    expect(find.bySemanticsLabel('演示模式 · 模拟数据'), findsOneWidget);
    expect(_theme(tester).brightness, Brightness.dark);
    expect(_theme(tester).colors.primary, const Color(0xFFFF7A45));
  });

  testWidgets('switches light, host primary, pseudo locale, scale, motion', (
    tester,
  ) async {
    await _pumpApp(tester, const GallerySettings(), const Size(1200, 2400));

    await tester.tap(find.text('浅色'));
    await tester.pumpAndSettle();
    expect(_theme(tester).brightness, Brightness.light);
    expect(_theme(tester).colors.primary, const Color(0xFFC2410C));

    await tester.tap(find.text('#1565C0'));
    await tester.pumpAndSettle();
    final t = _theme(tester);
    expect(t.colors.primary, const Color(0xFF1565C0));
    expect(
      t.components.buttonPrimary.normal.background,
      const Color(0xFF1565C0),
    );
    expect(
      VkContrast.ratio(t.colors.onPrimary, t.colors.primary),
      greaterThanOrEqualTo(4.5),
    );

    await tester.tap(find.text('伪本地化'));
    await tester.pumpAndSettle();
    expect(find.text(VkPseudo.transform('VideoKit 主题画廊')), findsOneWidget);
    expect(
      find.descendant(
        of: find.byType(GalleryDemoBadge),
        matching: find.text(VkPseudo.transform('演示模式 · 模拟数据')),
      ),
      findsOneWidget,
    );
    expect(find.text('VideoKit 主题画廊'), findsNothing);

    await tester.tap(find.text('200%'));
    await tester.pumpAndSettle();
    expect(
      MediaQuery.textScalerOf(tester.element(find.byType(GalleryPage)))
          .scale(10),
      20,
    );
    expect(tester.takeException(), isNull);

    await tester.tap(find.textContaining('减少动画'));
    await tester.pumpAndSettle();
    expect(_theme(tester).animations.reduced, isTrue);
    expect(
      find.byType(GalleryDemoBadge),
      findsOneWidget,
      reason: 'badge stays',
    );
  });

  for (final locale in galleryLocales) {
    for (final scale in galleryTextScales) {
      testWidgets(
        'no overflow on a phone: ${locale.toLanguageTag()} × $scale',
        (tester) async {
          await _pumpApp(
            tester,
            GallerySettings(locale: locale, textScale: scale),
            const Size(360, 780),
          );
          expect(tester.takeException(), isNull);
          for (var i = 0; i < 15; i++) {
            await tester.drag(find.byType(ListView), const Offset(0, -700));
            await tester.pumpAndSettle();
            expect(tester.takeException(), isNull);
          }
          expect(find.byType(GalleryDemoBadge), findsOneWidget);
        },
      );
    }
  }

  testWidgets('meets tap target and label guidelines', (tester) async {
    final handle = tester.ensureSemantics();
    await _pumpApp(tester, const GallerySettings(), const Size(800, 1600));
    await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
    await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
    handle.dispose();
  });
}
