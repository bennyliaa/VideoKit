import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'example_localizations_zh.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of ExampleLocalizations
/// returned by `ExampleLocalizations.of(context)`.
///
/// Applications need to include `ExampleLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'gen/example_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: ExampleLocalizations.localizationsDelegates,
///   supportedLocales: ExampleLocalizations.supportedLocales,
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
/// be consistent with the languages listed in the ExampleLocalizations.supportedLocales
/// property.
abstract class ExampleLocalizations {
  ExampleLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static ExampleLocalizations of(BuildContext context) {
    return Localizations.of<ExampleLocalizations>(
      context,
      ExampleLocalizations,
    )!;
  }

  static const LocalizationsDelegate<ExampleLocalizations> delegate =
      _ExampleLocalizationsDelegate();

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

  /// 示例 App 的任务标题。
  ///
  /// In zh, this message translates to:
  /// **'VideoKit 示例'**
  String get appTitle;

  /// 主题画廊页标题。
  ///
  /// In zh, this message translates to:
  /// **'VideoKit 主题画廊'**
  String get galleryTitle;

  /// 设置分组标题。
  ///
  /// In zh, this message translates to:
  /// **'设置'**
  String get sectionSettings;

  /// 主题模式设置项。
  ///
  /// In zh, this message translates to:
  /// **'主题'**
  String get settingTheme;

  /// 深色主题。
  ///
  /// In zh, this message translates to:
  /// **'深色'**
  String get themeDark;

  /// 浅色主题。
  ///
  /// In zh, this message translates to:
  /// **'浅色'**
  String get themeLight;

  /// 跟随系统主题。
  ///
  /// In zh, this message translates to:
  /// **'跟随系统'**
  String get themeSystem;

  /// 宿主主色覆盖设置项。
  ///
  /// In zh, this message translates to:
  /// **'宿主主色'**
  String get settingHostPrimary;

  /// 不覆盖主色。
  ///
  /// In zh, this message translates to:
  /// **'默认'**
  String get hostPrimaryDefault;

  /// 语言设置项。
  ///
  /// In zh, this message translates to:
  /// **'语言'**
  String get settingLanguage;

  /// 简体中文。
  ///
  /// In zh, this message translates to:
  /// **'中文'**
  String get languageChinese;

  /// 把中文拉长约 40% 的伪语言，用于检查截断与换行。
  ///
  /// In zh, this message translates to:
  /// **'伪本地化'**
  String get languagePseudo;

  /// 调试用字体倍数，乘在系统字体缩放之上（R1-11）。
  ///
  /// In zh, this message translates to:
  /// **'额外字体倍数（叠加系统字体）'**
  String get settingTextScale;

  /// 减少动画开关。
  ///
  /// In zh, this message translates to:
  /// **'减少动画'**
  String get settingReduceMotion;

  /// 主题 Token 架构版本。
  ///
  /// In zh, this message translates to:
  /// **'Token 架构版本：{version}'**
  String schemaVersion(int version);

  /// 颜色分组标题。
  ///
  /// In zh, this message translates to:
  /// **'颜色 Token'**
  String get sectionColors;

  /// 状态色分组标题。
  ///
  /// In zh, this message translates to:
  /// **'状态色'**
  String get sectionStatus;

  /// 文字样式分组标题。
  ///
  /// In zh, this message translates to:
  /// **'文字样式'**
  String get sectionTypography;

  /// 尺寸分组标题。
  ///
  /// In zh, this message translates to:
  /// **'间距与圆角'**
  String get sectionDimensions;

  /// 动效分组标题。
  ///
  /// In zh, this message translates to:
  /// **'动效'**
  String get sectionAnimations;

  /// 组件样式分组标题。
  ///
  /// In zh, this message translates to:
  /// **'组件样式'**
  String get sectionComponents;

  /// 错误文案分组标题。
  ///
  /// In zh, this message translates to:
  /// **'错误文案'**
  String get sectionErrors;

  /// 色块的读屏标签。
  ///
  /// In zh, this message translates to:
  /// **'{token}，{hex}'**
  String colorSwatch(String token, String hex);

  /// 色块上的对比度。
  ///
  /// In zh, this message translates to:
  /// **'对比度 {ratio}:1'**
  String contrastRatio(String ratio);

