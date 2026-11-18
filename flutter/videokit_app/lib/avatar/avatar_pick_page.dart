import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import '../l10n/app_text.dart';
import '../permissions/app_permissions.dart';
import '../permissions/permission_rationale.dart';
import '../picker/media_picker.dart';
import 'avatar_adjust_page.dart';
import 'avatar_widgets.dart';

/// "选择头像" (design page 25, first picture; REQ-ED-07). App business
/// (04A E6 5): the App decides which picture is used. Pops with the chosen
/// [MaskAvatar] (token, size, offset) or null.
class AvatarPickPage extends StatefulWidget {
  /// Creates the page.
  const AvatarPickPage({super.key, required this.tools, this.currentToken});

  /// The Kit's avatar tools (cut-out and built-ins).
  final VideoKitAvatarTools tools;

  /// The avatar the mask has now (highlighted).
  final String? currentToken;

  /// Opens the page; null when the user goes back.
  static Future<MaskAvatar?> open(
    BuildContext context, {
    required VideoKitAvatarTools tools,
    String? currentToken,
  }) => Navigator.of(context).push<MaskAvatar>(
    MaterialPageRoute(
      builder: (_) => AvatarPickPage(tools: tools, currentToken: currentToken),
    ),
  );

  @override
  State<AvatarPickPage> createState() => AvatarPickPageState();
}

