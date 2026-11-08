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
import 'player_page.dart';

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

  /// M4-A2: the snapshot is from a newer module schema
  /// (`UNSUPPORTED_SNAPSHOT_VERSION`); the saved entry is kept so a newer
  /// App can still open it.
  bool restoreTooNew = false;

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

  /// TEST-R3 R3-02: the Kit has no edit engine yet (`EDITING_NOT_AVAILABLE`,
  /// native editing comes after S3): shown as "暂不支持" with a way back.
  bool notAvailable = false;

  /// Opening failed for another reason (or never finished): error + back.
  bool openFailed = false;

  /// Whether [e] means the Kit cannot edit at all (R3-02).
  static bool isEditingNotAvailable(Object e) =>
      e is VideoKitException &&
      e.error.diagnostic == editingNotAvailableDiagnostic;

  /// Diagnostic the Kits use while the edit engine is missing.
  static const String editingNotAvailableDiagnostic = 'EDITING_NOT_AVAILABLE';

  Future<void> _open() async {
    // R3-02: every failure, including one that never answers, ends in a
    // final state with a back button; the page never stays on a spinner.
    VideoKitEditProject? p;
    try {
      await Future(() async {
        final presets = await _scope.backend.presets();
        final config = EditProjectConfig(debugLabel: 'app-concat');
        final restore = widget.restore;
        if (restore != null) {
          p = await _scope.backend.videoKit.restoreEditProject(
            restore.snapshot,
            config,
          );
        } else {
          final created = await _scope.backend.videoKit.createEditProject(
            config,
          );
          p = created;
          for (final e in widget.entries) {
            await _add(created, e);
          }
        }
        _presets = presets;
      }).timeout(PlayerPage.defaultOpenTimeout);
    } on Object catch (e) {
      final opened = p;
      if (opened != null) unawaited(opened.close());
      if (!mounted) return;
      setState(() {
        if (isEditingNotAvailable(e)) {
          notAvailable = true;
        } else if (widget.restore != null) {
          restoreFailed = true;
          restoreTooNew =
              e is VideoKitException &&
              e.error.code == ErrorCode.unsupportedSnapshotVersion;
        } else {
          openFailed = true;
        }
      });
      return;
    }
    final opened = p!;
    if (!mounted) {
      await opened.close();
      return;
    }
    setState(() => project = opened);
    // M4-A2: restore migrated an older schema; save the migrated form so
    // the entry is current from now on.
    if (widget.restore?.needsMigration ?? false) {
      unawaited(_scope.projects.save(projectId, opened));
    }
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
    final failed = restoreFailed || notAvailable || openFailed;
    if (failed) {
      // R3-02: UI-09 state (short title + detail) under a bar with "back".
      final model = notAvailable
          ? StateViewModel(
              kind: StateViewKind.error,
              iconName: 'info',
              titleText: a(a.l.editingUnavailableTitle),
              detailText: a(a.l.editingUnavailableDetail),
            )
          : StateViewModel(
              kind: StateViewKind.error,
              iconName: 'warning',
              titleText: a(
                restoreTooNew
                    ? a.l.recentProjectTooNew
                    : restoreFailed
                    ? a.l.recentProjectRestoreFailed
                    : a.l.openFailedTitle,
              ),
              detailText: restoreFailed ? null : a(a.l.openFailedDetail),
            );
      body = SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: EdgeInsetsDirectional.all(t.dimensions.spacing8),
              child: Align(
                alignment: AlignmentDirectional.centerStart,
                child: VkIconButton(
                  icon: t.icons.resolve('back'),
                  semanticLabel: VkStrings.of(context).text('playerBack'),
                  onPressed: () => Navigator.of(context).maybePop(),
                ),
              ),
            ),
            Expanded(child: VideoKitStateView(model: model)),
          ],
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
          // Design page 15 (UI-AUDIT-A3): saved 2 s after each edit into
          // "最近工程"; a failed write shows "未保存" with retry.
          onAutosave: () => _scope.projects.save(projectId, p, strict: true),
        ),
      );
    }
    return PopScope(
      canPop: restoreFailed || notAvailable || openFailed,
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
