# D1 E1E 实现与证据边界 V1.0

2026-10-16。本批仅修 E1D-D01 部分启动异常的围栏、逐 worker 所有权与失败出口，保留已认可 C01/C02、T02–T05 方案；等待整包独立复审。

## 启动状态与事实

CompletionHub 状态分 NEW、STARTING、RUNNING、FAILED、CLOSED。started 仅表示已尝试启动，不能作为可用证明；ensure_accepting 只允许 RUNNING 且没有 blocked/closing/closed。两条 worker 都实际进入包装函数并确认仍存活后才转 RUNNING。第一/第二预留、工厂、start 或 entry 验证异常均先 FAILED＋围栏、请求已启动 worker 停止，有限观察/回收后仍抛原异常。收尾错误另记 cleanupError，不替换原 startupError。

notify/deadline 各自保留 reserveEntered/Returned、creditReserved/Released、Thread 对象及逻辑 threadId、startEntered/Returned/InProgress、实际 entryIdent/nativeId、wrapper entered/exited、joinEntered/Returned/joined、unknown、错误与状态历史。逻辑 ID 不等 OS 线程已存在；alive=False、ident=None、start 抛异常都不能单独证明未启动。包装函数 exited 也不能代替真实 Thread 已退出。

信用按事实区分：未成功预留不退款；确认预留且 starter 从未调用时可以 THREAD_NOT_STARTED_PROVEN 归还；实际启动须原 Thread wrapper 进入/退出、真实 join 返回且 alive=False，才 THREAD_JOIN_PROVEN 归还。两种 proof 仅限 Ledger 的 worker 类型。预留接口在提交后抛错时核原 rid 的前后账本事实；原先已存在或外来信用不据此冒领。没有替换线程、自动重启或重试碰运气。

自有 thread_factory 必须只构造未启动 Thread，不运行 supplied target；自有 starter(thread,label) 才能启动。WorkerNotStartedError 是内部可信接口的明确“从未调用 start”承诺，且仍需没有 wrapper entry/OS identity 等反证才接受。普通异常没有该承诺，即使看起来没有活线程，也保留 UNKNOWN 信用。这个接口是限定合成注入点，不用于将未知系统线程错误伪装成未分配。

close 可重复，序列化有限回收；不 join 未启动或无法确证启动的 Thread。与 start 并发时先封闭、请求停止，启动调用尚未返回就保留 PENDING，不归还在途信用。未知、未排空、join 超时均 Stop，保留原对象、身份、信用和错误；后续只有新增的实际退出/join 事实可完成回收。closed 成功后不重复 join/记退款，原 startupError/blocked 仍留存，不能让失败变 PASS。

## 接纳与控制器出口

Flow.transaction 只对 NEW 的 PF/n01 setup 允许首次启动例外；其他非 GC 请求均先 ensure_accepting，不能用 started=False 绕过 FAILED。query、RPC、cell 登记同样封闭，RPC 在增加调用计数前核 Hub。GC 只处理原所有权，不以失败后重新 admission 恢复运行。

PF/n01 失败发生在 J/R 创建与日志打开之前，controller 直接走 stop_failure/emit_failure，不执行假定两 helper 存在的常规 GC。原失败出口输出一行有界 JSON 并返回 2，包含原 G PID、startupError、逐 worker 事实、remainingCredits、剩余资源、helper 尝试事实、logCloseProven。即使信用已完全回收仍是 FAIL；信用或所有权未知则 PENDING，不以非零失败冒充整批通过。

Engine 显式保存 J/R helper_attempts；PF/n02/n03 构造前标记 CONSTRUCTING，失败 UNKNOWN。只有有明确 attempted=False 才报告 helper started=False；缺少 Channel 对象本身不足证明未启动，证据缺失/构造失败报告 started=null 和 PENDING。已存在 helper 保留原身份和退出证明，不发额外 EXIT/RPC 或借其缺失猜退出。

错误时实际 native future 尚未完成、worker 未证或 Hub 失效会直接进入保守失败出口；有 callback/cell/worker/native 在途时不关闭其依赖资源或日志。失败出口仅对已证明安全的本地 Hub/log 做有限收尾；其余 helper/native 所有权保持 PENDING，不强杀。未打开日志明确 logOpened=false/logCloseProven=false/logOwnershipPending=false；实际 flush/fsync/close 返回后才记关闭证明。已知重复收尾保留原事实。

这些启动事实位于当前 G 内存及原返回通道，没有为它们新增 journal 事务。G 进程崩溃、回执丢失或未知系统状态仍需保留 PENDING，不能将其外推为新的崩溃耐久保证。

## 原通知方案与测试限界

source/cell 锁内一次性交付决定、全部应用锁外 Future 发布与同步 callback、native/gate/callback 三者排空后释放保持不变。普通/held 同一裁定，seal/fence 先赢丢弃未决定 read/晚 open，已定成功不倒退。固定两条 Hub 线程、8 cell/通知信用、每 cell 4 callback；决定后 callback 注册和外部 Future cancel/set* 拒绝。它是收窄的 Future 契约，不能宣传完全兼容普通 Future。

定向启动检查使用真实但自有的 Python Thread/start/join、生产 Hub/Ledger/Flow/query/RPC 与 emit_failure stdout，有限 Event 屏障，不制造系统线程耗尽、永久挂线程或磁盘故障。原 UNKNOWN/PENDING 回执在受控 retirement 前保存；测试 finally 放行原线程并真实 join，只用于清理测试本身，不能改写原失败证据或称生产自动重启成功。包装函数返回但 Thread 仍活的 join 到期负例单独核信用不归还。

正常完整回归另有真实 J/R 子进程、合成文件和 Windows 资源操作；仍是 L=131072B/C=4096B/Z=0/边界65536 的缩小 profile，不证明视频字幕解码、2GiB、NAS、真实版本/路径替换或共享模式。元数据单次 exact_write、恢复 max/缺 shard UNKNOWN、owner 与原关闭事实继续保留，实际 fsync 不等断电/命名空间耐久 READY。

23/5/1 仅工具受管资源、媒体句柄及 64KiB 槽峰，包含固定两 worker 信用；不是 Python/JVM/.NET 内部线程、句柄或内存总量测量。任意 callback/系统 IO 不返回时仍不能强制中断；180 秒限制接纳与等待，200 秒外层只停止等待，不证明原进程必退出。

维持 452 分配/544 控制硬界、101 query、输入1,573,522B/59次、目标10/记录32、输出655,360/验证262,144、元数据文件信用3,178,496B/硬4MiB及180秒。没有读取 test_media、真实 PF/媒体/设备/Gradle/ADB/下载或正式 run。真实配置/版本/requiredDurability/总资源口径未放行；JNI BLOCKED、D1 NOT_PASSED、M0 NOT_STARTED、C14/P0/历史 FAIL 不变。
