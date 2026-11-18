import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../entitlement/entitlement_gate.dart';
import '../entitlement/entitlement_service.dart';
import '../l10n/app_text.dart';
import '../pages/concat_page.dart';
import 'library_dialogs.dart';
import 'library_import_sheet.dart';
import 'library_media.dart';
import 'library_models.dart';
import 'library_settings_page.dart';
import 'library_store.dart';
import 'library_transfer_sheet.dart';

/// The media library (design pages 26–27, REQ-APP-09/12/13): folder bar
/// (beside the list on tablets and in landscape, a drawer from the start
/// edge on phones in portrait), "全部 / 视频 / 图片", paged grid with the
/// range and total, import, folder and item actions.
class LibraryPage extends StatefulWidget {
  /// Creates the page.
  const LibraryPage({super.key});

  /// Width from which the folder bar sits beside the list.
  static double sideBySideWidth(VideoKitThemeData t) => t.dimensions.targetMin * 12;

  @override
  State<LibraryPage> createState() => LibraryPageState();
}

/// State (public for tests).
class LibraryPageState extends State<LibraryPage> {
  /// Folder shown.
  LibraryScope scope = const AllMedia();

  /// Type filter.
  LibraryFilter filter = LibraryFilter.all;

  /// 1-based page.
  int page = 1;

  /// Folder bar beside the list (wide layouts); null = the setting.
  bool? folderBarShown;

  final GlobalKey<ScaffoldState> _scaffold = GlobalKey();

  LibraryStore get _store => AppScope.of(context).library;

  /// Name of [s] for titles.
  String scopeName(AppText a, LibraryScope s) => switch (s) {
    AllMedia() => a(a.l.libraryAllMedia),
    Unsorted() => a(a.l.libraryUnsorted),
    InFolder(:final folderId) =>
      _store.folderById(folderId)?.name ?? a(a.l.libraryUnsorted),
  };

  /// Folder new imports and exports go to (null = "未分类").
  String? get targetFolderId => switch (scope) {
    InFolder(:final folderId) => folderId,
    _ => null,
  };

  void _select(LibraryScope s) => setState(() {
    scope = s;
    page = 1;
    _clearItemSelection();
  });

  void _setFilter(LibraryFilter f) => setState(() {
    filter = f;
    page = 1;
    _clearItemSelection();
  });

  // ---------------------------------------------- selection (REQ-APP-13) --

  /// Media selection mode.
  bool selecting = false;

  /// Selected item IDs (when not [allSelected]).
  final Set<String> selectedItems = {};

  /// "全选": the whole folder and filter, every page (FT01A-19).
  bool allSelected = false;

  /// Folder selection mode (folder bar / drawer "选择").
  bool selectingFolders = false;

  /// Selected folder IDs.
  final Set<String> selectedFolders = {};

  void _clearItemSelection() {
    selectedItems.clear();
    allSelected = false;
  }

  /// Enters or leaves media selection.
  void setSelecting(bool on) => setState(() {
    selecting = on;
    selectingFolders = false;
    selectedFolders.clear();
    _clearItemSelection();
  });

  /// Enters or leaves folder selection.
  void setSelectingFolders(bool on) => setState(() {
    selectingFolders = on;
    selecting = false;
    _clearItemSelection();
    selectedFolders.clear();
  });

  /// Toggles one item; leaving "全选" keeps every other item selected.
  void toggleItem(String id) => setState(() {
    if (allSelected) {
      allSelected = false;
      selectedItems
        ..clear()
        ..addAll(_store.itemsIn(scope, filter).map((i) => i.id));
    }
    if (!selectedItems.remove(id)) selectedItems.add(id);
  });

  /// "全选" / "全不选" of the whole folder (all pages).
  void toggleAll() => setState(() {
    final everything = _store.itemsIn(scope, filter).length;
    final full = allSelected || selectedItems.length == everything;
    selectedItems.clear();
    allSelected = !full && everything > 0;
  });

  /// Toggles one folder.
  void toggleFolder(String id) => setState(() {
    if (!selectedFolders.remove(id)) selectedFolders.add(id);
  });

  /// All folders / none.
  void toggleAllFolders() => setState(() {
    final all = _store.folders.map((f) => f.id).toSet();
    if (selectedFolders.length == all.length) {
      selectedFolders.clear();
    } else {
      selectedFolders
        ..clear()
        ..addAll(all);
    }
  });

  /// Whether item [id] is selected.
  bool isItemSelected(String id) => allSelected || selectedItems.contains(id);

  /// The items the batch actions work on.
  List<LibraryItem> get selection {
    if (selectingFolders) {
      return [
        for (final i in _store.items)
          if (selectedFolders.contains(i.folderId)) i,
      ];
    }
    if (allSelected) return _store.itemsIn(scope, filter);
    return [
      for (final i in _store.items)
        if (selectedItems.contains(i.id)) i,
    ];
  }

