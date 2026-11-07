import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:videokit_api/videokit_api.dart';

import 'gen/videokit_localizations.dart';
import 'pseudo.dart';

/// Delegates hosts add to their app (VideoKit strings + Flutter's own).
const List<LocalizationsDelegate<Object>> videoKitLocalizationsDelegates = [
  VideoKitLocalizations.delegate,
  GlobalMaterialLocalizations.delegate,
  GlobalWidgetsLocalizations.delegate,
  GlobalCupertinoLocalizations.delegate,
];

/// Locales hosts list in `supportedLocales`: Chinese plus the pseudo locale
/// for layout checks.
const List<Locale> videoKitSupportedLocales = [Locale('zh'), VkPseudo.locale];

/// Locale resolution for hosts (13 §3.1): first version shows Chinese for
/// every system language; the pseudo locale is kept as is.
Locale videoKitResolveLocale(Locale? locale, Iterable<Locale> supported) =>
    VkPseudo.isPseudo(locale) ? VkPseudo.locale : const Locale('zh');

/// Host string overrides keyed by ARB key (03 §5.1 `VideoKitStrings`,
/// 14 §9.1 `strings`). Overrides change text only, never state or
/// semantics roles; missing keys fall back to the localized defaults.
class VideoKitStrings extends InheritedWidget {
  /// Creates an override scope.
  const VideoKitStrings({
    super.key,
    required this.overrides,
    required super.child,
  });

  /// ARB key → text.
  final Map<String, String> overrides;

  /// Nearest overrides, or empty.
  static Map<String, String> overridesOf(BuildContext context) =>
      context
          .dependOnInheritedWidgetOfExactType<VideoKitStrings>()
          ?.overrides ??
      const {};

  @override
  bool updateShouldNotify(VideoKitStrings oldWidget) =>
      oldWidget.overrides != overrides;
}

/// Resolved strings for components: ARB text + host overrides, pseudo
/// transformed under [VkPseudo.locale]. Works without the host registering
/// the delegate; fallback language is Chinese (13 §3.1).
final class VkStrings {
  VkStrings._(this.l10n, this._overrides, {required this.pseudo});

  /// Strings for [context].
  factory VkStrings.of(BuildContext context) {
    final locale = Localizations.maybeLocaleOf(context);
    final l = Localizations.of<VideoKitLocalizations>(
      context,
      VideoKitLocalizations,
    );
    return VkStrings._(
      l ?? _fallback(),
      VideoKitStrings.overridesOf(context),
      pseudo: VkPseudo.isPseudo(locale),
    );
  }

  /// Strings for [locale] without a widget tree (tests, native bridge).
  factory VkStrings.forLocale(
    Locale locale, [
    Map<String, String> overrides = const {},
  ]) => VkStrings._(_fallback(), overrides, pseudo: VkPseudo.isPseudo(locale));

  static VideoKitLocalizations _fallback() =>
      lookupVideoKitLocalizations(const Locale('zh'));

  /// Generated localizations.
  final VideoKitLocalizations l10n;
  final Map<String, String> _overrides;

  /// Whether pseudo-localization is active.
  final bool pseudo;

  /// intl locale name used for number formatting.
  String get intlLocale => l10n.localeName;

  String _out(String s) => pseudo ? VkPseudo.transform(s) : s;

  /// Every placeholder-free ARB key with its value (before pseudo).
  Map<String, String> get defaults => {
    'demoModeBadge': l10n.demoModeBadge,
    'demoExportNoFile': l10n.demoExportNoFile,
    'commonOk': l10n.commonOk,
    'commonCancel': l10n.commonCancel,
    'commonClose': l10n.commonClose,
    'commonRetry': l10n.commonRetry,
    'commonMore': l10n.commonMore,
    'stateLoading': l10n.stateLoading,
    'stateBuffering': l10n.stateBuffering,
    'stateUnavailable': l10n.stateUnavailable,
    'statePending': l10n.statePending,
    'stateSelected': l10n.stateSelected,
    'playerPlay': l10n.playerPlay,
    'playerPause': l10n.playerPause,
    'playerPlaying': l10n.playerPlaying,
    'tracksSubtitlesOff': l10n.tracksSubtitlesOff,
    'tracksNoAudio': l10n.tracksNoAudio,
    'tracksNoSubtitles': l10n.tracksNoSubtitles,
    'estimateUnavailable': l10n.estimateUnavailable,
    for (final a in SuggestedAction.values)
      if (a != SuggestedAction.none) actionKey(a): _action(a),
    for (final c in ErrorCode.values) errorKey(c): _error(c),
  };

