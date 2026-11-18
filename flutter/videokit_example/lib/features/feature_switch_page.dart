import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../editor/edit_demo_page.dart';
import '../gallery/gallery_text.dart';
import '../multiview/multi_view_demo_page.dart';

/// What the demo host's gate answers for a feature.
enum GateAnswer {
  /// Allowed.
  allow,

  /// Allowed with a "试用中" marker.
  trial,

  /// Denied with a lock (the demo host shows its "付费页" dialog first).
  deny,
}

/// Demo host with a scripted feature gate (REQ-API-10 ②, FT01B-02).
final class GateDemoHost extends NoopHostCallbacks {
  /// Creates the host.
  GateDemoHost({required this.answers, this.onDenied});

  /// Answer per feature (missing = allow).
  final Map<VideoKitFeature, GateAnswer> answers;

  /// Shows the host's own page for a denied feature (the demo dialog).
  final Future<void> Function(VideoKitFeature feature)? onDenied;

  /// Features asked, in order (tests).
  final List<VideoKitFeature> asked = [];

  @override
  Future<FeatureAccess> checkFeature(
    VideoKitFeature feature,
    String? sessionId,
  ) async {
    asked.add(feature);
    switch (answers[feature] ?? GateAnswer.allow) {
      case GateAnswer.allow:
        return FeatureAccess.allowed;
      case GateAnswer.trial:
        return const FeatureAllowed(FeatureBadge.trial);
      case GateAnswer.deny:
        await onDenied?.call(feature);
        return const FeatureDenied();
    }
  }
}

/// "功能开关" demo panel (VK-A2, FT01B-01/02/03): hide each of the 5
/// features, script the host's gate answer, then open the editor or the
/// multi-view, or call the API directly to see `FEATURE_DISABLED` /
/// `FEATURE_DENIED`.
class FeatureSwitchPage extends StatefulWidget {
  /// Creates the page.
  const FeatureSwitchPage({super.key});

  @override
  State<FeatureSwitchPage> createState() => FeatureSwitchPageState();
}

/// State (public for tests).
class FeatureSwitchPageState extends State<FeatureSwitchPage> {
  /// Hidden features.
  final Set<VideoKitFeature> hidden = {};

  /// Gate answers.
  final Map<VideoKitFeature, GateAnswer> answers = {};

  /// Use a gate at all (off = a host without `checkFeature`, FT01B-03).
  bool gateOn = true;

  /// Result of the last direct API call.
  String? apiResult;

  /// The switches.
  VideoKitFeatureConfig get config => VideoKitFeatureConfig({
    for (final f in hidden) f: FeatureMode.hidden,
  });

  /// The demo host for the current settings.
  VideoKitHostCallbacks host() => gateOn
      ? GateDemoHost(answers: Map.of(answers), onDenied: _paywall)
      : const NoopHostCallbacks();

  Future<void> _paywall(VideoKitFeature feature) async {
    if (!mounted) return;
    final g = GalleryText.of(context);
    final s = VkStrings.of(context);
    await showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(g(g.l.featurePaywallTitle)),
        content: Text(g(g.l.featurePaywallBody(featureName(g, feature)))),
        actions: [
          VkButton(
            label: s.text('commonClose'),
            variant: VkButtonVariant.text,
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      ),
    );
  }

  /// Name of [f].
  static String featureName(GalleryText g, VideoKitFeature f) => g(switch (f) {
    VideoKitFeature.multiView => g.l.featureMultiView,
    VideoKitFeature.edit => g.l.featureEdit,
    VideoKitFeature.maskTracking => g.l.featureMaskTracking,
    VideoKitFeature.avatar => g.l.featureAvatar,
    VideoKitFeature.export => g.l.featureExport,
    VideoKitFeature.unknown => g.l.featureEdit,
  });

