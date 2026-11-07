# 04A 公共 API 对齐裁定（M0-B1）

版本：V1.5（新增 §4A–§4E 补充裁定）；日期：2026-11-07；裁定人：负责人。依据：Coder A 报告 `test-workspace/reports/M0-B1-A/REPORT.md` §6，Coder B 报告 `test-workspace/reports/M0-B1-B/REPORT.md` §6 与附录 A–C。

> 本文件是 [04 公共 API 契约](04_PUBLIC_API_CONTRACT.md) 的补充裁定，与 04 冲突时以本文件为准；API 1.0.0 冻结时并入 04。
> 适用范围：Kotlin `videokit-api` / `videokit-api-android` 与 Dart `videokit_api`。两侧必须按本表一一对应，M0-B2 内完成对齐。

## 1. 对应规则补充（在 04 §12.1 基础上）

1. **Kotlin 名称为准**：同一概念两侧使用同一名称；Dart 只在与 Flutter/Dart SDK 冲突时改名，且改名在本表登记。
2. **嵌套 sealed 子类型**：Kotlin `Parent.Child` 在 Dart 写作 `ParentChild`（例：`EditCommandResult.Applied` ↔ `EditCommandResultApplied`）。为避免冗长，本表登记的少数例外除外。
3. **枚举**：Kotlin `UPPER_SNAKE` ↔ Dart `lowerCamel`，取值集合完全相同；wire 名用 Kotlin 写法。
4. **规则以 `spec/` 为准**：状态机行为以 `spec/vectors/state-machine/*.json` 为准，错误码以 `spec/errors.json` 为准；Kotlin Fake 与 Dart Fake 都必须通过全部向量。两侧 Fake 行为不一致时，以向量为准，向量没覆盖的补向量。

## 2. 命名与类型裁定

| # | 概念 | 裁定（两侧） | 改动方 |
| --- | --- | --- | --- |
| N1 | 会话可见性 | `SessionVisibility { VISIBLE, OFFSCREEN, BACKGROUND }` | Kotlin 改名 |
| N2 | 资源优先级 | `ResourcePriority` | Kotlin 改名 |
| N3 | 内容方向 | `MediaOrientation`，含 `UNKNOWN`（元数据缺失） | Kotlin 改名并加 UNKNOWN |
| N4 | 方向状态 | `OrientationState(request, contentOrientation: MediaOrientation, fullscreen)` | Dart 改字段名 |
| N5 | 锁屏隐藏 | 状态字段 `hiddenForLock` | Dart 改名（原 contentHiddenForLock） |
| N6 | 遮罩区域 | `MaskRegion(x, y, width, height, rotationDeg)`，归一化，左上角 | Dart 改名并加 rotationDeg |
| N7 | 覆盖区间 | `CoverageRange` | Dart 改名 |
| N8 | 媒体探测结果 | `MediaProbeResult` | Dart 改名 |
| N9 | 宿主图标 | `HostIcon.BuiltIn(iconKey)` / `HostIcon.Resource(resourceRef)` ↔ Dart `HostIconBuiltIn` / `HostIconResource` | 两侧（Kotlin `HostDrawable` 改为 `Resource`） |
| N10 | 日志策略 | sealed `LoggingPolicy`：`ReleaseDefault` / `Diagnostics(logger, minLevel)` | Dart 改为 sealed |
| N11 | 画面适配 | `FitMode { FIT, FILL, ORIGINAL }`（设计稿：适应 / 填充 / 原尺寸），去掉 STRETCH | Kotlin |
| N12 | 编辑结果 | `EditCommandResult.Applied(revision, createdId?) / Rejected / Unsupported / ProjectReleased` ↔ Dart `EditApplied` 等（登记的例外，保留 Dart 现名） | Kotlin 加 `createdId` |

## 3. 取值集合裁定

