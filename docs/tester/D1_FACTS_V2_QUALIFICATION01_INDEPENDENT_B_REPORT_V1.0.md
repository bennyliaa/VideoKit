# FACTS_V2_QUALIFICATION01 独立整包 B 测试报告 V1.0

报告日期：2026-10-24。结论：**FAIL，不签发 V2 资格，不进入后续测试；D1 未通过，M0 未启动。**

本报告按负责人正式整包 B 派单执行。发现三组需集中复核修复的问题：事实输出与接收容量不一致、资格输出与目标接收容量不一致、原 Capture 来源及嵌套绑定校验不足的模型反例。另有测试根不兼容、真实外部审批交接未证明两项交测缺口。请负责人集中安排下一整批，开发自测冻结后再交独立复审。本次没有设备、SDK、ADB、Gradle、媒体、Git 或旧运行对象查询操作。

## 1. 准确候选和证据范围

需求：`docs/tester/D1_FACTS_V2_QUALIFICATION01_INDEPENDENT_B_TESTER_REQUIREMENTS_V1.0.md`，SHA256 `78db226cca35e953ceddc660ae75daac5777ab18e348128a95a1a1e592316ae9`。

唯一候选：`docs/coder/d1android02-facts-v2-qualification01`。开发交付报告 SHA256 `20601b961d781773bee8e62703051f4673e7182b675437d8a3373f3b1d247338`；26 源摘要 `dfcd0add7bf89b9363b7efe23b45bed0145ee977fddd48fd45725546350e74d0`；18 gate 摘要 `e404f32bccb9aac960b001b7e529d7aed06a501d93aca2eca255c12b8a264a61`；开发计划摘要 `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8`。

候选 full-manifest SHA256 `07a7572ce553f4ad7cd85ca98a97e6fe7b643275d228deb6a9e05cb4c111a0c4`：132 文件、5,125,910 B。ZIP SHA256 `070989425d65bcc487ca1f7addfc7a9c425ee9cf9b1ed0e5bbd192397d7d551d`：133 个唯一成员。tester 在执行前后独立逐文件、逐 ZIP 成员检查内容长度和摘要，bad=0；本批冻结的全部 202 项源/驱动保持一致。未执行开发 worker 主入口，未写候选目录。

本批所有新测试证据在 `D:/CodexProjects/VideoKit/docs/tester/D1_FACTS_V2_QUALIFICATION01_INDEPENDENT_B_EVIDENCE`，下文简称证据根。`post-audit.json` 保留初次审计；`schema-and-coverage-addendum.json` 与 `phase160-trace-final.json` 是后续只读分析澄清，原始结果不改写。最终文件清单、摘要及字节数见证据根 `delivery-manifest-v2.json`、`delivery-freeze-v2.json`。初版文件汇总因 PowerShell 字典求和产生错误的 bytes=0，未发送即发现；初版保留为无效历史，V2 改用逐项整数累加并重新核验，不涉及任何场景重跑。

## 2. 执行及资源结算

仅一次集中动态批次、驱动一版、产品重试 0。执行前固定 order、源、输入、预算和完整 Popen/.NET 图，order SHA256 `4b3deb19c404c316e2351d16bb18abfcbaa9dceb0c3cb383acd7cafe5e75afdb`。纯准备修订及早期未使用输入全部保留，不作为动态重试。执行后的分析只读现有结果，没有补跑场景。

| 组 | 实际结果和限制 |
| --- | --- |
| 驱动资格 | 3 个原程序返回；包含自然退出及预期非零返回，未超时 |
| 新授权根原入口 | 原 CLI 返回 exit 2 / `GATE_FIXTURE_ROOT`；未到 Gate claim/lease/SDK，未产生 lock |
| 原实现对象/review 模型 | 295 行，219 行符合原声明判据，76 行不符；详见下文分类 |
| 当前 V1 | 346/346 通过，其中 42 个条件正例；包含原 45 项及独立 17 项对应回归 |
| 当前 V2 原 PS 函数 | 126/126 状态符合，120/126 精确原因符合，5 个正例；6 行安全拒绝但原因阶段不同 |
| 原 Capture 容量 | 大输出实际 `PIPE_BOUND`，所有原资源正常返回；小输出返回但 FactsBundle 拒绝其非 facts_entry 程序来源 |
| 原 preStart13 | 已执行，含 1 个 .NET 启动子程序，原等待/读取器/Dispose 完成 |
| 外部 review 可操作性 | 完成静态和现有对象保留核查；真实 facts 原 Capture→外部批准→资格链路未执行，不算通过 |

