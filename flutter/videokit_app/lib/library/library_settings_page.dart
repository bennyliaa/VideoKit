import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../l10n/app_text.dart';
import 'library_lock.dart';
import 'library_lock_page.dart';

/// "媒体库设置" (design page 27): password protection, change PIN,
/// fingerprint / face, auto-lock delay, page size (10/20/50/100 or 5–200),
/// folder bar default.
class LibrarySettingsPage extends StatelessWidget {
  /// Creates the page.
  const LibrarySettingsPage({super.key});

  /// Text of an auto-lock delay.
  static String lockAfterText(AppText a, int seconds) {
    if (seconds <= 0) return a(a.l.libraryAutoLockNow);
    if (seconds % 60 == 0) return a(a.l.libraryAutoLockMinutes(seconds ~/ 60));
    return a(a.l.libraryAutoLockSeconds(seconds));
  }

  Future<void> _togglePin(BuildContext context, bool on) async {
    final lock = AppScope.of(context).libraryLock;
    if (on) {
      await pushPinPage(context, PinMode.setUp);
      return;
    }
    // Turning protection off needs the current PIN.
    if (await pushPinPage(context, PinMode.verify)) await lock.clearPin();
  }

  Future<void> _changePin(BuildContext context) async {
    if (!await pushPinPage(context, PinMode.verify) || !context.mounted) {
      return;
    }
    await pushPinPage(context, PinMode.setUp);
  }

