# D1 E1E Hub 启动失败集中修复交付 V1.0

2026-10-16。依据负责人 E1E 要求及 E1D 独立复审，只修 **E1D-D01 P1**，保留 C01/C02、T02–T05 已认可方案。在 `D:\CodexProjects\VideoKit\docs\coder\d1e1e` 完成实现、编译、相关合成回归、只读审计与一次冻结。候选状态 **D01_FIXED_SYNTHETIC_VERIFIED_PENDING_INDEPENDENT_REVIEW**；请负责人安排整包独立复审，本窗口不自行派 tester/实验。

## 最终结果

| 选定证据 | 结果 |
|---|---|
| `D:\CodexProjects\VideoKit\docs\coder\d1e1e\evidence\selfcheck-1792163660432915800.json` | 一轮完整合成回归，159 项 PASS；执行根 `selfcheck/check-20261016T231420` |
| `D:\CodexProjects\VideoKit\docs\coder\d1e1e\evidence\targeted-1792163909644634300.json` | 一轮集中定向检查，619 项 PASS |
| `D:\CodexProjects\VideoKit\docs\coder\d1e1e\evidence\audit.json` | 最终共 **778 项**；预算、恢复、原实例退出、逐 worker 事实及上游文件一致 |

619 项包括：D01 新增 **205**、C01/C02 **153**、源/owner **139**、恢复 **33**、短写 **69**、通用 **20**。205 项检查使用生产 Hub/Flow/Engine 方法、真实自有 Thread 与 stdout，不启动 Engine 构造、Native/Channel/helper，不冒充真实系统线程耗尽。只统计本批一次完整回归＋一次定向结果，旧 E1D 573 项不重复计入。

正常完整回归实际 351N＋83 新 query＋18 重放＝452 控制，输入请求 1,573,492B/59 次，未用30B仍锁在原行；目标10、记录32、输出信用655,360B、验证请求128B。64个私有cell全排空，峰1；受管资源峰23/24、媒体5/6、64KiB槽1/8，最终受管资源0。两worker均保存 startReturned/entered/exited/joinReturned/joined、alive=false、THREAD_JOIN_PROVEN，最终 Hub CLOSED、remainingCredits=[]、ownershipPending=false、所有启动/运行/收尾错误为空。原 J/R 实际wait code0，全部本批工具、helper、受控线程与已知IO均已返回，无在途。

元数据 requested=written=6,397,718B，unknown请求0、HEALTHY，文件峰630,550B。累计写量与文件峰分开。fixture累计135,244B；冻结前日志/证据精确字节见freeze-summary，保持2MiB/4MiB边界。正常回归的n32外层见证关联关闭前摘要 SHA256 `07854054899797fcddc9cf32231bf7f1062368777214849cfa04d9b266460d2c`。

## D01 逐路径闭合

