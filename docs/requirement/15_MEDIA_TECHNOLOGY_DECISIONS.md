# 15 媒体技术路线决定

版本：V1.0；日期：2026-11-06；状态：**现行技术路线**（用户 2026-11-06 同意按本文推进）。对应原需求 §5、§6、§7、§10、§11、§14、§16、§21、§23、§29。

> 本文件对播放、解码、图片、剪辑、拼接、视频合成（打码效果）、导出封装、渲染、隔离和跟踪逐项给出技术方案决定，后续开发和里程碑按本文执行。
> 每项决定标为 **已定**（直接按此开发）或 **待验证**（方向已定，由第 4 节的聚焦验证给出结论；结论只能在本文列出的备选方案中选择，或提出变更评审）。
> 与 [02](02_SYSTEM_ARCHITECTURE.md) §3、§7 不一致时以本文为准，02 按本文回改。

## 1. 总体原则

1. **平台能力优先**：解码、编码用 Android 系统编解码器（MediaCodec，经 Media3 调用）；不自带软件编解码器。理由：硬件加速、功耗低、编解码专利由设备厂商覆盖、包体积小、安全更新随系统。
2. **一套媒体框架**：播放、抽帧、剪辑、合成、导出统一用 AndroidX Media3（Apache-2.0）。预览和导出使用同一套效果实现，保证所见即所得。
3. **缺口如实报告，不静默降级**：平台和 Media3 不支持的格式由能力报告返回 `UNSUPPORTED_*`，UI 给出原因。是否为缺口补充组件，由格式覆盖验证（S2）的数据决定。
4. **FFmpeg 不进入 V1.0 主线**：只有 S2 证明存在需要补的缺口时，才作为**可选模块**单独做许可、专利和安全评审（第 3 节）。
5. **高风险任务进程隔离**：导出编码、跟踪推理、任何自带原生解析代码在 `isolatedProcess` 中运行；播放在应用进程内（Media3 的解析在 Java/Kotlin 中，系统解码器运行在系统媒体进程）。
6. **版本固定**：Media3 以 D1 已使用的 1.9.3 为基线；正式工程初始化时升级到当时最新稳定版并锁定，之后只在里程碑边界评估升级。

## 2. 逐项决定

### 2.1 播放

| 项 | 决定 | 状态 | 说明 / 备选 |
| --- | --- | --- | --- |
| 播放器 | Media3 ExoPlayer | 已定 | 备选平台 MediaPlayer 能力不足（轨道选择、自定义数据源、效果），不采用 |
| 视频/音频解码 | 系统 MediaCodec（Media3 `MediaCodecRenderer`），硬解优先、系统软解回退 | 已定 | 解码器选择与失败回退用 Media3 `DefaultRenderersFactory` 的解码器回退开关 |
| 宿主随机读取 | 自定义 `HostDataSource : BaseDataSource`，在加载线程调用宿主 `readAt`（可取消桥接）；内存预读缓冲 | 待验证 S1 | 不使用磁盘缓存（隐私：不在 VideoKit 侧落盘媒体内容）。缓冲大小、预读策略由 S1 确定 |
| Seek | `SeekParameters`：拖动中 `CLOSEST_SYNC`/`PREVIOUS_SYNC` 低成本预览，松手按请求精确 Seek；可用时启用 Media3 拖动优化模式（scrubbing mode） | 待验证 S1 | 大文件（2 GiB 以上）与慢速源下的 Seek 耗时由 S1 测得 |
| 字幕 | Media3 内置解析：SRT、SSA/ASS（基础样式）、WebVTT、TTML、PGS、DVB；内嵌与外挂（外挂由宿主提供第二个源） | 已定 | ASS 高级特效（动画、复杂排版）不支持，能力报告标 `PARTIAL` |
| 音轨 | Media3 轨道选择（`TrackSelectionParameters`） | 已定 | |
| 音频焦点 | 只有当前发声会话请求音频焦点（`handleAudioFocus` 仅对发声会话开启） | 已定 | |
| 多画面不发声的槽 | **禁用音频轨道**（不选择音频轨，释放音频解码器），而不只是静音 | 已定 | 节省解码器与功耗；切换发声时重新选择音频轨，短暂无声可接受 |
| HDR 视频播放 | 交给 Media3 与设备：支持 HDR 显示的设备直通，否则由系统/Media3 处理 | 已定 | 能力报告给出是否 HDR 直通 |