“组已执行”不等于产品通过。实际图为父侧 Popen 13（与审计 13 项相符）+ .NET 子程序 1 + 外层 worker 1 = **15**；条件上限 17，预算进程上限 96、并发 1。新启动的原等待、读取器、流、持有句柄和 journal 均完成原回收；**新增 UNKNOWN=0，pending 原资源=0**。容量失败是已知业务失败，不能改写成通过，也不需要二次 close、杀进程或退款 ACK。

外层原返回耗时 14.594 s，worker 审计耗时 14.125 s；预算 360 s、320 s 停止新增。读取预算 1 GiB/8192 次，分项预留合计 973,078,528 B；外层观测源读取 11,908,736 B/206 次。未进行全系统物理 I/O 测量，不能将该观测值冒充全部实际读量。产物上限 16 MiB，最终文件结算见 delivery-freeze。观测写操作均位于本批授权根。未触碰历史 UNKNOWN、once、账本、旧 FAIL 或旧 pending。

## 3. 集中问题及交测缺口

### F01 / P1：合法 raw 的事实输出不能被现有容量链路承载

原 facts parser 实际接受每查询不超过 131,072 B、总 raw 不超过 139,264 B、系统包不超过 128 项的构造数据。包名、UID、HOME 唯一性符合本轮模型条件，ROLE 空白填充由原 parser 的 strip 规则接受。以下是合法协议数据及原接收实现的验证，不是真实设备采集。

| raw B | 系统包数 | entry UTF-8 B | rawHex B | 原 FactsBundle 模型解码 |
| --- | --- | --- | --- | --- |
| 581 | 2 | 6,542 | 1,162 | 接受 |
| 130,000 | 128 | 407,657 | 260,000 | `PREAUTH_BYTES` |
| 139,263 | 128 | 435,446 | 278,526 | `PREAUTH_BYTES` |

对最后一份固定 435,446 B 输出，**实际原 Capture** 读取计数 stdout=435,446、stderr=0，只保留 262,144 B，原进程 exit 0，但通道判定 `PIPE_BOUND` / semantic FAIL，原资源全部返回。FactsBundle 另复用 16,384 B 的 preauth 解码上限，因此还有更早的表示容量不一致。

证据：`capacity-static-final.json`、`inputs/large-entry.json`、`inputs/large-entry-metadata.json`、`post-audit.json` 及本批 Capture 原返回/journal。固定 emitter 是 tester 端传输夹具；未修改原 collector，也未把这个实验声称为实际 facts_entry 的大 raw 全链路采集。当前原 CLI 固定小数据，未提供合法大 raw 注入口。

建议下一批统一既有 bounded 序列化、生产端上限校验和接收契约，使可承诺的合法数据可交付；**不通过提高既定 cap 绕过本问题**。

### F02 / P1：资格生成成功但原目标接收拒绝

| services 数 | qualification UTF-8 B | review UTF-8 B | Python qualify | 原 PS 目标 |
| --- | --- | --- | --- | --- |
| 0 | 6,948 | 1,078 | 接受 | 合成 HOME 条件正例通过 |
| 1 | 8,130 | 1,646 | 接受 | 合成 HOME 条件正例通过 |
| 8 | 17,127 | 5,629 | 接受 | `GLOBAL_QUAL_BYTE_BOUND` |
| 16 | 27,407 | 10,181 | 接受 | `GLOBAL_QUAL_BYTE_BOUND` |
| 32 | 47,967 | 19,285 | `PREAUTH_BYTES` | `GLOBAL_V2_JSON_BOUND` |
| 68 | 94,227 | 39,769 | `PREAUTH_BYTES` | `GLOBAL_V2_JSON_BOUND` |

