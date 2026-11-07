import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_buttons.dart';
import '../common/vk_sheet_host.dart';
import '../common/vk_slider.dart';
import '../common/vk_switch.dart';
import '../editor/editor_controller.dart';
import '../foundation/format.dart';
import '../foundation/layout_class.dart';
import '../l10n/vk_strings.dart';
import '../player/media_surface.dart';
import '../theme/theme_scope.dart';
import 'coverage_strip.dart';
import 'mask_overlay.dart';

/// Sections of the mask editor (design pages 17–18).
enum MaskEditorTab {
  /// Manual masks: region, style, keyframes.
  manual,

  /// Face/object tracking, coverage and correction.
  tracking,
}

/// Target letter of the [i]-th automatic mask ("目标 A").
String vkTargetLetter(int i) => String.fromCharCode(0x41 + i % 26);

/// UI-07 `MaskEditor` (14 §5.7): entered as a mode of the editor (same
/// [EditorController], no new page). Manual masks are edited on the
/// picture (box + 8 handles, one `UpdateMaskKeyframe` per drag); tracking
/// detects faces (`detectCandidates`), lets the user pick targets or draw
/// an object box, shows progress with cancel, coverage per target and
/// correction (`CorrectTracking`). Interpolation comes from the API
/// (`MaskTrack.regionAt`), never from the UI.
class MaskEditor extends StatefulWidget {
  /// Creates the editor.
  const MaskEditor({
    super.key,
    required this.controller,
    this.tab = MaskEditorTab.manual,
    this.onTabChanged,
    this.pictureBuilder,
  });

  /// Editor controller.
  final EditorController controller;

  /// Section shown.
  final MaskEditorTab tab;

  /// Section switch.
  final ValueChanged<MaskEditorTab>? onTabChanged;

  /// Picture without texture (Dart Fake).
  final VideoKitPictureBuilder? pictureBuilder;

  @override
  State<MaskEditor> createState() => MaskEditorState();
}

/// State of [MaskEditor] (public for hosts and tests).
class MaskEditorState extends State<MaskEditor> {
  List<TrackingCandidate>? _candidates;
  bool _detecting = false;
  bool _objectMode = false;
  String? _correcting;

  EditorController get _c => widget.controller;

  /// Current face candidates (after "检测人脸").
  List<TrackingCandidate>? get candidates => _candidates;

  /// Mask being corrected, if any.
  String? get correcting => _correcting;

  List<MaskTrack> get _auto => [
    for (final m in _c.state.masks)
      if (m.type.isAutomatic) m,
  ];

  int get _duration => _c.state.timeline.durationUs;

  // ------------------------------------------------------------ actions --

  /// Adds a manual mask at the playhead (5 s long, inside the timeline).
  Future<void> addManualMask() async {
    final d = _duration;
    if (d <= 0) return;
    const len = 5000000;
    final start = math.max(0, math.min(_c.playheadUs, d - len));
    final r = await _c.apply(
      AddMask(
        MaskType.manual,
        const MaskRegion(x: 0.35, y: 0.35, width: 0.3, height: 0.2),
        start,
        math.min(d, start + len),
      ),
    );
    if (r is EditApplied && r.createdId != null) _c.selectMask(r.createdId);
  }

  /// Detects faces at the playhead.
  Future<void> detectFaces() async {
    setState(() => _detecting = true);
    final r = await _c.project.detectCandidates(_c.playheadUs);
    if (!mounted) return;
    setState(() {
      _detecting = false;
      _candidates = r.candidates;
    });
    final e = r.error;
    if (e != null) {
      _c.sheets.showToast(
        VkToastEntry(message: VkStrings.of(context).error(e.code)),
      );
    }
  }

  /// Picks a face candidate: one automatic mask + `StartTracking`.
  Future<void> chooseCandidate(TrackingCandidate cand) async {
    final r = await _c.apply(AddMask(MaskType.face, cand.region, 0, _duration));
    if (r is! EditApplied || r.createdId == null) return;
    _c.selectMask(r.createdId);
    setState(() => _chosen[cand.candidateId] = r.createdId!);
    await _c.apply(
      StartTracking(
        r.createdId!,
        TrackingKind.face,
        seedRegion: cand.region,
        targetId: cand.candidateId,
      ),
    );
  }

