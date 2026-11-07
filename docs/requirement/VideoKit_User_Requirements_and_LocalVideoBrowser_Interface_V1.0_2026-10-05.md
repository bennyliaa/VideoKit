# VideoKit 用户需求与 LocalVideoBrowser 接口需求

版本：1.0  
日期：2026-10-05  
状态：独立项目立项需求基线；公共接口在设计阶段评审后冻结  
首期平台：Android 12 / API 31及以上  
交付形态：独立Android Library（AAR/Gradle模块）+ 示例宿主App + Fake/TestKit  
关联宿主：LocalVideoBrowser（项目目录名可为`LocalVideosBrowser`）

## 1. 文档目的

本文件将已经确认的播放、图片查看、多画面和视频编辑需求统一整理为独立项目 **VideoKit** 的产品需求，并重点定义 LocalVideoBrowser 对 VideoKit 的宿主接口要求。

VideoKit必须能够：

1. 作为独立播放器和编辑器库，由LocalVideoBrowser或其他App接入。
2. 将播放器UI、图片查看、编辑时间线、导出和智能跟踪封装在自己的模块内。
3. 不依赖LocalVideoBrowser的NAS、SMB、标签、收藏、VideoBox、数据库和页面导航实现。
4. 通过稳定、版本化的小型接口接收媒体源、初始播放偏好、宿主按钮和输出目标。
5. 通过回调把播放状态、用户操作、错误、资源释放和编辑结果交还宿主。
6. 一个会话只负责一个当前媒体；多画面由宿主创建多个独立会话统一编排。
7. 编辑永远生成新输出，不直接覆盖或删除源媒体。

## 2. 产品定位

VideoKit是可复用的媒体播放与编辑能力库，不是NAS浏览器，也不是LocalVideoBrowser业务模块。

首期以Android AAR为正式交付目标。架构应将领域模型、时间线和编辑计划与Android UI及具体解码器隔离，为以后提供给其他App、制作独立App或扩展其他平台保留可能；本阶段不承诺iOS、macOS或Windows交付时间。

### 2.1 核心能力

- 单视频播放。
- 静态图片和动态图片查看。
- 可创建多个相互独立的播放实例。
- 单视频多片段选择、排序和重新拼接。
- 两个或多个视频按用户顺序拼接。
- 视频区域打码并生成新视频。
- 第一版编辑器即支持自动跟踪人脸和移动物体。
- 将输出写入宿主提供的临时目标。
- 将播放偏好和编辑结果返回宿主保存。

### 2.2 设计原则

- **宿主控制业务**：标签、收藏、VideoBox、文件路径变化和永久删除由宿主处理。
- **VideoKit控制媒体会话**：解码、渲染、控件、时间线、遮罩、跟踪、编码和会话资源由VideoKit处理。
- **源文件只读**：VideoKit不得移动、重命名、覆盖或删除输入媒体。
- **输出先暂存**：导出只写宿主授权的临时输出，最终替换由宿主事务执行。
- **一个实例一个媒体**：多画面不是一个巨型全局播放器，而是多个可独立释放的会话。
- **无全局单例播放器**：不得假设只有一个Activity、一个窗口或一个媒体。
- **能力协商**：宿主按VideoKit报告的能力启用功能，设备能力不足时稳定降级。
- **故障隔离**：单个媒体、解码器、跟踪或导出失败不得拖垮宿主App。
- **取消和释放明确**：所有长任务可取消，所有输入、解码器、Surface和输出句柄可验证释放。
- **许可证安全**：不得因引入VideoKit迫使闭源宿主开源。

## 3. 用户与主要使用场景

### 3.1 LocalVideoBrowser用户

用户从本地或局域网NAS浏览视频和图片，点击媒体后使用VideoKit全屏播放或查看；播放页可触发标签、收藏和编辑。LocalVideoBrowser负责媒体来源和业务数据，VideoKit负责媒体体验。

### 3.2 其他宿主App

其他Android App可以只使用播放能力、只使用编辑能力，或同时使用。VideoKit不得要求宿主建立LocalVideoBrowser的数据表、目录结构或NAS环境。

### 3.3 未来独立App

VideoKit可作为未来独立播放器/编辑器App的底层能力，但独立App的媒体库、文件选择、账号和业务导航不进入VideoKit核心库。

## 4. 功能范围与优先级

| 范围 | 优先级 | 首期要求 |
|---|---|---|
| 稳定公共API、Fake和示例宿主 | P0 | 必须首先完成并冻结基础契约 |
| 单视频播放 | P0 | 正式能力 |
| 静态/动态图片查看 | P0 | 正式能力 |
| HostAction扩展按钮 | P0 | 满足标签、收藏等宿主业务入口 |
| 播放状态捕获与恢复 | P0 | 宿主持久化，VideoKit不建立业务数据库 |
| 多实例与资源报告 | P0 | 为VideoBox多画面提供基础 |
| 单视频片段重排 | P0 | 编辑首版 |
| 多视频拼接 | P0 | 编辑首版 |
| 手动打码 | P0 | 编辑首版 |
| 人脸自动跟踪 | P0 | 编辑首版 |
| 移动物体自动跟踪 | P0 | 编辑首版 |
| 安全导出和取消 | P0 | 不损坏源文件 |
| LocalVideoBrowser适配器契约测试 | P0 | 集成前必须通过 |
| 复杂转场、滤镜、调色、文字贴纸 | 后续 | 本文件不要求首版实现 |
| 图片编辑或图片转视频 | 后续 | 本文件不要求首版实现 |
| 云端AI、素材云同步 | 不做 | 默认全部本机处理 |

## 5. 支持的媒体类型

### 5.1 VideoKit能力与宿主扫描范围的区别

LocalVideoBrowser首版扫描器正式识别以下后缀：

视频：

```text
mp4, mkv, mov, avi, webm, m4v, ts, m2ts
```

图片：

```text
jpg, jpeg, png, webp, heic, heif, avif, bmp, gif
```

扩展名匹配不区分大小写。VideoKit应尽可能播放/显示这些格式，但“被宿主识别”不等于“当前设备一定具备相应解码器”。VideoKit必须先探测能力并返回明确结果，不得因一个不支持的编码导致进程崩溃。

