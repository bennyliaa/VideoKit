# D1 E2B 别名修复与 R 启动资源定位集中交付 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2b`。按 [E2B 正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E2B_CODER_REQUIREMENTS_V1.0.md) 完成 A01 修复、预定两实例八阶段诊断，以及候选合格后唯一一次自有文件 actual OS observer 完整回归尝试。**最终定向 955 项 PASS；唯一完整回归尝试 FAIL，未完成全 61 分支。当前阻断为 G 句柄 369>256，较原 PF 前基线 160 增长 209>64。该次额度已消费，不补跑。**

交付状态 **E2B_FROZEN_PENDING_INDEPENDENT_REVIEW**。只读完整性审计通过只表示证据与封存一致，不表示运行时准入通过。真实媒体入口关闭；D1 NOT_PASSED，M0 NOT_STARTED。

## 改动与证据

| 正式要求 | 实现 | 本批结论 |
|---|---|---|
| A01 分离输入/输出后仍识别 C 别名 | `src/gengine.py:Ops.grant` 在原 grant 内使用 `Namespaces.input_path('C')` 与原已证物理身份，先登记原对象再验证；保持只读 open/query/close 与失败原对象账目 | `alias_checks` 四活动链 case、46 项通过，正常拒绝 INPUT_ALIAS；无 C 输出副本、delegate 字节 0、无新增 N/RPC。受控 query/identity/close 回执负例按注入范围标记 |
| 有限 R 启动定位 | `RHost.RunDiagnostic` 共用原初始化，只接受 HELLO/EXIT；`tools/diagnostic-r.ps1` 固定 Add-Type 和绝对路径 Assembly.LoadFrom 两个原实例，每个四阶段同步暂停 | 同 DLL、pwsh7.6.5/.NET10.0.11；八个实际 OS 样本具原 PID/creation/owner。Add-Type HELLO 首次超限 513>512；LoadFrom HELLO499，满足唯一自有实际回归启动条件 |
| 原实例/预算/清理不换证 | `tools/diagnose-r.py` 在创建任何进程前 CREATE_NEW 预约，单独诊断账本、单临时 observer 句柄、原进程 creation 锚及受控 ACK；`diagnostic_gate.py` 纯证据校验 | 2 R、8 metric samples、2 借用身份查询、4 HELLO/EXIT 请求、8 ACK；16 observer 开/关，峰1；总约1.203s，账本峰11/24、最终0，原实例退出0 |
| 合格后至多一次 actual full | `synthetic_admission.py` 校验并绑定诊断原文件与规范摘要、DLL、policy；外层 CREATE_NEW reservation 先于 G，原 G 再 CREATE_NEW claim；真实 profile 先拒绝 | 唯一尝试在 P09-TIMEOUT 因 G 句柄触限停止；77 为失败前局部断言，完整回归通过计数0。无第二实际尝试、无本批 full mock 替代 |
| 历史事实与真实执行边界 | 旧包只读；E2A R519 FAIL、原预算及 G/J/R baseline 规则保持 | 本批 R 实际回归自己的 HELLO501≤512，不消除新的 G 超限。未提高阈值、未重采洗去、未换 runtime/owner/flags、未强制 GC 或关闭 CLR 内部句柄 |

生产 R 启动使用固定绝对 DLL 的 `Assembly.LoadFrom`；自有路径计算/存在检查改用 `System.IO.Path`/`File.Exists`。这是本批候选加载实现。两实例仅证明本轮阶段总数与差异，不能识别句柄类型、给出因果分解，或保证稳定减少 14 个/7 个句柄。G 超限也仅有计数与原 baseline 证据，本批未增加根因实验或擅自修复。

## 选定结果及计数范围

| 范围 | 证据（包内） | 结果 |
|---|---|---|
| 一次集中编译 | `evidence/build.json`、`artifacts/E2B.dll`、Java class | 编译1次、修复重编0；JBR21.0.10，保既有限 FFM flags |
| 最终有界定向 | `evidence/targeted-1792171365263345400.json` | **955 PASS**＝E2B105＋A01 46＋diagnostic65＋namespace32＋observer87＋startup205＋completion153＋authority139＋recovery33＋metadata70＋unit20 |
| 固定实际启动诊断 | `evidence/diagnostic-1792171021038062900.json`、`diagnostic-summary.json` | 两实例八阶段，候选诊断门禁合格；Add-Type513 超限保留；两个原实例均退出0、无在途 |
| 唯一自有文件 actual-observer 完整回归尝试 | `evidence/run-selfcheck-1792171193652554100.json` | **FAIL**；PF＋19分支共20完成行，P09-TIMEOUT 进行中触限。reported77、passedFull0，未完成全61，不计入955 |
| 真实入口与一次性拒绝 | `evidence/entry-denials.json` | request-real、synthetic＋mock＋REAL_IO 均退出2；媒体0/helper0/不创真实 root。第二 reservation 直接拒绝，原 reservation/claim 未改，无新 helper |
| 只读证据审计及封存 | `evidence/audit.json`、`source-manifest.json`、`freeze-summary.json`、`artifacts/E2B-source.zip` | 审计/verify PASS 的含义为包完整、成本与原事实一致；actualFullStatus 仍 FAIL |

