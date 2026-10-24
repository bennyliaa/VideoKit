# QUALIFICATION04 独立整包 B 测试报告 V1.0

2026-10-24。结论：**FAIL_RECEIPT_FILE_IDENTITY_CONTRACT_AND_TESTER_AUX_COVERAGE_BLOCKED**。

新测试根已实际完成最大 facts、独立 OFFLINE reviewer、原完整生产前置合法/错固件链、同原来源账本并回及 Gate64 次边界。**同路径同字节替换 receipt 后，原生产链仍接受并完成**，不满足派单要求的固定原文件身份替换拒绝。辅助组又因 tester 驱动调用点地址未同步，被原固定参数门拒绝；辅助补证及尾部模型/V1 未执行，不能签整包通过。保留全部原结果和未执行项，集中回负责人，不重跑本批。

## 1. 准确来源与执行范围

按 `docs/tester/D1_FACTS_V2_QUALIFICATION04_INDEPENDENT_B_DISPATCH_V1.0.md` 执行，SHA256 `953011db6c50a065f08282f1e99125ea096adc19a2a60d335672213656893646`。工作前读三协调文档；阶段 A 63 项 oracle 及负责人裁定作为本批追踪依据。

唯一候选：`docs/coder/d1android02-facts-v2-qualification04`。开发报告 `1426449caa7dc700c34596ecbf6ef864de215b4b809ef07373ef497eedf6dfe8`；manifest `a577b3aab5a3b54f221ad3b4b049447d332ccca8744ecf9bccb1cb689768cc73`；ZIP `1c08d782367879d46a472f22ae32000733f4911e4b755b7e28e34d5b219bb750`。独立前后核 **284 项/5866724 B，ZIP285 唯一成员逐内容/大小/hash 均 bad=0**。

source31 `8ec622c56d4a23e43edd0b5631a2e40cff0836a53672dd8b6f5fbb9d197a5cf9`；gate23 `22b2bda720fd5c6a584ad6d3088246b00937bb0165ce571c13078950d76693de`；开发 profile `1613aab8d6940b9f2ab4dfde0a38e6e7d94908a07af111d2795a81e8f12ca36e`；原七角色 plan `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8`。

证据仅写 `D:/CodexProjects/VideoKit/docs/tester/D1_FACTS_V2_QUALIFICATION04_INDEPENDENT_B_EVIDENCE`（R）；唯一新 fixtures scope 为 `R/fixtures/347bcbab`（W）。本报告与最终清单同属新04前缀。未写候选、未运行开发 worker 主入口，未重放开发 scope/once。部分场景函数从冻结开发测试派生并在独立 root/输入下执行，来源明列于 `harness-provenance.json`；独立加入新辅助脚本、物理 receipt 替换及视图/容量模型计划，不把同判据重复执行冒充独立验收。

## 2. 一次实际批次与原始结果

order SHA256 `3852b65df8d5d80a7f9e69044c5d7b35b4a549d32c42774605cf9b757a1ac11b`；315 项 order 源执行后未变。输入、驱动、全图和预算在实际前冻结；批次一次，产品 retry=0。

| 组 | 原结果 | 实际范围 |
| --- | --- | --- |
| qualification | PASS | 3 原辅助返回0/7/0，各在5秒内 |
| actual-max-facts | PASS | 真正原 facts_entry→collector→Capture→FactsBundle，139264 B/128 包 |
| independent-review | PASS | 3 个有限独立 reviewer，准确新目标 scope 的合成批准 |
| production-prefix-positive | PASS | 原 Runner/Owner/PS 完整顶层 identity→global_idle，正常原账本并回/Gate64 |
| production-wrong-firmware | PASS（负例符合） | 原 identity 拒绝，未启动 global 后继 |
| receipt-same-byte-physical-replacement | PASS（执行断言） | 替换后原链继续两角色；**独立拒绝契约判据 FAIL** |
| source-budget-and-reload-models | FAIL | 我方驱动 EXACT_FROZEN_GRAPH_ONLY 拒绝，未进入该 helper Popen |
| independent-view-and-contract-models | NOT_RUN_STOP_NEW | 模型尾部未执行，不能拿脚本存在充覆盖 |
| V1-regression | NOT_RUN_STOP_NEW | 本批独立 V1 未执行，不回填开发346或旧02结果 |

