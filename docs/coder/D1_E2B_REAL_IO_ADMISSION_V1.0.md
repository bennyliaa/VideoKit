# D1 E2B 有限真实 IO 适配与准入说明 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2b`。**A01 别名修复的四个自有文件活动链检查通过；预定两实例 R 启动诊断完成，候选满足一次自有文件 actual-observer 回归的启动条件；该唯一回归实际 FAIL，当前仍因 G 句柄超限而阻断。真实媒体执行入口始终关闭，交付待独立审查。** 本文件不构成真实 PF、61 分支、唯一真实输出根或任何 `test_media` 内容访问的授权。

依据为 [E2B 正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E2B_CODER_REQUIREMENTS_V1.0.md)。配套交付及执行说明见 [DELIVERY](D:/CodexProjects/VideoKit/docs/coder/D1_E2B_DELIVERY_V1.0.md) 和 [EXECUTION_APPENDIX](D:/CodexProjects/VideoKit/docs/coder/D1_E2B_EXECUTION_APPENDIX_V1.0.md)。旧 E2A 包和失败证据只读保留，不通过新结果覆盖旧事实。

## 逐项裁定与本批结论

| 正式裁定 | 实现及本批证据 | 准入结论与限制 |
|---|---|---|
| A01 原 grant 内使用精确 C 输入及已证物理身份 | `Ops.grant(alias=True)` 调用 `Namespaces.input_path('C')`，比对原绑定 C 的 opened identity；真实 `Native.open/query/close` 在原控制内完成；分离 inputs/outputs 的四 case、46 断言通过 | 正常活动链拒绝 `INPUT_ALIAS`，文件字节 delegate 为 0，无新增 N/RPC，不在输出根放置或寻找 C 副本；不等于真实媒体版本已证 |
| 固定两个原 R 实例、每实例四阶段的有限诊断 | 相同 PowerShell 7.6.5、.NET 10.0.11 和同一 E2B.dll，依次执行一个 Add-Type 实例和一个绝对路径 Assembly.LoadFrom 实例；八阶段原身份及指标具证 | Add-Type 首个超限是 HELLO 的 513；LoadFrom HELLO 为 499。只支持本轮两实例的总数及阶段差异，不证明句柄类型根因或稳定节省数量 |
| 诊断成本独立、保原限额和原实例清理 | 两 helper、八采样、两次借用原进程句柄核身份；单临时 observer 句柄，16 开 16 关；总计约 1.203 秒、原实例均退出 0 | 不归入原 452 控制；没有重启碰低值、提高 512/+128、强制 GC 或关闭 CLR 任意内部句柄 |
| 候选合格后至多一次自有文件 actual-observer 完整回归尝试 | 诊断验证 `eligibleForOneActualSyntheticRegression=true`；CREATE_NEW reservation/claim 绑定诊断、DLL、policy 和原父进程；唯一实际尝试已消费 | 该次在 P09-TIMEOUT 触发 G handles369>256、delta209>64，FAIL 保留，不补跑；未完成全 61 分支，不以 mock full 替代 |
| 冻结审查、真实入口仍关闭、失败历史保持 | 最终定向 955 PASS；原诊断、唯一 actual FAIL、拒绝回执和旧证据分别保存，随源码、产物、manifest 和三文档封存 | 不累加早先同 955、上游 1003/Java87 或 partial77；真实授权层、唯一真实批次/root 未批准，D1 未通过、M0 未启动 |

## A01：精确 C 输入、原对象账目与关闭边界

原问题是 grant 的别名检查直接访问输出根下的 `C.bin`，在输入、输出分离时不能指向实际配置的 C。修复只作用于原 `Q09-ALIAS/n01` grant 内部：先通过 Namespaces 取得精确 C 输入路径和已绑定的原 opened identity，再登记 G 的 guard 资源记录，执行原只读 `Native.open`，将返回的 owner/object/ticket/identity 先写入该原对象记录，随后比对并拒绝输入别名。没有复制 C、创建替代输出根输入、path/hash 回退或新增 identity RPC。

