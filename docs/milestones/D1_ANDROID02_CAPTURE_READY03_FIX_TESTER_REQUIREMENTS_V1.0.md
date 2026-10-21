# CAPTURE_READY03_FIX 测试要求 V1.0

2026-10-21 正式新批 D1_ANDROID02_CAPTURE_READY03_FIX。完整独立B docs/tester/D1_ANDROID02_CAPTURE_READY02_FIX_PHASE_B_REVIEW_REPORT_V1.0.md，13904B/cffd1476883fcf9a6ebfa924888d16e74c1a0c8633dcedf5b48c8848d36b66bb，177证据manifest ed9c3f53c28a03d3a15eabc15de08159efd7e2b1260df7f84f850bd09f6234e2。两源码P2与缺失验证集中一批；旧核心delta/outer pending门已有限闭合，产品五项有限关闭不重开。

CR2-B01：固定同源request正文ReadJsonExact真实读取逻辑成本补入control，与request/admission写、admission读取及原console base/outer delta分别列出并防重复计费；首role无前驱仍必须计request读。不扩为所有物理源码/hash I/O审计，不自造不同计量口径。CR2-B02：同一共享proof deadline覆盖原writer之后必要events/digest/next/records/成功交接尾段直到本角色返回/END的最后受控观察点，及时原writer不等尾段及时，迟返sticky不放后继；不得下一role重建proof_start掩盖前次超窗。明确受控最后观察与不可自证解释器返回尾段边界，不要求无限自证明。

新目录docs/coder/d1android02-capture-ready03-fix，原候选/报告/证据及产品不改；最小修复既有owner/入口，不新dispatcher/诊断/release。SDK/设备/ADB/5037/占用/Gradle/JVM/媒体/共享cache/旧UNKNOWN操作0，PREPARATION_ONLY仍首SDK前拒，独立B后才另派准确设备范围。七角色/原产品pins/7op/并发1/无retry及原分组预算均不扩。仅固定采集host/Python producer有限本地集≤30秒、串行1、文本4MiB、载荷64KiB。未知原返回停新增准入保管原引用，不kill/interrupt/取消/二次close/未知重试。

本批集中补齐独立缺失目标：成功schema严格类型/必需字段/非负/等界/超界/firstFailure null与三类delta拒绝，以及两新修复。尾段测试应设计明确可达的受控点/单调时序，先保证writer自然及时返回，再在必要digest/交接尾段跨同一deadline，不能用之前正常proof timeout冒尾段复现；不靠不稳定sleep竞争或修改冻结候选状态冒生产路径。若无法动态证成如实分层静态/未运行/测试失败，不强行标绿。先在集内安排所有必需正常/负例，预算到期或断言失败停追加，报告完整覆盖及未覆盖，不延窗或重领旧集。保留正常七步、busy实际capture、stdin/pending-final、超量部分保存、outer/proof迟返保管核心回归。

当前保全READY02完整B与动态未完成事实，等待新整包冻结后负责人正式交B。不读浮动修复源。独立整包集中报告两项、旧修复回归与全部未覆盖目标，不自动activation。
D1未过/M0未启，真实平台效果仍NOT_RUN。

## 当前批最后一次正式整包B与批后暂停

2026-10-21，已核开发报告10348B/SHA301a56c1d341e9d0ca1d6b9d256f9b3b2a4993222ef24e784d414805fe296db3；seal e8750063bec93dec4dcad090b3dabab637816bcb6dea8d57f98302fdf2356b11 的225文件全size/hash、ZIP bf53714ace7473a2dcb60005b7e906ee60692acb1f64a05b75d1b6dc8cf6b69f 及226唯一成员一致。现在只正式交本候选一次完整独立离线B，来源docs/coder/d1android02-capture-ready03-fix及完整DELIVERY报告。逐ZIP内容由tester独立核。

集中核request正文同原ReadJsonExact实际raw.Length/calls计量与写/admission读独立防重，首步799+582及全七步；原共享proof_start覆盖writer之后必要events/digest/交接/records直到最后受控观察，后继及END及时writer后迟尾段必须sticky。新fixture绝对单调deadline门与真实生产路径差异需审，不以仅测试门命中代生产控制流。解释器return尾部不可自证边界保持，不扩无限证明。

本次独立集先安排此前NOT_RUN严格schema及三delta拒绝，再补两项修复和必要正常/忙碌/预算/原返回回归；各项如实静态/动态/未证分层。开发22.891秒9组不代独立验证。沿原≤30秒/串行1/文本4MiB/载荷64KiB；仅tester新输出目录受审采集host/固定Python producer，无SDK设备/5037/Gradle/JVM/共享cache/旧UNKNOWN，不改冻结，不强停或未知重试。

遵用户最新：完成这一轮整包测试及集中报告即暂停，所有缺陷/FAIL/NOT_RUN如实保留；不自动追加修复回归、新批或设备activation，等待用户通知。报告主动交负责人后停止后继。
