# QUALIFICATION05 阶段 A：独立驱动静态准备报告 V1.0

2026-10-24。结论：**STATIC_DRIVER_PREPARATION_COMPLETE_NOT_EXECUTED**。本阶段完成新独立辅助调用链、可靠结果保存设计、字段/理由表及整包 oracle 的静态准备；没有执行 helper、产品模块或任何动态用例，不签功能通过。05 完整候选尚待负责人核包正式派 B；D1未过、M0未启。

## 1. 范围与产物

按 `docs/tester/D1_FACTS_V2_QUALIFICATION05_TESTER_REQUIREMENTS_V1.0.md`，SHA256 `02d8b24c6941595a01797cc9eeaf873507d52ca2aa45a4faf8920c1268f9f553` 执行，工作前读取三协调文档顶部。

只读取冻结04候选 `docs/coder/d1android02-facts-v2-qualification04` 及自己的新准备文件。04 manifest `a577b3aab5a3b54f221ad3b4b049447d332ccca8744ecf9bccb1cb689768cc73` 的 **284项/5866724B**、ZIP **285唯一成员**逐内容/大小/hash静态核验 bad=0。旧04B只核报告 `307a32ad…f829`、manifest `971ec393…8988` 的文件摘要，**没有重新查询、收尾或修改旧capture1**，没有读取05浮动源码。

新文件仅在 `D:/CodexProjects/VideoKit/docs/tester/D1_FACTS_V2_QUALIFICATION05_PHASE_A_EVIDENCE`（R）及本报告：

| 文件 | 用途 |
| --- | --- |
| independent_driver.py | 共同调用规格、Capture前准入、实际budget_models调用点、原返回与结果文件判定 |
| independent_budget.ps1 | 独立辅助夹具，18项明确案例，逐项与最终持久化 |
| final-checks/driver-static-checks.json | 当前最终19项AST/文本结构核对，均为STATIC_STRUCTURE_MATCH |
| final-checks/call-template.json | argv/executable/cwd/env/源根/输入输出唯一模板，approved=false |
| final-checks/helper-fields-and-reasons.json | 输入、输出、ticket/ref/delta真实字段及18项静态预期理由 |
| final-checks/runtime-adapter-contract.json | 正式B需绑定的既有原IO/Capture适配与全图模板 |
| ps-static-checks.json | PS仅解析AST，语法错误0、裸false/true/null命令0 |
| oracle-and-readiness.json | 原63项、辅助18项、驱动15项、新receipt/容量12项的分层计划 |
| delivery-manifest.json / delivery-freeze.json | 本阶段准确文件、字节和摘要 |

早期 `driver-static-checks.json` 与 `final-static` 为纯准备修订历史，最终以 **final-checks** 为准；没有实际调用或重跑。规划行有不同层次及重叠，不以108行充当108项动态通过，也不要求无意义的组合补数。

## 2. 辅助实际调用与准入规格统一

`freeze_helper_tuple` 和真正的 `budget_models(runtime)` 都调用 **build_budget_spec**，只从新driverRoot选择 **independent_budget.ps1**；新驱动中不存在候选 `selfchecks/budget_models.ps1` 选择路径。

固定 argv 为：已绑定PS解释器、`-NoProfile -NonInteractive -File`、新独立脚本、`-InputFile` 新scope/budget-input.json、`-OutputFile` 同scope/budget-result.json。executable与argv[0]相同；cwd/env参数均明确为None，继承的实际worker cwd和规范化环境摘要另由正式order冻结并检查。shell=false、close_fds=true、stdin=-3、stdout=-1、stderr=-1，完整kwargs与实际原Capture.launch的形状对应。

顺序为：**共同spec→guard.admit_before_capture→成功才调用construct_capture_after_admission→原Capture.launch再次check→原Popen**。第一次准入失败分支保存分类并raise，不能落到Capture/Journal工厂。Guard还核driverRoot/scopeRoot、源与输入存在及摘要、input候选/admission根和源摘要、旧输出不存在、正式B标记与实际host；实际constructor前再次核同一完整spec/host/source。审计仅观察，不在Windows临时资源已创建后通过audit抛错。

因此本次准备针对04T01的修正不只是改一个字符串：实际调用点、冻结tuple和构造前检查共享规格，并额外绑定order根，避免“准入声明正确、调用仍指旧地址”。**这些是AST/文本结论，未实际构造Capture验证。** 05接口、原Capture构造/生命周期及完整graph还必须在正式候选冻结后按准确源绑定，不能从静态准备推定运行有效。

## 3. 结果保存与失败证据

辅助脚本每个Check后保存当前结果；最外层try/catch/finally再尝试最终保存。只有完整到达18项才complete=true，原异常保留fatalError；布尔均用 `$true/$false` 或明确bool转换，没有把false写成命令。输出包含schema、完整/预期/实际案例ID、每行want/reason/pass/used/reads、汇总布尔、fatal、synthetic/realAuthority、source/failure/fullReference delta。OS写入本身失败仍要由原exit/stderr证明，不能保证文件凭空存在。