  /// Number shown as "已选 N 项".
  int get selectionCount => selection.length;

  Future<void> _afterBatch() async {
    if (!mounted) return;
    setState(() {
      selecting = false;
      selectingFolders = false;
      selectedFolders.clear();
      _clearItemSelection();
    });
  }

  /// Batch "移动": into another library folder (or 未分类).
  Future<void> batchMove() async {
    final items = selection;
    if (items.isEmpty) return;
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    const unsorted = '\u0000unsorted';
    final target = await showModalBottomSheet<String>(
      context: context,
      backgroundColor: t.colors.surface,
      builder: (context) => _ActionSheet(
        title: a(a.l.libraryMoveTitle),
        actions: [
          for (final f in _store.folders)
            if (!selectedFolders.contains(f.id))
              (id: f.id, label: f.name, danger: false),
          (id: unsorted, label: a(a.l.libraryUnsorted), danger: false),
        ],
      ),
    );
    if (target == null) return;
    await _store.moveItems(
      items.map((i) => i.id),
      target == unsorted ? null : target,
    );
    await _afterBatch();
  }

  /// Batch "导出到相册".
  Future<void> batchExport() async {
    final r = await exportToGallery(context, selection);
    if (r != null) await _afterBatch();
  }

  /// Batch "移动到文件夹".
  Future<void> batchMoveOut() async {
    final r = await moveOut(context, selection);
    if (r != null) await _afterBatch();
  }

  /// Batch "删除" (confirmed; folders ask what happens to their media).
  Future<void> batchDelete() async {
    final a = AppText.of(context);
    if (selectingFolders) {
      final ids = selectedFolders.toList();
      if (ids.isEmpty) return;
      final count = selection.length;
      final how = await confirmDeleteFolder(
        context,
        name: ids.length == 1
            ? _store.folderById(ids.single)?.name ?? ''
            : a(a.l.libraryDeleteFoldersTitle(ids.length)),
        count: count,
        multiple: ids.length > 1,
      );
      if (how == null) return;
      for (final id in ids) {
        await _store.deleteFolder(
          id,
          deleteMedia: how == FolderDeleteChoice.deleteMedia,
        );
      }
      if (scope case InFolder(:final folderId) when ids.contains(folderId)) {
        scope = const AllMedia();
      }
      await _afterBatch();
      return;
    }
    final items = selection;
    if (items.isEmpty) return;
    final ok = await confirmDanger(
      context,
      title: a(a.l.libraryDeleteSelectedTitle(items.length)),
      body: a(a.l.libraryDeleteSelectedBody),
      action: a(a.l.libraryDelete),
    );
    if (!ok) return;
    await _store.deleteItems(items.map((i) => i.id));
    await _afterBatch();
  }

  /// Goes to page [p] (clamped when shown).
  void goToPage(int p) => setState(() => page = p);

  /// Shows or hides the folder bar beside the list.
  void setFolderBarShown(bool shown) =>
      setState(() => folderBarShown = shown);

  // ------------------------------------------------------------ actions --

  /// "导入": files, or a whole folder (REQ-APP-14).
  Future<void> importMedia() async {
    // REQ-APP-15 (final split): the private library is free.
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final how = await showModalBottomSheet<String>(
      context: context,
      backgroundColor: t.colors.surface,
      builder: (context) => _ActionSheet(
        title: a(a.l.libraryImport),
        actions: [
          (id: 'files', label: a(a.l.libraryImportFiles), danger: false),
          (id: 'folder', label: a(a.l.libraryImportFolder), danger: false),
        ],
      ),
    );
    if (!mounted || how == null) return;
    if (how == 'folder') {
      await importFolder(context);
      return;
    }
    await importFiles();
  }

  /// "选择视频和图片" into the current folder.
  Future<void> importFiles() async {
    final a = AppText.of(context);
    await pickAndImport(
      context,
      folderId: targetFolderId,
      folderName: targetFolderId == null
          ? a(a.l.libraryUnsorted)
          : scopeName(a, scope),
    );
  }

  Future<void> newFolder() async {
    final a = AppText.of(context);
    final name = await askFolderName(
      context,
      store: _store,
      title: a(a.l.libraryNewFolder),
      action: a(a.l.libraryCreate),
    );
    if (name == null || !mounted) return;
    final f = await _store.createFolder(name);
    _select(InFolder(f.id));
  }

