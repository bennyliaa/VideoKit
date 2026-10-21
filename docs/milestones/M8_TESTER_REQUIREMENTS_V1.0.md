# M8 测试需求：Android Flutter App 全功能与手机平板适配

## 国际化详细设计对接（2026-10-21）

按[国际化详细设计](../INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)与[数据模型](../INTERNATIONALIZATION_DATA_MODEL_V1.0.md)，按I18N-01–15独立整包验收全正式App、四域/重启保存/系统手选、RTL长文大字读屏及真实任务不中断。资源/Fake/UI/媒体/模型证据分层，未准入扩展不装模型。

这是未来阶段测试要求，不是当前派发；主里程碑不变，集中整包开发测试规则保持，项目继续暂停。

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。旧SkinKit强制实接要求已移入历史归档，当前不执行。完整现行范围见 [Flutter Theme 与延后集成决定](../FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前项目暂停，D1未过/M0未启。


## M0 起交付批次规则（2026-10-20）

负责人每批选择 1–3 个完整里程碑并向用户汇报范围与理由；coder 整批开发、自测、冻结后统一交 tester，tester 整批测试并集中报告，缺陷集中回交修复及回归。阶段需求与验收分栏保留，禁止逐问题反复交接，不以合批冒充阶段通过。详见 [协调规则](../MILESTONE_COORDINATION_V1.0.md)。此规则覆盖下文单里程碑立即交测的冲突表述，当前 D1 及 M0 未启动状态不变。


## 最新阶段补充（2026-10-20）

M8 复用 M0 UI 及 M1–M6 的逐批真实接线，完成全功能真实用户流程、自有Flutter Theme、国际化、手机平板与发布隔离验收；不得把演示 UI 当完整产品完成，不另起一套 UI。 完整依据：[M0 UI 总要求](../M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md)。阶段仍须正式派发后实施。


版本：V1.0；日期：2026-10-05；阶段：M8；原始需求关联：2、6–11、20、22、25–27。

基线：[用户需求](../VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)；最新执行范围：[项目决定](../PROJECT_DECISIONS_AND_EXECUTION_V1.0.md)；统一交接：[协调规则](../MILESTONE_COORDINATION_V1.0.md)。

状态：测试准备；只有收到负责人确认的完整候选交接包才执行正式验收。M9当前不执行平台测试。可先阅读和整理用例，但不抢跑产品测试、不为准备重复构建。

## 接收条件

对应 [coder需求](M8_CODER_REQUIREMENTS_V1.0.md) 全范围完成矩阵、candidateId、产物hash、集中构建及自检证据、已知问题、样本清单和设备条件齐全。若资料或必要功能不完整，先报告拒收/阻断原因，而不是频繁测试半成品。

## 必须执行的测试

- TC-M8-01：本地视频/图片、最近/权限失效、状态恢复/导航全流程。

- TC-M8-02：编辑入口、片段拼接、手动/自动打码、纠正及新输出保存，不覆盖源。

- TC-M8-03：多画面UI、独立状态、唯一声音、离屏/锁定/低资源降级。

- TC-M8-04：Android12手机/平板横竖屏/分屏/窗口/安全区域/触摸与外接输入。

- TC-M8-05：中英、伪本地化、RTL、大字体、无障碍焦点与文案无遗漏。

- TC-M8-06：Flutter纹理性能/生命周期，频繁导航无泄漏，纯原生宿主不依赖Flutter。

- TC-M8-07：完整Kit关键回归与Release包隐私/许可；四平台代码未实现不宣称已支持。

## 执行和证据

使用测试需求→用例→实际环境/样本hash→预期→实际→证据映射。按PASS/FAIL/NOT_RUN/BLOCKED记录。缺样本/设备/模型权利/未冻结阈值不得记PASS；Fake结果不代替真实设备/引擎/效果，扩展名不代替格式探测。性能与取消阈值据正式决定执行，暂无数值则提交测量并标未冻结。

Android12手机/平板由负责人通知用户开启调试后测试；无设备阶段先做可执行契约和产物核查，真机项等待，不擅自标通过。样本只读，输出仅授权临时目标，不上传媒体，不改产品源码。

tester不重复coder已完成且candidate未变的构建；优先检查并使用其产物。需要验证独立构建/R8/发布包或证据不足时，可做必要集中构建，并避免与coder并发占用构建缓存/设备。报告全部发现后统一交回，修复候选做缺陷验证和受影响回归，只有新变更/失败/风险才扩大或重复测试。

## 报告与判定

报告保存docs/tester/M8_TEST_REPORT_<candidateId>.md，附case表、缺陷复现/严重度/预期实际/修复建议、日志或截图证据及环境。所有关键安全缺陷立即阻断，其余同批汇总；不因一次测试通过就自动派发后续开发。

退出条件：Android App全部计划功能一次性交付，手机/平板/多语言及Kit回归通过。

阶段全通过后负责人确认退出并派发下一阶段；未经关闭的关键NOT_RUN/BLOCKED不能用口头结论掩盖。

## 设计依据

- [VIDEOKIT_APP_ARCHITECTURE](../VIDEOKIT_APP_ARCHITECTURE_V1.0.md)
- [PLAYBACK_AND_IMAGE_DESIGN](../PLAYBACK_AND_IMAGE_DESIGN_V1.0.md)
- [EDIT_TIMELINE_AND_EXPORT_DESIGN](../EDIT_TIMELINE_AND_EXPORT_DESIGN_V1.0.md)
- [TEST_AND_ACCEPTANCE_PLAN](../TEST_AND_ACCEPTANCE_PLAN_V1.0.md)


## 集中设计整理对接（未来正式派发前冻结）

[INTERNATIONALIZATION_DETAILED_DESIGN](../INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)；[TEST_AND_ACCEPTANCE_PLAN](../TEST_AND_ACCEPTANCE_PLAN_V1.0.md)。

[追踪总表](../REQUIREMENT_ACCEPTANCE_TRACEABILITY_V1.0.md)逐条确认原文与正文/示例字段；[指标冻结表](../METRIC_FREEZE_REGISTER_V1.0.md)明确本阶段必需参数/证据/批准，缺值不能判相应正式PASS。开发要求负责模块/模型/失败原返自检；测试要求负责独立用例/实际与NOT_RUN分栏，组级PASS不代原子条款。维持1–3主阶段整包交测，不为本次补文档启动构建或测试。项目仍暂停。
