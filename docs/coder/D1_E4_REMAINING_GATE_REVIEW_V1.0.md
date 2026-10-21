# D1 E4 剩余架构门禁评审 V1.0

2026-10-17。D1 未通过，M0 未启动，原文所有 P0 不变。E4 是独立单 APK Debug 原型与待审设备计划；Android 本机编译、源/产物身份和 JVM 规则检查只证明对应有限事实，不等于硬件编码、Android IPC/UID 认证、真实资源回收或故障隔离通过。

本评审继承[原文 §27/29](D:/CodexProjects/VideoKit/docs/VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md:1021)、[C14 剩余门禁](D:/CodexProjects/VideoKit/docs/coder/D1_C14_REMAINING_GATE_REVIEW_V1.0.md)、[R2 J01–J11 计划](D:/CodexProjects/VideoKit/docs/coder/D1_R2_NATIVE_FAILURE_GATE_PLAN_V1.0.md)和[本批架构](D:/CodexProjects/VideoKit/docs/coder/D1_E4_ARCHITECTURE_AND_THREAT_BOUNDARY_V1.0.md)。E3 有限 IO 工具通过不改变 Android 这些门禁。

## 1. 本批机制与尚待证明事实

负责人已批准 ordinary isolated 处理不可信压缩源/输出，同 APK 独立受控 codec service 承担系统枚举/编码/Image/封装。本批有记录地实施这个替代，不再把 J03–J06 全部写成“尚未选择机制”。新 service 与 host 同 UID，只有地址空间/崩溃边界，权限和 RCE 隔离仍不具备；同 UID 私有目录、凭据、Binder/系统一般能力无法由有限协议绝对撤销。

最终 APK 实物清单仅有两个 exported=false service，CPU isolated、codec 非 isolated。唯一应用权限是 Media3 common 合并的 normal `ACCESS_NETWORK_STATE`，host/同 UID codec 可查询网络状态，ordinary isolated CPU 不继承应用权限；无 INTERNET 或 companion query/绑定权限。这个权限事实不等于“无网络相关权限”，也不消除 host 残余 JNI 或同 UID 数据/RCE 风险。最终离线 Android build 与 JVM 规则检查已通过，所有新设备路径依旧 NOT_RUN，失败/修复日志不抹去。

JVM 中受控并发 close 未返回的检查只验证规则和强 owner 保留，确实使用 JVM 线程；本批没有设备权限/线程压力、真实 native crash、ADB 或 Android 故障执行。不能把这项规则通过当实际 Binder/native/FD 归还或 Android 并发性能证据。

| 门禁 | E4 新增的可审机制 | 冻结时仍未证明与合法后续 |
|---|---|---|
| 真六帧路径 | CPU isolated → host 原生 broker → typed RGBA queue2 → codec service → 临时 Sink → CPU isolated EOF 验证 | 两真实输入分别取得 6 源/6 编码输入/6 样本/6 验证、真实 PTS 与画面阈值；本机纯规则不是这个结果 |
| codec/Plane 崩溃边界 | 独立 `:e4_codec`、原实例/task/epoch/generation、单 owner 和 Debug 自身 fault 入口 | 必须实际命中该新阶段、host 同进程实例存活、另一真实任务完成、资源和输出无假 READY。普通 API 异常不充 native fault |
| 原因能力 | App 可报 WORKER_DIED 并保留原 reason/status、trace 状态和 UNKNOWN | 不承诺系统提供非零精确信号。严格历史 signal0 FAIL 保持，外部 raw 不回填 App；新功能后果与 O01/O02/O03/O04 分栏 |
| 取消/迟到/重连 | 撤销接纳、帧 lease、在途操作和未知 close 强保留；原 death 后仅 metadata 新 instance/generation 拒旧 QUERY/结果 | 不启动新 encoder、不解除旧 UNKNOWN 许可。实际取消响应、owner 返回、原 Source/FD/callback/codec 归还待设备；仅返回 CANCEL_PENDING 或客户端超时不能通过 |
| 另一任务/共享预算 | CPU2、encoder1、queue2、原代任务账本；死任务不清除其他 task | 故障前另一任务已实际读真实源，故障后真正完成；不能用空闲线程、统一 global=0 或新 host 进程替代 |
| 临时输出/源不变 | 只授本批临时 Sink，不传源写能力；关闭和验证共同约束 READY | 实际 writer/host 句柄/验证 lease/源引用归还及源前后身份内容核对待设备。READY 不等于宿主业务 COMMIT |
| 资源和性能 | 有限帧/队列/许可/输出/日志/等待与未知状态规则 | Android RSS/PSS/VMS、ART/Binder 复制峰值、FD/线程、厂商 codec/系统服务资源、发热/耗时必须实测；逻辑对象计数不是内核量 |
| 一般攻击面 | 不传路径/凭据，限制帧/metadata，ordinary isolated 压缩解析，exported=false | 同 UID codec RCE、已持 FD 恶意不合作、系统/vendor/驱动和 host 残余 JNI 仍未消除；不得因“系统服务”或小尺寸准入整个产品 |