8/16 项是原 Python 函数实际接受的合成模型资格，超过原目标 16,384 B 上限后被原 PS 函数拒绝，表明生成与消费字节契约不一致。32/68 项资格字节数仅为绕过构造器的明确静态 wire projection；原 qualify 已拒绝，**不是实际成功签发的资格**。services 数量上限本身不保证任意组合都满足字节上限；本问题重点是成功生产的 8/16 项输出无法被原接收器消费。未改动任何产品 cap。

证据：`capacity-static-final.json`、`inputs/volume-v3-q-*.json`、`ps-v2-results.json`、`models.py`。建议下一整批以原接收上限约束生产端可达表示，保持现有窄授权和证据绑定。

### F03 / P1：原对象来源证明及嵌套关键绑定存在模型反例

通过 `object.__new__(原 Capture 类)` 创建从未执行构造器、从未启动原进程的对象，填入冻结夹具状态，并令 original 为仅含 pid 的 SimpleNamespace，当前 FactsBundle 可接受。此实验是**纯对象模型反例**，并不是真实原 Capture 正例；没有查询旧 PID、创建假实际资源或申请设备资格。仅判断 Capture 精确类型并信任可填充状态，不能独立证明发生过原启动和原返回。

295 个模型原始结果中，76 行不符合预先声明的判据：44 行接受、32 行 KeyError/TypeError/AttributeError 等非受控异常。其中 `nested:release:failure:null` 与合法基线相同，属于 tester 的 no-op 判据错误，必须接受，不计产品缺陷；剩余为 **43 个变更输入或来源接受反例**，不是 43 个独立漏洞。部分未使用元数据在当前源中可选，不逐项夸大为安全问题。需集中复核的是 binding.schema、ownerThread、claimFileId、scope/proof tick、gateReceiptSha256、gateSourcesSha256 等关键绑定缺失/null/异型后仍接受，以及嵌套额外字段闭合。模型在必要处同步计算绑定摘要，用于到达对应校验层，不冒充外部审批真实性。

32 个非受控异常确实阻止了接受，但不等于稳定的精确 gate 原因覆盖。原始模型结果和异常全部保留。上述结论受可信 Python 宿主边界限制，不声称同进程任意对象修改等同于外部攻击成功；真实原 facts 正链路本轮因 G01 未达，不能据模型宣称真实通道已被绕过。

证据：`model-results.json`、`model-unmatched-classification.json`、`schema-and-coverage-addendum.json`、`model_suite.py`。建议下一批最小化补齐原启动/原返回来源绑定与关键嵌套结构校验，统一受控拒绝原因，不新增签名或 IPC 框架。

### G01：新授权测试根与冻结候选白名单不兼容

候选 `tools/entry_gates.py` 的 fixture_root_allowed 仅允许开发 selfchecks/work 或旧 `D1_READONLY_FACTS_PREAUTH01_REVIEW_EVIDENCE/fixtures`。本单只允许新证据根，因此原 CLI 在新根实际返回 `GATE_FIXTURE_ROOT`，未到事实采集。tester 没有写旧根、修改 BASE、复制改版候选、使用 junction 或放宽白名单。

这是交测范围/候选白名单兼容阻塞；不能直接推定实际设备事实逻辑失败。实际原 facts_entry→FactsBundle 正链路状态为 **NOT_RUN_AUTHORIZED_ROOT_INCOMPATIBLE**。请负责人在下一冻结批统一候选支持范围与正式测试根。

### G02：真实外部 review 的 300 秒内交接未证明

库接口支持持有原 Capture 后导出未批准候选，再向 qualify 输入外部 review 字节和摘要；但 CLI 返回退出后不能仅凭文件重建原 Capture，冻结交付未证明一个现有常驻调用端能保留该对象并接收独立外部审批。开发同调用者合成 review 不作为真实外批证据。

