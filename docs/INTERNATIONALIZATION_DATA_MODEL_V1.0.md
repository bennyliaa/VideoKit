# VideoKit 国际化数据模型

V1.0；2026-10-21；设计字段基线，非已冻结ABI/实现。主设计：[国际化详细设计](INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)。本模型与[播放数据模型](PLAYBACK_DATA_MODEL_V1.0.md)互补，四域语言独立。当前PAUSED_WAITING_USER；D1未过M0未启。

## 1. 类型与所有权

LanguageTag为规范BCP47风格language/script/region（可选其他标准子标签）；先结构校验/规范化，再按能力匹配。Flutter Locale适配与持久tag分离。AUTO/SYSTEM/OFF是策略枚举，不得存作语言tag。und/未知媒体语言不等于en。模型language code如zh/en由adapter显式映射，不能假定接受任意BCP47脚本区域。

| 对象 | 字段及约束 | 所有者 |
| --- | --- | --- |
| LanguageSettings | schemaVersion,revision,ui,subtitleDefaults,recognitionDefaults,translationDefaults | App Repository；四域独立校验/原子写 |
| UiLocalePreference | mode:SYSTEM/EXPLICIT,requestedTag?；EXPLICIT必填，SYSTEM不携有效显式tag | App全局偏好；不进Kit播放命令 |
| UiLocaleSnapshot | requestedMode,requestedTag?,systemTags[],effectiveTag,matchReason,direction,localeGeneration,persistenceStatus | LocaleController只读快照；effective限支持资源 |
| LocaleResourceManifest | resourceVersion,defaultTag=en,supportedTags=[en,zh-Hans],template,keyCoverage,buildOnlyLocales | App发布资源；buildOnly不得出现在正式选择器 |
| LocalizedMessageRef | code,typedArgs,resourceContractVersion | Kit给稳定code/args，App映射key；不存翻译句 |
| SubtitleLanguagePreference | mode:OFF/AUTO/TRACK,trackId?,preferredLanguageTags[],secondarySelection? | App默认及session覆盖；实际TrackDescriptor由Kit维护 |
| RecognitionLanguagePreference | enabled=false,mode:AUTO/EXPLICIT,requestedTag?,modelId?,configRevision | 扩展用户意图；显式tag必须结构合法 |
| TranslationLanguagePreference | enabled=false,sourceMode:FROM_TRACK_OR_DETECT/EXPLICIT,sourceTag?,targetTag?,providerRef=LOCAL,configRevision | 开启要求有效目标/能力；不内嵌在线密钥 |
| EffectiveLanguageState | domain,requested?,effective?,status:DISABLED/AVAILABLE/UNAVAILABLE/NEEDS_CONFIGURATION,reason,capabilityVersion | 相应能力协调器，不由UiLocale推导 |
| SessionLanguageOverrides | sessionId,bindingGeneration,subtitle?,recognition?,translation? | 内存覆盖；unset继承全局，不隐式保存另一媒体 |
| LanguagePreferenceWriteResult | requestId,revision,status:PERSISTED/FAILED,persistedRevision?,errorCode? | Repo回执；不能把临时显示成功冒持久保存 |

ui localeGeneration是显示快照版本，recognition/translation configRevision分别控制其任务失效，均不改变播放器bindingGeneration/timelineEpoch。真正媒体Seek/换轨沿播放模型推进epoch；任务结果接纳同时检查媒体generation/epoch和所属扩展configRevision。多个revision不能混用或只看taskId。

## 2. 配置示意（非运行产物）

```json
{
  "schemaVersion": 1,
  "revision": 1,
  "ui": {"mode": "SYSTEM", "requestedTag": null},
  "subtitleDefaults": {"mode": "AUTO", "trackId": null, "preferredLanguageTags": [], "secondarySelection": null},
  "recognitionDefaults": {"enabled": false, "mode": "AUTO", "requestedTag": null, "modelId": null, "configRevision": 0},
  "translationDefaults": {"enabled": false, "sourceMode": "FROM_TRACK_OR_DETECT", "sourceTag": null, "targetTag": null, "providerRef": "LOCAL", "configRevision": 0}
}
```

schema实例只是建议形状，正式签名/存储实现实施前冻结。sourceMode=EXPLICIT需sourceTag；启用translation还需targetTag及Provider/模型支持，不支持时EffectiveLanguageState明确不可用，不假设置成功产生内容。requested未知或能力失效可保留用户意图，effective只表示实际可用；UI默认回退en不回写requested。

## 3. 归一、迁移与存储

按域分别校验枚举/类型/互斥/tag/数值，revision为非负整数不接受bool/string。切换UI只更新ui和revision，不重写字幕/ASR/翻译；导出工程不保存App locale作视频语言。偏好文件小型本地原子写，最新revision写后才PERSISTED；串行合并防旧写覆盖。敏感字幕文本/凭据不入设置或日志。

从未有设置按示意默认；旧字段可知版本迁移到四域，不能把历史单locale复制到所有语言域。未知major保留原数据不覆盖，读取安全默认并发warning。单域坏值只回退其域，其他有效域保留；整体不可解析则SYSTEM及各安全关闭默认，不清媒体工程。持久化失败当前会话可临时应用，快照status=FAILED并提示，不声称已保存。

## 4. 事件、资源与测试关联

UiLocaleChanged包含localeGeneration/effectiveTag/direction/原因与持久化状态，不携PlaybackCommand，不改原时间线。错误消息稳定code/类型参数持久可查询，每次UI渲染映射当前资源；显示语言名与原BCP47 tag分离。未知key走已定义genericError，发布构建key缺失应被资源门阻断，不静默绕过。

I18N-01/02核resolver真值，03/04核localeGeneration与系统/手动，05核原子迁移和写失败，06/07核四域隔离及扩展revision，08/09核资源/错误映射，10–15核格式/方向/平台/发布资源。全部当前PLANNED_NOT_RUN，禁止以数据设计完成冒资源或产品国际化验收。

## 5. 与统一契约衔接

识别/翻译设置域内configRevision在任务wire分别映射recognitionConfigRevision/translationConfigRevision，不得结果遗漏。LanguageTag按[统一契约](API_DATA_CONTRACT_V1.0.md)统一字段languageTag/sourceLanguageTag/targetLanguageTag；session覆盖以bindingGeneration归属。HostTextRef采用宿主/Kit资源命名空间，UI语言切换只刷新宿主文本revision，不重发HostAction。
