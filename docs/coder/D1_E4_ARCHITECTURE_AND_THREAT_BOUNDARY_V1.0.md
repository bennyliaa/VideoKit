# D1 E4 单 APK 媒体执行进程与威胁边界 V1.0

2026-10-17。本批是 Android Debug 可行性原型。D1 未通过，M0 未启动，原文全部 P0 与验收阻断条件保持。本文按 [E4 开发需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E4_CODER_REQUIREMENTS_V1.0.md)记录实现边界；本机编译和 JVM 规则检查不能证明 Android 硬件 codec 可用、进程死亡处置、权限隔离或资源实际归还。

依据为[原文 §27/29](D:/CodexProjects/VideoKit/docs/VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md:1021)、[既有 J01–J11 与 F/O 分栏](D:/CodexProjects/VideoKit/docs/coder/D1_R2_NATIVE_FAILURE_GATE_PLAN_V1.0.md:19)、[C14 六帧边界](D:/CodexProjects/VideoKit/docs/coder/D1_C14_PIPELINE_BOUNDARY_DESIGN_V1.0.md)和[项目既定决定](D:/CodexProjects/VideoKit/docs/PROJECT_DECISIONS_AND_EXECUTION_V1.0.md)。E3 的真实有限 IO 通过只覆盖它自己的工具和授权样本窗口，不替 Android 媒体执行进程提供证据。

## 1. 批次与权限决定

本批在 `docs/coder/d1e4` 建立独立 Gradle 工程，只包含一个 app 模块和同一安装 APK。没有新增 companion 安装包，不改变根工程、C14 源码、C14 冻结、既有结果和设备调度。新 APK 内不沿用历史 companion 的跨包查询或绑定权限。CPU 解析闭包、受限 FFmpeg 原生库和 NOTICE 由 C14 按逐文件来源身份复制；对应源码、库、APK 与来源关系由本批冻结清单约束，不能因为来源叫 C14 就把新组合视作已测。

压缩输入及压缩输出验证继续放 ordinary isolated UID 的 C14 `CpuIsolatedService`；进程名前缀保持 `:d1_cpu_worker`，以匹配复制的原 `CpuTaskClient` 身份检查，不为实验名改动原 CPU 协议。系统编码、Image/Plane、Media3 fMP4 封装及其执行链移至 `E4CodecService` 的 `:e4_codec` 受控进程，`exported=false`，与本 APK 宿主同 UID。这个进程隔开地址空间，提供待实测的崩溃边界；它仍拥有宿主 UID 的权限、私有目录访问能力及同 UID 的一般能力。Binder 身份检查、有限协议和不传路径不构成针对同 UID 已被攻陷进程的权限/RCE 隔离。未建立内核级任意文件禁止、凭据撤权或完全沙箱，不以“系统 codec”抵消此风险。

最终 APK 的实际清单只有两个 service，均 `exported=false`，CPU 为 `isolatedProcess=true`，codec 为非 isolated。合并清单的应用权限只有 Media3 common 带入的 normal 权限 `android.permission.ACCESS_NETWORK_STATE`；没有 `INTERNET`、companion package query 或 companion 绑定权限。host 和同 UID codec 具有查询网络状态的应用权限，ordinary isolated CPU 不继承应用权限。不能称“无网络相关权限”；无 INTERNET 也不撤销其他同 UID 数据/系统能力，不构成 RCE 隔离。最终 DEX/native/签名/权限实物与 [APK 审计](D:/CodexProjects/VideoKit/docs/coder/d1e4/evidence/apk-audit.json)绑定。

只有新六帧管线迁移到这个机制。旧 C14 宿主 Media3、旧双轨 `MediaExtractor` 验证、字幕/图片/显示/音频及未来跟踪 GL 的危险链仍按原位置和缺证追踪，不能由新编码 service 一并覆盖。

## 2. 数据面与 owner