  /// 文字样式示例行。
  ///
  /// In zh, this message translates to:
  /// **'{style} · {size} · 敏捷的狐狸跳过懒狗 0123456789'**
  String typographySample(String style, String size);

  /// 尺寸示例标签。
  ///
  /// In zh, this message translates to:
  /// **'{name} {value}'**
  String dimensionValue(String name, String value);

  /// 动效时长。
  ///
  /// In zh, this message translates to:
  /// **'按下 {press} · 小 {small} · 常规 {normal} · 页面 {page} 毫秒'**
  String animationDurations(int press, int small, int normal, int page);

  /// 动效演示开关。
  ///
  /// In zh, this message translates to:
  /// **'演示动效'**
  String get animationToggle;

  /// 跟踪状态 TRACKED。
  ///
  /// In zh, this message translates to:
  /// **'已跟踪 / 成功'**
  String get statusTracked;

  /// 跟踪状态 LOW_CONFIDENCE。
  ///
  /// In zh, this message translates to:
  /// **'置信度低'**
  String get statusLowConfidence;

  /// 跟踪状态 AMBIGUOUS。
  ///
  /// In zh, this message translates to:
  /// **'可能混淆'**
  String get statusAmbiguous;

  /// 跟踪状态 LOST。
  ///
  /// In zh, this message translates to:
  /// **'丢失 / 错误'**
  String get statusLost;

  /// 信息状态。
  ///
  /// In zh, this message translates to:
  /// **'信息'**
  String get statusInfo;

  /// component.button.primary 示例。
  ///
  /// In zh, this message translates to:
  /// **'主按钮'**
  String get componentButtonPrimary;

  /// component.button.secondary 示例。
  ///
  /// In zh, this message translates to:
  /// **'次按钮'**
  String get componentButtonSecondary;

  /// component.button.text 示例。
  ///
  /// In zh, this message translates to:
  /// **'文字按钮'**
  String get componentButtonText;

  /// component.button.icon 示例。
  ///
  /// In zh, this message translates to:
  /// **'图标按钮'**
  String get componentButtonIcon;

  /// component.chip.default 示例（倍速）。
  ///
  /// In zh, this message translates to:
  /// **'选项片 1.5×'**
  String get componentChip;

  /// component.badge.default 示例。
  ///
  /// In zh, this message translates to:
  /// **'{count, plural, other{{count} 条}}'**
  String componentBadge(int count);

  /// apps.videokit.component.seekbar 示例。
  ///
  /// In zh, this message translates to:
  /// **'进度条'**
  String get componentSeekBar;

  /// 组件状态 normal。
  ///
  /// In zh, this message translates to:
  /// **'常态'**
  String get stateNormal;

  /// 组件状态 pressed。
  ///
  /// In zh, this message translates to:
  /// **'按下'**
  String get statePressed;

  /// 组件状态 focused。
  ///
  /// In zh, this message translates to:
  /// **'焦点'**
  String get stateFocused;

  /// 组件状态 disabled。
  ///
  /// In zh, this message translates to:
  /// **'禁用'**
  String get stateDisabled;

  /// 组件状态 selected。
  ///
  /// In zh, this message translates to:
  /// **'选中'**
  String get stateSelected;

  /// 组件状态 hovered。
  ///
  /// In zh, this message translates to:
  /// **'悬停'**
  String get stateHovered;

  /// 错误码与文案对照行。
  ///
  /// In zh, this message translates to:
  /// **'{code}：{message}'**
  String errorLine(String code, String message);

  /// 时间码示例（当前位置 / 总时长）。
  ///
  /// In zh, this message translates to:
  /// **'{position} / {duration}'**
  String timecodeRange(String position, String duration);

  /// 画廊中通往组件页与演示页的分组标题。
  ///
  /// In zh, this message translates to:
  /// **'演示页面'**
  String get sectionDemos;

  /// 画廊顶栏：打开组件页。
  ///
  /// In zh, this message translates to:
  /// **'组件'**
  String get navComponents;

  /// 画廊顶栏：打开播放器演示页。
  ///
  /// In zh, this message translates to:
  /// **'播放器'**
  String get navPlayer;

  /// 组件页标题（设计稿第 6 页）。
  ///
  /// In zh, this message translates to:
  /// **'组件库'**
  String get componentsTitle;

