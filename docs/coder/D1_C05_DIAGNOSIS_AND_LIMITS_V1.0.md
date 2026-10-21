# C05 诊断事实、方案与限制

日期：2026-10-05。C04平板23方法20PASS/3FAIL；C05设备全部NOT_RUN。三项均未关闭，下面区分静态明确缺陷、原设备事实与新方案。

## 普通broker与真实媒体故障

C04普通IsolatedWorker的SIGSEGV分支调用Process.sendSignal后返回true；原日志mode2之后RPC_DONE、普通返回结果断言失败。HANG在同一循环后面，因此被前面的断言遮蔽。这是明确的控制流/覆盖缺陷，但没有旧进程完整信号原因记录。C05独立方法各自有NORMAL控制，native分支同步raise本进程SIGSEGV、永不回复成功；不改已有不同UID companion的sample后SIGSEGV路径。

通过必须有同步ARMED、未返回结果、实际Binder death以及本task PID/isolated UID/开始时间匹配的OS signal11。cleanup SIGKILL、进入mode、泛化IOException、系统历史记录缺失都不能代替。finally执行Source实际账本与死亡检查，记录释放未知。native适配静态编译仅证明ABI/符号，不证明平台实际信号语义。

## ordinary codec死亡

C04回报WORKER_DIED且没有足够的isolated native原因日志。C05同步记录lease/create/release阶段；仅codec API本身的Java异常分类为调用失败，协议ACK异常不冒充codec cause。可观察native abort的严格条件为CREATE_BEGIN后死亡、匹配系统SIGABRT、匹配tombstone PID/UID/signal和已知具体abort原因。当前allowlist只识别“Binder driver could not be opened”，输出固定BINDER_DRIVER_OPEN_FATAL与trace SHA，不保留任意abort正文、路径/线程栈。该原因也不被改名为“已证codec权限拒绝”。C04没有这条原因，不能将它写成既成根因。

[ApplicationExitInfo官方API](https://developer.android.com/reference/android/app/ApplicationExitInfo)说明realUid对isolated进程是实际内核UID，packageUid是安装UID；API31提供native tombstone protobuf，记录/trace可能因循环存储丢失。采集匹配PID、realUid和启动时间；3秒轮询、4秒外层等待、单采集槽。native/Binder读取卡住时不虚构取消，保留单槽pending，不继续积累线程。trace最多接受256KiB、字段/长度/varint受限，异常保持UNKNOWN。

[AOSP tombstone schema](https://android.googlesource.com/platform/system/core/+/c89dd8594e4a9dcf859fdc1ca69d9a194a1c7b26/debuggerd/proto/tombstone.proto)公开pid/uid/signal_info/abort_message字段；本项目仅自编写小型有界字段读取器，未复制protobuf实现或引入新库。[AOSP Binder ProcessState](https://android.googlesource.com/platform/frameworks/native/+/d1490b2/libs/binder/ProcessState.cpp)包含该fatal文本，只为allowlist研究依据，不证明此平板C04曾触发它。其他错误文本待原始证据审查，当前不会宽泛匹配“codec”或“permission”来让未知死亡通过。

Java typed cause或已解释native abort只描述具体失败事实。AVAILABLE、RELEASE_UNKNOWN、bind/ACK失败与unknown death均不算符合预期结果。predicate失败仍独立检查Source消费者/操作、实际死亡、Linux flock独占可得后abort及无READY/token；未知lease/FD保持quarantine，不能删除材料。普通broker仅宿主输入账本，真实编码worker另有Writer FD/lease，二者不混淆。

## AVI指定时间帧

原AVI在retriever侧width/height null、10秒scaled/unscaled均空，两generation released=true；MP4控制非空，而Media3播放AVI成功。这支持“平台取帧容器支持不同”的推断，尚未定位native根因。C05保留直接AVI请求，只在稳定空帧错误后改用既有已审查Media3 Transformer解析/解码原AVI。

请求10秒映射为原AVI9～12秒片段，H264256×144/AAC 3秒转码；经过与正常导出相同的独立双轨、严格PTS、完整视频decode、fsync/READY门禁，然后在该片段请求1秒OPTION_CLOSEST。映射为9秒+1秒，未请求原片0秒；FrameWindow保留微秒余量并拒绝溢出。输入URI仍为AVI，MP4只作为控制和实际AVI产生的中间结果，不能直接用原控制片替代。

转码可有损且retriever不返回原视频实际frame PTS，因此actual_source_frame_pts=UNKNOWN；请求映射不能证明精确原帧或检测/跟踪质量。先实际返回非空再调用检测，quality=NOT_RUN。输入与转换/主线程等待分别受预算控制，但单次native无法硬中断。新片段和.task保留证据，缓存最多两份记录、未知资源保留，达到预算需负责人审查，不自动清理。Transformer cancel返回与所有graphics/native资源已释放不是同一个事实。

若该AVI不能由现有Transformer完整处理、验证或取帧，仍明确BLOCKED，不删除AVI要求。没有添加外部解码器/GPL/FFmpeg/权重。适合闭源的外部decoder必须单列来源、固定配置、许可证/对应源码或商用再分发/SDK授权、替换能力及专利审查，不能借本次实验默许准入。具体条件继续参照冻结D1_C04_ISOLATION_AND_AC3_OPTIONS_V1.0.md；目前未批准任何新增替代依赖。

## 产品与设备范围

host Debug取帧/转码仍不是最终权限隔离流水线；额外companion只批准D1实验，单App/独立Kit普通isolated CPU边界、已许可decoder/模型、性能/TOCTOU/恶意媒体/OOM及P0仍未完成。同UID多进程不提供权限隔离。手机AVI/SRT挂起、MKV AC3无声及Windows实际fixture传输仍须同机验证；平板声音正常不代替手机。
