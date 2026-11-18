import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../history/app_storage.dart';
import '../l10n/app_text.dart';
import '../l10n/gen/app_localizations.dart';

/// The user's consent to the privacy policy (REQ-APP-15 prerequisite,
/// FT01B-05): stored in the App-private file `privacy_consent.json` with
/// the policy version agreed to. A newer policy version asks again.
final class PrivacyConsentStore {
  /// Creates the store.
  PrivacyConsentStore(this.storage, {DateTime Function()? now})
    : now = now ?? DateTime.now;

  /// Storage (only this file is read before consent).
  final AppStorage storage;

  /// Clock.
  final DateTime Function() now;

  /// File name.
  static const String fileName = 'privacy_consent.json';

  /// Version of the policy text; raise it when the policy changes.
  static const int policyVersion = 1;

  /// Whether the current policy version was agreed to.
  Future<bool> accepted() async {
    final raw = await storage.read(fileName);
    if (raw == null) return false;
    try {
      final j = jsonDecode(raw) as Map<String, Object?>;
      return ((j['version'] as num?)?.toInt() ?? 0) >= policyVersion;
    } on Object {
      return false;
    }
  }

  /// Records the consent (strict write: if it cannot be saved the App
  /// still starts this time and asks again next time).
  Future<void> accept() => writeQuietly(
    storage,
    fileName,
    jsonEncode({
      'version': policyVersion,
      'acceptedAtEpochMs': now().millisecondsSinceEpoch,
    }),
  );
}

/// First launch (REQ-APP-15 prerequisite, VK-A2, FT01B-05): until the
/// privacy policy is agreed to, only this gate runs — no backend connects,
/// no Kit or other SDK is created, no device information is read; the
/// gate only reads its own consent file. Refusing leaves the policy and
/// "退出"; agreeing builds [builder] (the App's normal start).
class PrivacyGate extends StatefulWidget {
  /// Creates the gate.
  const PrivacyGate({
    super.key,
    required this.storage,
    required this.builder,
    this.locale,
    this.fontFamily,
    this.onExit,
  });

  /// Storage for the consent file.
  final AppStorage storage;

  /// The App after consent (called only then).
  final Widget Function() builder;

  /// Forced locale (tests).
  final Locale? locale;

  /// Font family (screenshots).
  final String? fontFamily;

  /// "退出" (tests replace `SystemNavigator.pop`).
  final VoidCallback? onExit;

  @override
  State<PrivacyGate> createState() => PrivacyGateState();
}

/// State (public for tests).
class PrivacyGateState extends State<PrivacyGate> {
  late final PrivacyConsentStore _store = PrivacyConsentStore(widget.storage);

  /// Null while reading; then whether consent was given.
  bool? accepted;

  /// The user said "不同意" (rejected view).
  bool rejected = false;

  @override
  void initState() {
    super.initState();
    unawaited(
      _store.accepted().then((v) {
        if (mounted) setState(() => accepted = v);
      }),
    );
  }

  /// "同意并继续".
  Future<void> agree() async {
    await _store.accept();
    if (mounted) setState(() => accepted = true);
  }

  /// "不同意".
  void disagree() => setState(() => rejected = true);

  /// "再次查看并同意".
  void showAgain() => setState(() => rejected = false);

  Widget? _app;

  @override
  Widget build(BuildContext context) {
    // Built once: the backend inside must not be recreated on rebuilds.
    if (accepted ?? false) return _app ??= widget.builder();
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      locale: widget.locale ?? const Locale('zh'),
      localizationsDelegates: [
        AppLocalizations.delegate,
        ...videoKitLocalizationsDelegates,
      ],
      supportedLocales: videoKitSupportedLocales,
      localeResolutionCallback: videoKitResolveLocale,
      theme: ThemeData(
        brightness: Brightness.dark,
        fontFamily: widget.fontFamily,
      ),
      builder: (context, child) =>
          VideoKitThemeScope(mode: VideoKitThemeMode.dark, child: child!),
      home: accepted == null
          ? const _Blank()
          : _ConsentPage(
              rejected: rejected,
              onAgree: () => unawaited(agree()),
              onDisagree: disagree,
              onShowAgain: showAgain,
              onExit: widget.onExit ?? () => unawaited(SystemNavigator.pop()),
            ),
    );
  }
}

