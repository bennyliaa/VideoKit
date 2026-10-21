# D1 E1 实现边界 V1.0

2026-10-16。对应[E1需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E1_CODER_REQUIREMENTS_V1.0.md)。**当前是可编译、可独立审阅的部分工具实现，不是完整61场景harness；不可直接批准真实媒体实验。** 源码与真实绑定已实现，整批场景调度及持久化/IPC/预算逐操作串联尚未完成，机器清单如实标`PRIMITIVES_IMPLEMENTED_FULL_SCENARIO_UNWIRED`。不以原语自检通过推断整批通过。

## 1. 已有实现和实际证据

| 模块 | 实际代码入口 | 已实现内容/证明范围 |
|---|---|---|
| 三层预算 | [Core.cs](D:/CodexProjects/VideoKit/docs/coder/d1e1/src/Core.cs) Budget.Reserve；[FrozenSession.cs](D:/CodexProjects/VideoKit/docs/coder/d1e1/src/FrozenSession.cs) | 原子检查row/task/global后收费，失败/未知不退预留。冻结61行预算载入，deadline停止等待并保留原Task/资源，拒绝空收费和无限pending。合成验证超额前副作用0、超时保持计费、真正晚完成后再ack。尚非所有原语的强制唯一入口。 |
| close | Core.CloseTicket；[Native.cs](D:/CodexProjects/VideoKit/docs/coder/d1e1/src/Native.cs) NativeFile.Close；[JavaHelper.java](D:/CodexProjects/VideoKit/docs/coder/d1e1/src/JavaHelper.java) Owned.close | nonce对象/owner/ticket、revision/attempt、缓存重放及参数冲突，最多3次安全尝试；已关只确认、UNKNOWN不重试。真实CloseHandle/RandomAccessFile.close有实际调用计数。未知注入为明确的delegate前模型注入，native0，不是实际OS close故障。 |
| source authority | Core.SourceAuthority | reserve、seal、双consumer/future-open、迟到open/读在途、取消、end、版本/旧通知、父guard/ref外部ticket参与Drained；锁内原子更新。未实现全权威状态持久化重建/完整resolver及逐RPC自动接线。 |
| Sink authority | Core.SinkAuthority | 不可写GrantView、唯一alloc/dup/send/take/claim、未知abort-only、逐descriptor关闭证明且重复证明不重复扣；验证lease及实际close证明、sha/revision/epoch receipt、source收尾条件、READY/abort/takeover仲裁。实际native输出已手工贯通一次。未实现全任务跨进程持久authority重建及完整场景封装。 |
| Windows绑定 | Native.NativeFile/Mailbox/NetHelper | 真实CreateFileW只读FileShare.Read guard/reference，DuplicateHandle SAME_ACCESS/不可继承/不用CLOSE_SOURCE；A/B不同descriptor且同文件身份；A关后B真写、FlushFileBuffers、逐份close、独立只读验证。一次mailbox移动同一B对象，不能重复take。不是mock dup。 |
| Java绑定 | JavaHelper.main | 真实RandomAccessFile open/64位seek/read/EOF/零请求/close，固定帧和请求缓存；独立.NET reference读同一合成文件。没有改C14或用memory provider替代。 |
| journal/只读恢复 | Core.Journal/ReadOnlyRecovery；JavaHelper RECOVER | 两个固定8KiB槽，序号＋SHA校验、FileStream.Flush(true)，累计写与文件峰值分开；损坏标DEGRADED/UNKNOWN，不能把旧快照当当前成功；已有journal未恢复不允许Save覆盖。J进程独立校验二进制record并返回合成终态记录，O域校验仍归G。仅OS data-sync，不证明目录/namespace或掉电持久性。 |
| 进程与退出 | [Controller.cs](D:/CodexProjects/VideoKit/docs/coder/d1e1/src/Controller.cs) Child | 明确启动J/R、bounded帧、pending传输不盲重试、原Process对象PID/StartTime/instance/实际退出码核对；记录退出观察时间。无Kill、崩溃/压力实验。仅实际退出释放原实例私有资源，父guard另关。 |
| 机器清单与入口 | [branches.json](D:/CodexProjects/VideoKit/docs/coder/d1e1/manifest/branches.json)；Controller.Plan/OperationRouter | 全61行、每N token/requestId/并发组、任务和数据预算、代码原语入口、PF16/GC32具名槽。452/101等离线重算。所有行executionStatus=NOT_RUN，完整驱动未连接，不把映射表称61行实现通过。 |