| # | 类型 | 取值（两侧完全一致） |
| --- | --- | --- |
| V1 | `UnsupportedReason` | NOT_IMPLEMENTED、DEVICE_CAPABILITY、FORMAT、MEDIA_KIND、SOURCE_SEQUENTIAL_ONLY、HOST_DISABLED、MODULE_NOT_INSTALLED、VALUE_OUT_OF_RANGE、TRACK_NOT_FOUND、CONTENT_LOCKED、UNKNOWN |
| V2 | `SuggestedAction` | NONE、RETRY、CHOOSE_OTHER_TRACK、REDUCE_QUALITY、FREE_SPACE、CHECK_PERMISSION、RECONNECT_SOURCE、CLOSE_OTHER_SESSIONS、CORRECT_TRACKING、CHOOSE_OTHER_SOURCE |
| V3 | `HostActionStatus` | COMPLETED、PENDING、FAILED、CANCELLED；`HostActionResult(status, updatedAction?, messageKey?)` |
| V4 | `NavigationResult` | ACCEPTED、UNAVAILABLE、FAILED（宿主回调失败或超时） |
| V5 | `RecoveryDecision` | RETRY、KEEP_ERROR、RELEASE |
| V6 | `ErrorStage` | 04 §9.1 的值 + `UNKNOWN`（未知阶段回退） |
| V7 | `ErrorCode` 新增 | `INVALID_STATE`（非法状态转换）、`INVALID_ARGUMENT`（参数越界/非法）、`UNSUPPORTED_SNAPSHOT_VERSION`（快照或工程 schema 不支持）；API 1.0.0 冻结前加入，`spec/errors.json` 同步为 25 个码；原来用 `INTERNAL_ERROR_REDACTED + diagnostic` 表达的情况改用新码 |

## 4. 接口与字段裁定

| # | 项 | 裁定 |
| --- | --- | --- |
| I1 | UI 触发宿主动作 | 会话方法 `requestHostAction(actionId): VideoKitCommandResult`（不作为播放命令）；pending 期间的重复请求返回 `Superseded`，且不再调用宿主。Dart 删除 `InvokeHostAction` 命令 |
| I2 | 导航请求 | 会话方法 `requestNavigation(direction): NavigationResult` |
| I3 | 控件可见性写回 | 会话方法 `setControlsVisible(visible)`（Dart 原 `reportControlsVisible` 改名） |
| I4 | 错误参数 | `VideoKitStableError.params: Map<String, String>`（默认空；key 为英文 lowerCamelCase，value 用 Locale.ROOT 格式化）；Dart 增加同名字段，UI 文案用 ICU 占位符读取 |
| I5 | 导出结果 | sealed：`VideoKitExportResult.Succeeded(media: VideoKitExportedMedia)` / `Failed(error, stage?)` / `Cancelled(partialOutputRemoved)` ↔ Dart `ExportSucceeded` 等；`export()` 正常失败与取消不抛异常 |
| I6 | 演示标识 | `VideoKit.isDemo`、`VideoKitSession.isDemo`、`VideoKitCapabilities.isDemo`、`VideoKitExportedMedia.isDemo` 两侧都有 |
| I7 | 宿主回调签名 | 播放快照 `VideoKitPlaybackState` 自带 `sessionId`、`mediaToken`；`onRecoverableError(sessionId, error)`、`onFatalSessionError(sessionId, error)` 增加 `sessionId` |
| I8 | 回调超时 | `VideoKitConfig.callbackTimeouts`：hostAction 10 s、navigation 3 s、recoveryDecision 3 s、notification 2 s（两侧一致；14 §12 同步） |
| I9 | 字幕开关 | 快照增加 `subtitlesEnabled: Boolean`，与 `selectedSubtitleTrackId` 一起区分“关闭”与“未选择” |
| I10 | 候选检测 | 编辑工程增加 `detectCandidates(atUs): CandidateDetectionResult`（两侧） |
| I11 | 编辑命令 | 两侧都有 `AcceptTrackingRange`（09 §4）；不设 `ReorderSources`（`MoveClip` 已覆盖排序）；分割统一为 `SplitAt` |
| I12 | 导出后再编辑 | COMPLETED / FAILED / CANCELLED 后的编辑命令使工程回到 READY（两侧已一致，写入向量） |
| I13 | 渲染目标不支持 | `attachSurface(target)` 改为返回 `VideoKitCommandResult`，不认识的目标类型返回 `Unsupported(DEVICE_CAPABILITY)`；Dart 侧不暴露 Surface，不涉及 |
| I14 | 写句柄 | 公共层 `VideoKitWriteHandle` 不含 FD；Android 提供 `FileDescriptorWriteHandle`（api-android） |
| I15 | 媒体源（Dart） | Dart 用 `sourceRef: VideoKitSourceRef`（sealed：Uri / Registered / Demo / Dart）描述源，原生侧打开；这是 04 §12.3 规定的语言差异，保留 |
| I16 | Sink（Dart） | Dart 的 `VideoKitOutputSink` 是原生 Sink 引用 + 能力描述，不含写方法；保留 |
| I17 | 异步差异（Dart） | `createSession`、`createEditProject`、`previewSession` 在 Dart 返回 `Future`；保留 |
| I18 | 会话上限 | `createSession` 超过上限抛 `VideoKitException(DECODER_RESOURCE_EXHAUSTED)`（两侧一致） |
| I19 | 宿主覆盖低对比度颜色 | 宿主显式给出的 on 色 / content 色低于 4.5:1 时替换为黑或白并记录诊断（Dart 现行为，确认保留） |

