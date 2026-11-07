import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_buttons.dart';
import '../common/vk_sheet_host.dart';
import '../export/export_panel.dart';
import '../foundation/format.dart';
import '../foundation/layout_class.dart';
import '../l10n/vk_strings.dart';
import '../mask/coverage_check_sheet.dart';
import '../mask/mask_editor.dart';
import '../player/media_surface.dart';
import '../player/picture_style.dart';
import '../theme/theme_scope.dart';
import 'editor_controller.dart';
import 'editor_panels.dart';
import 'timeline_view.dart';

/// UI-06 editor (14 §5.6, design pages 15–16).
///
/// ```text
/// expanded:  [preview + transport]  [properties]
///            [toolbar · estimate                ]
///            [timeline (full width)             ]
/// compact:   [preview] [timeline] [selected clip card] [bottom navigation]
/// ```
///
/// Masks (UI-07) and export (UI-08) are modes of the same controller.
/// The project is the only authority: every edit is one command, undo and
/// redo read `canUndo`/`canRedo` (Ctrl+Z / Ctrl+Shift+Z).
class VideoKitEditor extends StatefulWidget {
  /// Creates an editor.
  const VideoKitEditor({
    super.key,
    required this.project,
    required this.sink,
    this.title,
    this.onBack,
    this.onPickSourcesRequested,
    this.pictureBuilder,
    this.presets = const [],
    this.fastConcatCapable = true,
    this.exportSuccessActions,
  });

  /// Project (owned by the host).
  final VideoKitEditProject project;

  /// Output sink for export (host provided).
  final VideoKitOutputSink sink;

  /// Project title.
  final String? title;

  /// Back / close.
  final VoidCallback? onBack;

  /// "添加视频": the host picks files and calls `project.addSource`.
  final VoidCallback? onPickSourcesRequested;

  /// Picture without texture (Dart Fake).
  final VideoKitPictureBuilder? pictureBuilder;

  /// Export presets (capability `outputFormats`).
  final List<OutputFormat> presets;

  /// Device fast-concat capability (`EditCapability.fastConcat`).
  final bool fastConcatCapable;

  /// Host actions for a finished export.
  final Widget Function(BuildContext context, VideoKitExportedMedia media)?
  exportSuccessActions;

  @override
  State<VideoKitEditor> createState() => VideoKitEditorState();
}

/// State of [VideoKitEditor]; host and test handle via `GlobalKey`.
class VideoKitEditorState extends State<VideoKitEditor> {
  late EditorController _c = _create();
  MaskEditorTab _maskTab = MaskEditorTab.manual;
  final GlobalKey<MaskEditorState> _maskKey = GlobalKey();
  final GlobalKey<ExportPanelState> _exportKey = GlobalKey();

  /// Controller (tests and hosts).
  EditorController get controller => _c;

  /// Mask editor state when in mask mode.
  MaskEditorState? get maskEditor => _maskKey.currentState;

  /// Export panel state when in export mode.
  ExportPanelState? get exportPanel => _exportKey.currentState;

  EditorController _create() => EditorController(
    project: widget.project,
    strings: () => VkStrings.of(context),
  );

  @override
  void didUpdateWidget(VideoKitEditor oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!identical(oldWidget.project, widget.project)) {
      _c.dispose();
      _c = _create();
    }
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  /// Opens the mask editor on [tab].
  void openMasks(MaskEditorTab tab) {
    setState(() => _maskTab = tab);
    _c.mode = EditorMode.mask;
  }

  /// Opens the export panel.
  void openExport() => _c.mode = EditorMode.export;

  void _openOrder() {
    final s = VkStrings.of(context);
    _c.sheets.show(
      VkSheetEntry(
        id: 'order',
        title: s.text('sourcesTitle'),
        builder: (context) => ClipOrderSheet(
          controller: _c,
          onAddSources: widget.onPickSourcesRequested,
          fastConcatCapable: widget.fastConcatCapable,
        ),
      ),
    );
  }

