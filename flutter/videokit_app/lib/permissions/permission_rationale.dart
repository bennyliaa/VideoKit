import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../l10n/app_text.dart';
import 'app_permissions.dart';

/// Name and purpose of [p] (FT01B-06: every request is explained first).
(String name, String purpose) permissionText(AppText a, AppPermission p) =>
    switch (p) {
      AppPermission.camera => (
        a(a.l.permissionCamera),
        a(a.l.permissionRationaleCamera),
      ),
    };

/// Asks for [p] the way the stores require (VK-A2, FT01B-06): when it is
/// not granted yet, a dialog first says what it is for; only "继续" makes
/// the system request. "取消" asks nothing and reports `denied`, so the
/// feature degrades and the user can try again later.
Future<PermissionState> requestWithRationale(
  BuildContext context,
  AppPermission p,
) async {
  final permissions = AppScope.of(context).backend.permissions;
  final now = await permissions.status(p);
  if (now == PermissionState.granted || now == PermissionState.unavailable) {
    return permissions.request(p);
  }
  if (now == PermissionState.permanentlyDenied) return now;
  if (!context.mounted) return PermissionState.denied;
  final a = AppText.of(context);
  final (name, purpose) = permissionText(a, p);
  final go = await showDialog<bool>(
    context: context,
    builder: (context) {
      final t = VkTheme.of(context);
      final s = VkStrings.of(context);
      return AlertDialog(
        backgroundColor: t.colors.surfaceHigh,
        title: Text(
          a(a.l.permissionRationaleTitle(name)),
          style: t.typography.title.copyWith(color: t.colors.textPrimary),
        ),
        content: Text(
          purpose,
          style: t.typography.body.copyWith(color: t.colors.textSecondary),
        ),
        actions: [
          VkButton(
            label: s.text('commonCancel'),
            variant: VkButtonVariant.text,
            onPressed: () => Navigator.of(context).pop(false),
          ),
          VkButton(
            label: a(a.l.permissionContinue),
            onPressed: () => Navigator.of(context).pop(true),
          ),
        ],
      );
    },
  );
  if (go != true) return PermissionState.denied;
  return permissions.request(p);
}
