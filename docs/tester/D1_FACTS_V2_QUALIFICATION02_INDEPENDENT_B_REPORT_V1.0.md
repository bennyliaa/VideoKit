# FACTS_V2_QUALIFICATION02 独立整包 B 测试报告 V1.0

2026-10-24。结论：**FAIL_PRODUCTION_IDENTITY_AND_SOURCE_BUDGET_INTEGRATION**。原事实与独立离线审批到原 PS 目标函数的链路已在本轮新根通过；生产 identity 对新 wire 的兼容和来源读取累计预算整合仍有问题，不能整包验收。D1 未通过、M0 未启动；不自动进入后续测试。

## 1. 正式范围及唯一冻结来源

按 `D1_FACTS_V2_QUALIFICATION02_INDEPENDENT_B_DISPATCH_V1.0.md`（SHA256 `30558ddf2a21d73ca83c0045ba27186ae440db40f000b8e7c4de2d0bb377b8a9`）及 FIX 测试单执行；派单解除等待条件。工作前读取三协调文档顶部。

候选为 `docs/coder/d1android02-facts-v2-qualification02`，开发报告 SHA256 `d9f520975d5d6fc63fe908c9268275fb1fd4814c763d4657ff2dcbe97c90b142`；manifest `783d4b6c280da96b03c55c06722d9855d839cfc5504cbc62b9c1f7714acd02b4`；ZIP `c5056a4a07acccead34b0dd68cc59a3830bceac2302b217d2a431581bc59167f`。tester 前后独立检查 **277 文件/13,823,627 B**，ZIP **278 唯一成员逐内容、大小、摘要 bad=0**。

30 源摘要 `93f75030768cbd32702451a806ebaa3d50287c0067ef5c7ed5c75c7942bf088c`；22 gate 摘要 `2ad72384549c9d9e7d586848bd2a32e57d65ecb59cd983a1f143d3fa156ca819`；开发 profile `504081cbb3a48049f2156916850e4c04ca181b243d5f5109f516da4ada069d28`；七角色 plan `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8`。本轮未改候选、未运行开发 worker 主入口。

新证据根为 `D:/CodexProjects/VideoKit/docs/tester/D1_FACTS_V2_QUALIFICATION02_INDEPENDENT_B_EVIDENCE`，下称 R。本批唯一 fixtures scope 为 `R/fixtures/8df9b91d`，下称 W。最终清单和摘要见 R 下 `delivery-manifest.json`、`delivery-freeze.json`。

测试驱动沿用已验收 ENV02 的原进程观察/归还逻辑。部分回归场景函数由冻结开发测试夹具派生后在新 scope 重执行，来源明确保存在 `harness-provenance.json`，不把重复开发判据本身当作独立验收。独立增加 `independent_suite.py`、`independent_reference.ps1` 的来源预算、物理文件替换、wire 值变更与生产 RoleSemantic 集成检查；生成独立包名前缀和接近原文本字节上限的服务输入。原产品模块始终从候选目录加载。

## 2. 本批结算及执行结果

order SHA256 `9d7d4f4c5263a25d2e6d7b00660e97c04f2c3dd66ca00a02084d406d3f305df9`。执行前固定输入、源、驱动、完整图和预算。**动态批次一次，产品 retry=0**；执行后仅做文件审计及报告，不补跑场景。

| 项目 | 实际结果 |
| --- | --- |
| 驱动资格 | 3 个原返回；预期 0/7/0，均在 5 秒内 |
| 原 facts 正链 | 小 raw 581 B/2 包；最大 raw 139264 B/128 包均成功；139265 B 入口前拒绝 |
| 原来源/嵌套模型 | 350 个 packet 模型及 10 个 origin 模型，判据均符，无非受控异常 |
| 独立有限离线 reviewer | 6 个真实独立进程，持有同一已归还 facts Capture，全部正常返回 |
| 容量及原 PS 消费 | 0/1/8/16/68/近界 68 服务全部接受 |
| V2 Schema/路由/时钟/政策 | 205 项符合当前场景判据；展开 43×3、wire 15×3 均有实际结果 |
| V1 | 当前原实现 346/346，通过项含原 45/独立 17 对应回归、42 个条件正例 |
| 独立引用与集成 | Python 7/7、PS 8/8 helper 观测符合；另有 8/8 wire 变更拒绝；发现第 5 节两项集成问题 |
| preStart | 原 13 项通过；含一个 .NET 子程序，原返回完成 |

原始 worker 的 `allPassed=true` 表示各组代码声明的执行断言满足，其中独立组明确记录预算重置被接受、identity 被拒绝等观测；**不等于独立验收 PASS**。本报告保留全部原始结果，以独立判据作上述 FAIL 结论。

