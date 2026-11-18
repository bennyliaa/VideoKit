import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_buttons.dart';
import '../common/vk_segmented.dart';
import '../common/vk_sheet_host.dart';
import '../common/vk_slider.dart';
import '../common/vk_switch.dart';
import '../editor/editor_controller.dart';
import '../foundation/feature_scope.dart';
import '../foundation/format.dart';
import '../foundation/layout_class.dart';
import '../l10n/vk_strings.dart';
import '../player/media_surface.dart';
import '../theme/theme_data.dart';
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

/// Whether [r] covers the whole frame (the mask "全画面打码" adds, E7 Q9).
bool vkIsFullFrame(MaskRegion? r) =>
    r != null &&
    r.x <= 0.001 &&
    r.y <= 0.001 &&
    r.width >= 0.999 &&
    r.height >= 0.999;

/// Region of [m] at its last trusted keyframe at or before [atUs] (E7 Q1):
/// a user keyframe, or a tracker keyframe that is TRACKED or
/// LOW_CONFIDENCE. Null when there is none.
MaskRegion? vkLastTrustedRegion(MaskTrack m, int atUs) {
  MaskRegion? found;
  for (final k in m.keyframes) {
    if (k.atUs > atUs) break;
    final trusted =
        k.source == KeyframeSource.user ||
        k.state == TrackingState.tracked ||
        k.state == TrackingState.lowConfidence;
    if (trusted) found = k.region;
  }
  return found;
}

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
    this.onRequestAvatar,
    this.avatarBuilder,
  });

  /// "更换头像" (REQ-ED-07, 04A E6 5): the host opens its own avatar pages
  /// and returns the stored `avatarToken` with the size and offset chosen
  /// on its adjust page (a [MaskAvatar]), or null when the user cancels.
  /// The mask keeps its "随头部转动" setting. When this callback is null
  /// the avatar entry is hidden (a mask that already has an avatar keeps
  /// showing it).
  final Future<MaskAvatar?> Function(AvatarRequest request)? onRequestAvatar;

  /// Draws the avatar picture of a token (host storage or `builtin:N`);
  /// without it the preview shows a neutral placeholder.
  final Widget Function(BuildContext context, String avatarToken)?
  avatarBuilder;

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
          final panel = _panel(context, wide: wide);
          final preview = _preview(context);
          if (wide) {
            // Design pages 17–18: keyframes (manual) or one status row per
            // target (tracking) in a card under the picture.
            final bottom = widget.tab == MaskEditorTab.tracking
                ? _trackRows(context)
                : _keyframeCard(context);
            return Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(
                  width: math.min(d.targetMin * 8, c.maxWidth * 0.38),
                  child: _card(context, SingleChildScrollView(child: panel)),
                ),
                SizedBox(width: d.spacing16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Expanded(child: preview),
                      if (bottom != null) ...[
                        SizedBox(height: d.spacing12),
                        _card(context, bottom),
                      ],
                    ],
                  ),
                ),
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
    // E7 Q9: where "全画面打码" covers the frame, no avatar is drawn.
    final fullFrame = st.masks.any(
      (o) =>
          o.enabled &&
          o.style != MaskStyle.image &&
          vkIsFullFrame(o.regionAt(at)),
    );
    for (final (i, m) in st.masks.indexed) {
      if (!m.enabled) continue;
      var r = m.regionAt(at);
      final autoIndex = auto.indexOf(m);
      var avatar = m.style == MaskStyle.image ? m.avatar : null;
      var lost = false;
      if (avatar != null &&
          m.type.isAutomatic &&
          at >= m.startUs &&
          at < m.endUs) {
        // E7 Q1: never put the avatar on someone else's head: LOST,
        // AMBIGUOUS and not analysed show a dashed box at the last trusted
        // position, labelled "目标丢失".
        final state = st.tracking[m.maskId]?.coverage.stateAt(at);
        if (state == null || state.blocksExport) {
          avatar = null;
          lost = true;
          r = vkLastTrustedRegion(m, at) ?? r;
        }
      }
      if (r == null) continue;
      if (fullFrame) avatar = null;
      boxes.add(
        OverlayBox(
          id: m.maskId,
          region: r,
          dashed: lost,
          // REQ-ED-07: the avatar follows the box, its size, offset and
          // (optionally) the head roll.
          content: avatar == null ? null : _avatarPicture(context, avatar),
          contentScale: avatar?.scale ?? 1,
          contentOffset: avatar == null
              ? Offset.zero
              : Offset(avatar.offsetX, avatar.offsetY),
          contentRotationDeg: avatar != null && avatar.followRotation
              ? (m.rollAt(at) ?? 0)
              : 0,
          label: lost
              ? s.text('avatarTargetLost')
              : m.type.isAutomatic
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

  Widget _panel(BuildContext context, {required bool wide}) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final tracking = widget.tab == MaskEditorTab.tracking;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        VkSegmented<MaskEditorTab>(
          segments: [
            VkSegment(value: MaskEditorTab.manual, label: s.text('maskTitle')),
            VkSegment(
              value: MaskEditorTab.tracking,
              label: s.text('editorTrack'),
            ),
          ],
          selected: widget.tab,
          onChanged: widget.onTabChanged,
        ),
        SizedBox(height: d.spacing16),
        if (tracking)
          ..._trackingPanel(context, wide: wide)
        else
          ..._manualPanel(context, wide: wide),
      ],
    );
  }

  /// Keyframe controls of the selected manual mask (design page 17), or
  /// null when none is selected.
  Widget? _keyframeCard(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final st = _c.state;
    final sel = _c.selectedMaskId == null
        ? null
        : st.maskById(_c.selectedMaskId!);
    if (sel == null || sel.type.isAutomatic) return null;
    final selIndex = st.masks.indexOf(sel);
    final at = _c.playheadUs;
    final hasKeyframeHere = sel.keyframes.any(
      (k) => (k.atUs - at).abs() < 40000,
    );
    // UI-AUDIT-A4 (design page 17): the mask's range on the timeline with
    // its keyframe diamonds and the playhead.
    final bar = ExcludeSemantics(
      child: SizedBox(
        height: d.timelineMaskRow,
        child: CustomPaint(
          painter: KeyframeRangePainter(
            durationUs: st.timeline.durationUs,
            startUs: sel.startUs,
            endUs: sel.endUs,
            keyframesUs: [
              for (final k in sel.keyframes)
                if (k.source != KeyframeSource.tracker) k.atUs,
            ],
            playheadUs: at,
            theme: t,
          ),
          child: const SizedBox.expand(),
        ),
      ),
    );
    final header = Wrap(
      spacing: d.spacing8,
      runSpacing: d.spacing8,
      crossAxisAlignment: WrapCrossAlignment.center,
      alignment: WrapAlignment.spaceBetween,
      children: [
        Semantics(
          header: true,
          child: Text(
            s.maskKeyframeTitle(selIndex + 1),
            style: t.typography.body.copyWith(
              fontWeight: FontWeight.w600,
              color: t.colors.textPrimary,
            ),
          ),
        ),
        Wrap(
          spacing: d.spacing8,
          children: [
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
            VkButton(
              label: s.text('maskAddKeyframe'),
              variant: VkButtonVariant.text,
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
          ],
        ),
      ],
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [header, SizedBox(height: d.spacing8), bar],
    );
  }

  /// One status row per target plus the legend (design page 18), or null
  /// without targets.
  Widget? _trackRows(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final auto = _auto;
    if (auto.isEmpty) return null;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        for (final (i, m) in auto.indexed)
          Padding(
            padding: EdgeInsetsDirectional.only(bottom: d.spacing8),
            child: Row(
              children: [
                SizedBox(
                  width: d.targetMin * 1.5,
                  child: Text(
                    s.trackTarget(vkTargetLetter(i)),
                    style: t.typography.body.copyWith(
                      fontWeight: FontWeight.w600,
                      color: t.colors.textPrimary,
                    ),
                  ),
                ),
                Expanded(
                  child: CoverageStrip(
                    report:
                        _c.state.tracking[m.maskId]?.coverage ??
                        CoverageReport.empty(),
                    totalUs: _duration,
                    name: s.trackTarget(vkTargetLetter(i)),
                  ),
                ),
              ],
            ),
          ),
        const CoverageLegend(),
      ],
    );
  }

  // ------------------------------------------------------------- manual --

  String _styleLabel(VkStrings s, MaskStyle st) => s.text(switch (st) {
    MaskStyle.mosaic => 'maskStyleMosaic',
    MaskStyle.blur => 'maskStyleBlur',
    MaskStyle.image => 'maskStyleImage',
  });

  /// Avatar size slider range (design page 25 "大小").
  static const double avatarScaleMin = 0.5;

  /// See [avatarScaleMin].
  static const double avatarScaleMax = 2.0;

  Widget _avatarPicture(BuildContext context, MaskAvatar avatar) {
    final t = VkTheme.of(context);
    final b = widget.avatarBuilder;
    if (b != null) return b(context, avatar.avatarToken);
    return DecoratedBox(
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: t.colors.surfaceVariant,
      ),
      child: Center(
        child: Icon(
          t.icons.resolve('face'),
          color: t.colors.textSecondary,
          size: t.dimensions.icon24,
        ),
      ),
    );
  }

  /// "更换头像" / choosing the avatar style without an avatar: asks the
  /// host, then sets the avatar (keeping size and rotation) and the style.
  Future<void> requestAvatar(MaskTrack m) async {
    final ask = widget.onRequestAvatar;
    if (ask == null) return;
    // REQ-API-10: the host's gate before its avatar pages open.
    final open = await VideoKitFeatures.of(
      context,
    ).enter(VideoKitFeature.avatar, sessionId: _c.project.projectId);
    if (!open || !mounted) return;
    final chosen = await ask(
      AvatarRequest(
        projectId: _c.project.projectId,
        maskId: m.maskId,
        currentToken: m.avatar?.avatarToken,
      ),
    );
    if (chosen == null || !mounted) return;
    final avatar = chosen.copyWith(
      followRotation: m.avatar?.followRotation ?? chosen.followRotation,
    );
    await _c.apply(SetMaskAvatar(m.maskId, avatar));
    if (m.style != MaskStyle.image) {
      await _c.apply(SetMaskStyle(m.maskId, MaskStyle.image, m.strength));
    }
  }

  Future<void> _chooseStyle(MaskTrack m, MaskStyle style) async {
    if (style == MaskStyle.image && m.avatar == null) {
      await requestAvatar(m);
      return;
    }
    await _c.apply(SetMaskStyle(m.maskId, style, m.strength));
  }

  List<Widget> _avatarControls(BuildContext context, MaskTrack sel) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final avatar = sel.avatar!;
    final canChange = widget.onRequestAvatar != null;
    final scaleT =
        ((avatar.scale - avatarScaleMin) / (avatarScaleMax - avatarScaleMin))
            .clamp(0.0, 1.0);
    return [
      // Design page 25: the avatar row ("我的头像 / 点按更换").
      Semantics(
        button: canChange,
        label: s.text('maskAvatarMine'),
        hint: canChange ? s.text('maskAvatarChange') : null,
        excludeSemantics: true,
        onTap: canChange ? () => unawaited(requestAvatar(sel)) : null,
        child: InkWell(
          borderRadius: BorderRadius.circular(d.cornerMedium),
          onTap: canChange ? () => unawaited(requestAvatar(sel)) : null,
          child: Container(
            constraints: BoxConstraints(minHeight: d.targetMin),
            padding: EdgeInsetsDirectional.all(d.spacing12),
            decoration: BoxDecoration(
              color: t.colors.surfaceVariant,
              borderRadius: BorderRadius.circular(d.cornerMedium),
            ),
            child: Row(
              children: [
                SizedBox.square(
                  dimension: d.targetMin,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(d.cornerSmall),
                    child: _avatarPicture(context, avatar),
                  ),
                ),
                SizedBox(width: d.spacing12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        s.text('maskAvatarMine'),
                        style: t.typography.body.copyWith(
                          fontWeight: FontWeight.w600,
                          color: t.colors.textPrimary,
                        ),
                      ),
                      if (canChange)
                        Text(
                          s.text('maskAvatarChange'),
                          style: t.typography.caption.copyWith(
                            color: t.colors.textSecondary,
                          ),
                        ),
                    ],
                  ),
                ),
                if (canChange)
                  Icon(
                    t.icons.resolve('next'),
                    color: t.colors.textSecondary,
                    size: d.icon20,
                  ),
              ],
            ),
          ),
        ),
      ),
      SizedBox(height: d.spacing12),
      Row(
        children: [
          Text(
            s.text('maskAvatarSize'),
            style: t.typography.label.copyWith(color: t.colors.textSecondary),
          ),
          SizedBox(width: d.spacing12),
          Expanded(
            child: VkSlider(
              value: scaleT,
              semanticLabel: s.text('maskAvatarSize'),
              semanticValue: (v) => VkFormat.percent(
                s,
                (avatarScaleMin + v * (avatarScaleMax - avatarScaleMin)) / 2,
              ),
              onChangeEnd: (v) => unawaited(
                _c.apply(
                  SetMaskAvatar(
                    sel.maskId,
                    avatar.copyWith(
                      scale:
                          avatarScaleMin +
                          v * (avatarScaleMax - avatarScaleMin),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
      SizedBox(height: d.spacing8),
      Container(
        padding: EdgeInsetsDirectional.symmetric(
          horizontal: d.spacing12,
          vertical: d.spacing4,
        ),
        decoration: BoxDecoration(
          color: t.colors.surfaceVariant,
          borderRadius: BorderRadius.circular(d.cornerMedium),
        ),
        child: Row(
          children: [
            Expanded(
              child: Text(
                s.text('maskAvatarFollowRotation'),
                style: t.typography.body.copyWith(color: t.colors.textPrimary),
              ),
            ),
            VkSwitch(
              value: avatar.followRotation,
              semanticLabel: s.text('maskAvatarFollowRotation'),
              onChanged: (v) => unawaited(
                _c.apply(
                  SetMaskAvatar(
                    sel.maskId,
                    avatar.copyWith(followRotation: v),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    ];
  }

  String _typeLabel(VkStrings s, MaskType ty) => s.text(switch (ty) {
    MaskType.manual => 'maskTypeManual',
    MaskType.face => 'maskTypeFace',
    MaskType.object => 'maskTypeObject',
  });

  List<Widget> _manualPanel(BuildContext context, {required bool wide}) {
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
        // Design page 17: neutral segmented control.
        VkSegmented<MaskStyle>(
          segments: [
            for (final style in MaskStyle.values)
              // REQ-ED-07: "头像" only when the host can supply one (or the
              // mask already has one).
              // REQ-API-10: and only while AVATAR is not hidden.
              if (style != MaskStyle.image ||
                  (VideoKitFeatures.of(
                        context,
                      ).isEnabled(VideoKitFeature.avatar) &&
                      (widget.onRequestAvatar != null || sel.avatar != null)))
                VkSegment(value: style, label: _styleLabel(s, style)),
          ],
          selected: sel.style,
          semanticLabel: s.text('maskStyle'),
          onChanged: (style) => unawaited(_chooseStyle(sel, style)),
        ),
        SizedBox(height: d.spacing12),
        if (sel.style == MaskStyle.image && sel.avatar != null)
          ..._avatarControls(context, sel)
        else
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
        // Tablets show the keyframes in the card under the picture.
        if (!sel.type.isAutomatic && !wide) ...[
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

  List<Widget> _trackingPanel(BuildContext context, {required bool wide}) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final st = _c.state;
    final auto = _auto;
    final cands = _candidates;
    // Design page 18: the "本机处理 · 不上传" badge sits in the editor's top
    // bar (VideoKitEditor).
    return [
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
        _runSection(context, i, m, st.tracking[m.maskId], strip: !wide),
      ],
      if (auto.isNotEmpty && !wide) ...[
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
    TrackingRun? run, {
    required bool strip,
  }) {
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
          // Design page 18: full-width outlined cancel.
          VkButton(
            label: s.text('trackCancel'),
            variant: VkButtonVariant.outline,
            onPressed: () => unawaited(_c.apply(CancelTracking(m.maskId))),
          ),
        ],
        if (run != null && strip) ...[
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
                      VkFormat.timecodeTenths(seg.startUs),
                      VkFormat.timecodeTenths(seg.endUs),
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

/// Mask range bar of the keyframe card (UI-AUDIT-A4, design page 17): the
/// whole timeline as a track, the mask's range filled, user keyframes as
/// diamonds, the playhead as a line.
class KeyframeRangePainter extends CustomPainter {
  /// Creates the painter.
  KeyframeRangePainter({
    required this.durationUs,
    required this.startUs,
    required this.endUs,
    required this.keyframesUs,
    required this.playheadUs,
    required this.theme,
  });

  /// Timeline duration.
  final int durationUs;

  /// Mask range start.
  final int startUs;

  /// Mask range end.
  final int endUs;

  /// User keyframe times.
  final List<int> keyframesUs;

  /// Playhead.
  final int playheadUs;

  /// Theme.
  final VideoKitThemeData theme;

  @override
  void paint(Canvas canvas, Size size) {
    if (size.isEmpty || durationUs <= 0) return;
    final c = theme.colors;
    final d = theme.dimensions;
    final k = size.height * 0.3;
    final left = k;
    final width = math.max(0.0, size.width - k * 2);
    double x(int us) => left + width * (us.clamp(0, durationUs) / durationUs);
    final cy = size.height / 2;
    final trackH = size.height * 0.3;
    final radius = Radius.circular(trackH / 2);
    canvas
      ..drawRRect(
        RRect.fromRectAndRadius(
          Rect.fromLTRB(left, cy - trackH / 2, left + width, cy + trackH / 2),
          radius,
        ),
        Paint()..color = c.surfaceVariant,
      )
      ..drawRRect(
        RRect.fromRectAndRadius(
          Rect.fromLTRB(x(startUs), cy - trackH / 2, x(endUs), cy + trackH / 2),
          radius,
        ),
        Paint()..color = c.primaryContainer,
      );
    final diamond = Paint()..color = c.textPrimary;
    for (final us in keyframesUs) {
      final px = x(us);
      canvas.drawPath(
        Path()
          ..moveTo(px, cy - k)
          ..lineTo(px + k, cy)
          ..lineTo(px, cy + k)
          ..lineTo(px - k, cy)
          ..close(),
        diamond,
      );
    }
    final ph = x(playheadUs);
    canvas.drawLine(
      Offset(ph, 0),
      Offset(ph, size.height),
      Paint()
        ..color = c.primary
        ..strokeWidth = d.focusRingWidth,
    );
  }

  @override
  bool shouldRepaint(KeyframeRangePainter old) =>
      old.durationUs != durationUs ||
      old.startUs != startUs ||
      old.endUs != endUs ||
      old.playheadUs != playheadUs ||
      old.theme != theme ||
      !_same(old.keyframesUs, keyframesUs);

  static bool _same(List<int> a, List<int> b) {
    if (a.length != b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }
}
