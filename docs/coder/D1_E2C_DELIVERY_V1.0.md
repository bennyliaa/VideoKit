# D1 E2C G 生命周期定位与有据修正集中交付 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2c`。按 [正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E2C_CODER_REQUIREMENTS_V1.0.md) 完成唯一一次原 G 六点观察，以及由历史引用证据支持的生命周期修正。**本批没有修正后的第二次 OS 对照或 actual full；不能宣称旧 G 资源阻断已经解除。** E2B G369>256、原delta209>64及旧 E2A R519>512 FAIL 均只读保持。

交付状态 **E2C_FROZEN_PENDING_INDEPENDENT_REVIEW**。只读完整性核对不产生新运行时准入；真实媒体授权层仍未批准，D1 NOT_PASSED、M0 NOT_STARTED。

## 结果与改动

| 正式裁定 | 实现 / 证据 | 结论与边界 |
|---|---|---|
| 固定一个原G、六点观察 | `tools/diagnose-g.py`；`evidence/g-lifecycle-1792172968097380400.json`＋六stage/六entered＋CREATE_NEW预约＋outer-exit | 原G26368、原creation/owner不换；0→1活→drain→8活→drain→工具history释放。句柄160/164/164/196/196/196；总9cell/同时峰8、外部首Future明确保留。全部原返回/join、G exit0，无重采/强GC |
| 查真实Python/可得同步证据 | 原runtime及`synchronization-backend.json` | CPython3.12.14、MSC1944/64位；实际`_thread.lock/RLock`与本地Python等待源码具证，但具体编译C后端/句柄类型因果UNKNOWN，不编每cell若干句柄 |
| 有据修正历史重对象 | `gengine.py`、`authority.py`、`notifications.py` | Engine活动表与不可变CellAudit历史分离；`compact_cells`在调用者已用完的原owner串行安全边界，只归档native/gate/callback/notifier/monitor/源注销/真实release均已排空者。活8/累计64/审计64，total及peak不重置 |
| 断开工具引用、保外部行为 | PendingCell.archive、DeliveryFuture、Hub局部清理 | 断开工具release/on_drain/state/authority/hub与Future.cell边，释放已返回notifier/monitor最后局部；不改外部Future结果/异常/traceback，late callback保持稳定拒绝。已知callback错误入审计、Hub停止事实不洗去；UNKNOWN不归档 |
| 接回原调用者及统计 | Engine.begin、Cleanup/phases与return-channel适配 | 不在on_drain内删活动对象；held open/read、gate、source完成后的Future.result先用完。最终统计分列total/active/history，并核总数恒等，不以删对象清除历史 |
| 禁止额外实验 | controller full、继承full/R诊断wrapper及actual reserve/claim入口 | actual/full mock/旧R诊断均明确NOT_RUN；唯一G预约不能覆盖。没有第二诊断G、修正后OS样本或新actual许可 |

本批观察的工具history是对静态确认的原Engine.cells保留模式的有限复现，使用真实生产PendingCell/Hub/Future/callback/SourceAuthority，未构造Engine、Native、Channel。首次0cell基线在两原Hub worker启动后固定，不能替代E2B原PF前baseline，也不能与E2B含J/R、IO、日志的完整场景直接相减作根因计算。

最终点工具history0但weak cells9、weak Futures9、weak closures18仍活，外部Future1仍有原值。结合源码可证历史保留与环存在，足以修正不必要边；不能证明清某条边必然减少多少OS句柄。本批没有在修正后再采样证明OS资源已达门槛。

## 验证与证据选择

最终选定 `evidence/targeted-1792173615310105000.json`，**12组、1,125项PASS**＝E2C105＋alias46＋diagnostic纯逻辑65＋新增lifecycle170＋namespace32＋observer87＋startup205＋completion153＋authority139＋recovery33＋metadata70＋unit20。原C01/C02/D01/T02–T05及A01认可保持。只运行一轮本批定向，不将旧包、六观察点或入口拒绝数量累加进1,125。audit与冻结摘要保存同一选定结果；actualFull仍NOT_RUN/通过0。

