# VideoKit 公共 API 契约

## 2026-10-21 国际化详细设计补充（当前有效）

按[《VideoKit 国际化详细设计》](INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)和[国际化数据模型](INTERNATIONALIZATION_DATA_MODEL_V1.0.md)补齐语言契约：Kit稳定错误code+类型参数，App按当前资源映射，不以译文判断业务；UiLocalePreference只在宿主显示层。字幕轨道languageTag、识别AUTO/EXPLICIT、翻译source/target分离；localeGeneration、recognitionConfigRevision、translationConfigRevision与媒体generation/epoch分开。接口/字段为设计基线，尚未冻结ABI，不直接修改历史产物。

本次仅文档更新，项目继续暂停；主里程碑、原P0与历史冻结证据保持，D1未过/M0未启。

## 2026-10-21 最新播放子系统设计基线

播放详细接口与数据源参考[《VideoKit 播放子系统详细设计》](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)及[播放数据模型](PLAYBACK_DATA_MODEL_V1.0.md)。新增设计标识timelineEpoch区分同媒体Seek/换音轨旧任务，bindingGeneration沿原换媒体语义；新增Cue revision、PcmChunk媒体PTS、TaskReturnReport区分取消请求/逻辑终态/真实原返。PlaybackBackend、SubtitleProvider、AudioTapProvider、SpeechRecognizer、TranslationProvider为设计接口，尚未冻结语言签名/ABI，不直接改变现有产物。第三方/平台类型不得泄露，Core不依赖可选模型。保留readAt EOF=-1及零长=0；未知数据模型值用null+原因，禁止误改原读契约。

本节为当前设计；被撤销指令已从执行正文移出，修改前原文见history/design/2026-10-21-consolidation/。历史证据保持，项目继续暂停。

版本：V1.0；日期：2026-10-05；状态：语义设计草案，接口未冻结。

## 1. 公共边界

原文第 13–19 节建议接口作为起点。API、binding、snapshotSchema、editProjectSchema 分别版本化；语义版本主版本改变表示不兼容。跨平台遵守共同契约，各语言惯用封装不要求完全相同方法签名。Android API 可使用 Kotlin Flow/挂起接口，但不得将其当作 C ABI。

公共类型不得包含 Browser 数据表、SMBJ、Room、Compose 页面、解码器或模型类型。技术诊断与用户显示文案分开；错误包含code、stage、retryable、suggestedAction、typedArgs、resourceContractVersion、redactedDiagnostic、sessionId/requestId/taskId。

## 2. 顶层对象

| 对象 | 核心操作 | 归属 |
| --- | --- | --- |
| VideoKitFactory | capabilities、createSession、createEditProject | 实例工厂，无全局当前媒体 |
| MediaSession | bind、execute、updateHostActions、captureState、release | 单媒体及其资源 |
| EditProject | addSource、apply、snapshot、restore、track、cancelTracking、export、cancelExport、release | 多输入编辑工程 |
| HostCallbacks | action、navigation、snapshot、playbackEvent、controlsVisible、sourceReleased、error | 可取消宿主回调 |
| ResourceBudget | reserve、release、report、thermalUpdate | 宿主注入、可按窗口共享 |

保留原文要求，并补齐跟踪取消与工程释放；不增加源删除 API。无 UI 引擎模式、Compose/View、Flutter bindings 都调用相同会话契约。

## 3. 媒体源与读取

SourceDescriptor = mediaToken、mediaKind、displayName?、mimeHint?、extensionHint?、knownLength?、seekability、sourceFactory。长度是 64 位；hint 不替代实际探测。sourceFactory 创建不同用途（probe/playback/image/edit/tracking/asr/output-validation，按授权与能力）的短生命周期句柄。

ReadHandle.readAt(offset, target, targetOffset, length) 必须校验非负范围与溢出；可短读，EOF 返回 -1，length=0 返回 0；length>0 时不得用 0 表示持续无进展。超时和断线返回稳定错误。EOF/长度冲突标记源变化或损坏。随机读允许并发的范围由 handle capability 报告，默认串行；跨线程调用不依赖共享文件游标。

readAt可取消；close逻辑幂等、原物理close仅一次，重复操作ID只查询/返回缓存，PENDING/UNKNOWN不得再发close。调用方拥有目标缓冲直至操作完成；取消完成前不得复用。源改变时由宿主提供新 bindingGeneration 与新租约；Kit 不沿旧路径自动重连。

## 4. 命令排序与状态

