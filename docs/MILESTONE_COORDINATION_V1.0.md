# 里程碑开发与测试协调规则

<!-- CURRENT_STATUS_PREAUTH01_COVERAGE_CHECKPOINT01:BEGIN -->
> **2026-10-23 最新完整B已审，集中派PREAUTH01开发与COVERAGE_CHECKPOINT01。** [CONTRACT03 B报告](tester/D1_GLOBAL_IDLE_CONTRACT03_INDEPENDENT_B_REPORT_V1.0.md) SHA `f67cdf23cf0132fe6ae1d9ef50976ef91de06035e5e729cf2a77278c1f96925b`；负责人核manifest `19cf9a1e3d8f01c08ed8d8727ca2495bc9b836eb72bc1a7da939a7bd49824bb2` 744项/2668183B、bad0。10组PASS、11故障9精确命中/2未覆盖，无新确认产品源码缺陷或资源UNKNOWN；原FAIL_TARGET_COVERAGE_GAPS保留。接受实际单字节OWNER_SOURCE_PIN_ENTRY补充层作为source门覆盖，原大输入cap场景不改绿；物化中过期的原9s前置失败仍缺目标阶段。
>
> **coder下一整批**：[READONLY_FACTS_PREAUTH01开发要求](coder/D1_READONLY_FACTS_PREAUTH01_CODER_REQUIREMENTS_V1.0.md)。只在新目录开发固定七项只读facts的外部hash预授权模板→同原Gate运行时route/proof绑定→原capture返回薄路径及明确必要Schema；负责人本批批准该最小契约开发/离线自测，不批准实际LIVE执行。保持原90s/10s/30s等门，不增加签名/密钥/IPC框架，预授权不等于资格/服务政策或安装媒体批准。完整冻结回负责人后再整包交tester。
>
> **tester下一整批**：[COVERAGE_CHECKPOINT01要求](tester/D1_CONTRACT03_COVERAGE_CHECKPOINT01_TESTER_REQUIREMENTS_V1.0.md)。在旧17源冻结上静态先算合法时序区间，最多一次新scope补验物化内过期；不暖机/循环换TTL或改旧失败。原件全部返回、报告冻结后，按准确逐文件白名单将当前CONTRACT03离线快照与报告提交私人VideoKit仓库的WIP评审分支并创建草稿PR，保留FAIL/NOT_RUN、排除二进制/媒体/凭据及新PREAUTH浮动代码；不合并main或发布。原source/98/484/408/744和旧UNKNOWN保持。
>
> 双方输出隔离，coder不操作共享Git/index或原冻结文件；tester的Git操作仅在其动态结束、准确清单固定后执行。负责人在本Git检查点回报前不改这三份协调文档的当前快照。其他新报告可只读审核，不因此阻断独立开发。旧进程/锁/会话不查询、kill、二close、补ACK退款，也不是推进前提。
>
> 当前实际SDK/ADB/Native route/TCP/help/设备/Gradle/媒体0；新模板/authority/真实facts与现场尚未派。**D1未通过、M0未启动**；主里程碑、Flutter/独立Kit/既定成熟框架版本许可及全P0保持。下方旧状态为原时点历史。
<!-- CURRENT_STATUS_PREAUTH01_COVERAGE_CHECKPOINT01:END -->