专项检查覆盖：8活拒绝第9个、累计64拒绝第65个、不可变有界审计、notifier已释放private资源但原发布调用尚未返回时不能归档、monitor在途、native/gate/callback未排空、外部Future/值/异常身份及晚callback、晚完成/取消竞争和历史事实不重置。UNKNOWN方面，专项直接故障注入验证submit UNKNOWN；publication/release UNKNOWN是生产archive的静态拒绝条件，未冒称另做两类实际故障实验。检查是有界自有逻辑与真实Python线程/Future，不构成新增OS对照或61完整回归。

必要工具编译一次、修复重编0，pwsh7.6.5/.NET10.0.11/JBR21.0.10；`artifacts/E2C.dll` SHA256 `3af9ad9a3429e94eed48a6525bc6ee8f031255e6ba6c27bcea5140029834beae`。C#/Java仅编译，没有启动J/R或再次10进程桥验证。原运行时policy文件与E2B逐字节相同，不提高G256/+64、R512/+128、线程/内存阈值，不改原baseline、预算或超时。

`entry-denials.json`分别保留真实请求、controller full/full mock、混用REAL_IO、继承full及R诊断的拒绝；actual reserve/claim也先拒绝。通过构造守卫确认未进入Engine/Native/observer/Hub/Popen；仅尝试对既有G预约的CREATE_NEW产生FileExistsError，原hash不变，没有再次调用诊断run。

## 成本、关闭与封存

唯一实际诊断：1原G、2原Hub线程、6samples、1原身份查询、observer13开13关/同时峰1；独立账本峰3，buffer信用峰8/最终0，9次真实release/source drain/callback均完成，Hub两原worker实际join、账本0、原命令exit0。总约0.047s≤60，sampleDuration0.0是记录粒度，未声称零成本；6点之后没有第7个OS样本。不可中断调用若未返回仍PENDING，不强杀或伪关闭。

原诊断报告60,966B为当时快照，outer-exit和其它证据另外计最终量。诊断≤512KiB，整批fixture≤2MiB、日志/证据含seal≤4MiB，精确逐文件口径见freeze-summary。集中保存源码/编译产物、manifest、修正前四文件、原六点、引用与同步证据、修正差异、有界检查、全部拒绝及三文档。source ZIP、逐文件hash和只读verify齐全，不删失败/未知证据换预算。

旧E2B199条冻结/自检记录（27＋172）、63源文件及全部旧关系逐hash核验。E2B freeze SHA `93941847231390a5ffe4af8656cb5ce8d3120b9c07a16dcf55fcc9d802bf9ab0`；旧source ZIP3,141,738B/SHA `05eef8aa55013603070fc9fd77ac2adb6ff916ab73825ef7f8e6456ad9a26c43`。更早E2A326/53、E2231/43、E1E188/33及13基线也保持。旧E2B955、partial77/完整通过0、E2A1003及另87桥检查均不当本批新增通过数。

本批未读取/stat/hash `test_media`，未真实PF/61、未建真实runs/root、未J/R、NAS、Gradle/ADB、设备或下载。单次诊断及所有选定逻辑检查的原受控线程已实际返回/join，无本批在途；不承诺外部持有的任意值/traceback已被Python立即回收。

后续先由负责人安排独立审查；如果需要证明OS效果，应另行授权绑定本次修正hash的有限对照，再决定是否另派新actual自有回归。本窗口不自授第二G或重用E2B已消费许可。五产品namespace/READY仍NOT_RUN_DURABILITY_UNPROVEN，工具READY不发产品OutputToken/业务COMMIT；宿主JNI继续BLOCKED，P0/C14/历史FAIL不变。

配套 [RESOURCE_LIFECYCLE](D:/CodexProjects/VideoKit/docs/coder/D1_E2C_RESOURCE_LIFECYCLE_V1.0.md) 与 [EXECUTION_APPENDIX](D:/CodexProjects/VideoKit/docs/coder/D1_E2C_EXECUTION_APPENDIX_V1.0.md)。
