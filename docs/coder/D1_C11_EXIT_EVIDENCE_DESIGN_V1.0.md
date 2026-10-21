# C11 退出取证设计与未证限制

日期：2026-10-16；对应 C10-T01、C10-T02。验收门槛不降低；本文件不申请以 trace 替代原始系统 signal 的新判定依据。

## 能证明什么

Android ApplicationExitInfo 原始 reason/status、记录 PID/real UID/时间，以及从该记录 getTraceInputStream 取得的 protobuf 分开保存。status0 仍执行相同有界读取路径。匹配 PID/isolated UID、进程名、任务时间窗的 App trace 可以作为“该系统记录关联的 trace 内声明 signal11”的独立诊断证据；不能证明系统原始 status 已变为11，不能证明预期故障注入完成验收，更不能替代实际死亡、资源释放或第二槽存活证明。

`isSignal(11)` 仍要求系统原始非零 status==11 和允许的 reason；status0 加匹配 trace11 一律 UNKNOWN/FAIL。ARMED 和外部 ADB/raw 从未进入产品取证数据源。非零系统信号与 trace 冲突、错身份、错进程、无效时间、截断/解析失败均不能通过。系统非零信号且没有 native trace 的原有系统信号门槛保留；解释 codec native abort 另要求匹配系统的 trace、SHA 和原有原因白名单，不能凭缺失 trace 放行。

## 采集边界

- 原始系统字段不改写；日志 `signal` 仍是 OS status，新增 trace_source/trace_status/trace_relation/trace_pid/trace_uid/trace_signal/trace_process_sha/trace_sha/verdict。
- CPU 进程名来自首次代次 HELLO，使用隔离进程内 Application.getProcessName，后续不可替换。历史退出记录需匹配该名；legacy 仍按其原 PID/UID/时间入口，trace 还需匹配所选系统记录的进程名。
- 沿用 ExitRecordRules、TombstoneWitness；262144 字节上限、4096 顶层字段、64 signal 子字段、512 字节进程名、64 字节时间、2048 字节 abort 文本。重复关键字段、多个 command_line、错误 wire、无效 UTF-8 拒绝；不将任意堆栈/路径写日志。
- 时间仍为首次收集时固定上界；trace 的带时区 timestamp 必须落在原任务开始至该上界之间。设备时钟跳变或 OEM 格式不兼容会保守失败，不放宽窗口碰运气。
- 最多3次打开 trace，单次收集轮询最多3秒，调用方最多等待4秒。主线程直接拒绝；单线程采集器和1个信号量保留真实在途工作。超时返回 PENDING，不取消并伪称已关闭 InputStream，也不释放该采集器容量。流读可能受系统阻塞，实际返回前后续采集拒绝为 QUARANTINED_PENDING。close抛错标记TRACE_CLOSE_FAILED，强引用保留未证关闭的流且不释放信号量，后续采集为EXIT_TRACE_CLOSE_QUARANTINED；本批不提供自动重试或超时清零。
- 权限拒绝、无 trace、读取失败、截断/超限、解析失败、身份/信号/时间冲突、歧义、系统字段后续改变且未再次验证分别记录。第3次读取后 OS 字段变化只保存新原始字段，并标记 TRACE_SYSTEM_CHANGED_UNVERIFIED，不开第4条流。

## 进程代次与预算

CPU 仍只有2个任务槽。每个任务的首次 Binder/PID/UID 固定，worker 序号从1增长，死亡回调捕获该对象；旧死亡不能写新 worker 的死亡事实。任务终态不接受新的 START、Source 或帧；重复连接也不能再次占有首次连接。首次身份外的 worker 仅认证 HELLO/STOP，绝不发 START、broker、Source token、媒体输入或 FFmpeg 配额，因此不是2槽乘4个解码任务。

MAX_WORKERS=4 是每任务可保留的历史/异常端点记录数，包含已死亡记录，不是并发解码许可。超限设置永久 quarantine，未证明预算不释放；不借超时清零。全局 reservedCpuSlots/globalUnprovenWorkers 和逐代次日志记录可核查。容量溢出不是正常恢复路径，需负责人集中决策。

每次服务 onBind 在返回 Binder 前，通过 Intent 内私有 registrar 同步登记内核提供的 PID/UID 与端点，并链接真实死亡。这覆盖 Android 因 unbind 丢弃 ServiceConnection 回调、但服务 onBind 已发生的情况；额外 worker 立即进入独立停止路径。registrar 不传文件或权限，service 非导出且普通 isolatedProcess。首次实际死亡后异步尽早 unbind，关闭自动重建绑定；所有已派发 framework callback 和登记/停止调用保持在途计数。解除绑定只证明绑定撤销，不当成任何已登记进程死亡。全部登记 worker 实际死亡、绑定已撤销、Source 真实释放、所有回调/RPC/STOP 物理返回后才释放任务槽。

同一 APK 的服务 onDestroy 自杀是收敛动作，仍需所捕获端点的 DeathRecipient 作为死亡证明。若绑定结果不明、端点未登记、连接/HELLO/STOP 阻塞、解绑失败、未知 worker 或记录溢出，保留 quarantine。单个未创建证明只适用于未请求绑定或明确 bind 返回 false，不能从超时或 unbind 推导。

## 证据层级与剩余限制

本机 WorkerGenerations/TraceCapture 反例不等于 Android Binder 竞态。新增真实隔离额外端点、HELLO/取消、重复连接与旧死亡重放测试只编译，设备 NOT_RUN。额外端点调试用例不启动媒体，其 STOP 故意挂起以验证旧死亡不能释放预算，并要求第二任务继续真实解码。

实际 Android 服务重建、系统 callback 派发顺序、OEM trace 可见性/时间格式和真实收敛仍须整批设备证明。本批不能宣称所有可能的系统在途创建已实测排除；若日志出现 binding_closed 后未知登记或新的进程，不得以旧的 slot_released 结论放行，应判生命周期失败、停止调度并核查。C10-T02 的设备闭合尚未证明。手机 C10-ENV01 不绕过，signal0 同条件不重复重跑。D1 未通过，不进入 M0。

## 来源

Android SDK 36.1 本地 `android/app/ApplicationExitInfo.java` 的 API 文档说明 getStatus 是退出码/信号，API31 native trace 使用 tombstone protobuf，且全局环形缓冲可导致 null。解析字段按 [AOSP Android12 tombstone.proto](https://raw.githubusercontent.com/aosp-mirror/platform_system_core/android-12.0.0_r1/debuggerd/proto/tombstone.proto) 的 timestamp4、pid5、uid7、command_line9、signal_info10、abort_message14；独立编写有界解析器，没有引入新的 protobuf 依赖或 crash handler。