<!-- CURRENT_STATUS_CONTRACT03_INDEPENDENT_B:BEGIN -->
> **2026-10-23 已审双方完整结果，正式派CONTRACT03独立整包B。** [开发SELFCHECK02报告](coder/D1_GLOBAL_IDLE_CONTRACT03_SELFCHECK02_REPORT_V1.0.md) SHA `9acdf4089a4134997e53adf6a765b11ca4f6ca48a35a256eeaa21b7497f30246`，负责人核484项/5286017B、bad0及ZIP485唯一成员。三次驱动资格与原返回已证，14组13PASS/1已知时限FAIL、346语义通过；有限故障簇首两项提前gate拒绝未到目标、后九项NOT_RUN，原FAIL不改为全绿。当前17源`4881f181…5e93`/gate9`9cff279d…9d72`/plan`b2802b65…26c8`和原98冻结未变。
>
> [独立语义A](tester/D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_REPORT_V1.0.md)400/400及408证据bad0已限定接受。tester现按[正式B工作单](tester/D1_GLOBAL_IDLE_CONTRACT03_INDEPENDENT_B_TESTER_REQUIREMENTS_V1.0.md)集中审整个修订：可以明确引用同源已验收A，重点核原collector/完整入口、同一新tester根、preStart/七角色END/once/原释放、全部11个故障目标及准确小追加source门。每项必须记录准确命中阶段/拒绝原因；提前gate/proof/cap或任意ValueError不能冒目标覆盖。新scope、预冻结profile/预算，不重放开发失败scope或循环重试。
>
> coder当前产品/98项和本次材料保持冻结，无新增开发或反复自测；完整B统一交负责人决定下一整批与后续静止检查点分支PR，不逐问题交接。原辅助临时close未证及所有旧UNKNOWN保留、不查询/kill/二close/补ACK退款，也不作为其他独立推进的强制前提。
>
> 本次B仅离线，真实facts/SDK/ADB/Native route/TCP/help/设备/Gradle/媒体均不执行，未批准签名/密钥/IPC或外部authority。原生产时间/字节/source/角色门不扩。**D1未通过、M0未启动**；用户恢复授权、主里程碑和全P0/技术许可边界保持。下方旧状态为原时点记录。
<!-- CURRENT_STATUS_CONTRACT03_INDEPENDENT_B:END -->

<!-- CURRENT_STATUS_CONTRACT03_SEMANTICS_A_ACCEPTED:BEGIN -->
> **2026-10-23 独立语义A已审：限定PASS。** [完整报告](tester/D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_REPORT_V1.0.md) SHA `a6f2f4fe2cf1e7d8553d27f428f79753251ab8653e7d579a4fab621f506d7ea2`；负责人核manifest `8208c09cd12d91c942a9ceadaffe17842ddc0911515b276ccd5c18877210c066`，408项/3877819B、bad0。固定17源`4881f181…5e93`上366语义/34纯参数静态检查全部通过，原45矩阵及17条件正例实际通过、零错误PASS。前置记录及小数状态的准确语义拒绝在本范围已证；argv/身份/根和提案的纯/静态验证不能代原Gate/collector或完整根链。
>
> **下一依赖不变**：coder继续已派SELFCHECK02，在独立新scope修正辅助驱动并交完整整批自测结果；当前A结束，tester保持证据冻结，不自动进入整包B或现场。负责人收到双方完整结果后统一安排下一完整批。原BLOCKED/辅助FAIL/临时close未证及旧UNKNOWN不改，旧对象不查询/干预，也不要求强制收尾后才能推进。
>
> **仍未执行**：原七角色/END/once/preStart13/collector与完整调用链在本次A均NOT_RUN；当前外部签发/签名/IPC方案未批准实施，真实facts/SDK/ADB/Native route/TCP/设备/Gradle/媒体均0。正式B尚未派，D1未通过/M0未启；用户恢复和集中开发测试、后续tester整批分支PR规范保持。下方旧状态仅作原时点快照。
<!-- CURRENT_STATUS_CONTRACT03_SEMANTICS_A_ACCEPTED:END -->

<!-- CURRENT_STATUS_CONTRACT03_SELFCHECK02:BEGIN -->
> **2026-10-23 最新安排：冻结修订已交、辅助驱动阻塞独立处理。** 负责人已审[CONTRACT03完整BLOCKED报告](coder/D1_GLOBAL_IDLE_CONTRACT03_FIX_BLOCKED_DELIVERY_V1.0.md)，SHA `8e4e5b6f26867465852eeeee914c590b06204a7c6c7722e2dd5ffc7022cc7dba`；核原manifest `55e8f1b6a9fc1ccd4111ad4c1a1ddf4324ffc60951892d8f54e8ba636bde3d81` 的98项/1245040B、bad0及ZIP99唯一成员。五项修订代码已实现，第1纯参数组PASS，第2自有Windows审计驱动误读参数而失败，后11组/346语义未运行；原工具返回与Popen内部临时资源逐项原close未证分列，保留UNKNOWN，不据退出补绿。
>
> **coder**按[SELFCHECK02新工作单](coder/D1_GLOBAL_IDLE_CONTRACT03_SELFCHECK02_CODER_REQUIREMENTS_V1.0.md)在独立新目录修正驱动/profile：原Popen构造前纯校验、Windows audit仅观察、三次有限原返回资格后在同一预存360s整批预算内一次补齐受影响自测。原98文件与17源/gate9保持冻结，原失败scope不续跑、不二close；不开发新签名/密钥/IPC设施。
>
> **tester**按[SEMANTICS_A独立要求](tester/D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_TESTER_REQUIREMENTS_V1.0.md)并行只测准确冻结admission语义及纯参数/静态边界，独立新输出、有限函数宿主、无Runner/Gate/claim/设备。这是另有明确授权的阶段A，不是正式整包B；完整结果集中交负责人，开发完整自测与A审阅后再决定集中修复或准确B。
>
> 原未知临时对象和所有旧链继续隔离，不查询/kill/二close/补ACK退款，也不作为其他独立工作的强制前提。当前无SDK/ADB/Native route/TCP/help/Gradle/媒体/新依赖或共享Git/index操作，不批准真实facts/外部签发或现场测试。用户恢复授权有效，历史暂停/N2只约束原范围。**D1未通过、M0未启动**；全部原FAIL/UNKNOWN/预算/once与下方历史状态保留。
<!-- CURRENT_STATUS_CONTRACT03_SELFCHECK02:END -->

