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

  /// 建议操作 CHECK_PERMISSION。
  ///
  /// In zh, this message translates to:
  /// **'检查访问权限'**
  String get actionCheckPermission;

  /// 建议操作 RECONNECT_SOURCE。
  ///
  /// In zh, this message translates to:
  /// **'重新连接'**
  String get actionReconnectSource;

  /// 建议操作 CLOSE_OTHER_SESSIONS（释放解码资源）。
  ///
  /// In zh, this message translates to:
  /// **'关闭其他画面'**
  String get actionCloseOtherSessions;

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

  /// ErrorCode INVALID_STATE（04A V7）。
  ///
  /// In zh, this message translates to:
  /// **'当前状态下无法执行此操作'**
  String get errorInvalidState;

  /// ErrorCode INVALID_ARGUMENT（04A V7）。
  ///
  /// In zh, this message translates to:
  /// **'参数无效'**
  String get errorInvalidArgument;

  /// ErrorCode UNSUPPORTED_SNAPSHOT_VERSION（快照或工程来自更新的版本，04A V7）。
  ///
  /// In zh, this message translates to:
  /// **'此版本无法打开该记录'**
  String get errorUnsupportedSnapshotVersion;

  /// 顶部栏返回按钮（由宿主处理）。
  ///
  /// In zh, this message translates to:
  /// **'返回'**
  String get playerBack;

  /// 快退按钮。
  ///
  /// In zh, this message translates to:
  /// **'后退 {seconds} 秒'**
  String playerRewind(int seconds);

  /// 快进按钮。
  ///
  /// In zh, this message translates to:
  /// **'前进 {seconds} 秒'**
  String playerForward(int seconds);

  /// 倍速按钮与设置页签。
  ///
  /// In zh, this message translates to:
  /// **'倍速'**
  String get playerSpeed;

  /// 倍速档位，如“1.5×”。
  ///
  /// In zh, this message translates to:
  /// **'{speed}×'**
  String playerSpeedValue(String speed);

  /// 字幕按钮与设置页签。
  ///
  /// In zh, this message translates to:
  /// **'字幕'**
  String get playerSubtitles;

  /// 音轨按钮与设置页签。
  ///
  /// In zh, this message translates to:
  /// **'音轨'**
  String get playerAudioTrack;

  /// 音量滑杆的读屏标签。
  ///
  /// In zh, this message translates to:
  /// **'音量'**
  String get playerVolume;

  /// 静音按钮。
  ///
  /// In zh, this message translates to:
  /// **'静音'**
  String get playerMute;

  /// 取消静音按钮。
  ///
  /// In zh, this message translates to:
  /// **'取消静音'**
  String get playerUnmute;

  /// 方向锁定按钮。
  ///
  /// In zh, this message translates to:
  /// **'锁定方向'**
  String get playerLockOrientation;

  /// 解除方向锁定按钮。
  ///
  /// In zh, this message translates to:
  /// **'解除方向锁定'**
  String get playerUnlockOrientation;

  /// 进入全屏按钮。
  ///
  /// In zh, this message translates to:
  /// **'全屏'**
  String get playerFullscreen;

  /// 退出全屏按钮。
  ///
  /// In zh, this message translates to:
  /// **'退出全屏'**
  String get playerExitFullscreen;

  /// 编辑入口按钮（带当前播放位置进入编辑器）。
  ///
  /// In zh, this message translates to:
  /// **'编辑'**
  String get playerEdit;

  /// 进度条的读屏标签。
  ///
  /// In zh, this message translates to:
  /// **'播放进度'**
  String get playerSeekBar;

  /// 画面层的读屏标签；轻触可显示或隐藏控件。
  ///
  /// In zh, this message translates to:
  /// **'视频画面'**
  String get playerPicture;

  /// 双击切换适配后的提示。
  ///
  /// In zh, this message translates to:
  /// **'画面适配：{mode}'**
  String playerFitMode(String mode);

  /// FitMode.FIT。
  ///
  /// In zh, this message translates to:
  /// **'适应'**
  String get fitModeFit;

  /// FitMode.FILL。
  ///
  /// In zh, this message translates to:
  /// **'填充'**
  String get fitModeFill;

  /// FitMode.ORIGINAL。
  ///
  /// In zh, this message translates to:
  /// **'原尺寸'**
  String get fitModeOriginal;

  /// 轨道与设置面板标题（UI-02）。
  ///
  /// In zh, this message translates to:
  /// **'播放设置'**
  String get settingsTitle;

  /// 设备无法解码的轨道标记，保留显示但置灰。
  ///
  /// In zh, this message translates to:
  /// **'设备不支持'**
  String get tracksUnsupported;

  /// 没有语言和标签的轨道名。
  ///
  /// In zh, this message translates to:
  /// **'轨道 {index}'**
  String trackUnnamed(int index);

  /// 加载中标题（设计稿第 12 页）。
  ///
  /// In zh, this message translates to:
  /// **'正在打开…'**
  String get stateLoadingTitle;

  /// 加载中说明；不显示假进度。
  ///
  /// In zh, this message translates to:
  /// **'读取媒体信息'**
  String get stateLoadingDetail;

  /// 播放结束。
  ///
  /// In zh, this message translates to:
  /// **'播放结束'**
  String get stateEndedTitle;

  /// 播放结束后的重播按钮。
  ///
  /// In zh, this message translates to:
  /// **'重新播放'**
  String get actionReplay;

  /// 会话已释放，控件只读。
  ///
  /// In zh, this message translates to:
  /// **'播放已关闭'**
  String get stateReleasedTitle;

  /// 锁屏隐藏内容时的遮挡层。
  ///
  /// In zh, this message translates to:
  /// **'内容已隐藏'**
  String get stateLockedTitle;

  /// 断线、超时的说明。
  ///
  /// In zh, this message translates to:
  /// **'请检查网络或存储连接后重试'**
  String get stateDetailConnection;

  /// 无权访问的说明（宿主处理授权）。
  ///
  /// In zh, this message translates to:
  /// **'请在应用中授予访问权限'**
  String get stateDetailPermission;

  /// 格式或编码不支持的说明。
  ///
  /// In zh, this message translates to:
  /// **'此设备无法播放该格式，详见能力说明'**
  String get stateDetailUnsupported;

  /// 文件损坏的说明。
  ///
  /// In zh, this message translates to:
  /// **'文件可能未完整下载或已损坏'**
  String get stateDetailCorrupt;

  /// 解码资源不足的说明。
  ///
  /// In zh, this message translates to:
  /// **'关闭其他画面后可以重试'**
  String get stateDetailResources;

  /// 跟踪丢失的说明。
  ///
  /// In zh, this message translates to:
  /// **'在丢失的区间重新指定目标'**
  String get stateDetailTrackingLost;

  /// 存储空间不足的说明。
  ///
  /// In zh, this message translates to:
  /// **'释放空间或降低导出质量'**
  String get stateDetailSpace;

  /// 其他错误的说明。
  ///
  /// In zh, this message translates to:
  /// **'如果问题持续出现，请稍后再试'**
  String get stateDetailGeneric;

  /// 宿主动作失败或超时的轻提示。
  ///
  /// In zh, this message translates to:
  /// **'“{action}”未完成'**
  String hostActionFailed(String action);

  /// 宿主动作溢出菜单按钮。
  ///
  /// In zh, this message translates to:
  /// **'更多操作'**
  String get hostActionMore;

  /// 宿主返回 UNAVAILABLE 时的轻提示。
  ///
  /// In zh, this message translates to:
  /// **'没有更多内容了'**
  String get navigationUnavailable;

  /// 命令返回 Unsupported 时的轻提示。
  ///
  /// In zh, this message translates to:
  /// **'此操作当前不可用'**
  String get commandUnavailable;

  /// 角标超过 3 个字符时截断显示。
  ///
  /// In zh, this message translates to:
  /// **'{text}…'**
  String badgeClipped(String text);

  /// 画面顺时针旋转 90°。
  ///
  /// In zh, this message translates to:
  /// **'旋转画面'**
  String get playerRotate;

  /// “更多”面板第二组（播放器自身的次要控件）的标题；第一组是宿主动作。
  ///
  /// In zh, this message translates to:
  /// **'播放控制'**
  String get moreGroupPlayer;

  /// 图片查看器画面层的读屏标签；轻触显示或隐藏控件。
  ///
  /// In zh, this message translates to:
  /// **'图片画面'**
  String get viewerPicture;

  /// 打开图片信息面板的按钮与面板标题。
  ///
  /// In zh, this message translates to:
  /// **'图片信息'**
  String get viewerInfo;

  /// 缩放比例指示的读屏标签。
  ///
  /// In zh, this message translates to:
  /// **'缩放比例'**
  String get viewerZoomLabel;

  /// 放大时右下角小地图的读屏标签。
  ///
  /// In zh, this message translates to:
  /// **'可见区域'**
  String get viewerMiniMap;

  /// 翻到上一张图片（向宿主请求）。
  ///
  /// In zh, this message translates to:
  /// **'上一张'**
  String get viewerPrevious;

  /// 翻到下一张图片（向宿主请求）。
  ///
  /// In zh, this message translates to:
  /// **'下一张'**
  String get viewerNext;

  /// 动图循环播放开关。
  ///
  /// In zh, this message translates to:
  /// **'循环播放'**
  String get viewerLoop;

  /// 动图角标，例如“GIF · 动态”。
  ///
  /// In zh, this message translates to:
  /// **'{format} · 动态'**
  String viewerAnimatedBadge(String format);

  /// 图片信息：格式。
  ///
  /// In zh, this message translates to:
  /// **'格式'**
  String get infoFormat;

  /// 图片信息：像素尺寸。
  ///
  /// In zh, this message translates to:
  /// **'尺寸'**
  String get infoDimensions;

  /// 图片信息：文件大小。
  ///
  /// In zh, this message translates to:
  /// **'文件大小'**
  String get infoFileSize;

  /// 图片信息：画面方向。
  ///
  /// In zh, this message translates to:
  /// **'方向'**
  String get infoOrientation;

  /// 信息项尚未得到或无法得到。
  ///
  /// In zh, this message translates to:
  /// **'未知'**
  String get infoUnknown;

  /// 格式与静态/动态，例如“GIF（动态）”。
  ///
  /// In zh, this message translates to:
  /// **'{format}（{kind}）'**
  String infoFormatValue(String format, String kind);

  /// 像素尺寸，例如“1280 × 1152”。
  ///
  /// In zh, this message translates to:
  /// **'{width} × {height}'**
  String infoDimensionsValue(int width, int height);

  /// 静态图片。
  ///
  /// In zh, this message translates to:
  /// **'静态'**
  String get imageKindStatic;

  /// 动态图片（GIF、动态 WebP）。
  ///
  /// In zh, this message translates to:
  /// **'动态'**
  String get imageKindAnimated;

  /// 画面方向：竖向。
  ///
  /// In zh, this message translates to:
  /// **'竖向'**
  String get orientationPortrait;

  /// 画面方向：横向。
  ///
  /// In zh, this message translates to:
  /// **'横向'**
  String get orientationLandscape;

  /// 画面方向：方形。
  ///
  /// In zh, this message translates to:
  /// **'方形'**
  String get orientationSquare;

  /// 多画面中当前唯一发声画面的角标。
  ///
  /// In zh, this message translates to:
  /// **'发声'**
  String get slotActiveAudio;

  /// 静音角标的读屏标签：点按请求让这一格发声。
  ///
  /// In zh, this message translates to:
  /// **'设为发声画面'**
  String get slotActivateAudio;

  /// 静态图片格的角标。
  ///
  /// In zh, this message translates to:
  /// **'图片'**
  String get slotImage;

  /// 动态图片格的角标。
  ///
  /// In zh, this message translates to:
  /// **'动图'**
  String get slotAnimated;

  /// 格内加载中的读屏文字。
  ///
  /// In zh, this message translates to:
  /// **'加载中'**
  String get slotLoading;

  /// 宿主为释放解码器暂停了这一格。
  ///
  /// In zh, this message translates to:
  /// **'已暂停 · 资源不足'**
  String get slotPausedTitle;

  /// 暂停格的说明。
  ///
  /// In zh, this message translates to:
  /// **'点按恢复（将暂停其他画面）'**
  String get slotPausedDetail;

  /// 降级角标：这一格以低分辨率播放。
  ///
  /// In zh, this message translates to:
  /// **'已降为低分辨率'**
  String get slotLowResolution;

  /// 单格错误占位的说明。
  ///
  /// In zh, this message translates to:
  /// **'仅此格受影响'**
  String get slotErrorOnly;

  /// 从多画面中移除出错的这一格。
  ///
  /// In zh, this message translates to:
  /// **'移除'**
  String get slotRemove;

  /// 格的读屏标签。
  ///
  /// In zh, this message translates to:
  /// **'第 {index} 格，{title}'**
  String slotLabel(int index, String title);

  /// 多画面全部静音。
  ///
  /// In zh, this message translates to:
  /// **'全部静音'**
  String get gridMuteAll;

  /// 图片信息：帧数（04A L2，有值才显示）。
  ///
  /// In zh, this message translates to:
  /// **'帧数'**
  String get infoFrameCount;

  /// 帧数的值。
  ///
  /// In zh, this message translates to:
  /// **'{count, plural, other{{count} 帧}}'**
  String infoFrameCountValue(int count);

  /// 图片信息：当前解码位图占用的内存（有值才显示）。
  ///
  /// In zh, this message translates to:
  /// **'解码内存'**
  String get infoDecodedMemory;

  /// 图片信息：解码时的下采样倍数（有值才显示）。
  ///
  /// In zh, this message translates to:
  /// **'解码采样'**
  String get infoSampleSize;

  /// 解码采样为 1：按原始分辨率解码。
  ///
  /// In zh, this message translates to:
  /// **'原始分辨率'**
  String get infoSampleFull;

  /// 解码采样大于 1，例如“按 1/2 采样”。
  ///
  /// In zh, this message translates to:
  /// **'按 1/{size} 采样'**
  String infoSampleSizeValue(int size);
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