### 5.2 容器与编码

- VideoKit API不能只根据扩展名承诺可播放。
- 播放前允许探测容器、视频编码、音频编码和设备解码能力。
- 对不支持的编码返回稳定错误及建议，不把底层异常直接显示给用户。
- 编辑导出支持范围必须独立报告，不能因为可播放就宣称可无损拼接或可编码。
- 快速无重编码拼接只能在输入参数兼容且验证通过时使用；其他情况走转码导出。

## 6. 播放器用户需求

### 6.1 打开和全屏

- 用户点击媒体卡片后，LocalVideoBrowser创建VideoKit会话并进入独立全屏播放/查看界面。
- 横屏视频默认优先横屏全屏，竖屏视频默认优先竖屏全屏。
- 用户可以手动旋转并锁定方向。
- 每个媒体的方向、缩放等偏好可在下次播放时恢复。
- 偏好由LocalVideoBrowser保存；VideoKit只接收初始状态并在变化/释放时返回最新状态。

### 6.2 视频控件

视频模式至少提供：

- 播放、暂停。
- 进度条和时间显示。
- 快退、快进。
- 拖动Seek及连续快速Seek。
- 播放速度调整。
- 音量、静音。
- 字幕轨选择及开关。
- 音轨选择。
- 全屏、方向切换与方向锁定。
- 自由缩放和平移。
- 编辑入口。
- 宿主提供的标签、收藏等动作按钮。
- 明确的加载、缓冲、重试和失败原因。

不设置固定“上一个视频”和“下一个视频”按钮。邻近媒体列表由LocalVideoBrowser提供，详见第15节。

### 6.3 控件显示和隐藏

- 全屏观看时控件可自动隐藏。
- 用户轻触画面时显示或隐藏控件。
- 宿主叠加的邻近媒体条和宿主动作需要与VideoKit控件同步显示/隐藏。
- VideoKit必须提供控件可见性状态或回调，避免宿主叠加层与播放器控件不同步。
- 编辑模式和错误状态可保持必要控件显示，不得被自动隐藏逻辑遮挡。

### 6.4 缩放、平移和画面适配

- 取消仅提供少数固定画面比例的设计，改为自由缩放。
- 支持双指缩放、拖动平移、双击恢复或切换常用适配状态。
- 支持旋转后的坐标和边界正确处理。
- 缩放、平移、旋转、适配方式和方向属于每个媒体的用户偏好。
- 多画面中每个槽位拥有独立状态。
- 图片和视频使用统一的通用变换模型，但图片不得出现视频速度、字幕等无意义字段。

### 6.5 播放状态和进度

- VideoKit持续提供当前position、duration、播放/暂停、缓冲、用户Seek、可见性和实际观看时间事件。
- LocalVideoBrowser根据这些事件保存观看进度和计算“达到总时长30%计一次播放”。
- 单个播放会话最多计数一次；仅拖动跳到30%以后不能被误认为连续观看达到30%。
- VideoKit不得直接修改LocalVideoBrowser的播放次数数据库。
- 普通单媒体播放与每个VideoBoxFile中的播放状态必须可由宿主使用不同scope保存。

### 6.6 后台与锁定

- App退到后台后继续还是停止播放由LocalVideoBrowser用户设置决定。
- LocalVideoBrowser进入锁定状态时，VideoKit必须接受暂停、隐藏画面、静音或释放命令。
- 即使允许后台继续音频，VideoKit也不能自行解除宿主登录锁。
- VideoKit不创建超出宿主授权的长期后台服务。

## 7. 图片查看需求

- 图片由VideoKit统一会话显示，不能要求宿主另建完全不同的播放架构。
- 支持静态图片、动态GIF和动态WebP。
- 支持缩放、平移、旋转、方向和全屏。
- 图片界面隐藏进度、倍速、音轨、字幕、快进/快退等视频专属控件。
- 动态图片可以播放/暂停及循环；是否显示简化的动画控件由能力和UI设计决定。
- 左右翻页动作由VideoKit识别后向宿主发送导航请求，宿主决定前后媒体并重新绑定。
- VideoKit不得自行查询LocalVideoBrowser的上一张或下一张图片。
- 大图、长图、透明图、旋转元数据图和损坏图必须有内存限制及错误隔离。
- 图片不占用“视频解码器数量”额度，但仍计入总体内存和渲染资源预算。

## 8. 多实例和多画面需求

### 8.1 基本规则

- 一个VideoKit会话同一时刻只绑定一个视频或一张图片。
- LocalVideoBrowser单媒体播放是一个槽位的特例。
- 多画面由LocalVideoBrowser为每个槽位创建独立会话。
- VideoKit不得维护全局唯一播放器或全局唯一当前媒体。
- 每个会话拥有独立播放位置、缩放、平移、方向、字幕、音轨和错误状态。

### 8.2 数量和降级

- LocalVideoBrowser默认手机同时显示4个媒体、平板9个媒体。
- 用户可调整，但视频会话硬上限为12。
- VideoKit必须提供设备能力探测：可用硬件解码器预算、建议并发数、是否需要软件解码及资源风险。
- 当设备无法支持目标数量时返回可解释的降级结果，由LocalVideoBrowser减少活跃视频数、暂停离屏槽位或显示静态占位。
- 禁止反复创建解码器直到崩溃。

### 8.3 音频规则

- 同一时刻最多一个视频发声，也允许全部静音。
- 默认可以由LocalVideoBrowser指定“最后点击的槽位发声”。
- 用户可以选择某一槽位为声音来源。
- 选中媒体离开当前批次或释放后，默认所有槽位静音，等待用户重新选择。
- VideoKit会话接受宿主的音频焦点/静音命令，不自行争夺其他会话的声音。

### 8.4 可见性和生命周期

- 宿主可通知会话`VISIBLE`、`PARTIALLY_VISIBLE`、`OFFSCREEN`、`BACKGROUND`和`LOCKED`。
- 离屏会话可降帧、暂停或释放解码器，但必须返回可恢复状态。
- 页面销毁、槽位移除、媒体切换和App锁定都必须最终释放Surface、解码器、输入句柄和协程任务。

