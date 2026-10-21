# D1 E1B 实现与验证边界 V1.0

2026-10-16。配套 `D1_E1B_DELIVERY_V1.0.md`，只说明本包实际事实与剩余验证边界。

## 已实现的实际绑定

G为Python父权威，S/O为其中的源/输出状态机；J为JDK21独立进程真实RandomAccessFile，R为PowerShell/.NET10独立进程Windows原生适配器。Core.cs保留原语类型供Native.cs依赖，活动S/O入口在gengine.py，不将未被调用的旧Core状态机当本次驱动证据。G持只读guard，R独立reference，真实A→DuplicateHandle→B同一进程交付，不构造第二owning wrapper；A/B/validator独立票据。客户端不接收裸HANDLE。

请求HMAC绑定操作ID、行、任务、epoch、claim、角色和参数；传输重放只回缓存、冲突拒绝。G在行/任务/全局保留后记录ADMITTED，外部副作用前持久化；allocation意图包含精确owner/角色/key，写信用在副作用前入账。native动作至多一次；UNKNOWN不重试，安全close最多三attempt。纯元数据命令可以只用完成事务，外部副作用命令最多接纳/完成两次事务。journal命名空间持久性不因fsync返回而声称成立。

恢复包含task、batch/schema、命令指纹/结果/副作用意图、source各版本消费者、在途操作、对象/ticket/owner/disposition、grant/delivery/claim/epoch、输出信用/receipt/token、行使用量、query缓存及有限数据步。J只读两个槽后通过既有回调请求G观察，不增加N或query。G验证同task的READY记录并重建；离线恢复另外重建全部32个记录、按GC跨shard单调最大值合并其累计预算。损坏不回退为成功，不重开writer；尚ADMITTED的动作保留UNKNOWN/只读围栏，不把恢复当重新发起资格。

S17.D实际delegate close=0、attempts=3；S17.C实际进入close=1、原UNKNOWN保留。只有实际J退出后逐对象变为RELEASED_BY_OWNER_EXIT，其原close结果不变。GC source/sink通知分别接纳，仅释放所属域，不能借source通知清输出。恢复磁盘中的GC/n32仍不具关闭证明，必须结合独立外层回执；audit明确保留这个差别。

## 本批不能证明的事项

- 61个入口使用**缩小的合成fixture**：L=131072B、C=4096B、Z=0，窗口边界65536替代2GiB。它证明调度/状态/真实平台调用，未证明2GiB位置、真实媒体、解码或输入字幕行为。媒体实验启动入口保持禁用；下一阶段必须由负责人审查并另行安排实验配置/样本绑定，不能直接把SelfCheck改名成真实实验。
- Windows guard/reference共享模式与文件ID、Java长度/mtime/fileKey在合成文件上已取得。没有证明真实source version保证、其他写者/路径替换、NAS或所有文件系统行为。
- FlushFileBuffers、journal flush/fsync已真实返回；未进行断电、进程崩溃或命名空间ACK实验，requiredDurability仍UNPROVEN。合成READY仅为工具协议状态，不能发表为产品耐久READY或D1通过。
- `before`/`unknown`/ACK丢失、晚完成、固定能力缺失及空间不足是明确的工具故障包装。SPACEFAIL在真实写delegate前注入，未制造磁盘满、native crash、OS压力或信号故障。UNKNOWN包装即使内部close已返回，权威也不提升其知识。
- 账本统计本工具拥有的guard、媒体descriptor、元数据句柄、两helper固定pipe端和process句柄；baseline运行时内部句柄/GC/库缓冲不冒充可逐一持票据的工具对象。64KiB槽为媒体buffer，另有最多64KiB逻辑JSON、压缩校验8KiB槽及有界协议缓冲。未通过全系统内核跟踪证明运行时自身的额外资源峰值；该项实际平台资源保证仍需独立审查，不能把账本峰值当整个JVM/.NET总句柄数。
- 时间到只停止接纳/等待；真实内核IO不可强制撤回。正常本次证据均已退出；未知IO分支需保留owner/ticket/缓冲，不能由标志位宣称已关。极端挂起/外层200秒停止等待路径未做真实挂死实验。

## 限额与失败保持

不动452分配/544硬限额、101query、1,573,522B/59次输入分配、10目标/32记录、655,360写信用、262,144验证额度、3,178,496元数据文件峰值/4MiB硬界和180秒。未分配余量无效；row失败reservation不退款，也不挪给别行。最终实际输入少30B是各原行未花完的保留，不是允许补读。

源snapshot物理双槽最多16KiB，每次落盘8KiB，压缩展开硬限64KiB；事件每条≤1KiB，行N日志24KiB＋q日志8KiB，新query有限缓存事件，恢复不会把较旧seq覆盖较新权威状态。query日志的fsync成本也在100ms观察/行deadline内，实际持久化细节须独立审查其是否满足R4的query只读事务解释，不将日志写入隐去。

这五项原缺口现有具体代码和本批证据，但是否满足R3/R4全部契约由独立审查裁定，尤其query日志落盘、运行时资源口径、耐久性及后续真实实验配置。包状态不写“真实实验READY”。
