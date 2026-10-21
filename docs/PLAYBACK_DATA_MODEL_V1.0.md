# VideoKit 播放子系统数据模型

## 2026-10-21 国际化详细设计补充（当前有效）

国际化设置与解析快照见[国际化数据模型](INTERNATIONALIZATION_DATA_MODEL_V1.0.md)，行为见[《VideoKit 国际化详细设计》](INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)。App UI locale、SubtitleLanguagePreference、RecognitionLanguagePreference、TranslationLanguagePreference独立；subtitle cue内容/媒体PTS不随UI语言变化。RecognitionTask/TranslationRequest及对应结果设计补充所属configRevision用于本扩展设置变更失效；结合原媒体generation/epoch接纳，不为了UI切换提升播放epoch。新增字段正式实现前冻结schema。

本次仅文档更新，项目继续暂停；主里程碑、原P0与历史冻结证据保持，D1未过/M0未启。

版本V1.0；2026-10-21；设计字段基线，未冻结ABI/实现。主设计：[播放子系统详细设计](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)。沿原PUBLIC_API_CONTRACT语义，后续实现前评审签名及schema版本。原D1来源、产物、状态和账本不迁移不改写。

## 1. 共同标识与时间规则

ID均是不透明标识，不能当文件路径、凭据或可执行命令。sessionId标会话，mediaToken由宿主授权，bindingGeneration在换媒体递增，timelineEpoch在Seek/换音轨/不连续递增；requestId/taskId用于幂等和取消，sequence为会话有序事件。相同generation内epoch也必须匹配；旧结果丢弃仍须归还资源。

mediaTimeUs使用int64微秒，来自媒体PTS。monotonicNs用于本机耗时/超时，不跨进程当全局绝对时间，需相关时钟域。未知时长/长度/位置用nullable+reason，不以0或负数伪装。duration/position等非负并校验溢出；字幕偏移可有符号，原readAt EOF=-1不受模型未知值规则影响。JSON整数不得用bool/string/小数替代；跨Dart/JS桥需保证int64无损编码，不能不经检查转double。

## 2. 核心对象

| 对象 | 必需字段/约束 | 所有者与有效期 |
| --- | --- | --- |
| CommandEnvelope | apiVersion,sessionId,bindingGeneration,requestId,command,payload | 会话接纳，返回accepted与真正completed分离 |
| EventEnvelope | schemaVersion,sessionId,bindingGeneration,timelineEpoch,sequence,monotonicTimeNs,payloadType,payload,requestId? | 会话原事件；关键终态可查询 |
| SourceDescriptor | mediaToken,mediaKind,sourceFactory,seekability,knownLength?,mimeHint?,extensionHint? | 宿主租约；序列化只存描述不可存factory/原句柄 |
| MediaInfo | container?,durationUs?,video/audio/subtitle tracks,orientation,seekRange?,probeWarnings | probe结果带来源generation；不等实际解码通过 |
| TrackDescriptor | trackId,type,languageTag?,role?,codec?,backendTechnicalIdentity,selectable,textAccessible? | 当前media+generation；索引不能代stable identity |
| CapabilityReport | operation,status,reason,backend/version,platform,mediaConstraints,evidenceRef? | SUPPORTED/UNSUPPORTED/UNPROVEN；运行时与静态声明区分 |
| PlaybackClockSnapshot | positionUs?,bufferedPositionUs?,rate,state,epoch,isEstimated,anchorMonotonicNs | 后端媒体时钟；估计与解码实际落点分列 |
| PlaybackSnapshot | snapshotSchema,mediaFingerprint,state,positionUs?,rate,volume,muted,trackPreferences,viewTransform,subtitleSettings | 宿主保存；无解码器/Surface/model指针 |
| ResourceLease | leaseId,consumerId,purpose,reserved,actualKnown?,returnState | 宿主范围manager；实际原返后才归还 |
| StructuredError | code,stage,retryable,suggestedAction,typedArgs,resourceContractVersion,redactedDiagnostic,sessionId?,requestId?,taskId? | 内部异常映射稳定码；诊断不含凭据/字幕正文 |

Capability不采用“后缀支持=true”；容器+编码+输入seek性+平台解码/字幕路径分别判断。错误与状态枚举新增需API冻结，不以本草案强改现有接口。

## 3. 字幕对象与派生关联

SubtitleTrack={trackId,sourceKind:EMBEDDED/EXTERNAL/ASR/TRANSLATED,languageTag?,renderPath,textAccessible,parentTrackId?,modelRef?,bindingGeneration}。翻译轨仅引用parentTrackId，不持有引擎实例。

