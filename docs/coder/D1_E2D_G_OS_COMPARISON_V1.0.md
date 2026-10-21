# D1 E2D 修后 G 固定六点 OS 对照 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2d`。依据 [E2D 正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E2D_CODER_REQUIREMENTS_V1.0.md)，本批完成唯一一次修后小规模 G 对照，原报告状态为 `OBSERVED_POSTFIX_SIX_POINTS_WITHIN_LIMITS`。同一原 G 的六点句柄数为 **160、164、161、193、161、161**，相对本实例 ZERO 为 **0、+4、+1、+33、+1、+1**，均未超过256总数或+64增量。累计9个生产私有 cell、同时峰8；归档后弱 cell 与工具闭包均为0，首个外部 Future 及其原结果保持到 Hub 实际关闭之后。

这证明本次有限场景中的归档路径、引用断开及六次实际 OS 读数符合本批边界。它不证明完整 Engine 资源准入、不保证未来固定降幅，也不把最后+1归因于某一类 OS 句柄。旧 G369/+209、R519 等 FAIL 保持；本批没有 actual full、真实媒体准入或新回归授权。

## 原证据、冻结绑定与运行时

主证据为 [g-comparison-1792174935530529100.json](D:/CodexProjects/VideoKit/docs/coder/d1e2d/evidence/g-comparison-1792174935530529100.json)，其 SHA256 由 [原 caller 退出回执](D:/CodexProjects/VideoKit/docs/coder/d1e2d/evidence/g-comparison-outer-exit.json) 记录为 `9180cf6fe2b8358d2c3ccdc5a23ce85fbf7b5cda6148ea1da8b98bf7a279667a`。六份 `g-comparison-entered-0..5.json` 与六份 `g-comparison-stage-0..5.json` 保留逐点进入及返回事实；[一次预约](D:/CodexProjects/VideoKit/docs/coder/d1e2d/evidence/g-comparison-reservation.json) 在任何 Hub 或 cell 建立之前以 CREATE_NEW 写入，限定一个新原 G、六次指标采样、60秒决策边界。

[production-binding.json](D:/CodexProjects/VideoKit/docs/coder/d1e2d/evidence/production-binding.json) 绑定 E2C 原冻结与源码，逐文件记录生产源码、profiles、manifest 和继承编译产物的长度与 SHA256：

| 项目 | 本次绑定事实 |
|---|---|
| E2C freeze SHA256 | `bccacb2e98b1f4a4d3017fc8efb9bd0f047e58d91e7c910303fff40eb3896179` |
| E2C source ZIP SHA256 | `035263006cbaa99837656bb2b66045a3f5c6181ab8af8c8fe3f5bcf5ba3e5934` |
| 本次 compare-g.py SHA256 | `6975917a764cde4db387c35ddd93a902ba37433e072eb092d7ace598ebcaca46` |
| 实际解释器 | CPython3.12.14，`main, Aug 25 2026, 14:01:42`，`MSC v.1944 64 bit (AMD64)`，指针64位 |
| 原解释器路径 | `C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` |
| python312.dll SHA256 | `2b6fffde96cf24a57fca642aaefd5788816ab5ef8624ea63b722cbceb94d49b1` |
| 自动 GC | 启用，阈值700/10/10；强制 GC 调用0，未禁用 GC |
| 本批生产改动 / 编译 / targeted / actual full | 0 / 0 / 0 / 0 |

轻量 Probe 直接绑定实际 `gengine.Engine.private_cell`、`gengine.Engine.compact_cells` 与 `gengine.Engine.cell_facts` 方法，使用生产 PendingCell、DeliveryFuture、CompletionHub、SourceAuthority 和 Ledger。没有构造 Engine、Native 或 Channel；这里的 `nativeLogicCompletions` 是生产 cell 的受控逻辑完成，不代表文件 native IO。没有另写字典清理来替代生产 compact。

本次沿用 E2C 已记录的本地同步静态证据；实际 DLL 的具体 C 同步后端与句柄类型因果仍分别为 `exactCompiledSynchronizationBackend=UNKNOWN`、`handleTypeCausality=UNKNOWN`。解释器版本、头文件或 OS 总句柄变化不能单独证明每个 cell 对应固定数量、固定类型的内核对象。

## 唯一原实例与固定六点

原 G 的 PID 为 **35964**，creationTime100ns 为 **134366485352518462**，owner 为 `E2D-G-1792174935530529100`。一次原身份查询固定这一实例；六个点均核对原 creation。ZERO 在本实例生产 Hub 两个 worker 启动后、尚无 cell 时取得并固定；没有借用旧实例的160作基线、后移 ZERO、重新启动、重采择低或任意关闭运行时句柄。

