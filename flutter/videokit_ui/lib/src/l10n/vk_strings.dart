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
    'playerBack': l10n.playerBack,
    'playerSpeed': l10n.playerSpeed,
    'playerSubtitles': l10n.playerSubtitles,
    'playerAudioTrack': l10n.playerAudioTrack,
    'playerVolume': l10n.playerVolume,
    'playerMute': l10n.playerMute,
    'playerUnmute': l10n.playerUnmute,
    'playerLockOrientation': l10n.playerLockOrientation,
    'playerUnlockOrientation': l10n.playerUnlockOrientation,
    'playerFullscreen': l10n.playerFullscreen,
    'playerExitFullscreen': l10n.playerExitFullscreen,
    'playerEdit': l10n.playerEdit,
    'playerRotate': l10n.playerRotate,
    'playerSeekBar': l10n.playerSeekBar,
    'playerPicture': l10n.playerPicture,
    'fitModeFit': l10n.fitModeFit,
    'fitModeFill': l10n.fitModeFill,
    'fitModeOriginal': l10n.fitModeOriginal,
    'settingsTitle': l10n.settingsTitle,
    'tracksUnsupported': l10n.tracksUnsupported,
    'stateLoadingTitle': l10n.stateLoadingTitle,
    'stateLoadingDetail': l10n.stateLoadingDetail,
    'stateEndedTitle': l10n.stateEndedTitle,
    'actionReplay': l10n.actionReplay,
    'stateReleasedTitle': l10n.stateReleasedTitle,
    'stateLockedTitle': l10n.stateLockedTitle,
    'stateDetailConnection': l10n.stateDetailConnection,
    'stateDetailPermission': l10n.stateDetailPermission,
    'stateDetailUnsupported': l10n.stateDetailUnsupported,
    'stateDetailCorrupt': l10n.stateDetailCorrupt,
    'stateDetailResources': l10n.stateDetailResources,
    'stateDetailTrackingLost': l10n.stateDetailTrackingLost,
    'stateDetailSpace': l10n.stateDetailSpace,
    'stateDetailGeneric': l10n.stateDetailGeneric,
    'hostActionMore': l10n.hostActionMore,
    'navigationUnavailable': l10n.navigationUnavailable,
    'commandUnavailable': l10n.commandUnavailable,
    'moreGroupPlayer': l10n.moreGroupPlayer,
    'viewerPicture': l10n.viewerPicture,
    'viewerInfo': l10n.viewerInfo,
    'viewerZoomLabel': l10n.viewerZoomLabel,
    'viewerMiniMap': l10n.viewerMiniMap,
    'viewerPrevious': l10n.viewerPrevious,
    'viewerNext': l10n.viewerNext,
    'viewerLoop': l10n.viewerLoop,
    'infoFormat': l10n.infoFormat,
    'infoDimensions': l10n.infoDimensions,
    'infoFileSize': l10n.infoFileSize,
    'infoOrientation': l10n.infoOrientation,
    'infoUnknown': l10n.infoUnknown,
    'infoFrameCount': l10n.infoFrameCount,
    'infoDecodedMemory': l10n.infoDecodedMemory,
    'infoSampleSize': l10n.infoSampleSize,
    'infoSampleFull': l10n.infoSampleFull,
    'imageKindStatic': l10n.imageKindStatic,
    'imageKindAnimated': l10n.imageKindAnimated,
    'orientationPortrait': l10n.orientationPortrait,
    'orientationLandscape': l10n.orientationLandscape,
    'orientationSquare': l10n.orientationSquare,
    'slotActiveAudio': l10n.slotActiveAudio,
    'slotActivateAudio': l10n.slotActivateAudio,
    'slotImage': l10n.slotImage,
    'slotAnimated': l10n.slotAnimated,
    'slotLoading': l10n.slotLoading,
    'slotPausedTitle': l10n.slotPausedTitle,
    'slotPausedDetail': l10n.slotPausedDetail,
    'slotLowResolution': l10n.slotLowResolution,
    'slotErrorOnly': l10n.slotErrorOnly,
    'slotRemove': l10n.slotRemove,
    'gridMuteAll': l10n.gridMuteAll,
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
    'playerRewind',
    'playerForward',
    'playerSpeedValue',
    'playerFitMode',
    'trackUnnamed',
    'hostActionFailed',
    'badgeClipped',
    'viewerAnimatedBadge',
    'infoFormatValue',
    'infoDimensionsValue',
    'slotLabel',
    'infoFrameCountValue',
    'infoSampleSizeValue',
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

  /// Rewind button label.
  String rewind(int seconds) => _out(l10n.playerRewind(seconds));

  /// Forward button label.
  String forward(int seconds) => _out(l10n.playerForward(seconds));

  /// Speed value, e.g. 1.5×; [speed] is pre-formatted.
  String speedValue(String speed) => _out(l10n.playerSpeedValue(speed));

  /// Fit mode notice.
  String fitModeNotice(String mode) => _out(l10n.playerFitMode(mode));

  /// Name of an unlabeled track.
  String trackUnnamed(int index) => _out(l10n.trackUnnamed(index));

  /// Badge text cut to the first characters.
  String badgeClipped(String text) => l10n.badgeClipped(text);

  /// Animated image badge ("GIF · 动态").
  String viewerAnimatedBadge(String format) =>
      _out(l10n.viewerAnimatedBadge(format));

  /// Format row value.
  String infoFormatValue(String format, String kind) =>
      _out(l10n.infoFormatValue(format, kind));

  /// Pixel dimensions row value.
  String infoDimensionsValue(int width, int height) =>
      _out(l10n.infoDimensionsValue(width, height));

  /// Frame count value (ICU plural).
  String infoFrameCountValue(int count) =>
      _out(l10n.infoFrameCountValue(count));

  /// Decode sample size value (> 1).
  String infoSampleSizeValue(int size) => _out(l10n.infoSampleSizeValue(size));

  /// Slot screen-reader label.
  String slotLabel(int index, String title) =>
      _out(l10n.slotLabel(index, title));

  /// Host action failure notice.
  String hostActionFailed(String action) => _out(l10n.hostActionFailed(action));

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
    SuggestedAction.checkPermission => l10n.actionCheckPermission,
    SuggestedAction.reconnectSource => l10n.actionReconnectSource,
    SuggestedAction.closeOtherSessions => l10n.actionCloseOtherSessions,
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
    ErrorCode.invalidState => l10n.errorInvalidState,
    ErrorCode.invalidArgument => l10n.errorInvalidArgument,
    ErrorCode.unsupportedSnapshotVersion =>
      l10n.errorUnsupportedSnapshotVersion,
  };
}