## 9. 宿主动作：标签、收藏及扩展按钮

### 9.1 通用HostAction

VideoKit只理解宿主动作ID，不理解标签、收藏或其他业务含义。宿主可提供：

```text
actionId
labelKey
contentDescriptionKey
iconKey或宿主图标资源
enabled
selected
pending
badgeText?
displayPriority
placement
```

VideoKit负责在播放控件区域渲染或预留这些动作，并在用户点击时返回`actionId + sessionId + mediaToken`。

### 9.2 LocalVideoBrowser标签操作

- 播放时用户可点击标签按钮，创建新标签或把当前媒体加入已有标签。
- 标签选择、标签创建和业务校验由LocalVideoBrowser完成。
- 为避免边播放边移动/复制正在读取的文件，LocalVideoBrowser把标签变更放入持久工作队列。
- VideoKit继续使用当前有效媒体租约，不自行刷新路径。
- 用户离开媒体或会话释放后，VideoKit通知宿主资源已释放。
- LocalVideoBrowser随后执行标签物理事务并更新索引。
- 再次播放时LocalVideoBrowser按稳定`contentId`重新解析最新文件实例并提供新媒体源。
- VideoKit可显示宿主返回的`pending`状态，但不得自行移动文件。

### 9.3 收藏操作

- 收藏按钮也是HostAction。
- LocalVideoBrowser处理收藏读写并回传新的selected状态。
- VideoKit不得保存收藏记录或直接访问NAS用户资料。

### 9.4 宿主动作故障

- 宿主动作超时或失败不能中断播放。
- VideoKit显示轻量错误或恢复按钮，具体文案可由宿主提供。
- 重复点击需支持宿主去重；pending期间可禁用或合并操作。

## 10. 视频编辑需求

### 10.1 编辑入口和工程

- 用户可从播放界面进入编辑模式。
- 编辑工程必须可序列化、版本化和恢复，不使用源路径作为身份。
- 编辑工程引用宿主提供的稳定`mediaToken`和会话内sourceId。
- VideoKit不得把LocalVideoBrowser的`contentId`数据结构写进公共API；宿主可把contentId映射为不透明token。
- 原视频在整个编辑和导出过程中保持不变。

### 10.2 单视频片段重新拼接

支持用户从同一个视频中选择多个时间片段并生成新视频：

- 添加片段。
- 设置每段开始和结束时间。
- 调整片段前后顺序。
- 删除片段。
- 修改已有片段边界。
- 预览编辑后的顺序。
- 显示预计输出时长和空间。
- 导出为一个新视频。

首版片段之间使用直接切换即可，复杂转场不作为P0。输出时间边界应达到用户视觉可接受的准确度；关键帧限制或重编码差异必须透明处理。

### 10.3 多视频拼接

支持两个或多个视频重新拼接为一个视频：

- 从宿主接收多个独立输入源。
- 支持调整视频顺序。
- 支持对每个输入先裁剪需要的片段。
- 支持预览最终顺序。
- 输入参数兼容时允许安全快速拼接。
- 编码、分辨率、方向、帧率或音频参数不兼容时，按导出配置统一转码。
- 方向元数据必须正确处理，不能导出旋转错误的视频。
- 音视频时间轴不同步时必须失败或修复，不能静默生成明显错位结果。

首版不要求图片混入视频时间线，也不要求复杂转场、背景音乐或多轨合成。

### 10.4 手动打码

- 支持在指定时间范围对画面区域应用马赛克或模糊。
- 用户可以选择目标区域、调整大小和位置。
- 支持通过关键帧修正区域随时间的位置和大小。
- 多个打码目标可分别开启、暂停和删除。
- 预览与最终导出效果应保持一致。
- 画面旋转、裁剪、缩放和导出分辨率变化后，遮罩坐标必须正确映射。
- 打码失败不能输出被错误宣称为已保护的视频。

### 10.5 自动跟踪人脸

第一版即支持：

- 检测画面中的一个或多个人脸。
- 用户选择需要打码的人脸，而不是默认永久处理所有人脸。
- 在指定时间区间跟踪所选人脸。
- 跟踪目标短时遮挡或离开画面后，能尝试重新关联。
- 置信度不足、跟踪丢失或目标可能混淆时必须在时间线上明确提示。
- 用户可在任意关键帧重新指定/修正目标并继续跟踪。
- 导出前提供“未覆盖区间”检查，避免静默漏码。
- 默认全部在设备本地处理，不上传人脸图像或生物特征。

### 10.6 自动跟踪移动物体

第一版即支持：

- 用户通过点选或框选指定移动物体。
- 在指定时间区间内跟踪其位置、大小和必要的形变边界。
- 支持多个目标，但必须按设备能力限制并发。
- 遮挡、快速移动、出画、重新进入和相似物体混淆时显示明确状态。
- 用户可添加纠正关键帧，并从纠正点重新计算后续轨迹。
- 跟踪结果作为可编辑数据保存，不直接不可逆地写入源视频。
- 导出前允许逐段预览跟踪和打码效果。

### 10.7 智能跟踪质量要求

- 不能用“模型运行完成”代替效果验收。
- 建立包含单人、多人、遮挡、侧脸、快速移动、低光、竖屏、横屏和高分辨率的测试集。
- 分别记录检测率、跟踪丢失次数、错误关联、未覆盖帧、处理速度、峰值内存、设备温度和电量。
- 最终阈值在技术Spike后冻结；未达到阈值时允许用户切换为手动关键帧，不得假装自动跟踪可靠。
- 跟踪模块失败只影响对应编辑功能，普通播放和手动编辑必须继续可用。

## 11. 导出与输出安全

### 11.1 核心规则

- VideoKit导出永远生成新输出。
- VideoKit不得覆盖、重命名、移动或删除任何输入源。
- 输出只能写入宿主提供的`VideoKitOutputSink`。
- 导出失败或取消时调用宿主abort；不得把部分输出标记为完成。
- 导出成功后返回技术元数据和不透明OutputToken，由宿主验证和提交。