| 固定点 | 线程 | 句柄 | 较原 ZERO 句柄差 | workingSetBytes | privateBytes | 单次 sample 秒 |
|---|---:|---:|---:|---:|---:|---:|
| ZERO_CELLS | 6 | 160 | 0 | 27,082,752 | 18,104,320 | 0.0 |
| ONE_LIVE | 6 | 164 | +4 | 27,131,904 | 18,104,320 | 0.0 |
| ONE_DRAINED_COMPACTED | 6 | 161 | +1 | 27,131,904 | 18,104,320 | 0.0 |
| EIGHT_LIVE | 6 | 193 | +33 | 27,131,904 | 18,104,320 | 0.0 |
| EIGHT_DRAINED_COMPACTED | 6 | 161 | +1 | 27,136,000 | 18,104,320 | 0.0 |
| PROBE_AUDIT_COPY_RELEASED | 6 | 161 | +1 | 27,185,152 | 18,104,320 | 约0.015 |

每点 `limitExceedances=[]`，`sampleDeadlineMet=true`。原资源阈值保持：G线程16/+12、句柄256/+64，working set 与 private bytes 均为256MiB总数/+128MiB增量，单次采样期限0.1秒。六点最高观测线程6、句柄193；working set 最大增量102,400B，private bytes 增量0。它们是六个固定时点的实际观测值，不是两点之间连续捕获的 OS 峰值。前五个0.0来自本机计时粒度，不能解读为零成本。

最终耗时1.125秒，包含本次原流程及关闭决策；未启动第七次 OS 采样。最后一个固定点仍处于 Hub RUNNING、两 worker 存活的观察阶段，不能把该点句柄161写成 Hub 或原 G 退出后的 OS 读数。后续真实 join 和原 caller 退出由独立关闭字段及外层回执证明。

## 逐 cell 静默、归档与引用事实

先建立1个 cell，完成原逻辑、gate、callback 和 Future 消费；其调用帧返回之后调用一次生产 compact。再建立8个同时活 cell，逐个完成相同链路，所有消费调用帧返回之后再调用一次 compact。9份 `consumptionProofs` 均记录 `callerConsumedOriginalFuture/sourceDone/nativeReturned/gateOpened/callbackReturned/perCellHubQuiescent=true`。compact 不在异步 release/on_drain 中发生，也不以 `Future.done()` 或 `released` 单一字段替代 notifier/monitor 已返回的证明。

逐 cell 静默包含 Hub 注册表、deadline、队列、active 发布和 monitor 在途；本次归档前实际原调用者已读取对应 Future，native逻辑、gate、callback、release 和源 drain 均已完成。观察函数只短暂解引用 weakref 并返回标量事实，采样发生在该观察函数返回之后；批量操作保存的是 operation 字符串，不强持历史 cell。

| 固定点 | 活动重对象 | 生产累计 total | 生产历史审计 | Probe 审计副本 | 弱 cell 存活 | 弱 Future 存活 | 弱闭包存活 | 外部 Future |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ZERO_CELLS | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ONE_LIVE | 1 | 1 | 0 | 0 | 1 | 1 | 2 | 1 |
| ONE_DRAINED_COMPACTED | 0 | 1 | 1 | 1 | 0 | 1 | 0 | 1 |
| EIGHT_LIVE | 8 | 9 | 1 | 1 | 8 | 9 | 16 | 1 |
| EIGHT_DRAINED_COMPACTED | 0 | 9 | 9 | 9 | 0 | 1 | 0 | 1 |
| PROBE_AUDIT_COPY_RELEASED | 0 | 9 | 9 | 0 | 0 | 1 | 0 | 1 |

对应 `futureCellBackrefs` 为0/1/0/8/0/0，`releaseClosuresRetained` 与 `drainClosuresRetained` 均为0/1/0/8/0/0；SourceAuthority 登记数同样为0/1/0/8/0/0。这说明此次完成对象在安全归档后不再由这些工具反向边及闭包保留。它不把 weakref 观测提升为所有 Python 对象、异常 traceback 或 OS 对象都必须立即释放的承诺。

最后一点仅清除 `probe.audit_copy`。生产 `cell_total=9`、`cell_history`9条、`cell_peak=8` 保持，`active=retained=0`、`archived=9`；各 stage/report 中的纯审计副本也仍保留。没有清生产审计、重置总数、返还累计64限额或声称全部审计引用清空。九条不可变审计保留原 operation、binding、kind、native/gate/通知/callback/release事实；每条delivery1、callback注册及返回各1，错误摘要为空。审计不重新持有原 cell、Future、值或闭包。