  String _targetName(VkStrings s, String maskId) {
    final auto = [
      for (final m in _c.state.masks)
        if (m.type.isAutomatic) m.maskId,
    ];
    final i = auto.indexOf(maskId);
    return i < 0 ? maskId : s.trackTarget(vkTargetLetter(i));
  }

  void _reviewCoverage(List<UncoveredRange> ranges) {
    final s = VkStrings.of(context);
    _c.sheets.show(
      VkSheetEntry(
        id: 'coverage',
        title: s.text('checkCoverage'),
        builder: (context) => CoverageCheckSheet(
          ranges: ranges,
          targetName: (id) => _targetName(s, id),
          onJump: (r) {
            _c.sheets.close('coverage');
            openMasks(MaskEditorTab.tracking);
            WidgetsBinding.instance.addPostFrameCallback((_) {
              unawaited(
                _maskKey.currentState?.startCorrection(r.maskId, r.startUs),
              );
            });
          },
          onManualKeyframe: (r) async {
            _c.sheets.close('coverage');
            final m = _c.state.maskById(r.maskId);
            final region = m?.regionAt(r.startUs);
            if (m == null || region == null) return;
            await _c.apply(UpdateMaskKeyframe(r.maskId, r.startUs, region));
            await _c.apply(AcceptTrackingRange(r.maskId, r.startUs, r.endUs));
          },
          onFullFrame: (r) async {
            _c.sheets.close('coverage');
            await _c.apply(
              AddMask(
                MaskType.manual,
                const MaskRegion(x: 0, y: 0, width: 1, height: 1),
                r.startUs,
                r.endUs,
              ),
            );
            await _c.apply(AcceptTrackingRange(r.maskId, r.startUs, r.endUs));
          },
          onBack: () {
            _c.sheets.close('coverage');
            openMasks(MaskEditorTab.tracking);
          },
          onForceExport: () {
            _c.sheets.close('coverage');
            unawaited(_exportKey.currentState?.start(acceptUncovered: true));
          },
        ),
      ),
    );
  }