### 11.2 输出信息

导出结果至少返回：

```text
outputToken
container/extension
videoCodec?
audioCodec?
width/height
orientation
durationMs
sizeBytes
frameRate?
audioPresent
createdAt
sourceTokens[]
editProjectId
exportPresetId
warnings[]
```

VideoKit可报告元数据，但LocalVideoBrowser仍需通过自己的文件事务重新验证输出存在、大小、可打开性和目标空间。

### 11.3 暂停、取消和进程终止

- 导出任务可取消，并在有界时间停止读取、编码和写入。
- 如果所选编码器不支持可靠暂停，UI不得伪装“可暂停”；可提供取消后重新导出。
- App进程终止后，源文件不受影响。
- 宿主根据OutputToken/任务所有权清理未提交临时文件。
- VideoKit工程状态可恢复；正在编码的二进制任务首版允许从头重启，不强制实现跨进程断点编码。

## 12. LocalVideoBrowser编辑后业务规则

本节是VideoKit必须配合的接口需求，但业务由LocalVideoBrowser实现。

### 12.1 编辑完成后的替换流程

1. VideoKit把新视频写入宿主临时输出。
2. LocalVideoBrowser验证新视频可打开及元数据正确。
3. 新视频最终继承原视频正式名称和业务身份。
4. 原视频默认保持不变，直到用户确认后续处理。
5. 用户选择永久删除原视频时，LocalVideoBrowser通过文件事务执行永久删除。
6. 用户选择保留原视频时，LocalVideoBrowser把原视频改名为`视频名_dump_日期`。
7. 所有重命名、伴随文件、索引和用户资料变更都由LocalVideoBrowser负责。

VideoKit只返回新输出和来源关系，不能自行执行上述替换。

### 12.2 编辑前后成对管理

LocalVideoBrowser提供“已编辑视频”页面，新旧视频左右成对显示：

- 永久删除旧dump视频时，同时清理与旧实例关联且确认可删除的文件和数据。
- 永久删除当前新视频时，旧视频继承新视频的名称及应继承的业务资料。
- 删除任意一方并完成业务处理后，该配对不再继续显示。
- 所有删除永久生效并由LocalVideoBrowser二次确认。

VideoKit需在输出结果中提供`editProjectId`、输入token列表和输出token，方便LocalVideoBrowser建立配对，但不维护dump数据库。

## 13. 公共API总体要求

### 13.1 API原则

- API采用语义版本和明确`apiVersion`。
- 能力通过集合或版本化对象协商，未知可选字段可忽略。
- 删除字段、改变语义或改变状态机必须升级主版本并提供迁移说明。
- 公共接口不得暴露LocalVideoBrowser、SMBJ、Room DAO、Compose页面、宿主数据库或宿主导航类型。
- 播放核心不得强制宿主使用某一种依赖注入框架。
- 第三方播放器、编解码器、AI模型和图像库类型不得穿透公共API。
- 长任务使用可取消的挂起调用/Flow；状态流有界，避免高频事件压垮宿主。
- 每个句柄提供明确`close/release`并支持重复调用安全。

### 13.2 建议的顶层接口

以下接口用于表达需求，命名和拆分可在设计评审时微调：

```kotlin
interface VideoKit {
    val apiVersion: VideoKitApiVersion
    suspend fun capabilities(request: CapabilityRequest): VideoKitCapabilities
    fun createSession(config: VideoKitSessionConfig): VideoKitSession
    fun createEditProject(config: EditProjectConfig): VideoKitEditProject
}

interface VideoKitSession : AutoCloseable {
    val state: StateFlow<VideoKitSessionState>
    val events: Flow<VideoKitEvent>

    suspend fun bind(
        source: VideoKitMediaSource,
        initialState: VideoKitPlaybackState?,
        hostActions: List<VideoKitHostAction>
    )

    suspend fun execute(command: VideoKitCommand): VideoKitCommandResult
    suspend fun updateHostActions(actions: List<VideoKitHostAction>)
    suspend fun captureState(): VideoKitPlaybackState
    suspend fun release(): VideoKitPlaybackState
}

interface VideoKitEditProject : AutoCloseable {
    val state: StateFlow<VideoKitEditState>
    suspend fun addSource(source: VideoKitMediaSource): SourceToken
    suspend fun apply(command: VideoKitEditCommand): EditCommandResult
    suspend fun snapshot(): SerializedEditProject
    suspend fun export(
        request: VideoKitExportRequest,
        sink: VideoKitOutputSink
    ): VideoKitExportResult
    suspend fun cancelExport(exportId: String)
}
```

## 14. 媒体输入接口要求

### 14.1 VideoKitMediaSource

公共媒体源应是VideoKit自己的描述符，建议至少包含：

```text
mediaToken：宿主生成的不透明会话标识
mediaKind：VIDEO | IMAGE_STATIC | IMAGE_ANIMATED | IMAGE_UNKNOWN
displayName?：可选，仅显示用途
knownLength?：已知长度
mimeType?：可选提示，不作为唯一信任依据
extension?：可选提示
seekability：RANDOM_ACCESS | SEQUENTIAL_ONLY
sourceFactory：创建短生命周期输入句柄
```

VideoKit不得要求绝对NAS路径、SMB URL、用户名、密码或LocalVideoBrowser数据库对象。

### 14.2 随机读取句柄

为支持SMB大视频Seek，输入接口必须允许宿主提供随机读取：

```kotlin
interface VideoKitReadHandle : AutoCloseable {
    val length: Long?
    suspend fun readAt(
        offset: Long,
        target: ByteArray,
        targetOffset: Int,
        length: Int
    ): Int
}
```

要求：

- VideoKit按需读取，不为播放完整下载NAS视频。
- Seek可关闭旧读取区间并从新offset继续。
- 读取可取消，有超时和稳定错误映射。
- VideoKit不缓存凭据或可重建完整NAS地址。
- release后不再使用句柄。
- 同一会话可能为探测、播放和编辑创建不同句柄，宿主必须能追踪并关闭。

### 14.3 本地和离线媒体