### 2.2 容器与编码覆盖

原需求容器：mp4、mkv、mov、avi、webm、m4v、ts、m2ts。

| 容器 | Media3 解析器 | 状态 |
| --- | --- | --- |
| mp4 / m4v / mov | `Mp4Extractor` / `FragmentedMp4Extractor` | 已定 |
| mkv / webm | `MatroskaExtractor` | 已定 |
| avi | `AviExtractor` | 已定（覆盖范围由 S2 确认） |
| ts | `TsExtractor`（188 字节包） | 已定 |
| m2ts | Media3 不直接支持 192 字节包格式 → **自研轻量解析适配**：去掉每包 4 字节时间码前缀后交给 `TsExtractor` | 待验证 S2 |

| 编码 | 方案 | 状态 |
| --- | --- | --- |
| H.264、H.265/HEVC、VP8、VP9、AV1（视设备）| 系统解码器 | 已定；具体设备能力由能力探测报告 |
| MPEG-4 Part 2、H.263 | 系统解码器（多数设备有软解） | 待验证 S2 |
| MPEG-2 视频（ts/m2ts 常见）、VC-1 | 系统解码器若有则用；无则报告 `UNSUPPORTED_VIDEO_CODEC` | 待验证 S2，决定是否需要可选补充模块 |
| AAC、MP3、Opus、Vorbis、FLAC、PCM | 系统解码器 / Media3 | 已定 |
| AC-3、E-AC-3、DTS、TrueHD | 系统解码器（设备差异大）；无则报告不支持，**视频仍可无声播放并提示** | 待验证 S2，决定是否需要可选音频补充模块 |

### 2.3 图片

| 项 | 决定 | 状态 |
| --- | --- | --- |
| 静态图解码 | 平台 `ImageDecoder`（JPG、PNG、WebP、HEIF/HEIC、AVIF、BMP，API 31 全覆盖），按目标尺寸降采样解码 | 已定 |
| 大图 | `BitmapRegionDecoder` 分块解码，按视口与缩放级别加载 | 已定 |
| 动图（GIF、动画 WebP、动画 AVIF） | `ImageDecoder` → `AnimatedImageDrawable`，由原生侧按帧绘制到纹理 Surface，支持暂停/继续/循环 | 已定 |
| EXIF 方向 | `ImageDecoder` 自动应用；分块路径用 `ExifInterface` 读取后自行变换 | 已定 |
| 显示 | 统一经 Flutter Texture（与视频同一路径，便于内存控制），见 2.6 | 已定 |
| 第三方图片库 | 不引入（Coil 等不需要；保留为不满足时的备选） | 已定 |

### 2.4 剪辑、拼接与合成

| 项 | 决定 | 状态 | 说明 / 备选 |
| --- | --- | --- | --- |
| 剪辑与导出引擎 | Media3 Transformer + `Composition` / `EditedMediaItemSequence` | 已定 | 备选“MediaCodec + 自建管线”工作量大，只在 Transformer 无法满足的具体点上局部自建 |
| 片段裁剪 | `MediaItem.ClippingConfiguration` | 已定 | |
| 多视频拼接（转码路径） | 一个 `EditedMediaItemSequence` 串接；分辨率、帧率、方向按导出预设统一（`Presentation` 效果） | 待验证 S3 | 混合编码、混合方向、有无音频混合的正确性由 S3 验证 |
| 无重编码快速拼接（remux） | 条件满足时（[08](08_EDIT_TIMELINE_AND_EXPORT_DESIGN.md) §3.1）先用 Transformer 的转封装能力；若对多段序列不支持，**自建 remux**：Media3 解析器读取样本 → Media3 `Mp4Muxer` 写出，时间戳顺接 | 待验证 S3 | 判断错误会花屏，S3 必须含正反样本 |
| 无音频段补静音 | Transformer 的静音补齐（序列级强制音频轨） | 待验证 S3 | |
| 打码效果（马赛克/模糊） | 自研 Media3 `GlEffect` / `GlShaderProgram`：按帧时间取遮罩区域（关键帧插值结果）做像素化或高斯模糊，区域外原样输出 | 待验证 S3（性能） | **预览与导出用同一效果类**：预览用 `ExoPlayer.setVideoEffects`，导出用 `Effects` 挂到 `EditedMediaItem` |
| 遮罩插值 | 纯 Kotlin，在 `videokit-effects` 中实现；UI、预览、导出、覆盖检查共用 | 已定 | |
| 时间线缩略图 | Media3 帧提取（`ExperimentalFrameExtractor`，复用同一数据源与效果）；备选 `MediaMetadataRetriever` + `MediaDataSource` 桥接 readAt | 待验证 S1（顺带测） | 缩略图只在内存，不落盘 |
| HDR 输入导出 | 首版输出 SDR：Transformer HDR→SDR 色调映射（OpenGL） | 待验证 S3 | 设备不支持时能力报告标不可导出 |