完整新图：**父 Popen 18 + facts 内 4 + preStart .NET 1 + 外层 worker 1 = 24**，与冻结图一致；父 audit 18/18 匹配。每个辅助原等待、读取器、流、持有 H 和 journal 均返回；Python immutable 原文件事件 **21/21 close 返回**；PS 原文件正例、hash/identity 拒绝事件 close 返回。新 Capture/Gate/facts/file custody 均 0；外层原 wait/readers/流/H 返回；**新增 UNKNOWN=0**。没有故意永久挂起、二次 close、kill、attach 或补 ACK 退款。

worker 26.906 s，外层 27.094 s；限额 360 s、320 s 停止新增、进程 96、并发 1。读取限额 1 GiB/8192 次；预留 facts 原 Gate 512 MiB、PS/runtime 256 MiB、引用证据 128 MiB、静态/驱动 64 MiB，合计 **960 MiB**。外层观测源读 14,441,959 B/316 次，宿主源读 327,012 B，packet 模型源读 631,542 B。它们不是全系统物理 I/O 测量；原读取上限未提高。产物限额 16 MiB，精确最终字节数见 freeze。

## 3. 01 修复逐组复核

| 原项 | 本轮判断 | 证据及限制 |
| --- | --- | --- |
| F01 raw/输出容量 | 本轮最大合法夹具通过 | 真正 facts_entry→collector→原 Capture→FactsBundle，非 emitter/伪 Capture；原 262144 B cap 保持 |
| F02 资格表示容量 | 目标函数层关闭；生产整合仍失败 | 新 wire 小于 16384 B，0–68 及近界集合原 PS 实际消费；新问题见第 5 节 |
| F03 原来源/嵌套 | 本轮模型反例关闭 | 43 个旧变更接受模型均对应当前受控拒绝；350/10 结果及可信宿主边界单列 |
| G01 新测试根 | 关闭 | 本轮准确新根真实原 facts 进程成功；旧根、相似前缀、dot 路径拒绝 |
| G02 外部 review 交接 | 有限 OFFLINE 夹具层关闭 | 6 个独立进程真实往返，同原已归还 Capture，事实年龄不足 5 s；不代真人/设备审批 |

旧 01 的 132 文件及 tester 有效 209 项/8,532,587 B 冻结清单本轮后核均 bad=0。旧 FAIL/UNKNOWN 不改。旧报告“展开 44 字段”为计数文字错误：独立核旧 01 Schema=43、本轮展开实物=43、wire=15；功能没有因“44→43”删减。更正写入本报告及 `schema-coverage.json`，不改旧原件。

## 4. 实际容量和最小外部审批链

最大事实 raw **139264 B/128 系统包**，原 Capture stdout **193568 B**，无 stderr，exit 0，完整还原 raw/facts/receipt/hash。小包 stdout 8650 B。139265 B 原入口 exit 2 / `FACT_ENTRY_RAW_BOUND_OR_HASH`，Gate 未准备、没有 outputs。原单份 Base64 表示不截断；raw、原 stdout、preauth、资格 wire 上限保持 139264/262144/16384/16384 B。

| 服务集合 | Python wire B | 原 PS 重编码 wire B | review B | 固定证据 body B | 原 PS 结果 |
| --- | ---: | ---: | ---: | ---: | --- |
| 0 | 1341 | 1340 | 1219 | 11354 | PASS |
| 1 | 1341 | 1340 | 1787 | 12732 | PASS |
| 8 | 1341 | 1340 | 5770 | 22385 | PASS |
| 16 | 1344 | 1343 | 10324 | 33421 | PASS |
| 68 | 1345 | 1344 | 39912 | 105129 | PASS |
| 68 近界长名称 | 1355 | 1354 | 873258 | 1771821 | PASS |

最后一组每个 process **12318 个 ASCII 字符**，实际全局目标 UTF-8 **851953 B**，距原 **851968 B** 仅 15 B；同构造每项再增 1 字节会超过原界。此为独立生成的可达近界输入，不是开发 12000 字符样例复印或只算字符。Python/PS JSON 的尾换行差异产生 1 B 差，分别实际量字节。

raw Base64 的理论上界 185688 B；既有 Gate/proof 二进制上限编码后分别至多 21848/5464 B，合计 213000 B，其余是受控固定结构。本轮真实最大 raw 的最终 193568 B 在原 pipe cap 内。服务 process 由目标全局文本总字节上限约束；系统包/HOME/firmware 等还受原 raw 总量与 parser 约束，不能把 68 与每字段任意长相乘为合法范围。当前近界目标实测 review 0.84 MiB/body 1.69 MiB，8 MiB/2 MiB 均未触及；未声称这个样例枚举了所有可达名字和编码组合。**生产来源总预算整合仍未通过，故新文件 cap 本身不构成完整容量承诺。** 不提高 pipe/control/source 门，也不缩小合法 raw/128/68 范围。

