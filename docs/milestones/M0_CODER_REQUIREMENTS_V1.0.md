# M0 技术开发需求：工程骨架、公共 API、Fake 与 TestKit

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。旧SkinKit强制实接要求已移入历史归档，当前不执行。完整现行范围见 [Flutter Theme 与延后集成决定](../FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前项目暂停，D1未过/M0未启。


## M0 起交付批次规则（2026-10-20）

负责人每批选择 1–3 个完整里程碑并向用户汇报范围与理由；coder 整批开发、自测、冻结后统一交 tester，tester 整批测试并集中报告，缺陷集中回交修复及回归。阶段需求与验收分栏保留，禁止逐问题反复交接，不以合批冒充阶段通过。详见 [协调规则](../MILESTONE_COORDINATION_V1.0.md)。此规则覆盖下文单里程碑立即交测的冲突表述，当前 D1 及 M0 未启动状态不变。


## 最新阶段补充（2026-10-20）

原有全部范围保留，新增完整 UI 为 M0 必须退出项；必须同时执行 [M0 UI coder 工作单](M0_APP_UI_CODER_REQUIREMENTS_V1.0.md)，不能仅 API/Fake/TestKit 通过就判 M0 完成。 完整依据：[M0 UI 总要求](../M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md)。阶段仍须正式派发后实施。


版本：V1.0；日期：2026-10-05；阶段：M0；原始需求关联：13–19、23–26、28(VK-M0)。

基线：[用户需求](../VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)；最新执行范围：[项目决定](../PROJECT_DECISIONS_AND_EXECUTION_V1.0.md)；统一交接：[协调规则](../MILESTONE_COORDINATION_V1.0.md)。

状态：阶段规划，前置验收通过并由负责人派发后实施。下游文档由前阶段证据补充精确版本/阈值，任何P0变化必须记录，不能自行减项。

## 目标与完整开发范围

1. 依据 D1 结论冻结基础契约和错误模型；建立原文模块边界，API 不导入 Android UI、Browser、第三方引擎、数据库或 AI 模型类型。

2. 建立 Android API/core/testkit/sample-host；功能模块可有明确未实现占位，不得以占位宣称 P0 完成。本阶段同时建立完整正式Flutter App UI、自有VideoKit Theme、国际化和标注清晰的测试数据演示；SkinKit不接入。

3. 实现语义版本、能力协商、状态快照、命令结果、generation/requestId/sequence、幂等关闭、宿主回调和输出契约；未来主版本安全拒绝。

4. Fake 支持正常、短读、超时、断线、取消、重复命令、HostAction失败、状态保存失败、输出错误；实现可控时钟与资源报告，禁止 Fake 与真实接口分叉。

5. TestKit 建立可由 Fake/真实实现共同执行的契约；sample-host 不需要 NAS 或 Browser 数据表即可运行，支持创建独立会话和演示源/输出协议。

6. 配置 API/可选 AAR 的内部 group/namespace、固定依赖、校验与本地 Maven 消费；交付 Consumer R8/ProGuard 初版及 API 文档。

7. 提供 Browser 适配示例和契约 fixture，不修改 LocalVideosBrowser 实际工程。只有本地 fixture 通过，不得宣称 Browser 真实接入成功。

## 通用实施约束

Android12/API31+、手机与平板、多语言中英资源及RTL/大字体机制；App Flutter并含编辑/多画面。Kit全部P0保留，输入只读、输出仅授权临时Sink，凭据/宿主业务/路径不穿透。当前只开发Android，Apple/Windows仅设计兼容性分析。测试样本 `D:\\CodexProjects\\VideoKit\\test_media` 只读、不打包或上传。

负责人确定每批 1–3 个里程碑，整批全部内容完成并自测后再一次性交给tester，禁止按单按钮/小功能反复交接。coder阶段可自检和必要自动测试，这不算正式交接。按完整功能簇集中编译，尽量复用已有构建结果，不每改一个文件就编译；首次构建/依赖与接口变更/原生绑定、集成失败等必须及时检查，不能为了减少编译而长期累积不兼容代码。

只交付一个可辨识候选candidateId，列源码/构建配置/依赖版本、APK/AAR路径与SHA-256、构建与自检结果、范围完成矩阵、已知风险和环境缺口。无Git时用源码快照清单与hash标识，禁止声称有不存在的commit。tester验收期间冻结该候选；发现缺陷先汇总成修复批次，修复后统一新候选和针对性回归。紧急安全问题可立即阻断并修复。

coder写docs/coder/<ID>_DELIVERY_<candidateId>.md，tester报告写docs/tester/<ID>_TEST_REPORT_<candidateId>.md。源码由coder负责，tester仅写测试计划/报告/证据，未授权不得改产品源码；双方共用工作区，不并发占用Gradle或设备。需要真机调试由负责人通知用户，不绕过设备授权。

## 退出与交付条件

基础契约冻结，API/Fake/TestKit/sample-host 整包可构建，自包含契约通过；真实播放器/编辑器未实现项明确保留给后续阶段。

功能范围逐项DONE/NOT_DONE；实际自检采用PASS/FAIL/NOT_RUN/BLOCKED，不以已编译代替效果验证。没有资源的项列清阻断，不向tester交付假完成里程碑。

## 设计依据

- [PUBLIC_API_CONTRACT](../PUBLIC_API_CONTRACT_V1.0.md)
- [SYSTEM_ARCHITECTURE](../SYSTEM_ARCHITECTURE_V1.0.md)
- [LOCALVIDEOBROWSER_INTEGRATION](../LOCALVIDEOBROWSER_INTEGRATION_V1.0.md)
- [OPEN_SOURCE_AND_LICENSE_PLAN](../OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md)


## 集中设计整理对接（未来正式派发前冻结）

[API_DATA_CONTRACT](../API_DATA_CONTRACT_V1.0.md)；[NATIVE_BINDING_AND_MODULE_BOUNDARIES](../NATIVE_BINDING_AND_MODULE_BOUNDARIES_V1.0.md)。

[追踪总表](../REQUIREMENT_ACCEPTANCE_TRACEABILITY_V1.0.md)逐条确认原文与正文/示例字段；[指标冻结表](../METRIC_FREEZE_REGISTER_V1.0.md)明确本阶段必需参数/证据/批准，缺值不能判相应正式PASS。开发要求负责模块/模型/失败原返自检；测试要求负责独立用例/实际与NOT_RUN分栏，组级PASS不代原子条款。维持1–3主阶段整包交测，不为本次补文档启动构建或测试。项目仍暂停。
