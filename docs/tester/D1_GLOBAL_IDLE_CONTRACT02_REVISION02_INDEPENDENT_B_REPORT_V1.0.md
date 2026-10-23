# VideoKit GLOBAL_IDLE_CONTRACT02 revision02 独立整包 B 测试报告

日期：2026-10-23。执行者：tester。正式派单来源：负责人会话 `01a107c3-2bf9-7fa0-94a0-234258ca6774`，turn `01a1680c-ab38-7761-a698-c94a08b5882e`，call `exec-1538e5d2-28b8-4048-aa70-83f61c5049af`。准确原文见[派单记录](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/dispatch-source.json)。

## 结论

**FAIL：本轮整包复审不通过，集中回交负责人安排修复后重新整包冻结送审。** 共确认 5 项问题，其中两类解析缺陷在补充用例中造成 4 次错误 PASS。不得据开发自测通过、原 45 项矩阵通过或正常七角色链通过，批准当前候选进入后续现场测试。

原 23 条规则对应的独立 45 项矩阵 **45/45 通过**；独立用例含补充边界共 **175 项，170 通过、5 项原始断言失败**。其中 4 项为错误放行，另 1 项为小数 HOME 状态被后继 HOME 检查挡下、拒绝阶段不符合预期。17 个有意设计的条件正例全部实际通过，没有以永远拒绝代替正例。开发提供的 98 项回归另行执行，98/98 通过、10 个合成正例通过。所有历史原结果保持原样。

动态主批共 13 组，11 PASS、2 FAIL；第二个 FAIL 来自 tester 对事实帧错误码的错误预期，详见辅助检查说明，不能算作候选帧解析缺陷。其未到达的纯模型尾项以单独有界来源补齐，14 项通过，原 FAIL 保留。最终整包 FAIL 的依据是本报告列出的实际缺陷。

本轮仅本地夹具与静态/纯模型验证。真实 ADB、Native 路由/TCP、设备、help、Gradle、媒体测试均为 **NOT_RUN / 调用 0**。没有安装、卸载、后续现场采集或后续测试。D1 仍未通过，M0 未启动。

## 冻结对象与隔离

候选：[d1android02-global-idle-contract02-revision02](D:/CodexProjects/VideoKit/docs/coder/d1android02-global-idle-contract02-revision02/DELIVERY.md)。

| 对象 | SHA-256 / 数量 |
|---|---|
| 交付说明 | `4b47bac5caca3e719a575a8806d7388db977bd1ca11158f4d43b578929fe9ce0` |
| 全包 manifest | `de6da216ffe66a2d6cdc8d04c4f52468acc023ea044cef61b1556c9de36d7a80` / 1140 项 |
| 原冻结 ZIP | `3056515f70200c7bb5f6961c90a455ff1bc07611b051c264212e194f1fd5ebf2` / 1141 项 |
| source seal | `e0ad5adf1e0ae3a48d397ac0d8205a72394b54dffd9e85a3693e18ab831601db` / 17 项 |
| gate sources | `297bd1ef7189e46831bbab4cfd2b541cf325a6d4adb2c532111e87ee7faa8140` / 9 项 |
| 精确角色 plan | `ddcd1b0fec9b287b62d020c34507cf4f06a2a789c054ba5f31f4114434be42f9` |
| 生产 PS / Runner / Owner | `49958fd944cea830051483560624e87d985dfac1b9a95c1db01d0fc794f9714e` / `1f4e5d1f74aa03862c8d7798190aed6ce33bed562044e70c359875bbe5e86ff8` / `6100f82e8ac8ff1c6949d7186983e2c411f3c7b2bf8ffebe6ab62428e270b5e3` |

执行前核验全包 1140 项、17 源和固定上游材料；执行后再次核验原 1140 项及 ZIP 1141 项，全部 bad=0。产品 FIX02、Native/runtime 的冻结身份没有由 tester 改动。见[执行后核验](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/post-audit.json)。

批号 `6e74b888200e4bf98e72400e37d1a97e`；最终执行订单 SHA-256 `1b27dbb27981c9249654c0956f4aefcc3b8f2c2f61ddc026e20c3f76f4e0abb2`。SELF 采集资格引用原 13 源 package `b3cdd53b3527e39aac726d1014473e69f2c1a552fa7243a6be434adc5901c2e1` 和已接受 SELF 报告 `2fd415f0bbee624abae236934514a4f9a3310e3d04ac7937d10b65cc9f3fb613`；本轮新 profile 经 42 项纯预检后另行固定，未冒称继承候选无关 Activation 的现场权限。