### 2.5 导出与封装

| 项 | 决定 | 状态 | 说明 |
| --- | --- | --- | --- |
| 输出格式 | MP4 / H.264 / AAC / SDR；预设原始、1080p、720p（02 §7 #5） | 已定 | |
| 编码器 | 系统 MediaCodec 编码器，经 Transformer `DefaultEncoderFactory`；按能力回退分辨率/码率 | 已定 | D1 C13/C14 已验证系统 AVC 编码器在隔离进程中的配置协商 |
| 封装 | Media3 `InAppMp4Muxer`（media3-muxer）写到宿主 Sink 提供的可随机写 FD | 已定 | 不用平台 `MediaMuxer`：后者只接受文件路径/FD 且错误不可控 |
| 仅顺序写的 Sink | 先写 VideoKit 私有暂存文件，校验通过后顺序复制到 Sink，再删除暂存 | 已定 | 不用 fragmented MP4 作为最终输出（兼容性较差）；fragmented 仅作内部暂存可选格式 |
| 输出校验 | 导出后重新解析输出：时长、轨道、方向、首尾帧可解码 | 已定 | |
| 取消 | Transformer `cancel()` + 进程级兜底（超时后结束隔离进程），Sink `abort()` | 待验证 S4 | 取消上限时间由 S4 测得后冻结 |

### 2.6 渲染

| 项 | 决定 | 状态 |
| --- | --- | --- |
| Flutter 显示 | `TextureRegistry.SurfaceProducer` → `ExoPlayer.setVideoSurface`；Dart 侧 `Texture` | 已定 |
| Surface 回收与重建 | 响应 SurfaceProducer 回调：`clearVideoSurface` / 重新设置；解码器按可见性策略保持或释放 | 已定（M0 用 Fake 先测通） |
| 缩放/平移/旋转 | Flutter 侧矩阵变换，不重新解码 | 已定 |
| 不用 PlatformView | 多画面与性能原因 | 已定 |
| 原生纯引擎宿主 | 宿主提供 `SurfaceView`/`TextureView` 的 Surface | 已定 |

### 2.7 多实例与资源

| 项 | 决定 | 状态 |
| --- | --- | --- |
| 解码器预算 | `ResourceBudget` 先预留后创建（[07](07_MULTI_INSTANCE_AND_RESOURCE_DESIGN.md)）；初始值来自 `MediaCodecInfo` 并发实例数与性能点，再用实际创建失败记录校准 | 待验证 S5 |
| 降级 | 不可见槽暂停并释放解码器；资源不足时降低分辨率（选择较低码流轨道，若有）或暂停，不循环重建 | 已定 |

### 2.8 隔离