<!-- CURRENT_STATUS_GLOBAL_IDLE_CONTRACT03_FIX:BEGIN -->
> **2026-10-23 最新正式安排：GLOBAL_IDLE_CONTRACT03_FIX 集中修复，离线推进。** 用户恢复开发授权有效。负责人已审[revision02 独立整包 B](tester/D1_GLOBAL_IDLE_CONTRACT02_REVISION02_INDEPENDENT_B_REPORT_V1.0.md)，报告 SHA-256 `f4d16721f662a714133b7b0368a9ea50dedfe3fb1b60f653949843997c00006f`；原 manifest `3f59fd68a69a47e9016299f5c199ce86299db0bca9b2a12da65468d76edc6348`，独立核验1003项/5843549B、bad0。整包 **FAIL**：五项集中缺陷为未识别前置进程记录被跳过、状态小数被按整数前缀接受、fixture argv[0]未准确受限、当前未来提案仍指旧包、Runner/Gate/Owner夹具根不一致。原45/45、98/98、17条件正例及正常原链限定通过保留；175项中的4次错误PASS与1次拒绝阶段断言失败不改写。
>
> **已派 coder 下一整批**：[独立开发要求](coder/D1_GLOBAL_IDLE_CONTRACT03_FIX_CODER_REQUIREMENTS_V1.0.md)。新目录集中修五项、准确未来提案和最小外部交接静态方案；先固定源/预算、有限自测并完整冻结。tester仅可整理[独立测试要求](tester/D1_GLOBAL_IDLE_CONTRACT03_FIX_TESTER_REQUIREMENTS_V1.0.md)与原失败oracle，完整新候选经负责人审核后才正式派整包B，不逐问题交接、不测浮动源。本块是协调工作单，不是现场执行许可。
>
> **真实平台事实**：最新已审LIVE03在原生路由与设备identity后，global_idle以`ENV_WAIT_FOREGROUND_APP_OCCUPIED`停止（后续离线确认解析及真实HOME/服务资格缺口），实际SDK2/7；未安装APK、未进入scopeAll或声画/媒体测试。新解析候选尚无实机采集。真实外部事实批准/同原Gate交接受proof10s/gate30s、事实至目标资格至多300s约束，当前NOT_RUN/NOT_PROVEN；合成fixture正例不代现场资格，不扩门或自签LIVE许可。
>
> **保全与推进**：所有旧冻结/FAIL/UNKNOWN/once/原账目保持；旧55065/001a、31884/session30010、ticket40119及其他旧未返链隔离，不查询/kill/二close/补ACK退款，也不作为本批独立开发前提。当前无SDK/ADB/TCP/设备/Gradle/新依赖或共享Git/index操作。用户要求tester后续按需整批分支/PR提交继续有效，由负责人在独立复审后安排准确静止检查点。**D1未通过、M0未启动**；主里程碑、Flutter/独立Kit/既定成熟框架许可及全P0保持。
>
> 下方所有旧“当前/暂停/已派/待执行”均为各自原时点、原scope快照，按最新正式派发及完整报告解释，不从历史复述生成新执行或覆盖用户已明确恢复。
<!-- CURRENT_STATUS_GLOBAL_IDLE_CONTRACT03_FIX:END -->

