import 'dart:async';
import 'dart:typed_data';

import 'package:flutter/foundation.dart' show listEquals, setEquals;
import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_buttons.dart';
import '../export/export_panel.dart' show vkCodecName;
import '../foundation/format.dart';
import '../foundation/layout_class.dart';
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

/// Why a multi-input export transcodes instead of fast concatenation (M4).
enum ConcatFallbackReason {
  /// The device cannot remux (`EditFeatures.fastConcat` false).
  deviceUnsupported,

  /// Inputs differ from the first one (see [ConcatCompatibility.differences]).
  inputsDiffer,

  /// The engine refused fast concatenation at the export check
  /// (`ExportWarnings.fastConcatRejected`).
  engineRejected,
}

/// Input property that differs from the first input.
enum ConcatDifference {
  /// Width or height.
  resolution,

  /// Frame rate.
  frameRate,

  /// Video codec.
  codec,

  /// Rotation.
  rotation,

  /// The project flagged the source as not concatenable as is.
  other,

  /// A source has no probe, or its probe lacks the video codec, size,
  /// frame rate, or the audio codec of a source with audio (04A E3/E4,
  /// Kotlin `ConcatReason.PROBE_INCOMPLETE`).
  probeIncomplete,
}

/// Whether [p] can be compared for fast concatenation (same rule as Kotlin
/// `ConcatRules`: video codec, size and frame rate known; the audio codec
/// known when the source has audio).
bool vkProbeComplete(SourceProbe? p) =>
    p != null &&
    p.videoCodec != null &&
    p.width > 0 &&
    p.height > 0 &&
    p.fps != null &&
    !(p.hasAudio && p.audioCodec == null);

/// Multi-input compatibility (14 §5.6, design page 16): all inputs equal
/// in size, frame rate, codec and rotation → fast concat possible. M4: the
/// chosen path and, for a transcode, the reason ([reason], [differences];
/// [withPrecheck] applies the engine's answer).
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
        differences: const {},
        fastConcat: fastConcatCapable && sources.isNotEmpty,
        reason: fastConcatCapable
            ? null
            : ConcatFallbackReason.deviceUnsupported,
        multiInput: false,
      );
    }
    final ref = sources.first.probe;
    final differences = <ConcatDifference>{};
    final mismatched = <String>[];
    // 04A E3/E4: a missing probe value means the inputs cannot be compared:
    // transcode with PROBE_INCOMPLETE.
    for (final src in sources) {
      if (!vkProbeComplete(src.probe)) {
        mismatched.add(src.sourceId);
        differences.add(ConcatDifference.probeIncomplete);
      }
    }
    if (ref != null) {
      for (final src in sources.skip(1)) {
        final p = src.probe;
        if (p == null) continue;
        final diff = {
          if (p.width != ref.width || p.height != ref.height)
            ConcatDifference.resolution,
          if (p.fps != ref.fps) ConcatDifference.frameRate,
          if (p.videoCodec != ref.videoCodec) ConcatDifference.codec,
          if (p.rotationDeg != ref.rotationDeg) ConcatDifference.rotation,
          if (src.mismatch) ConcatDifference.other,
        };
        if (diff.isNotEmpty) {
          if (!mismatched.contains(src.sourceId)) mismatched.add(src.sourceId);
          differences.addAll(diff);
        }
      }
    }
    final fast = fastConcatCapable && mismatched.isEmpty;
    return ConcatCompatibility._(
      mismatched: mismatched,
      differences: differences,
      fastConcat: fast,
      reason: fast
          ? null
          : (fastConcatCapable
                ? ConcatFallbackReason.inputsDiffer
                : ConcatFallbackReason.deviceUnsupported),
      multiInput: true,
    );
  }

  const ConcatCompatibility._({
    required this.mismatched,
    required this.differences,
    required this.fastConcat,
    required this.reason,
    required this.multiInput,
  });

  /// Sources differing from the first one.
  final List<String> mismatched;

  /// Which properties differ (empty when they all match).
  final Set<ConcatDifference> differences;

  /// Fast (remux) concatenation is the chosen path.
  final bool fastConcat;

  /// Why the export transcodes; null when fast.
  final ConcatFallbackReason? reason;

  /// More than one source (the path matters).
  final bool multiInput;

  /// Whether a transcode is needed because the inputs differ.
  bool get needsTranscode => mismatched.isNotEmpty;

  /// Applies the export check: an engine refusal turns a fast path into a
  /// transcode with [ConcatFallbackReason.engineRejected].
  ConcatCompatibility withPrecheck(ExportPrecheck? precheck) {
    if (precheck == null ||
        !fastConcat ||
        !ExportWarnings.has(
          precheck.warnings,
          ExportWarnings.fastConcatRejected,
        )) {
      return this;
    }
    return ConcatCompatibility._(
      mismatched: mismatched,
      differences: differences,
      fastConcat: false,
      reason: ConcatFallbackReason.engineRejected,
      multiInput: multiInput,
    );
  }

  @override
  bool operator ==(Object other) =>
      other is ConcatCompatibility &&
      listEquals(other.mismatched, mismatched) &&
      setEquals(other.differences, differences) &&
      other.fastConcat == fastConcat &&
      other.reason == reason &&
      other.multiInput == multiInput;

  @override
  int get hashCode => Object.hash(
    Object.hashAll(mismatched),
    Object.hashAllUnordered(differences),
    fastConcat,
    reason,
    multiInput,
  );
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
    // Design page 15: one line in the status colour ("预计 01:42 · 约 96 MB ·
    // 快速拼接可用" green; otherwise secondary text).
    final color = d != null && fast
        ? t.colors.trackTracked
        : t.colors.textSecondary;
    return Semantics(
      container: true,
      liveRegion: true,
      child: Text(
        s.estimateWithPath(
          text,
          s.text(fast ? 'fastConcatAvailable' : 'fastConcatUnavailable'),
        ),
        style: t.typography.bodySmall.copyWith(color: color),
      ),
    );
  }
}

