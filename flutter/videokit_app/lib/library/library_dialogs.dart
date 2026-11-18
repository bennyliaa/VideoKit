import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../l10n/app_text.dart';
import 'library_store.dart';

/// Text of [error] for a folder name.
String folderNameErrorText(AppText a, FolderNameError error) => a(switch (error) {
  FolderNameError.empty => a.l.libraryNameEmpty,
  FolderNameError.duplicate => a.l.libraryNameDuplicate,
  FolderNameError.tooLong => a.l.libraryNameTooLong(LibraryStore.maxFolderName),
});

/// Asks for a folder name (create, or rename [initial]); the store's rules
/// are checked as the user types and again on submit (FT01A-10). Returns
/// the accepted name, or null when cancelled.
Future<String?> askFolderName(
  BuildContext context, {
  required LibraryStore store,
  required String title,
  required String action,
  String initial = '',
  String? exceptId,
}) => showDialog<String>(
  context: context,
  builder: (context) => FolderNameDialog(
    store: store,
    title: title,
    action: action,
    initial: initial,
    exceptId: exceptId,
  ),
);

/// The folder name dialog.
class FolderNameDialog extends StatefulWidget {
  /// Creates the dialog.
  const FolderNameDialog({
    super.key,
    required this.store,
    required this.title,
    required this.action,
    this.initial = '',
    this.exceptId,
  });

  /// Rules.
  final LibraryStore store;

  /// Title.
  final String title;

  /// Confirm label.
  final String action;

  /// Initial text.
  final String initial;

  /// Folder being renamed.
  final String? exceptId;

  @override
  State<FolderNameDialog> createState() => _FolderNameDialogState();
}

class _FolderNameDialogState extends State<FolderNameDialog> {
  late final TextEditingController _text = TextEditingController(
    text: widget.initial,
  );
  FolderNameError? _error;
  bool _touched = false;

  @override
  void dispose() {
    _text.dispose();
    super.dispose();
  }

  void _submit() {
    final error = widget.store.checkFolderName(
      _text.text,
      exceptId: widget.exceptId,
    );
    if (error != null) {
      setState(() {
        _touched = true;
        _error = error;
      });
      return;
    }
    Navigator.of(context).pop(_text.text.trim());
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final error = _touched ? _error : null;
    return AlertDialog(
      backgroundColor: t.colors.surfaceHigh,
      title: Text(
        widget.title,
        style: t.typography.title.copyWith(color: t.colors.textPrimary),
      ),
      content: TextField(
        controller: _text,
        autofocus: true,
        maxLength: LibraryStore.maxFolderName,
        style: t.typography.body.copyWith(color: t.colors.textPrimary),
        decoration: InputDecoration(
          labelText: a(a.l.libraryFolderName),
          errorText: error == null ? null : folderNameErrorText(a, error),
        ),
        onChanged: (v) => setState(() {
          _touched = true;
          _error = widget.store.checkFolderName(v, exceptId: widget.exceptId);
        }),
        onSubmitted: (_) => _submit(),
      ),
      actions: [
        VkButton(
          label: s.text('commonCancel'),
          variant: VkButtonVariant.text,
          onPressed: () => Navigator.of(context).pop(),
        ),
        VkButton(label: widget.action, onPressed: _submit),
      ],
    );
  }
}

/// How a folder is deleted.
enum FolderDeleteChoice {
  /// Media deleted too.
  deleteMedia,

  /// Media moved to "未分类".
  moveToUnsorted,
}

/// Confirms deleting folder [name] with [count] items (REQ-APP-13: the
/// user chooses what happens to the media). Null = cancelled.
Future<FolderDeleteChoice?> confirmDeleteFolder(
  BuildContext context, {
  required String name,
  required int count,
  bool multiple = false,
}) => showDialog<FolderDeleteChoice>(
  context: context,
  builder: (context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return AlertDialog(
      backgroundColor: t.colors.surfaceHigh,
      title: Text(
        // Several folders: [name] is already the full title.
        multiple ? name : a(a.l.libraryDeleteFolderTitle(name)),
        style: t.typography.title.copyWith(color: t.colors.textPrimary),
      ),
      content: Text(
        count == 0
            ? a(a.l.libraryDeleteFolderEmpty)
            : a(a.l.libraryDeleteFolderBody(count)),
        style: t.typography.body.copyWith(color: t.colors.textSecondary),
      ),
      actionsOverflowDirection: VerticalDirection.down,
      actions: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (count > 0) ...[
              VkButton(
                label: a(a.l.libraryMoveToUnsorted),
                variant: VkButtonVariant.secondary,
                onPressed: () => Navigator.of(
                  context,
                ).pop(FolderDeleteChoice.moveToUnsorted),
              ),
              SizedBox(height: d.spacing8),
            ],
            VkButton(
              label: count == 0
                  ? a(a.l.libraryDelete)
                  : a(a.l.libraryDeleteMediaToo),
              variant: VkButtonVariant.danger,
              onPressed: () =>
                  Navigator.of(context).pop(FolderDeleteChoice.deleteMedia),
            ),
            SizedBox(height: d.spacing8),
            VkButton(
              label: s.text('commonCancel'),
              variant: VkButtonVariant.text,
              onPressed: () => Navigator.of(context).pop(),
            ),
          ],
        ),
      ],
    );
  },
);

/// Confirms a destructive action; true when confirmed.
Future<bool> confirmDanger(
  BuildContext context, {
  required String title,
  required String body,
  required String action,
}) async =>
    await showDialog<bool>(
      context: context,
      builder: (context) {
        final t = VkTheme.of(context);
        final s = VkStrings.of(context);
        return AlertDialog(
          backgroundColor: t.colors.surfaceHigh,
          title: Text(
            title,
            style: t.typography.title.copyWith(color: t.colors.textPrimary),
          ),
          content: Text(
            body,
            style: t.typography.body.copyWith(color: t.colors.textSecondary),
          ),
          actions: [
            VkButton(
              label: s.text('commonCancel'),
              variant: VkButtonVariant.text,
              onPressed: () => Navigator.of(context).pop(false),
            ),
            VkButton(
              label: action,
              variant: VkButtonVariant.danger,
              onPressed: () => Navigator.of(context).pop(true),
            ),
          ],
        );
      },
    ) ??
    false;
