import 'dart:async';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart' as intl;
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import '../l10n/app_text.dart';
import '../projects/project_store.dart';
import 'launcher.dart';

/// UI-06 editor for several videos ("拼接为一个视频"): one source and one
/// full-length clip per record. M4: the project is saved as a snapshot when
/// the user leaves ("最近工程") and can be restored from it; "添加视频"
/// picks more videos.
class ConcatPage extends StatefulWidget {
  /// Creates the page for new [entries], or to restore [restore].
  const ConcatPage({super.key, this.entries = const [], this.restore});

  /// Video records (new project).
  final List<HistoryEntry> entries;

  /// Saved project to reopen.
  final RecentProject? restore;

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
  bool _leaving = false;

  /// Restoring failed (shown instead of the editor).
  bool restoreFailed = false;

  /// ID under which the project is saved.
  late final String projectId = widget.restore?.id ?? _scope.projects.newId();

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
    final config = EditProjectConfig(debugLabel: 'app-concat');
    final VideoKitEditProject p;
    final restore = widget.restore;
    if (restore != null) {
      try {
        p = await _scope.backend.videoKit.restoreEditProject(
          restore.snapshot,
          config,
        );
      } on VideoKitException {
        if (mounted) setState(() => restoreFailed = true);
        return;
      }
    } else {
      p = await _scope.backend.videoKit.createEditProject(config);
      for (final e in widget.entries) {
        await _add(p, e);
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

  /// "添加视频": more videos at the end of the timeline.
  Future<void> addVideos() async {
    final p = project;
    if (p == null) return;
    final picked = await _scope.backend.picker.pick(
      context,
      kinds: const {MediaKind.video},
    );
    for (final m in picked) {
      final e = await MediaLauncher.entryFor(_scope, m);
      await _add(p, e);
    }
  }

  Future<void> _add(VideoKitEditProject p, HistoryEntry e) async {
    final src = await p.addSource(_scope.backend.sourceFor(e));
    final probe = p.state.value.timeline.sourceById(src.sourceId)?.probe;
    if (probe != null && probe.durationUs > 0) {
      await p.apply(AddClip(src.sourceId, 0, probe.durationUs));
    }
  }

  /// Saves the project ("最近工程") and leaves.
  Future<void> leave() async {
    if (_leaving) return;
    _leaving = true;
    final p = project;
    if (p != null) await _scope.projects.save(projectId, p);
    if (mounted) Navigator.of(context).pop();
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
    final Widget body;
    if (restoreFailed) {
      body = SafeArea(
        child: VideoKitStateView(
          model: StateViewModel(
            kind: StateViewKind.error,
            iconName: 'warning',
            titleText: a(a.l.recentProjectRestoreFailed),
          ),
        ),
      );
    } else if (p == null) {
      body = Center(
        child: CircularProgressIndicator(
          color: t.components.progress.indicator,
        ),
      );
    } else {
      body = ValueListenableBuilder<VideoKitEditState>(
        valueListenable: p.state,
        builder: (context, st, _) => VideoKitEditor(
          project: p,
          sink: _scope.backend.exportSink,
          sinkProvider: _prepareSink,
          presets: _presets,
          title: a(a.l.concatTitle(st.timeline.sources.length)),
          pictureBuilder: _scope.backend.pictureBuilder,
          onBack: () => unawaited(leave()),
          onPickSourcesRequested: () => unawaited(addVideos()),
        ),
      );
    }
    return PopScope(
      canPop: restoreFailed,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) unawaited(leave());
      },
      child: Scaffold(backgroundColor: t.colors.background, body: body),
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
