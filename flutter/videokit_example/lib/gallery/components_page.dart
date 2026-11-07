import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../demo/demo_host.dart';
import 'gallery_page.dart';
import 'gallery_text.dart';

/// Component library (design page 6): common components, UI-09 state
/// views, UI-04 host action bar, UI-02 track settings sheet and the sheet
/// host with toasts. Every sample uses VideoKit tokens and ARB text.
class ComponentsPage extends StatefulWidget {
  /// Creates the page.
  const ComponentsPage({super.key});

  @override
  State<ComponentsPage> createState() => _ComponentsPageState();
}

class _ComponentsPageState extends State<ComponentsPage> {
  final VkSheetController _sheets = VkSheetController();
  final FakeVideoKit _kit = FakeVideoKit();
  VideoKitSession? _session;
  double _volume = 0.6;
  int _positionUs = 42000000;
  bool _favorited = false;

  @override
  void initState() {
    super.initState();
    _bind();
  }

  Future<void> _bind() async {
    final s = await _kit.createSession(const VideoKitSessionConfig());
    if (!mounted) {
      await s.close();
      return;
    }
    // Bind completes once the Fake clock has run the open delay.
    final bound = s.bind(
      const VideoKitMediaSource(
        mediaToken: 'components',
        mediaKind: MediaKind.video,
        sourceRef: DemoSourceRef('normal'),
      ),
    );
    await _kit.clock.advance(const Duration(seconds: 1));
    await bound;
    if (mounted) setState(() => _session = s);
  }

  @override
  void dispose() {
    _session?.close();
    _kit.close();
    _sheets.dispose();
    super.dispose();
  }

