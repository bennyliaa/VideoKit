import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_buttons.dart';
import '../foundation/format.dart';
import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';
import '../editor/editor_panels.dart';

/// `VideoKitStableError.params` key of the bytes an export still needs
/// (J8; reported by the Kit when known).
const String requiredBytesParam = 'requiredBytes';

/// J8: the space [e] says must be freed, rounded up to 10 MB, or null when
/// it is not an `OUTPUT_SPACE_INSUFFICIENT` with a valid `requiredBytes`.
int? vkSpaceToFree(VideoKitStableError e) {
  if (e.code != ErrorCode.outputSpaceInsufficient) return null;
  final need = int.tryParse(e.params[requiredBytesParam] ?? '');
  if (need == null || need <= 0) return null;
  const step = 10 * 1000 * 1000;
  return (need + step - 1) ~/ step * step;
}

/// Display name of a codec / container MIME type (technical names, not
/// translated).
String vkCodecName(String? mime) => switch (mime) {
  null => '',
  'video/avc' => 'H.264',
  'video/hevc' => 'HEVC',
  'video/x-vnd.on2.vp9' => 'VP9',
  'video/av01' => 'AV1',
  'video/x-vnd.on2.vp8' => 'VP8',
  'video/mp4v-es' => 'MPEG-4',
  'video/3gpp' => 'H.263',
  'video/mpeg2' => 'MPEG-2',
  'audio/mp4a-latm' => 'AAC',
  'audio/opus' => 'Opus',
  'audio/vorbis' => 'Vorbis',
  'audio/mpeg' => 'MP3',
  'audio/flac' => 'FLAC',
  'audio/ac3' => 'AC-3',
  'audio/eac3' => 'E-AC-3',
  'audio/raw' => 'PCM',
  _ => mime.split('/').last.toUpperCase(),
};

/// "MP4 · H.264 · AAC" for an output format (technical identifiers).
String vkFormatLine(String container, String? video, String? audio) => [
  container.toUpperCase(),
  if (video != null) vkCodecName(video),
  if (audio != null) vkCodecName(audio),
].join(' · ');

/// Label of a preset.
String vkPresetLabel(VkStrings s, String presetId) => switch (presetId) {
  ExportPresets.original => s.text('presetOriginal'),
  ExportPresets.p1080 => s.text('preset1080'),
  ExportPresets.p720 => s.text('preset720'),
  _ => presetId,
};

/// Resolves the sink right before an export starts, for example after the
/// host's system "另存为" dialog; null = the user cancelled, nothing starts.
typedef VideoKitSinkProvider = Future<VideoKitOutputSink?> Function(
  VideoKitExportRequest request,
);

/// UI-08 `ExportPanel` (14 §5.8, design pages 20–21). Reads the project
/// state, so reopening the panel during an export shows its progress:
///
/// * not started: presets, format, `checkExport` results (encoder, output
///   location, space, mask coverage), start;
/// * exporting: stage steps; a percentage and remaining time only when the
///   project reports a fraction, otherwise an indeterminate bar; cancel;
/// * cancelling / cancelled, failed (reason, impact, suggestion, error
///   code), completed (summary, host actions, demo notice).
class ExportPanel extends StatefulWidget {
  /// Creates a panel.
  const ExportPanel({
    super.key,
    required this.project,
    required this.sink,
    this.presets = const [],
    this.onBackToEdit,
    this.sinkProvider,
    this.fastConcatCapable = true,
    this.onReviewCoverage,
    this.successActions,
    this.pinActions = false,
    this.progressPreview,
  });

  /// Project.
  final VideoKitEditProject project;

  /// Output sink (host provided); used for `checkExport` and, without
  /// [sinkProvider], for the export.
  final VideoKitOutputSink sink;

  /// Sink for the export itself, resolved when the user starts it.
  final VideoKitSinkProvider? sinkProvider;

  /// Presets from the capability report (`outputFormats`).
  final List<OutputFormat> presets;

  /// Device capability `EditFeatures.fastConcat` (M4: path shown).
  final bool fastConcatCapable;

  /// Back to the editor.
  final VoidCallback? onBackToEdit;

  /// Uncovered tracking ranges block the export: the editor shows
  /// `CoverageCheckSheet` and may call [ExportPanelState.start] with
  /// `acceptUncovered: true`.
  final ValueChanged<List<UncoveredRange>>? onReviewCoverage;

