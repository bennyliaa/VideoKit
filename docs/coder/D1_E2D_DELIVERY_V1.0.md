# D1 E2D 修后 G 固定六点 OS 对照交付 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2d`。按 [正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E2D_CODER_REQUIREMENTS_V1.0.md) 完成唯一一次修后小范围OS对照，生产源码、配置和依赖产物逐字节绑定已冻结E2C。**六点均无批准指标超限；两次真实排空及生产归档后，重cell/闭包弱引用均为0，首外部Future及原值仍保持。** 这是一个G、累计9/峰8 cell的证据，不等于完整Engine准入，不解除旧G369/+209及R519 FAIL。

状态 **E2D_FROZEN_PENDING_INDEPENDENT_REVIEW**。本批没有改生产代码、重编、另跑定向或actual full；没有第七次采样、第二诊断G、强GC/禁GC或重启择低。真实媒体授权层未批准，D1 NOT_PASSED、M0 NOT_STARTED。

## 唯一实际结果

证据 [g-comparison-1792174935530529100.json](D:/CodexProjects/VideoKit/docs/coder/d1e2d/evidence/g-comparison-1792174935530529100.json)，status `OBSERVED_POSTFIX_SIX_POINTS_WITHIN_LIMITS`；六stage与六entered、CREATE_NEW预约、production-binding和原caller exit0回执一并保留。原G PID35964、creation100ns `134366485352518462`、owner `E2D-G-1792174935530529100`。

| 固定点 | 线程 / 句柄 | 较本ZERO句柄差 | active / archived / total | weak cell / Future / closure | probe审计副本数 |
|---|---|---:|---|---|---:|
| ZERO_CELLS | 6 / 160 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 |
| ONE_LIVE | 6 / 164 | +4 | 1 / 0 / 1 | 1 / 1 / 2 | 0 |
| ONE_DRAINED_COMPACTED | 6 / 161 | +1 | 0 / 1 / 1 | 0 / 1 / 0 | 1 |
| EIGHT_LIVE | 6 / 193 | +33 | 8 / 1 / 9 | 8 / 9 / 16 | 1 |
| EIGHT_DRAINED_COMPACTED | 6 / 161 | +1 | 0 / 9 / 9 | 0 / 1 / 0 | 9 |
| PROBE_AUDIT_COPY_RELEASED | 6 / 161 | +1 | 0 / 9 / 9 | 0 / 1 / 0 | 0 |

ZERO在本实例两原Hub worker启动后固定，未借旧160、未后移或重base；它与E2C数值恰同不表示复用基线。全部线程/句柄/WS/private绝对及增量在批准界内；WS从27,082,752至27,185,152B，private均18,104,320B。以上是离散六点采样，不是连续内核全程峰。

观察支持本实例在真实排空/归档后不再由工具持有已完成重cell及闭包，且原外部Future仍有效。末点只clear额外审计副本，生产 `cell_total=9/cell_history=9/cell_peak=8/active=0` 保持，未通过删生产历史或退款获得低数。外部首Future在最终Hub关闭后仍持有且 `result() is` 原value。末点+1既不要求归ZERO，也不把它具体归因于某一类OS句柄；每cell固定句柄数、精确编译同步C后端及类型因果仍UNKNOWN。

## 生产路径、绑定与调用者边界

`tools/compare-g.py` 只新增轻量Probe，直接绑定实际 `gengine.Engine.private_cell/compact_cells/cell_facts`，运行时校验函数对象身份并记录方法名；不构造Engine、Native、Channel，不J/R或媒体。创建函数只让首外部Future逃逸，其余cell/Future/闭包仅存weakref；生产活动表由生产方法管理，未手清dict替代归档。

消费函数依次执行原cell.complete、gate、读取原Future.result，并在Hub.condition下确认该cell notifier/monitor静默及源operation done/nativeReturned，返回仅标量证明。该调用者及谓词帧返回后，原creator才调用compact，分别实际归档1与8。引用统计函数只返回标量/纯审计视图，并在OS查询前返回，不以最后循环变量或批列表强持历史cell。生产原锁顺序、UNKNOWN/通知容量及外部Future行为均未改。

实际CPython3.12.14/MSC1944/64位、python312.dll SHA `2b6fffde96cf24a57fca642aaefd5788816ab5ef8624ea63b722cbceb94d49b1` 与E2C一致；GC原启用、阈值700/10/10，forceGC0。原probe SHA256 `6975917a764cde4db387c35ddd93a902ba37433e072eb092d7ace598ebcaca46` 随原回执保存，执行后未修改此脚本。

`production-binding.json` 在Hub前核：E2C freeze `bccacb2e98b1f4a4d3017fc8efb9bd0f047e58d91e7c910303fff40eb3896179`，source ZIP `035263006cbaa99837656bb2b66045a3f5c6181ab8af8c8fe3f5bcf5ba3e5934`；source-manifest本身须与freeze内记录相等，再核本包32源文件＋manifest/profiles共37文件及E2C.dll/9 class共10原产物。E2C命名、manifest/profile历史路径保留原样以保持字节绑定，不生成新的真实授权。

## 成本、退出与复核

诊断成本单列，未冒称原452内零成本：1原G、2生产Hub worker、6metric samples、identity1；原9次source admission/private cell creation/逻辑native completion/gate/Future消费/callback均完成，正常compact2，失败收尾complete/gate/consume/compact各0。没有文件native读写或媒体fixture，fixture0；observer13开13关、同时峰1、信用先留后开/实际close才返，独立账本峰3、buffer信用峰8/最终0。

末点后实际Hub.close，两原worker join、THREAD_JOIN_PROVEN，CLOSED、remainingCredits空、ownershipPending false；账本0、无observer UNKNOWN/pending。原命令实际exit0，outer-exit只记录该原caller结果，不另起G查询。总约1.125s≤60；最后样本约0.015s≤0.1，其余0.0为时钟粒度，不表示零成本。没有第七个“关闭后样本”。

原报告的100,630B为生成时g-comparison前缀文件快照，不含后加outer与独立production-binding；最终诊断总量与整批含seal精确量见audit/freeze-summary，保持诊断512KiB、日志/证据4MiB、fixture2MiB。完整源码依赖、原产物、绑定与六点/引用/退出证据、三文档、ZIP/逐文件hash/只读verify齐全。

本批当前targeted/compile/full断言计数均0，六观察点不计测试断言。旧E2C1125（含lifecycle170）只作历史；E2B955/partial77/通过0、E2A1003/另87均不累加。本包只读核验E2C103条冻结/自检记录（41＋62）与70源、更早E2B199/63、E2A326/53、E2231/43、E1E188/33及13基线，原失败证据未改。

只读verify的PASS只证明绑定/记录/成本/封存一致；当前小probe无超限不证明完整Engine的G256/+64门槛已通过。原61预算、policy及G/J/R全部门槛、baseline/日志/超时规则保持。后续是否另授新的actual自有回归由负责人裁定，本窗口不自派tester/full，不重用E2B已消费许可。

未test_media字节/stat/hash、真实PF/61、真实runs/root、J/R、NAS、Gradle/ADB、设备或下载。JNI/P0/C14/历史FAIL及五产品namespace/READY限制保持。配套 [G_OS_COMPARISON](D:/CodexProjects/VideoKit/docs/coder/D1_E2D_G_OS_COMPARISON_V1.0.md) 与 [EXECUTION_APPENDIX](D:/CodexProjects/VideoKit/docs/coder/D1_E2D_EXECUTION_APPENDIX_V1.0.md)。