原打开参数保持 `GENERIC_READ=0x80000000`、share READ=1、`OPEN_EXISTING=3`、flags0x80。查询来自该原 HANDLE；身份、长度或 mtime 的取得不读取源字节。查询未证明身份时返回 `BLOCKED_VERSION_NOT_PROVEN`；与原 C 身份不一致时返回 `SOURCE_VERSION_IDENTITY_CHANGED`。这两种失败仍保留原分配事实并执行原 close。close 返回失败或未知时，对象记录保留 `UNKNOWN`、原 object/ticket 和 closeError，原 Native.owned 及信用不按未打开处理，不继续 grant 或假称已关闭。

选定证据为 [targeted-1792171365263345400.json](D:/CodexProjects/VideoKit/docs/coder/d1e2b/evidence/targeted-1792171365263345400.json) 的 `alias_checks`：4 case、46 断言 PASS。测试使用真实自有 `inputs/C.bin`，各 `outputs/<case>` 均没有 C 副本；实际经过生产 `Flow`、`Ops.grant`、`Namespaces`、`Store` 与 G `Native`，没有启动 J/R helper、callback worker 或 observer。它不是完整 Engine 启动或真实 PF 的替代证明。

| case | 原 grant 结果 | 原对象及关闭事实 |
|---|---|---|
| normal | INPUT_ALIAS | 原 C 实际 open/query，原 object/ticket 保留，实际 close 一次 |
| query-failure | BLOCKED_VERSION_NOT_PROVEN | 原 open 实际分配；查询返回值受控失败，原 ticket 留账，实际 close 一次 |
| identity-mismatch | SOURCE_VERSION_IDENTITY_CHANGED | 原 open/query 实际执行；仅返回的身份受控修改，随后实际 close 一次 |
| close-unknown | GUARD_CLOSE_UNKNOWN_NO_RETRY | 测试包装层隐藏已观察到的实际成功 close 返回；先断言原对象 UNKNOWN、原信用及 Native.owned 仍保留，再凭测试层独立保留的实际返回收尾，不第二次 close |

后三项是明确的自有返回值注入，不冒称真实 OS 查询失败、真实文件换版或真实关闭未知已经发生。测试收尾不能被生产路径用于把 UNKNOWN 推断成 CLOSED。四 case 的别名检查各保持 1N、0RPC、0 文件字节 delegate、0 新目标；为建立原 C 证据而执行的 setup open/query/close 独立列示。合计实际 open8、实际 identity query7，另一次注入查询失败，实际 close8；新 fixture33B，元数据 requested=written=58,154B、文件占用58,154B、事务7（逐 case 为2/2/2/1，均不超过原两阶段），最终资源0。该活动链尚未在唯一 actual full 中走到，不能将独立 A01 检查写成全 61 已完成。

## R 启动诊断：八个原阶段的实测事实

唯一诊断为 [diagnostic-1792171021038062900.json](D:/CodexProjects/VideoKit/docs/coder/d1e2b/evidence/diagnostic-1792171021038062900.json)，汇总为 [diagnostic-summary.json](D:/CodexProjects/VideoKit/docs/coder/d1e2b/evidence/diagnostic-summary.json)。在第一实例启动前已保存固定两方法、四阶段的 [diagnostic-reservation.json](D:/CodexProjects/VideoKit/docs/coder/d1e2b/evidence/diagnostic-reservation.json)。没有增加第三实例、重启重采或选择较低值替换首个超限。

两方法均使用已有 PowerShell7.6.5/.NET10.0.11、NoProfile/NonInteractive 和同一 E2B.dll。该 DLL SHA256 为 `06befb5eee245e4d90ca5c91b35b50093cde9cd30bb639a242295f613fc01ac8`，与 [build.json](D:/CodexProjects/VideoKit/docs/coder/d1e2b/evidence/build.json) 及诊断绑定一致；一次集中编译成功，未修复重编。每个原进程通过阶段 ACK 等待点接受一次采样，保留 PID、creationTime100ns 和 owner；两实例分别是 Add-Type PID14880/creation134366446210466136、LoadFrom PID39424/creation134366446217969538，原 owner 和退出证明在原 JSON 中完整保存。没有以 PID 单独替代实例身份。