## 4A. 补充裁定（V1.1，2026-11-07，M0-B2 进行中由 Coder B 提出）

| # | 项 | 裁定 | 改动方 |
| --- | --- | --- | --- |
| S1 | 宿主动作状态 | `HostActionState(action, pending: Boolean, lastStatus: HostActionStatus?)` | Dart（原 inFlight） |
| S2 | 导出预检 | `ExportPrecheck(problems: List<…>, warnings: List<…>)`；有 problem 时不能开始导出 | Dart（原 issues） |
| S3 | 导出阶段 | `ExportStage { PREPARING, TRACKING, ENCODING, VERIFYING, WRITING }`（14 §5.8）；完成由 `EditPhase.COMPLETED` 表达，不设 WRITING_COMPLETE | Kotlin 改名 |
| S4 | 开始跟踪 | `StartTracking(maskId, kind: TrackingKind { FACE, OBJECT }, seedRegion: MaskRegion?, targetId?)`（14 §5.7 物体点选/框选需要 seedRegion） | Kotlin 补字段 |
| S5 | 播放事件字段 | 两侧取并集：`PlayStateChanged`、`BufferingEnded` 等事件字段以 Kotlin 为基础，Dart 补齐缺少的字段 | Dart |
| S6 | 能力模型取值 | `FeatureKey`、`ModuleState` 以 Kotlin 取值为准 | Dart |
| S7 | 纹理申请 | Dart `VideoKitSession` 增加 `VideoKitTextureLease acquireTexture()`：返回租约（`ValueListenable<int?> textureId` + `release()`）。插件适配层按引用计数管理，最后一个租约释放后延迟 2 s 销毁（14 §8.5）；Fake 的 textureId 恒为 null。UI 的 `VkMediaSurface` 显示时申请、卸载时释放。Kotlin 公共 API 不涉及 | Dart 接口（Coder A）+ 插件实现（Coder B） |
| S8 | 示例 App 接入插件 | `videokit_example/android/settings.gradle.kts` 增加 `includeBuild("../../..")` 替换 `com.videokit:*` 依赖；本批由 Coder B 修改这一个文件 | Coder B |

## 4B. 补充裁定（V1.2，2026-11-07，M0-B2 审查）

| # | 项 | 裁定 | 改动方 |
| --- | --- | --- | --- |
| T1 | 命令与结果类命名 | Dart 保留 14 §3.2 的扁平名称（`Play`、`SeekTo`、`Executed` 等），作为 §1 第 2 条的登记例外，不改为 ParentChild 形式 | 无 |
| T2 | `ExportPrecheck.uncoveredRanges` | 两侧都有（覆盖检查页 UI-07/08 需要）：`uncoveredRanges: List<CoverageRange>` | Kotlin 补字段 |
| T3 | `FeatureKey` 未知值 | Dart 的 `unknown` 作为解码兜底保留；Kotlin 解码未知值同样回退到 `UNKNOWN`（新增该值） | Kotlin |
| T4 | 宿主图标资源 | `HostIcon.Resource(resourceRef: String)`：平台无关的资源名（Android 为 `drawable` 资源名，由 api-android 解析为资源 ID）；不在公共层使用 Int 资源 ID | Kotlin 若仍为 Int 则改为 String |

## 4C. 补充裁定（V1.3，2026-11-07，M0-B3 由 Coder A 提出）

| # | 项 | 裁定 | 改动方 |
| --- | --- | --- | --- |
| L1 | 循环播放 | 新增命令 `SetLooping(looping: Boolean)`，`VideoKitSessionState` 增加 `looping`。默认值按媒体类型：动态图 `true`，视频 `false`。`looping=false` 时播放到末尾停在末帧（视频为最后一帧、动图为最后一帧），进入 ENDED 并发出 `PlaybackEnded`；`looping=true` 时不发 `PlaybackEnded`。静态图收到该命令返回 `Unsupported(MEDIA_KIND)` | 两侧 + spec 向量（Coder B） |
| L3 | 循环写入快照（V1.4 补充，M1-B1 提出） | 两侧 `VideoKitPlaybackState` 增加 `looping: Boolean?`：null 表示按媒体类型的默认值；bind 时 `initialState.looping` 非 null 则覆盖默认值。宿主按 05 §3 保存偏好时一并保存 | 两侧 + 通道 |
| L2 | 图片详情 | `VideoKitSessionState` 增加可空字段 `imageDetails: ImageDetails?`，`ImageDetails(frameCount: Int?, decodedBytes: Long?, sampleSize: Int?)`；原生侧能提供就填，拿不到为 null，UI 只显示有值的项。视频会话恒为 null | 两侧 |