驱动在原Capture确实返回后，**先保存原stdout/stderr/exit/归还状态，再读结果文件**。文件缺失返回RESULT_FILE_MISSING；无效/重复JSON、超界、schema不符、未complete、ID集合或顺序不符、布尔异型、理由不符、汇总不一致均分别记录。每行want必须等于冻结oracle理由、pass必须与实际reason一致；还核syntheticAuthority=true、realAuthority=false、actualProductionOwner=false，不凭allPassed摘要决定原生产验收。

真正原调用未返回/RETAIN时，在任何结果文件读取之前走既有原owner保留协议并停止新增，不二close/kill/attach/退款。原等待/读/close证据不能由输出文件代替。源/输入/结果读使用正式B绑定的既有owned-IO receiver；本阶段没有新造读取或诊断框架，也没有执行这些适配回调。

当前JSON失败样例只是序列化规格，不是运行inspect_result_file所得。缺文件、部分输出、异常退出与正确完整输出的真实验证仍为PLANNED_NOT_RUN。

## 4. 独立helper字段和理由

输入精确12字段：schema、artifactRoot、candidateRoot、admissionPath、admissionSha256、ref、root、name、wire、context、expectedFingerprint、expectedCaseIds。文件路径必须为独立脚本根下新fixtures scope，输入/输出名固定；module加载前核输入结构、完整18项ID和admission源hash。真实ref含path/bytes/sha256/volumeId/fileId，由正式B的新有限文件产生，不用假fileId冒原文件证明。

ticket/delta字段按冻结04原接口列出；ticket的scope/generation/owner/role/version/baseGate/baseRunner/reserve必须显式。sourceDelta每事件含pathSha256、reserved/actualBytes、opened/closeReturned/unknown；正式B逐项重新算路径hash并核实际计费/原close，不能只验64位格式。

| 案例族 | 依据冻结04的预期理由/结果 | 状态 |
| --- | --- | --- |
| 缺authority | GLOBAL_V2_SOURCE_AUTHORITY_REQUIRED | 计划未跑 |
| 正常固定文件、复载保留同原usage、真实wire配显式合成ticket | ACCEPT，必须保留原文件读取/关闭证据 | 计划未跑 |
| 重复初始化（两处） | GLOBAL_V2_SOURCE_AUTHORITY_ALREADY_BOUND | 计划未跑 |
| 错hash / 错fileId | GLOBAL_V2_EVIDENCE_ORIGINAL_BYTES / FILE_IDENTITY | 计划未跑 |
| 四次消耗后/复载后拒绝、零预留 | GLOBAL_V2_EVIDENCE_SOURCE_BUDGET | 计划未跑 |
| 四类base+reserve超界 | GLOBAL_V2_SOURCE_AUTHORITY_CAP | 计划未跑 |
| 缺base / 错scope / bool base | GLOBAL_QUAL_SCHEMA / SOURCE_AUTHORITY_BINDING / TYPE | 计划未跑 |

18项逐项ID和完整理由见字段表。辅助新建的ticket是**明确合成权威模型**；其有限原文件helper调用不等于真实Parent SourceBudget接线通过。原生产权威必须另在实际同一Gate/Runner/Owner链上验证。05新API/符号/理由当前未读，正式B必须对已冻结新源复核后绑定；不能盲沿旧VideoKitQ03变量名或旧消息签通过。

## 5. 后续整包oracle与执行门

保留阶段A原63项并明确全部待正式05：原owner/pid/thread/claim/scope，读前永久reserve、重复body/packet计费、原归还后单次delta，坏类型/陈旧/重复/拒绝/pending和原返回；尾项未跑不得回填旧开发或02。

新增重点为原writer句柄产生receipt volume/fileId→原writer/控制器实际归还→原console→Owner同原打开句柄核身份/大小/hash/前后身份及原close。同路径同字节替换必须拒绝，不能只从替换后文件新算身份或信裸console引用；samebytes替换不等于事实篡改。正常正链与错固件/替换负链各用全新scope，原Runner额外receipt/三次复读照常计费。

完整UTF8容量同时覆盖独立evidenceRoot和home、wire/body/permit/policy、Snapshot/metadata/identity/delta/admission/receipt/console及原逻辑转发/读取，资源前准入，原cap保持。Q04-G01仍仅条件序列化推导：没有OS物化、target实际接受或实际超限，不能挪成05实测。已知会进入保留等待的超界场景只做有界模型/纯预检，不启动原控制器制造永久UNKNOWN。

全图模板预计24、若替换被误接受继续global则条件上限26；只是规划，最终以正式冻结05原调用图核准。届时总动态360/320秒、读取1GiB、产物16MiB、辅助96、并发1/产品retry0，SDK/设备/Gradle/Git0；prefix不代七角色、OFFLINE不代真人。当前call-template的stage为STATIC_TEMPLATE、approved=false；没有B order或实际新scope。

## 6. 本阶段结算及回交

本阶段只做字节核验、AST/文本和JSON序列化。**产品模块import/PS dot-source/产品函数/Popen/Capture/Gate/claim/once/动态/SDK/ADB/设备/Gradle/Git均0**；05浮动源码读取0。旧capture1未查询、未收尾，旧false/custody1/分类/FAIL/UNKNOWN/账本/once不变。

本报告、新驱动、字段理由表、oracle和manifest整批一次发负责人，不逐问题交接。阶段A完成后停止；等待完整05经负责人核包正式派B，才绑定准确新候选与既有运行时适配、冻结全图及新输入，不凭本准备文件自行执行。
