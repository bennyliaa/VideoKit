import 'dart:async';

import 'package:flutter/material.dart';
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
              presets: _presets,
              title: a(a.l.concatTitle(widget.entries.length)),
              pictureBuilder: _scope.backend.pictureBuilder,
              onBack: () => Navigator.of(context).maybePop(),
            ),
    );
  }
}
