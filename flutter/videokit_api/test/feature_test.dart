// VK-A2 (REQ-API-10): feature list, static switches with the EDIT
// dependency, gate answers, timeouts.
import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';

final class _Host extends NoopHostCallbacks {
  _Host(this.answer);

  final Future<FeatureAccess> Function(VideoKitFeature f) answer;
  final List<(VideoKitFeature, String?)> asked = [];

  @override
  Future<FeatureAccess> checkFeature(VideoKitFeature f, String? sessionId) {
    asked.add((f, sessionId));
    return answer(f);
  }
}

void main() {
  test('5 configurable features with stable wire names; unknown fallback',
      () {
    expect(VideoKitFeature.configurable.map((f) => f.wireName), [
      'MULTI_VIEW',
      'EDIT',
      'MASK_TRACKING',
      'AVATAR',
      'EXPORT',
    ]);
    expect(VideoKitFeature.fromName('MASK_TRACKING'), VideoKitFeature.maskTracking);
    expect(VideoKitFeature.fromName('QUOTA'), VideoKitFeature.unknown);
    expect(FeatureMode.fromName('NOPE'), FeatureMode.enabled);
    expect(FeatureBadge.fromName(null), isNull);
    expect(FeatureBadge.fromName('GOLD'), FeatureBadge.unknown);
  });

  test('hiding EDIT hides MASK_TRACKING and AVATAR, not EXPORT\'s '
      'switch or MULTI_VIEW', () {
    const c = VideoKitFeatureConfig({VideoKitFeature.edit: FeatureMode.hidden});
    expect(c.isEnabled(VideoKitFeature.edit), isFalse);
    expect(c.isEnabled(VideoKitFeature.maskTracking), isFalse);
    expect(c.isEnabled(VideoKitFeature.avatar), isFalse);
    expect(c.isEnabled(VideoKitFeature.multiView), isTrue);
    expect(c.isEnabled(VideoKitFeature.unknown), isTrue);
    final only = VideoKitFeatureConfig.allEnabled.withMode(
      VideoKitFeature.avatar,
      FeatureMode.hidden,
    );
    expect(only.isEnabled(VideoKitFeature.avatar), isFalse);
    expect(only.isEnabled(VideoKitFeature.maskTracking), isTrue);
    expect(only, isNot(VideoKitFeatureConfig.allEnabled));
  });

  test('answers: allowed (with an optional marker), denied (lock by '
      'default)', () {
    expect(FeatureAccess.allowed.isAllowed, isTrue);
    expect(FeatureAccess.allowed.badge, isNull);
    expect(const FeatureAllowed(FeatureBadge.trial).badge, FeatureBadge.trial);
    expect(const FeatureDenied().badge, FeatureBadge.lock);
    expect(const FeatureDenied(null).badge, isNull);
    expect(const FeatureDenied().isAllowed, isFalse);
  });

  test('the default config and callbacks allow everything (FT01B-03)', () async {
    const config = VideoKitConfig();
    expect(config.features, VideoKitFeatureConfig.allEnabled);
    for (final f in VideoKitFeature.configurable) {
      expect((await config.featureGate.check(f)).isAllowed, isTrue);
    }
    expect(
      await const NoopHostCallbacks().checkFeature(VideoKitFeature.edit, null),
      FeatureAccess.allowed,
    );
  });

  test('gate: hidden throws FEATURE_DISABLED without asking (as Kotlin); '
      'throw and timeout count as denied without a marker', () async {
    final host = _Host((f) async => const FeatureDenied(FeatureBadge.lock));
    final gate = VideoKitFeatureGate(
      config: const VideoKitFeatureConfig({
        VideoKitFeature.export: FeatureMode.hidden,
      }),
      callbacks: host,
      timeout: const Duration(milliseconds: 20),
    );
    await expectLater(
      gate.check(VideoKitFeature.export),
      throwsA(
        isA<VideoKitException>()
            .having((e) => e.error.code, 'code', ErrorCode.featureDisabled)
            .having((e) => e.error.params['feature'], 'feature', 'EXPORT'),
      ),
    );
    expect(host.asked, isEmpty);
    expect(
      await gate.check(VideoKitFeature.edit, sessionId: 'p1'),
      const FeatureDenied(),
    );
    expect(host.asked.single, (VideoKitFeature.edit, 'p1'));
    final throwing = VideoKitFeatureGate(
      callbacks: _Host((f) async => throw StateError('host')),
    );
    expect(await throwing.check(VideoKitFeature.edit), const FeatureDenied(null));
    final slow = VideoKitFeatureGate(
      callbacks: _Host((f) => Completer<FeatureAccess>().future),
      timeout: const Duration(milliseconds: 20),
    );
    expect(await slow.check(VideoKitFeature.edit), const FeatureDenied(null));
  });

  test('errors carry the feature and the badge', () {
    final d = VideoKitFeatureGate.disabledError(
      VideoKitFeature.export,
      stage: ErrorStage.export,
    );
    expect((d.code, d.stage, d.params['feature']), (
      ErrorCode.featureDisabled,
      ErrorStage.export,
      'EXPORT',
    ));
    final x = VideoKitFeatureGate.deniedError(
      VideoKitFeature.avatar,
      badge: FeatureBadge.lock,
    );
    expect((x.code, x.retryable, x.params['badge']), (
      ErrorCode.featureDenied,
      true,
      'LOCK',
    ));
  });
}
