# 08 编辑时间线与导出设计

版本：V1.0；日期：2026-11-06；对应原需求 §10.1–§10.4、§11、§17、§26.5。自动跟踪见 [09](09_TRACKING_TECHNICAL_SPIKE.md)。

## 1. 原则

- 源只读：编辑全程不修改、移动、重命名、删除任何输入。
- 输出只经宿主 `VideoKitOutputSink`；失败或取消一定 abort，部分输出永不 markReady。
- 预览与导出使用同一份不可变编辑计划（同一 PTS 映射、同一遮罩轨迹），保证所见即所得。

## 2. 编辑工程模型

### 2.1 Schema（版本化 JSON）

```text
EditProject {
  schemaVersion, projectId, revision, createdAt, updatedAt
  sources: [ { sourceId, mediaToken, displayName?, probe: { durationUs, width, height, rotation, fps?, videoCodec, audioCodec?, hasAudio } } ]
  timeline: { clips: [ { clipId, sourceId, inUs, outUs } ] }         // 顺序即播放顺序
  masks: [ MaskTrack ]                                                // 见第 4 节
  tracking: [ TrackingTask 引用与结果 ]                                // 见 09
  exportPresetId?
}
```

- 身份用 `projectId + sourceId + mediaToken`，不使用源路径（§10.1）；不包含宿主 contentId 结构。
- 时间单位微秒；坐标为相对“方向校正后源画面”的归一化值。
- 每次修改 `revision + 1`；`snapshot()` 输出完整 JSON，宿主可保存；`restoreEditProject` 读取并迁移旧 `schemaVersion`，未知未来主版本拒绝。
- 恢复时若宿主提供的源探测结果与工程记录不一致（时长、尺寸变化），标记该源 MISMATCH，用户确认后才能继续。

### 2.2 编辑命令

```text
AddClip(sourceId, inUs, outUs, index?)   SplitClip(clipId, atUs)
TrimClip(clipId, inUs, outUs)            MoveClip(clipId, toIndex)
RemoveClip(clipId)                       ReorderSources(...)
AddMask(type, region, rangeUs)           UpdateMaskKeyframe(maskId, atUs, region)
SetMaskEnabled(maskId, enabled)          RemoveMask(maskId)
SetMaskStyle(maskId, MOSAIC|BLUR, strength)
StartTracking / AddCorrectionKeyframe / AcceptTrackingRange（见 09）
```

所有命令可撤销/重做（命令栈上限 M4 冻结为 100 步，超出时丢弃最早一步；04A E2）；非法命令（越界、重叠冲突）返回 `Rejected` 与稳定错误。

## 3. 片段与拼接（§10.2、§10.3）

- 单视频多片段与多视频拼接使用同一时间线：片段可来自同一或不同源。
- 片段间直接切换，首版无转场。
- 预计输出时长 = 各片段时长之和；预计空间 = 时长 × 预设码率（视频 + 音频）+ 容器开销，标为估算。
- 边界精度：快速拼接时边界只能落在关键帧，UI 明确显示实际起止与用户设定的差异；需要精确边界时走转码。

### 3.1 导出路径选择

| 条件 | 路径 |
| --- | --- |
| 所有片段同源或参数完全一致（容器、编码与 profile、分辨率、帧率、方向、音频参数），且切点在关键帧上（帧率比较容差冻结为 0.01 fps，M4-B1） | 快速拼接（remux，无重编码） |
| 否则 | 转码：按导出预设统一分辨率、帧率、方向和音频参数 |

- 方向：读取旋转元数据，转码时统一为预设方向，快速拼接只在旋转一致时允许；输出不得出现旋转错误。
- 音视频同步：检查每段音视频起始 PTS 与时长差，超出容差（M4 冻结）则对齐（补静音/裁剪）或失败，不静默错位。
- 无音频输入与有音频输入混拼时，为无音频段补静音。

## 4. 手动打码（§10.4）

```text
MaskTrack { maskId, type: MANUAL|FACE|OBJECT, style: MOSAIC|BLUR|IMAGE, strength, enabled,
            avatar?: { avatarToken, scale, offsetX, offsetY, followRotation },   // 仅 style=IMAGE（REQ-ED-07，schemaMinor 1）
            rangeUs: [start, end], keyframes: [ { atUs, region(normalized rect/rotated rect), source: USER|TRACKER, state } ] }
```

