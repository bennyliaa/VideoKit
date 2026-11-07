# 04 公共 API 契约

版本：V1.2（API 1.0.0 草案；V1.2 把 Android 类型拆到 videokit-api-android；M0-B1 对齐裁定见 [04A](04A_API_ALIGNMENT_M0B1.md)，冲突时以 04A 为准）；日期：2026-11-07；对应原需求 §13、§14、§15.5、§17.2、§18、§19。命名可在评审时微调；冻结后按第 10 节版本规则变更。

## 1. 原则

- 所有平台无关的公共类型在 `videokit-api`，包名 `com.videokit.api`：**纯 Kotlin（KMP `commonMain`），不含任何 Android 或 JVM 专属类型**，不依赖 Media3、AI、数据库类型（V1.2，2026-11-07，见 [02](02_SYSTEM_ARCHITECTURE.md) §4）。
- Android 专属类型（`Context`、`Surface`、Uri、FileDescriptor）放在独立模块 `videokit-api-android`（包名 `com.videokit.api.android`）：Android 工厂入口、`AndroidSurface` 渲染目标、`MediaSources` 适配。
- 长任务是 `suspend` 函数或 `Flow`，均可取消；状态是 `StateFlow`；事件是有界 `Flow`。
- 每个句柄实现 `AutoCloseable`，`close()`/`release()` 重复调用安全。
- 所有外部可见 ID 为不透明字符串；时间用微秒 `Long`；画面坐标为归一化 `Float`（0–1，相对于显示方向校正后的画面）。
- 不暴露宿主类型、凭据、完整路径或第三方库类型。
- 公共 API 不依赖任何依赖注入框架；入口是普通工厂函数。

## 2. 顶层接口

```kotlin
// videokit-api（平台无关）
interface VideoKit : AutoCloseable {
    val apiVersion: VideoKitApiVersion                // major.minor.patch
    suspend fun capabilities(request: CapabilityRequest): VideoKitCapabilities
    fun createSession(config: VideoKitSessionConfig): VideoKitSession
    fun createEditProject(config: EditProjectConfig): VideoKitEditProject
    suspend fun restoreEditProject(serialized: SerializedEditProject, config: EditProjectConfig): VideoKitEditProject
}

data class VideoKitConfig(
    val hostCallbacks: VideoKitHostCallbacks,
    val resourceBudget: ResourceBudget,               // 宿主范围，见 07
    val logging: LoggingPolicy = LoggingPolicy.ReleaseDefault,
)

// videokit-api-android（Android 入口）
object VideoKitFactory {
    fun create(context: android.content.Context,      // 仅用于取 applicationContext，不持有 Activity
               config: VideoKitConfig): VideoKit
}
```

其他平台各自提供工厂入口（如 Apple 平台的 `VideoKitFactory.create(config:)`），返回同一个平台无关的 `VideoKit` 接口。

## 3. 会话

```kotlin
interface VideoKitSession : AutoCloseable {
    val sessionId: String
    val state: StateFlow<VideoKitSessionState>
    val events: Flow<VideoKitEvent>

    suspend fun bind(
        source: VideoKitMediaSource,
        initialState: VideoKitPlaybackState?,
        hostActions: List<VideoKitHostAction>,
    ): VideoKitCommandResult

    suspend fun execute(command: VideoKitCommand): VideoKitCommandResult
    suspend fun updateHostActions(actions: List<VideoKitHostAction>)
    suspend fun captureState(): VideoKitPlaybackState
    suspend fun release(): VideoKitPlaybackState     // 幂等；返回最后快照
    fun attachSurface(target: VideoKitSurfaceTarget) // 见 4.4
    fun detachSurface()
}
```

- 一个会话同一时刻只绑定一个媒体（视频或图片）；重新 `bind` 会先释放旧源并发出 `SourceReleased`。
- `close()` 等价于不等待结果的 `release()`。

### 3.1 会话状态