早先 `targeted-1792170977795045900.json` 同为955，保留但不累加。旧 E2A 选定1003及另87 Java桥断言只作历史关系，不计本批；本批没有再跑10进程桥验证、没有新增 full mock。本批最终通过数仅955。

## 唯一实际回归的资源与停止事实

根为 `selfcheck/check-20261017T011953`，原 G36192/J13856/R31884 的身份、creation 与 owner 保存在原回执。G baseline 固定于原进程 PF/n01 前，J/R 使用本次原 HELLO，未沿用诊断499或旧519作为新基线。

| 角色 | baseline：线程 / 句柄 | 采样峰：线程 / 句柄 | WS baseline→采样峰 B | private baseline→采样峰 B |
|---|---|---|---|---|
| G | 5 / 160 | 11 / **369** | 25,227,264→26,075,136 | 15,536,128→16,125,952 |
| J | 25 / 268 | 25 / 268 | 63,524,864→70,283,264 | 369,745,920→373,788,672 |
| R | 25 / 501 | 25 / 501 | 83,193,856→86,589,440 | 26,685,440→27,697,152 |

这些是有界离散采样峰，不是连续 OS 全程最大值。第4周期记录 G 的绝对及 delta 两条失败原因。触限周期证据保留在原 observation/failure/preclose；global.log 只含3条正常周期 metric，不补写失败采样伪装完整观察。最大周期间隔1.687s；observer14开14关、同时峰1、最终信用0，无 pending query。新鲜可用内存2,454,781,952B达2GiB，仅证明该轮内存门槛。

停止时部分 usage：127N＋23新query＋1 replay，input1,573,188B/44 calls、validation0、目标0/记录11、output信用0。受管峰21/24、媒体3/6、槽1/8；原 J/R 均实际 wait exit0。44个 private cells 全释放，callback Hub CLOSED、原 worker join、worker信用0；global.log 关闭已证，最终账本0、外层 `noInFlight=true`。业务状态中的 UNKNOWN 与物理资源清理事实分列，不把未知业务提交当成成功。

metadata requested=written=2,593,620B、unknown0/HEALTHY、文件峰234,324B；这是累计写量与瞬时文件峰两个概念。最终 global.log36,951B＝events36,555＋metrics396，分别在104,320/26,752 cap内；原n32最后事件仍通过 exact_write 计数。关闭前摘要 SHA256 `623bc77602fdb668336b1955f54db74cf57724e0846a5573e831963f14664f02`。

## 封存、承接与后续

诊断日志（含 reservation、summary）20,698B≤512KiB；原报告17,962B是当时含 reservation 的快照，不回写成后来总量。整批自有 fixture、日志/证据含 seal 的最终精确量和每文件 SHA256 由 `freeze-summary.json` 给出，保持2MiB/4MiB内。全部诊断、两轮定向与唯一 FAIL 原文件保留，不清理失败证据换预算。

旧 E2A326条冻结/自检记录＋53源文件、旧 E2231＋43源文件、旧 E1E188＋33源文件、13基线均只读逐hash核验。继承的 A02 路径预检仍不是抗恶意祖先替换的原子保证；此环境未实际创建成功跨路径 hardlink/symlink，保留限制，不当作通过。A05 仅固定 Windows x64/JBR21.0.10 原 FD 的有界工具桥，不解除宿主 JNI/P0/C14/历史 FAIL。五产品 namespace/READY 变体仍 NOT_RUN_DURABILITY_UNPROVEN，工具 READY 不发布产品 OutputToken 或业务 COMMIT。

本批没有读取、stat、hash `test_media` 对象，没有真实 PF/61、真实 runs/root 创建、NAS扫描、Gradle/ADB、设备或下载。实际活动仅为自有定向文件、固定诊断与上述唯一自有回归；进程及受控线程均退出/join，无本批在途。

负责人后续需先安排独立审查并裁定新的 G 资源阻断；真实执行授权层及绑定冻结hash的唯一真实批次/root尚未批准。本窗口不自行派 tester 或真实实验，不复用已消费的实际回归许可。配套细节见 [REAL_IO_ADMISSION](D:/CodexProjects/VideoKit/docs/coder/D1_E2B_REAL_IO_ADMISSION_V1.0.md) 与 [EXECUTION_APPENDIX](D:/CodexProjects/VideoKit/docs/coder/D1_E2B_EXECUTION_APPENDIX_V1.0.md)。