| 环节 | 实际进程 / UID | 输入信任和授权 | 资源 owner 与关闭事实 |
|---|---|---|---|
| Source 授权及读取 broker | 新 APK host，普通宿主 UID | 宿主授权的只读 Provider；压缩字节不可信。路径、NAS 凭据和宿主数据库类型不进入帧/codec 协议 | host 持原 Provider/读句柄、已接纳 read/close 及回调；取消、CPU 死亡、Binder 解绑均不能直接把这些账项归零 |
| demux/decode/sws | 同 APK `CpuIsolatedService`，ordinary isolated UID | 只按原任务 broker 读取有限压缩字节；继承 MP4/H264、AVI/MPEG4 白名单与原 quota | CPU worker 持 FFmpeg/context/frame，host 保留 broker/槽。原进程实际死亡只消除其地址空间内引用，不能证明 host 句柄/在途 provider 调用已结束 |
| 原始帧交接 | host → codec service，原生 Binder；不经过 Dart/Flutter | 固定 256×144 / RGBA8888 / stride 1024 / 147456B / rotation 0；task、epoch、generation、service instance、序号、PTS、长度及 alpha 全检 | `E4Protocol.Frame` 持有不可变受控副本；`E4Broker` 队列只保留 2，消费者在途 1。帧归还与实际编码输入操作完成分开，不因发送/取消就丢 owner |
| 枚举/配置/编码/Image | `:e4_codec`，与 host 同 UID | 只收有界裸帧与有限配置，不接收原压缩源路径。平台 metadata 和 Plane 布局也须限界校验 | codec owner 线程串行持 MediaCodec/Image/转换 buffer 与 native call。取消仅发意图；未返回调用、close 异常或未证 ACK 保留 PENDING/UNKNOWN 及许可 |
| fMP4 / 授权临时 Sink | `E4CodecSink` 在 codec owner 内持 muxer、获授 FD、sync dup、worker lease；host `FencedTask` 保留目标权威 | 只传临时 Sink FD、lease FD 和有限 epoch，不传路径；单输出上限 2MiB；没有源写入、移动、删除或业务 COMMIT 方法 | host 原 FD、Binder 接收 dup、sync dup、AutoClose stream/channel 和 worker lease 分别关闭；`fsync` 只记录 OS ACK。执行进程死亡不替 host 关闭资源 |
| 输出独立验证 | ordinary isolated CPU，重新授权只读 broker | 编码后的容器仍不可信；必须解析/完整 decode 到 EOF 并验六帧、PTS、画面 | validator 的读取/关闭/回调/实际退出和源/输出 lease 都要排空；不能调用旧宿主 `AndroidOutputValidator` 代替 |
| 低频控制/结果 | host / service Binder，同步有限请求及 callback ACK | 核原 Binder UID、原 endpoint/instance、task/epoch/generation；PID 仅作一致性观测，消息内自称身份不可信 | 原 host UID/instance/magic ACK 实际返回后才扣 callback 调用；后续 QUERY 须 callbackInFlight=0 且 callbackUnknown=false。旧代不领取新资源或提交新结果 |

host 仍运行 C14 `AndroidLease.exclusive` 的受控 FD `flock/unlock` JNI，操作本 APK 私有输出 lease 元数据，不解析压缩媒体。它是 J06 明确保留的宿主 native 调用；host 的文件/同步/Binder/ART 等平台 native 路径也没有因此消失。本批不声称 host 为“零 JNI”。

上表是关闭判据而非设备通过结果。实际 runtime 类、调用链和有限状态由本批 source manifest 及[交付报告](D:/CodexProjects/VideoKit/docs/coder/D1_E4_DELIVERY_V1.0.md)绑定；不能只凭 `E4Broker` 的计数等于零宣称系统 FD、codec、RSS 或 GPU 已归还。C14 复制闭包与 7 个原 native 库及 NOTICE 的来源关系见 [upstream-copy-map.json](D:/CodexProjects/VideoKit/docs/coder/d1e4/evidence/upstream-copy-map.json)；新 APK 不编入旧 `MediaExtractor`/legacy pipeline/companion 闭包，旧源 ZIP 只作为对应源码归档。

可审入口为 host [E4Session](D:/CodexProjects/VideoKit/docs/coder/d1e4/android/com/videokit/spike/e4/E4Session.java)、原 CPU 适配 [E4CpuAdapter](D:/CodexProjects/VideoKit/docs/coder/d1e4/android/com/videokit/spike/c14/E4CpuAdapter.java)、[service](D:/CodexProjects/VideoKit/docs/coder/d1e4/android/com/videokit/spike/e4/E4CodecService.java)、[encoder](D:/CodexProjects/VideoKit/docs/coder/d1e4/android/com/videokit/spike/e4/E4Encoder.java)、[Sink](D:/CodexProjects/VideoKit/docs/coder/d1e4/android/com/videokit/spike/e4/E4CodecSink.java)、[有限 wire](D:/CodexProjects/VideoKit/docs/coder/d1e4/android/com/videokit/spike/e4/E4CodecWire.java)和[规则/owner 账本](D:/CodexProjects/VideoKit/docs/coder/d1e4/src/com/videokit/spike/e4/E4Broker.java)。`E4CpuAdapter` 复用 `CpuTaskClient.PIPELINE_FRAME` 与 `VERIFY_OUTPUT`；host 只做字节摘要、PTS/小画面结果核对和授权，不调用压缩源/输出 parser。