class _Blank extends StatelessWidget {
  const _Blank();

  @override
  Widget build(BuildContext context) =>
      ColoredBox(color: VkTheme.of(context).colors.background);
}

class _ConsentPage extends StatelessWidget {
  const _ConsentPage({
    required this.rejected,
    required this.onAgree,
    required this.onDisagree,
    required this.onShowAgain,
    required this.onExit,
  });

  final bool rejected;
  final VoidCallback onAgree;
  final VoidCallback onDisagree;
  final VoidCallback onShowAgain;
  final VoidCallback onExit;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    void open(bool terms) => unawaited(
      Navigator.of(context).push(
        MaterialPageRoute<void>(builder: (_) => PolicyPage(terms: terms)),
      ),
    );
    final links = Wrap(
      spacing: d.spacing8,
      children: [
        VkButton(
          label: a(a.l.privacyViewPolicy),
          variant: VkButtonVariant.text,
          onPressed: () => open(false),
        ),
        VkButton(
          label: a(a.l.privacyViewTerms),
          variant: VkButtonVariant.text,
          onPressed: () => open(true),
        ),
      ],
    );
    return Scaffold(
      backgroundColor: t.colors.background,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: EdgeInsetsDirectional.all(d.spacing24),
            child: ConstrainedBox(
              constraints: BoxConstraints(maxWidth: d.targetMin * 10),
              child: Container(
                padding: EdgeInsetsDirectional.all(d.spacing24),
                decoration: BoxDecoration(
                  color: t.colors.surfaceHigh,
                  borderRadius: BorderRadius.circular(d.cornerLarge),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Semantics(
                      header: true,
                      child: Text(
                        rejected
                            ? a(a.l.privacyRejectedTitle)
                            : a(a.l.privacyTitle),
                        textAlign: TextAlign.center,
                        style: t.typography.titleLarge.copyWith(
                          color: t.colors.textPrimary,
                        ),
                      ),
                    ),
                    SizedBox(height: d.spacing16),
                    Text(
                      rejected
                          ? a(a.l.privacyRejectedBody)
                          : a(a.l.privacySummary),
                      style: t.typography.body.copyWith(
                        color: t.colors.textSecondary,
                      ),
                    ),
                    SizedBox(height: d.spacing8),
                    links,
                    SizedBox(height: d.spacing16),
                    if (rejected) ...[
                      VkButton(
                        label: a(a.l.privacyShowAgain),
                        onPressed: onShowAgain,
                      ),
                      SizedBox(height: d.spacing8),
                      VkButton(
                        label: a(a.l.privacyExit),
                        variant: VkButtonVariant.text,
                        onPressed: onExit,
                      ),
                    ] else ...[
                      VkButton(
                        label: a(a.l.privacyAgree),
                        onPressed: onAgree,
                      ),
                      SizedBox(height: d.spacing8),
                      VkButton(
                        label: a(a.l.privacyDisagree),
                        variant: VkButtonVariant.text,
                        onPressed: onDisagree,
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Full text of the privacy policy or the terms (draft text from ARB until
/// the final text is supplied).
class PolicyPage extends StatelessWidget {
  /// Creates the page.
  const PolicyPage({super.key, this.terms = false});

  /// Terms instead of the policy.
  final bool terms;

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
          terms ? a(a.l.privacyTermsTitle) : a(a.l.privacyPolicyTitle),
          style: t.typography.titleLarge.copyWith(color: t.colors.textPrimary),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsetsDirectional.all(d.spacing16),
          child: Text(
            terms ? a(a.l.privacyTermsText) : a(a.l.privacyPolicyText),
            style: t.typography.body.copyWith(color: t.colors.textPrimary),
          ),
        ),
      ),
    );
  }
}