  final Map<String, String> _chosen = {};

  Future<void> _startObject(MaskRegion region) async {
    setState(() => _objectMode = false);
    final r = await _c.apply(AddMask(MaskType.object, region, 0, _duration));
    if (r is! EditApplied || r.createdId == null) return;
    _c.selectMask(r.createdId);
    await _c.apply(
      StartTracking(r.createdId!, TrackingKind.object, seedRegion: region),
    );
  }

  /// Starts correcting [maskId] at [atUs] (seek there, then draw a box).
  Future<void> startCorrection(String maskId, int atUs) async {
    _c.selectMask(maskId);
    setState(() {
      _correcting = maskId;
      _objectMode = false;
    });
    await _c.seek(atUs);
  }

  Future<void> _commitCorrection(String maskId, MaskRegion region) async {
    setState(() => _correcting = null);
    final m = _c.state.maskById(maskId);
    if (m == null) return;
    final at = _c.playheadUs.clamp(m.startUs, m.endUs - 1);
    await _c.apply(CorrectTracking(maskId, at, region));
  }

  Future<void> _commitEdit(MaskRegion region) async {
    final id = _c.selectedMaskId;
    final m = id == null ? null : _c.state.maskById(id);
    if (m == null || m.type.isAutomatic) return;
    final at = _c.playheadUs.clamp(m.startUs, m.endUs - 1);
    await _c.apply(UpdateMaskKeyframe(m.maskId, at, region));
  }