```text
CREATED → BINDING → READY ⇄ PLAYING ⇄ PAUSED
                     ↘ BUFFERING ↗      ↘ ENDED
任意 → ERROR_RECOVERABLE（可重试回 BINDING/READY）
任意 → ERROR_FATAL
任意 → RELEASING → RELEASED（终态）
```

```kotlin
data class VideoKitSessionState(
    val phase: SessionPhase,                // 上图状态
    val mediaKind: MediaKind?,
    val positionUs: Long, val durationUs: Long?, val bufferedUs: Long?,
    val playWhenReady: Boolean,
    val speed: Float, val volume: Float, val muted: Boolean,
    val audioTracks: List<TrackInfo>, val subtitleTracks: List<TrackInfo>,
    val selectedAudioTrackId: String?, val selectedSubtitleTrackId: String?,
    val transform: MediaTransform,
    val orientation: OrientationState,
    val visibility: Visibility,
    val activeAudio: Boolean,
    val controlsVisible: Boolean,
    val error: VideoKitStableError?,
    val resourcesHeld: Boolean,             // 宿主据此判断资源是否仍被占用（§19.1）
)
```

图片会话使用 READY 表示正在显示，动态图用 PLAYING/PAUSED 表示动画状态；视频专属字段（轨道、速度、音量）在图片会话中为空或默认值且 UI 不显示。

## 4. 命令与结果

### 4.1 命令（§15.5）

```kotlin
sealed interface VideoKitCommand {
    data object Play; data object Pause
    data class SeekTo(val positionUs: Long, val mode: SeekMode = SeekMode.CLOSEST_SYNC)
    data class SetSpeed(val speed: Float)
    data class SetMuted(val muted: Boolean)
    data class SetVolume(val volume: Float)
    data class SelectAudioTrack(val trackId: String?)
    data class SelectSubtitleTrack(val trackId: String?)   // null = 关闭字幕
    data class SetTransform(val transform: MediaTransform)
    data class SetOrientation(val request: OrientationRequest)
    data class SetFullscreen(val fullscreen: Boolean)
    data class SetVisibility(val visibility: Visibility)
    data class SetActiveAudio(val active: Boolean, val audioEpoch: Long)
    data class HideContentForLock(val hidden: Boolean)
    data object Release
}
```

### 4.2 结果

```kotlin
sealed interface VideoKitCommandResult {
    data object Executed
    data class Rejected(val error: VideoKitStableError)      // 非法状态转换等
    data object Superseded                                    // 被后续同类命令取代（如连续 Seek）
    data class Unsupported(val reason: UnsupportedReason)     // 能力不支持
    data object SessionReleased
}
```

### 4.3 连续 Seek

快速连续 Seek 只执行最新目标，之前未完成的返回 `Superseded`；拖动中可用 `SeekMode.PREVIEW` 低成本预览，松手发 `CLOSEST_SYNC` 或 `EXACT`。

### 4.4 渲染目标

```kotlin
// videokit-api（平台无关）：开放接口，由各平台模块提供具体实现
interface VideoKitSurfaceTarget {
    val width: Int
    val height: Int
}

// videokit-api-android
class AndroidSurface(val surface: android.view.Surface, override val width: Int, override val height: Int) : VideoKitSurfaceTarget
// Flutter 插件用 TextureRegistry.SurfaceProducer 提供的 Surface；原生纯引擎宿主用自己的 SurfaceView/TextureView
```

平台实现只接受本平台的目标类型，收到其他类型返回 `Unsupported`。

Flutter 侧不直接接触 Surface：`videokit_flutter` 为每个会话创建纹理并返回 `textureId`，UI 用 `Texture(textureId)` 显示（见第 12 节）。

## 5. 媒体输入（§14）