SubtitleCue={cueId,trackId,revision,startUs,endUs?,payloadKind:TEXT/BITMAP,text?,bitmapRef?,styleRef?,finality:PARTIAL/FINAL,sourceCueId?,sourceCueRevision?,bindingGeneration,timelineEpoch}。区间[start,end)，FINAL必须end>start；PARTIAL未知end明确不最终化。TEXT/BITMAP互斥，bitmapRef受资源租约约束，不把大像素序列塞JSON。revision单调、同ID旧revision拒绝；partial删除/retract显式事件，非静默留下旧文字。修改原文后旧翻译revision必须失效。

SubtitleSettings={primaryTrackId?,secondaryTrackId?,offsetUs,fontScale,position,styleOverrides,visible}，全部值有能力/范围校验，偏移不改源Cue时间。ViewTransform沿既有媒体M/显示V/导出O区分，不把字幕显示坐标直接当导出坐标。

## 4. PCM、识别与翻译任务

| 对象 | 字段与约束 |
| --- | --- |
| PcmChunk | streamId,chunkId,bindingGeneration,timelineEpoch,audioTrackId,startMediaPtsUs,sampleRate,channels,sampleFormat,validFrameCount,bufferLease,discontinuity；缓冲仅真实消费完成可复用，不传Dart逐帧数据 |
| RecognitionTask | taskId,sessionId,source/windowRange,modelRef,languageHintTag?,bindingGeneration,timelineEpoch,recognitionConfigRevision,state,queueBudget,cancellationToken；原速PCM与原媒体PTS，不以播放倍速重写采样率 |
| RecognitionSegment | taskId,segmentId,revision,text,languageTag?,startUs,endUs?,finality,qualityFlags,sessionId,bindingGeneration,timelineEpoch,recognitionConfigRevision；无置信度时null，不编造分数 |
| TranslationRequest | taskId,sourceTrackId,cues[cueId/revision/text/time],sourceLanguageTag?,targetLanguageTag,contextPolicy,modelRef/providerRef,sessionId,bindingGeneration,timelineEpoch,translationConfigRevision,deadlinePolicy |
| TranslationResult | taskId,sourceCueId/revision,targetLanguageTag,text,status,modelRef,qualityFlags,sessionId,bindingGeneration,timelineEpoch,translationConfigRevision；不允许改原时间/触发外部工具 |
| ModelDescriptor | modelId,upstream,version,weightsHash,format,quantization,languageCapabilities,licenseRef,sizeBytes,validatedDeviceProfiles；未知权利阻塞分发 |
| TaskReturnReport | taskId,logicalState,originalCallReturned,bufferReturned,callbacksReturned,leaseReleased,firstFailure?,unknownReasons；取消请求不等资源已返 |

任务状态建议QUEUED/RUNNING/CANCEL_REQUESTED/COMPLETED/CANCELLED/FAILED；逻辑终态不可逆，原返可迟到独立更新return report，不将FAILED升级成功或释放仍UNKNOWN预算。partial结果不是COMPLETED。

## 5. 快照、缓存与数据安全

schemaVersion/API/binding/model manifest分别版本化。新增可选字段向后兼容；未知major拒绝；恢复以媒体指纹/宿主新租约核源变化，轨道失效warning回默认，不沿路径偷偷重连。任务/原指针不持久化恢复；恢复重新创建bindingGeneration/timelineEpoch。

翻译缓存键至少source内容hash+cueRevision+语言对+modelVersion/quantization+promptPolicy。默认会话内存；宿主显式启用持久化才写，删除与配额可控。字幕文本可能含隐私和恶意指令，日志脱敏；在线端点/密钥仅宿主管理，不进入Snapshot/Cue。模型下载临时文件校验hash后原子就位，不把下载中模型发布为可用。

## 6. 数据验收映射

PB-01/07验证generation/epoch/request及原返；PB-02验证64位/EOF/源租约；PB-05验证cue半开区间/revision/位图文本；PB-08验证schema/快照/无损整数；ASR-01验证sample→PTS/换轨迟返；TR-01验证cue映射/缓存隔离。具体值域、队列与质量阈值实施前冻结，当前PLANNED_NOT_STARTED。项目保持暂停。

## 7. 统一命名与接口对齐

规范字段为bindingGeneration/timelineEpoch，原文解释中的generation/epoch仅作语义简称，wire不得并存两套字段。识别和翻译任务/结果分别必须带recognitionConfigRevision与translationConfigRevision；UI localeGeneration不参与内容任务身份。StructuredError新增typedArgs/resourceContractVersion并沿[统一契约](API_DATA_CONTRACT_V1.0.md)定义；兼容别名和未来major拒绝在此统一，不改冻结D1产物。

字幕/快照设置仍是Kit技术选择和显示状态，App四域用户意图见国际化模型。TaskReturnReport采用统一逻辑状态/原调用返回状态两层，不把cancel请求或UNKNOWN记资源释放。设计字段Schema为辅助片段，不替代合法状态/所有权与范围语义校验。