VideoKit允许宿主适配本地文件、Content URI、文件描述符或设备私有离线文件。Android具体类型只能出现在Android适配artifact中，核心编辑计划不得依赖它们。

### 14.4 媒体租约

- LocalVideoBrowser在解析`contentId`后选择当前可用`fileInstanceId`并取得媒体租约。
- 租约有效期间，标签整理、移动、重命名或删除任务等待资源释放。
- VideoKit释放输入后发出`SourceReleased`事件。
- LocalVideoBrowser收到释放事件后才执行排队的物理操作。
- VideoKit不得在释放后用旧路径自动重连。

## 15. LocalVideoBrowser播放接口需求

### 15.1 适配层

LocalVideoBrowser通过独立适配模块接入VideoKit，例如：

```text
:contract:playback
:contract:editor
:adapter:videokit
```

业务feature只依赖LocalVideoBrowser自己的contract，不直接依赖VideoKit具体实现。适配器完成：

```text
BrowserMediaSource → VideoKitMediaSource
MediaPlayHobby ↔ VideoKitPlaybackState
Browser宿主动作 ↔ VideoKitHostAction
VideoKitOutputToken → FileOperationPlan
VideoKitStableError → Browser稳定错误
```

移除VideoKit AAR后，LocalVideoBrowser仍应能够使用临时Media3播放器和图片查看实现进行基础浏览。

### 15.2 邻近媒体竖向列表

播放界面右侧显示与当前媒体相邻的前两个和后两个媒体，可上下滚动到更前或更后的媒体：

- 邻近媒体查询、分页、预览图和滚动状态属于LocalVideoBrowser。
- VideoKit不访问媒体索引，也不硬编码“前后两个”的业务规则。
- LocalVideoBrowser可在VideoKit渲染区域之外叠加列表，或通过通用宿主面板扩展点显示。
- 用户点击邻近媒体后，LocalVideoBrowser解析新`contentId`，获取新租约并调用bind/创建会话。
- 右侧列表与VideoKit控制栏同时显示和隐藏，因此VideoKit必须输出`controlsVisible`状态。
- 图片左右翻页同样通过宿主导航回调完成，不能绕过MediaResolver直接拼路径。

### 15.3 播放偏好映射

LocalVideoBrowser的`MediaPlayHobby`至少包括：

```text
zoom, panX, panY, rotation, fitMode,
preferredOrientation, fullscreen,
positionMs?, speed?, volume?, muted?,
subtitleTrack?, audioTrack?, lastViewedAt
```

作用域：

```text
SINGLE
VIDEO_BOX(videoBoxFileId)
```

要求：

- VideoKit不保存scope，只接收和返回一个状态快照。
- LocalVideoBrowser用`contentId + scope`持久化。
- 同一媒体的普通播放与不同VideoBoxFile互不覆盖。
- 图片相关快照中视频专属字段为空。
- 状态保存失败不能阻止会话释放。

### 15.4 播放统计事件

VideoKit应输出足够事件，让LocalVideoBrowser区分：

- 自然连续观看。
- 暂停时间。
- 缓冲时间。
- 用户拖动跳转。
- 前后台切换。
- 会话结束。

LocalVideoBrowser负责30%播放计数和每会话去重。VideoKit不直接增加计数。

### 15.5 生命周期命令

LocalVideoBrowser至少需要发送：

```text
PLAY
PAUSE
SEEK_TO
SET_SPEED
SET_MUTED
SET_VOLUME
SELECT_AUDIO_TRACK
SELECT_SUBTITLE_TRACK
SET_TRANSFORM
SET_ORIENTATION
SET_FULLSCREEN
SET_VISIBILITY
SET_ACTIVE_AUDIO
HIDE_CONTENT_FOR_LOCK
RELEASE
```

命令必须返回已执行、拒绝、被替代、能力不支持或会话已释放等稳定结果。

## 16. LocalVideoBrowser多画面接口需求

### 16.1 PlaybackCoordinator职责

LocalVideoBrowser的PlaybackCoordinator负责：

- 根据VideoBoxFile成员创建/销毁会话。
- 决定手机4路、平板9路、最多12路的布局。
- 处理媒体顺序、拖动重排和当前批次。
- 保存每个VideoBoxItem独立PlayHobby。
- 选择唯一声音来源。
- 根据可见性暂停、恢复或释放槽位。
- 根据VideoKit能力报告降级并向用户解释。

VideoKit只负责每个会话，不实现VideoBox仓储、动态查询或成员删除。

### 16.2 会话隔离

- 一个槽位失败只关闭或降级该槽位。
- 某个图片损坏不影响其他视频。
- 某个视频无解码器时可显示错误占位，其余槽位继续。
- 一个会话release不得释放其他会话共享但仍在使用的底层资源。
- VideoKit内部如使用共享池，必须引用计数正确且对宿主透明。

### 16.3 动态与手动VideoBox

- 系统动态VideoBox成员由LocalVideoBrowser查询条件决定，不能从播放页直接删除媒体。
- 手动VideoBox允许从播放页移除当前成员。
- VideoKit只发送“请求移除当前项”等宿主动作ID，不修改集合。

## 17. LocalVideoBrowser编辑接口需求

### 17.1 输入

LocalVideoBrowser向VideoKit提供：

- 一个或多个只读媒体源。
- 不透明mediaToken/sourceToken。
- 每个输入的显示名称和可选技术提示。
- 当前播放位置，可用于进入编辑时定位。
- 宿主允许的编辑能力和导出预设。
- 临时输出Sink。

LocalVideoBrowser不把SMB凭据、标签仓储或文件事务引擎传入VideoKit。

### 17.2 输出Sink建议接口

```kotlin
interface VideoKitOutputSink {
    suspend fun openTemporary(request: OutputOpenRequest): VideoKitWriteHandle
    suspend fun markReady(
        handleId: String,
        metadata: VideoKitExportedMedia
    ): VideoKitOutputToken
    suspend fun abort(handleId: String, reason: VideoKitAbortReason)
}
```

要求：

