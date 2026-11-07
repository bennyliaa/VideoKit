import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_store.dart';
import '../l10n/app_text.dart';
import 'app_settings.dart';

/// App version shown in settings (pubspec `version`).
const String kAppVersion = '1.0.0';

/// Settings (REQ-APP-04/08, design page 8): play history switch, saved
/// count, clear history; theme, reduced motion; language; version and
/// open-source licenses.
class SettingsPage extends StatelessWidget {
  /// Creates the page.
  const SettingsPage({super.key});

  Future<void> _confirmClear(BuildContext context) async {
    final scope = AppScope.of(context);
    final a = AppText.of(context);
    final ok = await showDialog<bool>(
      context: context,
      builder: (context) {
        final t = VkTheme.of(context);
        return AlertDialog(
          backgroundColor: t.colors.surface,
          title: Text(
            a(a.l.clearConfirmTitle),
            style: t.typography.title.copyWith(color: t.colors.textPrimary),
          ),
          content: Text(
            a(a.l.clearConfirmBody),
            style: t.typography.body.copyWith(color: t.colors.textSecondary),
          ),
          actions: [
            VkButton(
              label: a(a.l.cancel),
              variant: VkButtonVariant.text,
              onPressed: () => Navigator.of(context).pop(false),
            ),
            VkButton(
              label: a(a.l.clear),
              onPressed: () => Navigator.of(context).pop(true),
            ),
          ],
        );
      },
    );
    if (ok != true || !context.mounted) return;
    await scope.history.clear();
    if (!context.mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(a(a.l.cleared))));
  }

  /// J3: language choice; Simplified Chinese is the only language for now.
  Future<void> _chooseLanguage(BuildContext context) async {
    final a = AppText.of(context);
    await showModalBottomSheet<void>(
      context: context,
      builder: (context) {
        final t = VkTheme.of(context);
        final d = t.dimensions;
        return ColoredBox(
          color: t.colors.surface,
          child: SafeArea(
            child: Padding(
              padding: EdgeInsetsDirectional.all(d.spacing16),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Semantics(
                    header: true,
                    child: Text(
                      a(a.l.uiLanguage),
                      style: t.typography.title.copyWith(
                        color: t.colors.textPrimary,
                      ),
                    ),
                  ),
                  SizedBox(height: d.spacing12),
                  MergeSemantics(
                    child: Semantics(
                      selected: true,
                      button: true,
                      child: InkWell(
                        onTap: () => Navigator.of(context).pop(),
                        child: ConstrainedBox(
                          constraints: BoxConstraints(minHeight: d.targetMin),
                          child: Row(
                            children: [
                              Expanded(
                                child: Text(
                                  a(a.l.languageChinese),
                                  style: t.typography.body.copyWith(
                                    color: t.colors.textPrimary,
                                  ),
                                ),
                              ),
                              Icon(t.icons.check, color: t.colors.primary),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                  Text(
                    a(a.l.languageNote),
                    style: t.typography.bodySmall.copyWith(
                      color: t.colors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return ListenableBuilder(
      listenable: Listenable.merge([scope.history, scope.settings]),
      builder: (context, _) {
        final st = scope.settings.value;
        void update(AppSettings next) => unawaited(scope.settings.update(next));
        final systemReduced = MediaQuery.disableAnimationsOf(context);
        final inlineTheme = !VkLayoutClass.collapseSecondary(
          MediaQuery.textScalerOf(context),
        );
        final themeControl = VkSegmented<VideoKitThemeMode>(
          segments: [
            VkSegment(value: VideoKitThemeMode.dark, label: a(a.l.themeDark)),
            VkSegment(value: VideoKitThemeMode.light, label: a(a.l.themeLight)),
            VkSegment(
              value: VideoKitThemeMode.system,
              label: a(a.l.themeSystem),
            ),
          ],
          selected: st.themeMode,
          semanticLabel: a(a.l.theme),
          onChanged: (mode) => update(st.copyWith(themeMode: mode)),
        );
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
              a(a.l.settingsTitle),
              style: t.typography.titleLarge.copyWith(
                color: t.colors.textPrimary,
              ),
            ),
          ),
          body: ListView(
            padding: EdgeInsetsDirectional.all(d.spacing16),
            children: [
              _Section(title: a(a.l.secHistory)),
              _Card(
                children: [
                  _Row(
                    title: a(a.l.recordHistory),
                    subtitle: a(a.l.recordHistoryNote),
                    trailing: VkSwitch(
                      value: st.recordHistory,
                      semanticLabel: a(a.l.recordHistory),
                      onChanged: (v) => update(st.copyWith(recordHistory: v)),
                    ),
                  ),
                  _Row(
                    title: a(a.l.savedCount),
                    trailing: Text(
                      a(
                        a.l.savedValue(
                          scope.history.entries.length,
                          HistoryStore.limit,
                        ),
                      ),
                      style: t.typography.body.copyWith(
                        color: t.colors.textSecondary,
                      ),
                    ),
                  ),
                  _DangerRow(
                    label: a(a.l.clearHistory),
                    onPressed: scope.history.entries.isEmpty
                        ? null
                        : () => unawaited(_confirmClear(context)),
                  ),
                ],
              ),
              _Section(title: a(a.l.secAppearance)),
              _Card(
                children: [
                  // Design page 8: a neutral segmented control in the row (below
                  // the title at large text).
                  _Row(
                    title: a(a.l.theme),
                    wideTrailing: true,
                    trailing: inlineTheme ? themeControl : null,
                    below: inlineTheme ? null : themeControl,
                  ),
                  _Row(
                    title: a(a.l.reduceMotion),
                    subtitle: a(a.l.reduceMotionNote),
                    trailing: VkSwitch(
                      value: st.reduceMotion ?? systemReduced,
                      semanticLabel: a(a.l.reduceMotion),
                      onChanged: (v) =>
                          update(st.copyWith(reduceMotion: () => v)),
                    ),
                  ),
                ],
              ),
              _Section(title: a(a.l.secLanguage)),
              _Card(
                children: [
                  // J3 (design page 8): the row opens the language choice; only
                  // Simplified Chinese for now.
                  MergeSemantics(
                    child: Semantics(
                      button: true,
                      child: InkWell(
                        onTap: () => unawaited(_chooseLanguage(context)),
                        child: _Row(
                          title: a(a.l.uiLanguage),
                          subtitle: a(a.l.languageNote),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Flexible(
                                child: Text(
                                  a(a.l.languageChinese),
                                  style: t.typography.body.copyWith(
                                    color: t.colors.textSecondary,
                                  ),
                                ),
                              ),
                              Icon(
                                t.icons.resolve('next'),
                                color: t.colors.textSecondary,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              _Section(title: a(a.l.secAbout)),
              _Card(
                children: [
                  _Row(
                    title: a(a.l.version),
                    trailing: Text(
                      kAppVersion,
                      style: t.typography.body.copyWith(
                        color: t.colors.textSecondary,
                      ),
                    ),
                  ),
                  MergeSemantics(
                    child: Semantics(
                      button: true,
                      child: InkWell(
                        onTap: () => _licenses(context),
                        child: _Row(
                          title: a(a.l.licenses),
                          trailing: Icon(
                            t.icons.resolve('next'),
                            color: t.colors.textSecondary,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  void _licenses(BuildContext context) {
    final a = AppText.of(context);
    showLicensePage(
      context: context,
      applicationName: a(a.l.appTitle),
      applicationVersion: kAppVersion,
      applicationLegalese: a(a.l.legalese),
    );
  }
}

class _Section extends StatelessWidget {
  const _Section({required this.title});

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
  const _Card({required this.children});

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
    this.below,
    this.wideTrailing = false,
  });

  /// Gives the trailing widget most of the row (segmented controls).
  final bool wideTrailing;

  final String title;
  final String? subtitle;
  final Widget? trailing;
  final Widget? below;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return ConstrainedBox(
      constraints: BoxConstraints(minHeight: d.targetMin * 1.25),
      child: Padding(
        padding: EdgeInsetsDirectional.symmetric(vertical: d.spacing8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              children: [
                Expanded(
                  flex: wideTrailing ? 1 : 3,
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
                  Flexible(
                    flex: wideTrailing ? 3 : 2,
                    child: Align(
                      alignment: AlignmentDirectional.centerEnd,
                      child: trailing,
                    ),
                  ),
                ],
              ],
            ),
            if (below != null) ...[SizedBox(height: d.spacing8), below!],
          ],
        ),
      ),
    );
  }
}

/// Destructive settings row in the error colour (design page 8 red text);
/// always confirmed by a dialog before acting.
class _DangerRow extends StatelessWidget {
  const _DangerRow({required this.label, required this.onPressed});

  final String label;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final enabled = onPressed != null;
    return MergeSemantics(
      child: Semantics(
        button: true,
        enabled: enabled,
        child: InkWell(
          onTap: onPressed,
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: d.targetMin * 1.25),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              child: Text(
                label,
                style: t.typography.body.copyWith(
                  color: enabled ? t.colors.error : t.colors.disabledContent,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