## 4D. 补充裁定（V1.4，2026-11-07，M0-B5 App 外壳提出）

| # | 项 | 裁定 | 改动方 |
| --- | --- | --- | --- |
| P1 | 缩略图 | 会话新增 `captureThumbnail(atUs: Long, maxWidth: Int, maxHeight: Int): ThumbnailResult`（成功时为 JPEG 字节 + 实际尺寸；视频取最近帧，图片取缩放图；失败返回稳定错误）。经 SPI `FrameSource` / `ImageEngine` 实现；Fake 返回演示图 | 两侧（Kotlin 实现在 M1） |
| P2 | 媒体参数 | `VideoKitSessionState.mediaInfo: MediaInfo?`：`container`、`videoCodec`、`audioCodec`、`width`、`height`、`frameRate`、`bitrateBps`、`rotationDeg`、`durationUs`、`fileSizeBytes`（均可空，拿不到为 null）；bind 完成后填充 | 两侧 |
| P3 | 演示入口 | App 用独立入口文件 `lib/main_demo.dart`（只在 debug/开发使用，`flutter run -t lib/main_demo.dart`），`lib/main.dart` 不得 import `videokit_fake`；不使用 flavor。Release 隔离检查（14 §11.4）验证 `main.dart` 产物不含 Fake | App |
| P4 | applicationId | VideoKit App 暂定 `com.videokit.app`；对外发布前核对域名与商标权利（02 §7 #1） | App |

## 4E. 补充裁定（V1.5，2026-11-07，M1-A1 / TEST-R1 / M2-B1 提出）

| # | 项 | 裁定 | 改动方 |
| --- | --- | --- | --- |
| C1 | 音轨声道数 | `TrackInfo` 增加可空字段 `channelCount: Int?`（仅音轨有意义，拿不到为 null）。UI 显示“编码 + 声道布局”（1→单声道、2→2.0、6→5.1、8→7.1，其他显示“N 声道”），为 null 时只显示编码名。spec 与通道同批修改 | Kotlin + spec + 通道 + Media3 填充（Coder B）；Dart API + Fake + UI（Coder A） |
| I1 | 图片编码数据读取（M2-B1） | 宿主只提供 `readAt`，且不写临时文件，因此编码数据整读进内存，上限 96 MiB，不计入图片额度；超过上限返回稳定错误。“大图分块”指解码分块（BitmapRegionDecoder），不是读取分块。真正按块读取需要宿主提供文件描述符，属于 API 变更，等真机数据后再定 | Kotlin（Coder B） |
| I2 | ImageEngine SPI | 采用 M2-B1 改写版：规则（尺寸、分块、额度）在平台无关层；图片由 `PlaybackSession` 内的 `ImageController` 承载，共用状态机、宿主交互与释放顺序（videokit-playback 依赖 videokit-image） | Kotlin |
| I3 | 放大清晰度 | M2 以纹理最长边 4096 为上限，缩放由 Flutter 对纹理变换（06 §5）。更高倍数的清晰度改为原生按视口渲染，等 S 项与真机测试后再定 | — |
| I4 | 图片额度初值 | 每宿主 192 MiB、单会话 ≤ 64 MiB、分块余量 16 MiB、底图最长边 ≤ 2048；真机验证后调整（PENDING 22）。额度不足时降采样，并发轻提示 `IMAGE_MEMORY_REDUCED_QUALITY`（UI 需补中文文案） | Kotlin；文案 Coder A |
| I5 | EXIF | 使用平台 `android.media.ExifInterface`（minSdk 31 已含修复），不加 androidx 依赖；lint 文件级抑制 | Kotlin |
| U2 | U1 补充（M2-A1） | 图片查看器在图片集中浏览时，不支持页额外保留“上一张/下一张”（否则无法离开该页）。点按切换控件显隐不受播放状态限制：“未播放”只停止自动隐藏，不阻止手动隐藏（视频暂停时也可点按隐藏）。标签类宿主动作在打开编辑框时即完成，角标在编辑框关闭后更新，不延长 10 s 超时 | Flutter UI / App（Coder A） |
| V1 | 可见性取值（M3-A1） | `SessionVisibility` 增加 `PARTIALLY_VISIBLE`（07 §3：可降低帧率或分辨率），两侧 + spec 同批修改。07 的 LOCKED 不进入可见性枚举，锁定继续用已有的内容锁定命令（06 §4.2），锁定优先于可见性 | Kotlin + spec + 通道（Coder B）；Dart + Fake + 上报（Coder A） |
| V2 | 路由遮挡 | 只有不透明路由完全遮挡时，下面的格子才报 `OFFSCREEN`；半透明对话框、底部面板不改变可见性 | Flutter（Coder A） |
| K1 | 轻提示码登记 | 新增 `spec/notices.json` 统一登记所有 `TransientNotice` 码，一律大写下划线（如 `SEEK_CLAMPED`），Kit 与 Dart 两侧测试对照该文件（与 errors.json 同样做法）。Kit 发出 `AUDIO_FOCUS_LOST`（系统音频焦点被抢占）与 `RESOURCE_DEGRADED`（资源不足降级）；Dart 原有小写码改为大写 | 登记与 Kit（Coder B）；Dart（Coder A） |
| K2 | AUDIO_FOCUS_LOST 语义（M4-A1） | 按 Android 惯例：系统音频焦点被长期抢占时暂停播放（不是静音），发 `AUDIO_FOCUS_LOST`；短暂抢占按平台默认处理，不发提示。UI 文案为“其他应用正在播放，已暂停” | Kit（Coder B）；Fake 与文案（Coder A） |
| K3 | 导出警告码 | `ExportWarnings` 与提示码同样一律大写下划线（如 `FAST_CONCAT_REJECTED`），登记在 `spec/notices.json` 的独立分组 `exportWarnings` 中，两侧对照测试 | 登记与 Kit（Coder B）；Dart（Coder A） |
| E1 | 拼接方式字段（计划） | S3 完成后，`ExportPrecheck` 增加 `concatPath`（FAST / TRANSCODE）与 `concatReasons` 列表，由 Kit 决定；在那之前 UI 自行计算并用导出检查警告修正。随 M4 原生拼接引擎同批实现 | 两侧（M4 原生批次） |
| U3 | 视频左右滑动（M4-A1） | 保留视频画面左右滑动 seek（相对拖动，常见做法）；进度条所在条带始终归进度条（控件隐藏时也接收拖动，按绝对位置跳转并显示控件）。图片左右滑动用于翻页（设计稿第 11 页） | Flutter UI（Coder A） |
| U1 | 错误态下的底部控件 | 不支持（`UNSUPPORTED_*`）或致命错误：按设计稿第 12 页只保留返回和标题，底部控件隐藏；可恢复错误（带“重试”）：控件保留为禁用外观，点击放行给状态视图 | Flutter UI（Coder A） |

