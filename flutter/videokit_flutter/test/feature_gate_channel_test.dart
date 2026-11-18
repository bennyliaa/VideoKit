// REQ-API-10 (VK-A2-B): the Dart side sends the static switches in the
// handshake and answers the native feature gate with the Dart host's
// checkFeature; the native runtime enforces both at its entry points.
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter/src/msg_mapping.dart';
import 'package:videokit_flutter/videokit_flutter.dart';

import 'fake_platform.dart';

class _GateHost extends NoopHostCallbacks {
  final List<String> asked = [];

  @override
  Future<FeatureAccess> checkFeature(
    VideoKitFeature feature,
    String? sessionId,
  ) async {
    asked.add('${feature.wireName}:$sessionId');
    return feature == VideoKitFeature.export
        ? const FeatureDenied()
        : const FeatureAllowed(FeatureBadge.trial);
  }
}

void main() {
  test('the handshake carries the switches and the gate timeout', () async {
    final api = FakeHostApi();
    await FlutterVideoKit.connect(
      const VideoKitConfig(
        features: VideoKitFeatureConfig({
          VideoKitFeature.export: FeatureMode.hidden,
          VideoKitFeature.multiView: FeatureMode.enabled,
          VideoKitFeature.unknown: FeatureMode.hidden,
        }),
        callbackTimeouts: HostCallbackTimeouts(
          featureGate: Duration(seconds: 12),
        ),
      ),
      platform: FakePlatform(api),
    );
    expect(api.handshakeRequest!.features, {
      'EXPORT': 'HIDDEN',
      'MULTI_VIEW': 'ENABLED',
    });
    expect(api.handshakeRequest!.featureGateTimeoutMs, 12000);
  });

  test('without switches the handshake sends an empty map', () async {
    final api = FakeHostApi();
    await FlutterVideoKit.connect(
      const VideoKitConfig(),
      platform: FakePlatform(api),
    );
    expect(api.handshakeRequest!.features, isEmpty);
    expect(api.handshakeRequest!.featureGateTimeoutMs, 30000);
  });

  test('the native gate reaches the Dart host and maps its answer', () async {
    final host = _GateHost();
    final platform = FakePlatform(FakeHostApi());
    await FlutterVideoKit.connect(
      VideoKitConfig(hostCallbacks: host),
      platform: platform,
    );
    final denied = await platform.callbacks!.checkFeature('EXPORT', 'p-1');
    expect(denied.access, 'DENIED');
    expect(denied.badge, 'LOCK');
    final allowed = await platform.callbacks!.checkFeature('EDIT', null);
    expect(allowed.access, 'ALLOWED');
    expect(allowed.badge, 'TRIAL');
    expect(host.asked, ['EXPORT:p-1', 'EDIT:null']);
  });

  test('a host without a gate allows everything', () async {
    final platform = FakePlatform(FakeHostApi());
    await FlutterVideoKit.connect(const VideoKitConfig(), platform: platform);
    final answer = await platform.callbacks!.checkFeature('MULTI_VIEW', 's-1');
    expect(answer.access, 'ALLOWED');
    expect(answer.badge, isNull);
  });

  test('feature mappings', () {
    expect(
      featureAccessToMsg(const FeatureDenied(null)).badge,
      isNull,
    );
    expect(hiddenFeaturesFromMsg(['EDIT', 'FUTURE', 'EXPORT']), {
      VideoKitFeature.edit,
      VideoKitFeature.export,
    });
    expect(hiddenFeaturesFromMsg(null), isEmpty);
  });
}
