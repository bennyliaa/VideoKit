import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../gallery/gallery_text.dart';

/// Fake project scenarios of the edit demo.
enum EditDemoScenario {
  /// Everything works.
  normal('normal'),

  /// Tracking loses the target at 4–6 s.
  trackingLost('trackingLost'),

  /// Export fails while encoding (output space).
  exportFails('exportFails'),

  /// Cancelling an export takes 2 s.
  cancelSlow('exportCancelSlow'),

  /// The engine refuses fast concatenation (M4): the export transcodes.
  fastConcatRejected('fastConcatRejected'),

  /// The export looks done, then fails (M6-A1, 15 §2.8 constraint 4).
  failsAfterDone('exportFailsAfterDone'),

  /// The export worker is killed (M6-A1, 04A X1-3).
  workerKilled('exportWorkerKilled'),

  /// Cleaning up after a cancel takes 7 s (M6-A1, 04A X1-2).
  cleanupSlow('exportCleanupSlow');

  const EditDemoScenario(this.id);

  /// Scenario ID.
  final String id;

  /// ARB label.
  String label(GalleryText g) => g(switch (this) {
    normal => g.l.editScenarioNormal,
    trackingLost => g.l.editScenarioTrackingLost,
    exportFails => g.l.editScenarioExportFails,
    cancelSlow => g.l.editScenarioCancelSlow,
    fastConcatRejected => g.l.editScenarioFastConcatRejected,
    failsAfterDone => g.l.editScenarioFailsAfterDone,
    workerKilled => g.l.editScenarioWorkerKilled,
    cleanupSlow => g.l.editScenarioCleanupSlow,
  });
}

/// UI-06/07/08 driven by the Dart Fake: three demo videos are added as
/// clips; the page plays the host (source picker, output sink, export
/// actions). Flow: add clips → edit → mask → track → correct → export →
/// cancel / fail / succeed, depending on the scenario.
class EditDemoPage extends StatefulWidget {
  /// Creates the page.
  const EditDemoPage({
    super.key,
    this.initialScenario = EditDemoScenario.normal,
    this.showScenarioPicker = true,
    this.features = VideoKitFeatureConfig.allEnabled,
    this.hostCallbacks,
  });

  /// Static feature switches of the demo's Fake (REQ-API-10, the "功能开关"
  /// panel).
  final VideoKitFeatureConfig features;

  /// Host callbacks with a feature gate; null = no gate (allow all).
  final VideoKitHostCallbacks? hostCallbacks;

  /// First scenario.
  final EditDemoScenario initialScenario;

  /// Show the scenario row.
  final bool showScenarioPicker;

  /// Free space the demo sink reports.
  static const int demoFreeBytes = 12400000000;

  @override
  State<EditDemoPage> createState() => EditDemoPageState();
}

