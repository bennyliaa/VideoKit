# 06 播放与图片设计

版本：V1.1；日期：2026-11-06；对应原需求 §5–§7、§14、§15、§21、§26.2–§26.3。

## 1. 媒体类型与能力探测（§5）

- 宿主扫描范围：视频 mp4、mkv、mov、avi、webm、m4v、ts、m2ts；图片 jpg、jpeg、png、webp、heic、heif、avif、bmp、gif（大小写不敏感）。被宿主识别不等于设备可解码。
- `bind` 前或 `capabilities(request = 具体媒体)` 时执行探测：读取容器头（经宿主 readAt）、识别轨道与编码，对照设备解码器能力，得出 SUPPORTED / PARTIAL（如音轨不支持但视频可播）/ UNSUPPORTED。
- 不支持时返回稳定错误（UNSUPPORTED_CONTAINER / _VIDEO_CODEC / _AUDIO_CODEC）及建议，绝不让底层异常导致崩溃；未知格式的探测在隔离进程中执行（见 [07](07_MULTI_INSTANCE_AND_RESOURCE_DESIGN.md) §5）。
- 可播放与可编辑分开报告：可播放不代表可快速拼接或可编码（§5.2）。

## 2. 视频会话结构

```text
VideoKitSession（core）
 ├─ 命令执行器（串行）
 ├─ 状态 StateFlow / 事件 Flow（采样）
 ├─ PlaybackController（playback）
 │    └─ Media3Backend（media3）
 │         ├─ ExoPlayer 实例（每会话一个）
 │         ├─ HostDataSource（宿主 readAt 桥接）
 │         └─ 轨道 / 错误映射
 ├─ TransformState（通用缩放/平移/旋转/适配）
 └─ ResourceLease（来自 ResourceBudget，见 07）
```

- 每个会话独立 ExoPlayer，不共享全局播放器；解码器、Surface、输入句柄归会话所有。
- 播放后端通过内部 `PlaybackBackend` 接口接入，Media3 是 V1.0 唯一实现；接口保证将来替换不影响 API。

## 3. 宿主随机读取（§14.2）

`HostDataSource` 实现 Media3 `DataSource`：

1. `open(dataSpec)`：首次调用 `sourceFactory.open(PLAYBACK)` 获取句柄（或复用会话内已有句柄），记录 offset 与长度。
2. `read(buffer, off, len)`：在 Media3 加载线程中调用；内部以 `runBlocking` 加超时等待挂起的 `readAt`（运行在 IO 调度器），可被会话取消打断。不在主线程执行。
3. Seek：Media3 发起新 `open(position)`，关闭旧读取区间，从新 offset 继续，不重新下载。
4. 短读正常处理；返回 -1 表示 EOF；未知长度时 `C.LENGTH_UNSET`。
5. 错误映射：宿主异常 → `SOURCE_*` 稳定错误；超时 → `SOURCE_TIMEOUT`；取消 → `CANCELLED`。
6. 读取缓冲有上限（Media3 LoadControl 的缓冲上限按设备内存配置，值 M1 冻结），不完整下载大视频。
7. 关闭：会话释放时关闭所有句柄（探测、播放），全部关闭后发 `SourceReleased`。

2GiB 以上偏移使用 `Long`，单次读长度为 `Int`，测试覆盖 2GiB+ 位置读取（§26.2）。

## 4. 播放控制与状态

| 能力 | 实现要点 |
| --- | --- |
| 播放/暂停/结束/重播 | ExoPlayer 状态映射到 SessionPhase |
| Seek | 连续 Seek 只保留最新目标（旧的返回 Superseded）；拖动中 PREVIEW 模式，松手精确 |
| 快退/快进 | 固定步长（默认 10 秒，可配置），在边界处钳制 |
| 倍速 | 0.25–4.0 之间的离散档位；音调保持 |
| 音量/静音 | 会话内音量；静音同时受宿主 SetActiveAudio 约束（见 07） |
| 音轨/字幕 | 由 Media3 Tracks 映射为 TrackInfo（id、语言、标签、编码、是否支持）；字幕可关闭；外挂字幕由宿主作为附加源提供（API 预留，M1 决定是否首版支持） |
| 方向 | 依据视频显示宽高（考虑旋转元数据）决定默认横/竖；SetOrientation 支持 AUTO/PORTRAIT/LANDSCAPE/LOCKED；实际窗口方向由宿主 Activity 执行，VideoKit 通过回调请求 |
| 缩放平移 | `MediaTransform(scale, panX, panY, rotation, fitMode)`；手势在 UI 层计算后通过 SetTransform 提交，会话保存并在快照中返回；边界约束防止画面完全移出 |
| 缓冲与错误 | BUFFERING 相位；可恢复错误提供重试；失败原因来自稳定错误 |

### 4.1 事件与统计（§6.5、§15.4）