- Sink由宿主决定写设备私有临时文件还是NAS授权临时目录。
- VideoKit不能从token反推出最终目录或源路径。
- 输出句柄能力需明确：顺序写、随机写、flush、长度、剩余空间未知等。
- VideoKit根据编码器要求提前声明需要的Sink能力；不支持时在导出前失败。
- `markReady`只代表VideoKit写完，不代表LocalVideoBrowser已经正式提交。

### 17.3 宿主验证与提交

LocalVideoBrowser收到OutputToken后执行：

```text
计划 → 权限/空间/版本验证 → 验证输出 → 用户确认
→ 暂存/最终改名 → 更新索引和用户资料 → 清理临时文件
```

VideoKit不得绕过此流程，也不得获得永久删除接口。

### 17.4 编辑过程事件

VideoKit至少报告：

```text
项目准备进度
媒体探测状态
跟踪进度和丢失区间
导出阶段
已处理时长/帧数
预计剩余时间（仅在可可靠估计时）
输出字节数
警告和可恢复错误
取消确认
所有输入/输出资源释放
```

进度无法可靠计算时显示阶段和已完成量，不伪造百分比。

## 18. 宿主回调需求

建议提供：

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

要求：

- 回调可取消，有超时，不在主线程执行阻塞I/O。
- 回调失败不应让VideoKit死锁。
- VideoKit不得持有Activity或宿主页面的长期强引用。
- 事件携带最小必要数据和不透明ID，不携带密码及完整NAS地址。
- 高频进度事件支持采样/合并，避免写数据库风暴。

## 19. 状态、错误与能力模型

### 19.1 会话状态

至少包含：

```text
CREATED
BINDING
READY
PLAYING
PAUSED
BUFFERING
ENDED
ERROR_RECOVERABLE
ERROR_FATAL
RELEASING
RELEASED
```

图片会话可以使用READY/VIEWING等映射，但公共状态必须让宿主明确判断资源是否仍被占用。

### 19.2 编辑状态

至少包含：

```text
CREATED
PREPARING
READY
TRACKING
EXPORTING
CANCELLING
CANCELLED
COMPLETED
FAILED
RELEASING
RELEASED
```

非法状态转换必须拒绝并返回稳定错误，不能静默忽略。

### 19.3 稳定错误分类

至少包括：

- SOURCE_NOT_FOUND。
- SOURCE_PERMISSION_DENIED。
- SOURCE_DISCONNECTED。
- SOURCE_TIMEOUT。
- UNSUPPORTED_CONTAINER。
- UNSUPPORTED_VIDEO_CODEC。
- UNSUPPORTED_AUDIO_CODEC。
- DECODER_UNAVAILABLE。
- DECODER_RESOURCE_EXHAUSTED。
- CORRUPT_MEDIA。
- SEEK_UNSUPPORTED。
- OUTPUT_PERMISSION_DENIED。
- OUTPUT_SPACE_INSUFFICIENT。
- OUTPUT_CAPABILITY_UNSUPPORTED。
- ENCODER_UNAVAILABLE。
- EXPORT_FAILED。
- TRACKING_MODEL_UNAVAILABLE。
- TRACKING_LOST。
- CANCELLED。
- HOST_CALLBACK_FAILED。
- SESSION_RELEASED。
- INTERNAL_ERROR_REDACTED。

错误对象包含稳定code、阶段、是否可重试、建议动作和脱敏诊断摘要；第三方异常及堆栈不得穿透普通UI。

### 19.4 能力报告

能力报告至少包括：

- 视频/音频解码器信息摘要。
- 支持的容器和编码组合。
- 可用硬件视频会话建议值。
- 最大建议分辨率/帧率。
- 字幕、音轨、速度和精确Seek能力。
- 图片静态/动态及大图能力。
- 单视频片段编辑能力。
- 多输入拼接能力。
- 可用编码器和输出格式。
- 人脸/物体跟踪模块状态。
- 跟踪建议分辨率和并发目标数。
- 输出Sink能力要求。
- 功能不可用原因。

## 20. UI与适配要求

- 支持手机和平板。
- 支持竖屏、横屏、方向锁定、分屏和窗口尺寸变化。
- 控件适配系统手势区、刘海、圆角和安全区域。
- 支持触摸、鼠标/触控板和基本键盘操作，为平板及未来桌面形态保留。
- 支持大字体，不让关键按钮重叠或不可达。
- 提供内容描述、焦点顺序和无障碍状态。
- 所有用户可见文本可国际化；至少提供简体中文和英文资源机制。
- 宿主可以替换主题颜色、图标和部分文案，但不能破坏状态和无障碍语义。
- VideoKit UI不能硬编码LocalVideoBrowser名称、标签名或NAS概念。

## 21. 性能与资源要求

- 播放远程大视频按需随机读取，不完整下载后再播放。
- 不在主线程执行网络、解码、AI或编码任务。
- 所有队列、帧缓存和事件流有明确上限。
- 连续Seek、切换媒体、旋转和多实例不得持续泄漏句柄、Surface或解码器。
- 图片大图解码有采样/分块策略，禁止无条件原尺寸全量进入内存。
- 多画面根据可见性和设备能力降级帧率或暂停离屏媒体。
- 跟踪和导出记录耗时、峰值内存、CPU、温度和电量，但Release不保存永久操作日志。
- 资源不足优先返回可解释降级，不循环重试直至ANR或崩溃。

具体性能阈值在真实ARM64手机和平板Spike后冻结，不在没有实测时承诺统一毫秒数。

## 22. 安全、隐私与日志

- 默认所有播放、分析、人脸检测、物体跟踪和编辑在设备本地完成。
- 不上传媒体、截图、人脸数据、对象特征或时间线。
- 不保存SMB用户名、密码、Token、完整NAS URL或宿主数据库内容。
- 不直接访问宿主文件系统，只通过输入句柄和输出Sink工作。
- 不提供删除源文件API。
- Release不产生永久用户操作日志。
- 错误通过脱敏回调交给宿主；默认不记录完整媒体名和完整路径。
- Debug日志必须可关闭，且不得记录凭据和媒体内容。
- 原生代码必须执行边界检查、资源释放和损坏输入模糊测试。