  Future<void> folderActions(LibraryFolder f) async {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final choice = await showModalBottomSheet<String>(
      context: context,
      backgroundColor: t.colors.surface,
      builder: (context) => _ActionSheet(
        title: a(a.l.libraryQuoted(f.name)),
        actions: [
          (id: 'rename', label: a(a.l.libraryRename), danger: false),
          (id: 'delete', label: a(a.l.libraryDelete), danger: true),
        ],
      ),
    );
    if (!mounted) return;
    switch (choice) {
      case 'rename':
        final name = await askFolderName(
          context,
          store: _store,
          title: a(a.l.libraryRenameTitle(f.name)),
          action: a(a.l.librarySave),
          initial: f.name,
          exceptId: f.id,
        );
        if (name != null) await _store.renameFolder(f.id, name);
      case 'delete':
        final count = _store.countIn(InFolder(f.id));
        final how = await confirmDeleteFolder(
          context,
          name: f.name,
          count: count,
        );
        if (how == null) return;
        await _store.deleteFolder(
          f.id,
          deleteMedia: how == FolderDeleteChoice.deleteMedia,
        );
        if (scope == InFolder(f.id)) _select(const AllMedia());
    }
  }

  Future<void> itemActions(LibraryItem item, List<LibraryItem> pageItems) async {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final choice = await showModalBottomSheet<String>(
      context: context,
      backgroundColor: t.colors.surface,
      builder: (context) => _ActionSheet(
        title: item.displayName,
        actions: [
          (id: 'open', label: a(a.l.libraryOpen), danger: false),
          if (!item.isImage)
            (id: 'edit', label: a(a.l.libraryEdit), danger: false),
          (id: 'move', label: a(a.l.libraryMoveTo), danger: false),
          (id: 'delete', label: a(a.l.libraryRemoveItem), danger: true),
        ],
      ),
    );
    if (!mounted) return;
    switch (choice) {
      case 'open':
        await openLibraryItem(context, item, pageItems: pageItems);
      case 'edit':
        await edit(item);
      case 'move':
        await moveItem(item);
      case 'delete':
        final ok = await confirmDanger(
          context,
          title: a(a.l.libraryRemoveItemTitle(item.displayName)),
          body: a(a.l.libraryRemoveItemBody),
          action: a(a.l.libraryDelete),
        );
        if (ok) await _store.deleteItems([item.id]);
    }
  }

  /// "移动到…": another folder or "未分类" (FT01A-11).
  Future<void> moveItem(LibraryItem item) async {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    const unsorted = '\u0000unsorted';
    final target = await showModalBottomSheet<String>(
      context: context,
      backgroundColor: t.colors.surface,
      builder: (context) => _ActionSheet(
        title: a(a.l.libraryMoveTitle),
        actions: [
          for (final f in _store.folders)
            if (f.id != item.folderId)
              (id: f.id, label: f.name, danger: false),
          if (item.folderId != null)
            (id: unsorted, label: a(a.l.libraryUnsorted), danger: false),
        ],
      ),
    );
    if (target == null) return;
    await _store.moveItems([item.id], target == unsorted ? null : target);
  }

  /// Edits a video; the export goes back to this folder (REQ-APP-09).
  Future<void> edit(LibraryItem item) async {
    // REQ-APP-15: editing is paid (the library itself is free).
    if (!await ensureEntitled(context, AppFeature.edit) || !mounted) return;
    final a = AppText.of(context);
    return Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => ConcatPage(
          entries: [libraryEntry(item)],
          libraryTarget: LibraryExportTarget(
            folderId: item.folderId,
            folderName: item.folderId == null
                ? a(a.l.libraryUnsorted)
                : _store.folderById(item.folderId!)?.name ??
                      a(a.l.libraryUnsorted),
          ),
        ),
      ),
    );
  }

  // -------------------------------------------------------------- build --

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final scopeData = AppScope.of(context);
    final store = scopeData.library;
    store.reservedNames = {a(a.l.libraryAllMedia), a(a.l.libraryUnsorted)};
    return ListenableBuilder(
      listenable: Listenable.merge([store, scopeData.libraryLock]),
      builder: (context, _) {
        // A folder deleted elsewhere: back to everything.
        if (scope case InFolder(:final folderId)
            when store.folderById(folderId) == null) {
          scope = const AllMedia();
        }
        final settings = scopeData.libraryLock.value;
        final size = MediaQuery.sizeOf(context);
        final wide = size.width >= LibraryPage.sideBySideWidth(t);
        final barShown = folderBarShown ?? settings.showFolderBar;
        final result = store.query(
          scope,
          filter,
          page: page,
          pageSize: settings.pageSize,
        );
        page = result.page;
        final folderBar = _FolderBar(
          state: this,
          drawer: !wide,
          onClose: () {
            if (wide) {
              setFolderBarShown(false);
            } else {
              Navigator.of(context).maybePop();
            }
          },
        );
        final list = _ListArea(
          state: this,
          result: result,
          wide: wide,
          folderBarHidden: wide && !barShown,
        );
        return Scaffold(
          key: _scaffold,
          backgroundColor: t.colors.background,
          drawer: wide
              ? null
              : Drawer(
                  backgroundColor: t.colors.surface,
                  child: SafeArea(child: folderBar),
                ),
          body: SafeArea(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (selecting)
                  _SelectionHeader(
                    count: selectionCount,
                    all: allSelected,
                    onAll: toggleAll,
                    onClose: () => setSelecting(false),
                  )
                else
                  _TopBar(
                    state: this,
                    wide: wide,
                    protected: settings.protected,
                    onOpenDrawer: () => _scaffold.currentState?.openDrawer(),
                  ),
                Expanded(
                  child: wide
                      ? Padding(
                          padding: EdgeInsetsDirectional.fromSTEB(
                            t.dimensions.spacing16,
                            0,
                            t.dimensions.spacing16,
                            t.dimensions.spacing16,
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              if (barShown) ...[
                                SizedBox(
                                  width: math.min(
                                    t.dimensions.targetMin * 6,
                                    size.width * 0.3,
                                  ),
                                  child: Container(
                                    decoration: BoxDecoration(
                                      color: t.colors.surface,
                                      borderRadius: BorderRadius.circular(
                                        t.dimensions.cornerLarge,
                                      ),
                                    ),
                                    child: folderBar,
                                  ),
                                ),
                                SizedBox(width: t.dimensions.spacing16),
                              ],
                              Expanded(child: list),
                            ],
                          ),
                        )
                      : list,
                ),
              ],
            ),
          ),
          bottomNavigationBar: selecting
              ? _BatchBar(state: this, enabled: selectionCount > 0)
              : null,
          floatingActionButton: wide || selecting
              ? null
              : _ImportButton(onPressed: () => unawaited(importMedia())),
        );
      },
    );
  }
}