callback 采用同步有限 metadata ACK，主认证为原 Binder UID、原 endpoint/instance、完整 task/epoch/generation；PID 仅一致性观测，不当安全身份。[Binder.getCallingPid 的官方限制](https://developer.android.com/reference/android/os/Binder#getCallingPid())说明 oneway 无发送者 PID。host ACK 的 magic/原 host UID/instance 实际返回后，service callbackInFlight 才可归零；最终事件本身不能证明其调用已返回，host 后续 QUERY 必须确认 0 且 callbackUnknown=false。挂住/拒绝/ACK 未证保留原调用、event/owner 与许可，设备证明仍未取得。

BEGIN 之前登记 transferAttempted；远端拒绝关闭必须有显式 rejectedGrantCloseProven，已采用则须实际闭合证据。“未 adopt”、转递没回复、workerLeaseClear 均不证明远端没有 FD，不能据此 abort/释放许可。Source/Sink 及目录 sync 的两阶段 holder 在分配/构造失败或 FD close 未证时仍强留原 owner，UNKNOWN 不复用。

所有等待只观察原身份：HELLO 至多 51 次、5 秒 readiness 窗口；正常关闭至多 21 次 QUERY、取消至多 101 次，50ms 间隔（名义约 1/5 秒）。不启动新实例刷新基线；同步 Binder/native 未返回时限额不是强制终止或释放证明。`probeReplacementRejectsOldIdentity()` 只是原 death 后核新实例并拒旧身份的 metadata 探针，不开新 encoder，不能计作恢复编码或旧资源归还。

## 2. 原文 §29 十二项

| 项 | 本批事实 / 决定 | 未完成范围与后续里程碑 |
|---|---|---|
| 1 group/artifact/namespace/version | 内部 group `com.videokit`、SDK namespace `com.videokit.<module>`、App `com.videokit.app` 已确认；E4 实验单 APK 身份独立记录 | 实验包不是正式 AAR 坐标；artifact、语义版本/兼容/迁移、服务命名冲突和发行规则待 M0/M7 |
| 2 播放/编辑产物拆分 | 新实验不依赖 Browser 业务，复用原生薄适配/Source/Sink 意图 | api/core/playback/image/ui/timeline/effects/tracking/export/testkit 的真实依赖图、独立构建与可移除 AAR 待 M0/M7 |
| 3 Media3/图片/编码/FFmpeg及许可 | Media3 1.9.3、受限 FFmpeg 8.0.3、7 个原 native 库/NOTICE 来源不扩；最小 APK 依赖减至 35 坐标，14 个 GA 所选版本有差异、新增 GA=0 | 精确差异/锁/SBOM 随包保留，不称依赖图全不变；图片完整路线、发行/再链接/EULA/商店/专利和闭源宿主兼容仍 OPEN，M1/M2/M6/M7 |
| 4 跟踪组件/模型/最低设备 | E4 不下载或引入模型，既有 YuNet/ViTTrack 候选身份事实保留 | 权重/训练/再分发/样本人物权利、真实标注/质量/最低设备和正式高风险执行位置未证，M5 |
| 5 输出容器/编码/质量 | 仍是 6 帧、256×144、无音频 fMP4/AVC，最多 C14 四提案，新 codec service 尚未实机执行 | 硬/软具体设备分列；正式 MP4/H264/AAC/SDR 及分辨率/颜色/HDR/音频质量、持续输出矩阵待 M6；旧 C13 configure FAIL 不改 |
| 6 remux 兼容 | 本批做有限重编码，不声称无损拼接 | 时间戳/edit-list/旋转/字幕/音频/不兼容检测与明确 fallback 待 M6；六帧成功也不证明 remux |
| 7 效果/速度/内存/热阈值 | 六帧/queue2/encoder1/CPU2/2MiB 输出与原 FFmpeg quota，实际副本峰值按源码核对 | 不推导全进程 RSS；Android 12 手机/平板和低端分级、长时/多轨、热降级、跟踪/遮罩效果待 M3/M5/M6 |
| 8 UI/纯引擎组合 | E4 是原生无产品 UI 实验，帧不经 Dart；单 APK service 可由原生 host 控制 | Flutter/Compose/View/engine 生命周期、texture/Surface、可嵌入控件、跨宿主和多引擎验证待 M0/M1/M7/M8 |
| 9 Sink 顺序/随机/FD | 本批只授有界临时 Sink；writer close、隔离验证和源收尾后才可 READY | 通用能力协商/跨宿主 FD 权属/随机写、validation lease、持久 query 和恢复的公共协议仍待评审；OS sync 不等绝对掉电安全，M0/M6/M7 |
| 10 schema/迁移/恢复 | task/epoch/generation/instance 围栏和未知资源保留可审 | 原新进程机制未跑；正式工程 schema/undo/revision/迁移、宿主真实强杀恢复及跨设备范围待 M0/M4/M6；重连不是恢复已完成 |
| 11 控件/主题/overlay | 不更改原文 UI/宿主动作语义；不引 Browser 类型 | 正式布局、无障碍/主题/坐标、叠加同步、图片与遮罩编辑和 Flutter UI 待 M0/M1/M2/M5/M8 |
| 12 共享池/硬 codec 预算 | 单 host 域 CPU2、encoder1、queue2；未证资源继续占用 | 不等跨进程/多 host 全局池。公平性、抢占、多路硬件能力、音频唯一、1/4/9/12 槽与降级待 M0/M3/M7 |

这些门禁没有因本地断言数、源码行数、APK 成功打包或使用同一库版本而自动通过。正式多平台仍属同一完整 V1.0，不能把中间可行性版本作为删减版发布。

## 3. 仍未覆盖的危险链

J03–J05 和 J06 中 codec/mux owner 获得新可测进程位置；实际证明未完成。J06 host `FencedTask` 仍通过 C14 `AndroidLease.exclusive` 的极小受控 FD `flock/unlock` JNI 锁定私有输出 lease 元数据，并有文件/sync/Binder/运行时 native；这不是压缩媒体解析，但没有本批宿主 fatal containment 证明，不能称 host 完全零 JNI。J01 旧 host Source/Media3 与 J07 旧双轨 host `MediaExtractor` 未编入新最小 APK，仍存在于 C14 历史及全产品未闭合路线，不能按“新 APK 无此类”关闭产品需求。后续不能将“编码进程已拆出”替代全 host native 调用清单和 §27 宿主存活要求。

J08 字幕解析/字体、J09 图片/FaceDetector、J10 跟踪/遮罩/GL、J11 Surface/Texture/AudioTrack/焦点均不进入本编码原型。它们的正式进程/owner、合法输入与模型、取消旧代、native/驱动故障和实际归还仍 OPEN/BLOCKED。音频没有准入 PCM 解码路线，不扩 FFmpeg 音频；显示未创建真实 Surface，ByteBuffer 接收不算画面。不能把这四组风险用本 service 或“平台 API 自带隔离”关闭。

ordinary isolated 压缩解码和验证是有限边界，不证明任意恶意输入安全或被攻陷 worker 不会伪造完整验证结果。同 UID service 也不能证明无任意源写入/RCE：本批合作式 API 不提供源写权限，但内核权限边界不存在。若正式风险模型要求强权限隔离，须选择更强机制并独立评审，不能把当前方案措辞升级。

## 4. 原结果与下一设备批次

C14 冻结不改，73 可调度项和两项 `NOT_RUN_UNCHANGED_PLATFORM_LIMIT` 原样保留；不以 E4 同名/新方法覆盖。C13 平板 52 PASS / 3 FAIL / 14 BLOCKED、手机环境阻断事实不变。C13 self SIGSEGV App 系统 signal0 严格 FAIL，外部 raw11 与另一双槽方法系统11各自保留；trace 缺失、ordinary UNKNOWN 继续 OPEN。E4 不修改退出采集算法，不重复未变 CPU 触发求 signal，不新建 crash handler。

本批所有新设备正常、能力、取消、迟到、死亡/重连与资源观测均 NOT_RUN。负责人收到整批源码/APK/签名/SBOM/自检/只读 verify 和[设备附录](D:/CodexProjects/VideoKit/docs/coder/D1_E4_DEVICE_EXECUTION_APPENDIX_V1.0.md)后，先独立静态审查，再正式派有限新设备批次。coder 不 ADB、不轮询设备、不自行派测，不将此前手机/平板连接或 legacy companion 成功当新授权或通过。

设备执行须先确认真实源/只读授权/空间与新进程身份，再正常六帧和另一任务真实在途；前置失败即停止依赖项。新的故障注入只在受控自身 service、已证明阶段和固定任务中一次执行；独立观察原 PID/UID/实例/时间，检查原 host 实例和另一真实任务，然后核目标与他任务分别应有的资源。超时/失联/close 未证保留 UNKNOWN/PENDING；不能强制 GC、全局归零、改阈值、卸载清数据、替换包身份或重跑同条件获得理想原因。

Android 12 手机与平板分别验证，不能一台结果外推另一台；全产品还需原文中间/稳定 Android、窗口/分屏/旋转、字体与语言矩阵。iOS/macOS/Windows 本批只保留 adapter/权限/故障边界设计，实际实现 NOT_RUN；不以缺少这些环境阻断当前 Android 准备，也不称它们已支持。

## 5. 交付与准入结论

本批可以提供供独立审查的新机制和设备计划，不能据此宣布原 §27 会话故障安全、所有 J01–J11、产品源/Sink 协议、Kit/Flutter、性能或发行许可已通过。M0 API/Fake/TestKit/示例 host 尚未完成；M1–M8 与原全部 P0 继续追踪。是否正式派发新设备批次由负责人基于完整冻结和独立审查决定，不由本机编译状态或本文评审自行放行。
