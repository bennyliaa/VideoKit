# D1 E2C 执行清单、修正差异与只读复核附录 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2c`。本文件记录已执行的有界工作，不授权重跑。**唯一原G诊断已结束；本批没有修正后的第二次OS观察、实际完整61或真实媒体执行。** 旧E2B G369/+209 FAIL保持，修正效果待负责人另派验证。

## 本批活动与原凭据

| 活动 | 数量 / 证据 | 范围 |
|---|---|---|
| 原G生命周期诊断 | 1次；g-lifecycle-1792172968097380400.json | 原PID26368/creation134366465678168526，6固定点；首基线不重置；无Engine/Native/Channel/J/R/媒体 |
| 预约、阶段与原退出证明 | reservation1、entered6、stage6、outer-exit1 | CREATE_NEW预约在Hub/cell前；每点只一次OS样本；原exec exit0，不起新G补证 |
| 本地同步源码核对 | synchronization-backend.json | 仅读取实际Python/配套头/DLL文件；新OS采样0，具体编译C锁原语和句柄类型因果UNKNOWN |
| 有据生产修正 | src/authority.py、notifications.py、gengine.py、phases.py及必要return-channel | 保先排空再归档、外部Future原终态、活8/总64/immutable历史64；具体before/after SHA见lifecycle-change-map.json |
| 一次工具编译 | build.json，E2C.dll/Java classes | compile1/repair0，未运行J/R，不是新actual |
| 有界合成检查 | targeted-*.json，由audit选定最终PASS | 12组含lifecycle；真实生产方法/有界Python线程/Future，自有fixtures；不采OS、不运行full |
| 范围外入口拒绝 | entry-denials.json | CLI/API拒绝、唯一G预约不可替换；构造守卫未进入，不启动任何诊断/helper |
| 集中只读核对与封存 | audit/source-manifest/freeze-summary、E2C-source.zip | 所有旧失败与本批原证据保留，逐hash核验；完整性PASS不等于新OS准入 |

最终选定一轮 `targeted-1792173615310105000.json`，12组1,125项PASS，其中lifecycle170；entry-denials的7CLI/2API/预约拒绝单列，不加进断言总数。本批没有重跑定向、诊断或完整61。audit与封存输出保存同一计数；旧E2B955/partial77不累加。

## 六点执行及原身份

阶段预定为ZERO_CELLS、ONE_LIVE、ONE_DRAINED、EIGHT_LIVE、EIGHT_DRAINED、TOOL_HISTORY_RELEASED。两原Hub worker先启动，再对0cell采固定baseline；先1个实际drain，再8个同时活cell/实际drain，最后释放工具history且保留首外部Future。没有创建9个同时活cell、第二诊断G或强制GC。

原G owner `E2C-G-1792172968097380400`，同PID/creation锚贯穿全部周期。各阶段指标、引用、callbacks/drains、observer facts和Hub事实分别保存原stage文件，汇总JSON需与六stage完全相等；entered marker只证明进入调用，不能在调用未返回时伪造成样本。

句柄序列160/164/164/196/196/196，ZERO增量0/+4/+4/+36/+36/+36；线程均6，private均14,954,496B，WS24,637,440→24,686,592B。原报告完整保存八类引用计数及GC计数，末点history0、externalFuture1、weak cells9/Futures9/closures18。外部Future原结果仍稳定，不撤销或换值。

这些是在修正前保存的生产PendingCell/Hub源码上所做的观察，**不是修正后的资源对照**。源码基线四文件位于artifacts/diagnostic-source-before，并由原report逐hash绑定；以后产物/源码修改不能回写这些旧观察。对象存活及总数相关性不能用于直接推算E2B完整运行中的209增量根因，具体编译同步C后端与类型归因仍UNKNOWN。

diag reader6周期＋identity1＝13开13关、同时峰1；无observerUNKNOWN、信用0。独立受管峰3、buffer信用峰8/最终0，9次release/drain/callback已返回。末点后实际Hub.close/join原两worker，THREAD_JOIN_PROVEN、closed/ownershipPending false、ledger0，随后原G命令exit0。没有第7次OS采样来填“关闭后峰”；outer-exit是原caller观察，而非另启动进程查询PID。