/// State (public for tests).
class AvatarPickPageState extends State<AvatarPickPage> {
  late AppScope _scope;
  bool _started = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _scope = AppScope.of(context);
    if (_started) return;
    _started = true;
    unawaited(_scope.avatars.loadBuiltins(widget.tools));
  }

  /// A picture chosen from the album or the camera → "调整头像".
  Future<void> adjust(PickedMedia media) async {
    final entry = HistoryEntry(
      id: 'avatar-source',
      uri: media.uri,
      displayName: media.displayName,
      kind: media.kind,
      mimeType: media.mimeType,
      lastOpenedAtEpochMs: 0,
    );
    final result = await Navigator.of(context).push<MaskAvatar>(
      MaterialPageRoute(
        builder: (_) => AvatarAdjustPage(
          tools: widget.tools,
          entry: entry,
          source: _scope.backend.sourceFor(entry),
        ),
      ),
    );
    if (result != null && mounted) Navigator.of(context).pop(result);
  }

  /// 04A E7 Q4: every kept avatar is used by a kept project → no new one
  /// (said instead of evicting). True when blocked.
  bool _blockedFull() {
    if (!_scope.avatars.isFull) return false;
    final a = AppText.of(context);
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(a(a.l.avatarStoreFull))));
    return true;
  }

  Future<void> _album() async {
    if (_blockedFull()) return;
    final picked = await _scope.backend.picker.pick(
      context,
      multiple: false,
      kinds: const {MediaKind.imageStatic},
    );
    if (picked.isEmpty || !mounted) return;
    await adjust(picked.single);
  }

  /// "拍一张" (VK-M8): the camera permission is asked for here and only
  /// here. `unavailable` (no native permission handler) lets the picker
  /// decide, since a camera intent may not need the permission.
  Future<void> camera() async {
    if (_blockedFull()) return;
    // VK-A2 / FT01B-06: the purpose is explained before the system asks.
    final state = await requestWithRationale(context, AppPermission.camera);
    if (!mounted) return;
    switch (state) {
      case PermissionState.granted || PermissionState.unavailable:
        final photo = await _scope.backend.picker.capturePhoto(context);
        if (photo == null || !mounted) return;
        await adjust(photo);
      case PermissionState.denied:
        final a = AppText.of(context);
        ScaffoldMessenger.of(context)
          ..hideCurrentSnackBar()
          ..showSnackBar(SnackBar(content: Text(a(a.l.cameraDenied))));
      case PermissionState.permanentlyDenied:
        await _settingsDialog();
    }
  }

  Future<void> _settingsDialog() async {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final open = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: t.colors.surfaceHigh,
        title: Text(
          a(a.l.cameraSettingsTitle),
          style: t.typography.title.copyWith(color: t.colors.textPrimary),
        ),
        content: Text(
          a(a.l.cameraSettingsDetail),
          style: t.typography.body.copyWith(color: t.colors.textSecondary),
        ),
        actions: [
          VkButton(
            label: s.text('commonCancel'),
            variant: VkButtonVariant.text,
            onPressed: () => Navigator.of(context).pop(false),
          ),
          VkButton(
            label: a(a.l.openSystemSettings),
            onPressed: () => Navigator.of(context).pop(true),
          ),
        ],
      ),
    );
    if (open ?? false) await _scope.backend.permissions.openSettings();
  }

  void _use(String token) {
    unawaited(_scope.avatars.touch(token));
    Navigator.of(context).pop(MaskAvatar(avatarToken: token));
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    Widget section(String text) => Padding(
      padding: EdgeInsetsDirectional.only(
        top: d.spacing16,
        bottom: d.spacing8,
      ),
      child: Semantics(
        header: true,
        child: Text(
          text,
          style: t.typography.label.copyWith(color: t.colors.textSecondary),
        ),
      ),
    );
    Widget grid(List<Widget> tiles) => LayoutBuilder(
      builder: (context, c) {
        final columns = (c.maxWidth / (d.targetMin * 2)).floor().clamp(3, 6);
        final size = (c.maxWidth - d.spacing12 * (columns - 1)) / columns;
        return Wrap(
          spacing: d.spacing12,
          runSpacing: d.spacing12,
          children: [
            for (final tile in tiles) SizedBox.square(dimension: size, child: tile),
          ],
        );
      },
    );
    final picker = _scope.backend.picker;
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
          a(a.l.avatarPickTitle),
          style: t.typography.titleLarge.copyWith(color: t.colors.textPrimary),
        ),
      ),
      body: SafeArea(
        child: ListenableBuilder(
          listenable: _scope.avatars,
          builder: (context, _) {
            final recent = _scope.avatars.recent;
            return ListView(
              padding: EdgeInsetsDirectional.symmetric(
                horizontal: d.spacing16,
              ),
              children: [
                section(a(a.l.avatarFromPhotos)),
                Row(
                  children: [
                    Expanded(
                      child: _SourceCard(
                        icon: t.icons.resolve('image'),
                        label: a(a.l.avatarAlbum),
                        onTap: () => unawaited(_album()),
                      ),
                    ),
                    if (picker.canCapturePhoto) ...[
                      SizedBox(width: d.spacing12),
                      Expanded(
                        child: _SourceCard(
                          icon: t.icons.resolve('camera'),
                          label: a(a.l.avatarCamera),
                          onTap: () => unawaited(camera()),
                        ),
                      ),
                    ],
                  ],
                ),
                if (_scope.avatars.isFull)
                  Padding(
                    padding: EdgeInsetsDirectional.only(top: d.spacing8),
                    child: Text(
                      a(a.l.avatarStoreFull),
                      style: t.typography.bodySmall.copyWith(
                        color: t.colors.textSecondary,
                      ),
                    ),
                  ),
                if (recent.isNotEmpty) ...[
                  section(a(a.l.avatarRecent)),
                  grid([
                    for (final (i, r) in recent.indexed)
                      AvatarTile(
                        image: _scope.avatars.image(r.token),
                        label: a(a.l.avatarRecentItem(i + 1)),
                        selected: r.token == widget.currentToken,
                        onTap: () => _use(r.token),
                      ),
                  ]),
                ],
                section(a(a.l.avatarBuiltin)),
                grid([
                  for (var n = 1; n <= widget.tools.builtinAvatarCount; n++)
                    AvatarTile(
                      image: _scope.avatars.image(
                        '${MaskAvatar.builtinPrefix}$n',
                      ),
                      label: a(a.l.avatarBuiltinItem(n)),
                      checker: false,
                      selected:
                          '${MaskAvatar.builtinPrefix}$n' ==
                          widget.currentToken,
                      onTap: () => _use('${MaskAvatar.builtinPrefix}$n'),
                    ),
                ]),
                SizedBox(height: d.spacing24),
                // Design page 25: processed on this device, never uploaded.
                Container(
                  padding: EdgeInsetsDirectional.all(d.spacing16),
                  decoration: BoxDecoration(
                    color: t.colors.surface,
                    borderRadius: BorderRadius.circular(d.cornerLarge),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        t.icons.info,
                        size: d.icon20,
                        color: t.colors.textSecondary,
                      ),
                      SizedBox(width: d.spacing12),
                      Expanded(
                        child: Text(
                          a(a.l.avatarPrivacy),
                          style: t.typography.body.copyWith(
                            color: t.colors.textSecondary,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                SizedBox(height: d.spacing24),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _SourceCard extends StatelessWidget {
  const _SourceCard({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return Semantics(
      button: true,
      label: label,
      excludeSemantics: true,
      onTap: onTap,
      child: Material(
        color: t.colors.surface,
        borderRadius: BorderRadius.circular(d.cornerLarge),
        child: InkWell(
          borderRadius: BorderRadius.circular(d.cornerLarge),
          onTap: onTap,
          child: Padding(
            padding: EdgeInsetsDirectional.symmetric(
              vertical: d.spacing24,
              horizontal: d.spacing12,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(icon, size: d.icon24 * 1.5, color: t.colors.primary),
                SizedBox(height: d.spacing12),
                Text(
                  label,
                  textAlign: TextAlign.center,
                  style: t.typography.title.copyWith(
                    color: t.colors.textPrimary,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