| 项 | 决定 | 状态 | 说明 |
| --- | --- | --- | --- |
| 播放 | 应用进程内 | 已定 | 系统解码器崩溃发生在系统媒体进程，表现为可恢复错误 |
| 导出 | 独立 `isolatedProcess` Service；输入、输出经 `ParcelFileDescriptor` 由主进程代理传入（D1 `BrokerDataSource` / `FdOutputMuxer` 的做法） | 待验证 S4 | 宿主 `readAt` 源在主进程读取后经管道或共享内存传入 |
| 跟踪推理 | 独立 `isolatedProcess` Service | 待验证 S4、S6 | |
| 格式探测 | 应用进程内（Media3 解析）；若将来引入原生解析模块则移入隔离进程 | 已定 | |
| 进程粒度 | 每个导出任务、每个跟踪任务各一个进程实例，结束即退出 | 已定 | |

### 2.9 跟踪

| 项 | 决定 | 状态 |
| --- | --- | --- |
| 人脸检测 | OpenCV + YuNet | 待验证 S6（[09](09_TRACKING_TECHNICAL_SPIKE.md)） |
| 物体跟踪 | OpenCV + ViTTrack；对照 CSRT/KCF + 周期重检测 | 待验证 S6 |
| 推理运行时 | OpenCV DNN；对照 ONNX Runtime | 待验证 S6 |
| 帧来源 | Media3 帧提取 / 解码到 `ImageReader`，按分析分辨率降采样 | 已定 |
| 推理核心位置 | C++ `native/tracking-core`（OpenCV + 模型加载 + 预处理），Android 经 JNI 调用；跟踪编排、关联、覆盖报告在平台无关的 `videokit-tracking`（Kotlin） | 已定（2026-11-07，多平台复用） |

### 2.10 平台引擎接口与多平台复用（2026-11-07 确认）

本文第 2.1–2.9 节的 Android 方案全部作为**平台引擎接口（SPI）的 Android 实现**落地，业务规则不写进 Android 实现（分层见 [02](02_SYSTEM_ARCHITECTURE.md) §4，SPI 列表见 02 §4.2，规则见 [13](13_ENGINEERING_CONVENTIONS.md) §3.2）：

| 本文决定 | 放在哪一层 |
| --- | --- |
| ExoPlayer、HostDataSource、字幕/音轨、音频焦点 | Android 实现层 `videokit-media3`（`PlaybackEngine`） |
| 多画面不发声槽禁用音频轨、降级策略 | 平台无关层（`videokit-core` 资源策略），由 `PlaybackEngine` 执行 |
| 容器/编码能力探测 | `CapabilityProbe`（Android：`videokit-platform-android`）；能力模型与判定规则在平台无关层 |
| m2ts 适配 | Android 实现层（Media3 解析器包装） |
| ImageDecoder / BitmapRegionDecoder / AnimatedImageDrawable | `videokit-image-android`（`ImageEngine`）；分块调度、内存额度规则在 `videokit-image` |
| Transformer 拼接、remux、Mp4Muxer、暂存 + 顺序复制 | `videokit-media3`（`CompositionExporter`）；导出计划、快速拼接判定、阶段、取消、输出校验规则在 `videokit-export` / `videokit-timeline` |
| 打码 GlEffect | `EffectRenderer` Android 实现；区域计算与 CPU 参考实现在 `videokit-effects`，GPU 结果与 CPU 参考做黄金图像比对 |
| 遮罩关键帧插值 | 平台无关层 `videokit-timeline`（`spec/vectors` 固化） |
| isolatedProcess + FD 代理 | `IsolationHost` Android 实现（`videokit-platform-android`） |
| 跟踪推理 | `TrackerBackend` → `native/tracking-core`；编排在 `videokit-tracking` |

将来新增平台（另立需求，V1.0 不实现）时的参考映射：Apple 平台播放/导出用 AVFoundation、图片用 ImageIO、效果用 Metal、隔离在 macOS 用 XPC；Windows 用 Media Foundation、WIC、Direct3D。各平台只实现 SPI 与插件平台包，并通过同一套 SPI 契约测试与 `spec/vectors`。

## 3. 不采用 / 有条件采用