  /// 按钮分组标题。
  ///
  /// In zh, this message translates to:
  /// **'按钮'**
  String get sectionButtons;

  /// 图标按钮分组标题（常态/选中/等待中/角标/禁用）。
  ///
  /// In zh, this message translates to:
  /// **'图标按钮'**
  String get sectionIconButtons;

  /// 角标与演示标识分组标题。
  ///
  /// In zh, this message translates to:
  /// **'角标与演示标识'**
  String get sectionBadges;

  /// 滑杆分组标题。
  ///
  /// In zh, this message translates to:
  /// **'滑杆'**
  String get sectionSlider;

  /// UI-09 状态视图分组标题。
  ///
  /// In zh, this message translates to:
  /// **'状态视图'**
  String get sectionStateViews;

  /// UI-04 宿主动作栏分组标题。
  ///
  /// In zh, this message translates to:
  /// **'宿主动作栏'**
  String get sectionHostActions;

  /// 面板宿主与轻提示分组标题。
  ///
  /// In zh, this message translates to:
  /// **'面板与轻提示'**
  String get sectionSheets;

  /// 打开示例面板的按钮。
  ///
  /// In zh, this message translates to:
  /// **'打开面板'**
  String get openSheet;

  /// 显示示例轻提示的按钮。
  ///
  /// In zh, this message translates to:
  /// **'显示轻提示'**
  String get showToast;

  /// 示例面板标题。
  ///
  /// In zh, this message translates to:
  /// **'示例面板'**
  String get sheetSampleTitle;

  /// 示例面板正文。
  ///
  /// In zh, this message translates to:
  /// **'按返回键或 Esc 关闭面板，不会退出页面。'**
  String get sheetSampleBody;

  /// 示例轻提示。
  ///
  /// In zh, this message translates to:
  /// **'已添加到收藏'**
  String get toastSample;

  /// 示例滑杆的读屏标签。
  ///
  /// In zh, this message translates to:
  /// **'音量'**
  String get volumeLabel;

  /// 示例角标文字。
  ///
  /// In zh, this message translates to:
  /// **'新'**
  String get badgeSample;

  /// 超长角标示例（超过 3 个字符会被截断）。
  ///
  /// In zh, this message translates to:
  /// **'12345'**
  String get badgeLongSample;

  /// 播放器演示页标题。
  ///
  /// In zh, this message translates to:
  /// **'播放器演示'**
  String get playerDemoTitle;

  /// 演示播放器顶栏的视频名称。
  ///
  /// In zh, this message translates to:
  /// **'演示视频'**
  String get playerDemoVideoTitle;

  /// 场景选择分组标题。
  ///
  /// In zh, this message translates to:
  /// **'场景'**
  String get scenarioLabel;

  /// Fake 场景：正常播放。
  ///
  /// In zh, this message translates to:
  /// **'正常'**
  String get scenarioNormal;

  /// Fake 场景：打开耗时 3 秒。
  ///
  /// In zh, this message translates to:
  /// **'慢加载'**
  String get scenarioSlowLoad;

  /// Fake 场景：播放中缓冲。
  ///
  /// In zh, this message translates to:
  /// **'缓冲'**
  String get scenarioBuffering;

  /// Fake 场景：30 秒时来源断开。
  ///
  /// In zh, this message translates to:
  /// **'断线'**
  String get scenarioDisconnect;

  /// Fake 场景：视频编码不支持。
  ///
  /// In zh, this message translates to:
  /// **'不支持'**
  String get scenarioUnsupported;

  /// Fake 场景：“删除”宿主动作 10 秒不响应。
  ///
  /// In zh, this message translates to:
  /// **'宿主动作超时'**
  String get scenarioHostActionTimeout;

  /// 点编辑入口时的提示（本批没有剪辑页）。
  ///
  /// In zh, this message translates to:
  /// **'剪辑页面将在后续批次提供'**
  String get editNotAvailable;

  /// 宿主面板插槽示例（设计稿第 10 页）：同一文件夹中的其他视频，随控制层显示和隐藏（R1-05）。
  ///
  /// In zh, this message translates to:
  /// **'邻近媒体'**
  String get hostPanelHint;

  /// 邻近媒体条目的读屏描述：名称与时长。
  ///
  /// In zh, this message translates to:
  /// **'{name}，{duration}'**
  String hostPanelItem(String name, String duration);