三个入口的共同夹具白名单只有候选 `selfchecks/work`。为完成完整原链，预先固定全新输出子目录 `D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract02-revision02\selfchecks\work\tester-r2-6e74b888`。这些新增测试产物单独列入本轮证据清单；没有改写原冻结 1140 项、候选源、开发 evidence 或历史 suite。新 tester 根被拒绝的反例另在 tester 目录下创建，准确实际路径以其 `exact-root-disagreement.json` 为准。

旧 001a scope `a7036abcb551c826b1367d19eb74dd4ec83a97881f08015868c007a8026a37da` / session 55065 及其他旧未返回链保持隔离；未查询其运行态、会话、PID、尾日志或锁，未强停、二次 close、补 ACK、退款或补造返回。只读使用本次冻结包中的既存归档及已指定的 LIVE03 原始样本。没有 Git/index 操作，没有 test_media 写入。

## 集中缺陷

### B-R2-01 / P1：未识别的前置进程记录可被整体跳过

位置：[admission_checks.ps1:220](D:/CodexProjects/VideoKit/docs/coder/d1android02-global-idle-contract02-revision02/tools/admission_checks.ps1:220)，完整记录扫描及首个受支持 header 前的处理。

在正常 HOME 记录之前加入一条外部 TOP 进程，将其顶层头改为 `*APP* UID10065`、`*APP* uid 10065` 或 `*APP*UID 10065`，其 body 仍含 UID、packageList、`curProcState=2`。三个反例均得到 `PASS / GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY`，解析记录仅余正常 HOME，外部记录未进入盘点。

预期：混合受支持/不受支持顶层记录必须 `BLOCKED_UNPROVEN`；不能以两套相同窄匹配都没命中为完整性证明。对应原 I03、P02 与补充完整性边界。应先完整盘点可能的顶层进程记录，再验证每条受支持语法，无法解释的前置/中间内容不能静默跳过。

复现：[uid-spacing](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/reproductions/UNPARSED_PREFIX_uid-spacing.json)、[uid-case](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/reproductions/UNPARSED_PREFIX_uid-case.json)、[star-spacing](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/reproductions/UNPARSED_PREFIX_star-spacing.json)。均为合成解析输入，没有真实外部进程操作。

### B-R2-02 / P1：状态字段接受数字前缀，`16.5` 被解释成 `16`

位置：[admission_checks.ps1:230](D:/CodexProjects/VideoKit/docs/coder/d1android02-global-idle-contract02-revision02/tools/admission_checks.ps1:230)，`curProcState=(\d+)\b`。

外部 cached 记录的 own state 改为 `curProcState=16.5` 后，实际解析 state 为 16，完整决定为 PASS。预期该不支持的状态值应直接未证拒绝。相同机制下 HOME state `1.5` 被解析为 1，最终虽由 `GLOBAL_HOME_PROCESS_STATE_UNPROVEN` 阻挡，原始“应在状态解析阶段拒绝”的断言仍 FAIL，未改判。该项是同一根因的补充表现，不另计一项缺陷。

应校验 own state 的完整词法边界与完整整数值，不能接受小数/其他值的数字前缀。对应 P04、P13。

复现：[错误 PASS 的 cached 小数状态](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/reproductions/FLOAT_CACHED_STATE.json)、[被后继检查阻挡的 HOME 小数状态](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/reproductions/STATE_1_5.json)。

### B-R2-03 / P1：事实采集 fixture 分支未约束可执行程序 `argv[0]`

位置：[fact_collector.py:119](D:/CodexProjects/VideoKit/docs/coder/d1android02-global-idle-contract02-revision02/tools/fact_collector.py:119)。

分支校验长度、`argv[1:5]` 和 `[5:]`，随后直接 `argv=fixture_argv`，没有校验第 0 项。对冻结源码中该分支进行准确 AST 截取的纯参数模型，固定 Python、真实 adb 路径、未审 Python 路径均通过这一层参数守卫。因此交付中“fixture 不能选择 ADB、只允许固定本地 producer”的约束未由该入口完整落实。

这是 **OFFLINE_FIXTURE 参数守卫的静态反例**：没有伪造原 Gate、绕过其他 authority 检查，也没有实际启动上述错误程序；真实 SDK=0。当前 tester 外层审计另有准确程序约束，42 项纯预检已拒绝外来程序元组，实际运行只用固定 Python。本发现不能描述成 LIVE 授权已被绕过。