```kotlin
data class VideoKitMediaSource(
    val mediaToken: String,
    val mediaKind: MediaKind,                  // VIDEO | IMAGE_STATIC | IMAGE_ANIMATED | IMAGE_UNKNOWN
    val displayName: String? = null,           // 仅显示
    val knownLength: Long? = null,
    val mimeType: String? = null,              // 提示，不作唯一依据
    val extension: String? = null,             // 提示
    val seekability: Seekability,              // RANDOM_ACCESS | SEQUENTIAL_ONLY
    val sourceFactory: VideoKitSourceFactory,
)

fun interface VideoKitSourceFactory {
    suspend fun open(purpose: OpenPurpose): VideoKitReadHandle   // PROBE | PLAYBACK | EDIT | EXPORT
}

interface VideoKitReadHandle : AutoCloseable {
    val length: Long?
    suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int  // -1 = EOF
}
```

- `readAt` 由宿主实现；VideoKit 在 IO 调度器调用，按超时取消；返回值小于请求长度属于正常短读。
- 宿主可抛出 `VideoKitSourceException(code)` 表达 NOT_FOUND、PERMISSION_DENIED、DISCONNECTED、TIMEOUT，VideoKit 映射为对应稳定错误。
- Android 适配（模块 `videokit-api-android`，包 `com.videokit.api.android`）：`MediaSources.fromUri(context, uri, token)`、`fromFileDescriptor(pfdProvider, token)`、`fromFile(file, token)`，宿主可选用。

## 6. 编辑工程（§10、§17）

```kotlin
interface VideoKitEditProject : AutoCloseable {
    val projectId: String
    val state: StateFlow<VideoKitEditState>
    val events: Flow<VideoKitEditEvent>
    suspend fun addSource(source: VideoKitMediaSource): SourceToken
    suspend fun apply(command: VideoKitEditCommand): EditCommandResult
    suspend fun undo(): EditCommandResult
    suspend fun redo(): EditCommandResult
    suspend fun snapshot(): SerializedEditProject
    fun previewSession(): VideoKitSession                    // 预览用会话，与导出共用同一计划
    suspend fun checkExport(request: VideoKitExportRequest, sink: VideoKitOutputSink): ExportPrecheck
    suspend fun export(request: VideoKitExportRequest, sink: VideoKitOutputSink): VideoKitExportResult
    suspend fun cancelExport(exportId: String)
}
```

编辑状态（§19.2）：`CREATED → PREPARING → READY ⇄ TRACKING → READY → EXPORTING → COMPLETED / FAILED / CANCELLING → CANCELLED`，任意 → `RELEASING → RELEASED`。非法转换返回 `Rejected`。命令、Schema 详见 [08](08_EDIT_TIMELINE_AND_EXPORT_DESIGN.md)。

## 7. 宿主动作（§9）

```kotlin
data class VideoKitHostAction(
    val actionId: String,
    val labelKey: String,                       // 宿主文案 key 或直接文本，由宿主 resolver 解析
    val contentDescriptionKey: String,
    val icon: HostIcon,                         // 内置 iconKey 或宿主 drawable 资源 ID
    val enabled: Boolean = true,
    val selected: Boolean = false,
    val pending: Boolean = false,
    val badgeText: String? = null,
    val displayPriority: Int = 0,
    val placement: ActionPlacement,             // PRIMARY_BAR | SECONDARY_BAR | OVERFLOW
)
```

点击后 VideoKit 调用 `onHostActionRequested(HostActionRequest(actionId, sessionId, mediaToken))`。pending 期间同一动作的重复点击被合并。

## 8. 宿主回调（§18）

```kotlin
interface VideoKitHostCallbacks {
    suspend fun onHostActionRequested(request: HostActionRequest): HostActionResult
    suspend fun onNavigationRequested(request: NavigationRequest): NavigationResult
    suspend fun onPlaybackSnapshot(snapshot: VideoKitPlaybackState)
    suspend fun onPlaybackEvent(event: VideoKitPlaybackEvent)
    suspend fun onControlsVisibilityChanged(sessionId: String, visible: Boolean)
    suspend fun onSourceReleased(sessionId: String, mediaToken: String)
    suspend fun onRecoverableError(error: VideoKitStableError): RecoveryDecision
    suspend fun onFatalSessionError(error: VideoKitStableError)
}
```