## 2. 未完成项与准入阻断

以下是实现缺口，不是待用户提供媒体/设备或纯环境等待；当前交付不宣称E1全部实现要求已满足：

1. **61场景上下文/数据请求位置和检查点驱动未接线。** OperationRouter只分派已绑定原语，未绑定就NOT_RUN_CONTRACT_ADAPTER_MISSING。P01四大窗口、P04长度包装、P05短读cap、P06/P07错误映射、P08/P09故障闸门与query时序、P10-B/S17跨owner证据汇总、全部Q分支的真实调度都不能仅据机器manifest启动。
2. **未提供完整PF16/GC32执行器。** 实际自检启动两helper、真实guard/J/ref及正常退出只是合成绑定验证，不是PF。Child.Stop不能代替GC所有逐父/子引用收尾；S17未知与原owner退出的聚合账本尚需串联。GC/n32控制器最后log关闭回原通道也尚无整批实现。
3. **非query、D、额外RPC与native副作用尚未全路径自动关联。** FrozenSession原子门禁已具备，但NativeFile/NetHelper是受信任的底层原语，可单独调用；R helper的WRITE不独立验证O的claim/epoch，必须由G.CanWrite和预算前置。禁止将此原语通道当完整writer协议。实际串联若新增控制请求，须暴露与452分配的差异，不能隐藏RPC/借92余量。
4. **持久化不是完整权威恢复。** Journal可持久任意有界record，ReadOnlyRecovery只恢复同export/intent READY元数据，不恢复FD/写许可。尚未把每个S/O接纳/完成自动固化为R4规定的两事务，完整authority快照、source/descriptor/in-flight所有字段的恢复与unknown-owner围栏仍缺。J跨进程恢复用的是合成终态record，非完整真实导出回复丢失实验。
5. **运行时全维度记账仍需联调。** 已有行/任务/全局预算及live counters，但尚未把所有helpers/pipe/journal/缓冲绑定到同一live-vector，也缺跨行目标写预算信用的统一消费、完整file-peak/metadata-write控制器、各行实际native计数/事件闭环。不能以当前孤立计数器宣布24句柄/8缓冲或180秒的完整harness实证。

没有发现必须下载新组件才能继续实现的环境阻断；.NET SDK缺失已经通过本机PowerShell现有Roslyn/.NET宿主完成工具编译。上列代码工作仍需继续完成并独立审查，之后才可能满足真实实验准入。不能把本批记为61行已实现或以NOT_RUN掩盖必需场景缺少驱动。

## 3. 自检事实和剩余平台限制

最终[自检证据](D:/CodexProjects/VideoKit/docs/coder/d1e1/evidence/selfcheck.json)为80断言PASS，仅SYNTHETIC_SELF_CHECK：逻辑竞争/重放/版本、close资格/三次耗尽、预算预留/超时、journal损坏/恢复、真实Windows guard/dup/读回、真实J/R独立读取和退出。模拟UNKNOWN为native0注入，超时为合成阻塞任务，不能称内核IO阻塞或真实native故障实测。构造的恢复READY record只证明格式/校验/身份读取；实际输出READY的证明来自另一个本机native小字节probe，未混成跨进程恢复整批成功。

已有JDK21.0.10；本机dotnet仅8.0.23 runtime、没有SDK。实际R/G工具用PowerShell7.6.5自带Roslyn编译，在.NET10.0.11宿主运行，**不声称.NET8目标兼容**。没有下载/联网补依赖。正式平台绑定、测试媒体长度/版本/fileKey、已有写映射/竞争者、NAS/Android/Binder、目录同步/namespace ACK、掉电、长阻塞、任意short read、真实close失败、宿主JNI故障隔离均未验证。路径检查和private stdin只用于受信任本机合成工具，不是抵抗同UID恶意进程的安全边界。

完整实验预计预算保持452已分配控制（硬544）、101query、1,573,522B/59输入请求、10目标/32记录、写655,360B/验证262,144B、文件峰值3,178,496B、180秒与既有live限额；这些是冻结计划，不是本轮实耗。合成自检累计文件143,816B≤2MiB，证据日志另限4MiB，均不当测试媒体读取或正式run。所有本轮helper/构建已结束。

Kit/Flutter/C ABI/框架许可、全P0和历史FAIL、R1–R4及C14原件不变。宿主JNI仍BLOCKED；D1未通过、M0未启动。本批是工具代码审查材料，不能据此运行真实媒体、PF、设备或产品流程。
