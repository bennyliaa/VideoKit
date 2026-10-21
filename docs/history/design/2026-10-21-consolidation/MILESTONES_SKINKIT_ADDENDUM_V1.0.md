# 里程碑 UI 与 SkinKit 补充 V1.0

## 2026-10-21 国际化详细设计补充（当前有效）

依据[《VideoKit 国际化详细设计》](INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)及[国际化数据模型](INTERNATIONALIZATION_DATA_MODEL_V1.0.md)，首轮界面支持en/zh-Hans，SYSTEM/EXPLICIT切换与确定性script回退，资源离线完整；界面、字幕、识别、翻译四类语言分别设置，不隐式互改。UI localeGeneration不改变媒体generation/epoch，不重建播放或取消模型任务。

国际化任务归属按主里程碑最新补充：M0完整UI中英/四域设置演示，M8真实产品回归；SkinKit延后，不承担locale权威。

仅文档更新，主阶段/原P0/冻结证据保持，项目PAUSED_WAITING_USER，D1未过/M0未启。

## 2026-10-21 最新播放子系统设计基线

主里程碑D0/D1/M0–M10及原退出门不变。按照[《VideoKit 播放子系统详细设计》](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)在播放开发阶段拆阶段内子任务与验收ID，详见[映射](PLAYBACK_MILESTONE_MAPPING_V1.0.md)。M0保留完整Flutter UI+自有Theme/标识演示数据，M1真实播放、M3多实例、M7独立SDK、M8真实App接回、M9平台适配。ASR/翻译单列扩展，不自动添加D1/M1或发布门；启动前明确归属主阶段/版本及指标。子任务不是独立交测批次，仍每批1–3主阶段集中开发自测冻结/整包测试。项目暂停不变。

本节覆盖下文相冲突的历史候选说明；原P0、冻结报告和历史证据保持。仅文档更新，项目继续暂停。

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。本条覆盖下文此前“暂不自建 Theme”“M0 必须实接 SkinKit”等旧要求；供应方资料与历史要求保留供将来评审，不作为当前强制任务。完整现行范围见 [Flutter Theme 与延后集成决定](FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前 D1 冻结任务不变，M0 未启动。


## M0 起交付批次规则（2026-10-20）

负责人每批选择 1–3 个完整里程碑并向用户汇报范围与理由；coder 整批开发、自测、冻结后统一交 tester，tester 整批测试并集中报告，缺陷集中回交修复及回归。阶段需求与验收分栏保留，禁止逐问题反复交接，不以合批冒充阶段通过。详见 [协调规则](MILESTONE_COORDINATION_V1.0.md)。此规则覆盖下文单里程碑立即交测的冲突表述，当前 D1 及 M0 未启动状态不变。


用户最新决定（2026-10-20）：M0 在保留 API/Fake/TestKit/sample-host 原范围的同时，先搭建整个正式 Flutter App 的 UI 框架，按既有 18 页 PPT 的视觉与交互样式实现，并真实集成 SkinKit。允许生成带明确“演示模式·模拟数据”标识的本地测试数据演示全部主要页面与状态；演示不能冒充真实播放、跟踪或导出通过。后续 M1–M6 功能逐批实现并接回同一 UI，M7 保持独立宿主接入，M8 完成全功能真实集成与发布级验收，不再首次重建 UI。继续复用 SkinKit 默认/标准样式与合法最小宿主适配，不另建独立 Theme 系统、主题包或编辑器；通过既有配置与受支持的最小覆盖实现 PPT 样式，无法表达的差异列明评审。

| 阶段 | 新增/调整任务 | 验收边界 |
| --- | --- | --- |
| D1 | 保持当前验证与风险闭合 | 未通过，不以本文启动 M0 |
| M0 | 完整正式 Flutter App UI + 真实 SkinKit + 测试数据全页演示；原契约/Fake/TestKit 并行保留 | UI/真实主题/模拟数据隔离分别给证据 |
| M1–M6 | 播放、图片、多画面、编辑、跟踪、导出逐批实现并接回既有 UI | 各批真实媒体功能与受影响 UI 回归 |
| M7 | 独立 SDK/Browser 宿主接入 | 无 Flutter/SkinKit 强制依赖泄漏 |
| M8 | 全真实 App 整体验收、适配及发布隔离 | 非首次搭 UI，演示不冒充真实功能 |
| M9–M10 | 其他平台及许可/发布门槛保持 | 不由 Android 推断跨平台通过 |

完整任务：[M0 UI 框架](M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md)；[开发](milestones/M0_APP_UI_CODER_REQUIREMENTS_V1.0.md)；[测试](milestones/M0_APP_UI_TESTER_REQUIREMENTS_V1.0.md)；[SkinKit](SKINKIT_INTEGRATION_REQUIREMENTS_V1.0.md)。

历史主文件 MILESTONES_V1.0.md 本次写入被文件权限拒绝，未修改权限或原文；本补充为当前有效新增安排，覆盖其 M0/M8 相冲突表述，其余 P0 保留。当前仅文档更新，未编译、未设备测试。
