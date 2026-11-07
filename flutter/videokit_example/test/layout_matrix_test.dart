import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_example/gallery/components_page.dart';
import 'package:videokit_example/player/player_demo_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

/// {中文, 伪本地化} × {1.0, 1.3, 2.0} × {compact, expanded} (M0-B2 item 5).
const _locales = [Locale('zh'), VkPseudo.locale];
const _scales = [1.0, 1.3, 2.0];
const _sizes = {'compact': compactSize, 'expanded': expandedSize};

void main() {
  for (final locale in _locales) {
    for (final scale in _scales) {
      for (final MapEntry(key: sizeName, value: size) in _sizes.entries) {
        final tag = '${locale.toLanguageTag()} × $scale × $sizeName';

        testWidgets('player + panels without overflow: $tag', (tester) async {
          setViewSize(tester, size);
          final rig = await PlayerRig.create('normal');
          addTearDown(rig.dispose);
          final key = GlobalKey<VideoKitPlayerState>();
          await tester.pumpWidget(
            testApp(
              demoPlayer(rig.session, key: key),
              locale: locale,
              textScale: scale,
            ),
          );
          await rig.advance(tester, const Duration(seconds: 1));
          expect(tester.takeException(), isNull);
          for (final panel in [
            PlayerPanel.speed,
            PlayerPanel.subtitles,
            PlayerPanel.audio,
            PlayerPanel.more,
          ]) {
            key.currentState!.openPanel(panel);
            await tester.pump(const Duration(milliseconds: 400));
            expect(tester.takeException(), isNull, reason: panel.name);
            await tester.binding.handlePopRoute();
            await tester.pump(const Duration(milliseconds: 400));
          }
          expect(tester.takeException(), isNull);
        });

        testWidgets('player state views without overflow: $tag', (
          tester,
        ) async {
          setViewSize(tester, size);
          for (final scenario in ['slowLoad', 'unsupported']) {
            final rig = await PlayerRig.create(scenario);
            await tester.pumpWidget(
              testApp(
                demoPlayer(rig.session),
                locale: locale,
                textScale: scale,
              ),
            );
            await rig.advance(tester, const Duration(milliseconds: 500));
            expect(tester.takeException(), isNull, reason: scenario);
            await tester.pumpWidget(const SizedBox());
            rig.dispose();
            await tester.pump(Duration.zero);
          }
        });

        testWidgets('components page without overflow: $tag', (tester) async {
          setViewSize(tester, size);
          await tester.pumpWidget(
            testApp(const ComponentsPage(), locale: locale, textScale: scale),
          );
          await tester.pump(const Duration(milliseconds: 100));
          expect(tester.takeException(), isNull);
          for (var i = 0; i < 20; i++) {
            await tester.drag(
              find.byType(ListView).first,
              Offset(0, -size.height * 0.8),
            );
            await tester.pump(const Duration(milliseconds: 200));
            expect(tester.takeException(), isNull);
          }
          await tester.pumpWidget(const SizedBox());
          await tester.pump(Duration.zero);
        });

        testWidgets('player demo page without overflow: $tag', (tester) async {
          setViewSize(tester, size);
          await tester.pumpWidget(
            testApp(const PlayerDemoPage(), locale: locale, textScale: scale),
          );
          for (var i = 0; i < 10; i++) {
            await tester.pump(const Duration(milliseconds: 200));
          }
          expect(tester.takeException(), isNull);
          await tester.pumpWidget(const SizedBox());
          await tester.pump(Duration.zero);
        });
      }
    }
  }

  group('accessibility guidelines', () {
    for (final MapEntry(key: sizeName, value: size) in _sizes.entries) {
      testWidgets('player: tap targets, labels, contrast ($sizeName)', (
        tester,
      ) async {
        final handle = tester.ensureSemantics();
        setViewSize(tester, size);
        final rig = await PlayerRig.create('normal');
        addTearDown(rig.dispose);
        await tester.pumpWidget(testApp(demoPlayer(rig.session)));
        await rig.advance(tester, const Duration(seconds: 1));
        await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
        await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
        await expectLater(tester, meetsGuideline(textContrastGuideline));
        handle.dispose();
      });

      for (final mode in [VideoKitThemeMode.dark, VideoKitThemeMode.light]) {
        testWidgets('components page: tap targets, labels, contrast '
            '($sizeName, ${mode.name})', (tester) async {
          final handle = tester.ensureSemantics();
          setViewSize(tester, size);
          await tester.pumpWidget(testApp(const ComponentsPage(), mode: mode));
          await tester.pump(const Duration(milliseconds: 100));
          await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
          await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
          await expectLater(tester, meetsGuideline(textContrastGuideline));
          await tester.pumpWidget(const SizedBox());
          await tester.pump(Duration.zero);
          handle.dispose();
        });
      }
    }
  });
}