## 3. 六帧与有界状态

正常路径只允许六个真实源 snapshot 串行接续：复用 C14 CPU 任务取得原始解码 PTS，host 检查帧身份后送入有界队列，codec 完成六个输入及实际样本，关闭 writer 和 codec，再由 ordinary isolated CPU 验证完整输出。原始时间基及严格递增 PTS 保留，编码 PTS 由首源 PTS 归零，不以名义帧率伪造源时间。不以合成图案、仅“格式可打开”或六次消息接收替代六个真实帧。

`E4Protocol` 固定 6 帧、queue 2、encoder 1、256×144、每 RGBA 147456B、单输出 2097152B。`E4Broker` 的任务记录总上限 16、未释放活动任务上限 4、每任务资源记录上限 24、owner operation 上限 8；这些只是有限账本与拒绝条件，不是允许创建 4 个 encoder。全管线仍只有一个编码许可，CPU 沿用宿主域 2 槽。

新跨进程帧路径不能直接复用 C14 原 8 份 RGBA 上限。`E4Session` 每帧串行等待实际消费 ACK 后才取得下一帧；CPU result/受控 packet/sample、host `Frame` 和 wire clone、service Bundle/`Frame`/queue/消费者复制按保守至多 16 份可达 RGBA 计 2359296B，另 YUV scratch 55296B。主帧 Parcel 一次至多 196608B，callback Parcel 至多 16384B，service ingress 一次 1，源、主帧与控制并发分别受已有许可/有界 executor 限制。这个保守声明约束项目可达数组和提交大小，不包括 ART 尚未回收对象、Binder/系统 codec 内部副本、驱动池或全进程 RSS；实际 Android 内存与所有原生缓存仍须设备观测。不能把 queue 2 推导成仅 2 份内存。

能力查询不是 encoder ready。至多沿 C14 四提案协商；上一候选的 codec/Image/creating/owner calls 实际清空后才允许下一候选。E4 BEGIN 已携带获授临时 Sink/lease FD，随后 owner 才查询能力；能力拒绝不启动源 producer、`E4CodecSink.open`、muxer 或媒体写入，但 host 可能已经创建空目标及授出 FD，它们必须实际关闭，不能声称这一分支“FD 从未创建”。已选 configure/start 异常保留阶段和首次错误。运行期错误不自动重选。首因、cleanup 和系统原 reason/status 分开记录。

`E4Broker` 的 `NEW → ACTIVE` 只表示已接纳有限工作，`OUTPUT_CLOSED` 仍不是 READY。NEW 也可登记已产生的资源，避免配置前 owner 丢账；能力拒绝时这些 owner 必须已经实际归还。`createHost` 的 host 账本禁止拥有 ENCODER/IMAGE 或 codec 消费队列，`forwardedFrame` 只计接纳转发，不伪计真实编码；`remoteOutputClosed` 单列原认证 service 的远端证据及 `remoteEncoded`，host 自己的 Source/Sink/操作另行真实关闭。

READY 必须六帧接纳/实际编码、队列和在途归零、源/encoder/Sink 实际关闭、输出字节有限、隔离验证通过并完成其归还。`validatedOutput` 的纯 Java 规则不能独自认证 Android isolated UID；真实 adapter 必须使用原 CPU 注册/回调 Binder 的内核身份及实例，而不是相信 caller 提供的整数。

