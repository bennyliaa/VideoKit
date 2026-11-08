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
  String get stateBuffering => '缓冲中';

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
  String get actionCheckPermission => '检查访问权限';

  @override
  String get actionReconnectSource => '重新连接';

  @override
  String get actionCloseOtherSessions => '关闭其他画面';

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

  @override
  String get errorInvalidState => '当前状态下无法执行此操作';

  @override
  String get errorInvalidArgument => '参数无效';

  @override
  String get errorUnsupportedSnapshotVersion => '此版本无法打开该记录';

  @override
  String get playerBack => '返回';

  @override
  String playerRewind(int seconds) {
    return '后退 $seconds 秒';
  }

  @override
  String playerForward(int seconds) {
    return '前进 $seconds 秒';
  }

  @override
  String get playerSpeed => '倍速';

  @override
  String playerSpeedValue(String speed) {
    return '$speed×';
  }

  @override
  String get playerSubtitles => '字幕';

  @override
  String get playerAudioTrack => '音轨';

  @override
  String get playerVolume => '音量';

  @override
  String get playerMute => '静音';

  @override
  String get playerUnmute => '取消静音';

  @override
  String get playerLockOrientation => '锁定方向';

  @override
  String get playerUnlockOrientation => '解除方向锁定';

  @override
  String get playerFullscreen => '全屏';

  @override
  String get playerExitFullscreen => '退出全屏';

  @override
  String get playerEdit => '编辑';

  @override
  String get playerSeekBar => '播放进度';

  @override
  String get playerPicture => '视频画面';

  @override
  String playerFitMode(String mode) {
    return '画面适配：$mode';
  }

  @override
  String get fitModeFit => '适应';

  @override
  String get fitModeFill => '填充';

  @override
  String get fitModeOriginal => '原尺寸';

  @override
  String get settingsTitle => '播放设置';

  @override
  String get tracksUnsupported => '设备不支持';

  @override
  String trackUnnamed(int index) {
    return '轨道 $index';
  }

  @override
  String trackAudioUnnamed(int index) {
    return '音轨 $index';
  }

  @override
  String get stateLoadingTitle => '正在打开…';

  @override
  String get stateLoadingDetail => '读取媒体信息';

  @override
  String get stateEndedTitle => '播放结束';

  @override
  String get actionReplay => '重新播放';

  @override
  String get stateReleasedTitle => '播放已关闭';

  @override
  String get stateLockedTitle => '内容已隐藏';

  @override
  String get stateDetailConnection => '请检查网络或存储连接后重试';

  @override
  String get stateDetailPermission => '请在应用中授予访问权限';

  @override
  String get stateDetailUnsupported => '此设备无法播放该格式，详见能力说明';

  @override
  String get stateDetailCorrupt => '文件可能未完整下载或已损坏';

  @override
  String get stateDetailResources => '关闭其他画面后可以重试';

  @override
  String get stateDetailTrackingLost => '在丢失的区间重新指定目标';

  @override
  String get stateDetailSpace => '释放空间或降低导出质量';

  @override
  String get stateDetailGeneric => '如果问题持续出现，请稍后再试';

  @override
  String hostActionFailed(String action) {
    return '“$action”未完成';
  }

  @override
  String get hostActionMore => '更多操作';

  @override
  String get navigationUnavailable => '没有更多内容了';

  @override
  String get navigationFailed => '无法切换到下一项，请重试';

  @override
  String get noticeImageMemoryReduced => '内存不足，已降低图片清晰度';

  @override
  String get noticeAudioUnsupported => '无法播放此音轨，正在静音播放';

  @override
  String get noticeResourceDegraded => '设备资源紧张，已降低这路画面的画质';

  @override
  String get noticeAudioFocusLost => '其他应用正在播放，已暂停';

  @override
  String get commandUnavailable => '此操作当前不可用';

  @override
  String badgeClipped(String text) {
    return '$text…';
  }

  @override
  String get playerRotate => '旋转画面';

  @override
  String get moreGroupPlayer => '播放控制';

  @override
  String get viewerPicture => '图片画面';

  @override
  String get viewerInfo => '图片信息';

  @override
  String get viewerZoomLabel => '缩放比例';

  @override
  String get viewerMiniMap => '可见区域';

  @override
  String get viewerPrevious => '上一张';

  @override
  String get viewerNext => '下一张';

  @override
  String get viewerLoop => '循环播放';

  @override
  String viewerAnimatedBadge(String format) {
    return '$format · 动态';
  }

  @override
  String get infoFormat => '格式';

  @override
  String get infoDimensions => '尺寸';

  @override
  String get infoFileSize => '文件大小';

  @override
  String get infoOrientation => '方向';

  @override
  String get infoUnknown => '未知';

  @override
  String infoFormatValue(String format, String kind) {
    return '$format（$kind）';
  }

  @override
  String infoDimensionsValue(int width, int height) {
    return '$width × $height';
  }

  @override
  String get imageKindStatic => '静态';

  @override
  String get imageKindAnimated => '动态';

  @override
  String get orientationPortrait => '竖向';

  @override
  String get orientationLandscape => '横向';

  @override
  String get orientationSquare => '方形';

  @override
  String get slotActiveAudio => '发声';

  @override
  String get slotActivateAudio => '设为发声画面';

  @override
  String get slotImage => '图片';

  @override
  String get slotAnimated => '动图';

  @override
  String get slotLoading => '加载中';

  @override
  String get slotPausedTitle => '已暂停 · 资源不足';

  @override
  String get slotPausedDetail => '点按恢复（将暂停其他画面）';

  @override
  String get slotPausedShort => '已暂停';

  @override
  String get slotLowResolution => '已降为低分辨率';

  @override
  String get slotLowResolutionShort => '低清';

  @override
  String get gridTitle => '多画面';

  @override
  String gridCount(int count, int max) {
    return '$count / $max';
  }

  @override
  String get gridHint => '点按画面切换声音来源，同一时间只有一路发声';

  @override
  String get gridAddMedia => '添加媒体';

  @override
  String get gridLayout => '布局';

  @override
  String get gridLayoutAuto => '自动';

  @override
  String get gridLayout2x2 => '2×2';

  @override
  String get gridLayout3x3 => '3×3';

  @override
  String get gridLayout3x4 => '4×3';

  @override
  String get slotPlaceholderTitle => '资源不足 · 未播放';

  @override
  String get slotPlaceholderDetail => '减少画面数量后点按重试';

  @override
  String get slotPlaceholderShort => '未播放';

  @override
  String get slotErrorOnly => '仅此格受影响';

  @override
  String get slotRemove => '移除';

  @override
  String slotLabel(int index, String title) {
    return '第 $index 格，$title';
  }

  @override
  String get gridMuteAll => '全部静音';

  @override
  String get infoFrameCount => '帧数';

  @override
  String infoFrameCountValue(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count 帧',
    );
    return '$_temp0';
  }

  @override
  String get infoDecodedMemory => '解码内存';

  @override
  String get infoSampleSize => '解码采样';

  @override
  String get infoSampleFull => '原始分辨率';

  @override
  String infoSampleSizeValue(int size) {
    return '按 1/$size 采样';
  }

  @override
  String get editorTitle => '剪辑';

  @override
  String get editorUndo => '撤销';

  @override
  String get editorRedo => '重做';

  @override
  String get editorExport => '导出';

  @override
  String get editorAddVideo => '添加视频';

  @override
  String get editorSplit => '分割';

  @override
  String get editorDelete => '删除';

  @override
  String get editorReorder => '排序';

  @override
  String get editorMask => '打码';

  @override
  String get editorTrack => '自动跟踪';

  @override
  String get editorTrackShort => '跟踪';

  @override
  String get editorClipsTab => '剪辑';

  @override
  String get editorAddTab => '添加';

  @override
  String get editorNoSelection => '点按时间线上的片段进行编辑';

  @override
  String get editorEmpty => '还没有片段，先添加视频';

  @override
  String editorClip(int index) {
    return '片段 $index';
  }

  @override
  String editorClipProps(int index) {
    return '片段 $index 属性';
  }

  @override
  String editorClipSummary(int index, String duration) {
    return '片段 $index · $duration';
  }

  @override
  String get propSource => '来源';

  @override
  String get propIn => '起点';

  @override
  String get propOut => '终点';

  @override
  String get propDuration => '时长';

  @override
  String durationSeconds(String seconds) {
    return '$seconds 秒';
  }

  @override
  String get keyframeAlignNotice => '快速拼接时边界将对齐到最近的关键帧';

  @override
  String get concatFast => '参数一致，可快速拼接';

  @override
  String get concatTranscodeTitle => '参数不一致，将统一转码';

  @override
  String concatTranscodeDetail(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '有 $count 个视频的分辨率、帧率、编码或方向与第一个不同',
    );
    return '$_temp0：将按导出预设统一转码，并校正旋转方向。';
  }

  @override
  String get fastConcatAvailable => '快速拼接可用';

  @override
  String get fastConcatUnavailable => '快速拼接（无重编码）：不可用';

  @override
  String get concatParamsMatch => '参数一致';

  @override
  String get concatPathFast => '拼接方式：快速拼接（不重新编码）';

  @override
  String get concatPathTranscode => '拼接方式：统一转码';

  @override
  String get concatReasonDevice => '此设备不支持快速拼接';

  @override
  String get concatReasonEngine => '导出检查未通过快速拼接，已改为统一转码';

  @override
  String get concatDiffResolution => '分辨率不同';

  @override
  String get concatDiffFrameRate => '帧率不同';

  @override
  String get concatDiffCodec => '视频编码不同';

  @override
  String get concatDiffRotation => '旋转方向不同';

  @override
  String get concatDiffOther => '有视频无法直接拼接';

  @override
  String get concatDiffProbeIncomplete => '有视频的编码、尺寸或帧率未知';

  @override
  String estimateLine(String duration, String size) {
    return '预计 $duration · 约 $size';
  }

  @override
  String estimateDurationOnly(String duration) {
    return '预计 $duration · 大小无法预估';
  }

  @override
  String get estimateUnknown => '无法预估';

  @override
  String editorTime(String position, String duration) {
    return '$position / $duration';
  }

  @override
  String get timelineLabel => '时间线';

  @override
  String get timelineZoomIn => '放大时间线';

  @override
  String get timelineZoomOut => '缩小时间线';

  @override
  String clipSemantic(int index, String start, String end, String duration) {
    return '片段 $index，$start 至 $end，时长 $duration';
  }

  @override
  String get clipMoveEarlier => '前移一位';

  @override
  String get clipMoveLater => '后移一位';

  @override
  String get clipTrimStart => '调整起点';

  @override
  String get clipTrimEnd => '调整终点';

  @override
  String get sourcesTitle => '多视频拼接';

  @override
  String sourcesCount(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count 个视频',
    );
    return '$_temp0';
  }

  @override
  String sourceMeta(int width, int height, String fps, String codec) {
    return '$width × $height · $fps fps · $codec';
  }

  @override
  String sourceRotated(int degrees) {
    return '旋转 $degrees°';
  }

  @override
  String get maskTitle => '打码';

  @override
  String get maskDone => '完成';

  @override
  String get maskListTitle => '遮罩';

  @override
  String get maskAdd => '添加遮罩';

  @override
  String maskName(int index) {
    return '遮罩 $index';
  }

  @override
  String maskSummary(String style, String start, String end) {
    return '$style · $start – $end';
  }

  @override
  String maskKeyframes(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '关键帧 $count 个',
    );
    return '$_temp0';
  }

  @override
  String get maskKeyframesTracker => '关键帧由跟踪生成';

  @override
  String get maskTypeManual => '手动';

  @override
  String get maskTypeFace => '人脸跟踪';

  @override
  String get maskTypeObject => '物体跟踪';

  @override
  String get maskStyle => '样式';

  @override
  String get maskStyleMosaic => '马赛克';

  @override
  String get maskStyleBlur => '模糊';

  @override
  String get maskStrength => '强度';

  @override
  String get maskDelete => '删除遮罩';

  @override
  String get maskEnable => '启用遮罩';

  @override
  String maskKeyframeTitle(int index) {
    return '遮罩 $index 关键帧';
  }

  @override
  String get maskAddKeyframe => '在当前帧添加关键帧';

  @override
  String get maskRemoveKeyframe => '删除当前关键帧';

  @override
  String get maskBox => '遮罩区域';

  @override
  String get maskBoxHint => '拖动移动，四角与四边调整大小';

  @override
  String get maskNone => '还没有遮罩，点“添加遮罩”或使用自动跟踪';

  @override
  String get trackLocalOnly => '本机处理 · 不上传';

  @override
  String get trackDetectFaces => '检测人脸';

  @override
  String trackDetected(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '检测到 $count 张人脸',
      zero: '当前帧没有检测到人脸',
    );
    return '$_temp0';
  }

  @override
  String get trackChooseHint => '选择需要打码的目标，不会默认处理所有人';

  @override
  String trackTarget(String letter) {
    return '目标 $letter';
  }

  @override
  String trackFace(int index) {
    return '人脸 $index';
  }

  @override
  String get trackTapToSelect => '点按选择';

  @override
  String get trackObject => '框选物体';

  @override
  String get trackObjectHint => '在画面上点选或拖出物体所在区域';

  @override
  String get trackRunning => '跟踪中';

  @override
  String trackAnalyzed(String done, String total) {
    return '已分析 $done / $total';
  }

  @override
  String get trackAnalyzing => '正在分析…';

  @override
  String get trackCancel => '取消跟踪';

  @override
  String get trackCompleted => '跟踪完成';

  @override
  String get trackCancelled => '已取消跟踪';

  @override
  String get trackFailed => '跟踪失败';

  @override
  String get coverageTracked => '已跟踪';

  @override
  String get coverageLow => '置信度低';

  @override
  String get coverageAmbiguous => '可能混淆';

  @override
  String get coverageLost => '丢失';

  @override
  String get coverageNotAnalyzed => '未分析';

  @override
  String get coverageAccepted => '已确认';

  @override
  String coverageStripLabel(String name) {
    return '$name 跟踪状态';
  }

  @override
  String coverageSegment(String state, String start, String end) {
    return '$state，$start – $end';
  }

  @override
  String get trackCorrect => '纠正';

  @override
  String get trackCorrectHint => '在画面上拖出目标的新位置';

  @override
  String get trackRecomputing => '待重新计算';

  @override
  String checkTitle(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '发现 $count 个未覆盖区间',
    );
    return '$_temp0';
  }

  @override
  String get checkSubtitle => '这些时间段内目标可能未被打码';

  @override
  String checkRange(String name, String start, String end) {
    return '$name · $start – $end';
  }

  @override
  String get checkJump => '跳转纠正';

  @override
  String get checkManual => '手动关键帧';

  @override
  String get checkFullFrame => '全画面打码';

  @override
  String get checkBack => '返回修正';

  @override
  String get checkForce => '仍要导出（结果将标记为“打码不完整”）';

  @override
  String get exportTitle => '导出';

  @override
  String get exportPresets => '导出预设';

  @override
  String get presetOriginal => '原始';

  @override
  String get presetOriginalDetail => '与源视频相同 · 推荐';

  @override
  String get preset1080 => '1080p';

  @override
  String get preset720 => '720p';

  @override
  String presetLongEdge(int px) {
    return '长边 $px';
  }

  @override
  String get presetUnavailable => '此设备不可用';

  @override
  String exportFormat(String format) {
    return '格式 $format';
  }

  @override
  String get exportChecks => '导出前检查';

  @override
  String get checkEncoder => '编码器';

  @override
  String get checkEncoderOk => '编码器可用';

  @override
  String get checkEncoderFail => '编码器不可用';

  @override
  String get checkOutput => '输出位置';

  @override
  String get checkOutputOk => '由宿主提供';

  @override
  String get checkOutputFail => '输出位置不支持写入';

  @override
  String get checkSpace => '空间';

  @override
  String checkSpaceValue(String need, String free) {
    return '需约 $need，可用 $free';
  }

  @override
  String checkSpaceNeed(String need) {
    return '需约 $need';
  }

  @override
  String get checkSpaceUnknown => '无法预估所需空间';

  @override
  String get checkSpaceFail => '空间不足';

  @override
  String checkSpaceFailSize(String size) {
    return '空间不足，需释放约 $size';
  }

  @override
  String get checkCoverage => '打码覆盖';

  @override
  String get checkCoverageOk => '全部目标已覆盖';

  @override
  String get checkCoverageNone => '没有自动跟踪遮罩';

  @override
  String checkCoverageFail(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '有 $count 个未覆盖区间',
    );
    return '$_temp0';
  }

  @override
  String get checkPassed => '通过';

  @override
  String get checkProblem => '有问题';

  @override
  String get checkRunning => '正在检查…';

  @override
  String get exportSafety => '导出生成新文件，原视频不会被修改；保存位置与最终命名由宿主确认。';

  @override
  String get exportStart => '开始导出';

  @override
  String get exportReviewCoverage => '查看未覆盖区间';

  @override
  String get exporting => '正在导出';

  @override
  String get stagePreparing => '准备';

  @override
  String get stageTracking => '跟踪';

  @override
  String get stageEncoding => '编码';

  @override
  String get stageVerifying => '校验输出';

  @override
  String get stageWriting => '写入宿主位置';

  @override
  String get stageDone => '已完成';

  @override
  String get stageWaiting => '等待';

  @override
  String get stageInProgress => '进行中';

  @override
  String stageRemaining(String duration) {
    return '约 $duration';
  }

  @override
  String stageProcessed(String done, String total) {
    return '已处理 $done / $total';
  }

  @override
  String stageOutputSize(String size) {
    return '已输出 $size';
  }

  @override
  String get exportNoPause => '导出不支持暂停。取消后可重新导出，不会留下未完成的文件。';

  @override
  String get exportCancel => '取消导出';

  @override
  String get exportCancelling => '正在取消…';

  @override
  String get exportCancelled => '已取消，未生成文件';

  @override
  String get exportCancelledPartial => '已取消，部分输出未能删除';

  @override
  String get exportFailedTitle => '导出失败';

  @override
  String get exportImpactSource => '原视频未受影响';

  @override
  String get exportImpactDiscarded => '未完成的输出已丢弃';

  @override
  String exportErrorCode(String code) {
    return '错误代码 $code';
  }

  @override
  String get exportRetry => '重新导出';

  @override
  String exportUseSmaller(String preset) {
    return '改用 $preset 重新导出';
  }

  @override
  String get exportBackToEdit => '返回编辑';

  @override
  String get exportDoneTitle => '导出完成';

  @override
  String get exportDoneDetail => '文件已写入宿主提供的临时位置，正式保存由宿主确认。';

  @override
  String get exportDone => '完成';

  @override
  String get summaryFormat => '容器 / 编码';

  @override
  String get summaryResolution => '分辨率';

  @override
  String summaryResolutionValue(String size, String orientation) {
    return '$size · $orientation';
  }

  @override
  String get summaryLandscape => '横屏';

  @override
  String get summaryPortrait => '竖屏';

  @override
  String get summarySquare => '方形';

  @override
  String get summarySource => '来源';

  @override
  String summarySourceCount(int count) {
    return '$count 个视频';
  }

  @override
  String get summaryNoWarnings => '无';

  @override
  String get summaryDuration => '时长';

  @override
  String get summarySize => '大小';

  @override
  String get summaryWarnings => '警告';

  @override
  String get warnBoundary => '边界已对齐到关键帧';

  @override
  String get warnSilence => '已为无声片段插入静音';

  @override
  String get warnCoverage => '打码不完整（已确认导出未覆盖区间）';

  @override
  String get warnTrackingIncomplete => '有遮罩的跟踪没有完成，部分画面可能没有打码';

  @override
  String get warnTrackingLost => '有遮罩在跟踪丢失的区间没有处理，这些画面可能没有打码';

  @override
  String get warnDemo => '演示模式：未生成真实媒体文件';

  @override
  String maskNameTyped(int index, String type) {
    return '遮罩 $index · $type';
  }

  @override
  String get playerMediaInfo => '参数';

  @override
  String get infoVideoCodec => '视频编码';

  @override
  String get infoAudioCodec => '音频编码';

  @override
  String get infoResolution => '分辨率';

  @override
  String get infoFrameRate => '帧率';

  @override
  String infoFrameRateValue(String value) {
    return '$value fps';
  }

  @override
  String get infoBitrate => '码率';

  @override
  String infoBitrateKbps(String value) {
    return '$value kbps';
  }

  @override
  String infoBitrateMbps(String value) {
    return '$value Mbps';
  }

  @override
  String get infoRotation => '旋转';

  @override
  String infoRotationValue(int degrees) {
    return '$degrees°';
  }

  @override
  String get infoDuration => '时长';

  @override
  String get trackChannelsMono => '单声道';

  @override
  String trackChannelsCount(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count 声道',
    );
    return '$_temp0';
  }

  @override
  String trackCodecChannels(String codec, String channels) {
    return '$codec $channels';
  }

  @override
  String get editorAutosaved => '已自动保存';

  @override
  String get editorSaving => '正在保存…';

  @override
  String get editorSaveFailed => '未保存';

  @override
  String editorTitleWithProject(String name) {
    return '$name · 剪辑';
  }

  @override
  String get trackApply => '应用到打码';

  @override
  String get stateUnsupportedTitle => '格式不支持';

  @override
  String get stateUnsupportedContainer => '本设备不支持此文件格式';

  @override
  String get stateUnsupportedVideoCodec => '本设备不支持此视频编码';

  @override
  String get stateUnsupportedAudioCodec => '本设备不支持此音频编码';

  @override
  String get actionShowCapabilities => '查看能力说明';

  @override
  String get capabilitiesTitle => '能力说明';

  @override
  String get capabilitiesVideoDecoders => '视频解码';

  @override
  String get capabilitiesAudioDecoders => '音频解码';

  @override
  String get capabilitiesFormats => '容器与编码';

  @override
  String get capabilitiesLimits => '设备建议';

  @override
  String get capabilitiesHardware => '硬件';

  @override
  String get capabilitiesSoftware => '软件';

  @override
  String capabilitiesCodecValue(String kind, String size) {
    return '$kind · 最高 $size';
  }

  @override
  String get capabilitiesSupported => '支持';

  @override
  String get capabilitiesPartial => '部分支持';

  @override
  String get capabilitiesUnsupported => '不支持';

  @override
  String get capabilitiesSessions => '同时播放';

  @override
  String capabilitiesSessionsValue(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count 路',
    );
    return '$_temp0';
  }

  @override
  String get capabilitiesMaxResolution => '最高分辨率';

  @override
  String get capabilitiesMaxFrameRate => '最高帧率';

  @override
  String get capabilitiesNone => '未报告';

  @override
  String get orientationNoRotation => '无旋转元数据';

  @override
  String orientationRotated(int degrees) {
    return '旋转 $degrees°';
  }

  @override
  String get imageEdit => '编辑';

  @override
  String get imageEditUnsupported => '编辑，暂不支持';

  @override
  String get exportSuggestFreeSpace => '建议：释放存储空间';

  @override
  String exportSuggestFreeSpaceSize(String size) {
    return '建议：释放约 $size 空间';
  }

  @override
  String playerSubtitlesRow(String name) {
    return '字幕：$name';
  }

  @override
  String get playerMoreControls => '更多控制';

  @override
  String playerMediaSummary(String size, String codec) {
    return '$size · $codec';
  }

  @override
  String get concatNext => '下一步：预览';

  @override
  String get sourceTrimAll => '裁剪：全部';

  @override
  String sourceTrimRange(String start, String end) {
    return '裁剪：$start – $end';
  }

  @override
  String estimateWithPath(String estimate, String path) {
    return '$estimate · $path';
  }
}