worker 53.860 s，外层 55.172 s，原工具返回 exit2；没有超出360 s/320 s停止新增界。预定26图，实际 **父 Popen15+facts 内2+PS .NET5+外 worker1=23**；父 constructor/audit15/15一致。未发生的是 auxiliary、independent-matrix、V1 三个宿主调用。原始 allPassed=false 保持；各组“执行断言 PASS”不代独立产品判据。

实际启动的7个辅助 Capture 原 wait/readers/流/H/journal 均返回；5个原生产控制器原 wait/readers/流/H 返回，3个原目标 Gate claim 均归还。Python immutable 原文件事件 **117/117 close 返回**；PS 来源 delta 的 **14 次实际 body/packet 原 open/close** 均 returned，unknown=false；原外层进程全部返回。

**原始 auxOriginalsReturned=false、custody.capture=1，不能写成全清零。** 这一个是 helper 前构造的 Capture：构造即进入 custody，launch 在 `registry.check` 处拒绝，尚未写 launch-intent/尚未进入原 Popen。对应目录空、无 Guard constructor/audit、无该 helper 原进程。按源码顺序和实际证据分类为 `KNOWN_GUARD_REJECT_BEFORE_ORIGINAL_POPEN_WITH_UNFINALIZED_CAPTURE_OBJECT`；不是已启动原进程的返回未知，也不伪称对象已完成原收尾。原字段保留于 `prelaunch-pending-classification.json`，没有二次 close、kill、attach、补 ACK 或退款。**未观测到新增原资源 UNKNOWN；有1个未完成收尾的已知前启动对象记录。**

## 3. 实际事实、外部夹具和原生产证据

本轮不同包名前缀的新 raw **139264 B/128 系统包**，原 packet/stdout **193538 B**，原262144 B cap保持；FactsBundle 从同一已归还原 Capture 验来源及完整 raw/receipt/hash。三条新 target 的 candidate/review 均独立有限进程实际返回，宿主持有同一原 Capture，不重建原对象，不刷新 collectedAt。全部为 **OFFLINE 合成独立夹具，realHumanApproval=false**，不代真人批准或设备事实。

| 目标 | 原生产角色语义 | 原 console B | Gate B/次 | Runner B/次 |
| --- | --- | --- | --- | --- |
| positive | identity PASS、global_idle PASS | 2949 / 3313 | 9102472 /64 | 9674524 /73 |
| wrong-firmware | FACT_IDENTITY_FIRMWARE_DISAGREEMENT | 3180 | 8555540 /46 | 8967275 /47 |
| receipt-replace | identity PASS、global_idle PASS | 2950 /3313 | 9102556 /64 | 9675099 /73 |

两条正常完成目标均在同一原 claim 持有期间实际读至 Gate64 次，第65次 SOURCE_READ_BUDGET 在内容 open 前拒绝；下一角色预留 SOURCE_OWNER_BUDGET_BEFORE_LAUNCH，无后继 Popen。错固件目标只执行 identity，原已知失败后释放 claim；没有 global 进程。

五个 ticket 的实际来源结算如下，永久 reserve 与 actual 的差额不退：

| 目标/角色 | version | 永久预留 B/次 | actual B/次 |
| --- | ---: | --- | --- |
| positive identity | 0 | 273464 /2 | 204858 /2 |
| positive global | 1 | 546928 /4 | 409716 /4 |
| wrong-firmware identity | 0 | 273488 /2 | 204882 /2 |
| receipt-replace identity | 0 | 273492 /2 | 204886 /2 |
| receipt-replace global | 1 | 546984 /4 | 409772 /4 |

原 Parent 在 Popen 前向同一实际 Gate/Runner 预留，原 PS 读前占额，原归还后并回5份 delta，source pending 均清空而永久费用保留。实际 identity2 次、global 前驱+当前4次符合阶段 A 路径推导。post-audit 独立重算每个事件 pathSha256，均逐次对应本轮 wire body 路径及原 facts packet 路径；不是只验64位格式。