事件类型：PositionTick（采样）、PlayStateChanged、BufferingStarted/Ended、UserSeek(from, to)、VisibilityChanged、ForegroundChanged、WatchTimeAccumulated(deltaUs)、SessionEnded。

- 实际观看时间只在 PLAYING 且可见、未缓冲时累计，用户 Seek 不计入，使宿主能区分自然观看与跳转，并实现“达到 30% 计一次播放、每会话一次”。
- VideoKit 不计数、不写宿主数据库。

### 4.2 后台与锁定（§6.6）

- 退到后台是否继续由宿主通过 SetVisibility(BACKGROUND) + Play/Pause 决定。
- HideContentForLock：立即停止渲染到可见 Surface，画面替换为遮挡层，可选静音；锁定优先于其他命令，晚到的恢复命令不能解锁。
- 不创建前台服务或长期后台服务；如宿主需要后台音频，由宿主自己的服务持有会话。

## 5. 渲染

- Flutter UI：`videokit_flutter` 为每个会话用 `TextureRegistry.SurfaceProducer` 创建纹理，把其 Surface 交给会话 `attachSurface`，Dart 侧用 `Texture(textureId)` 显示。画面尺寸变化时更新 SurfaceProducer 尺寸。
- Flutter 后台或引擎回收 Surface 时（SurfaceProducer 的回调），会话 `detachSurface`，恢复时重新附加。
- 纯引擎原生宿主自行提供 `Surface`（`SurfaceView`/`TextureView`）。
- Surface 销毁时会话 `detachSurface`，解码器可保持或按可见性策略释放；重新附加后恢复。
- 缩放、平移、旋转在 Flutter 侧对 `Texture` 做矩阵变换（`Transform`），不重新解码；变换值同时以 SetTransform 提交给会话保存。
- 多画面每个槽一个纹理；不使用 PlatformView 承载视频（性能与多实例开销大）。
- 图片：静态图解码在原生侧完成后同样经纹理显示（统一渲染路径，便于大图分块与内存控制）；动态图逐帧写入纹理，由原生侧控制播放/暂停。

## 6. 图片会话（§7）

### 6.1 结构

```text
VideoKitSession（mediaKind = IMAGE_*）
 └─ ImageBackend（image）
      ├─ 探测：读文件头识别格式、尺寸、EXIF 方向
      ├─ 解码：ImageDecoder（静态 / GIF / WebP 动画 / HEIF / AVIF）
      ├─ 大图：BitmapRegionDecoder 分块 + 采样
      └─ 内存：按 ResourceBudget 的图片内存额度控制
```

### 6.2 解码策略

| 情况 | 策略 |
| --- | --- |
| 普通图片 | `ImageDecoder` 按显示尺寸采样（`setTargetSize`），不按原尺寸全量解码 |
| 大图 / 长图 | 低分辨率预览 + 可见区域分块高清解码（`BitmapRegionDecoder` 支持的格式）；不支持分块的格式按内存上限采样 |
| 动态 GIF / WebP | `AnimatedImageDrawable`；PLAYING/PAUSED 控制；默认循环；帧缓存受内存额度限制 |
| HEIC/HEIF、AVIF | 平台解码（API 31 支持）；能力探测中如实报告 |
| 旋转元数据 | 读 EXIF 方向并校正显示，坐标系统一到校正后画面 |
| 透明图 | 保留 Alpha，背景由主题 Token 决定 |
| 损坏图 | 返回 CORRUPT_MEDIA，不影响其他会话 |

- 输入经宿主 readAt：ImageDecoder 的 `Source` 从会话缓冲读取（小图整读到受限内存缓冲；大图走分块读取）。
- 图片不占视频解码器额度，但申请图片内存额度；额度不足时降级采样并在状态中提示。

### 6.3 交互

- 缩放、平移、旋转、适应/原尺寸复用通用 `MediaTransform`。
- 左右翻页：在未放大时左右滑动触发 `NavigationRequest`；放大时滑动为平移，到达边缘后再滑才翻页。
- 视频专属控件（进度、倍速、音轨、字幕、快进快退）不出现。

## 7. 资源释放

释放顺序：停止播放 → 取消在途读取 → 释放解码器 → 断开 Surface → 关闭全部输入句柄 → 发出 `SourceReleased` → 归还 ResourceLease → 状态 RELEASED。每一步失败也继续后续步骤，最终状态如实反映未能确认的资源（`resourcesHeld`）。

## 8. 验收要点

- 0%、25%、50%、90%、接近结尾 Seek；连续快速 Seek；暂停、恢复、结束、重播。
- 字幕、音轨、倍速、方向、缩放与状态恢复。
- 小视频、2GiB 以上、长视频、损坏、0 字节、播放中断线；每种容器至少一个真实样本，缺样本标 NOT_RUN。
- 输入释放后文件句柄归零。
- 图片全格式、静态/动态 WebP 与 GIF、小/大/长/透明/旋转/损坏图、导航请求、窗口变化与释放；图片界面无视频控件。
