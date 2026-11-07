// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'videokit_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Chinese (`zh`).
class VideoKitLocalizationsZh extends VideoKitLocalizations {
  VideoKitLocalizationsZh([String locale = 'zh']) : super(locale);

  @override
  String get demoModeBadge => '演示模式 · 模拟数据';

  @override
  String get demoExportNoFile => '演示模式：未生成真实媒体文件';

  @override
  String get commonOk => '确定';

  @override
  String get commonCancel => '取消';

  @override
  String get commonClose => '关闭';

  @override
  String get commonRetry => '重试';

  @override
  String get commonMore => '更多';

  @override
  String get stateLoading => '正在加载…';

  @override
  String get stateBuffering => '正在缓冲…';

  @override
  String get stateUnavailable => '不可用';

  @override
  String get statePending => '等待中';

  @override
  String get stateSelected => '已选中';

  @override
  String get playerPlay => '播放';

  @override
  String get playerPause => '暂停';

  @override
  String get playerPlaying => '播放中';

  @override
  String playerSeekValue(String position, String duration) {
    return '$position，共 $duration';
  }

  @override
  String get tracksSubtitlesOff => '关闭';

  @override
  String get tracksNoAudio => '此视频没有可选音轨';

  @override
  String get tracksNoSubtitles => '此视频没有字幕';

  @override
  String get estimateUnavailable => '无法预估';

  @override
  String durationSpoken(int hours, int minutes, int seconds) {
    String _temp0 = intl.Intl.pluralLogic(
      hours,
      locale: localeName,
      other: '$hours 小时 ',
      zero: '',
    );
    String _temp1 = intl.Intl.pluralLogic(
      minutes,
      locale: localeName,
      other: '$minutes 分 ',
      zero: '',
    );
    return '$_temp0$_temp1$seconds 秒';
  }

  @override
  String fileSizeBytes(String value) {
    return '$value 字节';
  }

  @override
  String fileSizeKilobytes(String value) {
    return '$value KB';
  }

  @override
  String fileSizeMegabytes(String value) {
    return '$value MB';
  }

  @override
  String fileSizeGigabytes(String value) {
    return '$value GB';
  }

  @override
  String get actionRetry => '重试';

  @override
  String get actionChooseOtherTrack => '选择其他音轨';

  @override
  String get actionReduceQuality => '降低质量';

  @override
  String get actionFreeSpace => '释放空间';

  @override
  String get actionGrantPermission => '授予访问权限';

  @override
  String get actionCorrectTracking => '纠正目标';

  @override
  String get actionChooseOtherSource => '选择其他文件';

  @override
  String get errorSourceNotFound => '找不到文件';

  @override
  String get errorSourcePermissionDenied => '无权访问此文件';

  @override
  String get errorSourceDisconnected => '连接中断';

  @override
  String get errorSourceTimeout => '连接超时';

  @override
  String get errorUnsupportedContainer => '不支持此格式（容器）';

  @override
  String get errorUnsupportedVideoCodec => '不支持此格式（视频编码）';

  @override
  String get errorUnsupportedAudioCodec => '不支持此格式（音频编码）';

  @override
  String get errorDecoderUnavailable => '此设备没有可用的解码器';

  @override
  String get errorDecoderResourceExhausted => '资源不足，已暂停';

  @override
  String get errorCorruptMedia => '文件已损坏或不完整';

  @override
  String get errorSeekUnsupported => '此来源不支持跳转';

  @override
  String get errorOutputPermissionDenied => '无权保存输出';

  @override
  String get errorOutputSpaceInsufficient => '存储空间不足';

  @override
  String get errorOutputCapabilityUnsupported => '目标位置无法保存此输出';

  @override
  String get errorEncoderUnavailable => '此预设没有可用的编码器';

  @override
  String get errorExportFailed => '导出失败';

  @override
  String get errorTrackingModelUnavailable => '此设备不支持跟踪';

  @override
  String get errorTrackingLost => '跟踪丢失';

  @override
  String get errorCancelled => '已取消';

  @override
  String get errorHostCallbackFailed => '操作未响应';

  @override
  String get errorSessionReleased => '播放已结束';

  @override
  String get errorInternalErrorRedacted => '出现问题';
}