- 每个回调有超时（默认值在 M0 冻结，宿主可配置）；超时或异常记为 `HOST_CALLBACK_FAILED`，不阻塞会话。
- 回调不在主线程执行阻塞 I/O；VideoKit 不持有 Activity 的长期强引用。
- 事件只带最小必要数据与不透明 ID。
- 高频事件（进度）采样合并；`onPlaybackSnapshot` 在状态变化稳定后与释放时发送。

## 9. 错误与能力

### 9.1 稳定错误（§19.3）

```kotlin
data class VideoKitStableError(
    val code: ErrorCode,              // 见下表
    val stage: ErrorStage,            // PROBE | BIND | PLAYBACK | DECODE | EDIT | TRACKING | EXPORT | SINK | CALLBACK
    val retryable: Boolean,
    val suggestedAction: SuggestedAction,   // RETRY | CHOOSE_OTHER_TRACK | REDUCE_QUALITY | FREE_SPACE | NONE …
    val diagnostic: String?,          // 脱敏摘要，不含路径、凭据、媒体名
)
```

`ErrorCode`：SOURCE_NOT_FOUND、SOURCE_PERMISSION_DENIED、SOURCE_DISCONNECTED、SOURCE_TIMEOUT、UNSUPPORTED_CONTAINER、UNSUPPORTED_VIDEO_CODEC、UNSUPPORTED_AUDIO_CODEC、DECODER_UNAVAILABLE、DECODER_RESOURCE_EXHAUSTED、CORRUPT_MEDIA、SEEK_UNSUPPORTED、OUTPUT_PERMISSION_DENIED、OUTPUT_SPACE_INSUFFICIENT、OUTPUT_CAPABILITY_UNSUPPORTED、ENCODER_UNAVAILABLE、EXPORT_FAILED、TRACKING_MODEL_UNAVAILABLE、TRACKING_LOST、CANCELLED、HOST_CALLBACK_FAILED、SESSION_RELEASED、INTERNAL_ERROR_REDACTED。新增错误码属于次版本变更，宿主须把未知码按 `INTERNAL_ERROR_REDACTED` 处理。

第三方异常与堆栈不穿透普通 UI；Debug 构建可通过开关输出脱敏诊断。

### 9.2 能力报告（§19.4）

```kotlin
data class VideoKitCapabilities(
    val schemaVersion: Int,
    val decoders: DecoderSummary,                    // 视频/音频解码器摘要
    val containerCodecSupport: List<FormatSupport>,  // 容器 × 编码 → SUPPORTED | PARTIAL | UNSUPPORTED + 原因
    val suggestedHardwareVideoSessions: Int,
    val maxSuggestedResolution: Size, val maxSuggestedFrameRate: Int,
    val playbackFeatures: PlaybackFeatures,          // 字幕、音轨、速度、精确 Seek
    val imageFeatures: ImageFeatures,                // 静态/动态/大图
    val editFeatures: EditFeatures,                  // 单视频片段、多输入拼接
    val encoders: List<EncoderSupport>, val outputFormats: List<OutputFormat>,
    val tracking: TrackingStatus,                    // 人脸/物体模块状态、建议分辨率、并发目标数
    val sinkRequirements: SinkRequirements,
    val unavailableReasons: Map<FeatureKey, UnsupportedReason>,
)
```

`CapabilityRequest` 可指定具体媒体源，以返回针对该媒体的探测结果（是否可播放、是否可快速拼接）。可播放不等于可编码或可无损拼接，二者分别报告（§5.2）。

## 10. 版本与兼容

| 变更 | 版本 |
| --- | --- |
| 新增可选字段、新增命令、新增错误码、新增能力项 | 次版本（minor） |
| 修复不改变语义 | 修订版本（patch） |
| 删除字段、改变语义、改变状态机 | 主版本（major），附迁移说明 |

