# VideoKit 统一接口与数据契约

V1.0；2026-10-21；当前设计基线，非实现/性能/许可验收证明。项目PAUSED_WAITING_USER，D1未过/M0未启；仅文档更新，不派开发、补测、设备或恢复自动跟进。

## 1. 字段标准与兼容映射

| 规范名 | 类型/语义 | 旧名称及迁移 |
| --- | --- | --- |
| sessionId | 不透明会话ID | 不复用为task/source identity |
| bindingGeneration | uint64逻辑计数，媒体重新绑定递增 | 旧generation只在已识别schema适配；不得双写矛盾值 |
| timelineEpoch | uint64，Seek/音轨切换/媒体不连续 | 旧epoch按已识别schema映射；UI语言切换不改变 |
| recognitionConfigRevision | uint64，识别配置版本 | 识别设置里的configRevision映射此字段 |
| translationConfigRevision | uint64，翻译配置版本 | 翻译设置里的configRevision映射此字段 |
| localeGeneration | uint64，界面资源快照版本 | 不参与媒体/模型内容身份 |
| languageTag | 规范BCP47语言标签或null | language/sourceLanguage/targetLanguage由适配器映射到对应Tag字段，unknown不等en |
| requestId/taskId/sequence | ID/ID/单会话有序序号 | 接纳ACK不是操作完成；task结果必须检查媒体和配置版本 |

规范只适用未来公共模型；冻结D1 JSON/header/SDK不做在位迁移。正式首个schema发布前确定wire版本；旧schema已知才翻译别名，未知major拒绝，双名冲突拒绝。计数不接bool/浮点/字符串；C ABI无符号溢出拒绝，JSON/Flutter/JS适配必须无损（必要时wire十进制字符串字段由对应schema明确定义，不混用），时间int64微秒与单调耗时独立。

## 2. 信封与任务接纳

CommandEnvelope={apiVersion,sessionId,bindingGeneration,requestId,command,payload}。EventEnvelope={schemaVersion,sessionId,bindingGeneration,timelineEpoch,sequence,monotonicTimeNs,requestId?,eventType,payload}。RecognitionTask/Segment/结果必含recognitionConfigRevision及上述媒体身份；TranslationRequest/Result必含translationConfigRevision及源cueId/revision。配置没变而旧taskId复用也不能绕过版本核对。

会话每次命令先校验版本/状态再串行接纳，返回commandReceipt(ACCEPTED/REJECTED及原因)，异步Completion单独给原契约EXECUTED/REJECTED/SUPERSEDED/UNSUPPORTED/RELEASED。幂等键=(sessionId,bindingGeneration,requestId)，重复同请求返回缓存或PENDING，不重复执行；同ID不同payload拒绝。关键事件有有界缓存和终态query，缓存驱逐返回GAP+最新快照，不能假装全事件已收到；position可合并，release/error不可静默丢失。

## 3. 错误与宿主文本

StructuredError={code,stage,retryable,suggestedAction,typedArgs,resourceContractVersion,redactedDiagnostic,sessionId?,requestId?,taskId?}。typedArgs值仅登记的string/int64/finiteNumber/bool及格式约束，不放任意对象/地址/凭据；错误code及suggestedAction是稳定机器枚举，不含已翻译长句。typedArgs只给已审安全上下文，路径/字幕正文默认脱敏。App映射资源key，未知code映射genericError，日志保留原code；retryable表示可向负责人/策略建议新请求，不是自动重复未知原调用。

HostTextRef={namespace:HOST/KIT,key,args,contractVersion}。HOST资源由宿主resolver在指定UI执行器提供；Kit只在可选UI适配层请求文本，纯Core不加载宿主资源。HostAction保存actionId/HostTextRef，语言变化由宿主触发textRevision更新，不能重发动作或换媒体；超时/缺key显示安全占位+禁用不明确操作，不回显key/HTML。旧labelKey只在宿主adapter转换，不假设其是Kit内置ARB。宿主原始label动态文本为另一种显式variant，不能两种同时有效。

## 4. 原调用归还与逻辑幂等

OperationReturn={operationId,logicalState:IN_PROGRESS/SUCCEEDED/FAILED/CANCELLED,originalCallState:NOT_STARTED/PENDING/RETURNED/UNKNOWN,bufferState,callbackState,leaseState,firstFailure?,unknownReasons[]}。原state不是另一个业务终态；FAILED可伴UNKNOWN，后续原返只补return证据，不能改成SUCCEEDED。查询无副作用，不读取旧原流冒新观察。

readAt的正长读EOF=-1、零长读0、范围/溢出/短读/异步缓冲持有遵原契约。close/release逻辑幂等仅表示相同操作ID返回已知状态，物理close只发一次；原close PENDING/UNKNOWN不再发第二次，也不能假归零。cancel只设置请求并停止新准入，原缓冲/预算归还要等对应调用/回调真实返回。源工厂用途枚举包含PROBE/PLAYBACK/IMAGE/EDIT/TRACKING/ASR/OUTPUT_VALIDATION，按能力/授权开放，不是每种都必实现；同源所有消费者聚合后才可移动文件。

## 5. 验收与实施门

API-01别名冲突/未来major/无损整数；API-02同ID重复/不同payload；API-03错误参数和HostTextRef回退；API-04状态查询与逻辑幂等/物理只一次；API-05事件GAP/关键终态；API-06扩展版本跨代丢弃与原返。均设计待测，分别纳M0契约、M1/M7真实适配；具体结构大小、callback ABI、缓存数/时限按指标冻结表，禁止永久无界缓存。辅助设计schema见[数据Schema](schemas/design_contracts_v1.schema.json)，仅作字段说明，完整语义以本文与专项模型为准。