| 方法 | 固定阶段 | 线程 | 句柄 | workingSetBytes | privateBytes |
|---|---|---:|---:|---:|---:|
| Add-Type | MINIMAL_START | 25 | 498 | 78,221,312 | 24,862,720 |
| Add-Type | LOAD_COMPLETE | 26 | 511 | 84,160,512 | 28,635,136 |
| Add-Type | INIT_COMPLETE | 26 | 511 | 85,925,888 | 29,786,112 |
| Add-Type | HELLO_SERIALIZED | 26 | **513** | 88,231,936 | 29,970,432 |
| LoadFrom | MINIMAL_START | 24 | 497 | 82,857,984 | 26,091,520 |
| LoadFrom | LOAD_COMPLETE | 24 | 497 | 83,431,424 | 26,492,928 |
| LoadFrom | INIT_COMPLETE | 24 | 497 | 85,098,496 | 27,340,800 |
| LoadFrom | HELLO_SERIALIZED | 24 | **499** | 87,437,312 | 27,672,576 |

首个超限保留为 Add-Type/HELLO_SERIALIZED/handles513>512，未被候选499覆盖。Add-Type 从自身最小启动到 HELLO 增加15句柄，LoadFrom 增加2；两个 HELLO 的总数相差14，但两实例最小启动本身已有498与497的差异。未枚举句柄类型、未把逐个 CLR 句柄归因于某条加载语句，因此不能声称 LoadFrom 已被证明固定减少14句柄、根因已经排除或未来都会满足512。历史 E2A 的 R519>512 同样保留，未复采洗去。

候选 `tools/r-helper.ps1` 使用已存在程序集的绝对路径 `Assembly.LoadFrom`，并以核心 `System.IO.Path/File` 替代启动包装中不必要的 Split-Path/Join-Path/Test-Path cmdlet 加载。没有换 PowerShell/.NET/runtime、放宽 flags/共享条件、强制 GC 或任意关闭 CLR 内部句柄。这是有界加载开销调整及本轮总数对照，不能从它推导产品宿主兼容性或稳定资源保证。

诊断阶段间的差异仅是描述数据，**MINIMAL_START 不是实际回归的 runtime baseline**。诊断验证 valid=true、候选 HELLO 的四类指标均在批准 R 绝对门槛内，才得到 `eligibleForOneActualSyntheticRegression=true`；这只允许正式需求所述一次自有文件回归尝试，`realExecutionAllowed` 仍为 false。

## 诊断独立成本及清理

本轮诊断共2个原 R helper、8个阶段采样、2次借用原 Popen 句柄核身份、4个控制请求（各实例 HELLO/EXIT）和8个阶段 ACK。诊断 runner 单独使用1个 native worker、每实例2个 transport reader；这些是诊断独立成本，不藏入原452或误用 reader 的 `newWorkers=0/rpcCalls=0` 说明整个诊断没有线程/控制。诊断没有创建媒体对象或 fixture，testMediaBytes=0。

observer 自有句柄累计16开16关、同时最多1个；每份 snapshot 在后续 process query 前关闭，临时信用实际归还。两次身份捕获借用原进程句柄，不另 open/dup/close 借用句柄。两个原实例均实际退出 code0，transport reader 和 native worker 已 join，unknowns为空、最终账本为空，受管峰11。Add-Type 实例约0.750秒、LoadFrom约0.453秒，总约1.203秒；各阶段未超5秒、各实例未超30秒、总诊断未超90秒。计时粒度下的0.0秒不表示 native 查询没有成本。

原 diagnostic 回执中的 logBytes17,962B，连同汇总后的诊断封存成本20,698B，小于512KiB，并计入本新批4MiB。诊断时记录的 batchEvidenceBytes206,517B 是当时快照，不充当最终整包总量。全部 fixture≤2MiB、全部日志/证据≤4MiB 的最终逐文件口径以本批 freeze-summary 为准，失败证据也纳入，不能删除失败记录来满足额度。

阶段或 OS 调用若未返回，5/30/90秒是停止等待边界，不是强制打断 OS、强杀 helper、制造退出或回收未知所有权的依据。本轮原返回和清理证据完整；这个事实不保证未来不会 PENDING。

## 一次自有文件 actual-observer 回归：实际 FAIL

