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
    'playerMediaInfo': l10n.playerMediaInfo,
    'infoVideoCodec': l10n.infoVideoCodec,
    'infoAudioCodec': l10n.infoAudioCodec,
    'infoResolution': l10n.infoResolution,
    'infoFrameRate': l10n.infoFrameRate,
    'infoBitrate': l10n.infoBitrate,
    'infoRotation': l10n.infoRotation,
    'infoDuration': l10n.infoDuration,
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
    'slotPausedShort': l10n.slotPausedShort,
    'slotLowResolution': l10n.slotLowResolution,
    'slotErrorOnly': l10n.slotErrorOnly,
    'slotRemove': l10n.slotRemove,
    'gridMuteAll': l10n.gridMuteAll,
    'editorTitle': l10n.editorTitle,
    'editorUndo': l10n.editorUndo,
    'editorRedo': l10n.editorRedo,
    'editorExport': l10n.editorExport,
    'editorAddVideo': l10n.editorAddVideo,
    'editorSplit': l10n.editorSplit,
    'editorDelete': l10n.editorDelete,
    'editorReorder': l10n.editorReorder,
    'editorMask': l10n.editorMask,
    'editorTrack': l10n.editorTrack,
    'editorTrackShort': l10n.editorTrackShort,
    'editorClipsTab': l10n.editorClipsTab,
    'editorAddTab': l10n.editorAddTab,
    'editorNoSelection': l10n.editorNoSelection,
    'editorEmpty': l10n.editorEmpty,
    'propSource': l10n.propSource,
    'propIn': l10n.propIn,
    'propOut': l10n.propOut,
    'propDuration': l10n.propDuration,
    'keyframeAlignNotice': l10n.keyframeAlignNotice,
    'concatFast': l10n.concatFast,
    'concatTranscodeTitle': l10n.concatTranscodeTitle,
    'fastConcatAvailable': l10n.fastConcatAvailable,
    'fastConcatUnavailable': l10n.fastConcatUnavailable,
    'estimateUnknown': l10n.estimateUnknown,
    'timelineLabel': l10n.timelineLabel,
    'timelineZoomIn': l10n.timelineZoomIn,
    'timelineZoomOut': l10n.timelineZoomOut,
    'clipMoveEarlier': l10n.clipMoveEarlier,
    'clipMoveLater': l10n.clipMoveLater,
    'clipTrimStart': l10n.clipTrimStart,
    'clipTrimEnd': l10n.clipTrimEnd,
    'sourcesTitle': l10n.sourcesTitle,
    'maskTitle': l10n.maskTitle,
    'maskDone': l10n.maskDone,
    'maskListTitle': l10n.maskListTitle,
    'maskAdd': l10n.maskAdd,
    'maskKeyframesTracker': l10n.maskKeyframesTracker,
    'maskTypeManual': l10n.maskTypeManual,
    'maskTypeFace': l10n.maskTypeFace,
    'maskTypeObject': l10n.maskTypeObject,
    'maskStyle': l10n.maskStyle,
    'maskStyleMosaic': l10n.maskStyleMosaic,
    'maskStyleBlur': l10n.maskStyleBlur,
    'maskStrength': l10n.maskStrength,
    'maskDelete': l10n.maskDelete,
    'maskEnable': l10n.maskEnable,
    'maskAddKeyframe': l10n.maskAddKeyframe,
    'maskRemoveKeyframe': l10n.maskRemoveKeyframe,
    'maskBox': l10n.maskBox,
    'maskBoxHint': l10n.maskBoxHint,
    'maskNone': l10n.maskNone,
    'trackLocalOnly': l10n.trackLocalOnly,
    'trackDetectFaces': l10n.trackDetectFaces,
    'trackChooseHint': l10n.trackChooseHint,
    'trackTapToSelect': l10n.trackTapToSelect,
    'trackObject': l10n.trackObject,
    'trackObjectHint': l10n.trackObjectHint,
    'trackRunning': l10n.trackRunning,
    'trackAnalyzing': l10n.trackAnalyzing,
    'trackCancel': l10n.trackCancel,
    'trackCompleted': l10n.trackCompleted,
    'trackCancelled': l10n.trackCancelled,
    'trackFailed': l10n.trackFailed,
    'coverageTracked': l10n.coverageTracked,
    'coverageLow': l10n.coverageLow,
    'coverageAmbiguous': l10n.coverageAmbiguous,
    'coverageLost': l10n.coverageLost,
    'coverageNotAnalyzed': l10n.coverageNotAnalyzed,
    'coverageAccepted': l10n.coverageAccepted,
    'trackCorrect': l10n.trackCorrect,
    'trackCorrectHint': l10n.trackCorrectHint,
    'trackRecomputing': l10n.trackRecomputing,
    'checkSubtitle': l10n.checkSubtitle,
    'checkJump': l10n.checkJump,
    'checkManual': l10n.checkManual,
    'checkFullFrame': l10n.checkFullFrame,
    'checkBack': l10n.checkBack,
    'checkForce': l10n.checkForce,
    'exportTitle': l10n.exportTitle,
    'exportPresets': l10n.exportPresets,
    'presetOriginal': l10n.presetOriginal,
    'presetOriginalDetail': l10n.presetOriginalDetail,
    'preset1080': l10n.preset1080,
    'preset720': l10n.preset720,
    'presetUnavailable': l10n.presetUnavailable,
    'exportChecks': l10n.exportChecks,
    'checkEncoder': l10n.checkEncoder,
    'checkEncoderOk': l10n.checkEncoderOk,
    'checkEncoderFail': l10n.checkEncoderFail,
    'checkOutput': l10n.checkOutput,
    'checkOutputOk': l10n.checkOutputOk,
    'checkOutputFail': l10n.checkOutputFail,
    'checkSpace': l10n.checkSpace,
    'checkSpaceUnknown': l10n.checkSpaceUnknown,
    'checkSpaceFail': l10n.checkSpaceFail,
    'checkCoverage': l10n.checkCoverage,
    'checkCoverageOk': l10n.checkCoverageOk,
    'checkCoverageNone': l10n.checkCoverageNone,
    'checkPassed': l10n.checkPassed,
    'checkProblem': l10n.checkProblem,
    'checkRunning': l10n.checkRunning,
    'exportSafety': l10n.exportSafety,
    'exportStart': l10n.exportStart,
    'exportReviewCoverage': l10n.exportReviewCoverage,
    'exporting': l10n.exporting,
    'stagePreparing': l10n.stagePreparing,
    'stageTracking': l10n.stageTracking,
    'stageEncoding': l10n.stageEncoding,
    'stageVerifying': l10n.stageVerifying,
    'stageWriting': l10n.stageWriting,
    'stageDone': l10n.stageDone,
    'stageWaiting': l10n.stageWaiting,
    'stageInProgress': l10n.stageInProgress,
    'exportNoPause': l10n.exportNoPause,
    'exportCancel': l10n.exportCancel,
    'exportCancelling': l10n.exportCancelling,
    'exportCancelled': l10n.exportCancelled,
    'exportCancelledPartial': l10n.exportCancelledPartial,
    'exportFailedTitle': l10n.exportFailedTitle,
    'exportImpactSource': l10n.exportImpactSource,
    'exportImpactDiscarded': l10n.exportImpactDiscarded,
    'exportRetry': l10n.exportRetry,
    'exportBackToEdit': l10n.exportBackToEdit,
    'exportDoneTitle': l10n.exportDoneTitle,
    'exportDoneDetail': l10n.exportDoneDetail,
    'summaryFormat': l10n.summaryFormat,
    'summaryResolution': l10n.summaryResolution,
    'summaryDuration': l10n.summaryDuration,
    'summarySize': l10n.summarySize,
    'summaryWarnings': l10n.summaryWarnings,
    'warnBoundary': l10n.warnBoundary,
    'warnSilence': l10n.warnSilence,
    'warnCoverage': l10n.warnCoverage,
    'warnDemo': l10n.warnDemo,
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
    'infoFrameRateValue',
    'infoBitrateKbps',
    'infoBitrateMbps',
    'infoRotationValue',
    'editorClip',
    'editorClipProps',
    'editorClipSummary',
    'durationSeconds',
    'concatTranscodeDetail',
    'estimateLine',
    'estimateDurationOnly',
    'editorTime',
    'clipSemantic',
    'sourcesCount',
    'sourceMeta',
    'sourceRotated',
    'maskName',
    'maskNameTyped',
    'maskSummary',
    'maskKeyframes',
    'maskKeyframeTitle',
    'trackDetected',
    'trackTarget',
    'trackFace',
    'trackAnalyzed',
    'coverageStripLabel',
    'coverageSegment',
    'checkTitle',
    'checkRange',
    'presetLongEdge',
    'exportFormat',
    'checkSpaceValue',
    'checkSpaceNeed',
    'checkCoverageFail',
    'stageRemaining',
    'stageProcessed',
    'stageOutputSize',
    'exportErrorCode',
    'exportUseSmaller',
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

  /// Frame rate value; [value] is locale-formatted.
  String infoFrameRateValue(String value) =>
      _out(l10n.infoFrameRateValue(value));

  /// Bit rate value; [value] is locale-formatted, [mega] selects Mbps.
  String infoBitrateValue(String value, {required bool mega}) =>
      _out(mega ? l10n.infoBitrateMbps(value) : l10n.infoBitrateKbps(value));

  /// Rotation value in degrees.
  String infoRotationValue(int degrees) =>
      _out(l10n.infoRotationValue(degrees));

  /// 时间线片段名。
  String editorClip(int index) => _out(l10n.editorClip(index));

  /// 属性面板标题。
  String editorClipProps(int index) => _out(l10n.editorClipProps(index));

  /// 手机端选中片段卡片标题。
  String editorClipSummary(int index, String duration) =>
      _out(l10n.editorClipSummary(index, duration));

  /// 以秒表示的时长，例如“18.6 秒”。
  String durationSeconds(String seconds) => _out(l10n.durationSeconds(seconds));

  /// 不一致时的说明。
  String concatTranscodeDetail(int count) =>
      _out(l10n.concatTranscodeDetail(count));

  /// 预计输出时长与大小。
  String estimateLine(String duration, String size) =>
      _out(l10n.estimateLine(duration, size));

  /// 只能估算时长。
  String estimateDurationOnly(String duration) =>
      _out(l10n.estimateDurationOnly(duration));

  /// 预览时间。
  String editorTime(String position, String duration) =>
      _out(l10n.editorTime(position, duration));

  /// 片段的读屏描述。
  String clipSemantic(int index, String start, String end, String duration) =>
      _out(l10n.clipSemantic(index, start, end, duration));

  /// 视频数量。
  String sourcesCount(int count) => _out(l10n.sourcesCount(count));

  /// 视频参数。
  String sourceMeta(int width, int height, String fps, String codec) =>
      _out(l10n.sourceMeta(width, height, fps, codec));

  /// 视频带旋转元数据。
  String sourceRotated(int degrees) => _out(l10n.sourceRotated(degrees));

  /// 遮罩名称。
  String maskName(int index) => _out(l10n.maskName(index));

  /// 遮罩样式与时间范围。
  String maskSummary(String style, String start, String end) =>
      _out(l10n.maskSummary(style, start, end));

  /// 关键帧数量。
  String maskKeyframes(int count) => _out(l10n.maskKeyframes(count));

  /// 关键帧行标题。
  String maskKeyframeTitle(int index) => _out(l10n.maskKeyframeTitle(index));

  /// 检测结果。
  String trackDetected(int count) => _out(l10n.trackDetected(count));

  /// 已选目标。
  String trackTarget(String letter) => _out(l10n.trackTarget(letter));

  /// 未选人脸。
  String trackFace(int index) => _out(l10n.trackFace(index));

  /// 已分析时长。
  String trackAnalyzed(String done, String total) =>
      _out(l10n.trackAnalyzed(done, total));

  /// 状态轨道的读屏标签。
  String coverageStripLabel(String name) => _out(l10n.coverageStripLabel(name));

  /// 状态区间的读屏描述。
  String coverageSegment(String state, String start, String end) =>
      _out(l10n.coverageSegment(state, start, end));

  /// 导出前覆盖检查标题。
  String checkTitle(int count) => _out(l10n.checkTitle(count));

  /// 未覆盖区间。
  String checkRange(String name, String start, String end) =>
      _out(l10n.checkRange(name, start, end));

  /// 预设长边像素。
  String presetLongEdge(int px) => _out(l10n.presetLongEdge(px));

  /// 输出格式。
  String exportFormat(String format) => _out(l10n.exportFormat(format));

  /// 所需与可用空间。
  String checkSpaceValue(String need, String free) =>
      _out(l10n.checkSpaceValue(need, free));

  /// 只知道所需空间。
  String checkSpaceNeed(String need) => _out(l10n.checkSpaceNeed(need));

  /// 存在未覆盖区间。
  String checkCoverageFail(int count) => _out(l10n.checkCoverageFail(count));

  /// 剩余时间。
  String stageRemaining(String duration) => _out(l10n.stageRemaining(duration));

  /// 已处理时长。
  String stageProcessed(String done, String total) =>
      _out(l10n.stageProcessed(done, total));

  /// 已输出大小。
  String stageOutputSize(String size) => _out(l10n.stageOutputSize(size));

  /// 保留的错误代码。
  String exportErrorCode(String code) => _out(l10n.exportErrorCode(code));

  /// 降低质量重新导出。
  String exportUseSmaller(String preset) => _out(l10n.exportUseSmaller(preset));

  /// Mask list title with type.
  String maskNameTyped(int index, String type) =>
      _out(l10n.maskNameTyped(index, type));

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