  /// Opens the editor with these switches and this gate.
  void openEditor() => unawaited(
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => EditDemoPage(
          showScenarioPicker: false,
          features: config,
          hostCallbacks: host(),
        ),
      ),
    ),
  );

  /// Opens the multi-view through the gate (no entry when hidden).
  Future<void> openMultiView() async {
    final gate = VideoKitFeatureGate(config: config, callbacks: host());
    if (!gate.isEnabled(VideoKitFeature.multiView)) return;
    final access = await gate.check(VideoKitFeature.multiView);
    if (!access.isAllowed || !mounted) return;
    await Navigator.of(context).push(
      MaterialPageRoute<void>(builder: (_) => const MultiViewDemoPage()),
    );
  }

  /// Calls the Kit directly (no UI): what an API caller gets.
  Future<void> callApi() async {
    final kit = FakeVideoKit(
      config: VideoKitConfig(hostCallbacks: host(), features: config),
    );
    String result;
    try {
      final p = await kit.createEditProject(EditProjectConfig());
      final add = await p.apply(
        const AddMask(
          MaskType.manual,
          MaskRegion(x: 0.4, y: 0.4, width: 0.2, height: 0.2),
          0,
          1000000,
        ),
      );
      result = switch (add) {
        EditUnsupported(:final reason) => 'AddMask: ${reason.wireName}',
        EditRejected(:final error) => 'AddMask: ${error.code.wireName}',
        _ => 'AddMask: OK',
      };
      // What `export` would answer, without running an export.
      // A hidden feature throws FEATURE_DISABLED (REQ-API-10).
      final String exportCode;
      try {
        final access = await kit.features.check(VideoKitFeature.export);
        exportCode = access.isAllowed
            ? 'OK'
            : ErrorCode.featureDenied.wireName;
      } on VideoKitException catch (e) {
        exportCode = e.error.code.wireName;
      }
      result = '$result · export: $exportCode';
      await p.close();
    } on VideoKitException catch (e) {
      result = 'createEditProject: ${e.error.code.wireName}';
    }
    await kit.close();
    if (mounted) setState(() => apiResult = result);
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final enabled = config;
    return Scaffold(
      backgroundColor: t.colors.background,
      appBar: AppBar(
        backgroundColor: t.colors.surface,
        leading: VkIconButton(
          icon: t.icons.resolve('back'),
          semanticLabel: s.text('playerBack'),
          onPressed: () => Navigator.of(context).maybePop(),
        ),
        title: Text(g(g.l.navFeatures), style: t.typography.title),
      ),
      body: ListView(
        padding: EdgeInsetsDirectional.all(d.spacing16),
        children: [
          Text(
            g(g.l.featureIntro),
            style: t.typography.bodySmall.copyWith(
              color: t.colors.textSecondary,
            ),
          ),
          SizedBox(height: d.spacing12),
          for (final f in VideoKitFeature.configurable)
            Padding(
              padding: EdgeInsetsDirectional.only(bottom: d.spacing12),
              child: Container(
                padding: EdgeInsetsDirectional.all(d.spacing12),
                decoration: BoxDecoration(
                  color: t.colors.surface,
                  borderRadius: BorderRadius.circular(d.cornerLarge),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            featureName(g, f),
                            style: t.typography.body.copyWith(
                              color: t.colors.textPrimary,
                            ),
                          ),
                        ),
                        if (f.requires != null && !enabled.isEnabled(f))
                          Text(
                            g(g.l.featureHiddenByEdit),
                            style: t.typography.caption.copyWith(
                              color: t.colors.textSecondary,
                            ),
                          ),
                        SizedBox(width: d.spacing8),
                        VkSwitch(
                          value: !hidden.contains(f),
                          semanticLabel: featureName(g, f),
                          onChanged: (on) => setState(
                            () => on ? hidden.remove(f) : hidden.add(f),
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: d.spacing8),
                    VkSegmented<GateAnswer>(
                      segments: [
                        VkSegment(
                          value: GateAnswer.allow,
                          label: g(g.l.gateAllow),
                        ),
                        VkSegment(
                          value: GateAnswer.trial,
                          label: g(g.l.gateTrial),
                        ),
                        VkSegment(
                          value: GateAnswer.deny,
                          label: g(g.l.gateDeny),
                        ),
                      ],
                      selected: answers[f] ?? GateAnswer.allow,
                      semanticLabel: g(g.l.gateAnswer(featureName(g, f))),
                      onChanged: gateOn
                          ? (a) => setState(() => answers[f] = a)
                          : null,
                    ),
                  ],
                ),
              ),
            ),
          Row(
            children: [
              Expanded(
                child: Text(
                  g(g.l.gateOn),
                  style: t.typography.body.copyWith(
                    color: t.colors.textPrimary,
                  ),
                ),
              ),
              VkSwitch(
                value: gateOn,
                semanticLabel: g(g.l.gateOn),
                onChanged: (v) => setState(() => gateOn = v),
              ),
            ],
          ),
          SizedBox(height: d.spacing16),
          Wrap(
            spacing: d.spacing8,
            runSpacing: d.spacing8,
            children: [
              VkButton(label: g(g.l.featureOpenEditor), onPressed: openEditor),
              if (enabled.isEnabled(VideoKitFeature.multiView))
                VkButton(
                  label: g(g.l.featureOpenMultiView),
                  variant: VkButtonVariant.secondary,
                  onPressed: () => unawaited(openMultiView()),
                ),
              VkButton(
                label: g(g.l.featureCallApi),
                variant: VkButtonVariant.secondary,
                onPressed: () => unawaited(callApi()),
              ),
            ],
          ),
          if (apiResult != null) ...[
            SizedBox(height: d.spacing12),
            Semantics(
              liveRegion: true,
              child: Text(
                apiResult!,
                style: t.typography.timecode.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
