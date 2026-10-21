# D1 R3 集中修订交付回执 V1.0

2026-10-16。交付范围：依据[D1_R3_CODER_REQUIREMENTS_V1.0](D:/CodexProjects/VideoKit/docs/milestones/D1_R3_CODER_REQUIREMENTS_V1.0.md)，回应[R2独立评审](D:/CodexProjects/VideoKit/docs/tester/D1_R2_REVIEW_REPORT_V1.0.md)的R2-R01–R03。仅离线设计及文档静态核对；本批未实现、未执行provider/输出实验，无产品编码、构建、Gradle、ADB、新候选或设备测试。**交付完整包待独立评审，D1未通过、M0未启动，宿主JNI仍BLOCKED。**

## 1. 本批三份文件与主体身份

| 文件 | SHA-256（文件原始字节） | 用途 |
|---|---|---|
| [D1_R3_CLOSE_AND_WRITER_CONTRACT_V1.0.md](D:/CodexProjects/VideoKit/docs/coder/D1_R3_CLOSE_AND_WRITER_CONTRACT_V1.0.md) | `c91743c74bab78ea854c4e5f6dbe7bd2c09da6e3428641f3b31db158323ebb44` | close disposition、稳定ticket、安全重试与writer grant/delivery/claim/逐引用清理 |
| [D1_R3_BRANCH_MANIFEST_V1.0.md](D:/CodexProjects/VideoKit/docs/coder/D1_R3_BRANCH_MANIFEST_V1.0.md) | `6b5cb83a9e67fc7de69cac0817f53e29e6ee82b69e9defc781504e0a148e569b` | 61分支冻结计划、共享任务、逐行预算和停止记账 |
| 本回执 | 不嵌自引用hash；通知负责人时另给实际文件hash | 问题映射、自查结果、冻结边界与下一步条件 |

本轮仅新增/修订上述三份R3文件；未将素材确认当交付，也未启动字幕测试。历史材料的链接、hash及现成完整性核对只读使用，不生成新的实验结果。

## 2. R2三问题映射与冲突覆盖范围

| 评审项 | 本批设计落点与具体修订 | 仍待证明 |
|---|---|---|
| R2-R01：close资格与实际释放 | 契约§1–3。区分确定未调用、实际关闭但ACK丢失、结果UNKNOWN；稳定resourceObjectId/descriptorId/ticket/revision，原对象独占且安全才可新attempt。首次＋最多两次安全重试；并发同revision只一方获权。同请求仅元数据，已关只确认、UNKNOWN保持PENDING。manifest P10-A/B/C/D覆盖三类、并发、布尔反例、耗尽及最后owner退出。 | backend实际证明、原生关闭失败行为及并发实现均未实验。HostFixtures先置closed布尔的静态差距保留，不能凭布尔判释放。 |
| R2-R02：writer授权不等于唯一FD | 契约§4–6。首次open也只不可写grant元数据，独立唯一delivery/receiver及一次take/claim；所有重放不含FD/stream。逐descriptor记录真实dup/send/install/take/claim/close；交付/认领不确定首轮仅query/fence/abort。manifest Q09并发/字段冲突、W0–W5、Q04关闭ACK及P10关闭对照覆盖W0–W7。 | 新内部协议及公共API承载未冻结；Windows同进程mailbox profile需真实绑定/计数。owner退休为模型注入，真实Binder、跨进程传递/OS死亡未验证。 |
| R2-R03：分支与累计预算 | manifest§1–6。P01–P13/Q01–Q09共22族展开31P＋30Q；Q05成功流式归T01 READY，空间错误归T04 ABORTED；Q08分writer/validator/READY/未知及排空。每行列前置、共享/独立、终态、I/C、V、目标/记录/写、句柄/缓冲、query与时间。PF及收尾也分配。 | 未运行；预算是上界和准入门禁，不是任意环境61项完成保证。合法短读不足预算为UNFILLED，不判provider违规。 |

冲突时以本批以下限定替代R2相应内容，未列部分继续保持：

- 契约§1–3覆盖R2 SOURCE_LEASE_CONTRACT§3、S07和PROVIDER_SPIKE_PLAN的P10统一重试解释；次数耗尽由**P10-D**独立展开，不能与P10-A真实第二次关闭混算。
- 契约§4–6覆盖R2 OUTPUT_CAPABILITY_AND_RECOVERY§3、O06及错误表“缓存结果”中可能重送writer的解释、provider Q09重放解释；首次grant和重放都不可携可写能力。公开签名尚待API评审，不假装已实现兼容。
- manifest覆盖R2 provider§2“22项各一次/每项10秒”、§3笼统分支及P01最多16次补齐承诺。用61行和全批180秒分配替代，不在180秒之外另加预检/清理。未分配余量不授权补读/重试/新增目标。
- 本批disposition、EXHAUSTED/STALE_REVISION等为内部候选状态，不额外冻结公共错误码；原R2功能码/原因/阶段分层及新增码待审属性不变。F03四次仍只适用已定encoder协商，不泛化close或普通API。

## 3. 算术与跨文档自查结果

对Markdown表格逐行解析求和（文档检查，不运行harness），核对结果：

