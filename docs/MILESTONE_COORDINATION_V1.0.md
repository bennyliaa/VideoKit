# 里程碑开发与测试协调规则

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