  /// Host actions for a finished export ("打开", "分享").
  final Widget Function(BuildContext context, VideoKitExportedMedia media)?
  successActions;

  /// Design pages 20–21: with a bounded height the content scrolls and the
  /// main buttons stay at the bottom; otherwise everything is one column.
  final bool pinActions;

  /// Picture shown above the stages while exporting (design page 20).
  final Widget? progressPreview;

  @override
  State<ExportPanel> createState() => ExportPanelState();
}

/// State of [ExportPanel] (host handle via `GlobalKey`).
class ExportPanelState extends State<ExportPanel> {
  late String _presetId = _firstAvailable();
  ExportPrecheck? _precheck;
  int _checkGeneration = 0;
  VideoKitExportResult? _result;
  int? _checkedRevision;
  bool _starting = false;

  /// Last finished result in this panel.
  VideoKitExportResult? get result => _result;

  /// Selected preset.
  String get presetId => _presetId;

  String _firstAvailable() {
    final ok = widget.presets.where((p) => p.available);
    return ok.isEmpty ? ExportPresets.original : ok.first.presetId;
  }

  @override
  void initState() {
    super.initState();
    widget.project.state.addListener(_onState);
    unawaited(_check());
  }

  @override
  void dispose() {
    widget.project.state.removeListener(_onState);
    super.dispose();
  }

  void _onState() {
    if (!mounted) return;
    final rev = widget.project.state.value.revision;
    if (_checkedRevision != rev && _result == null) unawaited(_check());
    setState(() {});
  }

  Future<void> _check() async {
    final gen = ++_checkGeneration;
    _checkedRevision = widget.project.state.value.revision;
    final p = await widget.project.checkExport(
      VideoKitExportRequest(presetId: _presetId),
      widget.sink,
    );
    if (!mounted || gen != _checkGeneration) return;
    setState(() => _precheck = p);
  }

  /// Selects a preset and re-runs the precheck.
  void selectPreset(String id) {
    setState(() {
      _presetId = id;
      _precheck = null;
    });
    unawaited(_check());
  }

  /// Starts the export ([acceptUncovered] after the coverage check).
  Future<void> start({bool acceptUncovered = false}) async {
    if (_starting) return;
    final request = VideoKitExportRequest(
      presetId: _presetId,
      acceptUncoveredTracking: acceptUncovered,
    );
    VideoKitOutputSink? sink;
    _starting = true;
    try {
      sink = widget.sinkProvider == null
          ? widget.sink
          : await widget.sinkProvider!(request);
    } on Object {
      // The host's save dialog failed (e.g. no document UI): nothing starts;
      // the preset view stays so the user can try again.
      sink = null;
    } finally {
      _starting = false;
    }
    if (sink == null || !mounted) return;
    setState(() => _result = null);
    final r = await widget.project.export(request, sink);
    if (mounted) setState(() => _result = r);
  }

  /// Back to the preset view (after a failure or cancel).
  void reset() {
    setState(() {
      _result = null;
      _precheck = null;
    });
    unawaited(_check());
  }

  @override
  Widget build(BuildContext context) {
    final st = widget.project.state.value;
    final progress = st.export;
    final r = _result;
    final Widget body;
    if (st.phase == EditPhase.cancelling) {
      body = _cancelling(context);
    } else if (st.phase == EditPhase.exporting && progress != null) {
      body = _progress(context, progress, st);
    } else if (r is ExportSucceeded) {
      body = _success(context, r.media);
    } else if (r is ExportFailed) {
      body = _failed(context, r.error);
    } else if (r is ExportCancelled) {
      body = _cancelled(context, r.partialOutputRemoved);
    } else {
      body = _idle(context, st);
    }
    return Semantics(container: true, child: _lay(context, body));
  }

  String _viewKind() {
    final st = widget.project.state.value;
    if (st.phase == EditPhase.cancelling) return 'cancelling';
    if (st.phase == EditPhase.exporting && st.export != null) {
      return 'progress';
    }
    return _result?.runtimeType.toString() ?? 'idle';
  }

