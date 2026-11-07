import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import '../l10n/app_text.dart';
import 'app_host.dart';

/// Resolves the App's host action string keys (`AppHostActions`).
String resolveAppHostString(BuildContext context, String key) {
  final a = AppText.of(context);
  final l = a.l;
  return a(switch (key) {
    'app.favorite' => l.hostFavorite,
    'app.favorited' => l.hostFavorited,
    'app.favorite.video.cd' => l.hostFavoriteVideoCd,
    'app.unfavorite.video.cd' => l.hostUnfavoriteVideoCd,
    'app.favorite.image.cd' => l.hostFavoriteImageCd,
    'app.unfavorite.image.cd' => l.hostUnfavoriteImageCd,
    'app.tag' => l.hostTag,
    'app.tag.video.cd' => l.hostTagVideoCd,
    'app.tag.image.cd' => l.hostTagImageCd,
    _ => key,
  });
}

/// Host of one page's session (M2): "收藏" and "标签" stored in the App's
/// history, and paging for image pages. Registered with the App's
/// [AppHostCallbacks] while the page shows [session].
class EntryHost implements AppSessionHost {
  /// Creates the host for [entryId].
  EntryHost({
    required this.scope,
    required this.context,
    required this.entryId,
    this.onNavigate,
  });

  /// App scope.
  final AppScope scope;

  /// Page context (dialogs).
  final BuildContext Function() context;

  /// Record shown.
  String entryId;

  /// Session the page shows (receives updated actions).
  VideoKitSession? session;

  /// Paging; null = "没有更多内容了".
  final Future<NavigationResult> Function(NavigationDirection direction)?
  onNavigate;

  /// Initial actions for [entry], or none when the record is not kept
  /// (history recording off): there is nothing to store them in.
  static List<VideoKitHostAction> actionsFor(
    AppScope scope,
    HistoryEntry entry,
  ) {
    final kept = scope.history.byId(entry.id);
    return kept == null ? const [] : AppHostActions.forEntry(kept);
  }

  @override
  Future<HostActionResult> onHostAction(HostActionRequest request) async {
    final e = scope.history.byId(entryId);
    if (e == null) return const HostActionResult.failed();
    switch (request.actionId) {
      case AppHostActions.favorite:
        final next = await scope.history.setFavorite(e.id, !e.favorite);
        return next == null
            ? const HostActionResult.failed()
            : HostActionResult.completed(AppHostActions.favoriteAction(next));
      case AppHostActions.tag:
        final ctx = context();
        if (!ctx.mounted) return const HostActionResult.cancelled();
        // The action completes when the editor opens; the badge follows
        // when it closes (the user may take longer than the 10 s timeout).
        unawaited(_editTags(ctx, e));
        return const HostActionResult.completed();
      default:
        return const HostActionResult.failed();
    }
  }

  Future<void> _editTags(BuildContext ctx, HistoryEntry e) async {
    final tags = await showTagEditor(ctx, e.tags);
    if (tags == null) return;
    final next = await scope.history.setTags(e.id, tags);
    final s = session;
    if (next != null && s != null) {
      await s.updateHostActions(AppHostActions.forEntry(next));
    }
  }

  @override
  Future<NavigationResult> onNavigation(NavigationRequest request) =>
      onNavigate?.call(request.direction) ??
      Future.value(NavigationResult.unavailable);
}

/// Tag editor (App UI): current tags with remove buttons, a field to add
/// one, "完成". Returns the new list, or null when dismissed.
Future<List<String>?> showTagEditor(BuildContext context, List<String> tags) =>
    showDialog<List<String>>(
      context: context,
      builder: (context) => TagEditor(initial: tags),
    );

/// Content of [showTagEditor] (public for tests).
class TagEditor extends StatefulWidget {
  /// Creates the editor.
  const TagEditor({super.key, required this.initial});

  /// Tags when opened.
  final List<String> initial;

  @override
  State<TagEditor> createState() => _TagEditorState();
}

class _TagEditorState extends State<TagEditor> {
  late final List<String> _tags = [...widget.initial];
  final TextEditingController _field = TextEditingController();

  @override
  void dispose() {
    _field.dispose();
    super.dispose();
  }

  void _add() {
    final v = _field.text.trim();
    if (v.isEmpty) return;
    setState(() {
      if (!_tags.contains(v)) _tags.add(v);
      _field.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    return Dialog(
      backgroundColor: t.colors.surface,
      child: Padding(
        padding: EdgeInsetsDirectional.all(d.spacing16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Semantics(
              header: true,
              child: Text(
                a(a.l.tagEditorTitle),
                style: t.typography.titleLarge.copyWith(
                  color: t.colors.textPrimary,
                ),
              ),
            ),
            SizedBox(height: d.spacing12),
            if (_tags.isEmpty)
              Text(
                a(a.l.tagEditorEmpty),
                style: t.typography.body.copyWith(
                  color: t.colors.textSecondary,
                ),
              )
            else
              Wrap(
                spacing: d.spacing8,
                runSpacing: d.spacing8,
                children: [
                  for (final tag in _tags)
                    VkPressable(
                      style: t.components.chip,
                      semanticLabel: a(a.l.tagEditorRemove(tag)),
                      onPressed: () => setState(() => _tags.remove(tag)),
                      builder: (context, box) => Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Flexible(child: Text(tag, style: box.textStyle)),
                          SizedBox(width: d.spacing4),
                          Icon(
                            t.icons.resolve('close'),
                            size: d.icon16,
                            color: box.content,
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            SizedBox(height: d.spacing12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _field,
                    style: t.typography.body.copyWith(
                      color: t.colors.textPrimary,
                    ),
                    decoration: InputDecoration(hintText: a(a.l.tagEditorHint)),
                    onSubmitted: (_) => _add(),
                  ),
                ),
                SizedBox(width: d.spacing8),
                VkButton(
                  label: a(a.l.tagEditorAdd),
                  variant: VkButtonVariant.secondary,
                  onPressed: _add,
                ),
              ],
            ),
            SizedBox(height: d.spacing16),
            Align(
              alignment: AlignmentDirectional.centerEnd,
              child: VkButton(
                label: a(a.l.tagEditorDone),
                onPressed: () {
                  _add();
                  Navigator.of(context).pop(List<String>.of(_tags));
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