<!-- CURRENT_STATUS_OFFLINE_LIVE01:BEGIN -->
> **2026-10-23 现行已审结论：准确候选限定完整离线准入接受**。负责人已审原R01–R05、N06–N08、REVIEW03四目标及SUPPLEMENT02，接受当前冻结PRODUCTION_RUNNER01的限定完整离线准入：source-only seal `399d14206ebb025f868d7e85402241605b2d397c0d52bef99b2b7ec3944df6ce`，完整seal `ff7095e31dd287cb80a4df2889818a6fe595f8f9eb0cf68d6adfd43e2556adea`。SUPPLEMENT02在新scope核同原lease与两次OPEN_EXISTING probe的卷/file-id/device/最终路径一致，原唯一释放及自身原返回已证；负责人核75项bad0。此合并资格不改旧probe身份缺失、SUPPLEMENT01 BLOCKED或任何历史FAIL/UNKNOWN。
>
> **一次LIVE01已正式派发，结果尚未证**：负责人原turn `01a16697-6f30-74a2-987c-1be051feee67`已派tester D1_ANDROID02_LIVE01，在启动前唯一新scope/窄permit下按原4metadata+7SDK顺序执行。所有原预算不扩、并发1/retry0；busy、身份/锁未知、包存在或任一门异常即停，不卸载/清数据/重启server/设备或增查。本块只记录派发，不推定已生成许可、已启动、已执行或通过；实际状态以完整实机报告及原返回为准。文档来源快照不是第二次执行许可。
>
> **当前协作边界**：coder产品候选冻结，不并发构建/设备/SDK或Git/index操作；本批仅同步现行文档，不读取LIVE动态输出或查询旧对象。旧31884链、session30010、ticket40119与旧锁/UNKNOWN继续隔离保留，不查询/干预/补ACK，也不作为其他不受影响工作整体推进前提。完整实机报告回负责人后统一选择下一功能簇，当前不先改产品、声画/隔离/模型或跨M0，不绕过既定scopeAll前置门。
>
> **验收边界**：限定离线准入不等于LIVE现场空闲、设备/平台能力或D1通过；**D1未通过、M0未启动**。更早CURRENT_STATUS_ISOLATION01、REVIEW03的未证细项和其他旧快照按原时点保留，本当前块只登记负责人已审合并结论及一次LIVE派发，不回填历史。

| 准确原报告 | 原范围与保全 | SHA256 |
| --- | --- | --- |
| [原R01–R05](tester/D1_PRODUCTION_RUNNER01_PHASE_B_REVIEW_REPORT_V1.0.md) | 原5组有限PASS，误计量停止/7 NOT_RUN与父ticket40119 UNKNOWN保留 | `2319452c000c6b1ebcd03aa21373b5eb1b799850b4f72b6ae464fd51417d25d3` |
| [N06–N08补测](tester/D1_PRODUCTION_RUNNER01_REVIEW02_REPORT_V1.0.md) | 原3组有限PASS，旧N09 tester FAIL/原holder隔离保留 | `b5d06b2c99cd139c2d9e1087f3942ca484a62bdb34d1a5e7a3e32279af549d56` |
| [REVIEW03四目标](tester/D1_CANDIDATE_FOUR_TARGETS_REVIEW03_REPORT_V1.0.md) | 四组离线脚本PASS，原probe同文件身份NOT_PROVEN不回填 | `af200c52f7354bc796935df252cadd54ca4985b0b1dcdb980b132d1170f87c45` |
| [SUPPLEMENT02](tester/D1_LOCK_FILE_ID_SUPPLEMENT02_REPORT_V1.0.md) | 新scope原lease与两OPEN_EXISTING probe卷/file-id/device一致及原释放PASS，原SUPPLEMENT01 BLOCKED保留 | `efa45cd9034460485e94984601cc9717727b016f12937183bddf711c77497a2a` |

> [本批工作单](coder/D1_CURRENT_STATUS_OFFLINE_LIVE01_WORK_ORDER_V1.0.md) · [完整交付及派发来源](coder/D1_CURRENT_STATUS_OFFLINE_LIVE01_DELIVERY_V1.0.md)。本批无候选/测试/claim/设备/进程或工具session查询。
<!-- CURRENT_STATUS_OFFLINE_LIVE01:END -->