6 条实际链：新 facts 原返回→宿主持有同一 Capture→导出 approved=false/REQUIRES_REVIEW 候选→有限独立 reviewer 从固定原文件引用核字节→返回准确 review/hash→宿主 qualify→原 PS 目标函数。各 reviewer 原等待/EOF/close 完成；fact age 分别约 2.658/2.936/3.215/3.463/3.727/4.035 s，单往返 0.235–0.297 s，未刷新原 collectedAt、未重放原采集。

这些都是明确 **OFFLINE 合成独立夹具，realHumanApproval=false**。review 的协调线程 ID 是协议字段，不是现实身份认证。未新增服务/IPC/签名框架，不代表真人批准、设备事实、完整七角色生产运行或现场资格。

## 5. 集中未关闭问题

### B02-01 / P1：新 wire 接入生产 identity 会被拒绝

生产 `tools/capture_android02.ps1` 的 `RoleSemantic` identity 分支仍直接比较：`$lines[3]` 与 `$policy.globalIdleQualification.fingerprint`。新资格 wire 只有 15 字段，其中不含 fingerprint；它在读取固定证据后才出现在展开对象。生产 runner 继续将资格 wire 原样传入 policy，identity 分支没有先解析对应固定证据。

本轮从冻结原文件 AST 提取 **未修改的 RoleSemantic 函数**，没有运行带设备/SDK 的顶层入口。输入本轮有效 wire，identity 文本的固件与已采集事实完全相同，实际返回 **`FACT_IDENTITY_FIRMWARE_DISAGREEMENT`**；相同文本配匹配 fingerprint 的展开形状对照返回 **PASS**。因此“新表示→Get-GlobalIdleDecision 通过”不能代替其前置 identity 角色兼容。证据在 W/`independent-results.json` 的 productionIdentityProbe；函数文本 SHA256 `15ba211e1298e85397456f77b60260e4ba529f62f0a572507a67ed8b2695d55c`。

该结果属于实际原函数的隔离集成验证，未声称执行了完整生产七角色或真实设备。建议下一整批通过已有可信、预算内的固定证据路径向 identity 提供准确事实，复核所有生产调用方对旧展开字段的直接访问，不能加裸 fingerprint 后忽略来源绑定。

### B02-02 / P1：文件来源局部计数没有接入原 Gate/整批累计账本

`qualification_reference.ps1` 及内联 admission 初始化各自 sourceBytes/sourceReads=0；helper 接受可选 `qualificationEvidenceBaseSourceBytes/Reads`，缺失默认 0。独立搜索全部候选 tools，只有两处读取这些变量的代码，**没有生产初始化赋值**。capture_android02 仅把局部计数附加到 console；未发现 outer_owner/production_runner 将引用读取并回原 Gate 来源累计预算的实现。本轮原 facts Gate 已消耗 **8449471 B/51 次**，与 PS helper 局部额度分离。

实际有界 helper 验证：显式传入已满 256 MiB 或 64 次 base 时准确拒绝 `GLOBAL_V2_EVIDENCE_SOURCE_BUDGET`；同一局部 ledger 读到 64 次后第 65 次拒绝；再次加载原模块后计数归零、同一文件重新接受，变成 1 B/1 次。这个复载是计数特性的观测，不是获准重置生产账本，也不声称可信同进程宿主可任意改内存属于外部攻击。它说明局部上限不证明调用方与全批累计门已经集成。

hash 拒绝实际读 1 B并计费、identity 拒绝读 0 B但占 1 次，实际原句柄 close 返回；Python hash 拒绝保留 reads=1/reservedBytes=2/bytes=1。PS 事件虽记录 sourceReservation，却没有把跨调用未决预留接入持久原账本。未故意注入短读/OSError/close UNKNOWN 或永久挂起；短读/异常预留覆盖缺口单列，不用模型声称真实未知回收成功。

本轮受控测试并未实际超出原 256 MiB/64 次生产门；结论是**要求的生产累计整合缺失/未证明**，不是宣称本次真的超读。建议最小接入原账本、携带 base 和 delta、重复消费与拒绝统一累计，并证明异常/短读/身份/hash 失败预留不能被模块或下一调用重置；保持原 268435456 B/64 次上限。

## 6. 来源、字段和覆盖的准确范围

原 Capture 内部登记把构造、真实 Popen 引用、启动、EOF/readers/wait、原流/H/journal 返回连接起来。实际正链与模型并列：`__new__` pid-only 和复制对象拒绝 `V2_CAPTURE_CONSTRUCTION_PROVENANCE`；替换 original 拒绝 `V2_CAPTURE_ORIGINAL_OBJECT`；身份/readers 变更拒绝 ORIGINAL_BINDING；returned/failure/wait bool 变更拒绝 COMPLETION_BINDING；二次 launch 在原构造器前拒绝 CAPTURE_ORIGIN_LAUNCH_ONCE。未启动额外子进程或二次 close。可信同进程私有内存任意修改不在保证范围。