  // -------------------------------------------------------------- build --

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: _c,
      builder: (context, _) => LayoutBuilder(
        builder: (context, c) {
          final t = VkTheme.of(context);
          final d = t.dimensions;
          final wide =
              VkLayoutClass.fromWidth(c.maxWidth) != VkLayoutClass.compact;
          final panel = _panel(context);
          final preview = _preview(context);
          if (wide) {
            return Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(
                  width: math.min(d.targetMin * 8, c.maxWidth * 0.38),
                  child: _card(context, SingleChildScrollView(child: panel)),
                ),
                SizedBox(width: d.spacing16),
                Expanded(child: preview),
              ],
            );
          }
          return ListView(
            children: [
              AspectRatio(aspectRatio: 16 / 9, child: preview),
              SizedBox(height: d.spacing12),
              _card(context, panel),
            ],
          );
        },
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

  Widget _preview(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final preview = _c.preview;
    final st = _c.state;
    final at = _c.playheadUs;
    final tracking = widget.tab == MaskEditorTab.tracking;
    final auto = _auto;
    final boxes = <OverlayBox>[];
    for (final (i, m) in st.masks.indexed) {
      if (!m.enabled) continue;
      final r = m.regionAt(at);
      if (r == null) continue;
      final autoIndex = auto.indexOf(m);
      boxes.add(
        OverlayBox(
          id: m.maskId,
          region: r,
          label: m.type.isAutomatic
              ? s.trackTarget(vkTargetLetter(autoIndex))
              : s.maskName(i + 1),
          selected:
              m.maskId == _c.selectedMaskId &&
              (!m.type.isAutomatic || _correcting == m.maskId),
          reference: _correcting == m.maskId,
        ),
      );
    }
    if (tracking) {
      for (final (i, cand) in (_candidates ?? const []).indexed) {
        if (_chosen.containsKey(cand.candidateId)) continue;
        boxes.add(
          OverlayBox(
            id: cand.candidateId,
            region: cand.region,
            label: s.text('trackTapToSelect'),
            semanticLabel: s.trackFace(i + 1),
            dashed: true,
          ),
        );
      }
    }
    final correcting = _correcting;
    final mode = _objectMode || correcting != null
        ? OverlayDrawMode.draw
        : OverlayDrawMode.edit;
    return ClipRRect(
      borderRadius: BorderRadius.circular(t.dimensions.cornerLarge),
      child: ColoredBox(
        color: t.colors.playerCanvas,
        child: Stack(
          fit: StackFit.expand,
          children: [
            if (preview != null)
              VkMediaSurface(session: preview, builder: widget.pictureBuilder),
            if (preview != null)
              ValueListenableBuilder<VideoSize?>(
                valueListenable: preview.videoSize,
                builder: (context, size, _) => MaskOverlay(
                  boxes: boxes,
                  mediaSize: size,
                  mode: mode,
                  onTapBox: (id) {
                    final cand = (_candidates ?? const <TrackingCandidate>[])
                        .where((x) => x.candidateId == id)
                        .firstOrNull;
                    if (cand != null) {
                      unawaited(chooseCandidate(cand));
                    } else {
                      _c.selectMask(id);
                    }
                  },
                  onCommit: (region) {
                    if (correcting != null) {
                      unawaited(_commitCorrection(correcting, region));
                    } else if (_objectMode) {
                      unawaited(_startObject(region));
                    } else {
                      unawaited(_commitEdit(region));
                    }
                  },
                ),
              ),
            if (_objectMode || correcting != null)
              PositionedDirectional(
                start: t.dimensions.spacing12,
                end: t.dimensions.spacing12,
                bottom: t.dimensions.spacing12,
                child: _hintBar(
                  context,
                  s.text(_objectMode ? 'trackObjectHint' : 'trackCorrectHint'),
                  () => setState(() {
                    _objectMode = false;
                    _correcting = null;
                  }),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _hintBar(BuildContext context, String text, VoidCallback onCancel) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return Semantics(
      liveRegion: true,
      container: true,
      child: Container(
        padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing12),
        decoration: BoxDecoration(
          color: t.colors.surfaceHigh,
          borderRadius: BorderRadius.circular(d.cornerMedium),
        ),
        child: Row(
          children: [
            Expanded(
              child: Text(
                text,
                style: t.typography.bodySmall.copyWith(
                  color: t.colors.textPrimary,
                ),
              ),
            ),
            VkButton(
              label: s.text('commonCancel'),
              variant: VkButtonVariant.text,
              onPressed: onCancel,
            ),
          ],
        ),
      ),
    );
  }

  Widget _panel(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final tracking = widget.tab == MaskEditorTab.tracking;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        Wrap(
          spacing: d.spacing8,
          runSpacing: d.spacing8,
          children: [
            VkButton(
              label: s.text('maskTitle'),
              variant: VkButtonVariant.secondary,
              selected: !tracking,
              onPressed: () => widget.onTabChanged?.call(MaskEditorTab.manual),
            ),
            VkButton(
              label: s.text('editorTrack'),
              variant: VkButtonVariant.secondary,
              selected: tracking,
              onPressed: () =>
                  widget.onTabChanged?.call(MaskEditorTab.tracking),
            ),
          ],
        ),
        SizedBox(height: d.spacing16),
        if (tracking) ..._trackingPanel(context) else ..._manualPanel(context),
      ],
    );
  }

  // ------------------------------------------------------------- manual --

  String _styleLabel(VkStrings s, MaskStyle st) =>
      s.text(st == MaskStyle.mosaic ? 'maskStyleMosaic' : 'maskStyleBlur');

  String _typeLabel(VkStrings s, MaskType ty) => s.text(switch (ty) {
    MaskType.manual => 'maskTypeManual',
    MaskType.face => 'maskTypeFace',
    MaskType.object => 'maskTypeObject',
  });

  List<Widget> _manualPanel(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final st = _c.state;
    final sel = _c.selectedMaskId == null
        ? null
        : st.maskById(_c.selectedMaskId!);
    final selIndex = sel == null ? -1 : st.masks.indexOf(sel);
    final at = _c.playheadUs;
    final hasKeyframeHere =
        sel != null && sel.keyframes.any((k) => (k.atUs - at).abs() < 40000);
    return [
      Row(
        children: [
          Expanded(
            child: Semantics(
              header: true,
              child: Text(
                s.text('maskListTitle'),
                style: t.typography.title.copyWith(color: t.colors.textPrimary),
              ),
            ),
          ),
          VkIconButton(
            icon: t.icons.resolve('add'),
            semanticLabel: s.text('maskAdd'),
            onPressed: () => unawaited(addManualMask()),
          ),
        ],
      ),
      if (st.masks.isEmpty)
        Text(
          s.text('maskNone'),
          style: t.typography.bodySmall.copyWith(color: t.colors.textSecondary),
        ),
      for (final (i, m) in st.masks.indexed)
        Padding(
          padding: EdgeInsetsDirectional.only(top: d.spacing8),
          child: _MaskRow(
            name: s.maskNameTyped(i + 1, _typeLabel(s, m.type)),
            summary: s.maskSummary(
              _styleLabel(s, m.style),
              VkFormat.timecode(m.startUs),
              VkFormat.timecode(m.endUs),
            ),
            keyframes: m.type.isAutomatic
                ? s.text('maskKeyframesTracker')
                : s.maskKeyframes(m.keyframes.length),
            selected: m.maskId == _c.selectedMaskId,
            enabled: m.enabled,
            onTap: () => _c.selectMask(m.maskId),
            onEnabled: (v) => unawaited(_c.apply(SetMaskEnabled(m.maskId, v))),
          ),
        ),
      if (sel != null) ...[
        SizedBox(height: d.spacing16),
        Text(
          s.text('maskStyle'),
          style: t.typography.label.copyWith(color: t.colors.textSecondary),
        ),
        SizedBox(height: d.spacing8),
        Wrap(
          spacing: d.spacing8,
          children: [
            for (final style in MaskStyle.values)
              VkButton(
                label: _styleLabel(s, style),
                variant: VkButtonVariant.secondary,
                selected: sel.style == style,
                onPressed: () => unawaited(
                  _c.apply(SetMaskStyle(sel.maskId, style, sel.strength)),
                ),
              ),
          ],
        ),
        SizedBox(height: d.spacing12),
        Row(
          children: [
            Text(
              s.text('maskStrength'),
              style: t.typography.label.copyWith(color: t.colors.textSecondary),
            ),
            SizedBox(width: d.spacing12),
            Expanded(
              child: VkSlider(
                value: sel.strength,
                semanticLabel: s.text('maskStrength'),
                semanticValue: (v) => VkFormat.percent(s, v),
                onChangeEnd: (v) =>
                    unawaited(_c.apply(SetMaskStyle(sel.maskId, sel.style, v))),
              ),
            ),
          ],
        ),
        if (!sel.type.isAutomatic) ...[
          SizedBox(height: d.spacing12),
          Text(
            s.maskKeyframeTitle(selIndex + 1),
            style: t.typography.label.copyWith(color: t.colors.textPrimary),
          ),
          SizedBox(height: d.spacing8),
          Wrap(
            spacing: d.spacing8,
            runSpacing: d.spacing8,
            children: [
              VkButton(
                label: s.text('maskAddKeyframe'),
                variant: VkButtonVariant.secondary,
                onPressed: at >= sel.startUs && at < sel.endUs
                    ? () => unawaited(
                        _c.apply(
                          UpdateMaskKeyframe(
                            sel.maskId,
                            at,
                            sel.regionAt(at) ?? sel.keyframes.first.region,
                          ),
                        ),
                      )
                    : null,
              ),
              if (hasKeyframeHere && sel.keyframes.length > 1)
                VkButton(
                  label: s.text('maskRemoveKeyframe'),
                  variant: VkButtonVariant.text,
                  onPressed: () {
                    final k = sel.keyframes.firstWhere(
                      (k) => (k.atUs - at).abs() < 40000,
                    );
                    unawaited(_c.apply(RemoveMaskKeyframe(sel.maskId, k.atUs)));
                  },
                ),
            ],
          ),
        ],
        SizedBox(height: d.spacing12),
        VkButton(
          label: s.text('maskDelete'),
          variant: VkButtonVariant.text,
          icon: t.icons.resolve('delete'),
          onPressed: () => unawaited(_c.apply(RemoveMask(sel.maskId))),
        ),
      ],
    ];
  }

  // ----------------------------------------------------------- tracking --

  List<Widget> _trackingPanel(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final st = _c.state;
    final auto = _auto;
    final cands = _candidates;
    return [
      Align(
        alignment: AlignmentDirectional.centerStart,
        child: Container(
          padding: EdgeInsetsDirectional.symmetric(
            horizontal: d.spacing12,
            vertical: d.spacing4,
          ),
          decoration: BoxDecoration(
            color: t.colors.successContainer,
            borderRadius: BorderRadius.circular(d.cornerFull),
          ),
          child: Text(
            s.text('trackLocalOnly'),
            style: t.typography.label.copyWith(color: t.colors.textPrimary),
          ),
        ),
      ),
      SizedBox(height: d.spacing12),
      Wrap(
        spacing: d.spacing8,
        runSpacing: d.spacing8,
        children: [
          VkButton(
            label: s.text('trackDetectFaces'),
            variant: VkButtonVariant.secondary,
            icon: t.icons.resolve('face'),
            onPressed: _detecting ? null : () => unawaited(detectFaces()),
          ),
          VkButton(
            label: s.text('trackObject'),
            variant: VkButtonVariant.secondary,
            icon: t.icons.resolve('selectbox'),
            selected: _objectMode,
            onPressed: () => setState(() {
              _objectMode = !_objectMode;
              _correcting = null;
            }),
          ),
        ],
      ),
      if (cands != null) ...[
        SizedBox(height: d.spacing12),
        Semantics(
          liveRegion: true,
          child: Text(
            s.trackDetected(cands.length),
            style: t.typography.title.copyWith(color: t.colors.textPrimary),
          ),
        ),
        Text(
          s.text('trackChooseHint'),
          style: t.typography.bodySmall.copyWith(color: t.colors.textSecondary),
        ),
        for (final (i, cand) in cands.indexed)
          _candidateRow(context, i, cand, auto),
      ],
      for (final (i, m) in auto.indexed) ...[
        SizedBox(height: d.spacing16),
        _runSection(context, i, m, st.tracking[m.maskId]),
      ],
      if (auto.isNotEmpty) ...[
        SizedBox(height: d.spacing16),
        const CoverageLegend(),
      ],
    ];
  }

  Widget _candidateRow(
    BuildContext context,
    int i,
    TrackingCandidate cand,
    List<MaskTrack> auto,
  ) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final chosenMask = _chosen[cand.candidateId];
    final chosen = chosenMask != null;
    final autoIndex = chosen
        ? auto.indexWhere((m) => m.maskId == chosenMask)
        : -1;
    final label = chosen && autoIndex >= 0
        ? s.trackTarget(vkTargetLetter(autoIndex))
        : s.trackFace(i + 1);
    return Semantics(
      checked: chosen,
      button: true,
      label: label,
      onTap: chosen ? null : () => unawaited(chooseCandidate(cand)),
      child: ExcludeSemantics(
        child: InkWell(
          onTap: chosen ? null : () => unawaited(chooseCandidate(cand)),
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: t.dimensions.targetMin),
            child: Row(
              children: [
                Icon(t.icons.resolve('face'), color: t.colors.textSecondary),
                SizedBox(width: t.dimensions.spacing12),
                Expanded(
                  child: Text(
                    label,
                    style: t.typography.body.copyWith(
                      color: t.colors.textPrimary,
                    ),
                  ),
                ),
                Icon(
                  t.icons.resolve(chosen ? 'checkboxon' : 'checkboxoff'),
                  color: chosen ? t.colors.primary : t.colors.borderStrong,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _runSection(
    BuildContext context,
    int index,
    MaskTrack m,
    TrackingRun? run,
  ) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final name = s.trackTarget(vkTargetLetter(index));
    final total = m.endUs - m.startUs;
    final status = run?.status;
    final progress = run?.progress;
    final blocking = [
      for (final seg in run?.coverage.segments ?? const <CoverageRange>[])
        if (seg.state.blocksExport && !seg.accepted) seg,
    ];
    final recomputing =
        status == TrackingRunStatus.running &&
        m.keyframes.any((k) => k.source == KeyframeSource.user);
    final statusText = switch (status) {
      TrackingRunStatus.running => s.text('trackRunning'),
      TrackingRunStatus.completed => s.text('trackCompleted'),
      TrackingRunStatus.cancelled => s.text('trackCancelled'),
      TrackingRunStatus.failed => s.text('trackFailed'),
      null => s.text('coverageNotAnalyzed'),
    };
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        Wrap(
          spacing: d.spacing8,
          runSpacing: d.spacing4,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            Text(
              name,
              style: t.typography.label.copyWith(color: t.colors.textPrimary),
            ),
            Text(
              statusText,
              style: t.typography.caption.copyWith(
                color: t.colors.textSecondary,
              ),
            ),
            if (status == TrackingRunStatus.running)
              Text(
                progress == null
                    ? s.text('trackAnalyzing')
                    : s.trackAnalyzed(
                        VkFormat.timecode((total * progress).round()),
                        VkFormat.timecode(total),
                      ),
                style: t.typography.caption.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
            if (recomputing)
              Text(
                s.text('trackRecomputing'),
                style: t.typography.caption.copyWith(color: t.colors.warning),
              ),
          ],
        ),
        if (status == TrackingRunStatus.running) ...[
          SizedBox(height: d.spacing8),
          Semantics(
            label: s.text('trackRunning'),
            value: progress == null ? null : VkFormat.percent(s, progress),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(d.cornerFull),
              child: LinearProgressIndicator(
                value: progress,
                minHeight: t.components.progress.height,
                color: t.components.progress.indicator,
                backgroundColor: t.components.progress.track,
              ),
            ),
          ),
          SizedBox(height: d.spacing8),
          Align(
            alignment: AlignmentDirectional.centerStart,
            child: VkButton(
              label: s.text('trackCancel'),
              variant: VkButtonVariant.secondary,
              onPressed: () => unawaited(_c.apply(CancelTracking(m.maskId))),
            ),
          ),
        ],
        if (run != null) ...[
          SizedBox(height: d.spacing8),
          CoverageStrip(report: run.coverage, totalUs: _duration, name: name),
        ],
        for (final seg in blocking)
          Padding(
            padding: EdgeInsetsDirectional.only(top: d.spacing4),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    s.coverageSegment(
                      coverageStateLabel(s, seg.state),
                      VkFormat.timecode(seg.startUs),
                      VkFormat.timecode(seg.endUs),
                    ),
                    style: t.typography.caption.copyWith(
                      color: t.colors.textPrimary,
                    ),
                  ),
                ),
                VkButton(
                  label: s.text('trackCorrect'),
                  variant: VkButtonVariant.text,
                  onPressed: status == TrackingRunStatus.running
                      ? null
                      : () => unawaited(startCorrection(m.maskId, seg.startUs)),
                ),
              ],
            ),
          ),
      ],
    );
  }
}