## 23. 开源与许可证要求

- 优先采用成熟、仍维护且许可证适合闭源商业App的组件。
- 允许优先评估AndroidX Media3等官方组件。
- 可选择性参考或合法移植明确允许的播放器交互实现，并记录来源Commit、许可证和修改内容。
- GPL、AGPL、SSPL、无许可证或许可证不清的代码不得进入产品模块。
- 若评估FFmpeg，必须在引入前明确所用构建配置、LGPL/GPL组件、链接方式、NOTICE、源码提供义务和宿主闭源影响；未经批准不得默认集成。
- AI跟踪模型和训练数据分别核查代码许可证、模型许可证、商用范围、再分发和隐私要求。
- 所有依赖使用精确版本、Version Catalog、依赖锁定和校验；禁止动态版本和Snapshot。
- 发布时交付BOM/SBOM、第三方NOTICE、传递依赖和已知漏洞检查。

## 24. 推荐模块边界

模块名称可在设计阶段微调，职责不得合并为巨型模块：

```text
:videokit-api            公共接口、DTO、版本和稳定错误
:videokit-core           会话状态机、能力协商、通用变换
:videokit-playback       播放控制与轨道模型
:videokit-media3         Media3薄适配实现
:videokit-image          静态/动态图片查看
:videokit-ui             Android播放器/编辑器UI
:videokit-timeline       片段、排序、关键帧和编辑工程
:videokit-effects        马赛克、模糊和遮罩
:videokit-tracking       人脸和移动物体跟踪适配层
:videokit-export         编码、拼接和输出Sink协调
:videokit-testkit        Fake、契约测试和故障注入
:sample-host             独立示例宿主App
```

依赖方向建议：

```text
UI/平台适配器 → core/api ← tracking/export/playback实现
```

要求：

- `videokit-api`不依赖具体播放器、AI模型和宿主业务。
- 修改普通UI不应无条件重编译所有原生编码/AI模块。
- 跟踪、导出和图片模块可被独立替换或禁用。
- LocalVideoBrowser只依赖发布的API/AAR和自己的适配器，不直接包含VideoKit源码树。

## 25. 构建和交付形态

VideoKit项目至少交付：

- 可版本化的Android AAR/Maven artifact。
- 独立API artifact及可选功能artifact。
- Consumer ProGuard/R8规则。
- API参考文档和版本变更记录。
- 示例宿主App。
- 不需要真实NAS的Fake媒体源。
- LocalVideoBrowser契约TestKit。
- 支持格式和能力说明。
- 依赖BOM/SBOM及第三方NOTICE。
- Debug/Release构建及SHA-256。
- 性能、稳定性、编辑输出和跟踪质量报告。
- 已知问题和不支持能力清单。

VideoKit工程可单独编译测试。LocalVideoBrowser日常CI默认使用Fake或已发布AAR，不因为浏览器普通业务改动而重新编译VideoKit全部源码。

## 26. 测试要求

### 26.1 公共契约测试

- API版本与能力协商。
- 旧状态快照读取和新增可选字段兼容。
- 未知未来主版本安全拒绝。
- 正常、取消、超时、重复调用和release幂等。
- HostAction超时/失败不影响播放。
- 输入句柄和输出Sink故障映射。
- Fake与真实实现执行同一套契约测试。

### 26.2 播放测试

- 0%、25%、50%、90%和接近结尾Seek。
- 连续快速Seek。
- 暂停、恢复、播放结束和重新播放。
- 字幕、音轨、倍速、方向、缩放和状态恢复。
- 小视频、2GiB以上视频、长视频、损坏视频、0字节和播放中断线。
- 每种正式容器至少测试一个真实有效样本；缺少样本标NOT_RUN。
- 输入释放后SMB/文件句柄归零。

### 26.3 图片测试

- JPG/JPEG、PNG、WebP、HEIC/HEIF、AVIF、BMP、GIF。
- 静态WebP、动态WebP和动态GIF。
- 小图、大图、长图、透明图、旋转元数据图和损坏图。
- 左右导航请求、缩放、平移、旋转、窗口变化和资源释放。
- 图片界面不显示视频专属控件。

### 26.4 多实例测试

- 1、4、9、12个槽位。
- 视频/静态图/动态图混排。
- 每格状态独立。
- 唯一音频源及全静音。
- 离屏暂停/释放和重新绑定。
- 解码器不足、内存压力和温度升高时稳定降级。
- 一个槽位故障不影响其他槽位。

### 26.5 编辑和导出测试

- 单视频多个片段的添加、裁剪、删除和重排。
- 多个同参数和不同参数视频拼接。
- 横竖屏、可变帧率、不同音频参数和无音频输入。
- 手动马赛克/模糊与坐标映射。
- 导出取消、空间不足、权限失败、输入断线、编码器失败和进程被杀。
- 任意失败时源媒体字节和路径保持不变。
- 不完整输出不被markReady。
- 宿主验证失败后VideoKit不自行提交或删除源。

### 26.6 自动跟踪测试

- 单人、多脸、侧脸、遮挡、离开/进入画面。
- 单物体、多物体、快速运动、低对比和相似目标。
- 关键帧纠正和从纠正点继续。
- 跟踪丢失区间提示。
- 预览与导出遮罩一致性。
- 取消、模型缺失、内存不足和热降级。
- 不产生网络上传或永久人脸资料。

### 26.7 LocalVideoBrowser集成契约

- BrowserMediaSource可映射为VideoKitMediaSource且不暴露凭据。
- MediaPlayHobby往返不丢字段，SINGLE/VIDEO_BOX作用域由宿主隔离。
- 标签/收藏HostAction只回传ID。
- 播放中标签操作等待SourceReleased。
- controlsVisible可驱动邻近媒体条同步显示。
- 多会话音频和资源限制由Browser协调。
- 输出只进入宿主Sink。
- 移除AAR后LocalVideoBrowser临时播放器仍可构建运行。
- VideoKit崩溃或加载失败不阻止LocalVideoBrowser启动和浏览。

### 26.8 设备矩阵