<!-- CURRENT_STATUS_ISOLATION01:BEGIN -->
> **2026-10-23 最新用户纠正：协调推进、旧链隔离**。用户原turn `01a16656-fcdf-7b90-bc49-188061de69dd`明确“不需要你强制收尾”，按coder/tester工作情况安排推进；[原话与来源](coder/D1_CURRENT_STATUS_ISOLATION01_USER_CORRECTION_SOURCE_V1.0.md)逐字保留。旧31884链、session30010、ticket40119及旧锁/UNKNOWN单独隔离，不查询、不干预、不补ACK。**旧链专项收尾不是项目继续或其他不受影响工作的强制前提**，当前不要求/执行强停；下方CURRENT_STATUS_RECONCILE01的过宽依赖按本更晚指令纠正，历史原文不改。
>
> **当前已派安排**：tester已正式进入SELF_DRIVER_VALIDATION01，独立新work、自有身份/预算，无native claim、不导入产品Python候选/不调用候选函数体，实体PS仅VerifyScopeOnly；完整结果待负责人审核，不由本块宣布通过。coder产品候选保持冻结，本批只作源码/报告只读隔离分析与现行文档同步，无新测试/claim/metadata/SDK/设备或共享Git/index操作。
>
> **下一依赖**：阶段1完整结果审核 + [ISOLATION_APPLICABILITY01分析](coder/D1_PRODUCTION_RUNNER01_ISOLATION_APPLICABILITY01_REPORT_V1.0.md) + 新驱动来源/预算/原返回资格 → 负责人选定另一个新work/新home/新scope的准确候选四目标范围。固定原源码的fixture锁按home派生，新home可真实验证同一局部协议；LIVE固定共享锁、ADB/设备等资源不因换home隔离，不能复制候选或改锁路径绕过。R11探针文件身份/不创建替代文件的证据限制及包hash资格变化须先审；纯R12准备无需native claim，完整N12仍依赖本批新N11记录。旧收尾单独处理，不成为这条推进链的总闸。
>
> **验收状态保持**：runner已实现，原R01–R05+N06–N08有限PASS，R09–R12未完整，未确认产品源码FAIL。D1未通过/M0未启；fixture/NoNative阶段不能代LIVE空闲/真实设备能力或完整独立B，不绕过scopeAll前置门推进真实功能。当前没有新增live批准或旧链处置许可。
>
> [本批工作单](coder/D1_CURRENT_STATUS_ISOLATION01_WORK_ORDER_V1.0.md) · [独立隔离报告](coder/D1_PRODUCTION_RUNNER01_ISOLATION_APPLICABILITY01_REPORT_V1.0.md) · [完整交付](coder/D1_CURRENT_STATUS_ISOLATION01_DELIVERY_V1.0.md)。所有更早状态、FAIL、UNKNOWN、预算、once和证据继续按原来源保留。
<!-- CURRENT_STATUS_ISOLATION01:END -->


<!-- CURRENT_STATUS_RECONCILE01:BEGIN -->
> **2026-10-23 现行状态（CURRENT_STATUS_RECONCILE01）**：PRODUCTION_RUNNER01的专用生产入口、自动物化与同原Owner交接已实现并冻结；独立准确`-I`七角色/END正常链已有限通过。当前接受原R01–R05及补测N06–N08有限PASS，R09–R12仍未完整验证；未确认新候选源码FAIL。**D1未通过、M0未启动**，不签完整独立B、设备READY或READY/COMMIT。
>
> **当前阻塞与原保管**：REVIEW02的N09自有PS函数宿主缺准确文件作用域，正确样本空路径失败；断言在计划原release之前，tester失败出口保留本批原holder。按冻结报告，原worker31884尚无原返回、parent/supervisor未终局；session30010只是工具会话标识，不当OS PID。本次不作新鲜运行状态查询，不读锁、不轮询/处置这些对象。旧ticket40119的父层终局UNKNOWN独立保留，已核下游返回不替它补ACK；各旧FAIL/UNKNOWN/预算/once/N2不改。
>
> **当前授权与可推进工作**：用户恢复开发仍有效，当前是具体测试驱动/收尾阻塞，不是全项目无限暂停。coder产品候选和开发四轮FAIL/证据缺失保持冻结，无产品修复、自检、构建或现场调用；本批只同步现行文档。tester在独立新目录完善未来完整驱动静态包（原身份、有限安全控制、已知FAIL同holder收尾及实体PS宿主），尚未动态验证，不启动新动态/设备。CLOSEOUT_DESIGN01只是待审静态方案；强停、新鲜绑定、条件后备、探针及可能的finally/ACK/内存证据损失，须用户准确专项批准。普通“继续开发”和一般设备授权不构成接受该损失，不复用旧N2。
>
> **后续依赖**：专项批准 → 仅在批准范围和身份条件成立时严格收尾，负责人审核真实结果（失配即停，UNKNOWN不转绿） → 完整新驱动静态冻结、另立新scope/预算验证 → R09–R12四目标集中补测 → 负责人审完整结果后另定准确现场范围。若缺批准或绑定/收尾未证，不越级启动动态；可独立推进已派静态工作。本轮runner真实live批准/metadata/SDK/5037/设备与产品平台仍未执行，不能绕过既定scopeAll前置门启动真实功能、呈现/音频/隔离、模型或Flutter。