新增 receipt 回读走原 Runner.read_file，读前按 stat+1/次数保守占额，保留 reserve 后3次 integrity 复读和每控制器 receipt 的额外来源成本；merge 未把这些合法追加重置掉。Runner256次/512 MiB、Gate字节临界和拒绝/复载细项，本轮未独立执行，不能用上述正常费用代全边界证据。完整七角色的四组八次仅静态；实际 prefix2 不代完整七角色或 D1。

## 4. 集中问题和我方执行错误

### Q04-B01：receipt 同路径同字节替换未拒绝（派单身份契约不满足）

第三个新目标 scope 在原 PS identity 退出，原 Owner 已完成其 wait/readers/流/H/console 写入后，到第一次原 receipt 回读边界执行有限替换：保留原文件到 `identity-receipt-original-retained.json`，在同路径新建完全同字节文件。NTFS FileId **281474980499820 → 281474980499823**，字节 **4339 B**，SHA256 同为 `b0c4c79cf4b5bd5b9548fe8dcb8886553a357f686467779a0b45dbbc581741cd`。

原绑定到实际 Runner 的 read_file 随后正常返回同 hash，identity/global 均完成，5份原 delta 中的该目标2份正常并回，claim归还。证据是 W 下 `receipt-replacement-observation.json`、`receipt-replacement-read-return.json`、`production-receipt-replace.json` 及全部原 console/receipt/native返回。

该故障夹具仅包裹本轮第三个实际 Runner 实例的 read_file 调用边界：在目标 receipt 读前替换自己新根的文件，随后委托**同一实际 Runner 的原 read_file**；未改候选源、未重放原调用、未伪造原 Capture，前两条正常/错固件链没有这个包装。原 receipt 与替换文件都保留。此注入是授权新根的物理替换夹具，不宣称是完全无夹具的正常运行。

根因：新 console 提供 receipt SHA，Owner 校 hash/大小/schema/scope/id/pid 后还原 bindings/readers/input；新增 receipt 读取沿通用 Runner 来源读，未绑定原 receipt 的固定文件身份及同原文件句柄前后身份。**hash 能证明字节相同，不能区分相同字节的替换文件**。这不表示修改了事实字节，也不表示绕过真人批准或原内核资源归还；但本单明确要求同路径替换拒绝，当前实现未满足。建议下一整批明确该新增原文件视图的身份权威及受控替换拒绝，保留既有原进程返回和原来源计费，不靠删事件/加裸引用避过。

### Q04-T01：tester 调用地址未同步，辅助及尾项未执行

我方 Guard 固定允许 `R/independent_budget.ps1`，但派生 worker 的 budget_models 调用点仍指向候选 `selfchecks/budget_models.ps1`。原 launch 先做 registry.check，立即 EXACT_FROZEN_GRAPH_ONLY 拒绝；没有执行候选已知 false 输出错误的脚本，也没有执行我方独立脚本。Capture 已构造但未进入 Popen，故留下上述 custody1，触发停止新增，后两组 NOT_RUN。

这是我方派生驱动遗漏，**不是产品辅助函数拒绝、不归因环境或开发输出错误**。当前独立补证缺 authority/复载/重复初始化/hash/identity拒绝计次、纯坏事件/Runner边界/prefix、视图变更矩阵、V1 等均未跑；脚本存在或语法检查不算完成。旧开发辅助 FAIL 及结果缺文件不更正，独立结果也不回填。

本批原生产 once 已消耗、唯一外层 order 已执行，故不适用“纯准备未入产品”修订后继续例外。按本单固定图、一次批次、产品 retry0 保留原驱动/FAIL/停止结果，不暗改源或补开第二次 worker。下一批应在 Capture 构造前核对**实际调用点**与准入 tuple，且在 helper 前校验预计源地址；不能只检查 Guard 声明或 AST 语法。由负责人集中安排补证范围。

### Q04-G01：独立证据目录长度未纳入完整容量证明（静态条件缺口）