  /// 宿主动作：收藏（未收藏时）。
  ///
  /// In zh, this message translates to:
  /// **'收藏'**
  String get hostFavorite;

  /// 宿主动作：收藏（已收藏时）。
  ///
  /// In zh, this message translates to:
  /// **'已收藏'**
  String get hostFavorited;

  /// 收藏的读屏描述。
  ///
  /// In zh, this message translates to:
  /// **'收藏这个视频'**
  String get hostFavoriteCd;

  /// 取消收藏的读屏描述。
  ///
  /// In zh, this message translates to:
  /// **'取消收藏这个视频'**
  String get hostUnfavoriteCd;

  /// 宿主动作：标签。
  ///
  /// In zh, this message translates to:
  /// **'标签'**
  String get hostTag;

  /// 标签的读屏描述。
  ///
  /// In zh, this message translates to:
  /// **'为这个视频添加标签'**
  String get hostTagCd;

  /// 宿主动作：删除（演示，不会删除任何文件）。
  ///
  /// In zh, this message translates to:
  /// **'删除'**
  String get hostDelete;

  /// 删除的读屏描述。
  ///
  /// In zh, this message translates to:
  /// **'删除这个视频'**
  String get hostDeleteCd;

  /// 宿主动作：分享（溢出菜单）。
  ///
  /// In zh, this message translates to:
  /// **'分享'**
  String get hostShare;

  /// 分享的读屏描述。
  ///
  /// In zh, this message translates to:
  /// **'分享这个视频'**
  String get hostShareCd;

  /// 图片页：收藏的读屏描述（R1-15）。
  ///
  /// In zh, this message translates to:
  /// **'收藏这张图片'**
  String get hostFavoriteImageCd;

  /// 图片页：取消收藏的读屏描述。
  ///
  /// In zh, this message translates to:
  /// **'取消收藏这张图片'**
  String get hostUnfavoriteImageCd;

  /// 图片页：标签的读屏描述。
  ///
  /// In zh, this message translates to:
  /// **'为这张图片添加标签'**
  String get hostTagImageCd;

  /// 图片页：删除的读屏描述。
  ///
  /// In zh, this message translates to:
  /// **'删除这张图片'**
  String get hostDeleteImageCd;

  /// 图片页：分享的读屏描述。
  ///
  /// In zh, this message translates to:
  /// **'分享这张图片'**
  String get hostShareImageCd;

  /// 宿主动作完成后的提示。
  ///
  /// In zh, this message translates to:
  /// **'已完成'**
  String get hostDone;

  /// 画廊顶栏：打开图片查看演示页。
  ///
  /// In zh, this message translates to:
  /// **'图片'**
  String get navImageViewer;

  /// 画廊顶栏：打开多画面演示页。
  ///
  /// In zh, this message translates to:
  /// **'多画面'**
  String get navMultiView;

  /// 图片查看演示页标题。
  ///
  /// In zh, this message translates to:
  /// **'图片查看演示'**
  String get imageDemoTitle;

  /// 演示图片名（静态）。
  ///
  /// In zh, this message translates to:
  /// **'沙丘.heic'**
  String get demoImageDune;

  /// 演示图片名（动态）。
  ///
  /// In zh, this message translates to:
  /// **'烟花.gif'**
  String get demoImageFireworks;

  /// 演示图片名（静态）。
  ///
  /// In zh, this message translates to:
  /// **'森林.webp'**
  String get demoImageForest;

  /// 演示图片名（不支持的格式，用于展示错误状态）。
  ///
  /// In zh, this message translates to:
  /// **'新格式.jxl'**
  String get demoImageBroken;

  /// 多画面演示页标题。
  ///
  /// In zh, this message translates to:
  /// **'多画面'**
  String get multiViewTitle;

  /// 当前格数 / 最大格数。
  ///
  /// In zh, this message translates to:
  /// **'{count} / {max}'**
  String multiViewCount(int count, int max);

  /// 多画面底部说明。
  ///
  /// In zh, this message translates to:
  /// **'点按画面切换声音来源，同一时间只有一路发声'**
  String get multiViewHint;

  /// 添加一格演示媒体（最多 12 格）。
  ///
  /// In zh, this message translates to:
  /// **'添加媒体'**
  String get multiViewAdd;