/// "已选 N 项" / "已选文件夹全部 N 项", "全选", close (REQ-APP-13).
class _SelectionHeader extends StatelessWidget {
  const _SelectionHeader({
    required this.count,
    required this.all,
    required this.onAll,
    required this.onClose,
    this.label,
  });

  final int count;
  final bool all;
  final VoidCallback onAll;
  final VoidCallback onClose;

  /// Text instead of the item count (folder selection).
  final String? label;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    return Padding(
      padding: EdgeInsetsDirectional.symmetric(
        horizontal: d.spacing8,
        vertical: d.spacing8,
      ),
      child: Row(
        children: [
          VkIconButton(
            icon: t.icons.resolve('close'),
            semanticLabel: a(a.l.libraryCancelSelect),
            onPressed: onClose,
          ),
          SizedBox(width: d.spacing8),
          Expanded(
            child: Semantics(
              liveRegion: true,
              header: true,
              child: Text(
                label ??
                    (all
                        ? a(a.l.librarySelectedAllFolder(count))
                        : a(a.l.librarySelectedCount(count))),
                maxLines: 2,
                style: t.typography.title.copyWith(
                  color: t.colors.textPrimary,
                ),
              ),
            ),
          ),
          VkButton(
            label: all ? a(a.l.libraryDeselectAll) : a(a.l.librarySelectAll),
            variant: VkButtonVariant.text,
            onPressed: onAll,
          ),
        ],
      ),
    );
  }
}

/// Bottom actions of a selection: 移动, 导出到相册, 移动到文件夹, 删除.
class _BatchBar extends StatelessWidget {
  const _BatchBar({required this.state, required this.enabled});

