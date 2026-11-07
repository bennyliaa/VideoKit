import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'videokit_localizations_zh.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of VideoKitLocalizations
/// returned by `VideoKitLocalizations.of(context)`.
///
/// Applications need to include `VideoKitLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'gen/videokit_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: VideoKitLocalizations.localizationsDelegates,
///   supportedLocales: VideoKitLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the VideoKitLocalizations.supportedLocales
/// property.
abstract class VideoKitLocalizations {
  VideoKitLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static VideoKitLocalizations of(BuildContext context) {
    return Localizations.of<VideoKitLocalizations>(
      context,
      VideoKitLocalizations,
    )!;
  }

  static const LocalizationsDelegate<VideoKitLocalizations> delegate =
      _VideoKitLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[Locale('zh')];

  /// Fake/演示后端驱动时常驻的标识（03 §8.3）。
  ///
  /// In zh, this message translates to:
  /// **'演示模式 · 模拟数据'**
  String get demoModeBadge;

  /// 模拟导出成功时追加的说明（03 §8.3）。
  ///
  /// In zh, this message translates to:
  /// **'演示模式：未生成真实媒体文件'**
  String get demoExportNoFile;

  /// 通用确认按钮。
  ///
  /// In zh, this message translates to:
  /// **'确定'**
  String get commonOk;

  /// 通用取消按钮。
  ///
  /// In zh, this message translates to:
  /// **'取消'**
  String get commonCancel;

  /// 关闭面板或浮层。
  ///
  /// In zh, this message translates to:
  /// **'关闭'**
  String get commonClose;

  /// 重试失败的操作。
  ///
  /// In zh, this message translates to:
  /// **'重试'**
  String get commonRetry;

  /// 溢出菜单按钮。
  ///
  /// In zh, this message translates to:
  /// **'更多'**
  String get commonMore;

  /// 加载中。
  ///
  /// In zh, this message translates to:
  /// **'正在加载…'**
  String get stateLoading;

  /// 缓冲中。
  ///
  /// In zh, this message translates to:
  /// **'正在缓冲…'**
  String get stateBuffering;

  /// 控件不可用时的读屏状态与提示。
  ///
  /// In zh, this message translates to:
  /// **'不可用'**
  String get stateUnavailable;

  /// 宿主动作等待中的读屏状态。
  ///
  /// In zh, this message translates to:
  /// **'等待中'**
  String get statePending;

  /// 选中项的读屏状态。
  ///
  /// In zh, this message translates to:
  /// **'已选中'**
  String get stateSelected;

  /// 播放按钮。
  ///
  /// In zh, this message translates to:
  /// **'播放'**
  String get playerPlay;

  /// 暂停按钮。
  ///
  /// In zh, this message translates to:
  /// **'暂停'**
  String get playerPause;

  /// 播放中的读屏状态。
  ///
  /// In zh, this message translates to:
  /// **'播放中'**
  String get playerPlaying;

  /// 进度条读屏值，如“1 分 5 秒，共 12 分 30 秒”。
  ///
  /// In zh, this message translates to:
  /// **'{position}，共 {duration}'**
  String playerSeekValue(String position, String duration);

  /// 关闭字幕的选项。
  ///
  /// In zh, this message translates to:
  /// **'关闭'**
  String get tracksSubtitlesOff;

  /// 音轨列表为空（14 §5.2）。
  ///
  /// In zh, this message translates to:
  /// **'此视频没有可选音轨'**
  String get tracksNoAudio;

  /// 字幕列表为空（14 §5.2）。
  ///
  /// In zh, this message translates to:
  /// **'此视频没有字幕'**
  String get tracksNoSubtitles;

  /// 无法预估时长/大小时显示，不显示假数字（14 §5.6）。
  ///
  /// In zh, this message translates to:
  /// **'无法预估'**
  String get estimateUnavailable;

  /// 读屏用时长。
  ///
  /// In zh, this message translates to:
  /// **'{hours, plural, =0{} other{{hours} 小时 }}{minutes, plural, =0{} other{{minutes} 分 }}{seconds} 秒'**
  String durationSpoken(int hours, int minutes, int seconds);

  /// 文件大小（字节）。
  ///
  /// In zh, this message translates to:
  /// **'{value} 字节'**
  String fileSizeBytes(String value);

  /// 文件大小（KB）。
  ///
  /// In zh, this message translates to:
  /// **'{value} KB'**
  String fileSizeKilobytes(String value);

  /// 文件大小（MB）。
  ///
  /// In zh, this message translates to:
  /// **'{value} MB'**
  String fileSizeMegabytes(String value);

  /// 文件大小（GB）。
  ///
  /// In zh, this message translates to:
  /// **'{value} GB'**
  String fileSizeGigabytes(String value);

  /// 建议操作 RETRY。
  ///
  /// In zh, this message translates to:
  /// **'重试'**
  String get actionRetry;

  /// 建议操作 CHOOSE_OTHER_TRACK。
  ///
  /// In zh, this message translates to:
  /// **'选择其他音轨'**
  String get actionChooseOtherTrack;

  /// 建议操作 REDUCE_QUALITY。
  ///
  /// In zh, this message translates to:
  /// **'降低质量'**
  String get actionReduceQuality;

  /// 建议操作 FREE_SPACE。
  ///
  /// In zh, this message translates to:
  /// **'释放空间'**
  String get actionFreeSpace;