codec callback 已改为同步事务，host 只验证和保存有限 metadata，然后返回有 magic、原 host UID、原 service instance 的 ACK，不在回调中等 owner/执行媒体 IO。依据 [Android Binder.getCallingPid 文档](https://developer.android.com/reference/android/os/Binder#getCallingPid())，oneway 不提供发送者 PID；即使同步返回 PID，它也只用于一致性观测，不作为安全主体或独立实例认证。授权主依据仍是原 Binder UID、原 endpoint/instance 与完整 task/epoch/generation。sender 必须实际收到 ACK；最后事件内 callbackInFlight=1 不是已归还，host 要在 ACK 返回后的独立 QUERY 取得 0 且无 callbackUnknown 才认可远端关闭。回调停住、拒绝或 ACK 未证保留原 event/owner 和 UNKNOWN，不复用许可。

readiness 只向同一个原 Binder 作至多 51 次 HELLO，在 5 秒准入窗口内等待 owner；正常收尾至多 21 次 QUERY、取消收尾至多 101 次 QUERY，间隔 50ms，分别是名义约 1 秒和 5 秒的有限 metadata 观察。不重建实例、不刷新基线、不领取新许可。这些轮询界限不取消已经进入的同步 Binder/native 调用；调用未返回仍为在途/PENDING，不能写成硬时间内必返或已释放。

## 4. 取消、死亡与重连

取消撤销新帧和新写授权，清掉仍属于队列的帧；已交消费者的 `FrameLease`、已接纳操作和真实资源留在原 owner。只有实际 owner 线程完成 close 并成功返回，才能解除对应引用。close 抛错或停在 native 内保留原对象和 UNKNOWN，禁止 GC 补释放、跨线程强行 release、释放许可后新建，或靠新任务 ID 规避未知资源。

service 原实例 Binder death 只影响匹配 `serviceInstance` 的任务。host 记录 `WORKER_DIED`，cause 缺证仍为 UNKNOWN，并保存系统原 reason/status 和 trace 状态。不能从 Debug 注入名、ARMED、外部 raw 或成功清理补成 SIGSEGV。已经存在的另一真实 CPU 任务须保持自己的源、账本和许可并真正完成，不能用空闲线程、假心跳或全局归零替代。

重连必须新 service instance 和递增 generation；task/epoch/generation/instance 的旧消息均不能更新新代。新代围栏只停止旧命令接纳，不会消灭旧 native 调用、FD 或 Provider 的事实。原代未证资源保留 UNKNOWN/PENDING，不因新实例注册而复用其许可。服务进程同 UID 不妨碍 host 在同 UID 域受到被攻陷 worker 的影响，这不是死亡功能验证可以消除的风险。

本批 `probeReplacementRejectsOldIdentity()` 只在原 death 已观察、原 owner 已返回且旧 binding 已结束后执行 metadata 重连：HELLO 核新 instance/新 generation，再确认远端旧 QUERY 和本地旧结果被拒绝。它不 BEGIN、不授 Sink、不启动新 encoder，也不释放原 UNKNOWN encoder 许可；不能把这个探针称“新任务已经恢复编码”或旧资源已经回收。

Debug fault 仅编译于本批自身 service 的受控路径，必须匹配原调用者与原任务阶段；本机不执行 native crash、进程杀死、设备权限/线程压力实验或 ADB。JVM 自检包含受控并发 close 未返回的规则检查，使用 JVM 线程不等于 Android/OS 资源压力或实际 native 关闭证明。`self-kill-arm/commit` 与 `native-segv-arm/commit` 分别要求已启动原 Session、一次 UUID arm token、原 Binder host UID、PID 一致性和当前实例，延迟执行前重新核对同一 Session/未关闭/未取消，防旧代计划杀掉新任务。native hook 另核 Debug 和 `:e4_codec` 自身进程，只调用本进程，不接收任意 PID。

`capability-deny` 是明确的 wrapper 能力拒绝对照；`configure-first` 是实际配置后的受控 Java 异常；`close-unproven` 是实际 release 后扣留/拒绝 ACK 的保守处置；`owner-pause` 只作有限延迟。它们不证明真实不支持、厂商 native crash、硬件 release 失败或 OOM。原生自故障也只证明受控阶段的故障处置，不表示发现媒体漏洞。所有这些新入口设备均 NOT_RUN。

BEGIN 发送前先落账 `transferAttempted`。拒绝时未接管 FD 仍须真实 close 并返回显式 `rejectedGrantCloseProven`；host 不能凭 `descriptorAdopted=false`、无回复或 `workerLeaseClear` 推断远端 FD 从未产生。已接管则必须有实际远端关闭/ACK/QUERY 证据；转递未返回或关闭未证时原 FD/owner 与许可继续保留。拒绝 close 异常保留原 PFD/Bundle 的有界强引用并锁住 admission，HELLO 也返回 PENDING，不能继续创造资源。host Sink/目录 sync 采用先保留 holder 再分配的两阶段所有权；构造/打开/目录同步异常仍保存原对象和 FD，UNKNOWN 不因构造未完成而丢账或复用。

本批独立设备计划按“正常前置 → 独立反例 → host/另一真实任务 → 全部资源”执行，实际批次由负责人另派；无正常前置就 BLOCKED，不循环重跑求理想 signal。

## 5. J01–J11 逐调用更新

“代码迁移”只表明新机制存在，不等于危险链已关闭。下面实际证明列在本批交付时全部保留设备 NOT_RUN；历史支持只适用于原设备、原任务和原地址空间。

| ID / 原调用 | E4 新路径的进程 / UID / owner 与输入 | 权限和故障边界 | 必须取得的实际资源/结果证明；残余 |
|---|---|---|---|
| J01 Media3 Source/Extractor/AssetLoader | 新六帧路径不用 host Media3 源解析；ordinary isolated CPU 读压缩源。旧 C14 `MediaEngine` 仍在旧 host | 新路径 parser 与 host 地址空间分开；旧 host parser JNI 不因 E4 迁移获通过 | CPU 解码实际返回/退出，broker 每份 source/read/close/callback 排空。正式 Media3 播放、字幕与任意格式 source-loader 路线仍 OPEN |
| J02 `NativeCpu.decode/decodePipelineFrame` → FFmpeg | 复制的同 APK ordinary isolated CPU；原 broker 授字节，worker 持 parser/codec/sws/frame | isolated UID 减少 app 权限；受限协议不是抵御任意 worker RCE 的完整结果真实性证明 | 六个真实帧、源 PTS/内容、原 worker/Source/槽归还另证。旧 C12/C13 结果保留，E4 不重跑未变 CPU 信号条件；全媒体/恶意输入/全进程 RSS 仍未证 |
| J03 CodecList/Capabilities | 新 `:e4_codec` 的 encoder owner 查询并限界 metadata | 与 host 分地址空间、同 UID；系统/vendor 查询仍可能阻塞/分配/abort | 真实枚举及每个 native call 返回、取消/死亡后 host 与他任务及许可。不是查询成功就证 codec 可用，也不消除全系统服务故障 |
| J04 MediaCodec create/configure/start/input/output/EOS/stop/release | 新 codec service owner，输入仅校验后的固定裸帧；最多四提案、encoder 1 | 新机制可待证阻止该进程 native crash 直接终止 host；同 UID 权限风险保持 | 实际六输入/六样本、选中配置、逐候选真实 release 和 creating/call 清空；真实原实例故障命中/host/他任务/资源仍 NOT_RUN。返回异常不冒充 native crash |
| J05 Image/Plane/close | 新 codec service 持 Image 和转换 buffer；平台 stride/pixelStride/base/limit 不可信假定 | plane 越界检查限制复制；本进程 native fault 与 host 地址空间分开但无权限沙箱 | 实际所选色格式/Image 路径、padding/边界、Image 真 close 与原帧 lease；未进入的 Image 分支 NOT_RUN，ByteBuffer 分支成功不能覆盖它 |
| J06 fMP4/stream/sync/lease | `E4CodecSink` owner 持 muxer、sink/lease FD、sync dup/stream；host `FencedTask`/`AndroidLease.exclusive` 持自身授权/事务/元数据引用 | 编码/封装迁出 host；host `flock/unlock` lease JNI、文件/Binder/运行时 native 仍在 host，不能称全 J06 已隔离 | 每份 stream/FD、write/flush/close/fsync 与 output lease 实际归还；关闭未知禁止 READY。host 极小 lease JNI 未有本批实际 fatal containment 证明。OS sync ACK 不是掉电/目录事务持久性，也不是同 UID 恶意 FD 撤权 |
| J07 输出验证：FFmpeg / 旧 MediaExtractor | 新输出只用 ordinary isolated CPU 六帧 EOF 验证；旧双轨 host validator 留在 C14 历史 | 输出仍不可信；隔离 parser 不把旧 host validator 变安全 | 实际 encode 产物、完整 EOF/PTS/画面及 validation read/close/退出归还；receipt 绑定原任务/代次/输出，不能复用旧 true。多轨/任意容器验证仍 OPEN |
| J08 SRT/Media3 字幕/字体 | E4 不接字幕；旧 host 字符/字体/绘制位置未迁移 | 新 codec service 不隔离字幕解析或 native 字体渲染 | 真实时序/错编码/限制/取消、parser/render/Surface 资源及致命故障边界仍 OPEN；SRT 文件存在或旧正常截图不是门禁关闭 |
| J09 Bitmap/Image/FaceDetector | E4 不接压缩图片或 FaceDetector；旧 host 图片/模型路线保持 | 不可用本编码 service 证明图片 parser/平台 native 模型权限或崩溃隔离 | 图片维度/坏图/取消/bitmap/native refs/source 归还和合法完整产品路线未证；模型权利、质量和最低设备仍 OPEN |
| J10 跟踪/遮罩/GL | E4 无正式 tracking/model/GL owner；自有模板不等产品链 | 未实现机制不能标已隔离；不新增模型下载或普通 isolated GPU 探针 | 真实 ROI/LOST/修正/旧 revision、模型权利/效果及 GL 资源/故障计划另审，保持 BLOCKED/NOT_RUN |
| J11 Surface/Texture/AudioTrack/焦点/Flutter | 新路径不创建 Surface、Texture、AudioTrack；视频输出无音频，Flutter 只保留未来控制设计 | encoder service 与显示/音频 owner 不同，不能覆盖 host graphics/audio JNI 或驱动故障 | 真实截图/声音、Surface generation、audioEpoch、旧帧拒绝、producer/texture/PCM/track 实际 stop-release 均未证。没有准入 PCM decoder 路线，不能扩 FFmpeg 音频白名单求通过 |

## 6. Android 手机/平板与未来 adapter

Android 当前目标 API31+、ARM64。Android 12 手机和平板分别记录系统/OEM、CPU/GPU、codec 名称与硬/软属性、尺寸/颜色/对齐/格式查询、选中提案、实际配置和释放；一台的支持不能外推另一台。进程机制不依赖屏幕尺寸；手机/平板的窗口、分屏、字体、UI、旋转和热/内存矩阵仍是后续产品验收。本批没有 UI/Surface/音频或横竖屏产品实现。被系统禁用、权限、磁盘或 codec 不支持按现场事实记录，不卸载清数据、换包名或改系统策略绕过。

Kit 的普通 host 提供 Source、临时 Sink、authority 与有限资源预算，服务命名和授权不能要求 Browser/SMB/Room/业务表存在。内部 Maven group `com.videokit`、SDK namespace `com.videokit.<module>` 与 App `com.videokit.app` 是既定方向；本实验包/Java 名字不是正式 artifact、公开 API 或兼容承诺。独立 AAR 的 manifest 合并、服务命名避免冲突、同一进程多 Kit 实例、跨宿主预算、binding 版本、移除 Kit 后降级启动仍须 M0/M7 实现与验证。帧不经 Dart，正式 Flutter engine/texture 生命周期未实现。

iOS/macOS 只设计 AVFoundation 薄 adapter、原生 owner/lease 与有界帧，不能假设 iOS 可以任意创建本原型式子进程；若实际 native fault 拖垮 host，原 §27 阻断仍成立。macOS 的可用受控辅助进程/权限设计另审，不能由 Android 同 UID service 直接复制。Windows 只设计 Media Foundation 与受控 worker/C ABI；进程 token、句柄复制/撤权、路径/网络权限、崩溃观测和原实例恢复均另证。本批不实现、不构建、不以缺少这些设备阻断 Android 本机准备，也不宣称已支持它们。

## 7. 当前结论的限度

E4 提供新的单 APK 编码执行机制、有限协议及后续可独立验证的故障位置。最终离线 Android 编译和有意义 JVM 规则自检已通过，首次失败和必要修复记录保留；仍不能把源码、APK、JVM mock owner 或编译通过计作真实 codec/隔离/清理 PASS。依赖图是本最小 APK 减少后的 35 个坐标，14 个 GA 的所选版本有差异，新增 GA 为 0；Media3 1.9.3 和复制的 7 个 FFmpeg/JNI/lease 原 native 库不变，不声称整个依赖图字节不变。精确版本变化见 [SBOM 差异](D:/CodexProjects/VideoKit/docs/coder/d1e4/evidence/sbom-difference.json)和 [SBOM](D:/CodexProjects/VideoKit/docs/coder/d1e4/evidence/sbom.json)。历史 C13 self App 原始 signal0 严格 FAIL、外部 raw11、另一方法 signal11、trace 缺失/ordinary UNKNOWN 分栏保持；C14 73 可调度项和两项 `NOT_RUN_UNCHANGED_PLATFORM_LIMIT` 不改。

完整未决门禁见[剩余门禁评审](D:/CodexProjects/VideoKit/docs/coder/D1_E4_REMAINING_GATE_REVIEW_V1.0.md)。新设备批次必须在整包冻结及独立审查之后由负责人派发，正常真实六帧、另一真实任务前置、受控故障命中与所有目标资源证明缺一不可。原文所有 P0、权限/RCE 风险、显示/音频/图片/字幕/跟踪链和发行条件继续约束正式交付。