所有命令携带 sessionId、bindingGeneration、requestId；每会话串行接纳。连续 Seek 可合并为最新请求，被替代的命令返回 SUPERSEDED。结果枚举 EXECUTED、REJECTED、SUPERSEDED、UNSUPPORTED、RELEASED。异步接纳结果与实际完成事件不得混淆。

主要状态保持原文：CREATED → BINDING → READY → PLAYING/PAUSED/BUFFERING → ENDED；错误分 RECOVERABLE/FATAL；任意非终态可转 RELEASING → RELEASED。图片有 VIEWING 映射与 mediaKind。Seek 活动独立标记；非法状态转移返回错误。重复 release 返回缓存的最终快照，不重新回调宿主业务。

媒体切换先终止旧读取并完成旧资源释放，再绑定新媒体；旧 generation 的异步结果丢弃，但对应资源必须释放。事件带bindingGeneration/timelineEpoch、单调sequence与单调时钟时间；高频 position 可合并，错误、结束、释放等关键事件不可静默丢失。订阅者迟到可查询终态和资源归零记录。

## 5. 状态快照与播放统计

快照包含归一化 zoom/pan、rotation、fitMode、orientation、fullscreen；视频含 position/speed/volume/muted/trackSelection；图片视频字段为空。轨道以技术特征匹配恢复，不能复用不稳定数组下标。恢复失败返回 warning 和合理默认值。

事件提供自然播放有效区间与实际观看累计量，排除 Seek/暂停/缓冲时间；前后台和可见性独立报告。30% 规则和 contentId+scope 去重归宿主；Kit 不存 scope。

## 6. 释放、回调和媒体租约

release 先停止命令接纳，取消读取/跟踪，排空在途回调，解绑 Surface，关闭句柄和解码器；宿主保存失败不得阻止资源清理。释放完成后才发 SourceReleased(sessionId, mediaToken, generation, releaseSequence)。正在编辑的句柄与播放句柄分别释放；宿主需等待同一租约全部消费者归零，不能收到单个会话事件就立即移动文件。

回调在指定执行器调用，有界超时且可取消。宿主 callback 失败映射 HOST_CALLBACK_FAILED，播放可继续；SourceReleased 通知丢失可查询资源报告，不重新打开旧源。回调不得阻塞主线程或持有 Activity 长期强引用。最终数值超时预算在 Spike 与评审后冻结。

## 7. 输出契约

Sink 提供 openTemporary、markReady、abort，与原文一致。补充声明 WriteHandle 的 sequential/randomWrite/seek/flush/close/knownFreeSpace 能力。容器需要回写索引时提前拒绝纯顺序 Sink；不隐式复制到未授权本地路径。

任务状态及验证门遵[输出生命周期协议](OUTPUT_LIFECYCLE_AND_RECOVERY_V1.0.md)：FINALIZING后VALIDATING，验证合格/原验证租约归还才仲裁READY；取消先ABORT_REQUESTED，原资源与清理确认才ABORTED。markReady逻辑同ID返回同token，结果未知只queryOutputStatus，不重复物理调用或并行abort，READY不等COMMITTED。

## 8. C ABI 与安全演进

C ABI 使用 opaque handle、固定宽整数、显式状态码、structSize/apiVersion；不传 C++ STL 或异常。缓冲所有权、retain/release、回调线程和取消令牌写入 header 合约。宿主异步 readAt 在平台层转为 request/completion，不允许 FFI 同步回调等待 UI 线程。序列化工程默认 JSON，时间 int64 微秒、坐标归一化；未来主版本安全拒绝。

Fake 实现正常/短读/断线/取消/超时/释放与输出故障；真实实现同套测试。原文第 19.3 节所有错误码必须覆盖，增补 SOURCE_CHANGED、SCHEMA_UNSUPPORTED 等错误是否需要公开，留待评审；不能直接用第三方异常代替稳定码。

## 9. 当前细化合同

[统一接口与数据契约](API_DATA_CONTRACT_V1.0.md)定义规范命名/错误参数/HostTextRef、幂等接纳与原调用归还；[输出协议](OUTPUT_LIFECYCLE_AND_RECOVERY_V1.0.md)补openValidationLease/reportValidation/queryOutputStatus及恢复；[绑定边界](NATIVE_BINDING_AND_MODULE_BOUNDARIES_V1.0.md)定义平台通道/FFI/原buffer所有权。正式实现前冻结语言签名/版本/数值，当前不增加产品方法、不构建测试。
