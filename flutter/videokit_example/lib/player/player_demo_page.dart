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
  hostActionTimeout('hostActionTimeout');

  const PlayerDemoScenario(this.id);

  /// Scenario ID in `Scenarios.catalog`.
  final String id;

  /// ARB label.
  String label(GalleryText g) => g(switch (this) {
    normal => g.l.scenarioNormal,
    slowLoad => g.l.scenarioSlowLoad,
    buffering => g.l.scenarioBuffering,
    disconnect => g.l.scenarioDisconnect,
    unsupported => g.l.scenarioUnsupported,
    hostActionTimeout => g.l.scenarioHostActionTimeout,
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
    setState(() => session = s);
    await s.bind(
      VideoKitMediaSource(
        mediaToken: 'example-${scenario.id}-$generation',
        mediaKind: MediaKind.video,
        sourceRef: DemoSourceRef(scenario.id),
        mimeType: 'video/mp4',
      ),
      hostActions: DemoHostActions.initial(),
    );
  }

  void _onStateAction(StateAction action) {
    switch (action) {
      case StateAction.retry || StateAction.reconnectSource:
        _open(_scenario);
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
class _HostPanel extends StatelessWidget {
  const _HostPanel({required this.visible});

  final bool visible;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final d = t.dimensions;
    if (!visible) return const SizedBox.shrink();
    return Align(
      alignment: AlignmentDirectional.bottomStart,
      child: Padding(
        padding: EdgeInsetsDirectional.all(d.spacing8),
        child: DecoratedBox(
          decoration: BoxDecoration(
            color: t.colors.surface,
            borderRadius: BorderRadius.circular(d.cornerSmall),
          ),
          child: Padding(
            padding: EdgeInsetsDirectional.symmetric(
              horizontal: d.spacing8,
              vertical: d.spacing4,
            ),
            child: Text(g(g.l.hostPanelHint), style: t.typography.label),
          ),
        ),
      ),
    );
  }
}