  void _openTracks(VideoKitSession s, GalleryText g) => _sheets.show(
    VkSheetEntry(
      id: 'tracks',
      title: VkStrings.of(context).text('settingsTitle'),
      builder: (_) => TrackSettingsSheet(session: s, onCommand: s.execute),
    ),
  );

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    Widget wrap(List<Widget> children) => Wrap(
      spacing: d.spacing12,
      runSpacing: d.spacing12,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: children,
    );
    Widget stateBox(StateViewModel model) => SizedBox(
      width: d.spacing32 * 10,
      child: AspectRatio(
        aspectRatio: 16 / 9,
        child: ClipRRect(
          borderRadius: BorderRadius.circular(d.cornerMedium),
          child: ColoredBox(
            color: t.colors.playerCanvas,
            child: VideoKitStateView(model: model, onStateAction: (_) {}),
          ),
        ),
      ),
    );
    final session = _session;
    return Scaffold(
      backgroundColor: t.colors.background,
      appBar: AppBar(
        title: Text(g(g.l.componentsTitle), style: t.typography.title),
        backgroundColor: t.colors.surface,
      ),
      body: VkSheetHost(
        controller: _sheets,
        child: Stack(
          children: [
            ListView(
              padding: EdgeInsetsDirectional.fromSTEB(
                d.spacing16,
                d.spacing16,
                d.spacing16,
                d.spacing32 * 2,
              ),
              children: [
                GallerySection(
                  title: g(g.l.sectionButtons),
                  child: wrap([
                    VkButton(
                      label: g(g.l.componentButtonPrimary),
                      onPressed: () {},
                    ),
                    VkButton(
                      label: g(g.l.componentButtonSecondary),
                      variant: VkButtonVariant.secondary,
                      onPressed: () {},
                    ),
                    VkButton(
                      label: g(g.l.componentButtonText),
                      variant: VkButtonVariant.text,
                      onPressed: () {},
                    ),
                    VkButton(
                      label: g(g.l.componentChip),
                      variant: VkButtonVariant.secondary,
                      selected: true,
                      onPressed: () {},
                    ),
                    VkButton(label: g(g.l.stateDisabled), onPressed: null),
                  ]),
                ),
                GallerySection(
                  title: g(g.l.sectionIconButtons),
                  child: wrap([
                    VkIconButton(
                      icon: t.icons.resolve('play'),
                      semanticLabel: s.text('playerPlay'),
                      onPressed: () {},
                    ),
                    VkIconButton(
                      icon: t.icons.resolve(
                        _favorited ? 'favorite' : 'favoriteborder',
                      ),
                      semanticLabel: g(
                        _favorited ? g.l.hostUnfavoriteCd : g.l.hostFavoriteCd,
                      ),
                      selected: _favorited,
                      onPressed: () => setState(() => _favorited = !_favorited),
                    ),
                    VkIconButton(
                      icon: t.icons.resolve('tag'),
                      semanticLabel: g(g.l.hostTagCd),
                      pending: true,
                      onPressed: () {},
                    ),
                    VkIconButton(
                      icon: t.icons.resolve('share'),
                      semanticLabel: g(g.l.hostShareCd),
                      badgeText: g(g.l.badgeLongSample),
                      onPressed: () {},
                    ),
                    VkIconButton(
                      icon: t.icons.resolve('delete'),
                      semanticLabel: g(g.l.hostDeleteCd),
                      onPressed: null,
                    ),
                  ]),
                ),
                GallerySection(
                  title: g(g.l.sectionBadges),
                  child: wrap([
                    VkBadge(text: g(g.l.badgeSample)),
                    VkBadge(text: VkBadge.clip(s, g(g.l.badgeLongSample))),
                    const DemoBadge(),
                  ]),
                ),
                GallerySection(
                  title: g(g.l.sectionSlider),
                  child: VkSlider(
                    value: _volume,
                    semanticLabel: g(g.l.volumeLabel),
                    semanticValue: (v) => VkFormat.percent(s, v),
                    onChanged: (v) => setState(() => _volume = v),
                  ),
                ),
                GallerySection(
                  title: g(g.l.componentSeekBar),
                  child: VkSeekBar(
                    positionUs: _positionUs,
                    durationUs: 300000000,
                    bufferedUs: 120000000,
                    onDragEnd: (us) => setState(() => _positionUs = us),
                  ),
                ),
                GallerySection(
                  title: g(g.l.sectionHostActions),
                  child: HostActionBar(
                    actions: [
                      for (final a in DemoHostActions.initial(
                        favorited: _favorited,
                      ))
                        HostActionState(
                          action: a,
                          pending: a.actionId == DemoHostActions.tag,
                        ),
                    ],
                    resolveString: (k) => DemoHostActions.resolve(context, k),
                    onActionPressed: (id) {
                      if (id == DemoHostActions.favorite) {
                        setState(() => _favorited = !_favorited);
                      }
                      _sheets.showToast(VkToastEntry(message: g(g.l.hostDone)));
                    },
                  ),
                ),
                GallerySection(
                  title: g(g.l.sectionSheets),
                  child: wrap([
                    VkButton(
                      label: g(g.l.openSheet),
                      variant: VkButtonVariant.secondary,
                      onPressed: () => _sheets.show(
                        VkSheetEntry(
                          id: 'sample',
                          title: g(g.l.sheetSampleTitle),
                          builder: (context) => Text(
                            g(g.l.sheetSampleBody),
                            style: VkTheme.of(context).typography.body,
                          ),
                        ),
                      ),
                    ),
                    VkButton(
                      label: g(g.l.showToast),
                      variant: VkButtonVariant.secondary,
                      onPressed: () => _sheets.showToast(
                        VkToastEntry(message: g(g.l.toastSample)),
                      ),
                    ),
                    VkButton(
                      label: s.text('settingsTitle'),
                      variant: VkButtonVariant.secondary,
                      onPressed: session == null
                          ? null
                          : () => _openTracks(session, g),
                    ),
                  ]),
                ),
                GallerySection(
                  title: g(g.l.sectionStateViews),
                  child: wrap([
                    stateBox(mapSessionState(phase: SessionPhase.binding)!),
                    stateBox(mapSessionState(phase: SessionPhase.buffering)!),
                    stateBox(
                      mapError(
                        const VideoKitStableError(
                          code: ErrorCode.sourceDisconnected,
                          stage: ErrorStage.playback,
                          retryable: true,
                          suggestedAction: SuggestedAction.reconnectSource,
                        ),
                      ),
                    ),
                    stateBox(
                      mapError(
                        const VideoKitStableError(
                          code: ErrorCode.unsupportedVideoCodec,
                          stage: ErrorStage.probe,
                          suggestedAction: SuggestedAction.chooseOtherSource,
                        ),
                        fatal: true,
                      ),
                    ),
                    stateBox(
                      mapError(
                        const VideoKitStableError(
                          code: ErrorCode.outputSpaceInsufficient,
                          stage: ErrorStage.sink,
                          suggestedAction: SuggestedAction.freeSpace,
                        ),
                      ),
                    ),
                    stateBox(mapSessionState(phase: SessionPhase.ended)!),
                    stateBox(
                      mapSessionState(
                        phase: SessionPhase.playing,
                        hiddenForLock: true,
                      )!,
                    ),
                    stateBox(mapSessionState(phase: SessionPhase.released)!),
                  ]),
                ),
              ],
            ),
            const PositionedDirectional(
              top: 0,
              end: 0,
              child: SafeArea(child: GalleryDemoBadge()),
            ),
          ],
        ),
      ),
    );
  }
}
