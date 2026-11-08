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
| B1 | 打开成功的判定（M3-B2，R2-03） | bind 在媒体解析完成、轨道已知时即算打开成功（不等缓冲到可播放），之后继续缓冲时报告 `BUFFERING`；10 s 打开超时只覆盖“解析到轨道已知”这一段。打开中途被 release 得到 `SessionReleased`；超时得到 `Rejected(SOURCE_TIMEOUT)`，会话进入 `ERROR_RECOVERABLE`。UI：打开成功后在 `BUFFERING` 时显示加载圈，不再显示“正在打开” | Kotlin（Coder B）；UI（Coder A） |
| A1 | 发声默认值（TEST-R3 R3-01） | 两侧 `activeAudio` 默认值统一为 `false`：会话 bind 后默认不发声，由宿主经 `SetActiveAudio(true, epoch)` 授予（07 §4）。单播放器宿主（VideoKitPlayer、App 播放页）在 bind 成功后自动授予；多画面由协调器授予 | Kotlin 默认值与向量（Coder B）；宿主侧授予（Coder A） |
| P5 | 缩略图的可取消性（S1 结论） | `captureThumbnail` 与拖动预览帧必须有硬超时并可取消：取帧在专用工作线程执行，并持有自己的宿主读取句柄；取消或超时时关闭该句柄，使阻塞的读取返回错误，然后丢弃该线程的结果，绝不阻塞会话和主线程。默认硬超时 3 s（14 §12 回调超时同级）。对宿主标记为慢速或网络的源，拖动预览帧默认关闭，只显示时间气泡；单张缩略图仍可取，但遵守硬超时。MediaMetadataRetriever 与 Media3 帧提取的取舍在真机对比后定（PENDING 41） | Kotlin（Coder B，M4 之前的 Kit 批次） |
| P6 | 慢速源标记（P5 配套，M3-B4） | `VideoKitMediaSource` 末尾增加 `latencyHint: SourceLatency = LOCAL`，枚举 `SourceLatency { LOCAL, SLOW }`（用枚举便于以后扩展）。宿主对网络或远程源（如 LocalVideoBrowser 的 SMB）传 `SLOW`；`SLOW` 时拖动预览帧默认关闭，只显示时间气泡。VideoKit App 只打开本机 content URI，传 `LOCAL`。两侧 API、Pigeon、spec 同批修改 | Kotlin + 通道（Coder B）；Dart API + UI（Coder A） |
| E2 | 工程 snapshot Schema v1 冻结（M4-A2 / M4-B1） | 唯一来源为 `spec/schema/edit-project.v1.json`（Coder B 在 M4-B1 建立），两侧 codec 都对照它测试。① 顶层按 08 §2.1：`schemaVersion`、`createdAt`/`updatedAt`（epoch 毫秒）、`exportPresetId`（可空）。② 已接受区间属于遮罩：`mask.acceptedRanges: [{startUs, endUs}]`。③ 跟踪条目只持久化 `{maskId, status, coverage: [{startUs, endUs, quality}]}`；`requestId`、`projectRevision`、`kind`、`progress` 是运行时状态，不写入 snapshot。④ 区间一律写成对象 `{startUs, endUs}`，不用数组。⑤ 关键帧 `state` 与 coverage `quality` 共用同一枚举（取值以 09 的跟踪质量定义为准，spec 中列出）。⑥ 版本：本次即为冻结的 v1（此前没有对外发布的数据）；缺失的可选字段按默认值读入；minor 更高可读，major 更高拒绝。迁移框架保留，用合成的旧数据做测试。⑦ 撤销栈上限冻结为 100（08 §2.2）。⑧ 向量文件为 `spec/vectors/state-machine/edit-project.json`，补 roundtrip、缺省字段、future_major 拒绝、minor 兼容等用例 | Schema 与向量、Kotlin（Coder B）；Dart codec 与 Fake（Coder A） |
| E4 | Dart 编辑模型与 Kotlin 对齐（M4-A2） | ① Dart 增加 `TimeRangeUs`（与 Kotlin 同名同义）与 `MaskTrack.acceptedRanges`（默认空，增量）；`CoverageRange.accepted` 保留为由遮罩区间推导的只读便利属性，不写入 snapshot。② `EditSource.probe` 改为可空（未探测为 null）。③ `SourceProbe.videoCodec` 改为可空。②③ 属于 Dart API 不兼容变更：模块尚无外部消费方（LocalVideoBrowser 未接入），按“两侧语义一致”原则允许，在变更记录中注明；UI 中所有读取点同步处理 null（例如导出路径判定为 `PROBE_INCOMPLETE`，信息面板不显示该项） | Dart API、Fake、UI（Coder A） |
| E5 | 头像替换 API 草案裁定（M5A-A1 API_DRAFT §6） | ① 头像 PNG 由宿主保存，工程只记 `avatarToken`（与 mediaToken 同理，模块不保存用户照片）；VideoKit App 作为宿主存于 App 私有目录。② `refineAvatar`（擦除/恢复）放在 Kit，两侧行为一致、便于多平台复用。③ 随头部转动：跟踪关键帧增加可选 `rollDeg`（由人脸关键点双眼连线得出，手动关键帧可设），属 schema minor 增加，随 VK-M5/M5A 实现。④ `scale`/`offset` v1 为整条遮罩一个值，不随关键帧变化（以后需要再按 minor 扩展）。⑤ 内置头像资源由 Kit 提供，token 为 `builtin:N`，UI 经 Kit 取缩略图显示，导出时 Kit 直接取像素。⑥ 新增错误码 `AVATAR_NO_FACE`、`AVATAR_IMAGE_UNSUPPORTED`（errors.json 由 Coder B 登记）。草案其余部分（prepareAvatar/AvatarImage/SetMaskAvatar/IMAGE 样式与 schemaMinor→1）同意，随 VK-M5A 冻结 | 两侧（VK-M5A） |
| E6 | 头像替换作为 Kit 对外能力（用户 2026-11-08 确认） | 头像替换属于对视频的操作，归 Kit 层，作为公共 API 提供给所有宿主（VideoKit App、LocalVideoBrowser 等），两侧（Kotlin / Dart）对等：① **导入图片**：`prepareAvatar(source: VideoKitMediaSource, options)`——图片沿用宿主媒体源（`mediaToken` + `readAt`，与视频相同，Kit 不直接访问文件路径），返回 `AvatarImage`（透明 PNG 字节、头部框、原图人脸框、warnings）；`refineAvatar(avatar, strokes)` 擦除/恢复。② **宿主保存**：宿主保存 PNG 并分配 `avatarToken`；Kit 在预览/导出时通过宿主回调 `openAvatar(avatarToken)` 读取（返回可读源，失败时该区间回退为马赛克并警告）。③ **应用到视频**：`SetMaskAvatar(maskId, avatarToken, scale, offset, followRotation)` + 样式 `IMAGE`；内置头像 `builtin:N` 不需要宿主回调。④ **能力探测**：`Capabilities.avatar`（可用 / 模型缺失 / 设备不支持），宿主据此显示或隐藏入口。⑤ **界面分工（用户 2026-11-08 修订）**：选择头像、调整头像（设计稿第 25 页前两图）属于各 App 业务层，由宿主自行实现，用什么图片完全由宿主决定；Kit 只负责“给定图片 → 贴到视频中选定人物的头部”。Kit 编辑器（`videokit_ui`）只含打码面板中的“头像”样式与参数（大小、随头部转动、跟踪覆盖），点“更换头像”时经宿主回调 `requestAvatar()` 让宿主打开自己的页面并返回 `avatarToken`（未实现回调则入口隐藏）。`prepareAvatar`/`refineAvatar` 作为可选工具 API 保留，宿主可用来抠图，也可完全不调用、直接提供自己处理好的透明 PNG（用户 2026-11-08 确认）。宿主自备的 PNG：头部范围取不透明像素的外接框（可另传 `headBox` 覆盖），透明度按原样使用；Kit 只做尺寸上限与格式校验（失败报 `AVATAR_IMAGE_UNSUPPORTED`）。全部本机处理，不上传 | 两侧（VK-M5A）；宿主接入说明写入 05 |
| X1 | 导出 UI 与故障（M6-A1 PLAN §1） | ① `ExportStage` 保持 5 个（PREPARING / TRACKING / ENCODING / VERIFYING / WRITING），UI 把 ENCODING 显示为“处理（解码 · 合成 · 编码）”。② 取消沿用 CANCELLING → CANCELLED(partialOutputRemoved)；超过 5 s 显示“清理时间较长…”。③ worker 故障用 `EXPORT_FAILED` + `params.reason`（`WORKER_KILLED` / `WORKER_CRASHED` / `WORKER_TIMEOUT`），不新增错误码；errors.json 在 params 说明中登记这三个值。④ 只信任 `export()` 返回的成功结果，进度到 100% 不算成功（15 §2.8 约束 4）。⑤ App 被杀后的恢复：App 自己记录进行中的导出，下次启动提示并清理（App 业务）。⑥ 顺序写 Sink 需本机暂存，暂存空间计入 `requiredBytes`，预检显示“写入方式”。⑦ 开源许可：Kit 在 `videokit_flutter` 中附带 NOTICE 资源并通过 Flutter `LicenseRegistry` 注册，App 的“关于”页直接用系统许可页显示，无需读取 AAR 内文件 | 两侧（⑦、③ 登记由 Coder B）；UI 与 App（Coder A） |
| E7 | 头像替换细则（TEST-PLAN-6 §4） | Q1 目标 LOST/AMBIGUOUS/未分析区间：预览中不显示头像，在最后可信位置显示虚线框与“目标丢失”标签，绝不贴到他人头上；导出前检查与打码规则相同。Q2 `rollDeg` 为 null 的关键帧：取相邻有值关键帧线性插值，两侧都无值时为 0；v1 不提供手动设转角的界面。Q3 旧读取端：内部旧版本降级为马赛克可接受；新增 schema 规则 R8——读取端的 schemaMinor 低于工程的 schemaMinor 时，不得覆盖原工程，只能另存为副本并提示（自 1.1 起的实现必须遵守）。Q4 App 头像库淘汰：被任一工程引用的头像不淘汰；全部被引用时提示用户清理，不自动删除。Q5 黄金图像容差冻结：位置 ≤ 2 px、大小 ≤ 2%、转角 ≤ 1°。Q6 多人指标：错挂硬性为 0，其余指标在 09 §5 阈值冻结前只记录不判定。Q7 切换样式时头像设置保留，只在用户明确清除时删除。Q8 镜头切换后目标再出现，单列为“切镜再出现”统计，与“出画再入画”分开。Q9 导出前检查选“全画面打码”的区间：该区间全画面马赛克、不显示头像，其他区间头像不变 | 两侧 + App（VK-M5A）；R8 写入 schema（Coder B） |
| E3 | SourceProbe 补充（M4-B1 §9，计划） | `SourceProbe` 增加 `container`、视频 `profile`、音频 `sampleRateHz`、`channelCount`（均可空），作为快速拼接判定的输入（08 §3）。两侧 API 与 spec 同批修改，随 M4 拼接引擎批次实现；在那之前 ConcatRules 遇到缺失字段一律判 TRANSCODE 并给出原因 `PROBE_INCOMPLETE` | 两侧（M4 引擎批次） |
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