  /// Moves the [_Actions] of [body] below a scrolling content area.
  Widget _lay(BuildContext context, Widget body) {
    if (!widget.pinActions || body is! Column) return body;
    final actions = body.children.whereType<_Actions>().toList();
    if (actions.isEmpty) return body;
    final content = [
      for (final c in body.children)
        if (c is! _Actions) c,
    ];
    return LayoutBuilder(
      builder: (context, c) {
        if (!c.hasBoundedHeight) return body;
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: SingleChildScrollView(
                // TEST-R4 R4-04: each view (presets, progress, result)
                // starts at the top; the result never inherits the
                // previous scroll offset.
                key: ValueKey(_viewKind()),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  mainAxisSize: MainAxisSize.min,
                  children: content,
                ),
              ),
            ),
            SizedBox(height: VkTheme.of(context).dimensions.spacing12),
            ...actions,
          ],
        );
      },
    );
  }

  // --------------------------------------------------------------- idle --

  Widget _section(BuildContext context, String title) {
    final t = VkTheme.of(context);
    return Padding(
      padding: EdgeInsetsDirectional.only(
        top: t.dimensions.spacing16,
        bottom: t.dimensions.spacing8,
      ),
      child: Semantics(
        header: true,
        child: Text(
          title,
          style: t.typography.label.copyWith(color: t.colors.textSecondary),
        ),
      ),
    );
  }

  Widget _idle(BuildContext context, VideoKitEditState st) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final pre = _precheck;
    final presets = widget.presets.isEmpty
        ? [
            for (final id in ExportPresets.all)
              OutputFormat(
                presetId: id,
                container: 'mp4',
                videoCodec: 'video/avc',
                audioCodec: 'audio/mp4a-latm',
              ),
          ]
        : widget.presets;
    final current = presets.where((p) => p.presetId == _presetId).firstOrNull;
    final codes = {
      for (final e in pre?.problems ?? const <VideoKitStableError>[]) e.code,
    };
    final uncovered = pre?.uncoveredRanges ?? const <UncoveredRange>[];
    final hasAuto = st.masks.any((m) => m.type.isAutomatic);
    final other = [
      for (final e in pre?.problems ?? const <VideoKitStableError>[])
        if (e.code != ErrorCode.encoderUnavailable &&
            e.code != ErrorCode.outputCapabilityUnsupported &&
            e.code != ErrorCode.outputSpaceInsufficient &&
            e.code != ErrorCode.trackingLost)
          e,
    ];
    final need = pre?.estimate.sizeBytes ?? st.estimate.sizeBytes;
    final free = widget.sink.capabilities.knownFreeSpaceBytes;
    // J8: the precheck names the space to free (rounded up to 10 MB).
    final toFree = [
      for (final e in pre?.problems ?? const <VideoKitStableError>[])
        ?vkSpaceToFree(e),
    ].firstOrNull;
    final blocking =
        pre == null || codes.any((c) => c != ErrorCode.trackingLost);
    final coverageBlocks = uncovered.isNotEmpty;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        _section(context, s.text('exportPresets')),
        for (final p in presets)
          Padding(
            padding: EdgeInsetsDirectional.only(bottom: d.spacing8),
            child: _PresetRow(
              title: vkPresetLabel(s, p.presetId),
              detail: !p.available
                  ? s.text('presetUnavailable')
                  : p.maxLongEdge == null
                  ? s.text('presetOriginalDetail')
                  : s.presetLongEdge(p.maxLongEdge!),
              selected: p.presetId == _presetId,
              onPressed: p.available ? () => selectPreset(p.presetId) : null,
            ),
          ),
        if (current != null)
          Text(
            s.exportFormat(
              vkFormatLine(
                current.container,
                current.videoCodec,
                current.audioCodec,
              ),
            ),
            style: t.typography.body.copyWith(color: t.colors.textSecondary),
          ),
        // M4: the chosen concat path and why (after the export check).
        Padding(
          padding: EdgeInsetsDirectional.only(top: t.dimensions.spacing8),
          child: ConcatPathInfo(
            compatibility: ConcatCompatibility.of(
              widget.project.state.value.timeline,
              fastConcatCapable: widget.fastConcatCapable,
            ).withPrecheck(pre),
          ),
        ),
        _section(context, s.text('exportChecks')),
        if (pre == null)
          _CheckRow(title: s.text('checkRunning'), detail: null, ok: null)
        else ...[
          _CheckRow(
            title: s.text(
              codes.contains(ErrorCode.encoderUnavailable)
                  ? 'checkEncoderFail'
                  : 'checkEncoderOk',
            ),
            detail: current == null ? null : vkCodecName(current.videoCodec),
            ok: !codes.contains(ErrorCode.encoderUnavailable),
          ),
          _CheckRow(
            title: s.text('checkOutput'),
            detail: s.text(
              codes.contains(ErrorCode.outputCapabilityUnsupported)
                  ? 'checkOutputFail'
                  : 'checkOutputOk',
            ),
            ok: !codes.contains(ErrorCode.outputCapabilityUnsupported),
          ),
          _CheckRow(
            title: s.text('checkSpace'),
            detail: codes.contains(ErrorCode.outputSpaceInsufficient)
                ? (toFree == null
                      ? s.text('checkSpaceFail')
                      : s.checkSpaceFailSize(VkFormat.fileSize(s, toFree)))
                : need == null
                ? s.text('checkSpaceUnknown')
                : free == null
                ? s.checkSpaceNeed(VkFormat.fileSize(s, need))
                : s.checkSpaceValue(
                    VkFormat.fileSize(s, need),
                    VkFormat.fileSize(s, free),
                  ),
            ok: !codes.contains(ErrorCode.outputSpaceInsufficient),
          ),
          _CheckRow(
            title: s.text('checkCoverage'),
            detail: !hasAuto
                ? s.text('checkCoverageNone')
                : coverageBlocks
                ? s.checkCoverageFail(uncovered.length)
                : s.text('checkCoverageOk'),
            ok: !coverageBlocks,
          ),
          for (final e in other)
            _CheckRow(title: s.error(e.code), detail: null, ok: false),
        ],
        SizedBox(height: d.spacing16),
        Text(
          s.text('exportSafety'),
          style: t.typography.bodySmall.copyWith(color: t.colors.textSecondary),
        ),
        SizedBox(height: d.spacing16),
        _Actions([
          if (coverageBlocks && !blocking)
            VkButton(
              label: s.text('exportReviewCoverage'),
              onPressed: widget.onReviewCoverage == null
                  ? null
                  : () => widget.onReviewCoverage!(uncovered),
            )
          else
            VkButton(
              label: s.text('exportStart'),
              onPressed: blocking || coverageBlocks
                  ? null
                  : () => unawaited(start()),
            ),
        ]),
      ],
    );
  }

  // ----------------------------------------------------------- progress --

  Widget _progress(
    BuildContext context,
    ExportProgress p,
    VideoKitEditState st,
  ) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final hasTracking = st.masks.any((m) => m.type.isAutomatic);
    final stages = [
      for (final stage in ExportStage.values)
        if (stage != ExportStage.tracking ||
            hasTracking ||
            p.stage == ExportStage.tracking)
          stage,
    ];
    final current = stages.indexOf(p.stage);
    final total = st.timeline.durationUs;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        Semantics(
          header: true,
          child: Text(
            s.text('exporting'),
            style: t.typography.titleLarge.copyWith(
              color: t.colors.textPrimary,
            ),
          ),
        ),
        SizedBox(height: d.spacing16),
        if (widget.progressPreview case final preview?) ...[
          ClipRRect(
            borderRadius: BorderRadius.circular(d.cornerLarge),
            child: AspectRatio(aspectRatio: 16 / 9, child: preview),
          ),
          SizedBox(height: d.spacing16),
        ],
        for (final (i, stage) in stages.indexed)
          _StageRow(
            title: s.text(switch (stage) {
              ExportStage.preparing => 'stagePreparing',
              ExportStage.tracking => 'stageTracking',
              ExportStage.encoding => 'stageEncoding',
              ExportStage.verifying => 'stageVerifying',
              ExportStage.writing => 'stageWriting',
            }),
            state: i < current
                ? _StageState.done
                : (i == current ? _StageState.active : _StageState.waiting),
            fraction: i == current ? p.fraction : null,
            trailing: i == current && p.fraction != null
                ? [
                    VkFormat.percent(s, p.fraction!),
                    if (p.remainingUs != null)
                      s.stageRemaining(
                        VkFormat.durationSpoken(s, p.remainingUs!),
                      ),
                  ].join(' · ')
                : null,
            detail: i == current
                ? [
                    if (p.processedUs != null)
                      s.stageProcessed(
                        VkFormat.timecode(p.processedUs!),
                        VkFormat.timecode(total),
                      ),
                    if (p.outputBytes != null)
                      s.stageOutputSize(VkFormat.fileSize(s, p.outputBytes!)),
                  ].join(' · ')
                : null,
            isLast: i == stages.length - 1,
          ),
        SizedBox(height: d.spacing16),
        _InfoCard(text: s.text('exportNoPause')),
        SizedBox(height: d.spacing16),
        _Actions([
          VkButton(
            label: s.text('exportCancel'),
            variant: VkButtonVariant.danger,
            onPressed: p.cancellable
                ? () => unawaited(widget.project.cancelExport(p.exportId))
                : null,
          ),
        ]),
      ],
    );
  }

  Widget _cancelling(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Semantics(
          liveRegion: true,
          child: Text(
            s.text('exportCancelling'),
            textAlign: TextAlign.center,
            style: t.typography.title.copyWith(color: t.colors.textPrimary),
          ),
        ),
        SizedBox(height: t.dimensions.spacing16),
        _Actions([
          VkButton(
            label: s.text('exportCancel'),
            variant: VkButtonVariant.danger,
            onPressed: null,
          ),
        ]),
      ],
    );
  }

  // ------------------------------------------------------------ results --

  Widget _resultHeader(
    BuildContext context, {
    required IconData icon,
    required Color color,
    required Color container,
    required String title,
    String? subtitle,
  }) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: EdgeInsetsDirectional.all(d.spacing16),
          decoration: BoxDecoration(color: container, shape: BoxShape.circle),
          child: Icon(icon, size: d.icon24 * 1.5, color: color),
        ),
        SizedBox(height: d.spacing12),
        Semantics(
          header: true,
          liveRegion: true,
          child: Text(
            title,
            textAlign: TextAlign.center,
            style: t.typography.titleLarge.copyWith(
              color: t.colors.textPrimary,
            ),
          ),
        ),
        if (subtitle != null)
          Text(
            subtitle,
            textAlign: TextAlign.center,
            style: t.typography.body.copyWith(color: t.colors.textSecondary),
          ),
      ],
    );
  }

  Widget _cancelled(BuildContext context, bool removed) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        _resultHeader(
          context,
          icon: t.icons.info,
          color: t.colors.info,
          container: t.colors.infoContainer,
          title: s.text(removed ? 'exportCancelled' : 'exportCancelledPartial'),
        ),
        SizedBox(height: d.spacing16),
        _Actions([
          VkButton(label: s.text('exportRetry'), onPressed: reset),
          if (widget.onBackToEdit != null) ...[
            SizedBox(height: d.spacing8),
            VkButton(
              label: s.text('exportBackToEdit'),
              variant: VkButtonVariant.outline,
              onPressed: widget.onBackToEdit,
            ),
          ],
        ]),
      ],
    );
  }

  /// Next smaller available preset, for "改用 720p 重新导出".
  String? _smallerPreset() {
    final order = [
      ExportPresets.original,
      ExportPresets.p1080,
      ExportPresets.p720,
    ];
    final i = order.indexOf(_presetId);
    for (final id in order.skip(i + 1)) {
      final p = widget.presets.where((x) => x.presetId == id).firstOrNull;
      if (p == null ? widget.presets.isEmpty : p.available) return id;
    }
    return null;
  }

  Widget _failed(BuildContext context, VideoKitStableError e) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final smaller = _smallerPreset();
    final reduce =
        smaller != null &&
        (e.suggestedAction == SuggestedAction.reduceQuality ||
            e.code == ErrorCode.outputSpaceInsufficient ||
            e.code == ErrorCode.encoderUnavailable);
    // J8: with the missing space reported (`requiredBytes`, rounded up to
    // 10 MB) the hint names it; otherwise a generic hint without numbers.
    final String? suggestion;
    if (e.code == ErrorCode.outputSpaceInsufficient) {
      final toFree = vkSpaceToFree(e);
      suggestion = toFree == null
          ? s.text('exportSuggestFreeSpace')
          : s.exportSuggestFreeSpaceSize(VkFormat.fileSize(s, toFree));
    } else {
      suggestion = s.action(e.suggestedAction);
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        _resultHeader(
          context,
          icon: t.icons.warning,
          color: t.colors.error,
          container: t.colors.errorContainer,
          title: s.text('exportFailedTitle'),
          subtitle: s.error(e.code),
        ),
        SizedBox(height: d.spacing16),
        _InfoCard(
          children: [
            _CheckRow(
              title: s.text('exportImpactSource'),
              detail: null,
              ok: true,
            ),
            _CheckRow(
              title: s.text('exportImpactDiscarded'),
              detail: null,
              ok: true,
            ),
            if (suggestion != null)
              _CheckRow(title: suggestion, detail: null, ok: null),
          ],
        ),
        SizedBox(height: d.spacing8),
        Text(
          s.exportErrorCode(e.code.wireName),
          textAlign: TextAlign.center,
          style: t.typography.caption.copyWith(color: t.colors.textSecondary),
        ),
        SizedBox(height: d.spacing16),
        _Actions([
          if (reduce)
            VkButton(
              label: s.exportUseSmaller(vkPresetLabel(s, smaller)),
              onPressed: () {
                selectPreset(smaller);
                setState(() => _result = null);
              },
            )
          else
            VkButton(label: s.text('exportRetry'), onPressed: reset),
          if (widget.onBackToEdit != null) ...[
            SizedBox(height: d.spacing8),
            VkButton(
              label: s.text('exportBackToEdit'),
              variant: VkButtonVariant.outline,
              onPressed: widget.onBackToEdit,
            ),
          ],
        ]),
      ],
    );
  }

  Widget _success(BuildContext context, VideoKitExportedMedia m) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    // 04A K3: compare by code (`CODE` or `CODE:argument`); one line per
    // kind; unknown codes are not shown raw.
    final warnings = <String>{
      for (final w in m.warnings)
        ?switch (ExportWarnings.codeOf(w)) {
          ExportWarnings.boundaryAlignedToKeyframe => s.text('warnBoundary'),
          ExportWarnings.silenceInserted => s.text('warnSilence'),
          ExportWarnings.trackingCoverageAccepted => s.text('warnCoverage'),
          ExportWarnings.trackingIncomplete => s.text('warnTrackingIncomplete'),
          ExportWarnings.trackingLostRanges => s.text('warnTrackingLost'),
          ExportWarnings.fastConcatRejected => s.text('concatReasonEngine'),
          _ => null,
        },
    }.toList();
    final demo =
        m.isDemo ||
        ExportWarnings.has(m.warnings, ExportWarnings.demoNoRealFile);
    // Design page 21: resolution with orientation, the number of source
    // videos, and the warnings line (in the warning colour, "无" if none).
    final orientation = m.width > m.height
        ? s.text('summaryLandscape')
        : m.width < m.height
        ? s.text('summaryPortrait')
        : s.text('summarySquare');
    final sources = {
      for (final c in widget.project.state.value.timeline.clips) c.sourceId,
    }.length;
    Widget row(String k, String v, {Color? valueColor}) => MergeSemantics(
      child: Padding(
        padding: EdgeInsetsDirectional.symmetric(vertical: d.spacing8),
        // Design page 21: label at the start, value at the end.
        child: SizedBox(
          width: double.infinity,
          child: Wrap(
            spacing: d.spacing16,
            alignment: WrapAlignment.spaceBetween,
            children: [
              ConstrainedBox(
                constraints: BoxConstraints(minWidth: d.targetMin * 1.5),
                child: Text(
                  k,
                  style: t.typography.body.copyWith(
                    color: t.colors.textSecondary,
                  ),
                ),
              ),
              Text(
                v,
                style: t.typography.body.copyWith(
                  fontWeight: FontWeight.w600,
                  color: valueColor ?? t.colors.textPrimary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        _resultHeader(
          context,
          icon: t.icons.check,
          color: t.colors.success,
          container: t.colors.successContainer,
          title: s.text('exportDoneTitle'),
          subtitle: s.text('exportDoneDetail'),
        ),
        if (demo) ...[
          SizedBox(height: d.spacing12),
          Center(
            child: Container(
              padding: EdgeInsetsDirectional.symmetric(
                horizontal: d.spacing12,
                vertical: d.spacing4,
              ),
              decoration: BoxDecoration(
                color: t.colors.demo,
                borderRadius: BorderRadius.circular(d.cornerFull),
              ),
              child: Text(
                s.text('warnDemo'),
                style: t.typography.label.copyWith(color: t.colors.demoContent),
              ),
            ),
          ),
        ],
        SizedBox(height: d.spacing16),
        _InfoCard(
          children: [
            row(
              s.text('summaryFormat'),
              vkFormatLine(m.container, m.videoCodec, m.audioCodec),
            ),
            row(
              s.text('summaryResolution'),
              s.summaryResolutionValue(
                s.infoDimensionsValue(m.width, m.height),
                orientation,
              ),
            ),
            row(s.text('summaryDuration'), VkFormat.timecode(m.durationUs)),
            row(s.text('summarySize'), VkFormat.fileSize(s, m.sizeBytes)),
            if (sources > 0)
              row(s.text('summarySource'), s.summarySourceCount(sources)),
            row(
              s.text('summaryWarnings'),
              warnings.isEmpty
                  ? s.text('summaryNoWarnings')
                  : warnings.join('；'),
              valueColor: warnings.isEmpty ? null : t.colors.warning,
            ),
          ],
        ),
        // Host actions ("打开", "分享") stay secondary under the summary;
        // the one main button is "完成" (design page 21).
        if (widget.successActions != null) ...[
          SizedBox(height: d.spacing16),
          widget.successActions!(context, m),
        ],
        if (widget.onBackToEdit != null) ...[
          SizedBox(height: d.spacing16),
          _Actions([
            VkButton(
              label: s.text('exportDone'),
              onPressed: widget.onBackToEdit,
            ),
          ]),
        ],
      ],
    );
  }
}

class _PresetRow extends StatelessWidget {
  const _PresetRow({
    required this.title,
    required this.detail,
    required this.selected,
    required this.onPressed,
  });

  final String title;
  final String detail;
  final bool selected;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final enabled = onPressed != null;
    return Semantics(
      inMutuallyExclusiveGroup: true,
      checked: selected,
      button: true,
      enabled: enabled,
      label: title,
      value: detail,
      onTap: onPressed,
      child: ExcludeSemantics(
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(d.cornerMedium),
          child: Container(
            padding: EdgeInsetsDirectional.all(d.spacing12),
            decoration: BoxDecoration(
              color: selected
                  ? t.colors.primaryContainer
                  : t.colors.surfaceVariant,
              borderRadius: BorderRadius.circular(d.cornerMedium),
              border: Border.all(
                color: selected ? t.colors.primary : t.colors.surfaceVariant,
                width: d.borderWidth * 1.5,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  t.icons.resolve(selected ? 'radioon' : 'radiooff'),
                  color: selected
                      ? t.colors.primary
                      : (enabled
                            ? t.colors.textSecondary
                            : t.colors.disabledContent),
                ),
                SizedBox(width: d.spacing12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: t.typography.title.copyWith(
                          color: selected
                              ? t.colors.onPrimaryContainer
                              : (enabled
                                    ? t.colors.textPrimary
                                    : t.colors.disabledContent),
                        ),
                      ),
                      Text(
                        detail,
                        style: t.typography.bodySmall.copyWith(
                          color: selected
                              ? t.colors.onPrimaryContainer
                              : t.colors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Precheck row: ✓ / ! / neutral, title and detail.
class _CheckRow extends StatelessWidget {
  const _CheckRow({
    required this.title,
    required this.detail,
    required this.ok,
  });

  final String title;
  final String? detail;
  final bool? ok;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final good = ok ?? false;
    final color = ok == null
        ? t.colors.info
        : (good ? t.colors.success : t.colors.error);
    final container = ok == null
        ? t.colors.infoContainer
        : (good ? t.colors.successContainer : t.colors.errorContainer);
    return MergeSemantics(
      child: Semantics(
        value: ok == null
            ? null
            : s.text(good ? 'checkPassed' : 'checkProblem'),
        child: Padding(
          padding: EdgeInsetsDirectional.symmetric(vertical: d.spacing8),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: EdgeInsetsDirectional.all(d.spacing8),
                decoration: BoxDecoration(
                  color: container,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  ok == null
                      ? t.icons.info
                      : (good ? t.icons.check : t.icons.warning),
                  size: d.icon16,
                  color: color,
                ),
              ),
              SizedBox(width: d.spacing12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      // Design pages 20–21: check / impact rows lead with
                      // a body-size semibold title.
                      style: t.typography.body.copyWith(
                        fontWeight: FontWeight.w600,
                        color: t.colors.textPrimary,
                      ),
                    ),
                    if (detail != null)
                      Text(
                        detail!,
                        style: t.typography.bodySmall.copyWith(
                          color: t.colors.textSecondary,
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

enum _StageState { done, active, waiting }

class _StageRow extends StatelessWidget {
  const _StageRow({
    required this.title,
    required this.state,
    required this.fraction,
    required this.trailing,
    required this.detail,
    required this.isLast,
  });

  final String title;
  final _StageState state;
  final double? fraction;
  final String? trailing;
  final String? detail;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final active = state == _StageState.active;
    final done = state == _StageState.done;
    final dot = d.spacing24 + d.spacing8;
    final status = s.text(switch (state) {
      _StageState.done => 'stageDone',
      _StageState.active => 'stageInProgress',
      _StageState.waiting => 'stageWaiting',
    });
    return Semantics(
      container: true,
      label: title,
      value: [status, ?trailing].join(' · '),
      liveRegion: active,
      child: ExcludeSemantics(
        child: IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Column(
                children: [
                  Container(
                    width: dot,
                    height: dot,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: done ? t.colors.primary : t.colors.surface,
                      border: Border.all(
                        color: done || active
                            ? t.colors.primary
                            : t.colors.borderStrong,
                        width: d.focusRingWidth,
                      ),
                    ),
                    child: done
                        ? Icon(
                            t.icons.check,
                            size: d.icon16,
                            color: t.colors.onPrimary,
                          )
                        : (active
                              ? Padding(
                                  padding: EdgeInsetsDirectional.all(
                                    d.spacing4,
                                  ),
                                  child: CircularProgressIndicator(
                                    strokeWidth: d.pendingRingStroke,
                                    color: t.components.progress.indicator,
                                  ),
                                )
                              : null),
                  ),
                  if (!isLast)
                    Expanded(
                      child: Container(
                        width: d.focusRingWidth,
                        color: done ? t.colors.primary : t.colors.borderStrong,
                      ),
                    ),
                ],
              ),
              SizedBox(width: d.spacing12),
              Expanded(
                child: Padding(
                  padding: EdgeInsetsDirectional.only(bottom: d.spacing16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Full width so the percentage sits at the end (design
                      // page 20); wraps below the title at large text.
                      SizedBox(
                        width: double.infinity,
                        child: Wrap(
                          spacing: d.spacing8,
                          alignment: WrapAlignment.spaceBetween,
                          children: [
                            Text(
                              title,
                              // Design page 20: body size; the running stage
                              // is bold, waiting stages are grey.
                              style: t.typography.body.copyWith(
                                fontWeight: active
                                    ? FontWeight.w600
                                    : FontWeight.w400,
                                color: state == _StageState.waiting
                                    ? t.colors.textSecondary
                                    : t.colors.textPrimary,
                              ),
                            ),
                            if (trailing != null)
                              Text(
                                trailing!,
                                style: t.typography.body.copyWith(
                                  fontWeight: FontWeight.w600,
                                  color: t.colors.primary,
                                ),
                              ),
                          ],
                        ),
                      ),
                      Text(
                        detail?.isNotEmpty ?? false ? detail! : status,
                        style: t.typography.bodySmall.copyWith(
                          color: t.colors.textSecondary,
                        ),
                      ),
                      if (active) ...[
                        SizedBox(height: d.spacing8),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(d.cornerFull),
                          child: LinearProgressIndicator(
                            value: fraction,
                            minHeight: t.components.progress.height,
                            color: t.components.progress.indicator,
                            backgroundColor: t.components.progress.track,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({this.text, this.children});

  final String? text;
  final List<Widget>? children;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return Container(
      padding: EdgeInsetsDirectional.all(d.spacing16),
      decoration: BoxDecoration(
        color: t.colors.surfaceVariant,
        borderRadius: BorderRadius.circular(d.cornerLarge),
      ),
      child: text != null
          ? Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  t.icons.info,
                  size: d.icon20,
                  color: t.colors.textSecondary,
                ),
                SizedBox(width: d.spacing12),
                Expanded(
                  child: Text(
                    text!,
                    style: t.typography.bodySmall.copyWith(
                      color: t.colors.textSecondary,
                    ),
                  ),
                ),
              ],
            )
          : Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: children ?? const [],
            ),
    );
  }
}

/// Main buttons of a panel view; kept at the bottom when
/// [ExportPanel.pinActions] is set.
class _Actions extends StatelessWidget {
  const _Actions(this.children);

  final List<Widget> children;

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    mainAxisSize: MainAxisSize.min,
    children: children,
  );
}
