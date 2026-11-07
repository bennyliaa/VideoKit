// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Chinese (`zh`).
class AppLocalizationsZh extends AppLocalizations {
  AppLocalizationsZh([String locale = 'zh']) : super(locale);

  @override
  String get appTitle => 'VideoKit';

  @override
  String get homeTitle => '最近播放';

  @override
  String get homeGrid => '网格视图';

  @override
  String get homeList => '列表视图';

  @override
  String get homeSettings => '设置';

  @override
  String get filterAll => '全部';

  @override
  String get filterVideo => '视频';

  @override
  String get filterImage => '图片';

  @override
  String get openFile => '打开文件';

  @override
  String footerLimit(int limit) {
    return '最多保存 $limit 条 · 只保存在本机';
  }

  @override
  String get emptyTitle => '还没有播放记录';

  @override
  String get emptyBody => '选择视频或图片开始播放，看过的媒体会出现在这里，方便接着看';

  @override
  String get emptyMulti => '可多选：多个视频可进入多画面或拼接';

  @override
  String get otherAppsTitle => '也可以从其他应用打开';

  @override
  String get otherAppsBody => '在文件管理器或相册中选择“用 VideoKit 打开”';

  @override
  String get historyOff => '播放历史记录已关闭，新的播放不会被记录';

  @override
  String get emptyFiltered => '没有符合筛选的记录';

  @override
  String entryWatched(String position, String when) {
    return '看到 $position · $when';
  }

  @override
  String entryNew(String when) {
    return '未播放 · $when';
  }

  @override
  String entryViewed(String when) {
    return '上次查看 · $when';
  }

  @override
  String resolutionLines(int lines) {
    return '${lines}p';
  }

  @override
  String dimensions(int width, int height) {
    return '$width×$height';
  }

  @override
  String metaVideo(String resolution, String codec) {
    return '$resolution · $codec';
  }

  @override
  String metaImage(String size) {
    return '图片 · $size';
  }

  @override
  String get timeJustNow => '刚刚';

