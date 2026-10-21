# M3 技术开发需求：多实例资源预算与唯一音频

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。旧SkinKit强制实接要求已移入历史归档，当前不执行。完整现行范围见 [Flutter Theme 与延后集成决定](../FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前项目暂停，D1未过/M0未启。


## M0 起交付批次规则（2026-10-20）

负责人每批选择 1–3 个完整里程碑并向用户汇报范围与理由；coder 整批开发、自测、冻结后统一交 tester，tester 整批测试并集中报告，缺陷集中回交修复及回归。阶段需求与验收分栏保留，禁止逐问题反复交接，不以合批冒充阶段通过。详见 [协调规则](../MILESTONE_COORDINATION_V1.0.md)。此规则覆盖下文单里程碑立即交测的冲突表述，当前 D1 及 M0 未启动状态不变。


## 最新阶段补充（2026-10-20）

复用 M0 已建 UI、SkinKit 与状态接口，将本阶段真实功能接回对应页面，保留 DEMO/REAL/UNSUPPORTED 来源区分；真实模式未实现项禁用并说明，不静默回落模拟成功。集中冻结后同时验收本阶段契约、真实功能和 UI 回归。 完整依据：[M0 UI 总要求](../M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md)。阶段仍须正式派发后实施。


版本：V1.0；日期：2026-10-05；阶段：M3；原始需求关联：8、16、19.4、21、26.4。

基线：[用户需求](../VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)；最新执行范围：[项目决定](../PROJECT_DECISIONS_AND_EXECUTION_V1.0.md)；统一交接：[协调规则](../MILESTONE_COORDINATION_V1.0.md)。

状态：阶段规划，前置验收通过并由负责人派发后实施。下游文档由前阶段证据补充精确版本/阈值，任何P0变化必须记录，不能自行减项。

## 目标与完整开发范围

1. 实现宿主范围资源管理器预留/创建/回收，视频会话硬上限12，建议并发依据实际媒体、设备、热与失败记录。

2. 实现1/4/9/12独立槽演示和视频/静态/动态图混排；手机默认4、平板默认9，资源不足由宿主减活跃数/占位，不承诺全设备12活跃硬解。

3. 完成音频 epoch 仲裁、先静音后授权、声音槽释放后全静音；不得由每个会话各自抢音频焦点。

4. 完成可见/部分可见/离屏/后台/锁定策略，状态恢复、共享池引用计数、单槽错误与故障隔离。

5. 完成资源和内存/热风险报告及有界失败退避，禁止循环创建解码器直到崩溃。

## 通用实施约束

Android12/API31+、手机与平板、多语言中英资源及RTL/大字体机制；App Flutter并含编辑/多画面。Kit全部P0保留，输入只读、输出仅授权临时Sink，凭据/宿主业务/路径不穿透。当前只开发Android，Apple/Windows仅设计兼容性分析。测试样本 `D:\\CodexProjects\\VideoKit\\test_media` 只读、不打包或上传。

负责人确定每批 1–3 个里程碑，整批全部内容完成并自测后再一次性交给tester，禁止按单按钮/小功能反复交接。coder阶段可自检和必要自动测试，这不算正式交接。按完整功能簇集中编译，尽量复用已有构建结果，不每改一个文件就编译；首次构建/依赖与接口变更/原生绑定、集成失败等必须及时检查，不能为了减少编译而长期累积不兼容代码。

只交付一个可辨识候选candidateId，列源码/构建配置/依赖版本、APK/AAR路径与SHA-256、构建与自检结果、范围完成矩阵、已知风险和环境缺口。无Git时用源码快照清单与hash标识，禁止声称有不存在的commit。tester验收期间冻结该候选；发现缺陷先汇总成修复批次，修复后统一新候选和针对性回归。紧急安全问题可立即阻断并修复。

coder写docs/coder/<ID>_DELIVERY_<candidateId>.md，tester报告写docs/tester/<ID>_TEST_REPORT_<candidateId>.md。源码由coder负责，tester仅写测试计划/报告/证据，未授权不得改产品源码；双方共用工作区，不并发占用Gradle或设备。需要真机调试由负责人通知用户，不绕过设备授权。

## 退出与交付条件

多实例、唯一音频、稳定降级和资源释放完整通过，设备能力报告诚实，单槽失败无全局清理。

功能范围逐项DONE/NOT_DONE；实际自检采用PASS/FAIL/NOT_RUN/BLOCKED，不以已编译代替效果验证。没有资源的项列清阻断，不向tester交付假完成里程碑。

## 设计依据

- [SYSTEM_ARCHITECTURE](../SYSTEM_ARCHITECTURE_V1.0.md)
- [LOCALVIDEOBROWSER_INTEGRATION](../LOCALVIDEOBROWSER_INTEGRATION_V1.0.md)
- [PLAYBACK_AND_IMAGE_DESIGN](../PLAYBACK_AND_IMAGE_DESIGN_V1.0.md)


## 集中设计整理对接（未来正式派发前冻结）

[RESOURCE_AND_ISOLATION_DESIGN](../RESOURCE_AND_ISOLATION_DESIGN_V1.0.md)。

[追踪总表](../REQUIREMENT_ACCEPTANCE_TRACEABILITY_V1.0.md)逐条确认原文与正文/示例字段；[指标冻结表](../METRIC_FREEZE_REGISTER_V1.0.md)明确本阶段必需参数/证据/批准，缺值不能判相应正式PASS。开发要求负责模块/模型/失败原返自检；测试要求负责独立用例/实际与NOT_RUN分栏，组级PASS不代原子条款。维持1–3主阶段整包交测，不为本次补文档启动构建或测试。项目仍暂停。
