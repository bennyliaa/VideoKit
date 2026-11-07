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

  /// 小格（如手机 3×3）中暂停格的短文案，完整原因见读屏描述（R1-12b）。
  ///
  /// In zh, this message translates to:
  /// **'已暂停'**
  String get slotPausedShort;

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

  /// 编辑器标题。
  ///
  /// In zh, this message translates to:
  /// **'剪辑'**
  String get editorTitle;

  /// 撤销上一步编辑（Ctrl+Z）。
  ///
  /// In zh, this message translates to:
  /// **'撤销'**
  String get editorUndo;

  /// 重做（Ctrl+Shift+Z）。
  ///
  /// In zh, this message translates to:
  /// **'重做'**
  String get editorRedo;

  /// 进入导出。
  ///
  /// In zh, this message translates to:
  /// **'导出'**
  String get editorExport;

  /// 请宿主选择更多视频加入工程。
  ///
  /// In zh, this message translates to:
  /// **'添加视频'**
  String get editorAddVideo;

  /// 在播放头处分割选中片段。
  ///
  /// In zh, this message translates to:
  /// **'分割'**
  String get editorSplit;

  /// 删除选中片段（只影响工程，不影响原视频）。
  ///
  /// In zh, this message translates to:
  /// **'删除'**
  String get editorDelete;

  /// 打开片段顺序列表。
  ///
  /// In zh, this message translates to:
  /// **'排序'**
  String get editorReorder;

  /// 进入打码模式。
  ///
  /// In zh, this message translates to:
  /// **'打码'**
  String get editorMask;

  /// 进入自动跟踪。
  ///
  /// In zh, this message translates to:
  /// **'自动跟踪'**
  String get editorTrack;

  /// 底部导航：跟踪。
  ///
  /// In zh, this message translates to:
  /// **'跟踪'**
  String get editorTrackShort;

  /// 底部导航：剪辑。
  ///
  /// In zh, this message translates to:
  /// **'剪辑'**
  String get editorClipsTab;

  /// 底部导航：添加。
  ///
  /// In zh, this message translates to:
  /// **'添加'**
  String get editorAddTab;

  /// 未选中片段时的提示。
  ///
  /// In zh, this message translates to:
  /// **'点按时间线上的片段进行编辑'**
  String get editorNoSelection;

  /// 工程为空时的提示。
  ///
  /// In zh, this message translates to:
  /// **'还没有片段，先添加视频'**
  String get editorEmpty;

  /// 时间线片段名。
  ///
  /// In zh, this message translates to:
  /// **'片段 {index}'**
  String editorClip(int index);

  /// 属性面板标题。
  ///
  /// In zh, this message translates to:
  /// **'片段 {index} 属性'**
  String editorClipProps(int index);

  /// 手机端选中片段卡片标题。
  ///
  /// In zh, this message translates to:
  /// **'片段 {index} · {duration}'**
  String editorClipSummary(int index, String duration);

  /// 属性：来源文件。
  ///
  /// In zh, this message translates to:
  /// **'来源'**
  String get propSource;

  /// 属性：片段起点。
  ///
  /// In zh, this message translates to:
  /// **'起点'**
  String get propIn;

  /// 属性：片段终点。
  ///
  /// In zh, this message translates to:
  /// **'终点'**
  String get propOut;

  /// 属性：片段时长。
  ///
  /// In zh, this message translates to:
  /// **'时长'**
  String get propDuration;

  /// 以秒表示的时长，例如“18.6 秒”。
  ///
  /// In zh, this message translates to:
  /// **'{seconds} 秒'**
  String durationSeconds(String seconds);

  /// 快速拼接（无重编码）时的边界提示。
  ///
  /// In zh, this message translates to:
  /// **'快速拼接时边界将对齐到最近的关键帧'**
  String get keyframeAlignNotice;

  /// 多视频参数一致。
  ///
  /// In zh, this message translates to:
  /// **'参数一致，可快速拼接'**
  String get concatFast;

  /// 多视频参数不一致。
  ///
  /// In zh, this message translates to:
  /// **'参数不一致，将统一转码'**
  String get concatTranscodeTitle;

  /// 不一致时的说明。
  ///
  /// In zh, this message translates to:
  /// **'{count, plural, other{有 {count} 个视频的分辨率、帧率、编码或方向与第一个不同}}：将按导出预设统一转码，并校正旋转方向。'**
  String concatTranscodeDetail(int count);

  /// 预计行：可快速拼接。
  ///
  /// In zh, this message translates to:
  /// **'快速拼接可用'**
  String get fastConcatAvailable;

  /// 不能快速拼接。
  ///
  /// In zh, this message translates to:
  /// **'快速拼接（无重编码）：不可用'**
  String get fastConcatUnavailable;

  /// 预计输出时长与大小。
  ///
  /// In zh, this message translates to:
  /// **'预计 {duration} · 约 {size}'**
  String estimateLine(String duration, String size);

  /// 只能估算时长。
  ///
  /// In zh, this message translates to:
  /// **'预计 {duration} · 大小无法预估'**
  String estimateDurationOnly(String duration);

  /// 无法估算输出（不显示假数字）。
  ///
  /// In zh, this message translates to:
  /// **'无法预估'**
  String get estimateUnknown;

  /// 预览时间。
  ///
  /// In zh, this message translates to:
  /// **'{position} / {duration}'**
  String editorTime(String position, String duration);

  /// 时间线的读屏标签。
  ///
  /// In zh, this message translates to:
  /// **'时间线'**
  String get timelineLabel;

  /// 时间线放大。
  ///
  /// In zh, this message translates to:
  /// **'放大时间线'**
  String get timelineZoomIn;

  /// 时间线缩小。
  ///
  /// In zh, this message translates to:
  /// **'缩小时间线'**
  String get timelineZoomOut;

  /// 片段的读屏描述。
  ///
  /// In zh, this message translates to:
  /// **'片段 {index}，{start} 至 {end}，时长 {duration}'**
  String clipSemantic(int index, String start, String end, String duration);

  /// 读屏自定义操作：片段前移。
  ///
  /// In zh, this message translates to:
  /// **'前移一位'**
  String get clipMoveEarlier;

  /// 读屏自定义操作：片段后移。
  ///
  /// In zh, this message translates to:
  /// **'后移一位'**
  String get clipMoveLater;

  /// 片段起点把手。
  ///
  /// In zh, this message translates to:
  /// **'调整起点'**
  String get clipTrimStart;

  /// 片段终点把手。
  ///
  /// In zh, this message translates to:
  /// **'调整终点'**
  String get clipTrimEnd;

  /// 多视频列表标题。
  ///
  /// In zh, this message translates to:
  /// **'多视频拼接'**
  String get sourcesTitle;

  /// 视频数量。
  ///
  /// In zh, this message translates to:
  /// **'{count, plural, other{{count} 个视频}}'**
  String sourcesCount(int count);

  /// 视频参数。
  ///
  /// In zh, this message translates to:
  /// **'{width} × {height} · {fps} fps · {codec}'**
  String sourceMeta(int width, int height, String fps, String codec);

  /// 视频带旋转元数据。
  ///
  /// In zh, this message translates to:
  /// **'旋转 {degrees}°'**
  String sourceRotated(int degrees);

  /// 打码模式标题。
  ///
  /// In zh, this message translates to:
  /// **'打码'**
  String get maskTitle;

  /// 退出打码模式。
  ///
  /// In zh, this message translates to:
  /// **'完成'**
  String get maskDone;

  /// 遮罩列表标题。
  ///
  /// In zh, this message translates to:
  /// **'遮罩'**
  String get maskListTitle;

  /// 在当前帧添加手动遮罩。
  ///
  /// In zh, this message translates to:
  /// **'添加遮罩'**
  String get maskAdd;

  /// 遮罩名称。
  ///
  /// In zh, this message translates to:
  /// **'遮罩 {index}'**
  String maskName(int index);

  /// 遮罩样式与时间范围。
  ///
  /// In zh, this message translates to:
  /// **'{style} · {start} – {end}'**
  String maskSummary(String style, String start, String end);

  /// 关键帧数量。
  ///
  /// In zh, this message translates to:
  /// **'{count, plural, other{关键帧 {count} 个}}'**
  String maskKeyframes(int count);

  /// 自动遮罩的关键帧来源。
  ///
  /// In zh, this message translates to:
  /// **'关键帧由跟踪生成'**
  String get maskKeyframesTracker;

  /// 遮罩类型：手动。
  ///
  /// In zh, this message translates to:
  /// **'手动'**
  String get maskTypeManual;

  /// 遮罩类型：人脸。
  ///
  /// In zh, this message translates to:
  /// **'人脸跟踪'**
  String get maskTypeFace;

  /// 遮罩类型：物体。
  ///
  /// In zh, this message translates to:
  /// **'物体跟踪'**
  String get maskTypeObject;

  /// 遮罩样式。
  ///
  /// In zh, this message translates to:
  /// **'样式'**
  String get maskStyle;

  /// 遮罩样式：马赛克。
  ///
  /// In zh, this message translates to:
  /// **'马赛克'**
  String get maskStyleMosaic;

  /// 遮罩样式：模糊。
  ///
  /// In zh, this message translates to:
  /// **'模糊'**
  String get maskStyleBlur;

  /// 遮罩强度。
  ///
  /// In zh, this message translates to:
  /// **'强度'**
  String get maskStrength;

  /// 删除选中遮罩。
  ///
  /// In zh, this message translates to:
  /// **'删除遮罩'**
  String get maskDelete;

  /// 遮罩开关。
  ///
  /// In zh, this message translates to:
  /// **'启用遮罩'**
  String get maskEnable;

  /// 关键帧行标题。
  ///
  /// In zh, this message translates to:
  /// **'遮罩 {index} 关键帧'**
  String maskKeyframeTitle(int index);

  /// 在播放头处添加关键帧。
  ///
  /// In zh, this message translates to:
  /// **'在当前帧添加关键帧'**
  String get maskAddKeyframe;

  /// 删除播放头处的关键帧。
  ///
  /// In zh, this message translates to:
  /// **'删除当前关键帧'**
  String get maskRemoveKeyframe;

  /// 遮罩框的读屏标签。
  ///
  /// In zh, this message translates to:
  /// **'遮罩区域'**
  String get maskBox;

  /// 遮罩框的读屏提示。
  ///
  /// In zh, this message translates to:
  /// **'拖动移动，四角与四边调整大小'**
  String get maskBoxHint;

  /// 遮罩列表为空。
  ///
  /// In zh, this message translates to:
  /// **'还没有遮罩，点“添加遮罩”或使用自动跟踪'**
  String get maskNone;

  /// 跟踪的隐私说明。
  ///
  /// In zh, this message translates to:
  /// **'本机处理 · 不上传'**
  String get trackLocalOnly;

  /// 在当前帧检测人脸。
  ///
  /// In zh, this message translates to:
  /// **'检测人脸'**
  String get trackDetectFaces;

  /// 检测结果。
  ///
  /// In zh, this message translates to:
  /// **'{count, plural, =0{当前帧没有检测到人脸} other{检测到 {count} 张人脸}}'**
  String trackDetected(int count);

  /// 选择目标说明。
  ///
  /// In zh, this message translates to:
  /// **'选择需要打码的目标，不会默认处理所有人'**
  String get trackChooseHint;

  /// 已选目标。
  ///
  /// In zh, this message translates to:
  /// **'目标 {letter}'**
  String trackTarget(String letter);

  /// 未选人脸。
  ///
  /// In zh, this message translates to:
  /// **'人脸 {index}'**
  String trackFace(int index);

  /// 未选人脸框上的提示。
  ///
  /// In zh, this message translates to:
  /// **'点按选择'**
  String get trackTapToSelect;

  /// 物体跟踪：在画面上框选。
  ///
  /// In zh, this message translates to:
  /// **'框选物体'**
  String get trackObject;

  /// 物体框选说明。
  ///
  /// In zh, this message translates to:
  /// **'在画面上点选或拖出物体所在区域'**
  String get trackObjectHint;

  /// 跟踪进行中。
  ///
  /// In zh, this message translates to:
  /// **'跟踪中'**
  String get trackRunning;

  /// 已分析时长。
  ///
  /// In zh, this message translates to:
  /// **'已分析 {done} / {total}'**
  String trackAnalyzed(String done, String total);

  /// 无法估算进度时。
  ///
  /// In zh, this message translates to:
  /// **'正在分析…'**
  String get trackAnalyzing;

  /// 取消跟踪。
  ///
  /// In zh, this message translates to:
  /// **'取消跟踪'**
  String get trackCancel;

  /// 跟踪完成。
  ///
  /// In zh, this message translates to:
  /// **'跟踪完成'**
  String get trackCompleted;

  /// 跟踪已取消。
  ///
  /// In zh, this message translates to:
  /// **'已取消跟踪'**
  String get trackCancelled;

  /// 跟踪失败。
  ///
  /// In zh, this message translates to:
  /// **'跟踪失败'**
  String get trackFailed;

  /// 覆盖状态：已跟踪。
  ///
  /// In zh, this message translates to:
  /// **'已跟踪'**
  String get coverageTracked;

  /// 覆盖状态：置信度低（斜线图案）。
  ///
  /// In zh, this message translates to:
  /// **'置信度低'**
  String get coverageLow;

  /// 覆盖状态：可能混淆（点状图案）。
  ///
  /// In zh, this message translates to:
  /// **'可能混淆'**
  String get coverageAmbiguous;

  /// 覆盖状态：丢失（叉号图案）。
  ///
  /// In zh, this message translates to:
  /// **'丢失'**
  String get coverageLost;

  /// 覆盖状态：未分析（虚线）。
  ///
  /// In zh, this message translates to:
  /// **'未分析'**
  String get coverageNotAnalyzed;

  /// 覆盖状态：用户已确认的区间。
  ///
  /// In zh, this message translates to:
  /// **'已确认'**
  String get coverageAccepted;

  /// 状态轨道的读屏标签。
  ///
  /// In zh, this message translates to:
  /// **'{name} 跟踪状态'**
  String coverageStripLabel(String name);

  /// 状态区间的读屏描述。
  ///
  /// In zh, this message translates to:
  /// **'{state}，{start} – {end}'**
  String coverageSegment(String state, String start, String end);

  /// 纠正丢失或混淆的区间。
  ///
  /// In zh, this message translates to:
  /// **'纠正'**
  String get trackCorrect;

  /// 纠正说明。
  ///
  /// In zh, this message translates to:
  /// **'在画面上拖出目标的新位置'**
  String get trackCorrectHint;

  /// 纠正点之后的区间。
  ///
  /// In zh, this message translates to:
  /// **'待重新计算'**
  String get trackRecomputing;

  /// 导出前覆盖检查标题。
  ///
  /// In zh, this message translates to:
  /// **'{count, plural, other{发现 {count} 个未覆盖区间}}'**
  String checkTitle(int count);

  /// 覆盖检查说明。
  ///
  /// In zh, this message translates to:
  /// **'这些时间段内目标可能未被打码'**
  String get checkSubtitle;

  /// 未覆盖区间。
  ///
  /// In zh, this message translates to:
  /// **'{name} · {start} – {end}'**
  String checkRange(String name, String start, String end);

  /// 跳到该区间纠正。
  ///
  /// In zh, this message translates to:
  /// **'跳转纠正'**
  String get checkJump;

  /// 改为手动关键帧。
  ///
  /// In zh, this message translates to:
  /// **'手动关键帧'**
  String get checkManual;

  /// 该区间全画面打码。
  ///
  /// In zh, this message translates to:
  /// **'全画面打码'**
  String get checkFullFrame;

  /// 返回修正。
  ///
  /// In zh, this message translates to:
  /// **'返回修正'**
  String get checkBack;

  /// 强制导出。
  ///
  /// In zh, this message translates to:
  /// **'仍要导出（结果将标记为“打码不完整”）'**
  String get checkForce;

  /// 导出面板标题。
  ///
  /// In zh, this message translates to:
  /// **'导出'**
  String get exportTitle;

  /// 预设分组标题。
  ///
  /// In zh, this message translates to:
  /// **'导出预设'**
  String get exportPresets;

  /// 预设：原始尺寸。
  ///
  /// In zh, this message translates to:
  /// **'原始'**
  String get presetOriginal;

  /// 原始预设说明。
  ///
  /// In zh, this message translates to:
  /// **'与源视频相同 · 推荐'**
  String get presetOriginalDetail;

  /// 预设：1080p。
  ///
  /// In zh, this message translates to:
  /// **'1080p'**
  String get preset1080;

  /// 预设：720p。
  ///
  /// In zh, this message translates to:
  /// **'720p'**
  String get preset720;

  /// 预设长边像素。
  ///
  /// In zh, this message translates to:
  /// **'长边 {px}'**
  String presetLongEdge(int px);

  /// 预设不可用。
  ///
  /// In zh, this message translates to:
  /// **'此设备不可用'**
  String get presetUnavailable;

  /// 输出格式。
  ///
  /// In zh, this message translates to:
  /// **'格式 {format}'**
  String exportFormat(String format);

  /// 预检分组标题。
  ///
  /// In zh, this message translates to:
  /// **'导出前检查'**
  String get exportChecks;

  /// 预检项：编码器。
  ///
  /// In zh, this message translates to:
  /// **'编码器'**
  String get checkEncoder;

  /// 编码器可用。
  ///
  /// In zh, this message translates to:
  /// **'编码器可用'**
  String get checkEncoderOk;

  /// 编码器不可用。
  ///
  /// In zh, this message translates to:
  /// **'编码器不可用'**
  String get checkEncoderFail;

  /// 预检项：输出位置。
  ///
  /// In zh, this message translates to:
  /// **'输出位置'**
  String get checkOutput;

  /// 输出位置可写。
  ///
  /// In zh, this message translates to:
  /// **'由宿主提供'**
  String get checkOutputOk;

  /// 输出位置不可写。
  ///
  /// In zh, this message translates to:
  /// **'输出位置不支持写入'**
  String get checkOutputFail;

  /// 预检项：空间。
  ///
  /// In zh, this message translates to:
  /// **'空间'**
  String get checkSpace;

  /// 所需与可用空间。
  ///
  /// In zh, this message translates to:
  /// **'需约 {need}，可用 {free}'**
  String checkSpaceValue(String need, String free);

  /// 只知道所需空间。
  ///
  /// In zh, this message translates to:
  /// **'需约 {need}'**
  String checkSpaceNeed(String need);

  /// 无法估算空间。
  ///
  /// In zh, this message translates to:
  /// **'无法预估所需空间'**
  String get checkSpaceUnknown;

  /// 空间不足。
  ///
  /// In zh, this message translates to:
  /// **'空间不足'**
  String get checkSpaceFail;

  /// 预检项：打码覆盖。
  ///
  /// In zh, this message translates to:
  /// **'打码覆盖'**
  String get checkCoverage;

  /// 覆盖完整。
  ///
  /// In zh, this message translates to:
  /// **'全部目标已覆盖'**
  String get checkCoverageOk;

  /// 没有需要检查的遮罩。
  ///
  /// In zh, this message translates to:
  /// **'没有自动跟踪遮罩'**
  String get checkCoverageNone;

  /// 存在未覆盖区间。
  ///
  /// In zh, this message translates to:
  /// **'{count, plural, other{有 {count} 个未覆盖区间}}'**
  String checkCoverageFail(int count);

  /// 预检项通过（读屏）。
  ///
  /// In zh, this message translates to:
  /// **'通过'**
  String get checkPassed;

  /// 预检项未通过（读屏）。
  ///
  /// In zh, this message translates to:
  /// **'有问题'**
  String get checkProblem;

  /// 预检进行中。
  ///
  /// In zh, this message translates to:
  /// **'正在检查…'**
  String get checkRunning;

  /// 导出安全说明。
  ///
  /// In zh, this message translates to:
  /// **'导出生成新文件，原视频不会被修改；保存位置与最终命名由宿主确认。'**
  String get exportSafety;

  /// 开始导出。
  ///
  /// In zh, this message translates to:
  /// **'开始导出'**
  String get exportStart;

  /// 存在未覆盖区间时的主按钮。
  ///
  /// In zh, this message translates to:
  /// **'查看未覆盖区间'**
  String get exportReviewCoverage;

  /// 导出中标题。
  ///
  /// In zh, this message translates to:
  /// **'正在导出'**
  String get exporting;

  /// 阶段：准备。
  ///
  /// In zh, this message translates to:
  /// **'准备'**
  String get stagePreparing;

  /// 阶段：跟踪。
  ///
  /// In zh, this message translates to:
  /// **'跟踪'**
  String get stageTracking;

  /// 阶段：编码。
  ///
  /// In zh, this message translates to:
  /// **'编码'**
  String get stageEncoding;

  /// 阶段：校验。
  ///
  /// In zh, this message translates to:
  /// **'校验输出'**
  String get stageVerifying;

  /// 阶段：写入。
  ///
  /// In zh, this message translates to:
  /// **'写入宿主位置'**
  String get stageWriting;

  /// 阶段已完成。
  ///
  /// In zh, this message translates to:
  /// **'已完成'**
  String get stageDone;

  /// 阶段未开始。
  ///
  /// In zh, this message translates to:
  /// **'等待'**
  String get stageWaiting;

  /// 阶段进行中但无法估算比例。
  ///
  /// In zh, this message translates to:
  /// **'进行中'**
  String get stageInProgress;

  /// 剩余时间。
  ///
  /// In zh, this message translates to:
  /// **'约 {duration}'**
  String stageRemaining(String duration);

  /// 已处理时长。
  ///
  /// In zh, this message translates to:
  /// **'已处理 {done} / {total}'**
  String stageProcessed(String done, String total);

  /// 已输出大小。
  ///
  /// In zh, this message translates to:
  /// **'已输出 {size}'**
  String stageOutputSize(String size);

  /// 导出说明。
  ///
  /// In zh, this message translates to:
  /// **'导出不支持暂停。取消后可重新导出，不会留下未完成的文件。'**
  String get exportNoPause;

  /// 取消导出。
  ///
  /// In zh, this message translates to:
  /// **'取消导出'**
  String get exportCancel;

  /// 取消中。
  ///
  /// In zh, this message translates to:
  /// **'正在取消…'**
  String get exportCancelling;

  /// 已取消。
  ///
  /// In zh, this message translates to:
  /// **'已取消，未生成文件'**
  String get exportCancelled;

  /// 已取消但宿主报告部分输出仍在。
  ///
  /// In zh, this message translates to:
  /// **'已取消，部分输出未能删除'**
  String get exportCancelledPartial;

  /// 导出失败。
  ///
  /// In zh, this message translates to:
  /// **'导出失败'**
  String get exportFailedTitle;

  /// 失败影响说明。
  ///
  /// In zh, this message translates to:
  /// **'原视频未受影响'**
  String get exportImpactSource;

  /// 失败影响说明。
  ///
  /// In zh, this message translates to:
  /// **'未完成的输出已丢弃'**
  String get exportImpactDiscarded;

  /// 保留的错误代码。
  ///
  /// In zh, this message translates to:
  /// **'错误代码 {code}'**
  String exportErrorCode(String code);

  /// 重新导出。
  ///
  /// In zh, this message translates to:
  /// **'重新导出'**
  String get exportRetry;

  /// 降低质量重新导出。
  ///
  /// In zh, this message translates to:
  /// **'改用 {preset} 重新导出'**
  String exportUseSmaller(String preset);

  /// 返回编辑。
  ///
  /// In zh, this message translates to:
  /// **'返回编辑'**
  String get exportBackToEdit;

  /// 导出成功。
  ///
  /// In zh, this message translates to:
  /// **'导出完成'**
  String get exportDoneTitle;

  /// 成功说明。
  ///
  /// In zh, this message translates to:
  /// **'文件已写入宿主提供的临时位置，正式保存由宿主确认。'**
  String get exportDoneDetail;

  /// 结果摘要：格式。
  ///
  /// In zh, this message translates to:
  /// **'格式'**
  String get summaryFormat;

  /// 结果摘要：分辨率。
  ///
  /// In zh, this message translates to:
  /// **'分辨率'**
  String get summaryResolution;

  /// 结果摘要：时长。
  ///
  /// In zh, this message translates to:
  /// **'时长'**
  String get summaryDuration;

  /// 结果摘要：大小。
  ///
  /// In zh, this message translates to:
  /// **'大小'**
  String get summarySize;

  /// 结果摘要：警告。
  ///
  /// In zh, this message translates to:
  /// **'提示'**
  String get summaryWarnings;

  /// 导出警告。
  ///
  /// In zh, this message translates to:
  /// **'边界已对齐到关键帧'**
  String get warnBoundary;

  /// 导出警告。
  ///
  /// In zh, this message translates to:
  /// **'已为无声片段插入静音'**
  String get warnSilence;

  /// 导出警告。
  ///
  /// In zh, this message translates to:
  /// **'打码不完整（已确认导出未覆盖区间）'**
  String get warnCoverage;

  /// Fake 导出结果的说明。
  ///
  /// In zh, this message translates to:
  /// **'演示模式：未生成真实媒体文件'**
  String get warnDemo;

  /// 遮罩列表项标题：名称与类型。
  ///
  /// In zh, this message translates to:
  /// **'遮罩 {index} · {type}'**
  String maskNameTyped(int index, String type);

  /// 播放器“更多”中的参数信息面板（设计稿第 9 页）：菜单项与面板标题。
  ///
  /// In zh, this message translates to:
  /// **'参数'**
  String get playerMediaInfo;

  /// 参数面板：视频编码（如 H.264）。
  ///
  /// In zh, this message translates to:
  /// **'视频编码'**
  String get infoVideoCodec;

  /// 参数面板：音频编码（如 AAC，有值才显示）。
  ///
  /// In zh, this message translates to:
  /// **'音频编码'**
  String get infoAudioCodec;

  /// 参数面板：视频分辨率。
  ///
  /// In zh, this message translates to:
  /// **'分辨率'**
  String get infoResolution;

  /// 参数面板：帧率（有值才显示）。
  ///
  /// In zh, this message translates to:
  /// **'帧率'**
  String get infoFrameRate;

  /// 帧率的值；value 已按区域格式化。
  ///
  /// In zh, this message translates to:
  /// **'{value} fps'**
  String infoFrameRateValue(String value);

  /// 参数面板：总码率（有值才显示）。
  ///
  /// In zh, this message translates to:
  /// **'码率'**
  String get infoBitrate;

  /// 码率，千比特每秒；value 已按区域格式化。
  ///
  /// In zh, this message translates to:
  /// **'{value} kbps'**
  String infoBitrateKbps(String value);

  /// 码率，兆比特每秒；value 已按区域格式化。
  ///
  /// In zh, this message translates to:
  /// **'{value} Mbps'**
  String infoBitrateMbps(String value);

  /// 参数面板：视频的旋转元数据（有值才显示）。
  ///
  /// In zh, this message translates to:
  /// **'旋转'**
  String get infoRotation;

  /// 旋转角度。
  ///
  /// In zh, this message translates to:
  /// **'{degrees}°'**
  String infoRotationValue(int degrees);

  /// 参数面板：时长。
  ///
  /// In zh, this message translates to:
  /// **'时长'**
  String get infoDuration;
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