| 项 | 可复算分配 | 硬上限/判断 |
|---|---:|---|
| 分支/族 | P31＋Q30＝61；P01–P13/Q01–Q09共22族 | 无删族；正常/合法短读四窗口各自具名 |
| 输入请求字节 | P1,573,426＋Q64＋PF32＝1,573,522B | ≤4,194,304B |
| 输入调用 | P55＋Q2＋PF2＝59 | ≤256；失败/未知不返还预留 |
| 物理目标/顶层记录 | 10；P17＋Q14＋PF1＝32 | ≤12/32，metadata-only拒绝仍占记录 |
| 写/验证读取 | 655,360B / 262,144B | ≤2,097,152B / 4,194,304B |
| 查询 | P重放7/新42；Q重放11/新41；合计18/83＝101 | 行Qr/Qn≤1/3，整体≤160，不能拿差额无限查 |
| 控制命令 | 非query 61×6＝366（D8/C4保持两行12）＋query101＋PF16＋清理/停止32＝515 | 清单自设544门禁，未使用29不扩分支；原规定IO/时间硬限额均不变 |
| 日志/元数据 | 61×32768＋131072＋32×16384＋524288＝3,178,496B | ≤4,194,304B；1,015,808B只停止证据 |
| 时间 | PF20＋源body52＋输出55＋close-tail5＋清理20＋记账10＋停止18＝180秒 | P表57＋Q表55＝112秒，P尾5已拆出，未重复计费 |
| 同时资源 | 媒体行峰值5≤6；媒体/管道/进程/log全部新增OS句柄≤24；缓冲≤8×64KiB | 行预算不累加成并发许可；基线runtime内存不伪装在缓冲预算内 |

修正了初稿日志合计笔误，并给控制命令总量增加明确逐行分配。S01的四正常窗口→EOF→ZERO先结束，再开始S02，避免共享guard尚在用就错误提前关闭/开始独立任务；同任务中间行的D/R/A指最终允许终态，实际归还按最后相关分支完成。C5与manifest P10-D映射已一致。

短返回S1–S4每窗实际四次1B，保守请求收费262138＋reference4＝262142，5调用，不足再预留65532，明确4B前缀已核、整窗未收齐。P05另有真实5次delegate最多7B补齐32的对照。二者不混成同一“短读成功”。所有query/重放、副作用、清理计既定deadline；控制额度不足也是停止，不能通过内部步骤绕过。

UNKNOWN或真实IO未返回时停止新授权，后续未接纳行记NOT_RUN_STOPPED_AFTER；仅已登记清理可继续。S17的两对象和关闭操作在负例前登记，最后D→C，再全局受控helper正常退出核实例；原close UNKNOWN不改成调用成功。180秒是controller接纳/等待决策上限，不承诺内核调用已结束；未证资源继续PENDING。正常满读也须现场结果才能给WINDOW_VERIFIED，不提前承诺全部窗口/全部61项完成。

主体本地文件链接均存在；两主体hash按最终文件原始字节计算。R2五原件逐项与既交付hash一致：SOURCE `b0bae695abdb189251ca81c40a45f2a6a27dacb2a9d740fbbe5d153f3a0dea17`；OUTPUT `b64ba9c1ce43cff8c353e17dff2370c7de407342c63a0130652f1ddca5d67a52`；PROVIDER `c070320396513c5d23d31535df62297f2961b6a4a0648716fc72c93439e75bf1`；NATIVE `e3adbcda852d421df0beda8c228e74de38f3e00421982da04089bbf476df07ec`；DELIVERY `c1ce4ae44be23219c41e1089db94aa6a67f3e68512c7a5f26f617dfddab74454`。

现成C14完整性脚本只读核对最终为PASS，含working-tree：342源、139证据、5产物；freeze-summary SHA `880b38f3896df2f6bed2657d54c7fb8a954d3d05d8c730faf1b11278726e7155`，source ZIP SHA `69ca847d7c1947ae65eb3ed6e79d8ab50e21ac9463a1a686cdeda6cfef2d683d`。没有重跑871断言或产生新的功能/设备PASS。R1、C14和媒体未编辑。

## 4. 保留边界、未实现项与下一步

Kit独立、Android先行、Flutter控制层、AAR/C ABI/框架及许可边界、Media3/受限Debug FFmpeg既定约束、全部P0与历史FAIL继续有效；本批不删除或降级R2交付§4的十二项归属和对应原需求。输入只读/不移动、身份/权限隔离、终态与实际引用分离、六真实帧与PTS/色差/EOF、正式媒体双轨/质量、宿主及他槽存活等均未由本地IO字节probe代替。新增SRT素材未执行，不纳入D1证据。

剩余工作：tester独立评审三问题是否闭合、负责人裁定协议/API承载与manifest。只有另行明确准入，才可实现有限本机harness并按冻结清单执行；版本/身份/真实dup/必要durability不满足即NOT_RUN/BLOCKED。真实Android/Binder、设备、NAS与宿主JNI隔离/故障仍需各自条件和另派任务，本批不能放行。没有新增代码/实验/设备任务在途，未自行派tester或下一阶段。

整批保存、自查后，按已明确的用户通信授权向负责人 `01a107c3-2bf9-7fa0-94a0-234258ca6774` 主动报告本回执、主体hash与限制；通知结果由当前窗口最终回复说明。通知失败保留报告、不重复绕过。负责人收到完整包后决定交tester，coder不代替独立评审裁定D1通过。