| 准确完整来源 | 原状态与范围 | SHA256 |
| --- | --- | --- |
| [开发交付](coder/D1_ANDROID02_PRODUCTION_RUNNER01_DELIVERY_V1.0.md) | runner已实现并冻结；最终6组开发离线PASS，不代独立验收 | `3e654f113e9dcd2ac45c7d3e2d6d8bd557549e9b18be400c10ba0058da1eb601` |
| [原独立B](tester/D1_PRODUCTION_RUNNER01_PHASE_B_REVIEW_REPORT_V1.0.md) | R01–R05有限PASS／R06–R12原NOT_RUN；tester误将生成量36864B记作stdin，实际已核stdin6144B；父ticket40119终局UNKNOWN | `2319452c000c6b1ebcd03aa21373b5eb1b799850b4f72b6ae464fd51417d25d3` |
| [REVIEW02补测](tester/D1_PRODUCTION_RUNNER01_REVIEW02_REPORT_V1.0.md) | N06–N08新增有限PASS；N09 tester驱动FAIL／BLOCKED，N10–N12 NOT_RUN，原holder未返，余R09–R12未完整 | `b5d06b2c99cd139c2d9e1087f3942ca484a62bdb34d1a5e7a3e32279af549d56` |
| [CLOSEOUT_DESIGN01](tester/D1_PRODUCTION_RUNNER01_CLOSEOUT_DESIGN01_REPORT_V1.0.md) | 静态收尾方案及未来驱动修正设计，未动态验证、未授权或执行强停；需用户专项批准及身份条件成立 | `b1403cdd1d5b40e78c9d289d36f451cf54d68646c2464e1bb61ceaf77201499f` |

> 本次[文档工作单](coder/D1_CURRENT_STATUS_RECONCILE01_WORK_ORDER_V1.0.md)与[完整交付](coder/D1_CURRENT_STATUS_RECONCILE01_DELIVERY_V1.0.md)。以下所有早期“当前/暂停/待实现”原文均为其原时点快照，保留字节及适用scope；不覆盖本现行块，不生成新许可。本批不切共享Git分支或修改index。
<!-- CURRENT_STATUS_RECONCILE01:END -->


> **2026-10-23 当前状态/下一准备范围**：负责人已审READY04独立B [报告](tester/D1_READY04_RUNTIME_BIND01_PHASE_B_REVIEW_REPORT_V1.0.md)，SHA da9104be7f6b5bf2d39b31142952d8aa6e4c08c467ce0c9d2b8708abe192ceb6；接受准确运行时绑定/来源拒绝/有限离线capture PASS，10组及五缺失目标在本次新scope通过。当前runtime来源阻塞已在新批有限解除，旧RESUME_REVIEW01 BLOCKED及旧FAIL/NOT_RUN/UNKNOWN不改；未来使用前仍须重核当前来源。真实设备/产品平台未执行，D1未通过、M0未启动，不签设备READY或READY/COMMIT。
>
> tester READY04_DEVICE_PREP01已完成准确生产计划/本地机械准备，但[报告](tester/D1_ANDROID02_READY04_DEVICE_PREP01_REPORT_V1.0.md)ec894031…11871e确认B01 route/claim原holder及B02初始pre-SDK原proof生产者/原返回/同批账本缺口，实际七角色NOT_RUN。负责人另派D1_ANDROID02_ENTRY_GATES01集中最小本地入口/薄适配；当前不设备/SDK/5037/构建/旧UNKNOWN操作。coder先收完[本次文档工作单](coder/D1_READY04_STATUS_NEXT01_WORK_ORDER_V1.0.md)和[完整建议交付](coder/D1_READY04_STATUS_NEXT01_DELIVERY_V1.0.md)，再独立进入该开发批；呈现/音频/隔离仅供scopeAll之后选择，不先改产品代码/扩模型或Flutter。当前运行时有限PASS不关闭现场能力门。
>
> 2026-10-23用户“继续推进开发”仍有效；下方早期“当前/最新/暂停”按其原时点和scope作历史快照保留，不复用旧once/停止或N2结算指令。主里程碑/技术基线不重排，候选冻结；提交和下一实际开发批由负责人统一安排，本窗口不切共享Git分支/索引/stage/commit/push。


