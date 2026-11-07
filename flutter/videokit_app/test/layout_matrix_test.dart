import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_app/settings/app_settings.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

/// {中文, 伪本地化} × {1.0, 1.3, 2.0} × {compact, expanded}.
const _locales = [Locale('zh'), VkPseudo.locale];
const _scales = [1.0, 1.3, 2.0];
const _sizes = {'compact': compactSize, 'expanded': expandedSize};

String _t(Locale l, String zh) =>
    VkPseudo.isPseudo(l) ? VkPseudo.transform(zh) : zh;

void main() {
  for (final locale in _locales) {
    for (final scale in _scales) {
      for (final MapEntry(key: sizeName, value: size) in _sizes.entries) {
        final tag = '${locale.toLanguageTag()} × $scale × $sizeName';

        testWidgets('empty state and picker sheet: $tag', (tester) async {
          final rig = AppRig.create();
          await rig.pump(tester, size: size, locale: locale, textScale: scale);
          expect(tester.takeException(), isNull, reason: 'empty');
          await tapText(tester, _t(locale, '打开文件'));
          await settle(tester, 2);
          expect(tester.takeException(), isNull, reason: 'picker');
          await unmount(tester);
        });

        for (final layout in HomeLayout.values) {
          testWidgets('home ${layout.name} + menu: $tag', (tester) async {
            final rig = AppRig.create(
              entries: sampleHistory(),
              settings: {'layout': layout.name},
            );
            await rig.pump(
              tester,
              size: size,
              locale: locale,
              textScale: scale,
            );
            expect(tester.takeException(), isNull, reason: 'home');
            for (var i = 0; i < 6; i++) {
              await tester.drag(
                find.byType(ListView).first,
                Offset(0, -size.height * 0.6),
              );
              await tester.pump(const Duration(milliseconds: 100));
              expect(tester.takeException(), isNull);
            }
            await tester.drag(
              find.byType(ListView).first,
              Offset(0, size.height * 6),
            );
            await tester.pump();
            await tester.tap(find.bySemanticsLabel(_t(locale, '更多')).first);
            await settle(tester, 2);
            expect(tester.takeException(), isNull, reason: 'menu');
            await unmount(tester);
          });
        }

        testWidgets('settings page: $tag', (tester) async {
          final rig = AppRig.create(entries: sampleHistory());
          await rig.pump(tester, size: size, locale: locale, textScale: scale);
          await tester.tap(find.bySemanticsLabel(_t(locale, '设置')));
          await settle(tester, 2);
          expect(tester.takeException(), isNull);
          for (var i = 0; i < 6; i++) {
            await tester.drag(
              find.byType(ListView).first,
              Offset(0, -size.height * 0.6),
            );
            await tester.pump(const Duration(milliseconds: 100));
            expect(tester.takeException(), isNull);
          }
          await unmount(tester);
        });
      }
    }
  }

  group('accessibility guidelines', () {
    for (final MapEntry(key: sizeName, value: size) in _sizes.entries) {
      for (final mode in ['dark', 'light']) {
        for (final page in ['empty', 'list', 'grid', 'settings']) {
          testWidgets('$page ($sizeName, $mode)', (tester) async {
            final handle = tester.ensureSemantics();
            final rig = AppRig.create(
              entries: page == 'empty' ? const [] : sampleHistory(),
              settings: {
                'themeMode': mode,
                'layout': page == 'grid' ? 'grid' : 'list',
              },
            );
            await rig.pump(tester, size: size);
            if (page == 'settings') {
              await tester.tap(find.bySemanticsLabel('设置'));
              await settle(tester, 6);
            } else if (page != 'empty') {
              // The contrast guideline samples pixels in each text's rect,
              // clipped or not: a line half under the list's edge would be
              // measured against the demo badge below. Check the list end,
              // where the footer is fully visible (R2-07).
              await tester.drag(
                find.byType(Scrollable).first,
                const Offset(0, -20000),
              );
              await settle(tester, 4);
            }
            await expectLater(
              tester,
              meetsGuideline(androidTapTargetGuideline),
            );
            await expectLater(
              tester,
              meetsGuideline(labeledTapTargetGuideline),
            );
            await expectLater(tester, meetsGuideline(textContrastGuideline));
            await unmount(tester);
            handle.dispose();
          });
        }
      }
    }
  });
}