诊断合格后，`src/synthetic_admission.py` 在启动 G 之前以 CREATE_NEW、单次精确写及 flush/fsync 保存 [actual-regression-reservation.json](D:/CodexProjects/VideoKit/docs/coder/d1e2b/evidence/actual-regression-reservation.json)。该记录绑定原始诊断文件 SHA、规范化诊断 SHA、E2B.dll SHA、runtime-policy SHA、runId 和原 launcher PID；controller 再核原父 PID 与这些身份，并以 CREATE_NEW 写入 [actual-regression-claim.json](D:/CodexProjects/VideoKit/docs/coder/d1e2b/evidence/actual-regression-claim.json)。runId 为 `1792171193652554100`，launcher PID26784、controller PID36192。诊断规范化 SHA 为 `f3c82bb9d99dbbad68660c88a21f44967a8451b97631cef8accce77c9d55a797`，原文件 SHA 为 `bd769f76300cb9f0c098c9b83f66ef3ce96b1b5f09f6928c748ee1aa057d382c`，两种摘要含义分列。

reservation/claim 的 profile 仅为自有 `SYNTHETIC`、mockMetricsUsed=false、maximumActualRuns=1、realExecutionAllowed=false。失败不退还这一次额度。最终 [entry-denials.json](D:/CodexProjects/VideoKit/docs/coder/d1e2b/evidence/entry-denials.json) 保留第二次 reservation 拒绝 `ACTUAL_SYNTHETIC_REGRESSION_ALREADY_RESERVED`，原 reservation/claim 未改变；REAL_IO 请求及 synthetic+mock+REAL_IO 混用也均退出2、零新 helper、不创建真实 root。该模块不是真实媒体授权器，纯 JSON 门禁65断言也不替代原诊断 OS 事实。

唯一实际回归证据为 [run-selfcheck-1792171193652554100.json](D:/CodexProjects/VideoKit/docs/coder/d1e2b/evidence/run-selfcheck-1792171193652554100.json)，自有根 `selfcheck/check-20261017T011953`。mode=ACTUAL_OS_OBSERVER、mockMetricsUsed=false、外层 exitCode1、witness FAIL。本批没有 mock full，也没有在这个 FAIL 后补跑完整回归。

该回归使用自己的原 G/J/R 身份和 baseline，未沿用诊断实例499作为 R 基线：原 R PID31884 的 HELLO handles501、采样峰501；G PID36192 在 PF/n01 前的原 handles baseline160 始终保留。在 P09-TIMEOUT 的等待/控制安全点，G 采样 handles369，同时超过绝对256和原增量64（369−160=209），记录 `METRIC_THRESHOLD_EXCEEDED:G:handles` 及 `METRIC_DELTA_EXCEEDED:G:handles` 后停止新接纳。R 在这一轮满足句柄门槛不能覆盖 G 的失败，受管账本峰21/24也不能替代 G 全进程 OS 句柄指标。

原回执 rows20、reported assertions77 只描述停止前的部分进展，不计作本批 PASS 总数，也不是完整61通过。实际消耗为 N127、新query23/重放1、输入请求1,573,188B/44、validation0、目标0、记录11、output信用0；输入均为自建非媒体文件，不能把 scope 中的 mediaRead=false 误读为没有执行任何自有文件字节 IO。该行之后未运行的分支不补记成功。

停止后的原 J/R helper 均实际 wait code0；44个 private cell 全部释放，Hub CLOSED、两 worker 实际 joined、remainingCredits为空、ownershipPending=false，账本0，外层 noInFlight=true。原 reader 共4周期、14开14关、同时峰1、无 close UNKNOWN 或 pending query；最大已观察 gap 约1.687秒。global.log 实际完成 flush/fsync/close。metadata requested=written=2,593,620B、unknown0/HEALTHY，文件峰234,324B；这是累计写量与文件峰两个口径，不把成功清理写成原运行成功。

当轮 fresh availablePhysical=2,454,781,952B 达到2GiB，但内存通过不能覆盖 G 句柄超限；该瞬时值不能复用于未来批次。当前没有得到 G369 的句柄类型或根因证明，也没有获得放宽 G256/+64、R512/+128、重置基线或继续调优补跑的授权。旧 R519、本轮 Add-Type513、本轮 G369 分别完整保留。