首个外部 Future 自建立起一直由外部持有，归档后 `Future.cell` 已解绑。报告以对象身份 `is` 检查原结果，归档后和 Hub 实际关闭后均稳定：`externalFutureHeldThroughClosure=true`、`externalFirstOriginalResultStableAfterClosure=true`。保留它是合法外部所有权，本次既没有清除其结果或异常来求回收，也没有要求最终句柄必须回到 ZERO。末点+1的具体内核对象类型及归属未被本次六点观测证明。

## 与历史观察的可比边界

E2C 原诊断 [g-lifecycle-1792172968097380400.json](D:/CodexProjects/VideoKit/docs/coder/d1e2c/evidence/g-lifecycle-1792172968097380400.json) 来自另一原 G：PID26368、creationTime100ns `134366465678168526`。当时六点句柄为160/164/164/196/196/196；最后清空工具历史后，弱 cell9、弱 Future9、弱闭包18仍存。本次修后最后为弱 cell0、弱 Future1、弱闭包0，生产9条轻量审计仍在。

两次证据共同支持“仅清历史容器不足；实际安全归档并断开工具引用边后，本次有限对象不再被同类历史链保留”的判断。本次原实例在两次 compact 后均观测到161句柄，而活峰为193。两次来自不同 PID/creation、各自固定 ZERO，working set/private baseline也不同，不能计算为同一进程的成对降幅、保证每 cell 少若干句柄，或证明 OS 根因已经枚举。没有为比较而追加旧实例或本实例样本。

旧 E2B actual full 的 G369总数/+209增量 FAIL、旧 R519及其它历史失败不因本次小9范围观测撤销。policy、原61用例预算和真实入口门禁保持；本次结论不涵盖完整 Engine、J/R、文件 native IO、异常 traceback 长期外部持有、真实媒体或更长业务生命周期。

## 独立成本、原关闭与交付裁定

本次诊断成本独立列账，`original452Charged=false`，不能写成原452控制内零成本：

| 成本 / 收尾事实 | 实际记录 |
|---|---|
| 原 G / 指标采样 / 原身份查询 | 1 / 6 / 1 |
| observer 实际打开 / 实际关闭 / 同时占有峰 | 13 / 13 / 1；六周期加一次身份查询，借用身份查询0 |
| observer 信用 / 关闭未知 / 新 worker | 最终信用未持有 / false / 0；先留信用、实际关闭后才返还 |
| 生产 Hub worker | 2；notify 与 deadline 均实际 entered/exited、join返回，`THREAD_JOIN_PROVEN` |
| cell建立 / source准入 / 逻辑完成 / gate / 原Future消费 / callback返回 | 各9 |
| 正常 compact / 清理 compact | 2 / 0 |
| 清理补逻辑完成 / gate / Future消费 | 各0 |
| 账本峰 / buffer峰 / 最终buffer | 3 / 8 / 0 |
| 新 RPC / 新 driver control / fixture bytes | 0 / 0 / 0 |
| helper启动 / 媒体读取字节 / 文件native媒体调用 | 0 / 0 / 0 |

六点之后关闭的是原 Hub；最终 `lifecycle=CLOSED`、`workersAlive=0`、`cells/queued/active/monitorInFlight=0`、`remainingCredits=[]`、`ownershipPending=false`，启动及清理错误均为空。`remainingResources={}`、`remainingBuffers=0`、`noInFlight=true`。原 caller 外层回执记录同一 PID/creation/owner 的 `observedCommandExitCode=0`、`originalInvocationComplete=true`、`rerun=false`、`newDiagnosticG=0`，没有为补退出事实另启动 G。关闭证明不冒充一次退出后 OS 指标采样。

原报告 `diagnosticArtifactBytesAtReport=100,630B` 是写报告时的诊断快照，未包含后补 outer-exit 与 production-binding，原字段保持不回写。中央只读 audit 已核本次全部 `g-comparison*.json` 加 `production-binding.json` 共 **109,229B≤512KiB**，包含 outer-exit，不含后续 audit 文件。整批日志/证据≤4MiB及fixture≤2MiB的最终完整文件数与字节仍以 freeze-summary 的逐文件统计为准，不能把诊断子集合或旧快照当作整批合计。60秒是停止等待和决策清理界，不将不可中断且未返回的调用写成已关闭；本次实际返回、关闭与原退出均完整，没有 UNKNOWN 或在途留存。

本批没有新编译、targeted、full、额外 G、第七样本、强制 GC 或禁用 GC；未读取、stat、hash、复制或扫描 test_media，未启动真实 PF、真实 runs、J/R、Gradle、ADB、设备或下载。唯一小对照预约已经消费，不能转作 actual full 或真实批次/root 授权。后续是否另授新的 actual 自有回归由负责人裁定。JNI仍 BLOCKED，P0/C14与历史 FAIL 保持，**D1 NOT_PASSED，M0 NOT_STARTED**。