  Future<void> _toggleBiometric(BuildContext context, bool on) async {
    final lock = AppScope.of(context).libraryLock;
    final a = AppText.of(context);
    final ok = await lock.setBiometric(on);
    if (!ok && context.mounted) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(content: Text(a(a.l.libraryBiometricUnavailable))),
        );
    }
  }

  Future<void> _chooseLockAfter(BuildContext context) async {
    final lock = AppScope.of(context).libraryLock;
    final a = AppText.of(context);
    final t = VkTheme.of(context);
    final chosen = await showModalBottomSheet<int>(
      context: context,
      backgroundColor: t.colors.surface,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            for (final s in LibrarySettings.lockAfterChoices)
              ListTile(
                title: Text(
                  lockAfterText(a, s),
                  style: t.typography.body.copyWith(
                    color: t.colors.textPrimary,
                  ),
                ),
                trailing: s == lock.value.lockAfterSeconds
                    ? Icon(t.icons.resolve('check'), color: t.colors.primary)
                    : null,
                onTap: () => Navigator.of(context).pop(s),
              ),
          ],
        ),
      ),
    );
    if (chosen != null) await lock.setLockAfter(chosen);
  }

  Future<void> _customPageSize(BuildContext context) async {
    final lock = AppScope.of(context).libraryLock;
    final size = await showDialog<int>(
      context: context,
      builder: (_) => _PageSizeDialog(initial: lock.value.pageSize),
    );
    if (size != null) await lock.setPageSize(size);
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final lock = AppScope.of(context).libraryLock;
    return Scaffold(
      backgroundColor: t.colors.background,
      appBar: AppBar(
        backgroundColor: t.colors.background,
        leading: VkIconButton(
          icon: t.icons.resolve('back'),
          semanticLabel: s.text('playerBack'),
          onPressed: () => Navigator.of(context).maybePop(),
        ),
        title: Text(
          a(a.l.librarySettings),
          style: t.typography.titleLarge.copyWith(color: t.colors.textPrimary),
        ),
      ),
      body: ValueListenableBuilder<LibrarySettings>(
        valueListenable: lock,
        builder: (context, st, _) {
          final chips = Wrap(
            spacing: d.spacing8,
            runSpacing: d.spacing8,
            alignment: WrapAlignment.end,
            children: [
              for (final n in LibrarySettings.pageSizeChoices)
                VkPressable(
                  style: t.components.chip.copyWithAll(
                    (b) => b.copyWith(radius: d.cornerMedium),
                  ),
                  semanticLabel: n.toString(),
                  selected: st.pageSize == n,
                  onPressed: () => unawaited(lock.setPageSize(n)),
                  builder: (context, box) =>
                      Text(n.toString(), style: box.textStyle),
                ),
            ],
          );
          return ListView(
            padding: EdgeInsetsDirectional.all(d.spacing16),
            children: [
              _Section(a(a.l.librarySecPrivate)),
              _Card([
                _Row(
                  title: a(a.l.libraryPinProtect),
                  trailing: VkSwitch(
                    value: st.protected,
                    semanticLabel: a(a.l.libraryPinProtect),
                    onChanged: (v) => unawaited(_togglePin(context, v)),
                  ),
                ),
                if (st.protected)
                  _Row(
                    title: a(a.l.libraryChangePin),
                    onTap: () => unawaited(_changePin(context)),
                    trailing: Icon(
                      t.icons.resolve('next'),
                      color: t.colors.textSecondary,
                    ),
                  ),
                if (st.protected)
                  _Row(
                    title: a(a.l.libraryBiometricUnlock),
                    trailing: VkSwitch(
                      value: st.biometric,
                      semanticLabel: a(a.l.libraryBiometricUnlock),
                      onChanged: (v) =>
                          unawaited(_toggleBiometric(context, v)),
                    ),
                  ),
              ]),
              SizedBox(height: d.spacing16),
              _Card([
                _Row(
                  title: a(a.l.libraryAutoLock),
                  subtitle: lockAfterText(a, st.lockAfterSeconds),
                  onTap: () => unawaited(_chooseLockAfter(context)),
                  trailing: Icon(
                    t.icons.resolve('next'),
                    color: t.colors.textSecondary,
                  ),
                ),
              ]),
              _Section(a(a.l.librarySecDisplay)),
              _Card([
                _Row(title: a(a.l.libraryPerPage), trailing: chips),
                _Row(
                  title: a(a.l.libraryCustomPerPage),
                  subtitle:
                      LibrarySettings.pageSizeChoices.contains(st.pageSize)
                      ? null
                      : a(a.l.libraryPageSizeCurrent(st.pageSize)),
                  onTap: () => unawaited(_customPageSize(context)),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        a(a.l.libraryPageSizeRange),
                        style: t.typography.body.copyWith(
                          color: t.colors.textSecondary,
                        ),
                      ),
                      Icon(
                        t.icons.resolve('next'),
                        color: t.colors.textSecondary,
                      ),
                    ],
                  ),
                ),
              ]),
              SizedBox(height: d.spacing16),
              _Card([
                _Row(
                  title: a(a.l.libraryShowFolderBar),
                  trailing: VkSwitch(
                    value: st.showFolderBar,
                    semanticLabel: a(a.l.libraryShowFolderBar),
                    onChanged: (v) => unawaited(lock.setShowFolderBar(v)),
                  ),
                ),
              ]),
              // REQ-APP-14 (design page 27): getting media out, and what
              // uninstalling does.
              _Section(a(a.l.librarySecData)),
              _Card([
                _Row(
                  title: a(a.l.libraryExportToGallery),
                  onTap: () => Navigator.of(context).pop('export'),
                  trailing: _Value(a(a.l.libraryChooseMedia)),
                ),
                _Row(
                  title: a(a.l.libraryMoveOut),
                  onTap: () => Navigator.of(context).pop('moveOut'),
                  trailing: _Value(a(a.l.libraryMoveOutHint)),
                ),
              ]),
              SizedBox(height: d.spacing12),
              const LibraryDataWarning(),
            ],
          );
        },
      ),
    );
  }
}

/// "卸载 App 或清除数据会删除媒体库中的所有文件。需要保留的媒体请先导出到
/// 相册或移动到文件夹。" (REQ-APP-14): warning colour and icon, shown on
/// first use and under the settings' data section.
class LibraryDataWarning extends StatelessWidget {
  /// Creates the warning.
  const LibraryDataWarning({super.key});

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    return MergeSemantics(
      child: Padding(
        padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing8),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              t.icons.resolve('warning'),
              size: d.icon20,
              color: t.colors.warning,
            ),
            SizedBox(width: d.spacing8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    a(a.l.libraryDataWarningTitle),
                    style: t.typography.body.copyWith(color: t.colors.warning),
                  ),
                  Text(
                    a(a.l.libraryDataWarningBody),
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
    );
  }
}

