// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'example_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Chinese (`zh`).
class ExampleLocalizationsZh extends ExampleLocalizations {
  ExampleLocalizationsZh([String locale = 'zh']) : super(locale);

  @override
  String get appTitle => 'VideoKit 示例';

  @override
  String get galleryTitle => 'VideoKit 主题画廊';

  @override
  String get sectionSettings => '设置';

  @override
  String get settingTheme => '主题';

  @override
  String get themeDark => '深色';

  @override
  String get themeLight => '浅色';

  @override
  String get themeSystem => '跟随系统';

  @override
  String get settingHostPrimary => '宿主主色';

  @override
  String get hostPrimaryDefault => '默认';

  @override
  String get settingLanguage => '语言';

  @override
  String get languageChinese => '中文';

  @override
  String get languagePseudo => '伪本地化';

  @override
  String get settingTextScale => '字体缩放';

  @override
  String get settingReduceMotion => '减少动画';

  @override
  String schemaVersion(int version) {
    return 'Token 架构版本：$version';
  }

  @override
  String get sectionColors => '颜色 Token';

  @override
  String get sectionStatus => '状态色';

  @override
  String get sectionTypography => '文字样式';

  @override
  String get sectionDimensions => '间距与圆角';

  @override
  String get sectionAnimations => '动效';

  @override
  String get sectionComponents => '组件样式';

  @override
  String get sectionErrors => '错误文案';

  @override
  String colorSwatch(String token, String hex) {
    return '$token，$hex';
  }

  @override
  String contrastRatio(String ratio) {
    return '对比度 $ratio:1';
  }

  @override
  String typographySample(String style, String size) {
    return '$style · $size · 敏捷的狐狸跳过懒狗 0123456789';
  }

  @override
  String dimensionValue(String name, String value) {
    return '$name $value';
  }

  @override
  String animationDurations(int press, int small, int normal, int page) {
    return '按下 $press · 小 $small · 常规 $normal · 页面 $page 毫秒';
  }

  @override
  String get animationToggle => '演示动效';

  @override
  String get statusTracked => '已跟踪 / 成功';

  @override
  String get statusLowConfidence => '置信度低';

  @override
  String get statusAmbiguous => '可能混淆';

  @override
  String get statusLost => '丢失 / 错误';

  @override
  String get statusInfo => '信息';

  @override
  String get componentButtonPrimary => '主按钮';

  @override
  String get componentButtonSecondary => '次按钮';

  @override
  String get componentButtonText => '文字按钮';

  @override
  String get componentButtonIcon => '图标按钮';

  @override
  String get componentChip => '选项片 1.5×';

  @override
  String componentBadge(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count 条',
    );
    return '$_temp0';
  }

  @override
  String get componentSeekBar => '进度条';

  @override
  String get stateNormal => '常态';

  @override
  String get statePressed => '按下';

  @override
  String get stateFocused => '焦点';

  @override
  String get stateDisabled => '禁用';

  @override
  String get stateSelected => '选中';

  @override
  String get stateHovered => '悬停';

  @override
  String errorLine(String code, String message) {
    return '$code：$message';
  }

  @override
  String timecodeRange(String position, String duration) {
    return '$position / $duration';
  }

  @override
  String get sectionDemos => '演示页面';

  @override
  String get navComponents => '组件';

  @override
  String get navPlayer => '播放器';

  @override
  String get componentsTitle => '组件库';

  @override
  String get sectionButtons => '按钮';

  @override
  String get sectionIconButtons => '图标按钮';

  @override
  String get sectionBadges => '角标与演示标识';

  @override
  String get sectionSlider => '滑杆';

  @override
  String get sectionStateViews => '状态视图';

  @override
  String get sectionHostActions => '宿主动作栏';

  @override
  String get sectionSheets => '面板与轻提示';

  @override
  String get openSheet => '打开面板';

  @override
  String get showToast => '显示轻提示';

  @override
  String get sheetSampleTitle => '示例面板';

  @override
  String get sheetSampleBody => '按返回键或 Esc 关闭面板，不会退出页面。';

  @override
  String get toastSample => '已添加到收藏';

  @override
  String get volumeLabel => '音量';

  @override
  String get badgeSample => '新';

  @override
  String get badgeLongSample => '12345';

  @override
  String get playerDemoTitle => '播放器演示';

  @override
  String get playerDemoVideoTitle => '演示视频';

  @override
  String get scenarioLabel => '场景';

  @override
  String get scenarioNormal => '正常';

  @override
  String get scenarioSlowLoad => '慢加载';

  @override
  String get scenarioBuffering => '缓冲';

  @override
  String get scenarioDisconnect => '断线';

  @override
  String get scenarioUnsupported => '不支持';

  @override
  String get scenarioHostActionTimeout => '宿主动作超时';

  @override
  String get editNotAvailable => '剪辑页面将在后续批次提供';

  @override
  String get hostPanelHint => '宿主面板插槽';

  @override
  String get hostFavorite => '收藏';

  @override
  String get hostFavorited => '已收藏';

  @override
  String get hostFavoriteCd => '收藏这个视频';

  @override
  String get hostUnfavoriteCd => '取消收藏这个视频';

  @override
  String get hostTag => '标签';

  @override
  String get hostTagCd => '为这个视频添加标签';

  @override
  String get hostDelete => '删除';

  @override
  String get hostDeleteCd => '删除这个视频';

  @override
  String get hostShare => '分享';

  @override
  String get hostShareCd => '分享这个视频';

  @override
  String get hostDone => '已完成';

  @override
  String get navImageViewer => '图片';

  @override
  String get navMultiView => '多画面';

  @override
  String get imageDemoTitle => '图片查看演示';

  @override
  String get demoImageDune => '沙丘.heic';

  @override
  String get demoImageFireworks => '烟花.gif';

  @override
  String get demoImageForest => '森林.webp';

  @override
  String get demoImageBroken => '新格式.jxl';

  @override
  String get multiViewTitle => '多画面';

  @override
  String multiViewCount(int count, int max) {
    return '$count / $max';
  }

  @override
  String get multiViewHint => '点按画面切换声音来源，同一时间只有一路发声';

  @override
  String get multiViewAdd => '添加媒体';

  @override
  String get multiViewLayout => '布局';

  @override
  String get layoutAuto => '自动';

  @override
  String get layout2x2 => '2×2';

  @override
  String get layout3x3 => '3×3';

  @override
  String get layout3x4 => '4×3';

  @override
  String multiViewNotice(int suggested, int paused) {
    return '当前设备建议同时播放 $suggested 路视频：已暂停 $paused 路离屏或较早加入的画面，显示封面';
  }

  @override
  String demoSlotTitle(int index) {
    return '演示画面 $index';
  }
}