  final LibraryPageState state;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    Widget action(String icon, String label, Future<void> Function() run,
        {bool danger = false}) =>
        Expanded(
          child: MergeSemantics(
            child: Semantics(
              button: true,
              enabled: enabled,
              child: InkWell(
                onTap: enabled ? () => unawaited(run()) : null,
                child: ConstrainedBox(
                  constraints: BoxConstraints(minHeight: d.targetMin * 1.25),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        t.icons.resolve(icon),
                        size: d.icon20,
                        color: !enabled
                            ? t.colors.disabledContent
                            : danger
                            ? t.colors.error
                            : t.colors.textPrimary,
                      ),
                      SizedBox(height: d.spacing4),
                      Text(
                        label,
                        textAlign: TextAlign.center,
                        maxLines: 2,
                        style: t.typography.caption.copyWith(
                          color: !enabled
                              ? t.colors.disabledContent
                              : danger
                              ? t.colors.error
                              : t.colors.textPrimary,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
    return Material(
      color: t.colors.surface,
      child: SafeArea(
        top: false,
        child: Padding(
          padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing8),
          child: Row(
            children: [
              action('folder', a(a.l.libraryActionMove), state.batchMove),
              action('image', a(a.l.libraryExportToGallery), state.batchExport),
              action('export', a(a.l.libraryMoveOut), state.batchMoveOut),
              action(
                'delete',
                a(a.l.libraryDelete),
                state.batchDelete,
                danger: true,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TopBar extends StatelessWidget {
  const _TopBar({
    required this.state,
    required this.wide,
    required this.protected,
    required this.onOpenDrawer,
  });

  final LibraryPageState state;
  final bool wide;
  final bool protected;
  final VoidCallback onOpenDrawer;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final lockButton = VkIconButton(
      icon: t.icons.resolve('lock'),
      semanticLabel: a(a.l.libraryLockNow),
      style: t.components.buttonIcon.copyWithAll(
        (b) => b.copyWith(content: t.colors.success),
      ),
      onPressed: AppScope.of(context).libraryLock.lock,
    );
    final settings = VkIconButton(
      icon: t.icons.resolve('settings'),
      semanticLabel: a(a.l.librarySettings),
      // "数据 · 导出到相册 / 移动到文件夹" come back here to choose media.
      onPressed: () async {
        final r = await Navigator.of(context).push<String>(
          MaterialPageRoute(builder: (_) => const LibrarySettingsPage()),
        );
        if (r != null) state.setSelecting(true);
      },
    );
    final select = VkButton(
      label: a(a.l.librarySelect),
      variant: VkButtonVariant.text,
      onPressed: () => state.setSelecting(true),
    );
    return Padding(
      padding: EdgeInsetsDirectional.symmetric(
        horizontal: d.spacing8,
        vertical: d.spacing8,
      ),
      child: Row(
        children: [
          if (wide) ...[
            VkIconButton(
              icon: t.icons.resolve('back'),
              semanticLabel: s.text('playerBack'),
              onPressed: () => Navigator.of(context).maybePop(),
            ),
            SizedBox(width: d.spacing8),
            Semantics(
              header: true,
              child: Text(
                a(a.l.libraryTitle),
                style: t.typography.titleLarge.copyWith(
                  color: t.colors.textPrimary,
                ),
              ),
            ),
            if (protected) ...[
              SizedBox(width: d.spacing16),
              Icon(t.icons.resolve('lock'), size: d.icon16, color: t.colors.success),
              SizedBox(width: d.spacing4),
              Text(
                a(a.l.libraryPrivateUnlocked),
                style: t.typography.bodySmall.copyWith(
                  color: t.colors.success,
                ),
              ),
            ],
            const Spacer(),
            select,
            if (protected) lockButton,
            settings,
            SizedBox(width: d.spacing8),
            VkButton(
              label: a(a.l.libraryImport),
              icon: t.icons.resolve('add'),
              onPressed: () => unawaited(state.importMedia()),
            ),
          ] else ...[
            // Design page 27: folder button opens the drawer; the title
            // is the current folder.
            VkIconButton(
              icon: t.icons.resolve('folder'),
              semanticLabel: a(a.l.libraryShowFolders),
              onPressed: onOpenDrawer,
            ),
            SizedBox(width: d.spacing8),
            Expanded(
              child: Semantics(
                header: true,
                button: true,
                child: InkWell(
                  onTap: onOpenDrawer,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Flexible(
                        child: Text(
                          state.scopeName(a, state.scope),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: t.typography.titleLarge.copyWith(
                            color: t.colors.textPrimary,
                          ),
                        ),
                      ),
                      // A chevron pointing down (no separate token).
                      RotatedBox(
                        quarterTurns: 1,
                        child: Icon(
                          t.icons.resolve('next'),
                          size: d.icon20,
                          color: t.colors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            select,
            if (protected) lockButton,
            settings,
          ],
        ],
      ),
    );
  }
}

class _FolderBar extends StatelessWidget {
  const _FolderBar({
    required this.state,
    required this.drawer,
    required this.onClose,
  });

  final LibraryPageState state;
  final bool drawer;
  final VoidCallback onClose;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    final store = AppScope.of(context).library;
    void pick(LibraryScope s) {
      state._select(s);
      if (drawer) Navigator.of(context).maybePop();
    }

    Widget row({
      required LibraryScope scope,
      required String icon,
      required String name,
      LibraryFolder? folder,
    }) {
      final choosing = state.selectingFolders;
      final checked = folder != null && state.selectedFolders.contains(folder.id);
      final selected = choosing ? checked : state.scope == scope;
      final count = store.countIn(scope);
      return Padding(
        padding: EdgeInsetsDirectional.only(bottom: d.spacing4),
        child: MergeSemantics(
          child: Semantics(
            button: true,
            selected: selected,
            checked: choosing && folder != null ? checked : null,
            enabled: !choosing || folder != null,
            child: Material(
              type: selected ? MaterialType.canvas : MaterialType.transparency,
              color: selected ? t.colors.primaryContainer : null,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(d.cornerMedium),
                side: selected && !drawer
                    ? BorderSide(
                        color: t.colors.primary,
                        width: d.borderWidth * 1.5,
                      )
                    : BorderSide.none,
              ),
              child: InkWell(
                borderRadius: BorderRadius.circular(d.cornerMedium),
                onTap: choosing
                    ? (folder == null ? null : () => state.toggleFolder(folder.id))
                    : () => pick(scope),
                onLongPress: folder == null || choosing
                    ? null
                    : () => unawaited(state.folderActions(folder)),
                child: ConstrainedBox(
                  constraints: BoxConstraints(minHeight: d.targetMin * 1.1),
                  child: Padding(
                    padding: EdgeInsetsDirectional.symmetric(
                      horizontal: d.spacing12,
                    ),
                    child: Row(
                      children: [
                        Icon(
                          t.icons.resolve(icon),
                          size: d.icon20,
                          color: selected
                              ? t.colors.primary
                              : t.colors.textSecondary,
                        ),
                        SizedBox(width: d.spacing12),
                        Expanded(
                          child: Text(
                            name,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: t.typography.body.copyWith(
                              color: t.colors.textPrimary,
                              fontWeight: selected
                                  ? FontWeight.w600
                                  : FontWeight.w400,
                            ),
                          ),
                        ),
                        Text(
                          count.toString(),
                          style: t.typography.bodySmall.copyWith(
                            color: t.colors.textSecondary,
                          ),
                        ),
                        if (choosing && folder != null) ...[
                          SizedBox(width: d.spacing8),
                          Icon(
                            t.icons.resolve(
                              checked ? 'checkboxon' : 'checkboxoff',
                            ),
                            color: checked
                                ? t.colors.primary
                                : t.colors.borderStrong,
                          ),
                        ],
                        if (!choosing && folder != null && selected && !drawer)
                          VkIconButton(
                            icon: t.icons.resolve('more'),
                            semanticLabel: a(a.l.libraryFolderActions),
                            onPressed: () =>
                                unawaited(state.folderActions(folder)),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      );
    }

    final allFolders =
        store.folders.isNotEmpty &&
        state.selectedFolders.length == store.folders.length;
    return Padding(
      padding: EdgeInsetsDirectional.all(d.spacing12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (state.selectingFolders)
            _SelectionHeader(
              count: state.selectedFolders.length,
              all: allFolders,
              label: a(
                a.l.librarySelectedFolders(
                  state.selectedFolders.length,
                  state.selectionCount,
                ),
              ),
              onAll: state.toggleAllFolders,
              onClose: () => state.setSelectingFolders(false),
            )
          else
          Row(
            children: [
              SizedBox(width: d.spacing8),
              Expanded(
                child: Semantics(
                  header: true,
                  child: Text(
                    a(a.l.libraryFolders),
                    style: t.typography.title.copyWith(
                      color: t.colors.textPrimary,
                    ),
                  ),
                ),
              ),
              if (store.folders.isNotEmpty)
                VkButton(
                  label: a(a.l.librarySelect),
                  variant: VkButtonVariant.text,
                  onPressed: () => state.setSelectingFolders(true),
                ),
              VkIconButton(
                icon: t.icons.resolve('add'),
                semanticLabel: a(a.l.libraryNewFolder),
                style: t.components.buttonIcon.copyWithAll(
                  (b) => b.copyWith(content: t.colors.primary),
                ),
                onPressed: () => unawaited(state.newFolder()),
              ),
              VkIconButton(
                icon: t.icons.resolve(drawer ? 'close' : 'previous'),
                semanticLabel: a(
                  drawer ? a.l.libraryCloseFolders : a.l.libraryCollapseFolders,
                ),
                onPressed: onClose,
              ),
            ],
          ),
          SizedBox(height: d.spacing8),
          Expanded(
            child: ListView(
              children: [
                row(
                  scope: const AllMedia(),
                  icon: 'grid',
                  name: a(a.l.libraryAllMedia),
                ),
                for (final f in store.folders)
                  row(
                    scope: InFolder(f.id),
                    icon: 'folder',
                    name: f.name,
                    folder: f,
                  ),
                row(
                  scope: const Unsorted(),
                  icon: 'folder',
                  name: a(a.l.libraryUnsorted),
                ),
              ],
            ),
          ),
          if (state.selectingFolders)
            _BatchBar(
              state: state,
              enabled: state.selectedFolders.isNotEmpty,
            )
          else
            Padding(
              padding: EdgeInsetsDirectional.all(d.spacing8),
              child: Text(
                a(a.l.libraryFolderHint),
                style: t.typography.caption.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _ListArea extends StatelessWidget {
  const _ListArea({
    required this.state,
    required this.result,
    required this.wide,
    required this.folderBarHidden,
  });

  final LibraryPageState state;
  final LibraryPageResult result;
  final bool wide;
  final bool folderBarHidden;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    final r = result;
    final chips = Wrap(
      spacing: d.spacing8,
      children: [
        for (final (f, label) in [
          (LibraryFilter.all, a(a.l.libraryFilterAll)),
          (LibraryFilter.video, a(a.l.libraryFilterVideo)),
          (LibraryFilter.image, a(a.l.libraryFilterImage)),
        ])
          VkPressable(
            style: t.components.chip,
            semanticLabel: label,
            selected: state.filter == f,
            onPressed: () => state._setFilter(f),
            builder: (context, box) => Text(label, style: box.textStyle),
          ),
      ],
    );
    final header = wide
        ? Row(
            children: [
              if (folderBarHidden)
                VkIconButton(
                  icon: t.icons.resolve('folder'),
                  semanticLabel: a(a.l.libraryShowFolders),
                  onPressed: () => state.setFolderBarShown(true),
                ),
              Semantics(
                header: true,
                child: Text(
                  state.scopeName(a, state.scope),
                  style: t.typography.titleLarge.copyWith(
                    color: t.colors.textPrimary,
                  ),
                ),
              ),
              SizedBox(width: d.spacing12),
              Text(
                a(a.l.libraryItemCount(AppScope.of(context).library.countIn(state.scope))),
                style: t.typography.body.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
              const Spacer(),
              chips,
            ],
          )
        : Align(alignment: AlignmentDirectional.centerStart, child: chips);
    final pageItems = r.items;
    final grid = LayoutBuilder(
      builder: (context, c) {
        final columns = wide
            ? (c.maxWidth / (d.targetMin * 4)).floor().clamp(2, 6)
            : 2;
        return GridView.builder(
          padding: EdgeInsetsDirectional.only(bottom: d.spacing16),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: columns,
            crossAxisSpacing: d.spacing12,
            mainAxisSpacing: d.spacing12,
            childAspectRatio: 1.15,
          ),
          itemCount: pageItems.length,
          itemBuilder: (context, i) => _Tile(
            item: pageItems[i],
            checked: state.selecting
                ? state.isItemSelected(pageItems[i].id)
                : null,
            onOpen: state.selecting
                ? () => state.toggleItem(pageItems[i].id)
                : () => unawaited(
                    openLibraryItem(context, pageItems[i], pageItems: pageItems),
                  ),
            onMenu: state.selecting
                ? () => state.toggleItem(pageItems[i].id)
                : () => unawaited(state.itemActions(pageItems[i], pageItems)),
          ),
        );
      },
    );
    final empty = Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            t.icons.resolve('film'),
            size: d.targetMin,
            color: t.colors.textSecondary,
          ),
          SizedBox(height: d.spacing12),
          Text(
            a(a.l.libraryEmpty),
            style: t.typography.title.copyWith(color: t.colors.textPrimary),
          ),
          SizedBox(height: d.spacing8),
          Text(
            a(a.l.libraryEmptyHint),
            textAlign: TextAlign.center,
            style: t.typography.body.copyWith(color: t.colors.textSecondary),
          ),
        ],
      ),
    );
    final perPage = AppScope.of(context).libraryLock.value.pageSize;
    return Padding(
      padding: wide
          ? EdgeInsetsDirectional.zero
          : EdgeInsetsDirectional.symmetric(horizontal: d.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          header,
          SizedBox(height: d.spacing12),
          Expanded(child: r.total == 0 ? empty : grid),
          if (r.total > 0) ...[
            Semantics(
              liveRegion: true,
              child: Text(
                wide
                    ? a(a.l.libraryRangePerPage(r.first, r.last, r.total, perPage))
                    : a(a.l.libraryRange(r.first, r.last, r.total)),
                textAlign: TextAlign.center,
                style: t.typography.bodySmall.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
            ),
            SizedBox(height: d.spacing8),
            _Pager(
              page: r.page,
              count: r.pageCount,
              onPage: state.goToPage,
            ),
            // Room for the floating import button on phones.
            SizedBox(height: wide ? d.spacing8 : d.targetMin * 1.5),
          ],
        ],
      ),
    );
  }
}

class _Tile extends StatelessWidget {
  const _Tile({
    required this.item,
    required this.onOpen,
    required this.onMenu,
    this.checked,
  });

  final LibraryItem item;
  final VoidCallback onOpen;
  final VoidCallback onMenu;

  /// Selection mode: whether this item is selected (null = not selecting).
  final bool? checked;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    return MergeSemantics(
      child: Semantics(
        button: true,
        checked: checked,
        customSemanticsActions: checked != null
            ? null
            : {CustomSemanticsAction(label: a(a.l.libraryItemActions)): onMenu},
        child: InkWell(
          borderRadius: BorderRadius.circular(d.cornerMedium),
          onTap: onOpen,
          onLongPress: onMenu,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    LibraryThumbnail(item: item),
                    if (checked != null) ...[
                      if (checked!)
                        DecoratedBox(
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(
                              d.cornerMedium,
                            ),
                            border: Border.all(
                              color: t.colors.primary,
                              width: d.focusRingWidth * 1.5,
                            ),
                          ),
                        ),
                      PositionedDirectional(
                        top: d.spacing8,
                        end: d.spacing8,
                        child: ExcludeSemantics(
                          child: Icon(
                            t.icons.resolve(
                              checked! ? 'checkboxon' : 'checkboxoff',
                            ),
                            color: checked!
                                ? t.colors.primary
                                : t.colors.playerControlsContent,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              SizedBox(height: d.spacing4),
              Text(
                item.displayName,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: t.typography.body.copyWith(color: t.colors.textPrimary),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// "‹ 1 2 3 … 9 ›": first, last, current ±1, ellipses between.
class _Pager extends StatelessWidget {
  const _Pager({required this.page, required this.count, required this.onPage});

  final int page;
  final int count;
  final ValueChanged<int> onPage;

  /// Page numbers shown; null = "…".
  static List<int?> numbers(int page, int count) {
    final shown = <int>{1, count, page - 1, page, page + 1}
      ..removeWhere((p) => p < 1 || p > count);
    final sorted = shown.toList()..sort();
    final out = <int?>[];
    for (final (i, p) in sorted.indexed) {
      if (i > 0 && p - sorted[i - 1] > 1) out.add(null);
      out.add(p);
    }
    return out;
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    final style = t.components.chip.copyWithAll(
      (b) => b.copyWith(radius: d.cornerMedium),
    );
    Widget cell(String text, String semantic, VoidCallback? onTap, {bool on = false}) =>
        VkPressable(
          style: style,
          semanticLabel: semantic,
          selected: on,
          onPressed: onTap,
          builder: (context, box) => Text(text, style: box.textStyle),
        );
    return Wrap(
      alignment: WrapAlignment.center,
      spacing: d.spacing8,
      runSpacing: d.spacing8,
      children: [
        VkIconButton(
          icon: t.icons.resolve('previous'),
          semanticLabel: a(a.l.libraryPrevPage),
          onPressed: page > 1 ? () => onPage(page - 1) : null,
        ),
        for (final n in numbers(page, count))
          if (n == null)
            ExcludeSemantics(
              child: Padding(
                padding: EdgeInsetsDirectional.symmetric(
                  horizontal: d.spacing8,
                  vertical: d.spacing12,
                ),
                child: Text(
                  a(a.l.libraryEllipsis),
                  style: t.typography.body.copyWith(
                    color: t.colors.textSecondary,
                  ),
                ),
              ),
            )
          else
            cell(
              n.toString(),
              a(a.l.libraryPageN(n)),
              n == page ? null : () => onPage(n),
              on: n == page,
            ),
        VkIconButton(
          icon: t.icons.resolve('next'),
          semanticLabel: a(a.l.libraryNextPage),
          onPressed: page < count ? () => onPage(page + 1) : null,
        ),
      ],
    );
  }
}

class _ImportButton extends StatelessWidget {
  const _ImportButton({required this.onPressed});

  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    return VkButton(
      label: a(a.l.libraryImport),
      icon: t.icons.resolve('add'),
      pill: true,
      onPressed: onPressed,
    );
  }
}

typedef _SheetAction = ({String id, String label, bool danger});

class _ActionSheet extends StatelessWidget {
  const _ActionSheet({required this.title, required this.actions});

  final String title;
  final List<_SheetAction> actions;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return SafeArea(
      child: Padding(
        padding: EdgeInsetsDirectional.all(d.spacing16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: EdgeInsetsDirectional.all(d.spacing8),
              child: Semantics(
                header: true,
                child: Text(
                  title,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: t.typography.title.copyWith(
                    color: t.colors.textPrimary,
                  ),
                ),
              ),
            ),
            for (final (i, x) in actions.indexed) ...[
              if (i > 0) Divider(height: d.borderWidth, color: t.colors.divider),
              InkWell(
                onTap: () => Navigator.of(context).pop(x.id),
                child: ConstrainedBox(
                  constraints: BoxConstraints(minHeight: d.targetMin),
                  child: Padding(
                    padding: EdgeInsetsDirectional.symmetric(
                      horizontal: d.spacing8,
                    ),
                    child: Align(
                      alignment: AlignmentDirectional.centerStart,
                      child: Text(
                        x.label,
                        style: t.typography.body.copyWith(
                          color: x.danger
                              ? t.colors.error
                              : t.colors.textPrimary,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