本批实际小通道原 Capture 已关闭且在同宿主持有约 1.407 s；其 argv 属于固定 emitter，被原 FactsBundle 以 `V2_OUTER_ENTRY_ARGV` 拒绝，因此不构成 facts 正链路。真实 reviewer 往返状态为 **NOT_RUN_INTERFACE_NOT_DEMONSTRATED**。这不是证明 API 在逻辑上无法实现；现有可信长驻宿主可能满足要求，但本冻结包和本轮证据未证明。未新建 IPC、签名、常驻审批框架，未伪造人工批准。

## 4. 回归、鲜度与 oracle 澄清

当前 V1 346 项由当前冻结实现执行，346 项通过，非沿用旧报告。V2 126 项均达到预期接受/拒绝状态，但 6 项 `factPlanId/factRunId/factNonce` 的 null/异型实际先被 `GLOBAL_V2_REVIEW_PROVENANCE` 拒绝，原 tester 预期 `GLOBAL_QUAL_SCHEMA`。这六行原 pass=false 不改写；属于 tester 对拒绝阶段的假设及深层字段类型覆盖缺口，不能报成六个放行漏洞或深层类型检查通过。

年龄 0/299.999 s：Python 模型及原 PS 目标接受；300 s：Python `V2_FACT_STALE_FUTURE`、PS `GLOBAL_FACT_STALE_OR_FUTURE`；未来 -1 s：Python stale/future、PS 先到 `GLOBAL_V2_REVIEW_WINDOW`。bool/int/float 时钟类型在原调用中拒绝，分别保留 PREAUTH_UTC / GLOBAL_V2_REVIEW_CLOCK 等实际原因。全部为合成状态/原纯函数执行，不能当作真实采集事实或真实外批资格。

阶段 A 的 160 项已逐项追踪，最终解释以 `phase160-trace-final.json` 为准：

| 最终状态 | 数量 |
| --- | ---: |
| 原状态及精确原因符合 | 105 |
| 安全拒绝，先到 provenance 而非预期 schema | 6 |
| 模型接受或非受控拒绝 | 7 |
| 模型判据符合 | 22 |
| 仅静态契约、未独立执行 | 3 |
| 未执行或仅静态 | 12 |
| 实际原通道拒绝非目标程序 | 1 |
| 空 evidence 先到 HOME，未达到服务专门校验 | 1 |
| V1→V2 / V2→V1 完整版本路由未精确执行 | 2 |
| 新授权根不兼容，原 facts 正链路未执行 | 1 |
| 合计 | 160 |

混入旧字段的 extra-field 测试不能替代完整双向版本路由。初次 trace 的宽映射已由单独 final/addendum 澄清，原 trace 和 PS 原结果保持不变。

最终资格实际 44 个顶层字段；原 160 项提案不等于最终 Schema 全覆盖。下列 12 字段未形成独立的删除/null/异型 PS 矩阵：adapterSourceSha256、approved、authorizationKind、bundleSha256、bundleUtf8、candidateUtf8、outerReturnUtf8、reviewSha256、reviewSourceThreadId、reviewSourceTurnId、reviewUtf8、targetPlanId。部分字段在容量/来源等场景涉及，但不能替代完整矩阵。raw 精确边界、部分 HOME/类型组合等未达项目见逐项追踪。**不声称 160/160 通过或最终 Schema 全覆盖。**

## 5. 集中回交与停止点

建议负责人把 F01–F03 和 G01–G02 连同覆盖缺口集中交下一整批开发，先处理既有容量契约、最小来源与嵌套绑定、授权测试根和已有宿主外批交接路径；开发整批自测冻结后，重新独立整包 B。tester 不在本批修改产品代码、不逐问题交接、不补跑浮动源码，不把离线回归当作现场验收。

本批新增原资源全部返回，失败和未执行均保留原值；旧资源/fence/预算/once/UNKNOWN 不变。完整报告和证据清单提交负责人后停止，**不自动进入 SDK、设备、资格签发或任何后续测试**。