> **2026-10-23 最新有效恢复与派发**：用户在负责人窗口明确“继续推进开发”（原用户turn 01a1657d-8c8e-7001-a462-7cbbca7ceaa0），历史全项目暂停已解除。本次仅派 coder `D1_READY03_RESUME_PREP01` 整理准确D1实机交接准备，以及 tester `D1_READY03_RESUME_REVIEW01` 在新目录补准确冻结READY03的五项NOT_RUN；当前无新确认源码缺陷，不改旧候选或先造READY04。D1仍未通过、M0未启动，主里程碑与技术决定不变。
>
> 本批开发要求见[准备工作单](coder/D1_READY03_RESUME_PREP01_CODER_REQUIREMENTS_V1.0.md)，完整交付见[交付说明](coder/D1_READY03_RESUME_PREP01_DELIVERY_V1.0.md)。本次coder不SDK/设备/ADB/Gradle/新构建，不改tester目录/共享cache，不操作旧UNKNOWN；tester完整结果由负责人审核后才另派集中修复或准确新实机范围。新scope/预算/现场门尚未签，本段不是设备activation；后续提交遵守GitHub整批分支/PR规则，不擅自操作共享索引。以下2026-10-21暂停表述和历史停止scope按原文保留，仅作当时快照，不推翻本条用户恢复，也不复用旧指令发新任务。


2026-10-21集中整理；当前PAUSED_WAITING_USER。D1未通过、M0未启动；本轮只改设计文档，不恢复coder/tester、补测、设备或自动跟进。

## 1. 当前范围与历史入口

当前技术决定按[当前设计基线](CURRENT_DESIGN_BASELINE_V1.0.md)；具体实现结果只按原候选和报告。最后READY03独立完整报告60776d11cfe73fff1cd0afc3ccd2d4dbbe90193c8744960bca78d76f8e0c2a65：源码修复可核，独立10组5通过/5 NOT_RUN，无完整B/READY。旧原UNKNOWN/历史FAIL/预算/once不重置，不补ACK退款，不处置旧进程。

历史C01–E系列、RESUME、fixture及capture派发全过程在[修改前协调文档归档](history/design/2026-10-21-consolidation/MILESTONE_COORDINATION_V1.0.md)，所有原报告仍位于docs/coder与docs/tester，均未改。归档只是证据索引，不从其中任何“继续/停止/当前任务”生成新派单。

## 2. 角色与暂停边界

负责人01a107c3-2bf9-7fa0-94a0-234258ca6774；coder01a107f2-678c-7ce3-adac-3c199241c221；tester01a1080d-8710-7b60-b4ab-f3e1554ba685，local。用户授权协调不等于暂停期间可以派发。当前双方已结束本批并暂停，整批报告完成，无自动跟进。

用户明确恢复后，负责人先读最新状态/完整报告再派准确范围；历史任务停止只限其原范围，但本次全项目暂停覆盖所有新增开发/测试。设备持续一般授权保留，不因权限重新索取重复确认；实际使用须准确新批/fresh空闲门，其他项目占用不操作/不轮询，无并发设备或Gradle/共享可变缓存。暂停期间不做占用查询。

## 3. 主阶段与独立工作单

