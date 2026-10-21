# CAPTURE_READY03_FIX 开发要求 V1.0

2026-10-21 正式新批 D1_ANDROID02_CAPTURE_READY03_FIX。完整独立B docs/tester/D1_ANDROID02_CAPTURE_READY02_FIX_PHASE_B_REVIEW_REPORT_V1.0.md，13904B/cffd1476883fcf9a6ebfa924888d16e74c1a0c8633dcedf5b48c8848d36b66bb，177证据manifest ed9c3f53c28a03d3a15eabc15de08159efd7e2b1260df7f84f850bd09f6234e2。两源码P2与缺失验证集中一批；旧核心delta/outer pending门已有限闭合，产品五项有限关闭不重开。

CR2-B01：固定同源request正文ReadJsonExact真实读取逻辑成本补入control，与request/admission写、admission读取及原console base/outer delta分别列出并防重复计费；首role无前驱仍必须计request读。不扩为所有物理源码/hash I/O审计，不自造不同计量口径。CR2-B02：同一共享proof deadline覆盖原writer之后必要events/digest/next/records/成功交接尾段直到本角色返回/END的最后受控观察点，及时原writer不等尾段及时，迟返sticky不放后继；不得下一role重建proof_start掩盖前次超窗。明确受控最后观察与不可自证解释器返回尾段边界，不要求无限自证明。

新目录docs/coder/d1android02-capture-ready03-fix，原候选/报告/证据及产品不改；最小修复既有owner/入口，不新dispatcher/诊断/release。SDK/设备/ADB/5037/占用/Gradle/JVM/媒体/共享cache/旧UNKNOWN操作0，PREPARATION_ONLY仍首SDK前拒，独立B后才另派准确设备范围。七角色/原产品pins/7op/并发1/无retry及原分组预算均不扩。仅固定采集host/Python producer有限本地集≤30秒、串行1、文本4MiB、载荷64KiB。未知原返回停新增准入保管原引用，不kill/interrupt/取消/二次close/未知重试。

本批集中补齐独立缺失目标：成功schema严格类型/必需字段/非负/等界/超界/firstFailure null与三类delta拒绝，以及两新修复。尾段测试应设计明确可达的受控点/单调时序，先保证writer自然及时返回，再在必要digest/交接尾段跨同一deadline，不能用之前正常proof timeout冒尾段复现；不靠不稳定sleep竞争或修改冻结候选状态冒生产路径。若无法动态证成如实分层静态/未运行/测试失败，不强行标绿。先在集内安排所有必需正常/负例，预算到期或断言失败停追加，报告完整覆盖及未覆盖，不延窗或重领旧集。保留正常七步、busy实际capture、stdin/pending-final、超量部分保存、outer/proof迟返保管核心回归。

集中实现及自检，保存最终源与所有中间失败、最小diff、原预算/返回证据、清单ZIP完整冻结后主动报告负责人，再正式交tester。
D1未过/M0未启，真实平台效果仍NOT_RUN。
