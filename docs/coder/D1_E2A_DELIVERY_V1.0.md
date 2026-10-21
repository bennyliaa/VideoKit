# D1 E2A 必要适配集中交付 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2a`。按负责人E2A裁定完成A02、A05及observer接线，状态 **ADAPTERS_FROZEN_PENDING_INDEPENDENT_REVIEW**。真实入口关闭；运行时准入仍为 **BLOCKED_R_HANDLES_519_GT_512**，不能直接派真实PF或61媒体实验。

## 实现与裁定对应

| 裁定 | 实现及核验 |
|---|---|
| A02只读别名、独立CREATE_NEW输出 | `src/namespaces.py`、Native.cs Sandbox、Java输入别名及G/R接线；精确L/C/Z、所有祖先reparse预检、输入名称/路径拒绝、已存在目标拒绝、实际opened输入物理身份比较。SYNTHETIC映射仍限本包selfcheck，不能指向test_media；CANDIDATE_IO仅既存独立runs根，不产生执行授权。 |
| A05原opened FD证据 | 固定Windows x64/JBR21.0.10、preview/native-access与仅java.io开放；原RAF/FD强引用、inspect/close互斥，FFM查询原HANDLE，原OPEN回执带volume/fileIndex/length/mtime及原object/ticket；无另开/dup/借句柄close、无path/hash回退、无identity RPC。查询失败先记原分配事实，再阻断并按原ticket清理。 |
| 首字节前guard比对 | G、J及该分支原本已分配的R实际opened身份、长度及100ns mtime一致，guard仍实际持有；不在未配R的分支新增r+。失败BLOCKED_VERSION_NOT_PROVEN。 |
| 批准的指标策略 | `runtime_metrics.py`、`runtime_wiring.py`接原两worker IO池及安全等待点。G原进程PF前固定基线，线程16/+12；J/R原HELLO后基线，借原Popen进程句柄核PID/creation，不能替换或重base。1s/201/gap2.5/返回后0.1、fresh2GiB及其余批准阈值按全文实现。 |
| 预算和日志 | 原24/6/8、452/544、101query、IO、事务、32记录及180/200规则不变。observer最多1临时预留信用，无新增线程/RPC/日志文件；global.log131072内events104320＋metrics26752强制计数/exact_write，UNKNOWN后先停再查询。 |

每个原操作内有限查询、验证限制及后续准入见 `D:\CodexProjects\VideoKit\docs\coder\D1_E2A_REAL_IO_ADMISSION_V1.0.md` 和包内 `evidence/adapter-feasibility.json`。

## 选定证据与未通过记录

| 范围 | 证据 | 结果和含义 |
|---|---|---|
| 实际OS策略门禁 | `evidence/selfcheck-1792168123102649100.json` | 原执行FAIL保留；PF/n05 R baseline/peak handles519>批准512，首字节前停止，input0/0；两原helper退出0、Hub关闭、账本0。单列EXPECTED_STOP_VERIFIED，不计合成通过数。 |
| 完整自建文件回归 | `evidence/selfcheck-1792168565737747500.json` | 159项PASS，PF＋61行，root `selfcheck/check-20261017T003606`。显式SYNTHETIC_OBSERVER_MOCK，仅指标值受控；原FD桥、G/R身份、源/输出IO、helper退出与清理仍实际执行自建文件。不是实际运行时阈值通过。 |
| 最终定向 | `evidence/targeted-1792168592014078700.json` | 844项PASS：E2A105、namespace32、observer87、startup205、completion153、authority139、recovery33、metadata70、unit20。 |
| 独立Java原FD验证 | `evidence/java-bridge-1792168105652835000.json` | 10个进程、87项PASS，成功、decoy-path分离、query/field/type/symbol失败、close互斥及缺flags；缺preview预期在启动时非零拒绝，其余原对象关闭一次；全部实际退出、无在途。 |
| 真实入口拒绝 | `evidence/entry-denials.json` | request-real及synthetic＋mock＋REAL_IO均退出2、零媒体/零helper/不创真实root。 |

最终 **1003项自有/合成断言＝159＋844**，另87项Java桥检查。不累计早期失败、旧E2结果或实际策略STOP以冒充运行时准入。

保留 `selfcheck-1792168242897341600.json`：首次mock回归在P12-OLDOPEN原1秒预算触发截止，清理和原退出均完成。修复Store每次close遍历所有元数据文件的开销：真实close后只stat本文件，沿用G单写者其它文件已证大小；开放global.log以原FileIO位置和有效exact_write返回量计入，保留最终无参全量复核。没有少写、少sync、少事务或增加时间。最终P12同19控制/4数据/1query用时约0.140秒，在原1秒内；新增自有文件增量峰与最终全量stat一致检查。

保留 `targeted-1792168285935793100.json` 的namespace创建硬链接WinError5失败。最终检查如实记录hardlink/symlink未实际创建，未将跨路径别名或真实reparse成功测试算成通过；另两个实际打开的同源自有FD/fstat物理拒绝、注入reparse位、路径/名称/已存在目标门禁通过。祖先预检不是抗恶意目录替换的原子保证。

## 实际资源事实

实际OS阻断轮采3周期，G/J/R原身份与baseline保留；observer自有句柄共10开10关、同时峰1、信用0。该轮fresh availablePhysical=3,004,215,296B达到2GiB，但R519仍超512，未复采洗去或上调阈值。旧machine.json快照仍是历史资料，不替代未来新鲜现场门槛。

选定完整回归的5线程/100句柄/32MiB是明确的mock指标，不能写成OS峰。该轮只读OS身份查询3次，其中J/R借原hProcess2次；自有G查询句柄1开1关、实际counter采样0。6条mock指标连同头560B；最终global.log93462B＝事件92902＋指标560，n32前快照events92828，最后原n32事件74B仍经过事件cap。两栏始终分开。

选定完整回归351N＋83新query＋18重放＝452；input1,573,492B/59、validation128、10目标/32记录、output信用655360。受管峰23/24、媒体5/6、槽1/8，最终0；64cell全部排空，两helper实际wait code0，Hub CLOSED、无未知/worker信用0。metadata requested=written=6,401,375B、unknown0/HEALTHY、文件峰634207B，累计写与文件峰分列。关闭前摘要SHA `961bcd4949299644861580ca1aab4d468bd105d8c876a2e529c249b3044aafc2`。

## 冻结与边界

一次集中编译成功，未修复重编；三个自建文件完整回归尝试、两轮定向及一轮10进程Java验证的成功/失败证据均保留。fixture累计与日志/证据含seal的精确值见freeze-summary，保持2MiB/4MiB内。全源码/配置/上游ZIP、E2A.dll、Java class、manifest、三文档、SHA清单及只读verify齐全；旧E2 15冻结＋216自检＝231、43源文件，旧E1E188＋33源文件及13基线均保持。

本批没有访问test_media文件内容、stat或重算hash，只有已有历史文档/清单；真实PF/61媒体、runs根、NAS扫描、Gradle/ADB/设备/下载均NOT_RUN。自有合成helper及Java探针进程与受控线程已返回/退出/join，原已知IO排空，无本批在途。

下一步由负责人安排独立审查，并先处理实际R句柄超限及验证限制；本窗口不调大512、不自行派测或真实运行，也不生成能自解锁的批次/root授权。五产品namespace/READY变体继续NOT_RUN_DURABILITY_UNPROVEN，工具READY不发布产品OutputToken/业务COMMIT。有限J工具FFM批准不解除宿主JNI/P0/C14/历史FAIL；D1 NOT_PASSED、M0 NOT_STARTED。