修复需把固定程序及其身份纳入本分支的准确约束，并在启动前拒绝错误首项。证据：[原分支、纯模型、完整输入与结果](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/fixture-executable-guard-analysis.json)。

### B-R2-04 / P2：当前命名的未来事实提案仍绑定旧候选

位置：[next-readonly-facts-execution-proposal.json](D:/CodexProjects/VideoKit/docs/coder/d1android02-global-idle-contract02-revision02/reference/next-readonly-facts-execution-proposal.json)。

提案仍为 source seal `001a0089ddd9140b7b46cd21c1822579703a1d789062b9bb3b8bed962a226039`、gate `2aa021f939a6f19bae6eb4b740592f6c88e83591adca213f2eb44ea38697577e`，factPlan 路径仍指向旧 `d1android02-global-idle-contract02`。它在新版完整 manifest 中，schema/status/next 仍表达后续执行提案，没有明确标记为历史归档原案。

`approvedForExecution=false` 阻止直接执行，但不能消除来源绑定错误。collector 文件 hash 与 factPlan **内容** hash 本次确实未变，应与错误的 source/gate/path 分开。该文件不是当前生产 Runner 的自动加载入口，未观察到由它绕过生产源校验；本轮没有套用该提案执行。

需更新准确新版提案，或明确移入历史原案并提供新版提案。证据：[提案逐字段裁定](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/proposal-adjudication.json)。

### B-R2-05 / P2：Runner、Gate、Owner 的 tester 夹具白名单不一致

Runner 与 Owner 接受 `D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/fixtures`；未改的 Gate 只接受原 `D1_COMPAT03_SCHEMA_PARITY01_REVIEW_EVIDENCE/fixtures`。在新版 tester 根中创建准确新 scope，Runner 准入成功，随即在 `GateSession` 构造中准确拒绝 `GATE_FIXTURE_ROOT`。原 claim、checker、SDK 均未进入，原 Runner IO 线程全部返回。

使用三者共同允许的候选预留测试输出区后，本轮完整原链可以执行，因而没有把这个目录问题冒称为七角色功能失败；也没有改源、链接或扩大白名单绕过。

需整批统一三者支持的输出根并同步来源 pins。证据：[目录反例组](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/group-6.json)、[预先声明的隔离方案](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/scope-isolation.json)。

## 已通过的测试及适用范围

| 测试 | 结果与证据 |
|---|---|
| 原 23 规则 / 独立 45 矩阵 | 45/45 PASS；含 APP/PERS、全冒号名、own 字段、UID/user/core/isolated/shared、唯一 resume/HOME、仪器优先、资格与归档边界。原判据文件保持原历史状态，本报告记录这次新候选执行结果 |
| 独立补充语义及资格 | 175 项整体 170 PASS / 5 原始失败；17/17 有条件正例 PASS；所有资格顶层字段、home、originalReturn、service 字段删除及所列篡改，逐项保留准确拒绝原因。system 列表不等于服务许可；299s、300s、未来、301s 窗口明确分列 |
| 开发 98 项语义回归 | 使用真实冻结 admission 模块函数执行，98 PASS / 10 合成正例 PASS；没有复制开发旧 PASS 代验 |
| preStart 原生命周期 | 先于 Runner/collector 动态执行。13 项 PASS：0/1/2 raw 与 input 原 source 唯一 close、原 Process Dispose 一次；没有制造 EOF/pipeClose；真实已启动的固定本地子进程仅走原正常返回路径；9 类 UNKNOWN 只做纯状态模型 |
| API31/角色来源、事实帧 | 固定官方 commit 的 9 份材料字节 hash 核验；AIDL UNKNOWN=-1、已有记录状态0..19、NONEXISTENT=20 分开。RoleShell 无 get-role-holders，固定只读替代 dumpsys role；7 项查询 plan 与固定文件一致。剩余独立纯模型 14 PASS，含 UTF8/NUL/帧长度/时序/重复尾项/角色语法/PM 选项/RS 尾换行与 C 字节长度模型。设备 shell 未运行 |
| 原本地事实 collector | 原 prepared Gate + 固定 producer 实际 Popen、双 reader、wait、原 H close、原 claim 唯一释放通过；532B stdout / 0 stderr；0.063s；错误外部 approval hash 精确拒绝、once 拒重入。receipt 的外部返回仍需证明标志未改写，后由本轮实际 worker/outer 返回补足本地 fixture 的观察层 |
| 原完整入口 | 默认/live 无准许拒绝；外部 hash、schema、source/scope/backend、预算类型、操作/产品/角色反例通过；真实 PS 原七角色、END、初 proof 不变、once、唯一 claim 释放通过 |
| 生产 PS 守卫 | post/receiver reset、重复、event/source/holder/mode/类型/extra 反例和最终启动 proof/gate/whole/过期/未来/整数时钟反例通过；保留精确拒绝原因 |
| 物化变化 | 原 materialization 追加一个空格后准确拒绝 `MATERIALIZATION_ORIGINAL_PENDING_OR_BYTES`，原 holder 唯一释放 |
| 精确 source guard | 预先算账后，仅给本轮自有 PS 副本追加一个换行字节，准确到达 `OWNER_SOURCE_PIN_ENTRY`；启动控制器 0，初 proof 未改，pending 0，原 claim 唯一释放 |

