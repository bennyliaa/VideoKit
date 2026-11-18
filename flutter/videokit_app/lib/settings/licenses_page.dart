import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../l10n/app_text.dart';

/// Whether a component is settled for the product (10 §2).
enum LicenseStatus {
  /// In use, license checked.
  adopted,

  /// Still a candidate / spike: license or rights not confirmed ("待定").
  pending,
}

/// One third-party component of the App (10 §2; product only, test
/// dependencies are not listed).
@immutable
final class AppComponent {
  /// Creates an entry.
  const AppComponent(this.name, this.use, this.license, this.status);

  /// Name text.
  final String Function(AppText a) name;

  /// What it is used for.
  final String Function(AppText a) use;

  /// License text.
  final String Function(AppText a) license;

  /// Status.
  final LicenseStatus status;
}

/// Components of the App and the VideoKit module (10 §2, 2026-11-08).
/// Native components come with the module; the cut-out model is decided
/// by S7.
final List<AppComponent> appComponents = [
  AppComponent(
    (a) => a.l.compMedia3,
    (a) => a.l.compUsePlayback,
    (a) => a.l.licApache2,
    LicenseStatus.adopted,
  ),
  AppComponent(
    (a) => a.l.compFlutter,
    (a) => a.l.compUseUi,
    (a) => a.l.licBsd3,
    LicenseStatus.adopted,
  ),
  AppComponent(
    (a) => a.l.compDart,
    (a) => a.l.compUseLanguage,
    (a) => a.l.licBsd3,
    LicenseStatus.adopted,
  ),
  AppComponent(
    (a) => a.l.compPathProvider,
    (a) => a.l.compUseStorage,
    (a) => a.l.licBsd3,
    LicenseStatus.adopted,
  ),
  AppComponent(
    (a) => a.l.compAndroidX,
    (a) => a.l.compUseNative,
    (a) => a.l.licApache2,
    LicenseStatus.adopted,
  ),
  AppComponent(
    (a) => a.l.compKotlin,
    (a) => a.l.compUseNative,
    (a) => a.l.licApache2,
    LicenseStatus.adopted,
  ),
  AppComponent(
    (a) => a.l.compOpenCv,
    (a) => a.l.compUseTracking,
    (a) => a.l.licApache2,
    LicenseStatus.pending,
  ),
  AppComponent(
    (a) => a.l.compYuNet,
    (a) => a.l.compUseFaces,
    (a) => a.l.licMitCatalog,
    LicenseStatus.pending,
  ),
  AppComponent(
    (a) => a.l.compViTTrack,
    (a) => a.l.compUseTracking,
    (a) => a.l.licApache2Catalog,
    LicenseStatus.pending,
  ),
  AppComponent(
    (a) => a.l.compOnnx,
    (a) => a.l.compUseInference,
    (a) => a.l.licMit,
    LicenseStatus.pending,
  ),
  AppComponent(
    (a) => a.l.compAvatarModel,
    (a) => a.l.compUseAvatar,
    (a) => a.l.licPending,
    LicenseStatus.pending,
  ),
];

/// "开源许可" (VK-M8, REQ-LIC): the components with their license and
/// status — undecided ones are marked "待定" — and the full texts
/// (Flutter's license registry; `videokit_flutter` registers the native
/// NOTICE there, 04A X1-7).
class LicensesPage extends StatelessWidget {
  /// Creates the page.
  const LicensesPage({super.key, required this.version});

  /// App version.
  final String version;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
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
          a(a.l.licenses),
          style: t.typography.titleLarge.copyWith(color: t.colors.textPrimary),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: EdgeInsetsDirectional.all(d.spacing16),
          children: [
            Text(
              a(a.l.licensesIntro),
              style: t.typography.body.copyWith(color: t.colors.textSecondary),
            ),
            SizedBox(height: d.spacing12),
            for (final c in appComponents)
              Padding(
                padding: EdgeInsetsDirectional.only(bottom: d.spacing8),
                child: MergeSemantics(
                  child: Container(
                    padding: EdgeInsetsDirectional.all(d.spacing12),
                    decoration: BoxDecoration(
                      color: t.colors.surface,
                      borderRadius: BorderRadius.circular(d.cornerMedium),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                a(c.name(a)),
                                style: t.typography.body.copyWith(
                                  fontWeight: FontWeight.w600,
                                  color: t.colors.textPrimary,
                                ),
                              ),
                              Text(
                                a(a.l.licenseLine(a(c.use(a)), a(c.license(a)))),
                                style: t.typography.caption.copyWith(
                                  color: t.colors.textSecondary,
                                ),
                              ),
                            ],
                          ),
                        ),
                        if (c.status == LicenseStatus.pending)
                          Container(
                            padding: EdgeInsetsDirectional.symmetric(
                              horizontal: d.spacing8,
                              vertical: d.spacing4,
                            ),
                            decoration: BoxDecoration(
                              color: t.colors.warningContainer,
                              borderRadius: BorderRadius.circular(
                                d.cornerFull,
                              ),
                            ),
                            child: Text(
                              a(a.l.licensePendingBadge),
                              style: t.typography.label.copyWith(
                                color: t.colors.textPrimary,
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            SizedBox(height: d.spacing8),
            Text(
              a(a.l.licensesNativeNote),
              style: t.typography.caption.copyWith(
                color: t.colors.textSecondary,
              ),
            ),
            SizedBox(height: d.spacing16),
            VkButton(
              label: a(a.l.licensesFullText),
              variant: VkButtonVariant.secondary,
              onPressed: () => showLicensePage(
                context: context,
                applicationName: a(a.l.appTitle),
                applicationVersion: version,
                applicationLegalese: a(a.l.legalese),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