| 组件 | 结论 | 条件 |
| --- | --- | --- |
| FFmpeg（含 D1 的 8.0.3 LGPL 构建） | V1.0 主线不采用 | S2 证明有必须补的视频/音频编码或容器缺口时，作为可选模块 `videokit-codec-ext` 提交评审：LGPL 动态链接与替换义务、专利风险、包体积、安全更新责任、只在隔离进程运行。优先考虑只补音频（Media3 官方 FFmpeg 音频扩展的做法） |
| libmpv | 不采用 | 已退出选型（交接文档） |
| 平台 MediaPlayer / MediaMuxer | 不采用 | — |
| Coil / Glide 等图片库 | 不采用 | 平台解码不满足时再评估 |
| Jetpack Compose（Kit 内） | 不采用 | UI 用 Flutter；原生示例宿主可自用 |
| 磁盘媒体缓存（Media3 SimpleCache） | 不采用 | 隐私要求；宿主有需要时自己实现数据源缓存 |

## 4. D1 重新划定：聚焦验证 S1–S6

用户 2026-11-06 决定：原 D1 的离线验证工具链（七角色离线准入链、PowerShell 进程预算对账等）**不再作为开发门禁**；原有 D1 证据、批次记录及其 PASS/FAIL/UNKNOWN/NOT_RUN 状态保持原样，不改写、不追认为通过。D1 改为下列 6 项直接验证技术本身的聚焦验证，与 VK-M0 并行进行。

| 编号 | 问题 | 方法 | 通过标准 | 影响的决定 | 必须完成于 |
| --- | --- | --- | --- | --- | --- |
| S1 宿主读取与 Seek | 自定义 `HostDataSource` 接宿主 `readAt`，在本地、慢速、高延迟（模拟 SMB：每次读取加 20/50/100 ms 延迟、限速）下能否正常播放 | 最小 Android 测试 App：ExoPlayer + HostDataSource；大文件（≥2 GiB）与常见样本；测起播时间、Seek 耗时、卡顿次数、取消读取响应、内存；比较 3 种预读缓冲大小；顺带测缩略图提取 | 本地源起播与 Seek 达到 M1 指标草案；高延迟下可播放且取消在有界时间内返回；无主线程阻塞；释放后句柄归零 | 2.1 宿主读取、Seek，2.4 缩略图 | VK-M1 开始前 |
| S2 格式覆盖 | Media3 + 系统解码器对原需求容器/编码的实际覆盖，缺口在哪里 | 用 `test_media` 全部样本（只读）及补充的公开样本，在至少 2 台不同芯片的设备上跑探测与 10 s 播放；m2ts 适配原型 | 产出“容器 × 编码 × 设备”矩阵；每个缺口给出建议：接受不支持 / 自研适配 / 可选补充模块 | 2.2 全部待验证项；第 3 节 FFmpeg 是否需要 | VK-M1 开始前 |
| S3 拼接与合成 | Transformer 多段拼接（混合编码、方向、帧率、有无音频）和打码 GlEffect 的正确性与速度；多段 remux 是否可行 | 测试 App：组合样本做转码拼接、快速拼接（正反样本）、带 1–4 个遮罩的导出；测输出时长、PTS 连续性、音画同步、方向、导出耗时、发热 | 输出全部通过校验；快速拼接的反例被正确拒绝改走转码；打码导出速度给出实测值（供冻结 M5 指标）；预览与导出遮罩位置一致 | 2.4 全部待验证项 | VK-M4 开始前 |
| S4 隔离与取消 | 导出在 isolatedProcess 中运行，输入输出经 FD 代理；崩溃、内存耗尽、被杀时主进程与播放是否不受影响；取消多久生效 | 在 D1 d1c14 隔离进程代码基础上：注入 SIGSEGV、OOM、无限循环、进程被杀；同时主进程播放视频；测取消耗时 | 每种故障下主进程存活、播放不中断、输出被 abort 且无残留、资源归还；取消耗时给出实测上限 | 2.5 取消，2.8 导出/跟踪隔离 | VK-M4 开始前（M6 冻结） |
| S5 并发解码 | 目标设备同时能运行几个硬解码会话（1080p/4K、H.264/HEVC），失败表现是什么 | 测试 App 逐个增加 ExoPlayer 实例至失败；记录 `MediaCodecInfo` 声明值与实际值、失败错误码、内存、温度 | 每台设备得到实测上限与失败模式；预算估算公式与校准方法确定 | 2.7 解码器预算 | VK-M3 开始前 |
| S6 跟踪 | 见 [09](09_TRACKING_TECHNICAL_SPIKE.md) | 见 09 | 见 09 §7 | 2.9 | VK-M5 开始前 |