  Map<ShortcutActivator, VoidCallback> _shortcuts() => {
    const SingleActivator(LogicalKeyboardKey.keyZ, control: true): () =>
        unawaited(_c.undo()),
    const SingleActivator(
      LogicalKeyboardKey.keyZ,
      control: true,
      shift: true,
    ): () =>
        unawaited(_c.redo()),
    const SingleActivator(LogicalKeyboardKey.keyZ, meta: true): () =>
        unawaited(_c.undo()),
    const SingleActivator(
      LogicalKeyboardKey.keyZ,
      meta: true,
      shift: true,
    ): () =>
        unawaited(_c.redo()),
    const SingleActivator(LogicalKeyboardKey.keyS): () =>
        unawaited(_c.splitAtPlayhead()),
    const SingleActivator(LogicalKeyboardKey.delete): () =>
        unawaited(_c.removeSelected()),
    const SingleActivator(LogicalKeyboardKey.space): () =>
        unawaited(_c.togglePlay()),
  };

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    return CallbackShortcuts(
      bindings: _shortcuts(),
      child: Focus(
        autofocus: true,
        child: VkSheetHost(
          controller: _c.sheets,
          child: ColoredBox(
            color: t.colors.background,
            child: SafeArea(
              child: ListenableBuilder(
                listenable: _c,
                builder: (context, _) => LayoutBuilder(
                  builder: (context, c) {
                    final wide =
                        VkLayoutClass.fromWidth(c.maxWidth) ==
                        VkLayoutClass.expanded;
                    return wide
                        ? _expanded(context, c.biggest)
                        : _compact(context, c.biggest);
                  },
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  // ------------------------------------------------------------ top bar --

  Widget _topBar(BuildContext context, {required bool compact}) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final st = _c.state;
    final modeTitle = switch (_c.mode) {
      EditorMode.clips => widget.title ?? s.text('editorTitle'),
      EditorMode.mask => s.text(
        _maskTab == MaskEditorTab.manual ? 'maskTitle' : 'editorTrack',
      ),
      EditorMode.export => s.text('exportTitle'),
    };
    final inMode = _c.mode != EditorMode.clips;
    return Padding(
      padding: EdgeInsetsDirectional.symmetric(
        horizontal: d.spacing8,
        vertical: d.spacing8,
      ),
      child: Row(
        children: [
          if (inMode)
            VkIconButton(
              icon: t.icons.resolve('back'),
              semanticLabel: s.text('playerBack'),
              onPressed: () => _c.mode = EditorMode.clips,
            )
          else if (widget.onBack != null)
            VkIconButton(
              icon: t.icons.resolve(compact ? 'close' : 'back'),
              semanticLabel: s.text(compact ? 'commonClose' : 'playerBack'),
              onPressed: widget.onBack,
            ),
          SizedBox(width: d.spacing8),
          Expanded(
            child: Semantics(
              header: true,
              child: Text(
                modeTitle,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: t.typography.titleLarge.copyWith(
                  color: t.colors.textPrimary,
                ),
              ),
            ),
          ),
          if (_c.mode != EditorMode.export) ...[
            VkIconButton(
              icon: t.icons.resolve('undo'),
              semanticLabel: s.text('editorUndo'),
              onPressed: st.canUndo ? () => unawaited(_c.undo()) : null,
            ),
            VkIconButton(
              icon: t.icons.resolve('redo'),
              semanticLabel: s.text('editorRedo'),
              onPressed: st.canRedo ? () => unawaited(_c.redo()) : null,
            ),
            SizedBox(width: d.spacing8),
            if (_c.mode == EditorMode.mask)
              ConstrainedBox(
                constraints: BoxConstraints(minWidth: d.targetMin * 2),
                child: VkButton(
                  label: s.text('maskDone'),
                  onPressed: () => _c.mode = EditorMode.clips,
                ),
              )
            else
              // Regular button height, pill width (design page 15).
              ConstrainedBox(
                constraints: BoxConstraints(minWidth: d.targetMin * 2),
                child: VkButton(
                  label: s.text('editorExport'),
                  onPressed: st.timeline.clips.isEmpty ? null : openExport,
                ),
              ),
          ],
        ],
      ),
    );
  }

  // ------------------------------------------------------------ preview --

  Widget _preview(BuildContext context, {bool showTime = true}) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final p = _c.preview;
    final style = vkOnPictureIconStyle(context);
    final playing = p?.state.value.phase == SessionPhase.playing;
    final duration = _c.state.timeline.durationUs;
    return ClipRRect(
      borderRadius: BorderRadius.circular(d.cornerLarge),
      child: ColoredBox(
        color: t.colors.playerCanvas,
        child: Stack(
          fit: StackFit.expand,
          children: [
            if (p != null)
              Semantics(
                image: true,
                label: s.text('playerPicture'),
                child: VkMediaSurface(
                  session: p,
                  builder: widget.pictureBuilder,
                ),
              ),
            if (showTime)
              PositionedDirectional(
                top: d.spacing12,
                start: d.spacing12,
                child: Container(
                  padding: EdgeInsetsDirectional.symmetric(
                    horizontal: d.spacing12,
                    vertical: d.spacing4,
                  ),
                  decoration: BoxDecoration(
                    color: t.drawables.glassPlayer.color,
                    borderRadius: BorderRadius.circular(d.cornerFull),
                  ),
                  child: Text(
                    s.editorTime(
                      VkFormat.timecode(_c.playheadUs),
                      VkFormat.timecode(duration),
                    ),
                    style: t.typography.timecode.copyWith(
                      color: t.colors.playerControlsContent,
                    ),
                  ),
                ),
              ),
            PositionedDirectional(
              start: 0,
              end: 0,
              bottom: d.spacing12,
              child: Center(
                child: Container(
                  padding: EdgeInsetsDirectional.symmetric(
                    horizontal: d.spacing8,
                  ),
                  decoration: BoxDecoration(
                    color: t.drawables.glassPlayer.color,
                    borderRadius: BorderRadius.circular(d.cornerFull),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      VkIconButton(
                        icon: t.icons.resolve('seekback'),
                        semanticLabel: s.rewind(10),
                        style: style,
                        onPressed: p == null
                            ? null
                            : () =>
                                  unawaited(_c.seek(_c.playheadUs - 10000000)),
                      ),
                      VkIconButton(
                        icon: playing ? t.icons.pause : t.icons.play,
                        semanticLabel: s.text(
                          playing ? 'playerPause' : 'playerPlay',
                        ),
                        style: style,
                        onPressed: p == null || duration <= 0
                            ? null
                            : () => unawaited(_c.togglePlay()),
                      ),
                      VkIconButton(
                        icon: t.icons.resolve('seekforward'),
                        semanticLabel: s.forward(10),
                        style: style,
                        onPressed: p == null
                            ? null
                            : () =>
                                  unawaited(_c.seek(_c.playheadUs + 10000000)),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _card(BuildContext context, Widget child) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return Container(
      padding: EdgeInsetsDirectional.all(d.spacing16),
      decoration: BoxDecoration(
        color: t.colors.surface,
        borderRadius: BorderRadius.circular(d.cornerLarge),
      ),
      child: child,
    );
  }

  Widget _exportPanel(BuildContext context) => ExportPanel(
    key: _exportKey,
    project: widget.project,
    sink: widget.sink,
    presets: widget.presets,
    onBackToEdit: () => _c.mode = EditorMode.clips,
    onReviewCoverage: _reviewCoverage,
    successActions: widget.exportSuccessActions,
  );

  Widget _maskEditor(BuildContext context) => MaskEditor(
    key: _maskKey,
    controller: _c,
    tab: _maskTab,
    onTabChanged: (tab) => setState(() => _maskTab = tab),
    pictureBuilder: widget.pictureBuilder,
  );

  Widget _estimate(BuildContext context) => EstimateLine(
    estimate: _c.state.estimate,
    compatibility: ConcatCompatibility.of(
      _c.state.timeline,
      fastConcatCapable: widget.fastConcatCapable,
    ),
  );

  // ----------------------------------------------------------- expanded --

  Widget _expanded(BuildContext context, Size size) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final hasClip = _c.selectedClipId != null;
    final toolbar = Wrap(
      spacing: d.spacing8,
      runSpacing: d.spacing8,
      children: [
        if (widget.onPickSourcesRequested != null)
          VkButton(
            label: s.text('editorAddVideo'),
            variant: VkButtonVariant.secondary,
            icon: t.icons.resolve('add'),
            onPressed: widget.onPickSourcesRequested,
          ),
        VkButton(
          label: s.text('editorReorder'),
          variant: VkButtonVariant.secondary,
          icon: t.icons.resolve('reorder'),
          onPressed: _c.state.timeline.clips.length > 1 ? _openOrder : null,
        ),
        VkButton(
          label: s.text('editorSplit'),
          variant: VkButtonVariant.secondary,
          icon: t.icons.resolve('split'),
          onPressed: _c.state.timeline.clips.isEmpty
              ? null
              : () => unawaited(_c.splitAtPlayhead()),
        ),
        VkButton(
          label: s.text('editorDelete'),
          variant: VkButtonVariant.secondary,
          icon: t.icons.resolve('delete'),
          onPressed: hasClip ? () => unawaited(_c.removeSelected()) : null,
        ),
        VkButton(
          label: s.text('editorMask'),
          variant: VkButtonVariant.secondary,
          icon: t.icons.resolve('mask'),
          onPressed: () => openMasks(MaskEditorTab.manual),
        ),
        VkButton(
          label: s.text('editorTrack'),
          variant: VkButtonVariant.secondary,
          icon: t.icons.resolve('face'),
          onPressed: () => openMasks(MaskEditorTab.tracking),
        ),
      ],
    );
    final Widget upper = switch (_c.mode) {
      EditorMode.clips => Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(child: _preview(context)),
          SizedBox(width: d.spacing16),
          SizedBox(
            width: math.min(d.targetMin * 8, size.width * 0.32),
            child: _card(
              context,
              SingleChildScrollView(
                child: ClipPropertiesPanel(
                  controller: _c,
                  fastConcatCapable: widget.fastConcatCapable,
                ),
              ),
            ),
          ),
        ],
      ),
      EditorMode.mask => _maskEditor(context),
      EditorMode.export => Center(
        child: ConstrainedBox(
          constraints: BoxConstraints(maxWidth: d.targetMin * 12),
          child: _card(
            context,
            SingleChildScrollView(child: _exportPanel(context)),
          ),
        ),
      ),
    };
    final scroll =
        MediaQuery.textScalerOf(context).scale(10) > 13 ||
        size.height < d.targetMin * 14;
    final lower = <Widget>[
      if (_c.mode == EditorMode.clips) ...[
        SizedBox(height: d.spacing12),
        Wrap(
          spacing: d.spacing16,
          runSpacing: d.spacing8,
          alignment: WrapAlignment.spaceBetween,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [toolbar, _estimate(context)],
        ),
      ],
      if (_c.mode != EditorMode.export) ...[
        SizedBox(height: d.spacing12),
        TimelineView(controller: _c),
      ],
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _topBar(context, compact: false),
        Expanded(
          child: Padding(
            padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing16),
            child: scroll
                ? ListView(
                    children: [
                      SizedBox(height: size.height * 0.7, child: upper),
                      ...lower,
                    ],
                  )
                : Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Expanded(child: upper),
                      ...lower,
                    ],
                  ),
          ),
        ),
      ],
    );
  }

  // ------------------------------------------------------------ compact --

  Widget _compact(BuildContext context, Size size) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final st = _c.state;
    final clips = st.timeline.clips;
    final index = clips.indexWhere((c) => c.clipId == _c.selectedClipId);
    final Widget body = switch (_c.mode) {
      EditorMode.clips => ListView(
        padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing16),
        children: [
          AspectRatio(
            aspectRatio: 16 / 9,
            child: _preview(context, showTime: false),
          ),
          SizedBox(height: d.spacing8),
          Center(
            child: Text(
              s.editorTime(
                VkFormat.timecode(_c.playheadUs),
                VkFormat.timecode(st.timeline.durationUs),
              ),
              style: t.typography.timecode.copyWith(
                color: t.colors.textSecondary,
              ),
            ),
          ),
          SizedBox(height: d.spacing8),
          TimelineView(controller: _c),
          SizedBox(height: d.spacing8),
          _card(
            context,
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  index < 0
                      ? s.text(
                          clips.isEmpty ? 'editorEmpty' : 'editorNoSelection',
                        )
                      : s.editorClipSummary(
                          index + 1,
                          s.durationSeconds(
                            VkFormat.number(
                              s,
                              clips[index].durationUs / 1e6,
                              maxFractionDigits: 1,
                            ),
                          ),
                        ),
                  style: t.typography.title.copyWith(
                    color: t.colors.textPrimary,
                  ),
                ),
                SizedBox(height: d.spacing12),
                Wrap(
                  spacing: d.spacing8,
                  runSpacing: d.spacing8,
                  alignment: WrapAlignment.spaceAround,
                  children: [
                    _actionDisc(
                      context,
                      'split',
                      s.text('editorSplit'),
                      clips.isEmpty
                          ? null
                          : () => unawaited(_c.splitAtPlayhead()),
                    ),
                    _actionDisc(
                      context,
                      'delete',
                      s.text('editorDelete'),
                      index < 0 ? null : () => unawaited(_c.removeSelected()),
                      danger: true,
                    ),
                    _actionDisc(
                      context,
                      'reorder',
                      s.text('editorReorder'),
                      clips.length > 1 ? _openOrder : null,
                    ),
                    _actionDisc(
                      context,
                      'mask',
                      s.text('editorMask'),
                      () => openMasks(MaskEditorTab.manual),
                    ),
                    _actionDisc(
                      context,
                      'face',
                      s.text('editorTrackShort'),
                      () => openMasks(MaskEditorTab.tracking),
                    ),
                  ],
                ),
              ],
            ),
          ),
          SizedBox(height: d.spacing12),
          _estimate(context),
          SizedBox(height: d.spacing16),
        ],
      ),
      EditorMode.mask => Column(
        children: [
          Expanded(
            child: Padding(
              padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing16),
              child: _maskEditor(context),
            ),
          ),
          Padding(
            padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing16),
            child: TimelineView(controller: _c),
          ),
        ],
      ),
      EditorMode.export => ListView(
        padding: EdgeInsetsDirectional.all(d.spacing16),
        children: [_exportPanel(context)],
      ),
    };
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _topBar(context, compact: true),
        Expanded(child: body),
        _bottomNav(context),
      ],
    );
  }

  Widget _actionDisc(
    BuildContext context,
    String icon,
    String label,
    VoidCallback? onPressed, {
    bool danger = false,
  }) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final style = t.components.buttonIcon.copyWithAll(
      (b) => b.copyWith(
        background: t.colors.surfaceVariant,
        content: danger ? t.colors.error : t.colors.textPrimary,
        minSize: d.targetMin,
      ),
    );
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        VkIconButton(
          icon: t.icons.resolve(icon),
          semanticLabel: label,
          onPressed: onPressed,
          style: style,
        ),
        SizedBox(height: d.spacing4),
        ExcludeSemantics(
          child: Text(
            label,
            style: t.typography.caption.copyWith(color: t.colors.textSecondary),
          ),
        ),
      ],
    );
  }

  Widget _bottomNav(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    Widget item(
      String icon,
      String label,
      bool selected,
      VoidCallback? onPressed,
    ) => Expanded(
      child: Semantics(
        button: true,
        selected: selected,
        enabled: onPressed != null,
        label: label,
        onTap: onPressed,
        child: ExcludeSemantics(
          child: InkWell(
            onTap: onPressed,
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: d.targetMin * 1.25),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    t.icons.resolve(icon),
                    color: selected
                        ? t.colors.primary
                        : (onPressed == null
                              ? t.colors.disabledContent
                              : t.colors.textSecondary),
                  ),
                  Text(
                    label,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: t.typography.caption.copyWith(
                      color: selected
                          ? t.colors.primary
                          : t.colors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
    final m = _c.mode;
    return DecoratedBox(
      decoration: BoxDecoration(color: t.colors.surface),
      child: Row(
        children: [
          item(
            'clips',
            s.text('editorClipsTab'),
            m == EditorMode.clips,
            () => _c.mode = EditorMode.clips,
          ),
          item(
            'add',
            s.text('editorAddTab'),
            false,
            widget.onPickSourcesRequested,
          ),
          item(
            'mask',
            s.text('editorMask'),
            m == EditorMode.mask && _maskTab == MaskEditorTab.manual,
            () => openMasks(MaskEditorTab.manual),
          ),
          item(
            'face',
            s.text('editorTrackShort'),
            m == EditorMode.mask && _maskTab == MaskEditorTab.tracking,
            () => openMasks(MaskEditorTab.tracking),
          ),
          item(
            'export',
            s.text('editorExport'),
            m == EditorMode.export,
            _c.state.timeline.clips.isEmpty ? null : openExport,
          ),
        ],
      ),
    );
  }
}
