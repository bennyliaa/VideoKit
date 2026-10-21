# VideoKit 当前设计基线与文档权威

V1.0；2026-10-21；当前设计基线，非实现/性能/许可验收证明。项目PAUSED_WAITING_USER，D1未过/M0未启；仅文档更新，不派开发、补测、设备或恢复自动跟进。

## 1. 当前决定

- 正式App为Flutter+自有VideoKit Theme，M0先完整UI/明确演示数据，M1–M6逐批接真实功能，M8全真实产品验收；SkinKit待正式Flutter支持另评估，当前无原生桥接/实接门。libmpv退出正式选型/对照，Android Media3确定，Apple/Windows按原M9安排，不提前实装。
- Kit独立原生发行，纯播放不强制Flutter、主题、模型或编辑依赖。Core不持有宿主业务/凭据。ASR/Translation分别为EXT-ASR/EXT-TR，whisper.cpp优先验证，llama.cpp+适用模型评估，可替换且不自动加D1/M1发布门。
- 四类语言独立，界面首轮en/zh-Hans；UI切换不重建会话。输入只读，导出临时Sink、READY≠业务COMMITTED；原P0/安全门不降级。
- 主阶段D0/D1/M0–M10不重排，不新增主阶段。子任务只细化既有范围，1–3主阶段成批开发自测冻结/整包独立测试；当前暂停优先，不将历史继续指令当新派单。

## 2. 文档优先级与模型归属

最新用户明确指令→当前决定/主里程碑→专项详细设计→公共接口与统一字段字典→各阶段开发/测试要求。发现冲突必须集中记录并同步，不让coder任选正文。当前字段冲突按[统一接口与数据契约](API_DATA_CONTRACT_V1.0.md)及对应模型修正；模型设计通过不代表ABI/阈值已冻结。

[播放设计](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)、[播放模型](PLAYBACK_DATA_MODEL_V1.0.md)、[国际化设计](INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)、[国际化模型](INTERNATIONALIZATION_DATA_MODEL_V1.0.md)、[工程跟踪输出模型](EDIT_TRACKING_EXPORT_DATA_MODEL_V1.0.md)、[图片设计](IMAGE_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)、[输出协议](OUTPUT_LIFECYCLE_AND_RECOVERY_V1.0.md)、[资源隔离](RESOURCE_AND_ISOLATION_DESIGN_V1.0.md)、[原生绑定边界](NATIVE_BINDING_AND_MODULE_BOUNDARIES_V1.0.md)共同构成当前细化基线。

原始用户需求全文、docs/coder与docs/tester冻结证据/报告、原账本once/预算/FAIL/UNKNOWN不得为文档一致性而改写。旧设计原文归档在[历史清单](history/design/2026-10-21-consolidation/manifest.json)，只是历史引用，不再是执行工作单。

## 3. 状态归属

截至当前暂停快照：最后READY03独立报告60776d11cfe73fff1cd0afc3ccd2d4dbbe90193c8744960bca78d76f8e0c2a65记录源码修复核实，独立10组5通过/5 NOT_RUN，不签完整B或设备READY。既有产品局部PASS及历史FAIL/UNKNOWN原样；不能写全项目全部未测试或已通过。此处是历史状态摘要，不重新判断证据，不迁移旧调用。

新设计验收全部PLANNED_NOT_RUN，结果报告只PASS/FAIL/NOT_RUN/BLOCKED，设计/实现/验收三状态独立。实现进度与冻结版本以原候选来源清单为证；设计中的待冻结不得覆盖已有锁定产物，也不得从Spike固定依赖推断正式产品已准入。

## 4. 冻结与恢复

[追踪总表](REQUIREMENT_ACCEPTANCE_TRACEABILITY_V1.0.md)登记原需求→设计→子任务→测试→证据，[指标冻结表](METRIC_FREEZE_REGISTER_V1.0.md)登记责任/阶段/测量/批准。不因本文补齐设计启动验证。恢复必须用户明确通知，然后负责人审当前剩余项再派准确整批；自动跟进保持停止。