≤60秒为决策/清理边界，约0.047s为本轮原记录；不可中断OS若未返回仍保entered marker/原PID和PENDING，不重复查询、重启、强杀或推断已关闭。诊断原报告60,966B含当时reservation/stage/entered/report；最终含outer-exit等的精确诊断量由audit给出，不能改原快照字段冒充后来总量。

## 生命周期修正的调用合同

`Engine.compact_cells()`仅在原owner线程的串行安全边界运行。源native/消费者gate/notification/callback真实排空、release与on_drain成功、SourceAuthority注销、Hub逐cell cells/deadlines/queue/active/monitor处理均静默之后，才生成冻结CellAudit并从活动重对象表移除。on_drain内不删Engine表，Future.done/released/drained任一单项不足以归档。

总cell数单调≤64，活动表≤8，历史tuple≤64、peak保原值，`total=active+history`核对；归档不返总历史配额。终态快照只含有界纯字段，不含值、Future、异常、锁、闭包、Engine或可变dict。已知callback异常在真返回后保错误审计与原Hub.blocked；提交/发布/release未知或monitor/notifier尚在处理则保原重对象和停止事实。

外部Future及value/exception保持原对象和原终态；不清外部traceback，不推断任意外部持有对象即时回收。Future.cell解绑后晚callback仍稳定CALLBACK_REGISTRATION_CLOSED。工具release/on_drain/state/authority/hub等边只在有据静默时断开；notifier/monitor局部也在原调用真正返回后释放，不能提前还通知容量。

原held/gate/complete_source_response仍先用完原cell/Future；Cleanup并列活动与历史，未返回native、未知owner、回调/通知未返回继续保留。原IO Future完成后移除pending的规则不改；未完成Future绝不当作可归档已返回。

新增lifecycle专项只调用生产方法与真实Future/Hub，无Engine/Native/Channel构造、无OS指标读取；覆盖容量64/8、notifier返回屏障、monitor in-flight、外部持有、晚完成、取消、回调与UNKNOWN。其它继承定向组保留既有自有文件/Native元数据检查，例如A01与namespace；这些自有操作不是额外G生命周期OS采样或J/R/完整回归。修正后的OS效果与新actual准入必须由负责人另授，不从逻辑PASS推导。

## 只读复核命令与封存口径

在项目目录运行以下命令核已有源、产物、ZIP、三文档、阶段/引用/拒绝/检查回执、上游hash，以及原本机Python DLL/头文件hash；不编译、不启动G诊断/J/R、不查OS指标或媒体。若本机runtime后来更新，这项原环境hash复核会报不符，不能据此改写本包旧观察。

```powershell
& 'C:\Users\benny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -B 'D:\CodexProjects\VideoKit\docs\coder\d1e2c\tools\verify.py'
```

预期完整性PASS、state E2C_FROZEN_PENDING_INDEPENDENT_REVIEW、actualFullStatus NOT_RUN、actualFullAssertions0、realMedia NOT_RUN；runtimeAdmission保留来自E2B的G369/256及delta209/64阻断，无新OS准入。源码ZIP字节/hash、freeze SHA、source/frozen/selfcheck文件数、fixture及日志/证据含seal精确值以冻结摘要和verify输出为准，避免文档自引用。

原E2B freeze SHA `93941847231390a5ffe4af8656cb5ce8d3120b9c07a16dcf55fcc9d802bf9ab0`，source ZIP3,141,738B/SHA `05eef8aa55013603070fc9fd77ac2adb6ff916ab73825ef7f8e6456ad9a26c43`；199记录/63源逐hash保持。更早E2A326/53、E2231/43、E1E188/33及13基线同样核验。旧E2B955、partial77、E2A1003/另87桥不累加本批通过数。

不访问test_media字节/stat/hash，不运行真实PF/61、不建真实runs/root，无NAS/Gradle/ADB/设备/下载；真实启动授权层未批准。五产品namespace/READY、JNI/P0/C14/历史FAIL保持，D1未通过、M0未启动。完整交付后只向负责人报告，不自行派tester或执行新的OS/actual实验。
