# 07 多实例与资源设计

版本：V1.1；日期：2026-11-06；对应原需求 §8、§16、§21、§26.4。

## 1. 原则

- 多画面 = 多个独立会话，不是一个全局播放器（§8.1）。
- 资源预算由宿主注入、宿主范围生效，不是进程全局单例；同一进程可以有多个宿主范围（例如两个窗口）。
- 先预留、后创建：任何解码器、Surface 大缓冲、模型、隔离进程都先向预算申请，获准后才创建。
- 资源不足时返回可解释的降级建议，绝不循环重试创建解码器（§8.2、§27）。

## 2. ResourceBudget

```kotlin
interface ResourceBudget {
    suspend fun reserve(request: ResourceRequest): ReservationResult  // Granted(lease) | Denied(reason, suggestion)
    fun snapshot(): ResourceReport
}

data class ResourceRequest(
    val sessionId: String,
    val kind: ResourceKind,        // VIDEO_DECODER | IMAGE_MEMORY | TRACKING_WORKER | EXPORT_WORKER | ENCODER
    val estimate: ResourceEstimate,// 分辨率、帧率、编码、是否硬解、字节数
    val priority: Priority,        // VISIBLE_AUDIBLE > VISIBLE > OFFSCREEN > OPTIONAL
)
```

- 默认实现 `DefaultResourceBudget(capabilities, policy)` 由 VideoKit 提供，宿主可替换或配置。
- 估算依据：解码器能力（`MediaCodecInfo` 并发实例与性能点）、分辨率与帧率、历史创建失败记录、热状态（`PowerManager` 热状态）、可用内存。
- 设备声明的最大实例数只作上限提示，不当作可靠容量；实际创建失败会更新历史并降低后续建议值。
- `ResourceReport`：每类资源的已预留、实际持有、消费者列表、未确认释放项，供宿主展示与调试。

## 3. 数量与降级

| 项 | 规则 |
| --- | --- |
| 默认布局 | 宿主决定：手机 4、平板 9 |
| 硬上限 | 视频会话 12，超过时 `createSession` 返回拒绝 |
| 能力报告 | `suggestedHardwareVideoSessions`、是否需软件解码、风险等级 |
| 不足时 | `Denied(reason, suggestion)`，建议之一：减少活跃视频数、暂停离屏槽、改显示静态占位、降低分辨率 |
| 宿主选择 | 由宿主（Browser 的 PlaybackCoordinator / 示例宿主）执行降级并向用户解释 |
| 压力升高 | 先停止可选任务（预取、缩略图），再通知宿主降级；不强行取消其他槽位正在进行的调用 |

图片会话申请 IMAGE_MEMORY，不占视频解码器额度（§7）。

## 4. 唯一音频（§8.3）

- 音频由宿主协调：宿主维护单调递增的 `audioEpoch`，通过 `SetActiveAudio(active, audioEpoch)` 指定唯一发声会话。
- 切换顺序：先让旧会话静音并确认，再让新会话取消静音；epoch 小于已接受值的命令被拒绝（防止旧命令晚到）。
- 默认“最后点击的槽位发声”由宿主实现；用户也可选择某槽为声音来源；选中会话被释放或移出批次后全部静音，等待用户重新选择。
- 系统音频焦点只由当前发声会话申请；会话之间不争夺。锁定优先于一切音频命令。

## 5. 故障隔离

### 5.1 会话级隔离

- 每个会话独立的错误状态；可恢复错误不影响其他会话。
- 共享资源（例如共享的输入缓冲池、模型实例）使用引用计数；一个会话 release 只归还自己的引用，不释放其他会话仍在使用的资源（§16.2）。

### 5.2 进程级隔离

| 任务 | 隔离方式 |
| --- | --- |
| 未知或可疑格式的探测 | 隔离进程中执行，得到结论后再在主进程创建播放 |
| 跟踪推理 | 每个编辑任务一个隔离 worker（受预算限制并发数） |
| 导出编码与效果渲染 | 每个导出任务一个隔离 worker |
| 普通播放 | 主进程（Media3 解码器本身运行在系统 mediaserver/codec 进程） |

- 隔离 worker 使用 `android:isolatedProcess="true"` 的 Service，无文件和网络权限；输入通过主进程代理的读取通道（有界共享内存/管道）获取，输出通过主进程转交 Sink。
- IPC 消息带版本、任务 ID、worker 代次、序号与长度上限；worker 重启后旧代次的回复一律拒绝。
- worker 死亡：只让该任务失败（状态 FAILED，错误 INTERNAL_ERROR_REDACTED 或具体码），主进程归还该任务的资源；不重放、不影响其他槽位。
- 隔离只能通过故障注入（崩溃、OOM、卡死、坏消息）在真机验证后宣称有效；未验证前在能力报告中标记为“未验证”。

### 5.3 可见性与生命周期（§8.4）

| 可见性 | 行为 |
| --- | --- |
| VISIBLE | 正常播放 |
| PARTIALLY_VISIBLE | 可降低帧率或分辨率 |
| OFFSCREEN | 暂停；按策略在超时后释放解码器，保留可恢复状态（位置、轨道、变换） |
| BACKGROUND | 按宿主指令；默认暂停并释放 Surface |
| LOCKED | 隐藏画面并静音，等待宿主指令 |

页面销毁、槽位移除、媒体切换、锁定：最终释放 Surface、解码器、输入句柄与协程任务，见 [06](06_PLAYBACK_AND_IMAGE_DESIGN.md) 第 7 节释放顺序。

## 6. 验收要点（§26.4）

- 1、4、9、12 槽；视频/静态图/动态图混排；每格状态独立。
- 唯一音频源及全静音；epoch 乱序、切换中目标释放。
- 离屏暂停/释放与重新绑定。
- 解码器不足、内存压力、温度升高时稳定降级，不循环创建。
- 单槽故障（坏媒体、worker 崩溃）不影响其他槽；共享资源引用计数正确。
- 多槽长时间运行后资源报告归零。
