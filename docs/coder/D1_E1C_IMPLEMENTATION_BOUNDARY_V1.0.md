# D1 E1C 实现与证据边界 V1.0

2026-10-16。五项修复候选已集中实现并完成限定合成检查，仍待独立复审，不等真实媒体/产品验收。

## 实际权威与响应

活动路径为Python G中的SourceAuthority/S/O，J真实RandomAccessFile与R真实Windows native绑定。Core.cs旧状态类型仅供底层依赖，不能替代活动Python路径。E1C的每次源open/read，包括普通非hold调用，均在同一原子点核task/version/consumer/generation、reservation未finished/未cancelled、句柄精确归属与可用disposition，随后建立原操作与私有cell。

原操作已接纳后不因end/cancel重发delegate；真实返回与消费者响应是两种事实。held cell在native返回后仍使Future等待；cancel/真实Timer deadline完成CANCELLED/SOURCE_TIMEOUT，不释放其私有结果与buffer租用。原gate只丢弃或单次交付已存在结果，随后实际release；普通调用在自动gate前同锁复核生命周期，已结束则只排空不交付。普通同步便捷包装仍可能等待真实RPC返回；私有Future可先收到取消，不能宣称取消已强制中断系统IO。

138项逻辑权威检查中，使用生产SourceAuthority、PendingCell、complete_source_response、Engine.private_cell和Ledger，观察真实Future等待/结果/错误、真实租用计数和一次release。它们不启动J/R，注入的逻辑delegate计数只证明接纳路径；实际J/R事实由独立完整合成回归证明。不是用测试布尔值当真实native证明。

ready请求由原owner捕获并深复制完整身份，当前持久owner/epoch决定STALE_OWNER；receipt与其他绑定独立验证。ready提交、takeover和cancel/abort终态判断共用G锁。测试中的错误请求来自改变实际身份字段，不再有old布尔快捷分支。

## 恢复与元数据提交

schema3记录绑定batch/task；PF admitted inventory在第一次task副作用前保留最小信用与初次命令。恢复只认同身份有效槽与完整q行，较少日志不能覆盖较大snapshot预留；q损坏/截断/缺失、inventory不可信或已接纳shard丢失明确UNKNOWN，usageKnownMinimum只表示已知下界，不能把差额当新额度。正常完整记录才有usageExact=true。缺失且未能证明“从未接纳”时，不以0宣称完整。

恢复始终只读、加围栏、无新进程/媒体IO、无raw handle重造；对原ADMITTED/WAITING及未证引用不重做。GC跨shard预算取单调最大值，不能求和或退款。两个物理8KiB槽合计16KiB，单个逻辑JSON展开硬限64KiB，压缩并校验；这不是断电耐久性证明。

所有权威snapshot/event、global header/log与关闭前receipt使用同一单次exact_write：实际返回必须等于完整请求；不以fsync能发现坏记录替代副作用前门禁。短返回/None/非法返回/异常令Store提交UNKNOWN，后续transaction/query/remote均停止；文件关闭仍只对本地精确owner做一次。自有wrapper只模拟返回值，没有制造磁盘满或真实磁盘故障。69项短写检查的action0/RPC未授权是逻辑接纳顺序事实，不说成真实Windows故障已发生。

query仍记录有界证据/cache日志及实际sync成本，非字面零磁盘IO；T04修复其恢复合并，不删除这项实现事实。最终关闭前summary仍不能证明log已关，必须结合原外层回执；恢复本身保留GC/n32待外部见证状态。

## 保持未验证的范围

- 全61入口仍为缩小合成profile：L=131072B、C=4096B、Z=0、边界65536，未证明2GiB窗口/真实媒体/字幕/解码。真实实验启动禁用，另行审查与派实验配置。
- 文件ID/guard/reference与共享模式仅有合成绑定证据；真实source version、路径替换、NAS等未证。
- 数据flush、journal fsync实际返回不等断电/命名空间ACK；requiredDurability仍UNPROVEN，合成READY不是产品耐久READY。
- 21/5/1是工具受管OS资源、媒体句柄、64KiB媒体槽峰值；JVM/.NET基线、内部句柄及固定协议/JSON缓冲不当作已做全系统内核测量。原运行时资源限制仍待验证。
- native未知/挂起时停止接纳和等待，保留pending事实；极端真实挂死、信号/native crash/全局压力未做。当前正常两轮回归均已退出，不外推异常分支全部已验证释放。

控制分配452/硬544、101query、输入1,573,522B/59、目标10/记录32、写655,360/验证262,144、元数据文件峰3,178,496/硬4MiB、180秒均不扩大。独立合成开发检查的累计fixture/log按2MiB/4MiB另计，不将多个回归的单轮控制汇总伪装成一轮。

宿主JNI BLOCKED；D1未通过、M0未启动，正式Kit/Flutter/Android/NAS/许可/P0及历史FAIL/C14状态不变。
