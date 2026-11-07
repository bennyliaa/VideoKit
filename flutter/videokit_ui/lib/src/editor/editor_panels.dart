import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_buttons.dart';
import '../foundation/format.dart';
import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';
import 'editor_controller.dart';

/// `mm:ss.mmm` for precise clip boundaries (design page 15).
String vkPreciseTime(int us) {
  final ms = (us / 1000).round();
  final m = ms ~/ 60000;
  final s = (ms ~/ 1000) % 60;
  final r = ms % 1000;
  return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}'
      '.${r.toString().padLeft(3, '0')}';
}

/// Multi-input compatibility (14 §5.6, design page 16): all inputs equal
/// in size, frame rate, codec and rotation → fast concat possible.
@immutable
final class ConcatCompatibility {
  /// Computes compatibility of [timeline]'s sources; [fastConcatCapable]
  /// is the device capability (`EditCapability.fastConcat`).
  factory ConcatCompatibility.of(
    Timeline timeline, {
    bool fastConcatCapable = true,
  }) {
    final sources = timeline.sources;
    if (sources.length < 2) {
      return ConcatCompatibility._(
        mismatched: const [],
        fastConcat: fastConcatCapable && sources.isNotEmpty,
      );
    }
    final ref = sources.first.probe;
    final mismatched = [
      for (final src in sources.skip(1))
        if (src.mismatch ||
            src.probe.width != ref.width ||
            src.probe.height != ref.height ||
            src.probe.fps != ref.fps ||
            src.probe.videoCodec != ref.videoCodec ||
            src.probe.rotationDeg != ref.rotationDeg)
          src.sourceId,
    ];
    return ConcatCompatibility._(
      mismatched: mismatched,
      fastConcat: fastConcatCapable && mismatched.isEmpty,
    );
  }

  const ConcatCompatibility._({
    required this.mismatched,
    required this.fastConcat,
  });

  /// Sources differing from the first one.
  final List<String> mismatched;

  /// Fast (remux) concatenation possible.
  final bool fastConcat;

  /// Whether a transcode is needed.
  bool get needsTranscode => mismatched.isNotEmpty;
}

/// "预计 01:42 · 约 96 MB · 快速拼接可用" — or "无法预估" when the project
/// cannot estimate (never fake numbers, 14 §5.6).
class EstimateLine extends StatelessWidget {
  /// Creates the line.
  const EstimateLine({
    super.key,
    required this.estimate,
    required this.compatibility,
  });

  /// Estimate.
  final EditEstimate estimate;