## 5. 工程与构建裁定

| # | 项 | 裁定 |
| --- | --- | --- |
| B1 | KMP 只启用 `jvm()` 拦不住 `java.*` | 采纳实测结论。V1.0 以源码检查 `checkCommonPortability`（挂在 `check` 上）作为门禁；开始 Apple 平台工作时启用 `iosArm64()` 等非 JVM 目标，由编译器检查。02 §4.0 与 13 §3.2 已按此修正 |
| B2 | kotlinx-serialization | M0 不引入，testkit 内部 `MiniJson` 只用于测试与向量；VK-M4 做工程 Schema 时引入 |
| B3 | JUnit 4（EPL-1.0） | 只用于测试、不随产品分发，允许；记入 10 |
| B4 | 关闭 AGP 9 内置 Kotlin | 暂时接受（BCV 需要独立 kotlin-android 插件）；AGP 10 之前迁移，列为风险 |
| B5 | verification-metadata 只有 Windows 的 aapt2 | 建 CI 时补 Linux 条目 |
| B6 | Flutter Android 模板要求 Java/Kotlin 17 | 示例 App 与插件平台包可用 17；Kit 模块保持 11 |
| B7 | Dart `copyWith` 哨兵参数（`Object?`） | 暂时接受；若评审中发现类型错误频发，再改 |
| B8 | 文件大小进制 | 改为 1000 进制（与 Android 系统 `Formatter` 一致） |
| B9 | Dart 契约入口签名 | `runVideoKitContractTests(VideoKit Function(VideoKitConfig), {fixtures, elapse})`，Kotlin Fake 支持 `demo:<scenarioId>` 引用；14 §11.1 同步 |
| B10 | 本批补充的主题键 | `apps.videokit.color.demo.content`、`color.elevation.floating/modal`、`dimension.border.width`、`dimension.focusring.width`、`dimension.elevation.*` 接受，并入 14 §7.2 |
| B11 | `.gitignore` | 增加 `.claude/` 与 `**/GeneratedPluginRegistrant.java` |