/// Chosen concat path and, for a transcode, why (M4): "拼接方式：快速拼接"
/// or "拼接方式：统一转码" plus one line per reason. Shown only for more than
/// one input.
class ConcatPathInfo extends StatelessWidget {
  /// Creates the info.
  const ConcatPathInfo({super.key, required this.compatibility});

  /// Compatibility (after [ConcatCompatibility.withPrecheck] when known).
  final ConcatCompatibility compatibility;

  /// Reason lines for [c], in display order.
  static List<String> reasons(VkStrings s, ConcatCompatibility c) =>
      switch (c.reason) {
        null => const [],
        ConcatFallbackReason.deviceUnsupported => [
          s.text('concatReasonDevice'),
        ],
        ConcatFallbackReason.engineRejected => [s.text('concatReasonEngine')],
        ConcatFallbackReason.inputsDiffer => [
          for (final d in ConcatDifference.values)
            if (c.differences.contains(d))
              s.text(switch (d) {
                ConcatDifference.resolution => 'concatDiffResolution',
                ConcatDifference.frameRate => 'concatDiffFrameRate',
                ConcatDifference.codec => 'concatDiffCodec',
                ConcatDifference.rotation => 'concatDiffRotation',
                ConcatDifference.other => 'concatDiffOther',
                ConcatDifference.probeIncomplete => 'concatDiffProbeIncomplete',
              }),
        ],
      };