  @override
  String timeMinutes(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n 分钟前',
    );
    return '$_temp0';
  }

  @override
  String timeHours(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n 小时前',
    );
    return '$_temp0';
  }

  @override
  String get timeYesterday => '昨天';

  @override
  String timeDays(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n 天前',
    );
    return '$_temp0';
  }

  @override
  String get unavailable => '无法打开';

  @override
  String get unavailableReason => '文件已移动或授权失效';

  @override
  String get reselect => '重新选择';

  @override
  String get temporaryGrant => '临时授权，下次可能需要重新选择';

  @override
  String get imageBadge => '图片';

  @override
  String get menuMore => '更多';

  @override
  String get menuFromStart => '从头播放';

  @override
  String get menuMultiView => '在多画面中打开';

  @override
  String get menuDelete => '从记录中删除';

  @override
  String openChoiceTitle(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '已选择 $count 个文件',
    );
    return '$_temp0';
  }

  @override
  String get openMultiView => '在多画面中打开';

  @override
  String get openConcat => '拼接为一个视频';

  @override
  String openFailed(String name) {
    return '无法打开“$name”';
  }

  @override
  String get settingsTitle => '设置';

  @override
  String get secHistory => '播放记录';

  @override
  String get recordHistory => '记录播放历史';

  @override
  String get recordHistoryNote => '只保存在本机，不上传';

  @override
  String get savedCount => '已保存';

  @override
  String savedValue(int count, int limit) {
    return '$count / $limit 条';
  }

  @override
  String get clearHistory => '清空播放记录';

  @override
  String get clearConfirmTitle => '清空播放记录？';

  @override
  String get clearConfirmBody => '将删除全部记录与缩略图，并释放已保存的文件访问授权。原文件不受影响。';

  @override
  String get cancel => '取消';

  @override
  String get clear => '清空';

  @override
  String get cleared => '已清空播放记录';

  @override
  String get secAppearance => '外观';

  @override
  String get theme => '主题';

  @override
  String get themeDark => '深色';

  @override
  String get themeLight => '浅色';

  @override
  String get themeSystem => '跟随系统';

  @override
  String get reduceMotion => '减少动画';

  @override
  String get reduceMotionNote => '默认跟随系统设置';

  @override
  String get secLanguage => '语言';

  @override
  String get uiLanguage => '界面语言';

  @override
  String get languageNote => '英文版本后续提供';

  @override
  String get languageChinese => '简体中文';

  @override
  String get secAbout => '关于';

  @override
  String get version => '版本';

  @override
  String get licenses => '开源许可';

  @override
  String get legalese => 'VideoKit 视频播放与编辑。App 与模块使用的开源组件见下表。';

  @override
  String get multiViewTitle => '多画面';

  @override
  String concatTitle(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '拼接 $count 个视频',
    );
    return '$_temp0';
  }

  @override
  String get pickerTitle => '选择视频或图片';

  @override
  String get pickerDemoNote => '演示模式：从演示媒体中选择';

  @override
  String pickerConfirm(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '打开 $count 个',
      zero: '请选择',
    );
    return '$_temp0';
  }

  @override
  String get pickerConfirmOne => '选择';

  @override
  String get demoValley => '山谷黄昏.mkv';

  @override
  String get demoStreet => '街头夜景 · 竖屏.mp4';

  @override
  String get demoDune => '沙丘.heic';

  @override
  String get demoFireworks => '烟花.gif';

  @override
  String get demoFamily => '家庭录像.avi';

  @override
  String get demoTravel => '旅行合集.mp4';

  @override
  String get demoUnsupported => '旧格式录像.mkv';

  @override
  String get startupConnecting => '正在启动 VideoKit';

  @override
  String get startupProtocolTitle => 'VideoKit 版本不匹配';

  @override
  String get startupProtocolDetail => 'App 与播放组件的版本不一致，请安装最新版本的 App。';

  @override
  String get startupNoBackendTitle => '播放组件不可用';

  @override
  String get startupNoBackendDetail => '这个版本的 App 没有包含播放组件，请重新安装 App。';

  @override
  String get startupChannelTitle => '无法连接播放组件';

  @override
  String get startupChannelDetail => '播放组件没有响应。请重试；如果仍然失败，请重新启动 App。';

  @override
  String get startupUnknownTitle => 'VideoKit 启动失败';

  @override
  String get startupUnknownDetail => '启动时出现意外错误。请重试；如果仍然失败，请重新启动 App。';

  @override
  String exportFileName(String stamp) {
    return 'VideoKit_$stamp';
  }

  @override
  String get hostFavorite => '收藏';

  @override
  String get hostFavorited => '已收藏';

  @override
  String get hostFavoriteVideoCd => '收藏这个视频';

  @override
  String get hostUnfavoriteVideoCd => '取消收藏这个视频';

  @override
  String get hostFavoriteImageCd => '收藏这张图片';

  @override
  String get hostUnfavoriteImageCd => '取消收藏这张图片';

  @override
  String get hostTag => '标签';

  @override
  String get hostTagVideoCd => '为这个视频添加标签';

  @override
  String get hostTagImageCd => '为这张图片添加标签';

  @override
  String get tagEditorTitle => '标签';

  @override
  String get tagEditorHint => '输入新标签';

  @override
  String get tagEditorAdd => '添加';

  @override
  String get tagEditorDone => '完成';

  @override
  String get tagEditorEmpty => '还没有标签';

  @override
  String tagEditorRemove(String tag) {
    return '删除标签“$tag”';
  }

  @override
  String get historyFavorite => '已收藏';

  @override
  String historyTags(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count 个标签',
    );
    return '$_temp0';
  }

  @override
  String get recentProjects => '最近工程';

  @override
  String get recentProjectsEmpty => '还没有保存的工程。选择多个视频并“拼接为一个视频”，离开编辑器时会自动保存。';

  @override
  String recentProjectSaved(String when) {
    return '保存于 $when';
  }

  @override
  String recentProjectClips(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count 个片段',
    );
    return '$_temp0';
  }

  @override
  String get recentProjectDelete => '删除工程';

  @override
  String get recentProjectRestoreFailed => '无法打开这个工程：格式版本过新或文件已损坏';

  @override
  String get openFailedTitle => '没有打开成功';

  @override
  String get openFailedDetail => '等待时间过长，或播放组件已中断。请重试；如果仍然失败，请返回后重新打开。';

  @override
  String get editingUnavailableTitle => '暂不支持';

  @override
  String get editingUnavailableDetail => '剪辑与拼接功能即将提供';

  @override
  String get featureComingSoon => '功能即将提供';
}
