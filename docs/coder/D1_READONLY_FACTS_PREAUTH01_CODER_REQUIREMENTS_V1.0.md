# D1 READONLY_FACTS_PREAUTH01 集中开发要求

2026-10-23；负责人已审CONTRACT03完整B，正式派一个最小只读事实采集授权功能簇，开发及离线自测授权有效。本批不是现场采集/安装/媒体许可，也不批准原签名、公钥、密钥托管或IPC框架方案。

## 1. 准确输入与目的

- 原B报告 `docs/tester/D1_GLOBAL_IDLE_CONTRACT03_INDEPENDENT_B_REPORT_V1.0.md`，SHA `f67cdf23cf0132fe6ae1d9ef50976ef91de06035e5e729cf2a77278c1f96925b`；manifest `19cf9a1e3d8f01c08ed8d8727ca2495bc9b836eb72bc1a7da939a7bd49824bb2`，负责人核744项/2668183B、bad0。接受已覆盖范围，原FAIL_TARGET_COVERAGE_GAPS及两原场景不改绿；没有新确认产品源码缺陷。准确小追加已实际覆盖source门，物化内过期剩余由tester独立原源补验。
- 源输入为冻结CONTRACT03目录，source17 `4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93`、gate9 `9cff279ddb9e60632b1422dca16af0dac4ab1922fb6b0b27c5a232055e439d72`、plan `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8`。原98/SELF02 484/A408/B744记录和全部旧FAIL/UNKNOWN/once均不改。
- 当前实际问题：原外部authority必须在原Gate.prepare之后绑定运行时routeProof，却要求外部双hash回传仍在proof10s/gate30s内。此前同调用者合成issuer并未证明真实外部往返。要在不扩窗、不添加签名/密钥/IPC设施的前提下，做一条明确预授权、原对象运行时绑定的可执行路径。

## 2. 负责人批准的本批最小契约

负责人在此**批准开发和离线验证以下预授权契约修订**，实际LIVE仍需新候选独立验收后另派准确执行批：

1. 真实批准对象改为在Gate.prepare之前即可冻结并由负责人明确提供外部hash的 `GLOBAL_IDLE_FACT_PREAUTH_V1`。其内容封闭绑定：准确源seal/gate/collector/binder/runtime/SDK/factPlan、唯一scope/plan/run/nonce、LIVE或OFFLINE_FIXTURE模式、固定设备serial/model/API/user、固定七项只读query/action、原SDK一次/字节/时间/无retry预算、负责人来源及notBefore/expires。有效区间不超过原authority90s，不作全局/长期/任意后续任务授权。
2. 新入口必须从外部参数获得准确已批准template hash，缺失、默认、来源/任一字段/模式/时间或预算不合均在构造前拒绝；不能只信sourceThreadId/approved=true字符串，也不能由调用者自写一个template就自动认领负责人批准。模板可预先生成以供审阅，生成本身不赋予执行权。
3. 原Gate.prepare后，只由同进程、同原prepared且未消费/未换owner的Gate读取真实route/proof和原身份，产生类型明确的 `GLOBAL_IDLE_FACT_RUNTIME_BINDING_V1`；绑定原template hash、原scope/generation/holder、实际route/proof hash、时钟和当前源。该层是负责人预先批准的确定性运行时填充，不冒称负责人事后逐字批准了尚未出现的routeProof。
4. 接收器在原proof10s/gate30s内重新核同原Gate与该绑定，仍只调用原固定一次事实采集：model/api/firmware/user/system/role/home七项，SDK1/并发1/retry0、stdout139264/stderr8192/合147456、qualification15/outer30/proof10/whole90全部不扩。LIVE共享claim路径、无ADB覆盖env、原source/SDK验证与原Popen/reader/wait/H/owner归还保持。不得查询额外资料或开放任意shell/argv，不自动安装、global_idle放行或目标七角色。
5. 复用原采集/返回机制。可在新候选中将旧授权验证与共同的私有原capture路径分离，保留原V1外部双hash验证分支；新模式须独立、显式、封闭校验。**禁止生成一份合成legacy authority/approval再走旧路径伪称原外部批准。** 默认拒绝、模式错配、旧许可借用、重放/换Gate/换scope/过期均拒绝，不因失败退款/rearm。
6. 新事实回执明确记录authorizationKind、外部preauth hash及runtimeBinding hash、原采集/原外层返回证据；不得将新字段塞进旧factAuthoritySha/factApprovalSha而保持旧语义。若向后续资格接收提供适配，使用明确、严格区分的qualification V2字段/Schema，保留V1兼容；V2仍需负责人对真实facts/窄HOME服务政策的独立review绑定、目标source/scope/plan、原返回与至多300s新鲜期。**预授权只授权取事实，不批准资格、系统服务或安装/媒体。** 本批可做显式OFFLINE合成端到端示例，真实资格不生成。

