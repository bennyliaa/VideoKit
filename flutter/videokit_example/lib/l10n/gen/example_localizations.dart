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

  /// 字体缩放设置项。
  ///
  /// In zh, this message translates to:
  /// **'字体缩放'**
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