- Android 12/API31最低版本。
- 一个中间主流Android版本。
- 当前稳定Android版本。
- ARM64实体手机。
- 10英寸级实体平板或明确记录的等价设备。
- 竖屏、横屏、分屏和窗口变化。
- 字体100%、130%、200%。
- 简体中文、英文、伪本地化和RTL冒烟。

## 27. 验收阻断条件

出现以下任一项不得发布VideoKit正式版本或交给LocalVideoBrowser正式集成：

- VideoKit可能覆盖、移动或删除输入源。
- 输出绕过宿主Sink或绕过宿主验证直接成为正式文件。
- NAS凭据、完整路径或宿主数据库类型进入公共API。
- 一个会话故障导致整个宿主崩溃或其他会话被错误释放。
- 多实例无法限制音频或资源不足时循环创建解码器。
- 人脸/物体跟踪丢失时仍把结果宣称为完整打码。
- 编辑失败后留下被标记为成功的部分输出。
- 稳定复现ANR、OOM、Surface/句柄泄漏或无法取消的任务。
- GPL/AGPL/SSPL或许可证不明代码进入计划闭源的产品模块。
- Release包含测试凭据、真实NAS资料、压力入口或永久调试日志。
- AAR无法独立构建，或LocalVideoBrowser必须直接依赖VideoKit源码才能运行。

## 28. 建议开发里程碑

| 里程碑 | 内容 | 退出条件 |
|---|---|---|
| VK-M0 | 项目骨架、许可证审查、API/Fake/TestKit、示例宿主 | LocalVideoBrowser可只用Fake完成契约集成 |
| VK-M1 | 单视频播放、随机读取、状态恢复、字幕/音轨/缩放/方向 | Android 12手机及真机大视频播放通过 |
| VK-M2 | 图片查看、动态图片、左右导航、HostAction和宿主叠加同步 | 图片矩阵与标签/收藏回调通过 |
| VK-M3 | 多实例能力探测、1/4/9/12槽、音频唯一和降级 | 单槽故障隔离，多槽稳定释放 |
| VK-M4 | 时间线、单视频片段重排、多视频拼接、编辑工程保存 | 新输出正确，源文件不变 |
| VK-M5 | 手动打码、人脸跟踪、移动物体跟踪和纠正关键帧 | 跟踪质量报告及漏码检查通过 |
| VK-M6 | 导出Sink、取消、故障恢复、性能和安全收尾 | 输出协议、资源释放及许可证通过 |
| VK-M7 | 发布AAR、版本兼容、LocalVideoBrowser真实适配 | 可移除/替换AAR，宿主仍可降级运行 |

里程碑可并行的前提是公共API已经评审冻结；跟踪和导出模块可在播放/图片模块之后并行开发。

## 29. 设计阶段必须冻结的待定项

以下内容不得由开发者无记录地自行决定：

1. Maven group、artifact、Android namespace和版本策略。
2. 公共API是否拆分播放artifact与编辑artifact。
3. Media3、图像库、编码器、FFmpeg替代方案及许可证结论。
4. 人脸和移动物体跟踪技术、模型许可证和最低设备要求。
5. 首版输出容器、编码器和质量预设。
6. 快速无重编码拼接的兼容条件。
7. 跟踪效果、导出速度、内存和温度验收阈值。
8. Compose UI、Android View及纯引擎模式的对外组合方式。
9. OutputSink需要顺序写、随机写还是文件描述符能力。
10. 编辑工程Schema、版本迁移和进程恢复范围。
11. 默认控件布局、主题扩展和宿主叠加层API。
12. 多实例共享资源池及硬件解码器预算算法。

每一项需形成设计决定、替代方案、风险、许可证和测试计划，再进入相应实现。

## 30. VideoKit项目交接要求

新的VideoKit项目负责人收到本文件后，应先提交以下设计文档，评审通过再开始大规模编码：

```text
docs/PRODUCT_REQUIREMENTS.md
docs/SYSTEM_ARCHITECTURE.md
docs/PUBLIC_API_CONTRACT.md
docs/LOCALVIDEOBROWSER_INTEGRATION.md
docs/PLAYBACK_AND_IMAGE_DESIGN.md
docs/EDIT_TIMELINE_AND_EXPORT_DESIGN.md
docs/TRACKING_TECHNICAL_SPIKE.md
docs/OPEN_SOURCE_AND_LICENSE_PLAN.md
docs/TEST_AND_ACCEPTANCE_PLAN.md
docs/MILESTONES.md
```

设计报告必须特别回答：

- 如何让LocalVideoBrowser提供SMB随机读取而VideoKit不知道账号和路径。
- 如何保证播放资源释放后标签工作队列才移动/复制媒体。
- 如何让普通播放和不同VideoBox的PlayHobby互不覆盖。
- 如何由宿主统一控制多会话音频、数量和降级。
- 如何把标签/收藏设计为通用HostAction而不引入宿主业务依赖。
- 如何确保编辑输出只写宿主临时Sink且永不覆盖源。
- 如何让自动跟踪失败区间对用户可见并可人工修正。
- 如何独立发布AAR、运行契约测试，并在缺失或故障时由LocalVideoBrowser安全回退。

## 31. 最终成功标准

VideoKit成功不是只在示例视频上显示画面，而是同时满足：

1. LocalVideoBrowser无需把NAS、标签、收藏、VideoBox或数据库交给VideoKit。
2. VideoKit可以通过宿主随机读取接口稳定播放本地及NAS大视频。
3. 视频和图片共享统一会话边界，图片隐藏无关控件。
4. 单媒体和多画面使用同一种可多实例架构。
5. 每个媒体的播放偏好可完整交还宿主，并按作用域隔离。
6. 标签、收藏、邻近媒体和导航全部通过宿主接口完成。
7. 单视频片段重排、多视频拼接、手动打码及自动人脸/物体跟踪可生成新视频。
8. 任意编辑失败、取消、断线或进程终止都不改变源媒体。
9. VideoKit可作为版本化AAR独立构建、测试和替换。
10. 缺少VideoKit或单个功能模块失败时，LocalVideoBrowser仍可启动、浏览并回退到临时播放器。
