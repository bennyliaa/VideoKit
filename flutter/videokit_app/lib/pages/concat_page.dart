import 'dart:async';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart' as intl;
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../entitlement/entitlement_gate.dart';
import '../entitlement/entitlement_service.dart';
import '../avatar/avatar_pick_page.dart';
import '../history/history_entry.dart';
import '../l10n/app_text.dart';
import '../library/library_models.dart';
import '../projects/project_store.dart';
import 'launcher.dart';
import 'player_page.dart';

/// UI-06 editor for several videos ("拼接为一个视频"): one source and one
/// full-length clip per record. M4: the project is saved as a snapshot when
/// the user leaves ("最近工程") and can be restored from it; "添加视频"
/// picks more videos.
class ConcatPage extends StatefulWidget {
  /// Creates the page for new [entries], or to restore [restore].
  const ConcatPage({
    super.key,
    this.entries = const [],
    this.restore,
    this.libraryTarget,
  });

  /// Video records (new project).
  final List<HistoryEntry> entries;

  /// Opened from the media library: the export is saved back into this
  /// folder and the project is not kept in "最近工程" (APP-LIB-A1).
  final LibraryExportTarget? libraryTarget;

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

  /// The Kit's optional avatar tools (04A E6), null when it has none.
  VideoKitAvatarTools? get _avatarTools => switch (_scope.backend.videoKit) {
    final VideoKitAvatarTools tools => tools,
    _ => null,
  };
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

  /// 04A E7 Q3 / R8: the copy notice was shown.
  bool savedAsCopyNoticed = false;

  /// Saves the project; R8 may redirect it to a copy (the original was
  /// written by a newer App) → a one-time notice.
  Future<void> _save(VideoKitEditProject p, {bool strict = false}) async {
    // REQ-APP-10: private media never show up in "最近工程".
    if (widget.libraryTarget != null) return;
    final saved = await _scope.projects.save(projectId, p, strict: strict);
    if (saved == projectId || savedAsCopyNoticed || !mounted) return;
    savedAsCopyNoticed = true;
    final a = AppText.of(context);
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(a(a.l.projectSavedAsCopy))));
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _scope = AppScope.of(context);
    if (_started) return;
    _started = true;
    // REQ-APP-15: editing is a paid feature (every way in: concat, recent
    // projects, the export notice, the library). Projects are kept either
    // way; a denied user just goes back.
    if (_scope.entitlements.allows(AppFeature.edit)) {
      unawaited(_open());
    } else {
      WidgetsBinding.instance.addPostFrameCallback((_) async {
        if (!mounted) return;
        await ensureEntitled(context, AppFeature.edit);
        if (mounted) Navigator.of(context).maybePop();
      });
    }
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
    opened.state.addListener(_onProjectState);
    // REQ-ED-07: built-in avatars come from the Kit (04A E5 5).
    final tools = _avatarTools;
    if (tools != null) unawaited(_scope.avatars.loadBuiltins(tools));
    // M4-A2: restore migrated an older schema; save the migrated form so
    // the entry is current from now on.
    if (widget.restore?.needsMigration ?? false) {
      unawaited(_save(opened));
    }
  }

  /// Library export in progress: the private file and its name.
  ({String path, String name, String mime})? _libraryExport;

  /// "另存为" right before the export starts (REQ-APP-03 export part).
  /// From the media library the export goes straight into a private file
  /// of the current folder instead (REQ-APP-09, no system dialog).
  Future<VideoKitOutputSink?> _prepareSink(VideoKitExportRequest request) async {
    // REQ-APP-15: export is a paid feature; denied = no sink (cancelled).
    if (!await ensureEntitled(context, AppFeature.export)) return null;
    if (!mounted) return null;
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
    if (widget.libraryTarget != null) {
      final dir = await _scope.backend.library.mediaDirectory();
      final path = '$dir/${_scope.library.newId('item')}.$ext';
      _libraryExport = (
        path: path,
        name: '${a.l.exportFileName(stamp)}.$ext',
        mime: mime,
      );
      return _scope.backend.prepareLibraryExport(path: path);
    }
    return _scope.backend
        .prepareExport(
          suggestedName: '${a.l.exportFileName(stamp)}.$ext',
          mimeType: mime,
        )
        .then((sink) async {
          // M6-A1: remembered until the export ends, so a kill during it
          // is reported at the next start.
          if (sink != null) {
            await _save(project!);
            await _scope.exportJournal.begin(
              _scope.projects.resolveId(projectId),
            );
          }
          return sink;
        });
  }

  /// M6-A1: the export ended (any way) → nothing to report later.
  void _onProjectState() {
    final phase = project?.state.value.phase;
    final lib = _libraryExport;
    if (lib != null &&
        (phase == EditPhase.completed ||
            phase == EditPhase.failed ||
            phase == EditPhase.cancelled)) {
      _libraryExport = null;
      unawaited(_finishLibraryExport(lib, phase == EditPhase.completed));
      return;
    }
    if (widget.libraryTarget != null) return;
    if (phase == EditPhase.completed ||
        phase == EditPhase.failed ||
        phase == EditPhase.cancelled) {
      unawaited(_scope.exportJournal.end(_scope.projects.resolveId(projectId)));
    }
  }

  /// REQ-APP-09: a finished export becomes a library item of the folder;
  /// a failed or cancelled one leaves no file.
  Future<void> _finishLibraryExport(
    ({String path, String name, String mime}) lib,
    bool ok,
  ) async {
    final platform = _scope.backend.library;
    final target = widget.libraryTarget!;
    if (!ok) {
      await platform.delete(lib.path);
      return;
    }
    final probed = await platform.probe(lib.path, MediaKind.video);
    final dir = await platform.mediaDirectory();
    final id = lib.path.split('/').last.split('.').first;
    final thumb = '$dir/thumbs/$id.jpg';
    final thumbOk = await platform.thumbnail(lib.path, MediaKind.video, thumb);
    await _scope.library.addItem(
      LibraryItem(
        id: id,
        path: lib.path,
        displayName: lib.name,
        kind: MediaKind.video,
        importedAtEpochMs: _scope.history.now().millisecondsSinceEpoch,
        folderId: target.folderId,
        mimeType: lib.mime,
        durationUs: probed?.durationUs,
        width: probed?.width,
        height: probed?.height,
        thumbnailPath: thumbOk ? thumb : null,
      ),
    );
    if (!mounted) return;
    final a = AppText.of(context);
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(content: Text(a(a.l.libraryExportSaved(target.folderName)))),
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
    if (p != null) await _save(p);
    if (mounted) Navigator.of(context).pop();
  }

  @override
  void dispose() {
    project?.state.removeListener(_onProjectState);
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
          onAutosave: () => _save(p, strict: true),
          // REQ-ED-07 (04A E6 5): the App's own avatar pages; hidden when
          // the Kit has no avatar tools.
          onRequestAvatar: _avatarTools == null
              ? null
              : (request) => AvatarPickPage.open(
                  context,
                  tools: _avatarTools!,
                  currentToken: request.currentToken,
                ),
          avatarBuilder: (context, token) => ListenableBuilder(
            listenable: _scope.avatars,
            builder: (context, _) => switch (_scope.avatars.image(token)) {
              null => const SizedBox.shrink(),
              final image => Image(
                image: image,
                fit: BoxFit.contain,
                gaplessPlayback: true,
              ),
            },
          ),
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