## 断言计数、硬界及后续真实准入

选定最终定向为 [targeted-1792171365263345400.json](D:/CodexProjects/VideoKit/docs/coder/d1e2b/evidence/targeted-1792171365263345400.json)：955项 PASS，包括 E2B105、A01 alias46、诊断门禁纯逻辑65、namespace32、observer87、startup205、completion153、authority139、recovery33、metadata70、unit20。先前 [targeted-1792170977795045900.json](D:/CodexProjects/VideoKit/docs/coder/d1e2b/evidence/targeted-1792170977795045900.json) 的同955结果保留而不重复累加。诊断八阶段和实际 FAIL 单列，不加 partial77；上游 E2A 的1003及独立 Java87不是本批新增通过数。受控字典、接口故障注入和 worker 检查不冒称真实 OS 故障或媒体执行。

原61分支控制452/硬544、query101、输入硬分配1,573,522B/59、validation262,144B、10目标/32记录、输出信用655,360B、metadata峰3,178,496B、受管24/媒体6/8槽、180秒及外层200秒仅停止等待规则均不扩张。原 global.log131,072B 内 events104,320＋metrics26,752 的独立门禁、exact_write、journal/flush/fsync 和未知所有权规则保持。A01 的原控制内 metadata 与诊断的额外独立清单分别计数。

G 继续使用 PF前原基线，线程16/+12、句柄256/+64；J/R 使用各原 HELLO，线程64/+32、句柄512/+128。WS/private 的 G256MiB/+128、J768MiB/+256、R512MiB/+256不变。observer 1秒、最多201周期、gap≤2.5秒、返回后0.1秒停止规则及 fresh availablePhysical≥2GiB不变；采样值不等于绝对内核峰，停止等待不等于 OS 已返回。

继承 A02 的精确只读 L/C/Z、独立 CREATE_NEW 输出、祖先 reparse 预检及 post-open 输入物理身份拒绝，继承 A05 固定 Windows x64/JBR21.0.10 的原 RAF/FD FFM 元数据桥及查询失败原 ticket 清理。原 OPEN 的 owner 证明由核验原 Popen/PID/creation 的 HELLO、固定 Channel.owner、原 request id/私有管道和 journal 中 object/ticket 组合绑定；11fields 字串不能脱离会话作为独立 owner 证明，请求 HMAC 不等于回执另有 HMAC。祖先预检也不是防敌对目录替换的原子保证。本批结果不扩大这些既有范围。

本批没有对 `test_media` 做字节读取、stat、hash、复制或扫描。输入配置中的旧 stat、历史 SHA 和 machine 快照均是继承资料，不能证明真实输入当前内容、当前 opened 版本或未来现场资源；live version 仍 UNPROVEN。`REAL_IO` 入口、manifest/profile 执行标志保持关闭，未创建真实 runs/root。真实授权层与唯一真实批次/root 未获批准；改 JSON、approved 标志、SelfCheck 名称或使用候选别名均不能获得真实执行能力。

31个源分支维持 NONE、30个本地字节/恢复 probe 维持 OS_DATA_SYNC_ACK；Q01-SEQ、Q05-STREAM、Q06-LOST、Q08-READY、Q07-READYFIRST 的五项产品 namespace/READY 变体继续 NOT_RUN_DURABILITY_UNPROVEN。工具 READY 不产生产品 OutputToken/业务 COMMIT，不声称 namespace/掉电耐久或真实 G 崩溃重启。

本批源码、产物、manifest、诊断清单、成功及失败证据、三文档和逐文件 SHA 随新包冻结，最终总量与文件集合由 freeze-summary/只读 verify 给出；旧包不重跑、不修改。后续先由负责人独立审查 A01、两实例对照及 G 资源阻断，再裁定必要宿主兼容性工作；本窗口不自行派 tester、真实实验或第二次 actual full。宿主 JNI 继续 BLOCKED，P0/C14 与历史 FAIL 保持，D1 NOT_PASSED、M0 NOT_STARTED。本批无 Gradle、ADB、设备、NAS 或下载活动。
