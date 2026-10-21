# M9 测试需求：Apple/Windows 后续平台目标（当前不启动）

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。旧SkinKit强制实接要求已移入历史归档，当前不执行。完整现行范围见 [Flutter Theme 与延后集成决定](../FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前项目暂停，D1未过/M0未启。


## M0 起交付批次规则（2026-10-20）

负责人每批选择 1–3 个完整里程碑并向用户汇报范围与理由；coder 整批开发、自测、冻结后统一交 tester，tester 整批测试并集中报告，缺陷集中回交修复及回归。阶段需求与验收分栏保留，禁止逐问题反复交接，不以合批冒充阶段通过。详见 [协调规则](../MILESTONE_COORDINATION_V1.0.md)。此规则覆盖下文单里程碑立即交测的冲突表述，当前 D1 及 M0 未启动状态不变。


版本：V1.0；日期：2026-10-05；阶段：M9；原始需求关联：用户四平台补充；20、23、25–27。

基线：[用户需求](../VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)；最新执行范围：[项目决定](../PROJECT_DECISIONS_AND_EXECUTION_V1.0.md)；统一交接：[协调规则](../MILESTONE_COORDINATION_V1.0.md)。

状态：测试准备；只有收到负责人确认的完整候选交接包才执行正式验收。M9当前不执行平台测试。可先阅读和整理用例，但不抢跑产品测试、不为准备重复构建。

## 接收条件

对应 [coder需求](M9_CODER_REQUIREMENTS_V1.0.md) 全范围完成矩阵、candidateId、产物hash、集中构建及自检证据、已知问题、样本清单和设备条件齐全。若资料或必要功能不完整，先报告拒收/阻断原因，而不是频繁测试半成品。

## 必须执行的测试

- TC-M9-01：当前仅检查跨平台边界设计，所有未实现真机能力标NOT_RUN，不阻断当前Android阶段。

- TC-M9-02：后续启动后公共契约与黄金变换/工程迁移矩阵跨平台一致。

- TC-M9-03：各平台全部P0真实媒体、随机源、Sink与质量验证。

- TC-M9-04：手机/平板/桌面窗口、输入方式、中英/RTL/无障碍。

- TC-M9-05：平台文件权限、后台/锁定、故障隔离、资源和设备阈值。

- TC-M9-06：各SDK/App独立构建、签名、依赖/模型权利与商店提交材料。

## 执行和证据

使用测试需求→用例→实际环境/样本hash→预期→实际→证据映射。按PASS/FAIL/NOT_RUN/BLOCKED记录。缺样本/设备/模型权利/未冻结阈值不得记PASS；Fake结果不代替真实设备/引擎/效果，扩展名不代替格式探测。性能与取消阈值据正式决定执行，暂无数值则提交测量并标未冻结。

Android12手机/平板由负责人通知用户开启调试后测试；无设备阶段先做可执行契约和产物核查，真机项等待，不擅自标通过。样本只读，输出仅授权临时目标，不上传媒体，不改产品源码。

tester不重复coder已完成且candidate未变的构建；优先检查并使用其产物。需要验证独立构建/R8/发布包或证据不足时，可做必要集中构建，并避免与coder并发占用构建缓存/设备。报告全部发现后统一交回，修复候选做缺陷验证和受影响回归，只有新变更/失败/风险才扩大或重复测试。

## 报告与判定

报告保存docs/tester/M9_TEST_REPORT_<candidateId>.md，附case表、缺陷复现/严重度/预期实际/修复建议、日志或截图证据及环境。所有关键安全缺陷立即阻断，其余同批汇总；不因一次测试通过就自动派发后续开发。

退出条件：本阶段当前DEFERRED，不派发实现或真机任务；以后平台范围启动后，必须完成全套证据才可声称四平台正式支持。

阶段全通过后负责人确认退出并派发下一阶段；未经关闭的关键NOT_RUN/BLOCKED不能用口头结论掩盖。

## 设计依据

- [SYSTEM_ARCHITECTURE](../SYSTEM_ARCHITECTURE_V1.0.md)
- [VIDEOKIT_APP_ARCHITECTURE](../VIDEOKIT_APP_ARCHITECTURE_V1.0.md)
- [TEST_AND_ACCEPTANCE_PLAN](../TEST_AND_ACCEPTANCE_PLAN_V1.0.md)
- [OPEN_SOURCE_AND_LICENSE_PLAN](../OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md)


## 集中设计整理对接（未来正式派发前冻结）

[NATIVE_BINDING_AND_MODULE_BOUNDARIES](../NATIVE_BINDING_AND_MODULE_BOUNDARIES_V1.0.md)；[RESOURCE_AND_ISOLATION_DESIGN](../RESOURCE_AND_ISOLATION_DESIGN_V1.0.md)。

[追踪总表](../REQUIREMENT_ACCEPTANCE_TRACEABILITY_V1.0.md)逐条确认原文与正文/示例字段；[指标冻结表](../METRIC_FREEZE_REGISTER_V1.0.md)明确本阶段必需参数/证据/批准，缺值不能判相应正式PASS。开发要求负责模块/模型/失败原返自检；测试要求负责独立用例/实际与NOT_RUN分栏，组级PASS不代原子条款。维持1–3主阶段整包交测，不为本次补文档启动构建或测试。项目仍暂停。