生产 home 已有210字符门，开发按此做 Unicode 模型；本轮静态核到该门，**不把 home>210 当合法反例，也不要求缩小此原范围**。但是 wire 的独立 evidenceRoot 与生产 home 不同，当前 target/引用路径规则未展示同等长度界；开发容量模型把 authority 放在短 folder，不能自动覆盖任意合法来源目录表示。

以本轮实际短路径 identity 控制用量 **48297 B**作前像，仅做文件后序列化模型：独立 evidenceRoot 7189字符、单组件180字符，wire15564 B<16384、permit26024 B<32768、policy24050 B<65536，生产 home仍120字符；permit及policy各增长14188 B。identity逻辑读包含二者，得到控制字节**下界76673 B>65536**，其余消息增长尚未加。`capacity-static-addendum.json` 保存推导。

**没有创建该长路径文件、没有签发该资格、没有实际调用 target 接受该路径，也没有运行长路径控制器或制造溢出/挂死。** 路径 OS 物化、固定身份及全部可达性均未证明；因此这是源字段表示范围与总体控制预算的条件缺口，不能报成实际溢出。下一批需给真正合法可达来源路径上界/完整包容量证明，或在现有契约内明确受控前置准入；不能单以 home210、delta定长64位或本轮短路径通过代整体证明，不能提高原 cap 或静默缩合法范围。

## 5. 修复关闭范围与63项追踪

| 项目 | 本轮独立结论 |
| --- | --- |
| 固定 helper 恢复 | 47f9原字节静态一致；真实原入口已越过原阻断，未重放03 USED |
| B02-01 identity wire适配 | 本轮原完整前置合法/错固件链得到限定实证；不代完整七角色 |
| B02-02 原来源权威 | 正常 ticket/并回/14次原文件关闭/Gate64有实际证据；辅助拒绝/复载及其他边界未独立补证，**整组不关闭** |
| 新 console receipt视图 | 实际短路径表面大小及原计费成立；文件身份替换拒绝失败，其他错误矩阵未执行 |
| console/admission/逻辑控制容量 | 本轮实际短路径正常返回；完整合法来源路径上界未证明，静态缺口保留 |
| V1、原类型模型、鲜度等 | 原开发/旧02已有限定层只能准确参考；本轮独立尾项未跑，不冒新通过 |

R/phase-A63-trace.json 逐项保留：静态预检部分8、实际新scope限定12、因驱动前构造器拒绝/停止未跑39、receipt替换实际接受1、其他准确未跑1、短路径实际+静态大小缺口1、读前准入代码已改但边界未跑1，共63。**不报63/63通过**。最终wire15/展开43保持冻结 Schema；对应全字段模型未在本轮执行，不以静态字段数冒类型覆盖。真实短读/OSError/close UNKNOWN、reparse/硬链接和长路径超界场景未注入。

## 6. 预算、原件及交付停止点

限额：动态360 s、320 s停止新增、读取1 GiB、产物16 MiB、辅助96、并发1、产品retry0。分区预留 facts Gate256 MiB、目标 Gates合计256 MiB、Runner sources合计256 MiB、驱动模型192 MiB，总960 MiB；原Gate256 MiB/64、Runner512 MiB/256门未提高。外层可观测源读6350923 B/319次，不代表全系统物理IO；固定包/解释器/OS隐式IO不伪称全部测量。最终文件数、字节和摘要见 delivery-manifest/freeze。

原03候选101、02候选277、01候选132、阶段A14、tester02证据259、tester01证据209后核均 bad0；旧 FAIL/UNKNOWN/预算/once 不改。新增实际产品进程均原返回；原始前启动 custody1/false 不抹除。SDK/ADB/设备/Native route/TCP/Gradle/安装/媒体/Git及旧运行对象查询0。原 Runner 对冻结产品文件做不透明完整性hash，不是安装或媒体测试，不触及 test_media。

本报告集中交负责人，安排下一整批处理 receipt 身份、完整容量义务和我方辅助补证，不逐问题交接。保持本批所有源、order/once、原FAIL及未执行状态冻结；**不自动设备、Git、修复或重测。D1未通过，M0未启动。**
