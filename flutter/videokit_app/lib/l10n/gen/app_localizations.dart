import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_zh.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'gen/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
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
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

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

  /// App 名称（任务切换器）。
  ///
  /// In zh, this message translates to:
  /// **'VideoKit'**
  String get appTitle;

  /// 首页标题。
  ///
  /// In zh, this message translates to:
  /// **'最近播放'**
  String get homeTitle;

  /// 切换到网格视图。
  ///
  /// In zh, this message translates to:
  /// **'网格视图'**
  String get homeGrid;

  /// 切换到列表视图。
  ///
  /// In zh, this message translates to:
  /// **'列表视图'**
  String get homeList;

  /// 进入设置。
  ///
  /// In zh, this message translates to:
  /// **'设置'**
  String get homeSettings;

  /// 筛选：全部。
  ///
  /// In zh, this message translates to:
  /// **'全部'**
  String get filterAll;

  /// 筛选：视频。
  ///
  /// In zh, this message translates to:
  /// **'视频'**
  String get filterVideo;

  /// 筛选：图片。
  ///
  /// In zh, this message translates to:
  /// **'图片'**
  String get filterImage;

  /// 打开系统文件选择器（M0 为演示列表）。
  ///
  /// In zh, this message translates to:
  /// **'打开文件'**
  String get openFile;

  /// 列表底部说明。
  ///
  /// In zh, this message translates to:
  /// **'最多保存 {limit} 条 · 只保存在本机'**
  String footerLimit(int limit);

  /// 首次使用空状态标题。
  ///
  /// In zh, this message translates to:
  /// **'还没有播放记录'**
  String get emptyTitle;

  /// 空状态说明。
  ///
  /// In zh, this message translates to:
  /// **'选择视频或图片开始播放，看过的媒体会出现在这里，方便接着看'**
  String get emptyBody;

  /// 多选说明。
  ///
  /// In zh, this message translates to:
  /// **'可多选：多个视频可进入多画面或拼接'**
  String get emptyMulti;

  /// “打开方式”提示标题。
  ///
  /// In zh, this message translates to:
  /// **'也可以从其他应用打开'**
  String get otherAppsTitle;

  /// “打开方式”提示说明。
  ///
  /// In zh, this message translates to:
  /// **'在文件管理器或相册中选择“用 VideoKit 打开”'**
  String get otherAppsBody;

  /// 记录关闭时的提示。
  ///
  /// In zh, this message translates to:
  /// **'播放历史记录已关闭，新的播放不会被记录'**
  String get historyOff;

  /// 筛选后为空。
  ///
  /// In zh, this message translates to:
  /// **'没有符合筛选的记录'**
  String get emptyFiltered;

  /// 视频记录：续播位置与时间。
  ///
  /// In zh, this message translates to:
  /// **'看到 {position} · {when}'**
  String entryWatched(String position, String when);

  /// 视频记录：没有续播位置。
  ///
  /// In zh, this message translates to:
  /// **'未播放 · {when}'**
  String entryNew(String when);

  /// 图片记录：最后查看时间。
  ///
  /// In zh, this message translates to:
  /// **'上次查看 · {when}'**
  String entryViewed(String when);

  /// 分辨率简称，例如“1080p”。
  ///
  /// In zh, this message translates to:
  /// **'{lines}p'**
  String resolutionLines(int lines);

  /// 像素尺寸。
  ///
  /// In zh, this message translates to:
  /// **'{width}×{height}'**
  String dimensions(int width, int height);

  /// 视频参数。
  ///
  /// In zh, this message translates to:
  /// **'{resolution} · {codec}'**
  String metaVideo(String resolution, String codec);

  /// 图片参数。
  ///
  /// In zh, this message translates to:
  /// **'图片 · {size}'**
  String metaImage(String size);

  /// 相对时间：一分钟内。
  ///
  /// In zh, this message translates to:
  /// **'刚刚'**
  String get timeJustNow;

  /// 相对时间：分钟。
  ///
  /// In zh, this message translates to:
  /// **'{n, plural, other{{n} 分钟前}}'**
  String timeMinutes(int n);

  /// 相对时间：小时。
  ///
  /// In zh, this message translates to:
  /// **'{n, plural, other{{n} 小时前}}'**
  String timeHours(int n);

  /// 相对时间：昨天。
  ///
  /// In zh, this message translates to:
  /// **'昨天'**
  String get timeYesterday;

  /// 相对时间：天。
  ///
  /// In zh, this message translates to:
  /// **'{n, plural, other{{n} 天前}}'**
  String timeDays(int n);

  /// 记录无法打开。
  ///
  /// In zh, this message translates to:
  /// **'无法打开'**
  String get unavailable;

  /// 无法打开的原因。
  ///
  /// In zh, this message translates to:
  /// **'文件已移动或授权失效'**
  String get unavailableReason;

  /// 重新选择文件。
  ///
  /// In zh, this message translates to:
  /// **'重新选择'**
  String get reselect;

  /// 从“打开方式”进入、只有临时授权的记录。
  ///
  /// In zh, this message translates to:
  /// **'临时授权，下次可能需要重新选择'**
  String get temporaryGrant;

  /// 缩略图上的图片角标。
  ///
  /// In zh, this message translates to:
  /// **'图片'**
  String get imageBadge;

  /// 记录的更多菜单。
  ///
  /// In zh, this message translates to:
  /// **'更多'**
  String get menuMore;

  /// 从头播放。
  ///
  /// In zh, this message translates to:
  /// **'从头播放'**
  String get menuFromStart;

  /// 在多画面中打开。
  ///
  /// In zh, this message translates to:
  /// **'在多画面中打开'**
  String get menuMultiView;

  /// 删除记录（不影响原文件）。
  ///
  /// In zh, this message translates to:
  /// **'从记录中删除'**
  String get menuDelete;

  /// 多选后的打开方式标题。
  ///
  /// In zh, this message translates to:
  /// **'{count, plural, other{已选择 {count} 个文件}}'**
  String openChoiceTitle(int count);

  /// 多选：多画面。
  ///
  /// In zh, this message translates to:
  /// **'在多画面中打开'**
  String get openMultiView;

  /// 多选：进入剪辑拼接。
  ///
  /// In zh, this message translates to:
  /// **'拼接为一个视频'**
  String get openConcat;

  /// 打开失败的提示。
  ///
  /// In zh, this message translates to:
  /// **'无法打开“{name}”'**
  String openFailed(String name);

  /// 设置页标题。
  ///
  /// In zh, this message translates to:
  /// **'设置'**
  String get settingsTitle;

  /// 设置分组：播放记录。
  ///
  /// In zh, this message translates to:
  /// **'播放记录'**
  String get secHistory;

  /// 记录播放历史开关。
  ///
  /// In zh, this message translates to:
  /// **'记录播放历史'**
  String get recordHistory;

  /// 记录开关说明。
  ///
  /// In zh, this message translates to:
  /// **'只保存在本机，不上传'**
  String get recordHistoryNote;

  /// 已保存条数。
  ///
  /// In zh, this message translates to:
  /// **'已保存'**
  String get savedCount;

  /// 已保存条数的值。
  ///
  /// In zh, this message translates to:
  /// **'{count} / {limit} 条'**
  String savedValue(int count, int limit);

  /// 清空播放记录。
  ///
  /// In zh, this message translates to:
  /// **'清空播放记录'**
  String get clearHistory;

  /// 清空确认标题。
  ///
  /// In zh, this message translates to:
  /// **'清空播放记录？'**
  String get clearConfirmTitle;

  /// 清空确认说明。
  ///
  /// In zh, this message translates to:
  /// **'将删除全部记录与缩略图，并释放已保存的文件访问授权。原文件不受影响。'**
  String get clearConfirmBody;

  /// 取消。
  ///
  /// In zh, this message translates to:
  /// **'取消'**
  String get cancel;

  /// 确认清空。
  ///
  /// In zh, this message translates to:
  /// **'清空'**
  String get clear;

  /// 清空后的提示。
  ///
  /// In zh, this message translates to:
  /// **'已清空播放记录'**
  String get cleared;

  /// 设置分组：外观。
  ///
  /// In zh, this message translates to:
  /// **'外观'**
  String get secAppearance;

  /// 主题。
  ///
  /// In zh, this message translates to:
  /// **'主题'**
  String get theme;

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

  /// 减少动画开关。
  ///
  /// In zh, this message translates to:
  /// **'减少动画'**
  String get reduceMotion;

  /// 减少动画说明。
  ///
  /// In zh, this message translates to:
  /// **'默认跟随系统设置'**
  String get reduceMotionNote;

  /// 设置分组：语言。
  ///
  /// In zh, this message translates to:
  /// **'语言'**
  String get secLanguage;

  /// 界面语言。
  ///
  /// In zh, this message translates to:
  /// **'界面语言'**
  String get uiLanguage;

  /// 语言说明。
  ///
  /// In zh, this message translates to:
  /// **'英文版本后续提供'**
  String get languageNote;

  /// 简体中文。
  ///
  /// In zh, this message translates to:
  /// **'简体中文'**
  String get languageChinese;

  /// 设置分组：关于。
  ///
  /// In zh, this message translates to:
  /// **'关于'**
  String get secAbout;

  /// 版本号。
  ///
  /// In zh, this message translates to:
  /// **'版本'**
  String get version;

  /// 开源许可页。
  ///
  /// In zh, this message translates to:
  /// **'开源许可'**
  String get licenses;

  /// 许可页说明。
  ///
  /// In zh, this message translates to:
  /// **'VideoKit 视频播放与编辑。App 与模块使用的开源组件见下表。'**
  String get legalese;

  /// 多画面页标题。
  ///
  /// In zh, this message translates to:
  /// **'多画面'**
  String get multiViewTitle;

  /// 拼接（编辑器）标题。
  ///
  /// In zh, this message translates to:
  /// **'{count, plural, other{拼接 {count} 个视频}}'**
  String concatTitle(int count);

  /// 选择器标题。
  ///
  /// In zh, this message translates to:
  /// **'选择视频或图片'**
  String get pickerTitle;

  /// 演示选择器说明。
  ///
  /// In zh, this message translates to:
  /// **'演示模式：从演示媒体中选择'**
  String get pickerDemoNote;

  /// 多选确认。
  ///
  /// In zh, this message translates to:
  /// **'{count, plural, =0{请选择} other{打开 {count} 个}}'**
  String pickerConfirm(int count);

  /// 单选确认。
  ///
  /// In zh, this message translates to:
  /// **'选择'**
  String get pickerConfirmOne;

  /// 演示文件名。
  ///
  /// In zh, this message translates to:
  /// **'山谷黄昏.mkv'**
  String get demoValley;

  /// 演示文件名。
  ///
  /// In zh, this message translates to:
  /// **'街头夜景 · 竖屏.mp4'**
  String get demoStreet;

  /// 演示文件名。
  ///
  /// In zh, this message translates to:
  /// **'沙丘.heic'**
  String get demoDune;

  /// 演示文件名。
  ///
  /// In zh, this message translates to:
  /// **'烟花.gif'**
  String get demoFireworks;

  /// 演示文件名。
  ///
  /// In zh, this message translates to:
  /// **'家庭录像.avi'**
  String get demoFamily;

  /// 演示文件名（演示“文件已移动”）。
  ///
  /// In zh, this message translates to:
  /// **'旅行合集.mp4'**
  String get demoTravel;

  /// 演示文件名（不支持的格式）。
  ///
  /// In zh, this message translates to:
  /// **'旧格式录像.mkv'**
  String get demoUnsupported;

  /// 首次启动/重试时连接播放后端的等待文字。
  ///
  /// In zh, this message translates to:
  /// **'正在启动 VideoKit'**
  String get startupConnecting;

  /// 启动错误页标题：原生与 Dart 协议版本不一致。
  ///
  /// In zh, this message translates to:
  /// **'VideoKit 版本不匹配'**
  String get startupProtocolTitle;

  /// 启动错误页说明：协议不匹配，重试无用。
  ///
  /// In zh, this message translates to:
  /// **'App 与播放组件的版本不一致，请安装最新版本的 App。'**
  String get startupProtocolDetail;

  /// 启动错误页标题：原生侧没有后端。
  ///
  /// In zh, this message translates to:
  /// **'播放组件不可用'**
  String get startupNoBackendTitle;

  /// 启动错误页说明：无后端，重试无用。
  ///
  /// In zh, this message translates to:
  /// **'这个版本的 App 没有包含播放组件，请重新安装 App。'**
  String get startupNoBackendDetail;

  /// 启动错误页标题：插件通道不可用。
  ///
  /// In zh, this message translates to:
  /// **'无法连接播放组件'**
  String get startupChannelTitle;

  /// 启动错误页说明：通道失败，可重试。
  ///
  /// In zh, this message translates to:
  /// **'播放组件没有响应。请重试；如果仍然失败，请重新启动 App。'**
  String get startupChannelDetail;

  /// 启动错误页标题：其他原因。
  ///
  /// In zh, this message translates to:
  /// **'VideoKit 启动失败'**
  String get startupUnknownTitle;

  /// 启动错误页说明：其他原因，可重试。
  ///
  /// In zh, this message translates to:
  /// **'启动时出现意外错误。请重试；如果仍然失败，请重新启动 App。'**
  String get startupUnknownDetail;

  /// 导出“另存为”的建议文件名（不含扩展名）；stamp 为 yyyyMMdd_HHmmss。
  ///
  /// In zh, this message translates to:
  /// **'VideoKit_{stamp}'**
  String exportFileName(String stamp);
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['zh'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'zh':
      return AppLocalizationsZh();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