  /// 网格布局选择的标题。
  ///
  /// In zh, this message translates to:
  /// **'布局'**
  String get multiViewLayout;

  /// 网格布局：自动。
  ///
  /// In zh, this message translates to:
  /// **'自动'**
  String get layoutAuto;

  /// 网格布局：2 列 2 行。
  ///
  /// In zh, this message translates to:
  /// **'2×2'**
  String get layout2x2;

  /// 网格布局：3 列 3 行。
  ///
  /// In zh, this message translates to:
  /// **'3×3'**
  String get layout3x3;

  /// 网格布局：4 列 3 行（最多 12 格）。
  ///
  /// In zh, this message translates to:
  /// **'4×3'**
  String get layout3x4;

  /// 能力提示（并发数超过建议值时）。
  ///
  /// In zh, this message translates to:
  /// **'当前设备建议同时播放 {suggested} 路视频：已暂停 {paused} 路离屏或较早加入的画面，显示封面'**
  String multiViewNotice(int suggested, int paused);

  /// 多画面中演示格的名称（读屏）。
  ///
  /// In zh, this message translates to:
  /// **'演示画面 {index}'**
  String demoSlotTitle(int index);

  /// 画廊：打开剪辑演示页。
  ///
  /// In zh, this message translates to:
  /// **'剪辑'**
  String get navEditor;

  /// 演示工程名称。
  ///
  /// In zh, this message translates to:
  /// **'海边旅行'**
  String get editProjectTitle;

  /// 剪辑演示的 Fake 场景选择。
  ///
  /// In zh, this message translates to:
  /// **'场景'**
  String get editScenario;

  /// Fake 场景：一切正常。
  ///
  /// In zh, this message translates to:
  /// **'正常'**
  String get editScenarioNormal;

  /// Fake 场景：跟踪在 4–6 秒丢失目标。
  ///
  /// In zh, this message translates to:
  /// **'跟踪丢失'**
  String get editScenarioTrackingLost;

  /// Fake 场景：编码阶段因空间不足失败。
  ///
  /// In zh, this message translates to:
  /// **'导出失败'**
  String get editScenarioExportFails;

  /// Fake 场景：取消导出需要 2 秒。
  ///
  /// In zh, this message translates to:
  /// **'取消较慢'**
  String get editScenarioCancelSlow;

  /// Fake 场景：引擎拒绝快速拼接，改为统一转码（M4）。
  ///
  /// In zh, this message translates to:
  /// **'快速拼接被拒'**
  String get editScenarioFastConcatRejected;

  /// 演示视频名。
  ///
  /// In zh, this message translates to:
  /// **'海边.mp4'**
  String get demoVideoSea;

  /// 演示视频名。
  ///
  /// In zh, this message translates to:
  /// **'山谷黄昏.mkv'**
  String get demoVideoValley;

  /// 演示视频名。
  ///
  /// In zh, this message translates to:
  /// **'城市夜景.mov'**
  String get demoVideoCity;

  /// “添加视频”加入的演示视频名。
  ///
  /// In zh, this message translates to:
  /// **'补充素材 {index}.mp4'**
  String demoVideoMore(int index);

  /// 导出完成后的宿主动作：打开。
  ///
  /// In zh, this message translates to:
  /// **'打开'**
  String get exportOpen;

  /// 导出完成后的宿主动作：分享。
  ///
  /// In zh, this message translates to:
  /// **'分享'**
  String get exportShare;

  /// 演示：宿主动作被触发。
  ///
  /// In zh, this message translates to:
  /// **'宿主处理：{action}'**
  String hostHandled(String action);
}

class _ExampleLocalizationsDelegate
    extends LocalizationsDelegate<ExampleLocalizations> {
  const _ExampleLocalizationsDelegate();

  @override
  Future<ExampleLocalizations> load(Locale locale) {
    return SynchronousFuture<ExampleLocalizations>(
      lookupExampleLocalizations(locale),
    );
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['zh'].contains(locale.languageCode);

  @override
  bool shouldReload(_ExampleLocalizationsDelegate old) => false;
}

ExampleLocalizations lookupExampleLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'zh':
      return ExampleLocalizationsZh();
  }

  throw FlutterError(
    'ExampleLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