执行规则：

1. 每项验证是一个独立的小批次：测试代码 + 原始数据 + 设备清单 + 结论报告，按项目规则整批自测冻结后交独立复核；不需要原 D1 的离线准入链。
2. 验证代码放在 `spikes/<编号>/`，只作参考，不直接进入 Kit；结论通过后在正式模块中按设计重写。
3. 设备：至少一台 Android 12 中端机与一台较新旗舰机（芯片厂商不同），记录型号、系统版本、补丁级别。
6. 2026-11-07 用户决定：S1、S4 先在模拟器（emulator-5556）上做，得出逻辑正确性与相对数据；S2、S3、S5 等测试机分配后再做。模拟器数据不代替真机指标，测试机到位后 S1、S4 的性能项在真机上补测。VK-M1–M3 已按“开发先行、测试后补”（12 §3B）先行开发，相关指标待对应 S 项结论回填。
4. 结论只回填本文第 2 节对应行（把“待验证”改为“已定”并附报告链接），选择超出本文备选范围时走变更评审。
5. 原 D1 已有的可复用结果（隔离进程中系统 AVC 编码器配置协商、FD 代理输入输出、FragmentedMp4Muxer 输出验证等）可作为 S4 的起点，但需在 S4 中按新标准重新测量，不直接计为 S4 通过。

## 5. 技术路线图

```text
          ┌──────────── VK-M0：Flutter UI 框架 + API + Fake（不依赖 S1–S6）────────────┐
并行 ───▶ │ S1 宿主读取/Seek   S2 格式覆盖   S5 并发解码   S3 拼接合成   S4 隔离取消   S6 跟踪 │
          └────────────────────────────────────────────────────────────────────────────┘
VK-M1 单视频播放        需要：S1、S2 结论；M0 API 冻结
VK-M2 图片 + HostAction 需要：M1（方案已定，无额外验证）
VK-M3 多实例            需要：S5
VK-M4 时间线与拼接      需要：S3、S4
VK-M5 打码与跟踪        需要：S3（GlEffect）、S6
VK-M6 导出与安全收尾    需要：S4（取消上限冻结）
VK-M7 发布              —
```

| 里程碑 | 使用的技术（本文决定） |
| --- | --- |
| VK-M1 | ExoPlayer、HostDataSource、系统解码器、Media3 字幕/轨道、SurfaceProducer 纹理、m2ts 适配（若 S2 需要） |
| VK-M2 | ImageDecoder、BitmapRegionDecoder、AnimatedImageDrawable → 纹理 |
| VK-M3 | 多 ExoPlayer 实例、ResourceBudget（S5 校准）、不发声槽禁用音频轨 |
| VK-M4 | Transformer + Composition、ClippingConfiguration、Presentation、自建 remux（若 S3 需要）、InAppMp4Muxer、隔离导出进程 |
| VK-M5 | 自研 GlEffect（预览 `setVideoEffects` + 导出 `Effects` 共用）、OpenCV/YuNet/ViTTrack（S6 结论）、隔离跟踪进程 |
| VK-M6 | Sink 协商、私有暂存 + 顺序复制、取消与进程兜底、输出校验 |

## 6. 变更规则

- “已定”项变更需要说明原因、影响范围和替代方案，经负责人与用户确认后修改本文并记录版本。
- “待验证”项由对应验证结论关闭；验证失败时启用本文列出的备选方案；备选也不可行时提交变更评审，不自行引入新框架。
- 任何新增第三方依赖（包括 S2 后可能的补充模块）按 [10](10_OPEN_SOURCE_AND_LICENSE_PLAN.md) 走许可门禁，未经批准不得进入构建。

## 7. 变更记录

| 版本 | 日期 | 内容 |
| --- | --- | --- |
| V1.0 | 2026-11-06 | 首版；D1 重新划定为 S1–S6，与 VK-M0 并行 |