| 路径 | 实现 | 有意义负例/观察 |
|---|---|---|
| 未完整启动却接纳 | `notifications.py:CompletionHub.start/ensure_accepting`；`gengine.py:Flow.transaction/query/Engine.remote` | NEW/STARTING/RUNNING/FAILED/CLOSED 分明，仅两worker实际entry且alive才RUNNING。第二starter停在Event屏障时第一已活、第二未启，cell/transaction/query/RPC均拒绝，无预算、状态、副作用增加。PF/n01 NEW setup是唯一初始例外。 |
| 第一/第二启动失败 | `CompletionHub._start_worker/start/_cleanup_workers` | 自有starter在调用真实start前显式WorkerNotStartedError；第一未启不join、不造join proof；第二失败时第一实际停止/join，第二不join，分别归还。保原异常、startupError及稳定拒接纳，不能重启。 |
| 第一/第二信用失败 | 同上；`gcore.py:Ledger.release` | 第一预留失败无Thread/退款；第二失败只回收第一实际worker。第二已提交信用再抛错时核精确rid的前后账本事实，归还确证未启信用，不漏账；不假定两worker/两信用存在。 |
| 实际启动后异常 | 包装 `_entry` 事件、原Thread身份与真实join | starter真实start后在entry屏障确认线程进入再抛错；startReturned=false仍按实际已启回收，只能真实join，不能按“未启”退款。 |
| 无法证明是否启动 | `CompletionHub.pending/close` | 通用start异常、alive=false/ident=None不足退款；保留UNKNOWN、信用和PENDING。原emit_failure输出2及原身份/剩余信用。测试随后单独受控退休原对象，原失败回执不改写。 |
| join期限到达 | `_cleanup_workers_owned/close` | 自有Thread在生产wrapper已exit后通过Event保持真实Thread存活，实际有限join返回但alive=true；仍保留原credit/owner、joined=false，无THREAD_JOIN_PROVEN。原返回通道PENDING，放行后实际join才归还。 |
| 重复close及并发启动 | 有界cleanup锁、逐worker字段、closed幂等 | 未启不join，已回收不重复join/退款，FAILED/CLOSED后接纳稳定拒绝。启动调用在途不可归还信用，未知继续Stop；正常/失败/未知收尾保持原错误。 |
| controller/PF尚无helper | `controller.py:stop_failure/emit_failure/run`；`phases.py:preflight`；`Engine.helper_attempts` | D01失败直接有界失败出口，不运行假定J/R存在的GC。真实stdout一行JSON、code2；有确证未尝试才started=false，无Channel但构造已尝试/证据缺失则started=null/PENDING。未开log不假close；Hub/native/callback在途不关依赖资源。 |

Ledger的THREAD_NOT_STARTED_PROVEN仅限worker，与实际THREAD_JOIN_PROVEN分开；未成功预留没有“退款”。所有原始失败/PENDING观察先保存，测试finally的受控放行/退休只证明测试最终无遗留，不把生产未知改记自动成功，不强杀或重启线程碰运气。

## 保持的控制与实现

PF/n01既有setup内逐worker预留、构造、start/entry验证和失败收尾；正常GC/n31既有journalClose内逐workerjoin。controller异常出口仅收原所有权，不发新EXIT/RPC。新增事实是G内存及原返回通道数据，没有额外journal事务、控制token、媒体请求、替换worker或重跑。manifest的startupFixes.D01及PF/n01/GC/n31 boundedEffects列出映射。

仍为61行/22家族、PF16/GC32、452分配/544硬界、101query、原IO/资源/180秒分配、每N/D最多两次snapshot。原C01/C02的原操作原子决定、锁外通知、实际回调排空和active容量归还保持；原T02–T05的精确源绑定、owner/epoch请求、恢复max/缺shard UNKNOWN、exact_write/短写封下游保持，所有相关组回归通过。

## 文件、冻结与保留

- 三文档：本文件及 `D:\CodexProjects\VideoKit\docs\coder\D1_E1E_IMPLEMENTATION_BOUNDARY_V1.0.md`、`D:\CodexProjects\VideoKit\docs\coder\D1_E1E_EXECUTION_APPENDIX_V1.0.md`。
- 全依赖源码：`D:\CodexProjects\VideoKit\docs\coder\d1e1e\artifacts\E1E-source.zip`；本批一次本地编译成功的E1E.dll和JavaHelper两个class；manifest/只读verify/source-manifest/freeze-summary齐全，逐文件字节/SHA及ZIP成员一致。
- upstream-e1d保存原E1D源ZIP、freeze、source-manifest、branches及13项基线关系，嵌套继续保留E1C/E1B/E1源码；原E1D 12冻结＋216自检＝228文件只读SHA核验一致，原包/旧失败证据未改。

限制详见边界文档。受限Future、任意Python callback/native IO不能强制中断、运行时总资源尚未测量等限制继续生效。未读test_media、未真实PF/媒体/设备/Gradle/ADB/下载或正式run。真实配置/版本/requiredDurability/总资源仍未放行，JNI BLOCKED、D1 NOT_PASSED、M0 NOT_STARTED、C14/P0/历史FAIL不变。778项是D01修复候选的合成证据，不是正式产品交付完成。