  /// 建议操作 GRANT_PERMISSION。
  ///
  /// In zh, this message translates to:
  /// **'授予访问权限'**
  String get actionGrantPermission;

  /// 建议操作 CORRECT_TRACKING。
  ///
  /// In zh, this message translates to:
  /// **'纠正目标'**
  String get actionCorrectTracking;

  /// 建议操作 CHOOSE_OTHER_SOURCE。
  ///
  /// In zh, this message translates to:
  /// **'选择其他文件'**
  String get actionChooseOtherSource;

  /// ErrorCode SOURCE_NOT_FOUND。
  ///
  /// In zh, this message translates to:
  /// **'找不到文件'**
  String get errorSourceNotFound;

  /// ErrorCode SOURCE_PERMISSION_DENIED。
  ///
  /// In zh, this message translates to:
  /// **'无权访问此文件'**
  String get errorSourcePermissionDenied;

  /// ErrorCode SOURCE_DISCONNECTED。
  ///
  /// In zh, this message translates to:
  /// **'连接中断'**
  String get errorSourceDisconnected;

  /// ErrorCode SOURCE_TIMEOUT。
  ///
  /// In zh, this message translates to:
  /// **'连接超时'**
  String get errorSourceTimeout;

  /// ErrorCode UNSUPPORTED_CONTAINER。
  ///
  /// In zh, this message translates to:
  /// **'不支持此格式（容器）'**
  String get errorUnsupportedContainer;

  /// ErrorCode UNSUPPORTED_VIDEO_CODEC。
  ///
  /// In zh, this message translates to:
  /// **'不支持此格式（视频编码）'**
  String get errorUnsupportedVideoCodec;

  /// ErrorCode UNSUPPORTED_AUDIO_CODEC。
  ///
  /// In zh, this message translates to:
  /// **'不支持此格式（音频编码）'**
  String get errorUnsupportedAudioCodec;

  /// ErrorCode DECODER_UNAVAILABLE。
  ///
  /// In zh, this message translates to:
  /// **'此设备没有可用的解码器'**
  String get errorDecoderUnavailable;

  /// ErrorCode DECODER_RESOURCE_EXHAUSTED。
  ///
  /// In zh, this message translates to:
  /// **'资源不足，已暂停'**
  String get errorDecoderResourceExhausted;

  /// ErrorCode CORRUPT_MEDIA。
  ///
  /// In zh, this message translates to:
  /// **'文件已损坏或不完整'**
  String get errorCorruptMedia;

  /// ErrorCode SEEK_UNSUPPORTED。
  ///
  /// In zh, this message translates to:
  /// **'此来源不支持跳转'**
  String get errorSeekUnsupported;

  /// ErrorCode OUTPUT_PERMISSION_DENIED。
  ///
  /// In zh, this message translates to:
  /// **'无权保存输出'**
  String get errorOutputPermissionDenied;

  /// ErrorCode OUTPUT_SPACE_INSUFFICIENT。
  ///
  /// In zh, this message translates to:
  /// **'存储空间不足'**
  String get errorOutputSpaceInsufficient;

  /// ErrorCode OUTPUT_CAPABILITY_UNSUPPORTED。
  ///
  /// In zh, this message translates to:
  /// **'目标位置无法保存此输出'**
  String get errorOutputCapabilityUnsupported;

  /// ErrorCode ENCODER_UNAVAILABLE。
  ///
  /// In zh, this message translates to:
  /// **'此预设没有可用的编码器'**
  String get errorEncoderUnavailable;

  /// ErrorCode EXPORT_FAILED。
  ///
  /// In zh, this message translates to:
  /// **'导出失败'**
  String get errorExportFailed;

  /// ErrorCode TRACKING_MODEL_UNAVAILABLE。
  ///
  /// In zh, this message translates to:
  /// **'此设备不支持跟踪'**
  String get errorTrackingModelUnavailable;

  /// ErrorCode TRACKING_LOST。
  ///
  /// In zh, this message translates to:
  /// **'跟踪丢失'**
  String get errorTrackingLost;

  /// ErrorCode CANCELLED。
  ///
  /// In zh, this message translates to:
  /// **'已取消'**
  String get errorCancelled;

  /// ErrorCode HOST_CALLBACK_FAILED。
  ///
  /// In zh, this message translates to:
  /// **'操作未响应'**
  String get errorHostCallbackFailed;

  /// ErrorCode SESSION_RELEASED。
  ///
  /// In zh, this message translates to:
  /// **'播放已结束'**
  String get errorSessionReleased;

  /// ErrorCode INTERNAL_ERROR_REDACTED 及任何未知错误码。
  ///
  /// In zh, this message translates to:
  /// **'出现问题'**
  String get errorInternalErrorRedacted;
}

class _VideoKitLocalizationsDelegate
    extends LocalizationsDelegate<VideoKitLocalizations> {
  const _VideoKitLocalizationsDelegate();

  @override
  Future<VideoKitLocalizations> load(Locale locale) {
    return SynchronousFuture<VideoKitLocalizations>(
      lookupVideoKitLocalizations(locale),
    );
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['zh'].contains(locale.languageCode);

  @override
  bool shouldReload(_VideoKitLocalizationsDelegate old) => false;
}

VideoKitLocalizations lookupVideoKitLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'zh':
      return VideoKitLocalizationsZh();
  }

  throw FlutterError(
    'VideoKitLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
