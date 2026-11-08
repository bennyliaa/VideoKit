import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

Widget _app(Widget child) => MaterialApp(
  locale: const Locale('zh'),
  localizationsDelegates: videoKitLocalizationsDelegates,
  supportedLocales: videoKitSupportedLocales,
  home: VideoKitThemeScope(child: Scaffold(body: child)),
);

SourceProbe _probe({
  int w = 1920,
  int h = 1080,
  double fps = 30,
  int rot = 0,
}) => SourceProbe(
  durationUs: 60000000,
  width: w,
  height: h,
  rotationDeg: rot,
  fps: fps,
  videoCodec: 'video/avc',
  audioCodec: 'audio/mp4a-latm',
  hasAudio: true,
);

void main() {
  group('TimelineScale (14 §5.6)', () {
    test('x ↔ time, zoom around the focus, limits', () {
      const s = TimelineScale(pxPerSecond: 50, scrollX: 100);
      expect(s.xForUs(4000000), 100);
      expect(s.usForX(100), 4000000);
      final z = s.zoomAround(100, 2);
      expect(z.pxPerSecond, 100);
      expect(z.usForX(100), 4000000, reason: 'focus time kept');
      expect(s.zoomAround(0, 100).pxPerSecond, TimelineScale.maxPxPerSecond);
      expect(s.zoomAround(0, 0.001).pxPerSecond, TimelineScale.minPxPerSecond);
      expect(s.tickStepUs(minLabelPx: 64), 2000000);
    });

    test('snap within 8 dp to the closest target only', () {
      const s = TimelineScale(pxPerSecond: 100);
      // 8 px = 80 ms.
      expect(s.snap(1050000, [1000000, 2000000], 8), 1000000);
      expect(s.snap(1100000, [1000000], 8), isNull);
      expect(s.snap(1030000, [1000000, 1050000], 8), 1050000);
    });
  });

  group('ConcatCompatibility (design page 16)', () {
    EditSource src(String id, SourceProbe p, {bool mismatch = false}) =>
        EditSource(sourceId: id, mediaToken: id, probe: p, mismatch: mismatch);

    test('equal inputs → fast concat; differences → transcode', () {
      final same = Timeline(sources: [src('a', _probe()), src('b', _probe())]);
      final c1 = ConcatCompatibility.of(same);
      expect(c1.fastConcat, isTrue);
      expect(c1.needsTranscode, isFalse);
      final diff = Timeline(
        sources: [
          src('a', _probe()),
          src('b', _probe(fps: 60)),
          src('c', _probe(w: 3840, h: 2160, rot: 90)),
        ],
      );
      final c2 = ConcatCompatibility.of(diff);
      expect(c2.mismatched, ['b', 'c']);
      expect(c2.fastConcat, isFalse);
      expect(
        ConcatCompatibility.of(same, fastConcatCapable: false).fastConcat,
        isFalse,
      );
      expect(
        ConcatCompatibility.of(
          Timeline(
            sources: [src('a', _probe()), src('b', _probe(), mismatch: true)],
          ),
        ).needsTranscode,
        isTrue,
      );
    });

    testWidgets('estimate: numbers, duration only, or 无法预估', (tester) async {
      Future<void> show(EditEstimate e) => tester.pumpWidget(
        _app(
          EstimateLine(
            estimate: e,
            compatibility: ConcatCompatibility.of(Timeline()),
          ),
        ),
      );
      await show(
        const EditEstimate(durationUs: 102000000, sizeBytes: 96000000),
      );
      // Design page 15: estimate and concat path on one line.
      expect(find.textContaining('预计 01:42 · 约 96 MB · '), findsOneWidget);
      await show(const EditEstimate(durationUs: 102000000));
      expect(find.textContaining('预计 01:42 · 大小无法预估 · '), findsOneWidget);
      await show(EditEstimate.unknown);
      expect(find.textContaining('无法预估 · '), findsOneWidget);
      expect(
        find.textContaining('MB'),
        findsNothing,
        reason: 'no fake numbers',
      );
    });
  });

  group('mask geometry', () {
    test('display rect letterboxes; region round-trips', () {
      final r = vkDisplayRect(
        const Size(400, 400),
        const VideoSize(1920, 1080),
      );
      expect(r.width, 400);
      expect(r.height, closeTo(225, 0.01));
      expect(r.top, closeTo(87.5, 0.01));
      const region = MaskRegion(x: 0.25, y: 0.5, width: 0.5, height: 0.25);
      final px = vkRegionToRect(region, r);
      final back = vkRectToRegion(px, r);
      expect(back.x, closeTo(0.25, 1e-9));
      expect(back.y, closeTo(0.5, 1e-9));
      expect(back.width, closeTo(0.5, 1e-9));
      expect(back.height, closeTo(0.25, 1e-9));
      final clamped = vkRectToRegion(const Rect.fromLTWH(-50, 0, 10, 1), r);
      expect(clamped.x, 0);
      expect(clamped.width, greaterThanOrEqualTo(0.02));
    });
  });

  group('CoverageStrip (14 §5.7)', () {
    testWidgets('segments are announced; legend has five states', (
      tester,
    ) async {
      final report = CoverageReport(
        segments: const [
          CoverageRange(
            startUs: 0,
            endUs: 4000000,
            state: TrackingState.tracked,
          ),
          CoverageRange(
            startUs: 4000000,
            endUs: 6000000,
            state: TrackingState.lost,
          ),
          CoverageRange(
            startUs: 6000000,
            endUs: 8000000,
            state: TrackingState.lowConfidence,
          ),
        ],
      );
      await tester.pumpWidget(
        _app(
          Column(
            children: [
              CoverageStrip(report: report, totalUs: 8000000, name: '目标 A'),
              const CoverageLegend(),
            ],
          ),
        ),
      );
      final node = tester.getSemantics(find.byType(CoverageStrip));
      expect(node.label, '目标 A 跟踪状态');
      expect(node.value, contains('丢失，00:04.0 – 00:06.0'));
      expect(node.value, contains('置信度低'));
      for (final l in ['已跟踪', '置信度低', '可能混淆', '丢失', '未分析']) {
        expect(find.text(l), findsOneWidget, reason: l);
      }
    });
  });

  testWidgets('VkSwitch: toggled semantics, 48 dp target', (tester) async {
    var v = false;
    await tester.pumpWidget(
      _app(
        StatefulBuilder(
          builder: (context, set) => VkSwitch(
            value: v,
            semanticLabel: '遮罩 1',
            onChanged: (x) => set(() => v = x),
          ),
        ),
      ),
    );
    expect(tester.getSize(find.byType(VkSwitch)).height, 48);
    await tester.tap(find.byType(VkSwitch));
    await tester.pump();
    expect(v, isTrue);
    expect(
      tester
          .getSemantics(find.bySemanticsLabel('遮罩 1'))
          .flagsCollection
          .isToggled
          .toString(),
      contains('isTrue'),
    );
  });
}