| 阶段 | 当前状态 | 开发/测试工作单 |
| --- | --- | --- |
| D1 | 未通过；批后暂停，不把局部PASS升级 | 原D1与各冻结批报告，只读历史 |
| M0 | PLANNED_NOT_STARTED | [开发](milestones/M0_CODER_REQUIREMENTS_V1.0.md) / [测试](milestones/M0_TESTER_REQUIREMENTS_V1.0.md) |
| M1 | PLANNED_NOT_STARTED | [开发](milestones/M1_CODER_REQUIREMENTS_V1.0.md) / [测试](milestones/M1_TESTER_REQUIREMENTS_V1.0.md) |
| M2 | PLANNED_NOT_STARTED | [开发](milestones/M2_CODER_REQUIREMENTS_V1.0.md) / [测试](milestones/M2_TESTER_REQUIREMENTS_V1.0.md) |
| M3 | PLANNED_NOT_STARTED | [开发](milestones/M3_CODER_REQUIREMENTS_V1.0.md) / [测试](milestones/M3_TESTER_REQUIREMENTS_V1.0.md) |
| M4 | PLANNED_NOT_STARTED | [开发](milestones/M4_CODER_REQUIREMENTS_V1.0.md) / [测试](milestones/M4_TESTER_REQUIREMENTS_V1.0.md) |
| M5 | PLANNED_NOT_STARTED | [开发](milestones/M5_CODER_REQUIREMENTS_V1.0.md) / [测试](milestones/M5_TESTER_REQUIREMENTS_V1.0.md) |
| M6 | PLANNED_NOT_STARTED | [开发](milestones/M6_CODER_REQUIREMENTS_V1.0.md) / [测试](milestones/M6_TESTER_REQUIREMENTS_V1.0.md) |
| M7 | PLANNED_NOT_STARTED | [开发](milestones/M7_CODER_REQUIREMENTS_V1.0.md) / [测试](milestones/M7_TESTER_REQUIREMENTS_V1.0.md) |
| M8 | PLANNED_NOT_STARTED | [开发](milestones/M8_CODER_REQUIREMENTS_V1.0.md) / [测试](milestones/M8_TESTER_REQUIREMENTS_V1.0.md) |
| M9 | DEFERRED，原平台目标 | [开发](milestones/M9_CODER_REQUIREMENTS_V1.0.md) / [测试](milestones/M9_TESTER_REQUIREMENTS_V1.0.md) |
| M10 | PLANNED_NOT_STARTED | [开发](milestones/M10_CODER_REQUIREMENTS_V1.0.md) / [测试](milestones/M10_TESTER_REQUIREMENTS_V1.0.md) |

M0须同时含完整UI工作单：[开发](milestones/M0_APP_UI_CODER_REQUIREMENTS_V1.0.md)/[测试](milestones/M0_APP_UI_TESTER_REQUIREMENTS_V1.0.md)；只API/Fake不算M0完成。主表见[MILESTONES](MILESTONES_V1.0.md)。

## 4. 恢复后的完整交接规则

负责人实际一次选择1–3主阶段，向用户说明范围与理由；按[追踪总表](REQUIREMENT_ACCEPTANCE_TRACEABILITY_V1.0.md)拆子任务/用例和[指标表](METRIC_FREEZE_REGISTER_V1.0.md)数值，分别保存开发/测试要求。子任务不是逐个交测单位。

READY→CODING→SELF_CHECK→完整冻结CANDIDATE→整包TESTING→集中报告。缺陷统一FIX_BATCH→新候选→受影响整包回归，不逐问题往返；严重源安全/隐私/错误READY立即阻断。未完成/构建失败/证据不足不交半包反复验。候选期间不改浮动源码或偷偷换产物。

coder交需求矩阵/精确来源和hash/依赖模型清单/必要集中构建及自检/所有失败与未证/产物及预算原返回；tester独立审同候选，不照抄开发PASS，证据分静态/Fake/UI/真实媒体/原调用归还。用例结果PASS/FAIL/NOT_RUN/BLOCKED，覆盖完成与候选通过分开。

## 5. 构建、样本及授权

以完整功能簇自检冻结，必要基线/接口/原生绑定检查允许，禁止每控件频繁编译、无原因clean或复跑不变已通过任务。tester优先用交付产物，只有独立构建/证据不足/新风险才集中重建，记录准确来源。

样本test_media只读、不打包不上传；缺语料不假格式/质量PASS。输入只读、输出宿主临时Sink、READY≠COMMITTED。超时不自动杀进程/二次close/退款，原UNKNOWN只保留原事实。第三方权利/付费/不可逆发布和范围变更另按准确授权处理；本次文档不是执行授权。

## GitHub与tester按需提交

用户指定私人仓库bennyliaa/VideoKit。后续用户恢复后tester按需提交准确整批已审源码/文档/报告，严格区分PASS/FAIL/NOT_RUN，按[提交规则](GITHUB_SYNC_AND_TESTER_COMMIT_POLICY_V1.0.md)检查diff/分支/许可与排除项，默认整批PR审核，不force push或自动发布。本次仅版本同步，当前暂停不派tester新任务。