把上述内容做成准确字段表/Schema、调用图和批准来源说明；若发现现有模型无法在此边界内实现，先集中交具体契约冲突，不自行扩大权力/时窗或加设施。

## 3. 新候选、实现与一次整批自测

新目录 `docs/coder/d1android02-readonly-facts-preauth01`，不改原CONTRACT03目录/17源。只实现现有Gate/collector的薄适配和必要明确CLI入口；不重造进程管理、claim/注册表、捕获器、通用授权或调度框架。不升级/新依赖，不改产品FIX02/Native/runtime实现，源码新增项须进入完整source/gate/调用图/许可pins，不能沿用旧17/9 seal冒同一候选。

先固定全部新源、预算、驱动和精确profile再一次集中离线自测：

- 规范Schema/整数/大小写重复/额外字段及每个关键字段删除和篡改；外部template hash缺失/错误、caller自生成未外批、过期/未来、旧nonce/scope/source/route/mode、非原Gate/已消费/不同holder均精确拒绝。错误程序与未知Start/close只纯模型，不实际触发构造后审计异常。
- 原prepared OFFLINE Gate与固定producer的实际新预授权接收→runtime绑定→原capture→原返回/唯一释放；证明运行时绑定不用等待人或跨会话手工补hash。正例如实标明外部批准输入为合成fixture，不能声称真实负责人往返或设备资格已测。
- 旧外部V1路径原准确正/反例和至少原45矩阵/17条件正例回归，preStart和原返回机制不回退；如新增qualification V2，集中验证完整正例、所有身份/原返回/窄策略/目标/时间负例及V1/V2错配。可用一个明确模拟目标链检查数据接回，不循环编译/自检。
- 原source/control读写和新增template/binding账本全计；没有免费重读、重复ACK或以逻辑量代全部物理IO。直接有限原件已知返回后归还，未知即停新增并集中报告，不重试未知scope。

开发动态整批总360s、320s停新增、并发1/retry0；读取最多1GiB，产物16MiB，辅助进程96以内且先按实际图预存。实际估算不适配先交静态完整估算，不事后扩额。复用已接受SELF/SELFCHECK02的成熟返回机制，新完整argv/cwd/env及profile仍在Popen构造前验证；Windows audit仅观察，不在临时pipe后主动拒绝。

## 4. 并行、版本与交付

tester在原冻结CONTRACT03上补验并准备准确GitHub WIP检查点；你只写本次新目录，不修改其输入、原文档或共享Git/index，不按共享HEAD/分支变化替代固定source身份。负责人现行文档可能按报告更新，但不属于可浮动的测试输入。

本批实际SDK/ADB/Native route/TCP/help/设备/Gradle/媒体均0；不运行新LIVE模板、不发真实authority/资格，不处理任何旧未知进程、会话、锁、预算或once。原签名/密钥/IPC方案保留历史未实施，当前改用本明确最小模式。

交一份完整源码/差异、Schema/调用图、外部预授权与运行时绑定边界、准确未来执行提案（approved=false）、自测逐项及原返回/NOT_RUN、source/gate/plan/full manifest/唯一ZIP和独立回执。完整冻结后主动整批报告负责人，负责人审核后才交tester独立整包B；不逐问题交接、不自动现场。D1未通过/M0未启，主里程碑、Flutter/独立Kit/既定框架许可及全P0不变。
