# M8 技术开发需求：Android Flutter App 全功能与手机平板适配

## 国际化详细设计对接（2026-10-21）

按[国际化详细设计](../INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)与[数据模型](../INTERNATIONALIZATION_DATA_MODEL_V1.0.md)，全真实App接回后补齐资源/四域设置与切换不中断媒体编辑导出，保持无硬编码/裸异常。模型语言按已准入扩展范围，不由M8自动扩围。

这是未来阶段开发要求，不是当前派发；主里程碑不变，集中整包开发测试规则保持，项目继续暂停。

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。旧SkinKit强制实接要求已移入历史归档，当前不执行。完整现行范围见 [Flutter Theme 与延后集成决定](../FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前项目暂停，D1未过/M0未启。


## M0 起交付批次规则（2026-10-20）

负责人每批选择 1–3 个完整里程碑并向用户汇报范围与理由；coder 整批开发、自测、冻结后统一交 tester，tester 整批测试并集中报告，缺陷集中回交修复及回归。阶段需求与验收分栏保留，禁止逐问题反复交接，不以合批冒充阶段通过。详见 [协调规则](../MILESTONE_COORDINATION_V1.0.md)。此规则覆盖下文单里程碑立即交测的冲突表述，当前 D1 及 M0 未启动状态不变。


## 最新阶段补充（2026-10-20）

M8 复用 M0 UI 及 M1–M6 的逐批真实接线，完成全功能真实用户流程、自有Flutter Theme、国际化、手机平板与发布隔离验收；不得把演示 UI 当完整产品完成，不另起一套 UI。 完整依据：[M0 UI 总要求](../M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md)。阶段仍须正式派发后实施。


版本：V1.0；日期：2026-10-05；阶段：M8；原始需求关联：2、6–11、20、22、25–27。

基线：[用户需求](../VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)；最新执行范围：[项目决定](../PROJECT_DECISIONS_AND_EXECUTION_V1.0.md)；统一交接：[协调规则](../MILESTONE_COORDINATION_V1.0.md)。

状态：阶段规划，前置验收通过并由负责人派发后实施。下游文档由前阶段证据补充精确版本/阈值，任何P0变化必须记录，不能自行减项。

## 目标与完整开发范围

1. 复用 M0 已建正式 Flutter Android App UI，完成真实功能集成：系统本地文件选择、最近文件、偏好、设置、许可证页；不依赖Browser业务和真实NAS。

2. 接入相同原生SDK，播放器、静态/动态图、编辑入口、时间线/打码/自动跟踪/安全导出、多画面UI全部完成后整包交付。

3. 实现手机/平板、自适应窗口、横竖屏、分屏、安全区域、触摸/鼠标/键盘、字体100/130/200%；按窗口空间非仅设备标签切布局。

4. 统一ARB/国际化资源，中英文、长文本、复数/时间格式、RTL、内容描述与焦点顺序；无硬编码用户文本。

5. 视频帧走纹理/平台显示目标，不经Dart逐帧拷贝；统一状态事件及独立会话，输出提交由App宿主层处理。

6. 保留纯原生宿主SDK可用性和Compose/View可选交付，Flutter不成为Kit运行前提。

## 通用实施约束

Android12/API31+、手机与平板、多语言中英资源及RTL/大字体机制；App Flutter并含编辑/多画面。Kit全部P0保留，输入只读、输出仅授权临时Sink，凭据/宿主业务/路径不穿透。当前只开发Android，Apple/Windows仅设计兼容性分析。测试样本 `D:\\CodexProjects\\VideoKit\\test_media` 只读、不打包或上传。

负责人确定每批 1–3 个里程碑，整批全部内容完成并自测后再一次性交给tester，禁止按单按钮/小功能反复交接。coder阶段可自检和必要自动测试，这不算正式交接。按完整功能簇集中编译，尽量复用已有构建结果，不每改一个文件就编译；首次构建/依赖与接口变更/原生绑定、集成失败等必须及时检查，不能为了减少编译而长期累积不兼容代码。

只交付一个可辨识候选candidateId，列源码/构建配置/依赖版本、APK/AAR路径与SHA-256、构建与自检结果、范围完成矩阵、已知风险和环境缺口。无Git时用源码快照清单与hash标识，禁止声称有不存在的commit。tester验收期间冻结该候选；发现缺陷先汇总成修复批次，修复后统一新候选和针对性回归。紧急安全问题可立即阻断并修复。

coder写docs/coder/<ID>_DELIVERY_<candidateId>.md，tester报告写docs/tester/<ID>_TEST_REPORT_<candidateId>.md。源码由coder负责，tester仅写测试计划/报告/证据，未授权不得改产品源码；双方共用工作区，不并发占用Gradle或设备。需要真机调试由负责人通知用户，不绕过设备授权。

## 退出与交付条件

Android App全部计划功能一次性交付，手机/平板/多语言及Kit回归通过。

功能范围逐项DONE/NOT_DONE；实际自检采用PASS/FAIL/NOT_RUN/BLOCKED，不以已编译代替效果验证。没有资源的项列清阻断，不向tester交付假完成里程碑。

## 设计依据

- [VIDEOKIT_APP_ARCHITECTURE](../VIDEOKIT_APP_ARCHITECTURE_V1.0.md)
- [PLAYBACK_AND_IMAGE_DESIGN](../PLAYBACK_AND_IMAGE_DESIGN_V1.0.md)
- [EDIT_TIMELINE_AND_EXPORT_DESIGN](../EDIT_TIMELINE_AND_EXPORT_DESIGN_V1.0.md)
- [TEST_AND_ACCEPTANCE_PLAN](../TEST_AND_ACCEPTANCE_PLAN_V1.0.md)


## 集中设计整理对接（未来正式派发前冻结）

[INTERNATIONALIZATION_DETAILED_DESIGN](../INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)；[TEST_AND_ACCEPTANCE_PLAN](../TEST_AND_ACCEPTANCE_PLAN_V1.0.md)。

[追踪总表](../REQUIREMENT_ACCEPTANCE_TRACEABILITY_V1.0.md)逐条确认原文与正文/示例字段；[指标冻结表](../METRIC_FREEZE_REGISTER_V1.0.md)明确本阶段必需参数/证据/批准，缺值不能判相应正式PASS。开发要求负责模块/模型/失败原返自检；测试要求负责独立用例/实际与NOT_RUN分栏，组级PASS不代原子条款。维持1–3主阶段整包交测，不为本次补文档启动构建或测试。项目仍暂停。