汇总及原结果：[独立矩阵裁定](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/independent-matrix-adjudication.json)、[主批结果](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/worker-final.json)、[补齐纯模型](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/remaining-pure-results.json)。

有限故障的实际返回如下，全部保持原失败资格并由原 holder 唯一释放；没有以释放证明把失败改成 PASS 业务结果：

| 场景 | 实际拒绝 | 已进入本地控制器 |
|---|---|---:|
| MATERIALIZE_KNOWN_REJECT | CONTROLLED_MATERIALIZATION_REJECT_BEFORE_OPEN | 0 |
| NO_SDK_ABORT | CONTROLLED_NO_SDK_ABORT | 0 |
| WRONG_HOLDER | WRONG_HOLDER_REJECTED | 0 |
| WRONG_OUTPUT_SOURCE | RUNNER_CONTROL_CAP | 0 |
| MATERIALIZE_LATE / RECEIVER_LATE / TAIL_LATE | RUNNER_PROOF_STICKY | 各 0 |
| EXPIRE_DURING_MATERIALIZE | PERMIT_EXPIRED_OR_FUTURE | 0 |
| BUSY | OWNER_STICKY_NO_SUCCESSOR:CAPTURE_FAILED_STICKY | 2 |
| PRESTART_KNOWN_REJECT | OWNER_STICKY_NO_SUCCESSOR:CAPTURE_FAILED_STICKY | 1 |
| OWNER_END_TAIL | OWNER_STICKY_NO_SUCCESSOR:PROOF_WALL_TIMEOUT_STICKY | 7 |

`WRONG_OUTPUT_SOURCE` 的 cap 抢先缺口原样保留；另一个小追加用例才是 source guard 的准确覆盖证据，未把前者任意拒绝当成后者通过。见[有限故障](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/group-10.json)和[准确 source guard](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/group-13.json)。

LIVE03 原 388784B 样本 SHA-256 `6eab0a9190438367150182a530395585066826514242dbaf5dc70bb6f49596b0` 在两套回归中均解析 68 记录，因真实新资格缺失继续未证。没有回填 LIVE03 PASS、原 FAIL/UNKNOWN/once 或原 amountUnknown 字段。

## 原返回、预算和实际账本

| 项目 | 预存上限 / 实际 |
|---|---|
| 新外层 / worker | 720s / 660s，600s 停新准入；worker 235.234s、外层 236.453s |
| 原自有辅助工具 | 每个 180s，最多32；实际 9 个全部原 wait、reader、stream、H close 返回，pipe 合计3032B，均未过期 |
| 实际审计 | 上限256，实际34，真实拒绝0；新准确元组在构造前固定并有纯正/反例。当前 worker 观察自己的调用；CLI/.NET 后代以冻结调用图和原返回证据校验，不冒称都被本层回调观察 |
| in-process Runner source | 15 个，实际126556777B / 405 次；逐 Runner 原536870912B /256次不扩额；外层另预存4GiB /8192次，不把此数冒称包括全部后代 source IO |
| 正常七角色 | 初 proof control183963B，post41566B、receiver14049B，合计239578B <262144；END control470149B <1048576，logical inbound472201B <3276800 |
| 准确 source guard | 构造前 runner bound243996B、gate bound218781B；实际 runner237906B、gate195784B，均<262144；创建测试输入11874B已计入 pre，自己的追加1B，无免费整文件 control 重读 |
| 归档 | 单证据文件1MiB、总134217728B /4096项预存；完整实际文件字节和 hash 见本轮证据 manifest 与冻结回执，后验核验不冒充物理 IO 证明 |
| 未归还 / 旧链 | 本轮 Runner/Gate/fact/aux/Native custody 均0、新资源 UNKNOWN=false；旧链运行态查询0，原 UNKNOWN不变 |