- 关键帧之间线性插值区域；用户可增加关键帧修正位置和大小。
- 多个遮罩可分别开启、暂停（enabled=false）、删除。
- 坐标映射：渲染时把归一化区域变换到输出坐标（考虑源旋转、裁剪、缩放、导出分辨率），预览与导出共用同一变换函数，并以黄金图像测试校验。
- 效果实现：Media3 `GlEffect` 自定义着色器（马赛克=像素块平均、模糊=分离高斯、头像=按区域合成带透明通道的头像纹理），预览与导出同一着色器。
- 头像替换（REQ-ED-07，VK-M5A）：头像 PNG 由宿主保存，工程只记 `avatarToken`（`builtin:N` 为 Kit 内置头像）；合成区域 = 跟踪框扩展到头部，再乘 `scale` 并加 `offset`；`followRotation=true` 时按关键帧的 `rollDeg`（双眼连线角度）旋转；头像缺失或解码失败时该区间改用马赛克并在导出警告中注明，绝不输出未遮挡的画面。头像准备（裁到头部、去背景与边缘、擦除/恢复）在 Kit 的 `prepareAvatar` / `refineAvatar` 中完成，模型选型见 15 §2.9（S7）。旧版本读取端遇到 `IMAGE` 按 schema R4 回退为马赛克。
- 安全规则：任何遮罩渲染失败都使导出失败，不能输出被错误宣称已保护的视频（§10.4）。

## 5. 输出 Sink（§11、§17.2）

```kotlin
interface VideoKitOutputSink {
    val capabilities: SinkCapabilities          // sequentialWrite, randomWrite, fileDescriptor, flush, knownFreeSpace?
    suspend fun openTemporary(request: OutputOpenRequest): VideoKitWriteHandle
    suspend fun markReady(handleId: String, metadata: VideoKitExportedMedia): VideoKitOutputToken
    suspend fun abort(handleId: String, reason: VideoKitAbortReason)
}

interface VideoKitWriteHandle : AutoCloseable {
    val handleId: String
    suspend fun write(data: ByteArray, offset: Int, length: Int)
    suspend fun writeAt(position: Long, data: ByteArray, offset: Int, length: Int) // 仅 randomWrite
    fun fileDescriptor(): android.os.ParcelFileDescriptor?                          // 仅 fileDescriptor 模式
    suspend fun flush()
}
```

- MP4 muxer 需要随机写（回写 moov/样本表）或文件描述符。导出前 `checkExport` 按所选预设声明需求：
  - Sink 支持 FD 或 randomWrite → 直接写入。
  - Sink 只支持顺序写 → 使用分段 MP4（fMP4，可顺序写）或先写 VideoKit 私有缓存再顺序复制；采用哪种在 M4 冻结，私有缓存需计入空间预检并在结束后清理。
  - 都不满足 → 导出前失败 `OUTPUT_CAPABILITY_UNSUPPORTED`。
- VideoKit 不能从 token 反推目录；`markReady` 只表示 VideoKit 写完并通过自检，不代表宿主已提交。

## 6. 导出流程

```text
checkExport：能力（编码器、格式）、Sink 能力、空间估算、跟踪覆盖检查（见 09）
  ↓ 通过
EXPORTING：
  PREPARING → (TRACKING 补算) → ENCODING（已处理时长/帧数、输出字节）→ VERIFYING → WRITING_COMPLETE
  ↓
VERIFYING：重新打开输出检查容器可解析、轨道、时长、尺寸、方向与计划一致
  ↓ 通过
markReady → VideoKitExportResult
任意失败/取消 → abort → FAILED / CANCELLED
```

- 导出在隔离 worker 中执行（[07](07_MULTI_INSTANCE_AND_RESOURCE_DESIGN.md) §5.2）。
- 进度：可可靠估计时给百分比与剩余时间；否则只给阶段与已完成量，不伪造百分比（§17.4）。
- 取消：`cancelExport` 在有界时间（M6 冻结）内停止读取、编码与写入，调用 abort，进入 CANCELLED 并发取消确认事件。
- 暂停：Media3 Transformer 不支持可靠暂停，UI 不提供“暂停导出”，只提供取消后重新导出（§11.3）。
- 进程终止：源不受影响；工程状态可从最近 snapshot 恢复；导出任务从头重启；未提交临时文件由宿主按 OutputToken/任务所有权清理。

## 7. 导出结果（§11.2）

`VideoKitExportResult`：outputToken、container/extension、videoCodec?、audioCodec?、width、height、orientation、durationUs、sizeBytes、frameRate?、audioPresent、createdAt、sourceTokens[]、editProjectId、exportPresetId、warnings[]（如“边界已对齐到关键帧”“已补静音”）。

## 8. 首版预设（§29.5）

| 预设 | 容器 / 编码 | 分辨率 | 备注 |
| --- | --- | --- | --- |
| ORIGINAL | MP4 / H.264 / AAC / SDR | 与首个源一致（不超过设备编码能力） | 默认 |
| P1080 | 同上 | 长边 1920 | |
| P720 | 同上 | 长边 1280 | 低端设备推荐 |

码率与关键帧间隔在 M4 冻结；设备不支持的预设在能力报告中标为不可用。

## 9. 验收要点（§26.5）

单视频多片段添加/裁剪/删除/重排；同参数与不同参数多视频拼接；横竖屏、可变帧率、不同音频参数、无音频输入；手动马赛克/模糊与坐标映射；取消、空间不足、权限失败、输入断线、编码器失败、进程被杀；任何失败后源字节与路径不变；不完整输出不 markReady；宿主验证失败后 VideoKit 不提交、不删源。
