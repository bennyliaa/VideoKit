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
}
