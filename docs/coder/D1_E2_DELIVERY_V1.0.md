# D1 E2 配置与准入准备交付 V1.0

2026-10-16。E1E复审D01及前项静态闭合后，按E2需求在 `D:\CodexProjects\VideoKit\docs\coder\d1e2` 完成真实IO候选配置、机器绑定、关闭的真实入口、显式profile适配、只读OS指标准备组件及集中验证。状态 **CONFIGURATION_FROZEN_PENDING_ADMISSION_REVIEW**。本批不是准许真实执行；A02输入/输出绑定及A05 Java opened-FD桥仍明确待适配，交具体可行方案，请负责人安排独立准入审查后决定后续批次。

## 配置及必要适配

- `profiles/inputs.json`：精确R2 L/C/Z路径、历史SHA/来源文档SHA、长度、现场stat和真实2GiB四窗口；三长度相符，未读媒体字节或重算hash，未查祖先reparse，不冒称版本已证。
- `profiles/cases.json`：61行继承R4全部分配，逐case列真实/注入IO、窗口/请求、输出和durability。31源NONE、30输出OS_DATA_SYNC_ACK条件probe；5个产品namespace/READY变体NOT_RUN_DURABILITY_UNPROVEN，不发布业务COMMIT。
- `profiles/machine.json`、`runtime-policy.json`：只读本机快照、版本路径、受管24/6/8与原G/J/R运行时指标分栏、1秒/201周期和有限阈值提案；PROPOSED未批准。当前快照可用内存低于提出的2GiB门槛，未来须新鲜检查和负责人决策。
- `src/profile_bindings.py`、Engine/Scenarios：显式SYNTHETIC/REAL_IO几何，去掉按目录名猜B；Engine在Native/目录之前只允许严格合成绑定，不能把真实素材改名SelfCheck运行。
- `src/admission.py`、controller REAL_IO分派、launch Inspect/RealAdmission：只读配置、核原预算和派生用量；真实请求固定非零且不创建目录/启动helper，假approved/stat不升级版本。
- `src/runtime_metrics.py`：纯mock策略检查及显式Win32只读元数据reader，原PID/creation身份、缺指标/阈值/间隔/样本耗尽停止；一个observer信用/最多一个临时句柄，不增线程/RPC。未接真实runner，不表示真实policy已批准。

差异/方案在 `D:\CodexProjects\VideoKit\docs\coder\d1e2\evidence\adapter-feasibility.json`；逐窗口、版本门槛、durability与阈值全文见同目录上层 `D1_E2_REAL_IO_ADMISSION_V1.0.md`。J现有path属性不能证明其opened FD与G/R同对象；未新做JNI/FFM桥，缺证明必须真实读取前BLOCKED_VERSION_NOT_PROVEN。guard/ref未分配的分支不偷加控制。observer日志分配和接线仍待审，不暗增文件/总量。

## 选定验证与证据

| 范围 | 证据与结果 |
|---|---|
| 完整合成适配 | `evidence/selfcheck-1792165512531930500.json`；159项PASS，执行根 `selfcheck/check-20261016T234512` |
| 最终定向 | `evidence/targeted-1792165801504473800.json`；716项PASS：E2 97、D01 205、C01/C02 153、源owner139、恢复33、短写69、通用20 |
| 配置进程元数据绑定 | `evidence/observer-self-1792165801337125700.json`；另6项PASS，只当前配置Python进程，不是实验G/J/R基线或峰值 |
| 实际入口拒绝 | `evidence/entry-denials.json`；request-real及混合synthetic-selfcheck+REAL_IO均退出2、执行关闭、未创真实输出根 |
| 只读审计 | `evidence/audit.json`；配置/来源文档/预算/恢复/原关闭事实/逐worker事实及旧包均一致 |

最终 **875项合成断言**（159＋716），另6项配置元数据绑定检查，不将早期712项定向或旧E1E778重复累计。E2组含真实窗口/历史身份/61预算篡改负例、stat不作版本、namespace不降级、假批准与零副作用门禁，以及mock指标的缺失/身份/阈值/间隔/201周期停止。静态审查发现非零window可用charge=false漏计后已修并补4负例；真正bridge零请求仍允许。没有继续扩旧异常框架。

本批一次本地编译、一轮完整合成、两轮定向（早期712保留）、一次自有进程元数据检查。元数据reader实际只开snapshot和自身query两个句柄，先后关闭、同时峰1、剩余信用0；观测仅当前配置进程4线程/140句柄/工作集21,393,408B/private12,365,824B，不外推未来G/J/R。

完整合成351N＋83新query＋18重放=452；请求1,573,492B/59、验证128、目标10/记录32、输出信用655360；64cell全排空，两原J/R实际wait code0、Hub CLOSED/无未知/信用0。受管峰23/24、媒体5/6、槽1/8，最终0。metadata requested=written=6,397,708B、unknown0/HEALTHY、文件峰630540B，累计写与文件峰分列。fixture累计135244B；日志/证据冻结前精确量见freeze-summary，在2MiB/4MiB内。本批全部构建/工具/合成helper/受控线程/已知IO已返回，无在途。

## 冻结与边界

完整源码/配置依赖ZIP、E2.dll、JavaHelper*.class、manifest、source-manifest/freeze-summary、只读verify及三文档齐全。upstream-e1e嵌套保留E1E/E1D/E1C/E1B/E1源码身份；旧E1E 11冻结＋177自检＝188和33源码均SHA一致，13项R1–R4基线保留。原E1E只读verify亦PASS，未修改旧包或失败证据。

原C01/C02、D01、T02–T05和受限Future/实际drain/部分启动UNKNOWN方案保持。原媒体仅3项精确stat，媒体读取/hash为0；真实PF/61媒体、Gradle/ADB/设备/下载/正式run为NOT_RUN。数据sync不等namespace/掉电耐久，采样峰不等内核绝对峰，875项不代表真实版本/durability/总资源通过。JNI/P0/历史FAIL/C14保持，D1 NOT_PASSED、M0 NOT_STARTED。冻结后主动报告负责人，不自行派tester或真实执行。
