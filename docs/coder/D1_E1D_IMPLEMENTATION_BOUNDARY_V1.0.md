# D1 E1D 实现与证据边界 V1.0

2026-10-16。C01/C02 两项 P1 修复候选已完成 573 项限定合成检查并待独立复审。活动实现是 Python G 中的 SourceAuthority/CompletionHub/Flow，与 J 的 RandomAccessFile 和 R 的 Windows native 绑定；Core.cs 中旧状态类不替代活动路径。

## 裁定、通知、所有权

原操作在 admission 点绑定 task/version/consumer/generation。完成交付不会重新 admit：SourceAuthority.complete 与 gate 都在同一权威锁下检查这个原操作，以及当前 finished/cancelled/sealed、全局和状态围栏、recovered、精确 handle 及 OWNED_OPEN_RETRYABLE。两者都使用同一个 _decide_delivery_locked，cell 锁仅决定一次 outcome。seal/fence 先于该决定时，晚 open 不交消费者，只保留原 H 清理所有权；read 同样保守丢弃。决定先赢后，后来的 seal/end/cancel/deadline 不逆转已定结果。

决定是线性化点，Future 通知是后续步骤，可以存在队列延迟。单一 notifier 在不持 source/cell/Hub/Ledger 等应用锁时调用标准 Future.set_result/set_exception；标准 Future 自身的条件锁由标准库在调用 callbacks 前释放。绑定的 end/cancel 先在权威锁内裁定，释放锁后提交；deadline monitor 也先释放 Hub 条件锁再取消 cell。GC 使用同一 cell 路径，没有独立的锁内快捷完成。

最多 8 个已注册 cell，各预占一次通知信用；排队＋active 最多 8。active 的私有资源释放后，仍保留通知容量至 notifier 返回；同一个 Hub 条件锁内同时清 active/归还容量，避免新注册抢占尚未归还的信用。post 使用 posting 防并发，提交成功才标 submitted；提交异常明确保留 submit_error 并封闭接纳，不自动重试或虚报已通知。

消费者可在决定前注册最多 4 个 callable callback。决定后注册（包括 callback 内再次注册）拒绝 CALLBACK_REGISTRATION_CLOSED，不触发标准 Future 的立即同步回调分支；外部 cancel/set_result/set_exception 拒绝 COMPLETION_OWNED_BY_HUB。这个有界契约收窄了普通 Future 接口，后续产品 API 需明确承接；不能对外宣称完全兼容任意 Future 使用方式。

Future.done 只说明结果/错误已发布。callback 尚在执行时 cell、operation、buffer lease 仍持有；notification_done 只在所有注册 callback 真正返回后成立。释放还要求 native_done 和 gated；release/on_drain hook 在应用锁外执行，唯一 release_claimed 避免重复。hook 或通知异常保留 UNKNOWN/PENDING 和信用，不伪造排空。cancel/timeout 可以先完成消费者响应，但不强制中断 native IO，原同步包装仍可能等待实际 RPC 返回。

交付的 Future 值仅包含对象标识/长度或 base64 字节等普通 Python 值，不暴露 raw native handle 或可重复租用的 native buffer。callback 返回后消费者仍可保存 Future/值；工具只管理自身 cell、原 owner 与 lease 生命周期，不承诺回收外部缓存、逃逸引用、任意 Python 内存。清除 Future callback 列表只移除已返回 callback 的工具侧引用，不等于撤销消费者已有引用。

## 有界执行与异常停止

固定一条非 daemon notifier 和一条非 daemon deadline monitor，无 per-cell Timer、无限通知线程或可增长线程池。默认 callback 观察期限 0.1 秒，cell gate/drain 默认有限等待 0.2 秒；队列中 callback 串行执行，工具无法规定用户 callback 本身必须返回。超时/异常后停止新 transaction/query/RPC 接纳；GC 仍允许对原操作排空。slow callback 不能通过 Future.done 或 owner 子进程退出被代写成资源已释放。

GC 开始先有限 drain 已提交/active 通知，再处理原 gate、引用 close 与 helper exit；GC/n31 有限 join Hub 两线程，最终 n32 前核 workersAlive=0/cells=0。drain 本身只等通知队列和 active，不等尚未 native 返回/尚未 gate 的 live cell；close 另查 live cell，不能用空队列推断整体排空。

任意用户 Python callback 挂住时，不强杀线程；非 daemon worker 继续保留其引用与可观察 ownership。controller 保存 PENDING、原 G/helper 身份及 logCloseProven=false，停止新接纳，发出退出请求。stop_when_drained 只是停止请求，不证明任意 live cell 或 worker 已结束。最外层 200 秒停止等待仅记录原 G PID，180 秒预算只约束接纳/等待，不保证任意挂回调或系统 IO 的进程强制退出。

本批受控慢回调均通过 Event 放行后真实返回并 join；没有运行永久挂 callback、真实 native 卡死、强制中断或系统压力实验。线程创建部分失败/启动失败的回收没有注入验证，当前 start 不提供事务式部分启动回滚；这类异常不能据正常回归声称自动排空或资源全部释放。非正常退出仍需查看 PENDING/原实例与实际线程、进程见证。

## 证据能证明什么

153 项新增 completion 检查实际使用生产 SourceAuthority、PendingCell、CompletionHub、标准 Future 回调和 Ledger 逻辑 lease。另一线程对同一权威/cell 的有限屏障访问证明发布线程不持这些锁；计时超限不接受为 PASS。普通/held open/read、单 seal 两种顺序、全局 fence、错绑定、六条回调路径、慢回调、队列延迟、active 交接与提交失败均有真实状态断言。这组不构造 Engine/Native/Channel，不冒充真实 OS 句柄实验。

139 项原权威/owner 检查与 33 项恢复、69 项自有 writer 短写、20 项通用检查保留。writer 只是受控返回异常，不制造真实磁盘故障。完整 61 行回归另有实际 J/R 进程、合成文件、Windows 句柄操作、原实例 wait 与 flush/fsync/close 返回证据；仍是缩小 profile：L=131072B、C=4096B、Z=0、边界65536，未证明真实视频/字幕、解码、2GiB 窗口或 NAS。

恢复 schema3/同身份 admitted inventory/可信 query 日志逐维取 max；缺 shard 或不可信日志仍 UNKNOWN，不能将差额退款。恢复只读、围栏、不重造 raw handle 或 writer。exact_write 对每次有界 write 的实际返回核完整请求，短/非法/异常后 UNKNOWN、无补写、禁新下游；这些 T02–T05 行为未因新 Hub 降低要求。

23/5/1 只指本工具受管资源、媒体句柄和 64KiB 媒体槽峰，包含新 2 个 worker 信用。既有 native pool、管道读线程、临时测试池及 Python/JVM/.NET 的栈、锁、内部句柄、JSON/base64 内存未做完整系统资源测量；不能据此宣称整个运行时真实 OS 总量≤24。requiredDurability、真实 source version/路径替换及断电/命名空间确认仍未证，实际 fsync 返回不等于断电耐久 READY。

控制分配 452/硬 544、101 query、输入 1,573,522B/59 次、目标10/记录32、输出655,360/验证262,144、文件峰信用3,178,496B/硬4MiB、180 秒不扩大。独立开发自检 fixture/log 按2MiB/4MiB累计。没有读取 test_media 或运行真实 PF/媒体/设备实验；JNI BLOCKED、D1 NOT_PASSED、M0 NOT_STARTED 及历史 FAIL/C14/P0 不变。
