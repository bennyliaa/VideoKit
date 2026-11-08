import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../demo/demo_host.dart';
import '../gallery/gallery_text.dart';

/// Fake scenarios offered by the player demo (M0-B2 dispatch item 4).
enum PlayerDemoScenario {
  /// Normal playback.
  normal('normal'),

  /// Opening takes 3 s.
  slowLoad('slowLoad'),

  /// Buffering during playback.
  buffering('buffering'),

  /// Source disconnects at 30 s.
  disconnect('disconnect'),

  /// Video codec unsupported.
  unsupported('unsupported'),

  /// The "删除" host action never answers (10 s timeout).
  hostActionTimeout('hostActionTimeout'),

  /// A network source (04A P6): bound with `SourceLatency.slow`, so seek
  /// drags show only the time bubble.
  slowSource('slowSource');

  const PlayerDemoScenario(this.id);

  /// Scenario ID in `Scenarios.catalog`.
  final String id;

  /// Latency hint the demo binds with.
  SourceLatency get latency =>
      this == slowSource ? SourceLatency.slow : SourceLatency.local;

  /// ARB label.
  String label(GalleryText g) => g(switch (this) {
    normal => g.l.scenarioNormal,
    slowLoad => g.l.scenarioSlowLoad,
    buffering => g.l.scenarioBuffering,
    disconnect => g.l.scenarioDisconnect,
    unsupported => g.l.scenarioUnsupported,
    hostActionTimeout => g.l.scenarioHostActionTimeout,
    slowSource => g.l.scenarioSlowSource,
  });
}

/// UI-01 `VideoKitPlayer` driven by the Dart Fake: pick a scenario, the
/// page creates a Fake session for it and binds a demo source with the
/// demo host actions. Time follows real frames (Fake clock ticker).
class PlayerDemoPage extends StatefulWidget {
  /// Creates the page.
  const PlayerDemoPage({
    super.key,
    this.initialScenario = PlayerDemoScenario.normal,
  });

  /// Scenario bound first.
  final PlayerDemoScenario initialScenario;

  @override
  State<PlayerDemoPage> createState() => PlayerDemoPageState();
}