固定生产预算仍为 whole600/gate30/checker20/proof10/outer120，7 SDK角色/并发1/retry0，metadata4、local262144/control1048576/text3276800/payload7629605/command28672。所有固定 fixture 数字均为本地模拟与逻辑记账；真实 SDK、真实 Native 路由/TCP调用为0。SELF 期间仅使用原自有进程句柄的身份 API，不能把它写成真实 Native 路由已测。

原 worker PID39232，原 H 的 creation FILETIME `134372220996600215`；wait/readers/streams/H 唯一 close 均实际返回。原 worker exit2，外层观察 exit2；测试工具层终态 exit1，分别保留。外层原返回与证据文件 close 均已观察；没有新增 pending。候选 `candidateOnlyWriterCloseNotProven` 等保守字段保持原值，physical IO 仍 UNPROVEN。见[原外层返回](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/outer-final.json)。

## 后续事实采集的可操作性与 NOT_RUN

静态未发现目标 permit 的固有 hash 环：可以先保留准确 targetScope，再由审查绑定事实/target/source/plan，资格绑定最终 review hash，permit 绑定资格，外部批准再绑定 permit。

但事实采集前的 authority 必须绑定**运行时原 Gate.prepare 后才出现的 routeProof hash**。随后仍需外部 authority/approval 双 hash，经原 `Gate.receive` 接收时满足 initial proof<10s、Gate准入<30s；本地 fixture 在同一调用者中生成合成 issuer 字符串与双 hash，只证明模块所有权及返回路径，没有证明真实外部负责人的批准往返。该步仍需一个准确冻结、有界、保留同原对象并可观察返回的外部交接方案。

事实采集至窄策略审查、目标 permit 构造、源码准入和 global_idle 还需在剩余<=300s新鲜期内完成；过期必须拒绝。299s/300s/未来/301s 窗口已做纯模型，真实跨会话时效链 **NOT_RUN / NOT_PROVEN**。未来提案本身还存在 B-R2-04 的旧绑定。

真实 facts、真实 HOME/system/service 窄策略、外部 owner 返回及批准链、真实目标设备七角色均未执行或未获本批批准；不能用本轮合成 PASS 补空。见[外部链静态审查](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/operability-review.json)。本轮完成后等待负责人另行准确安排，不自动进入后续测试。

## 测试辅助过程的原失败保留

1. 首版测试订单在任何动态构造前，发现 tester 的 AIDL 符号断言误写成 `PROCESS_STATE_TOP` 等前缀。原订单及两个源 preimage 留存；只修 tester 断言/最终订单文件名，重新完成42项纯 profile检查，冻结 v2 后仅执行一次。候选未改。
2. 主批 group4 对较短 model 帧长度的实际严格拒绝为 `FACT_ORDER_OR_FRAME`，tester 预期误设 `FACT_ITEM_STATUS_TIME_OR_BYTES`，因此该组原 FAIL 保留。较短长度先消费了原 payload 换行，下一帧才不匹配，当前拒绝与代码路径一致。其未到达的尾项在原动态批所有原件返回后，用独立、禁进程/SDK/Native 的纯模型范围补齐14项；没有重跑这个已失败输入或修改原结果。
3. 首次后验 ZIP 核验用后缀匹配，混入原包嵌套归档中同名 reference 文件，tester 核验脚本失败。原脚本/失败记录保留，v2 改为 ZIP 完整路径准确匹配，原1140文件及ZIP1141项核验通过。该修正仅影响文件核验，没有重试动态 scope。

这些辅助错误不删除、不藏入全绿结论，也不归因给候选。原件均在[本轮证据目录](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE/execution-order-v2.json)及对应 amendment/failure 文件中。

## 集中回交与复审条件

请负责人集中安排 B-R2-01 至 B-R2-05 修复，重新冻结完整 source/gate/plan/调用图/事实提案和相应自测产物后，一次性整包送 tester。解析反例必须在实际生产函数准确未证拒绝；原条件正例、七角色、preStart原资源返回和原账本/once/END应继续通过。任何后续事实 scope 都需准确新来源与外部交接边界，不复用本轮 fixture 准许或旧未返 scope。

报告与证据存放于 `D:\CodexProjects\VideoKit\docs\tester`。本轮 manifest 和发送回执与报告同目录，原报告结论不随发送操作改写。按用户既有授权，完整报告冻结后直接发给负责人；没有逐问题交 coder 或自行进入开发/现场测试。