  @override
  Widget build(BuildContext context) {
    final c = compatibility;
    if (!c.multiInput) return const SizedBox.shrink();
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return MergeSemantics(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            s.text(c.fastConcat ? 'concatPathFast' : 'concatPathTranscode'),
            style: t.typography.label.copyWith(color: t.colors.textPrimary),
          ),
          for (final r in reasons(s, c))
            Padding(
              padding: EdgeInsetsDirectional.only(top: d.spacing4),
              child: Text(
                r,
                style: t.typography.bodySmall.copyWith(
                  color: t.colors.textSecondary,
                ),
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
    final c = compatibility;
    final warn = !c.fastConcat;
    final title = c.needsTranscode
        ? 'concatTranscodeTitle'
        : (c.fastConcat ? 'concatFast' : 'concatParamsMatch');
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
                    s.text(title),
                    style: t.typography.label.copyWith(
                      color: t.colors.textPrimary,
                    ),
                  ),
                  if (c.needsTranscode) ...[
                    SizedBox(height: d.spacing4),
                    Text(
                      s.concatTranscodeDetail(compatibility.mismatched.length),
                      style: t.typography.bodySmall.copyWith(
                        color: t.colors.textPrimary,
                      ),
                    ),
                  ],
                  SizedBox(height: d.spacing8),
                  ConcatPathInfo(compatibility: compatibility),
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
    // Design page 15: label column, value box filling the rest; stacked
    // at large text scales.
    final stacked = VkLayoutClass.collapseSecondary(
      MediaQuery.textScalerOf(context),
    );
    Widget row(String label, String value) {
      final labelText = Text(
        label,
        style: t.typography.bodySmall.copyWith(color: t.colors.textSecondary),
      );
      final box = Container(
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
      );
      return Padding(
        padding: EdgeInsetsDirectional.only(bottom: d.spacing8),
        child: MergeSemantics(
          child: stacked
              ? Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    labelText,
                    SizedBox(height: d.spacing4),
                    box,
                  ],
                )
              : Row(
                  children: [
                    SizedBox(width: d.targetMin * 1.25, child: labelText),
                    SizedBox(width: d.spacing12),
                    Expanded(child: box),
                  ],
                ),
        ),
      );
    }

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
        // Design page 15: split (outline) and delete (danger) share the row.
        Row(
          children: [
            Expanded(
              child: VkButton(
                label: s.text('editorSplit'),
                variant: VkButtonVariant.outline,
                onPressed: () => unawaited(controller.splitAtPlayhead()),
              ),
            ),
            SizedBox(width: d.spacing12),
            Expanded(
              child: VkButton(
                label: s.text('editorDelete'),
                variant: VkButtonVariant.danger,
                onPressed: () => unawaited(controller.removeSelected()),
              ),
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
    this.onNext,
  });

  /// Design page 16: the primary "next: preview" button (closes the sheet).
  final VoidCallback? onNext;

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
                        // Design page 16: picture with the clip length
                        // (first frame when the project offers timeline
                        // media, UI-AUDIT-A4).
                        _ClipThumb(
                          duration: VkFormat.timecode(clip.durationUs),
                          media: switch (controller.project) {
                            final VideoKitEditMediaPreview m => m,
                            _ => null,
                          },
                          sourceId: clip.sourceId,
                          atUs: clip.inUs,
                        ),
                        SizedBox(width: d.spacing12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                src?.displayName ?? clip.sourceId,
                                style: t.typography.body.copyWith(
                                  fontWeight: FontWeight.w600,
                                  color: t.colors.textPrimary,
                                ),
                              ),
                              // 04A E4: a probe without codec / size / frame
                              // rate shows no meta line (nothing guessed).
                              if (p != null && vkProbeComplete(p))
                                Text(
                                  s.sourceMeta(
                                    p.width,
                                    p.height,
                                    VkFormat.number(s, p.fps ?? 0),
                                    vkCodecName(p.videoCodec),
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
                                p != null &&
                                        clip.inUs <= 0 &&
                                        clip.outUs >= p.durationUs
                                    ? s.text('sourceTrimAll')
                                    : s.sourceTrimRange(
                                        VkFormat.timecodeTenths(clip.inUs),
                                        VkFormat.timecodeTenths(clip.outUs),
                                      ),
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
                variant: VkButtonVariant.outline,
                icon: t.icons.resolve('add'),
                onPressed: onAddSources,
              ),
            SizedBox(height: d.spacing12),
            CompatibilityNotice(compatibility: compat),
            SizedBox(height: d.spacing12),
            EstimateLine(estimate: st.estimate, compatibility: compat),
            if (onNext != null) ...[
              SizedBox(height: d.spacing16),
              VkButton(label: s.text('concatNext'), onPressed: onNext),
            ],
          ],
        );
      },
    );
  }
}

/// Clip picture with its length (design page 16): the clip's first frame
/// when the project offers timeline media (UI-AUDIT-A4), otherwise a plain
/// frame.
class _ClipThumb extends StatefulWidget {
  const _ClipThumb({
    required this.duration,
    required this.media,
    required this.sourceId,
    required this.atUs,
  });

  final String duration;
  final VideoKitEditMediaPreview? media;
  final String sourceId;
  final int atUs;

  @override
  State<_ClipThumb> createState() => _ClipThumbState();
}

class _ClipThumbState extends State<_ClipThumb> {
  Uint8List? _bytes;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void didUpdateWidget(_ClipThumb old) {
    super.didUpdateWidget(old);
    if (old.sourceId != widget.sourceId ||
        old.atUs != widget.atUs ||
        old.media != widget.media) {
      _load();
    }
  }

  void _load() {
    final media = widget.media;
    if (media == null) return;
    final key = (widget.sourceId, widget.atUs);
    unawaited(
      media
          .sourceThumbnail(widget.sourceId, widget.atUs)
          .then((b) {
            if (!mounted || key != (widget.sourceId, widget.atUs)) return;
            setState(() => _bytes = b);
          })
          .catchError((Object _) {}),
    );
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final bytes = _bytes;
    return ExcludeSemantics(
      child: Container(
        width: d.targetMin * 2,
        height: d.targetMin * 1.25,
        alignment: AlignmentDirectional.bottomStart,
        padding: EdgeInsetsDirectional.all(d.spacing4),
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(
          color: t.colors.playerCanvas,
          borderRadius: BorderRadius.circular(d.cornerSmall),
          image: bytes == null
              ? null
              : DecorationImage(image: MemoryImage(bytes), fit: BoxFit.cover),
        ),
        child: Container(
          padding: EdgeInsetsDirectional.symmetric(
            horizontal: d.spacing8,
            vertical: d.spacing4 / 2,
          ),
          decoration: BoxDecoration(
            color: t.drawables.glassPlayer.color,
            borderRadius: BorderRadius.circular(d.cornerFull),
          ),
          child: Text(
            widget.duration,
            style: t.typography.timecode.copyWith(
              color: t.colors.playerControlsContent,
            ),
          ),
        ),
      ),
    );
  }
}
