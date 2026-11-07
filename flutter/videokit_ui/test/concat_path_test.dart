// M4-A1: chosen concat path and the reason when it is a transcode.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

EditSource src(
  String id, {
  int w = 1920,
  int h = 1080,
  double fps = 30,
  String codec = 'video/avc',
  int rot = 0,
  bool mismatch = false,
}) => EditSource(
  sourceId: id,
  mediaToken: id,
  mismatch: mismatch,
  probe: SourceProbe(
    durationUs: 10000000,
    width: w,
    height: h,
    fps: fps,
    videoCodec: codec,
    rotationDeg: rot,
  ),
);

void main() {
  final s = VkStrings.forLocale(const Locale('zh'));

  test('matching inputs on a capable device: fast, no reason', () {
    final c = ConcatCompatibility.of(Timeline(sources: [src('a'), src('b')]));
    expect(c.fastConcat, isTrue);
    expect(c.reason, isNull);
    expect(c.multiInput, isTrue);
    expect(ConcatPathInfo.reasons(s, c), isEmpty);
  });

  test('device without remux: transcode, device reason', () {
    final c = ConcatCompatibility.of(
      Timeline(sources: [src('a'), src('b')]),
      fastConcatCapable: false,
    );
    expect(c.fastConcat, isFalse);
    expect(c.reason, ConcatFallbackReason.deviceUnsupported);
    expect(ConcatPathInfo.reasons(s, c), ['此设备不支持快速拼接']);
  });

  test('differing inputs: one line per differing property, in order', () {
    final c = ConcatCompatibility.of(
      Timeline(
        sources: [
          src('a'),
          src('b', rot: 90, fps: 25),
          src('c', w: 1280, h: 720, codec: 'video/hevc'),
          src('d', mismatch: true),
        ],
      ),
    );
    expect(c.reason, ConcatFallbackReason.inputsDiffer);
    expect(c.mismatched, ['b', 'c', 'd']);
    expect(ConcatPathInfo.reasons(s, c), [
      '分辨率不同',
      '帧率不同',
      '视频编码不同',
      '旋转方向不同',
      '有视频无法直接拼接',
    ]);
  });

  test('engine refusal at the export check turns fast into transcode', () {
    final fast = ConcatCompatibility.of(
      Timeline(sources: [src('a'), src('b')]),
    );
    final rejected = fast.withPrecheck(
      ExportPrecheck(warnings: const [ExportWarnings.fastConcatRejected]),
    );
    expect(rejected.fastConcat, isFalse);
    expect(rejected.reason, ConcatFallbackReason.engineRejected);
    expect(ConcatPathInfo.reasons(s, rejected), ['导出检查未通过快速拼接，已改为统一转码']);
    expect(fast.withPrecheck(ExportPrecheck()), fast);
    expect(fast.withPrecheck(null), fast);
  });

  test('single input: path not shown', () {
    final c = ConcatCompatibility.of(Timeline(sources: [src('a')]));
    expect(c.multiInput, isFalse);
  });

  testWidgets('ConcatPathInfo renders path and reasons', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: videoKitLocalizationsDelegates,
        supportedLocales: videoKitSupportedLocales,
        home: VideoKitThemeScope(
          child: Scaffold(
            body: ConcatPathInfo(
              compatibility: ConcatCompatibility.of(
                Timeline(sources: [src('a'), src('b', fps: 60)]),
              ),
            ),
          ),
        ),
      ),
    );
    expect(find.text('拼接方式：统一转码'), findsOneWidget);
    expect(find.text('帧率不同'), findsOneWidget);
    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: videoKitLocalizationsDelegates,
        supportedLocales: videoKitSupportedLocales,
        home: VideoKitThemeScope(
          child: Scaffold(
            body: ConcatPathInfo(
              compatibility: ConcatCompatibility.of(
                Timeline(sources: [src('a'), src('b')]),
              ),
            ),
          ),
        ),
      ),
    );
    expect(find.text('拼接方式：快速拼接（不重新编码）'), findsOneWidget);
  });
}