/// State of [PlayerDemoPage] (public for tests: [session], [kit]).
class PlayerDemoPageState extends State<PlayerDemoPage>
    with SingleTickerProviderStateMixin {
  final DemoHostCallbacks _callbacks = DemoHostCallbacks();
  late final FakeVideoKit kit = FakeVideoKit(
    config: VideoKitConfig(hostCallbacks: _callbacks),
  );
  late PlayerDemoScenario _scenario = widget.initialScenario;

  /// Current session (null while switching).
  VideoKitSession? session;
  int _generation = 0;
  bool _fullscreen = false;
  VideoKitMediaSource? _source;

  @override
  void initState() {
    super.initState();
    _callbacks.clock = kit.clock;
    kit.clock.attachTicker(this);
    _open(_scenario);
  }

  Future<void> _open(PlayerDemoScenario scenario) async {
    final generation = ++_generation;
    final old = session;
    setState(() {
      _scenario = scenario;
      session = null;
    });
    if (old != null) await old.close();
    final s = await kit.createSession(
      const VideoKitSessionConfig(debugLabel: 'example'),
    );
    if (!mounted || generation != _generation) {
      await s.close();
      return;
    }
    final source = VideoKitMediaSource(
      mediaToken: 'example-${scenario.id}-$generation',
      mediaKind: MediaKind.video,
      sourceRef: DemoSourceRef(scenario.id),
      latencyHint: scenario.latency,
      mimeType: 'video/mp4',
    );
    setState(() {
      session = s;
      _source = source;
    });
    await s.bind(source, hostActions: DemoHostActions.initial());
  }

  /// "重试" / "重新连接" (R1-09): re-binds the same session to the same
  /// source from where it stopped; a session that cannot be re-bound (fatal,
  /// released) is replaced by a new one.
  Future<void> retry() async {
    final s = session;
    final source = _source;
    if (s == null ||
        source == null ||
        s.state.value.phase != SessionPhase.errorRecoverable) {
      return _open(_scenario);
    }
    VideoKitPlaybackState? resume;
    try {
      resume = await s.captureState();
    } on Object {
      resume = null;
    }
    if (!mounted || !identical(s, session)) return;
    final r = await s.bind(
      source,
      initialState: resume,
      hostActions: DemoHostActions.initial(),
    );
    if ((r is Rejected || r is SessionReleased) &&
        mounted &&
        identical(s, session)) {
      await _open(_scenario);
    }
  }

  void _onStateAction(StateAction action) {
    switch (action) {
      case StateAction.retry || StateAction.reconnectSource:
        unawaited(retry());
      case StateAction.showCapabilities:
        // J4: read-only capability page.
        unawaited(
          Navigator.of(context).push(
            MaterialPageRoute<void>(
              builder: (_) => VideoKitCapabilitiesPage(
                capabilities: kit.capabilities(const CapabilityRequest()),
              ),
            ),
          ),
        );
      default:
        break;
    }
  }

  @override
  void dispose() {
    _generation++;
    session?.close();
    kit.clock.detachTicker();
    kit.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final d = t.dimensions;
    final s = session;
    final player = s == null
        ? ColoredBox(
            color: t.colors.playerCanvas,
            child: VideoKitStateView(
              model: mapSessionState(phase: SessionPhase.created)!,
            ),
          )
        : VideoKitPlayer(
            key: ObjectKey(s),
            session: s,
            title: g(g.l.playerDemoVideoTitle),
            subtitle: _scenario.label(g),
            latencyHint: _scenario.latency,
            pictureBuilder: (context, session) =>
                DemoSessionPicture(session: session),
            resolveHostString: (k) => DemoHostActions.resolve(context, k),
            onStateAction: _onStateAction,
            onFullscreenRequested: (v) => setState(() => _fullscreen = v),
            onEditRequested: (_) => ScaffoldMessenger.of(context)
              ..hideCurrentSnackBar()
              ..showSnackBar(SnackBar(content: Text(g(g.l.editNotAvailable)))),
            onBack: _fullscreen
                ? () => setState(() => _fullscreen = false)
                : () => Navigator.of(context).maybePop(),
            hostPanel: (context, visible) => _HostPanel(visible: visible),
          );
    return Scaffold(
      backgroundColor: t.colors.background,
      appBar: _fullscreen
          ? null
          : AppBar(
              title: Text(g(g.l.playerDemoTitle), style: t.typography.title),
              backgroundColor: t.colors.surface,
            ),
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, c) {
            final wide = c.maxWidth > c.maxHeight;
            if (_fullscreen || wide) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (!_fullscreen) _ScenarioPicker(_scenario, _open),
                  Expanded(child: player),
                ],
              );
            }
            return ListView(
              children: [
                AspectRatio(aspectRatio: 9 / 12, child: player),
                Padding(
                  padding: EdgeInsetsDirectional.all(d.spacing8),
                  child: _ScenarioPicker(_scenario, _open),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _ScenarioPicker extends StatelessWidget {
  const _ScenarioPicker(this.selected, this.onSelected);

  final PlayerDemoScenario selected;
  final ValueChanged<PlayerDemoScenario> onSelected;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final d = t.dimensions;
    return Padding(
      padding: EdgeInsetsDirectional.symmetric(
        horizontal: d.spacing8,
        vertical: d.spacing4,
      ),
      child: Wrap(
        spacing: d.spacing8,
        runSpacing: d.spacing8,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          Semantics(
            header: true,
            child: Text(g(g.l.scenarioLabel), style: t.typography.label),
          ),
          for (final s in PlayerDemoScenario.values)
            VkButton(
              label: s.label(g),
              variant: VkButtonVariant.secondary,
              selected: s == selected,
              onPressed: () => onSelected(s),
            ),
        ],
      ),
    );
  }
}

/// Host panel slot sample (03 §6): shown and hidden with the controls.
/// Host panel slot example (design page 10, R1-05): "邻近媒体", other
/// videos of the same folder as thumbnail cards in a column at the side
/// (landscape; portrait leaves the space to the host actions). Shows and
/// hides with the controls (the player passes [visible]).
class _HostPanel extends StatelessWidget {
  const _HostPanel({required this.visible});

  final bool visible;

  static const List<(int, int)> _items = [
    (11, 186000000),
    (23, 512000000),
    (37, 95000000),
  ];

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    if (!visible) return const SizedBox.shrink();
    final names = [
      g(g.l.demoVideoSea),
      g(g.l.demoVideoValley),
      g(g.l.demoVideoCity),
    ];
    Widget card(int i) {
      final (seed, duration) = _items[i];
      final width = d.targetMin * 3;
      return Semantics(
        button: true,
        label: g(
          g.l.hostPanelItem(names[i], VkFormat.durationSpoken(s, duration)),
        ),
        child: GestureDetector(
          excludeFromSemantics: true,
          onTap: () => ScaffoldMessenger.of(context)
            ..hideCurrentSnackBar()
            ..showSnackBar(
              SnackBar(content: Text(g(g.l.hostHandled(names[i])))),
            ),
          child: ExcludeSemantics(
            child: SizedBox(
              width: width,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(d.cornerSmall),
                    child: SizedBox(
                      width: width,
                      height: width * 9 / 16,
                      child: Stack(
                        fit: StackFit.expand,
                        children: [
                          DemoPicture(
                            seed: seed,
                            positionUs: duration ~/ 3,
                            durationUs: duration,
                          ),
                          PositionedDirectional(
                            end: d.spacing4,
                            bottom: d.spacing4,
                            child: DecoratedBox(
                              decoration: BoxDecoration(
                                color: t.colors.playerCanvas,
                                borderRadius: BorderRadius.circular(
                                  d.cornerSmall,
                                ),
                              ),
                              child: Padding(
                                padding: EdgeInsetsDirectional.symmetric(
                                  horizontal: d.spacing4,
                                ),
                                child: Text(
                                  VkFormat.timecode(duration),
                                  style: t.typography.caption.copyWith(
                                    color: t.colors.playerControlsContent,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: d.spacing4),
                  Text(
                    names[i],
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: t.typography.caption.copyWith(
                      color: t.colors.playerControlsContent,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    }

    final title = Semantics(
      header: true,
      child: Text(
        g(g.l.hostPanelHint),
        style: t.typography.label.copyWith(
          color: t.colors.playerControlsContent,
        ),
      ),
    );
    return LayoutBuilder(
      builder: (context, c) {
        // Portrait: no room beside the host action column; the design shows
        // the panel in landscape only.
        if (!c.maxHeight.isFinite) return const SizedBox.shrink();
        final list = ListView.separated(
          shrinkWrap: true,
          itemCount: _items.length,
          separatorBuilder: (_, _) => SizedBox(height: d.spacing8),
          itemBuilder: (_, i) => card(i),
        );
        return Container(
          width: d.targetMin * 3 + d.spacing8 * 2,
          padding: EdgeInsetsDirectional.all(d.spacing8),
          decoration: BoxDecoration(
            color: t.colors.scrim,
            borderRadius: BorderRadius.circular(d.cornerMedium),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: EdgeInsetsDirectional.symmetric(
                  horizontal: d.spacing8,
                ),
                child: title,
              ),
              SizedBox(height: d.spacing8),
              Flexible(child: list),
            ],
          ),
        );
      },
    );
  }
}