350 个 packet 模型使用本轮真实归还包作前像，仍是纯变更模型；嵌套字段删/null/异型、额外字段、raw/hash/order/tick/gate/proof 均保留实际受控原因。`old43-model-closure.json` 逐项对应 01 的 43 个变更接受模型，当前 43/43 受控拒绝；**不是 43 个漏洞**。合法 `release.failure=null` no-op 与原真实对象还原对照均接受，不误计缺陷。当前 350/10 未见原 32 类非受控异常；不能外推为所有输入都不会异常。

`representation-map.json` 从冻结原 PS 的实际构造表达式提取完整 **15 wire→引用 body/packet→43 展开字段**映射；原文件 ref 包含 path/bytes/SHA/volume/fileId，读取同一原文件句柄检查固定根/路径、非 reparse、单链接、原大小、前后身份与 hash，原 close 保留。Python 实际同路径同字节替换后旧 fileId 引用拒绝；Python/PS 的错 hash/身份/固定路径、wire scope/root/plan/mode/批准字段变更有本轮结果。PS 的实际同路径物理替换、真实 reparse/硬链接、短读/拒绝中 OSError 未完整动态覆盖，保留为缺口，不能仅依据静态代码签全通过。

展开 43×3=129 项和 wire 15×3=45 项删除/null/异型均执行，包含 01 遗漏 12 个字段的各三行；这是当前函数模型中的受控拒绝覆盖。部分 null/异型仍先到 provenance，不能叫深层精确类型门覆盖。另一方面，旧六项 factPlanId/factRunId/nonce null/异型已用与前置摘要一致的独立新证据 body 达到原 PS 深层门，分别确认为 GLOBAL_V2_FACT_PLAN_NONCE_TYPE / GLOBAL_V2_FACT_RUN_TYPE。

完整 V1→V2、V2→V1 错上下文均 GLOBAL_QUAL_SCHEMA 拒绝；合法 V1 路由通过。0/299.999 秒接受，300/300.001 秒 GLOBAL_FACT_STALE_OR_FUTURE；未来 -1 秒更早 GLOBAL_V2_REVIEW_WINDOW。None/bool/int/float 时钟 GLOBAL_V2_REVIEW_CLOCK；原采集时间不刷新。HOME 符合后缺服务证据准确 GLOBAL_V2_SERVICE_EVIDENCE；TOP 2/3 先 BLOCKED_OCCUPIED/ENV_WAIT_FOREIGN_FOREGROUND，instrumentation 先 ENV_WAIT_OTHER_PROJECT_OR_TEST_OCCUPIED，非整数 state 拒绝。其余具体 policy 拒绝见 56 行 host-review-models。

阶段 A 160 项在 `phase160-trace.json` 全部有状态：144 项映射本轮实际原函数或纯模型、1 项真实未批准导出、1 项静态信任边界、9 项准确提案未执行、4 项只有相关场景而准确提案未执行、1 项真实 Capture/reviewer/原目标函数链。选择 ID 的线索来自冻结开发 trace，但结果逐条从**本轮**文件读取，未引用开发 PASS。嵌套别名映射不冒旧提案顶层结构，**不报 160/160 精确通过**。缺口包括 receipt-body-only、empty-custody、unknown、wrong-preauth、wrong-target-plan、home-ambiguous、service-wrong-process、unknown-record、APP-PERS-own-missing；相关而非准确组合另有 self-controllerReturned、wrong-source、service-wrong-state、float 1.0。禁止为补数制造真实永久挂起。

## 7. 交付及停止点

请负责人集中安排 **B02-01/B02-02** 及上述必要覆盖缺口到下一整批，开发自测冻结后再正式交独立整包复审。容量/原来源/外部离线夹具层已改善，但不能替代生产预算与前置角色集成。

动态后首次文件审计把 facts 中预期为 false 的状态字段也当成 true 检查，审计脚本断言失败；没有运行新场景或改任何原结果。保留 `audit.py`，以 `audit_v2.py` 按准确返回字段核验，`post-audit.json` 已完成。全部 312 项 order 源未变，候选/旧原件前后核验一致。

SDK/ADB/设备/Native route/TCP/Gradle/媒体/Git 操作均 0；文件身份 Win32 API 仅作用于固定证据文件。原件、旧账本/once/FAIL/UNKNOWN 不写。本批完整报告集中发负责人，后续保持停止，不自动现场、资格签发、修复或重测。
