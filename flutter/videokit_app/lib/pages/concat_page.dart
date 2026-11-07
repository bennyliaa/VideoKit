import 'dart:async';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart' as intl;
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import '../l10n/app_text.dart';

/// UI-06 editor for several videos ("拼接为一个视频"): one source and one
/// full-length clip per record.
class ConcatPage extends StatefulWidget {
  /// Creates the page.
  const ConcatPage({super.key, required this.entries});

  /// Video records.
  final List<HistoryEntry> entries;

  @override
  State<ConcatPage> createState() => ConcatPageState();
}

/// State (public for tests).
class ConcatPageState extends State<ConcatPage> {
  /// Project once prepared.
  VideoKitEditProject? project;
  List<OutputFormat> _presets = const [];
  late AppScope _scope;
  bool _started = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _scope = AppScope.of(context);
    if (_started) return;
    _started = true;
    unawaited(_open());
  }

  Future<void> _open() async {
    final presets = await _scope.backend.presets();
    final p = await _scope.backend.videoKit.createEditProject(
      EditProjectConfig(debugLabel: 'app-concat'),
    );
    for (final e in widget.entries) {
      final src = await p.addSource(_scope.backend.sourceFor(e));
      final probe = p.state.value.timeline.sourceById(src.sourceId)?.probe;
      if (probe != null && probe.durationUs > 0) {
        await p.apply(AddClip(src.sourceId, 0, probe.durationUs));
      }
    }
    if (!mounted) {
      await p.close();
      return;
    }
    setState(() {
      project = p;
      _presets = presets;
    });
  }

  /// "另存为" right before the export starts (REQ-APP-03 export part).
  Future<VideoKitOutputSink?> _prepareSink(VideoKitExportRequest request) {
    final a = AppText.of(context);
    final container = _presets
        .where((p) => p.presetId == request.presetId)
        .map((p) => p.container)
        .firstOrNull;
    final (ext, mime) = exportFileType(container);
    final stamp = intl.DateFormat(
      'yyyyMMdd_HHmmss',
      'en',
    ).format(_scope.history.now());
    return _scope.backend.prepareExport(
      suggestedName: '${a.l.exportFileName(stamp)}.$ext',
      mimeType: mime,
    );
  }

  @override
  void dispose() {
    unawaited(project?.close());
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final p = project;
    return Scaffold(
      backgroundColor: t.colors.background,
      body: p == null
          ? Center(
              child: CircularProgressIndicator(
                color: t.components.progress.indicator,
              ),
            )
          : VideoKitEditor(
              project: p,
              sink: _scope.backend.exportSink,
              sinkProvider: _prepareSink,
              presets: _presets,
              title: a(a.l.concatTitle(widget.entries.length)),
              pictureBuilder: _scope.backend.pictureBuilder,
              onBack: () => Navigator.of(context).maybePop(),
            ),
    );
  }
}

/// File extension and MIME type of an output [container] (`mp4` default).
(String, String) exportFileType(String? container) =>
    switch (container?.toLowerCase()) {
      'webm' => ('webm', 'video/webm'),
      'mkv' || 'matroska' => ('mkv', 'video/x-matroska'),
      '3gp' || '3gpp' => ('3gp', 'video/3gpp'),
      _ => ('mp4', 'video/mp4'),
    };