  /// Compatibility.
  final ConcatCompatibility compatibility;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = estimate.durationUs;
    final size = estimate.sizeBytes;
    final text = d == null
        ? s.text('estimateUnknown')
        : size == null
        ? s.estimateDurationOnly(VkFormat.timecode(d))
        : s.estimateLine(VkFormat.timecode(d), VkFormat.fileSize(s, size));
    final fast = compatibility.fastConcat;
    return Semantics(
      container: true,
      liveRegion: true,
      child: Wrap(
        spacing: t.dimensions.spacing8,
        runSpacing: t.dimensions.spacing4,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          Text(
            text,
            style: t.typography.label.copyWith(color: t.colors.textPrimary),
          ),
          Text(
            s.text(fast ? 'fastConcatAvailable' : 'fastConcatUnavailable'),
            style: t.typography.label.copyWith(
              color: fast ? t.colors.trackTracked : t.colors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}

/// Compatibility notice card (design page 16): consistent → fast concat;
/// otherwise how the export will unify the inputs.
class CompatibilityNotice extends StatelessWidget {
  /// Creates the notice.
  const CompatibilityNotice({super.key, required this.compatibility});

  /// Compatibility.
  final ConcatCompatibility compatibility;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final warn = compatibility.needsTranscode;
    return Semantics(
      container: true,
      child: Container(
        padding: EdgeInsetsDirectional.all(d.spacing12),
        decoration: BoxDecoration(
          color: warn ? t.colors.warningContainer : t.colors.surfaceVariant,
          borderRadius: BorderRadius.circular(d.cornerMedium),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              warn ? t.icons.warning : t.icons.check,
              size: d.icon20,
              color: warn ? t.colors.warning : t.colors.trackTracked,
            ),
            SizedBox(width: d.spacing8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    s.text(warn ? 'concatTranscodeTitle' : 'concatFast'),
                    style: t.typography.label.copyWith(
                      color: t.colors.textPrimary,
                    ),
                  ),
                  if (warn) ...[
                    SizedBox(height: d.spacing4),
                    Text(
                      s.concatTranscodeDetail(compatibility.mismatched.length),
                      style: t.typography.bodySmall.copyWith(
                        color: t.colors.textPrimary,
                      ),
                    ),
                  ],
                  SizedBox(height: d.spacing4),
                  Text(
                    s.text(
                      compatibility.fastConcat
                          ? 'fastConcatAvailable'
                          : 'fastConcatUnavailable',
                    ),
                    style: t.typography.caption.copyWith(
                      color: t.colors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Properties of the selected clip (design page 15): source, in/out,
/// duration, keyframe-alignment note for fast concat, split/delete.
class ClipPropertiesPanel extends StatelessWidget {
  /// Creates the panel.
  const ClipPropertiesPanel({
    super.key,
    required this.controller,
    this.fastConcatCapable = true,
  });

  /// Editor controller.
  final EditorController controller;

  /// Device fast-concat capability.
  final bool fastConcatCapable;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final st = controller.state;
    final id = controller.selectedClipId;
    final clips = st.timeline.clips;
    final index = clips.indexWhere((c) => c.clipId == id);
    if (index < 0) {
      return Padding(
        padding: EdgeInsetsDirectional.all(d.spacing16),
        child: Text(
          s.text(clips.isEmpty ? 'editorEmpty' : 'editorNoSelection'),
          style: t.typography.body.copyWith(color: t.colors.textSecondary),
        ),
      );
    }
    final clip = clips[index];
    final src = st.timeline.sourceById(clip.sourceId);
    final compat = ConcatCompatibility.of(
      st.timeline,
      fastConcatCapable: fastConcatCapable,
    );
    Widget row(String label, String value) => Padding(
      padding: EdgeInsetsDirectional.only(bottom: d.spacing8),
      child: MergeSemantics(
        child: Wrap(
          spacing: d.spacing12,
          runSpacing: d.spacing4,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            ConstrainedBox(
              constraints: BoxConstraints(minWidth: d.targetMin * 1.25),
              child: Text(
                label,
                style: t.typography.label.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
            ),
            Container(
              padding: EdgeInsetsDirectional.symmetric(
                horizontal: d.spacing12,
                vertical: d.spacing8,
              ),
              decoration: BoxDecoration(
                color: t.colors.surfaceVariant,
                borderRadius: BorderRadius.circular(d.cornerSmall),
              ),
              child: Text(
                value,
                style: t.typography.body.copyWith(color: t.colors.textPrimary),
              ),
            ),
          ],
        ),
      ),
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        Semantics(
          header: true,
          child: Text(
            s.editorClipProps(index + 1),
            style: t.typography.title.copyWith(color: t.colors.textPrimary),
          ),
        ),
        SizedBox(height: d.spacing12),
        row(s.text('propSource'), src?.displayName ?? clip.sourceId),
        row(s.text('propIn'), vkPreciseTime(clip.inUs)),
        row(s.text('propOut'), vkPreciseTime(clip.outUs)),
        row(
          s.text('propDuration'),
          s.durationSeconds(
            VkFormat.number(s, clip.durationUs / 1e6, maxFractionDigits: 1),
          ),
        ),
        if (compat.fastConcat && clips.length > 1) ...[
          SizedBox(height: d.spacing4),
          Container(
            padding: EdgeInsetsDirectional.symmetric(
              horizontal: d.spacing12,
              vertical: d.spacing8,
            ),
            decoration: BoxDecoration(
              color: t.colors.warningContainer,
              borderRadius: BorderRadius.circular(d.cornerFull),
            ),
            child: Text(
              s.text('keyframeAlignNotice'),
              style: t.typography.caption.copyWith(color: t.colors.textPrimary),
            ),
          ),
        ],
        SizedBox(height: d.spacing16),
        Wrap(
          spacing: d.spacing12,
          runSpacing: d.spacing8,
          children: [
            VkButton(
              label: s.text('editorSplit'),
              variant: VkButtonVariant.secondary,
              icon: t.icons.resolve('split'),
              onPressed: () => unawaited(controller.splitAtPlayhead()),
            ),
            VkButton(
              label: s.text('editorDelete'),
              variant: VkButtonVariant.secondary,
              icon: t.icons.resolve('delete'),
              onPressed: () => unawaited(controller.removeSelected()),
            ),
          ],
        ),
      ],
    );
  }
}

/// Clip order sheet (design page 16 right): one row per clip with its
/// source parameters, drag to reorder (one `MoveClip` per drop), add more
/// videos, compatibility and estimate.
class ClipOrderSheet extends StatelessWidget {
  /// Creates the sheet content.
  const ClipOrderSheet({
    super.key,
    required this.controller,
    this.onAddSources,
    this.fastConcatCapable = true,
  });

  /// Editor controller.
  final EditorController controller;

  /// Host source picker (null hides “添加视频”).
  final VoidCallback? onAddSources;

  /// Device fast-concat capability.
  final bool fastConcatCapable;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return ListenableBuilder(
      listenable: controller,
      builder: (context, _) {
        final st = controller.state;
        final clips = st.timeline.clips;
        final compat = ConcatCompatibility.of(
          st.timeline,
          fastConcatCapable: fastConcatCapable,
        );
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              s.sourcesCount(clips.length),
              style: t.typography.label.copyWith(color: t.colors.textSecondary),
            ),
            SizedBox(height: d.spacing8),
            ReorderableListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              buildDefaultDragHandles: false,
              itemCount: clips.length,
              onReorderItem: (from, target) {
                if (target != from) {
                  unawaited(
                    controller.apply(MoveClip(clips[from].clipId, target)),
                  );
                }
              },
              itemBuilder: (context, i) {
                final clip = clips[i];
                final src = st.timeline.sourceById(clip.sourceId);
                final p = src?.probe;
                final odd = compat.mismatched.contains(clip.sourceId);
                return Padding(
                  key: ValueKey(clip.clipId),
                  padding: EdgeInsetsDirectional.only(bottom: d.spacing8),
                  child: Container(
                    padding: EdgeInsetsDirectional.all(d.spacing12),
                    decoration: BoxDecoration(
                      color: t.colors.surfaceVariant,
                      borderRadius: BorderRadius.circular(d.cornerMedium),
                    ),
                    child: Row(
                      children: [
                        Text(
                          VkFormat.number(s, i + 1),
                          style: t.typography.title.copyWith(
                            color: t.colors.textSecondary,
                          ),
                        ),
                        SizedBox(width: d.spacing12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                src?.displayName ?? clip.sourceId,
                                style: t.typography.label.copyWith(
                                  color: t.colors.textPrimary,
                                ),
                              ),
                              if (p != null)
                                Text(
                                  s.sourceMeta(
                                    p.width,
                                    p.height,
                                    VkFormat.number(s, p.fps ?? 0),
                                    p.videoCodec,
                                  ),
                                  style: t.typography.caption.copyWith(
                                    color: odd
                                        ? t.colors.warning
                                        : t.colors.textSecondary,
                                  ),
                                ),
                              if (p != null && p.rotationDeg != 0)
                                Text(
                                  s.sourceRotated(p.rotationDeg),
                                  style: t.typography.caption.copyWith(
                                    color: t.colors.warning,
                                  ),
                                ),
                              Text(
                                VkFormat.timecode(clip.durationUs),
                                style: t.typography.caption.copyWith(
                                  color: t.colors.textSecondary,
                                ),
                              ),
                            ],
                          ),
                        ),
                        ReorderableDragStartListener(
                          index: i,
                          child: Semantics(
                            label: s.text('editorReorder'),
                            child: SizedBox.square(
                              dimension: d.targetMin,
                              child: Icon(
                                t.icons.resolve('reorder'),
                                color: t.colors.textSecondary,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
            if (onAddSources != null)
              VkButton(
                label: s.text('editorAddVideo'),
                variant: VkButtonVariant.secondary,
                icon: t.icons.resolve('add'),
                onPressed: onAddSources,
              ),
            SizedBox(height: d.spacing12),
            CompatibilityNotice(compatibility: compat),
            SizedBox(height: d.spacing12),
            EstimateLine(estimate: st.estimate, compatibility: compat),
          ],
        );
      },
    );
  }
}