/// State (public for tests).
class EditDemoPageState extends State<EditDemoPage>
    with SingleTickerProviderStateMixin {
  late final FakeVideoKit kit = FakeVideoKit(
    config: VideoKitConfig(
      hostCallbacks: widget.hostCallbacks ?? const NoopHostCallbacks(),
      features: widget.features,
    ),
  );

  /// Feature state of the editor below (switches + the host's gate).
  late final VideoKitFeatures features = VideoKitFeatures(kit.features);

  /// Opening failed (e.g. `FEATURE_DISABLED` when EDIT is hidden).
  VideoKitStableError? openError;

  /// Current project.
  VideoKitEditProject? project;

  late EditDemoScenario _scenario = widget.initialScenario;
  int _generation = 0;
  int _more = 0;

  /// Output sink of the demo host.
  static const VideoKitOutputSink sink = VideoKitOutputSink(
    sinkRef: 'demo:example',
    capabilities: SinkCapabilities(
      fileDescriptor: true,
      knownFreeSpaceBytes: EditDemoPage.demoFreeBytes,
    ),
  );

  @override
  void initState() {
    super.initState();
    kit.clock.attachTicker(this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) unawaited(open(_scenario));
    });
  }

  /// Creates a project for [scenario] with three demo clips.
  Future<void> open(EditDemoScenario scenario) async {
    final gen = ++_generation;
    final old = project;
    setState(() {
      _scenario = scenario;
      project = null;
    });
    if (old != null) await old.close();
    kit.defaultScenario = Scenarios.byId(scenario.id);
    final VideoKitEditProject p;
    try {
      p = await kit.createEditProject(EditProjectConfig());
    } on VideoKitException catch (e) {
      // REQ-API-10: EDIT hidden or denied — shown as a state view.
      if (mounted && gen == _generation) setState(() => openError = e.error);
      return;
    }
    if (!mounted || gen != _generation) {
      await p.close();
      return;
    }
    final g = GalleryText.of(context);
    for (final (i, name) in [
      g(g.l.demoVideoSea),
      g(g.l.demoVideoValley),
      g(g.l.demoVideoCity),
    ].indexed) {
      await _addSource(p, 'edit-$gen-$i', name);
    }
    if (mounted && gen == _generation) setState(() => project = p);
  }

  Future<void> _addSource(
    VideoKitEditProject p,
    String token,
    String name,
  ) async {
    final src = await p.addSource(
      VideoKitMediaSource(
        mediaToken: token,
        mediaKind: MediaKind.video,
        displayName: name,
        sourceRef: const DemoSourceRef('normal'),
      ),
    );
    final probe = p.state.value.timeline.sourceById(src.sourceId)?.probe;
    // Demo clips use the first 20 s of every source (none while unprobed).
    if (probe == null || probe.durationUs <= 0) return;
    await p.apply(
      AddClip(
        src.sourceId,
        0,
        probe.durationUs < 20000000 ? probe.durationUs : 20000000,
      ),
    );
  }

  /// Host source picker: adds one more demo video.
  Future<void> addMore() async {
    final p = project;
    if (p == null) return;
    final g = GalleryText.of(context);
    _more++;
    await _addSource(p, 'edit-more-$_more', g(g.l.demoVideoMore(_more)));
  }

  @override
  void dispose() {
    _generation++;
    unawaited(project?.close());
    kit.clock.detachTicker();
    unawaited(kit.close());
    features.dispose();
    super.dispose();
  }

  void _hostAction(String action) {
    final g = GalleryText.of(context);
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(g(g.l.hostHandled(action)))));
  }

  /// Demo host for "更换头像": a sheet of the Kit's built-in avatars.
  Future<MaskAvatar?> _pickBuiltinAvatar(AvatarRequest request) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final d = t.dimensions;
    return showModalBottomSheet<MaskAvatar>(
      context: context,
      backgroundColor: t.colors.surface,
      builder: (context) => SafeArea(
        child: Padding(
          padding: EdgeInsetsDirectional.all(d.spacing16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                g(g.l.demoAvatarSheetTitle),
                style: t.typography.title.copyWith(
                  color: t.colors.textPrimary,
                ),
              ),
              SizedBox(height: d.spacing12),
              Wrap(
                spacing: d.spacing12,
                runSpacing: d.spacing12,
                children: [
                  for (var n = 1; n <= FakeAvatarTools.builtinCount; n++)
                    Semantics(
                      button: true,
                      selected:
                          request.currentToken ==
                          '${MaskAvatar.builtinPrefix}$n',
                      label: g(g.l.demoAvatarBuiltin(n)),
                      excludeSemantics: true,
                      child: InkWell(
                        onTap: () => Navigator.of(context).pop(
                          MaskAvatar(
                            avatarToken: '${MaskAvatar.builtinPrefix}$n',
                          ),
                        ),
                        child: SizedBox.square(
                          dimension: d.targetMin * 1.25,
                          child: Image.memory(FakeAvatarTools.builtinPng(n)),
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final d = t.dimensions;
    final p = project;
    return Scaffold(
      backgroundColor: t.colors.background,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (widget.showScenarioPicker)
            SafeArea(
              bottom: false,
              child: Padding(
                padding: EdgeInsetsDirectional.symmetric(
                  horizontal: d.spacing16,
                  vertical: d.spacing4,
                ),
                child: Wrap(
                  spacing: d.spacing8,
                  runSpacing: d.spacing8,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    Text(g(g.l.editScenario), style: t.typography.label),
                    for (final s in EditDemoScenario.values)
                      VkButton(
                        label: s.label(g),
                        variant: VkButtonVariant.secondary,
                        selected: s == _scenario,
                        onPressed: () => unawaited(open(s)),
                      ),
                  ],
                ),
              ),
            ),
          Expanded(
            child: openError != null
                ? VideoKitStateView(model: mapError(openError!, fatal: true))
                : p == null
                ? Center(
                    child: CircularProgressIndicator(
                      color: t.components.progress.indicator,
                    ),
                  )
                : VideoKitFeatureScope(
                    features: features,
                    child: VideoKitEditor(
                    key: ObjectKey(p),
                    project: p,
                    sink: sink,
                    title: g(g.l.editProjectTitle),
                    // Design page 15: autosave; the demo takes a snapshot.
                    onAutosave: p.snapshot,
                    presets: FakeVideoKit.demoCapabilities().outputFormats,
                    pictureBuilder: (context, session) =>
                        DemoSessionPicture(session: session),
                    onBack: () => Navigator.of(context).maybePop(),
                    onPickSourcesRequested: () => unawaited(addMore()),
                    // REQ-ED-07 extension point (04A E6 5): this demo host
                    // only offers the Kit's built-in avatars; the App has
                    // the full choose / adjust pages.
                    onRequestAvatar: (request) => _pickBuiltinAvatar(request),
                    avatarBuilder: (context, token) =>
                        switch (FakeAvatarTools.builtinFor(token)) {
                          null => const SizedBox.shrink(),
                          final png => Image.memory(
                            png,
                            fit: BoxFit.contain,
                            gaplessPlayback: true,
                          ),
                        },
                    exportSuccessActions: (context, media) => Wrap(
                      spacing: d.spacing12,
                      children: [
                        // Design page 21: "完成" is the one main button;
                        // the host's own actions stay secondary.
                        VkButton(
                          label: g(g.l.exportOpen),
                          variant: VkButtonVariant.secondary,
                          onPressed: () => _hostAction(g(g.l.exportOpen)),
                        ),
                        VkButton(
                          label: g(g.l.exportShare),
                          variant: VkButtonVariant.secondary,
                          onPressed: () => _hostAction(g(g.l.exportShare)),
                        ),
                      ],
                    ),
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}