class _Value extends StatelessWidget {
  const _Value(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Flexible(
          child: Text(
            text,
            style: t.typography.body.copyWith(color: t.colors.textSecondary),
          ),
        ),
        Icon(t.icons.resolve('next'), color: t.colors.textSecondary),
      ],
    );
  }
}

class _PageSizeDialog extends StatefulWidget {
  const _PageSizeDialog({required this.initial});

  final int initial;

  @override
  State<_PageSizeDialog> createState() => _PageSizeDialogState();
}

class _PageSizeDialogState extends State<_PageSizeDialog> {
  late final TextEditingController _text = TextEditingController(
    text: '${widget.initial}',
  );
  bool _invalid = false;

  @override
  void dispose() {
    _text.dispose();
    super.dispose();
  }

  void _submit() {
    final v = LibrarySettings.parsePageSize(_text.text);
    if (v == null) {
      setState(() => _invalid = true);
      return;
    }
    Navigator.of(context).pop(v);
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    return AlertDialog(
      backgroundColor: t.colors.surfaceHigh,
      title: Text(
        a(a.l.libraryCustomPerPage),
        style: t.typography.title.copyWith(color: t.colors.textPrimary),
      ),
      content: TextField(
        controller: _text,
        autofocus: true,
        keyboardType: TextInputType.number,
        // Non-digits are still possible from a hardware keyboard or paste;
        // the value is checked on submit.
        inputFormatters: [LengthLimitingTextInputFormatter(4)],
        style: t.typography.body.copyWith(color: t.colors.textPrimary),
        decoration: InputDecoration(
          labelText: a(a.l.libraryPageSizeRange),
          errorText: _invalid ? a(a.l.libraryPageSizeInvalid) : null,
        ),
        onSubmitted: (_) => _submit(),
      ),
      actions: [
        VkButton(
          label: s.text('commonCancel'),
          variant: VkButtonVariant.text,
          onPressed: () => Navigator.of(context).pop(),
        ),
        VkButton(label: a(a.l.libraryConfirm), onPressed: _submit),
      ],
    );
  }
}

class _Section extends StatelessWidget {
  const _Section(this.title);

  final String title;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return Padding(
      padding: EdgeInsetsDirectional.fromSTEB(
        d.spacing8,
        d.spacing16,
        d.spacing8,
        d.spacing8,
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
}

class _Card extends StatelessWidget {
  const _Card(this.children);

  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return Container(
      padding: EdgeInsetsDirectional.symmetric(
        horizontal: d.spacing16,
        vertical: d.spacing4,
      ),
      decoration: BoxDecoration(
        color: t.colors.surface,
        borderRadius: BorderRadius.circular(d.cornerLarge),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final (i, c) in children.indexed) ...[
            if (i > 0) Divider(height: d.borderWidth, color: t.colors.divider),
            c,
          ],
        ],
      ),
    );
  }
}

class _Row extends StatelessWidget {
  const _Row({
    required this.title,
    this.subtitle,
    this.trailing,
    this.onTap,
  });

  final String title;
  final String? subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final row = ConstrainedBox(
      constraints: BoxConstraints(minHeight: d.targetMin * 1.25),
      child: Padding(
        padding: EdgeInsetsDirectional.symmetric(vertical: d.spacing8),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: t.typography.body.copyWith(
                      color: t.colors.textPrimary,
                    ),
                  ),
                  if (subtitle != null)
                    Text(
                      subtitle!,
                      style: t.typography.bodySmall.copyWith(
                        color: t.colors.textSecondary,
                      ),
                    ),
                ],
              ),
            ),
            if (trailing != null) ...[
              SizedBox(width: d.spacing12),
              Flexible(child: trailing!),
            ],
          ],
        ),
      ),
    );
    if (onTap == null) return row;
    return MergeSemantics(
      child: Semantics(
        button: true,
        child: InkWell(onTap: onTap, child: row),
      ),
    );
  }
}