  /// ARB keys that take placeholders.
  static const Set<String> placeholderKeys = {
    'playerSeekValue',
    'durationSpoken',
    'fileSizeBytes',
    'fileSizeKilobytes',
    'fileSizeMegabytes',
    'fileSizeGigabytes',
  };

  /// Text for [key]: override, else localized default, else [key].
  String text(String key) => _out(_overrides[key] ?? defaults[key] ?? key);

  /// ARB key of [code], e.g. `errorSourceNotFound`.
  static String errorKey(ErrorCode code) => 'error${_pascal(code.name)}';

  /// ARB key of [action], e.g. `actionFreeSpace`.
  static String actionKey(SuggestedAction action) =>
      'action${_pascal(action.name)}';

  static String _pascal(String s) => s[0].toUpperCase() + s.substring(1);

  /// Title for an error code (unknown codes already map to
  /// `internalErrorRedacted` in the API).
  String error(ErrorCode code) =>
      _out(_overrides[errorKey(code)] ?? _error(code));

  /// Label for a suggested action; null for [SuggestedAction.none].
  String? action(SuggestedAction action) => action == SuggestedAction.none
      ? null
      : _out(_overrides[actionKey(action)] ?? _action(action));

  /// Demo badge text.
  String get demoBadge => text('demoModeBadge');

  /// Seek bar semantics value.
  String seekValue(String position, String duration) =>
      _out(l10n.playerSeekValue(position, duration));

  /// Spoken duration (ICU plural).
  String durationSpoken(int hours, int minutes, int seconds) =>
      _out(l10n.durationSpoken(hours, minutes, seconds).trim());

  /// File size with a formatted [value] in [unit] (0 B, 1 KB, 2 MB, 3 GB).
  String fileSize(String value, int unit) => _out(switch (unit) {
    0 => l10n.fileSizeBytes(value),
    1 => l10n.fileSizeKilobytes(value),
    2 => l10n.fileSizeMegabytes(value),
    _ => l10n.fileSizeGigabytes(value),
  });

  String _action(SuggestedAction a) => switch (a) {
    SuggestedAction.retry => l10n.actionRetry,
    SuggestedAction.chooseOtherTrack => l10n.actionChooseOtherTrack,
    SuggestedAction.reduceQuality => l10n.actionReduceQuality,
    SuggestedAction.freeSpace => l10n.actionFreeSpace,
    SuggestedAction.grantPermission => l10n.actionGrantPermission,
    SuggestedAction.correctTracking => l10n.actionCorrectTracking,
    SuggestedAction.chooseOtherSource => l10n.actionChooseOtherSource,
    SuggestedAction.none => '',
  };

  String _error(ErrorCode c) => switch (c) {
    ErrorCode.sourceNotFound => l10n.errorSourceNotFound,
    ErrorCode.sourcePermissionDenied => l10n.errorSourcePermissionDenied,
    ErrorCode.sourceDisconnected => l10n.errorSourceDisconnected,
    ErrorCode.sourceTimeout => l10n.errorSourceTimeout,
    ErrorCode.unsupportedContainer => l10n.errorUnsupportedContainer,
    ErrorCode.unsupportedVideoCodec => l10n.errorUnsupportedVideoCodec,
    ErrorCode.unsupportedAudioCodec => l10n.errorUnsupportedAudioCodec,
    ErrorCode.decoderUnavailable => l10n.errorDecoderUnavailable,
    ErrorCode.decoderResourceExhausted => l10n.errorDecoderResourceExhausted,
    ErrorCode.corruptMedia => l10n.errorCorruptMedia,
    ErrorCode.seekUnsupported => l10n.errorSeekUnsupported,
    ErrorCode.outputPermissionDenied => l10n.errorOutputPermissionDenied,
    ErrorCode.outputSpaceInsufficient => l10n.errorOutputSpaceInsufficient,
    ErrorCode.outputCapabilityUnsupported =>
      l10n.errorOutputCapabilityUnsupported,
    ErrorCode.encoderUnavailable => l10n.errorEncoderUnavailable,
    ErrorCode.exportFailed => l10n.errorExportFailed,
    ErrorCode.trackingModelUnavailable => l10n.errorTrackingModelUnavailable,
    ErrorCode.trackingLost => l10n.errorTrackingLost,
    ErrorCode.cancelled => l10n.errorCancelled,
    ErrorCode.hostCallbackFailed => l10n.errorHostCallbackFailed,
    ErrorCode.sessionReleased => l10n.errorSessionReleased,
    ErrorCode.internalErrorRedacted => l10n.errorInternalErrorRedacted,
  };
}