class _MaskRow extends StatelessWidget {
  const _MaskRow({
    required this.name,
    required this.summary,
    required this.keyframes,
    required this.selected,
    required this.enabled,
    required this.onTap,
    required this.onEnabled,
  });

  final String name;
  final String summary;
  final String keyframes;
  final bool selected;
  final bool enabled;
  final VoidCallback onTap;
  final ValueChanged<bool> onEnabled;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return Container(
      decoration: BoxDecoration(
        color: selected ? t.colors.primaryContainer : t.colors.surfaceVariant,
        borderRadius: BorderRadius.circular(d.cornerMedium),
        border: Border.all(
          color: selected ? t.colors.primary : t.colors.surfaceVariant,
          width: d.borderWidth * 1.5,
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Semantics(
              selected: selected,
              child: MergeSemantics(
                child: InkWell(
                  onTap: onTap,
                  child: Padding(
                    padding: EdgeInsetsDirectional.all(d.spacing12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          name,
                          // Design page 17: the mask name leads the row.
                          style: t.typography.body.copyWith(
                            fontWeight: FontWeight.w600,
                            color: selected
                                ? t.colors.onPrimaryContainer
                                : t.colors.textPrimary,
                          ),
                        ),
                        Text(
                          summary,
                          style: t.typography.caption.copyWith(
                            color: selected
                                ? t.colors.onPrimaryContainer
                                : t.colors.textSecondary,
                          ),
                        ),
                        Text(
                          keyframes,
                          style: t.typography.caption.copyWith(
                            color: selected
                                ? t.colors.onPrimaryContainer
                                : t.colors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
          VkSwitch(value: enabled, semanticLabel: name, onChanged: onEnabled),
        ],
      ),
    );
  }
}