- 序列化快照（播放状态、编辑工程）带 `schemaVersion`；读取旧版本必须成功，新增可选字段有默认值；遇到未知的未来主版本安全拒绝（§26.1）。
- `VideoKitApiVersion` 在运行时可查询；宿主可据此启用功能。

## 11. 契约测试

`videokit-testkit` 提供 `VideoKitContractSuite`：对任意 `VideoKit` 实现运行同一套用例（版本与能力协商、状态机合法与非法转换、命令结果、取消与超时、release 幂等、回调失败隔离、输入与 Sink 故障映射、快照兼容）。Fake 与真实实现都必须通过，详见 [11](11_TEST_AND_ACCEPTANCE_PLAN.md)。

Dart 侧 `videokit_fake` 提供同名的 Dart 契约测试，对 `videokit_fake` 与 `videokit_flutter`（连接真实原生 Kit，在设备上以 `integration_test` 运行）执行相同用例。

## 12. Dart API（`videokit_api`）

Dart API 与 Kotlin API 语义一一对应，供 `videokit_ui` 与 Flutter 宿主使用。

### 12.1 对应规则

| Kotlin | Dart |
| --- | --- |
| `suspend fun` | `Future<T>` |
| `StateFlow<T>` | `ValueListenable<T>`（同时提供 `Stream<T>`） |
| `Flow<T>` 事件 | `Stream<T>`（有界、采样） |
| `sealed interface` | Dart 3 `sealed class` |
| `data class` | 不可变类（`final` 字段 + `copyWith` + 相等性） |
| `AutoCloseable.close()` | `Future<void> close()`，幂等 |
| `Long` 微秒 | `int` 微秒 |
| 错误码枚举 | `enum ErrorCode`；未知值映射为 `internalErrorRedacted` |

### 12.2 顶层接口（示意）

```dart
abstract interface class VideoKit {
  VideoKitApiVersion get apiVersion;
  Future<VideoKitCapabilities> capabilities(CapabilityRequest request);
  Future<VideoKitSession> createSession(VideoKitSessionConfig config);
  Future<VideoKitEditProject> createEditProject(EditProjectConfig config);
  Future<void> close();
}

abstract interface class VideoKitSession {
  String get sessionId;
  ValueListenable<VideoKitSessionState> get state;
  Stream<VideoKitEvent> get events;
  int? get textureId;                       // 画面纹理；Fake 为 null，UI 用演示画面
  Future<VideoKitCommandResult> bind(VideoKitMediaSource source,
      {VideoKitPlaybackState? initialState, List<VideoKitHostAction> hostActions = const []});
  Future<VideoKitCommandResult> execute(VideoKitCommand command);
  Future<void> updateHostActions(List<VideoKitHostAction> actions);
  Future<VideoKitPlaybackState> captureState();
  Future<VideoKitPlaybackState> release();
}
```

`VideoKitEditProject`、宿主回调、错误与能力的 Dart 定义按 12.1 规则从 Kotlin 版本生成或手写对应，冻结时两侧同时评审。

### 12.3 媒体源与 Sink 在 Dart 侧

- Flutter 宿主通常持有原生侧可直接访问的源（本地文件、Content URI），Dart 只传描述符与 token，读取在原生侧完成。
- 宿主需要自定义 `readAt`（如 SMB）时，推荐在原生侧实现 `VideoKitSourceFactory` 并以 token 注册；Dart 实现 `readAt` 也支持，但每次读取跨通道，仅用于低带宽场景，并在能力说明中标注性能影响。
- 输出 Sink 同理：推荐原生实现；Dart 侧只接收 `VideoKitExportResult`。

### 12.4 通道

- 命令与查询：Pigeon 生成的 `@HostApi`（Dart → 原生）。
- 状态与事件：每个会话一个 EventChannel 流，原生侧已做采样合并。
- 回调（HostAction、导航等）：Pigeon `@FlutterApi`（原生 → Dart），带超时；Dart 回调异常按 `HOST_CALLBACK_FAILED` 处理。
- 通道协议带版本号；Dart 包与原生 AAR 版本不匹配时初始化失败并给出明确错误。
