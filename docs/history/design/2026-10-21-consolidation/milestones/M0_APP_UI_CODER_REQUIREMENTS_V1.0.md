# M0 技术开发补充：完整 Flutter UI 框架、SkinKit 与演示数据 V1.0

## 国际化详细设计对接（2026-10-21）

按[国际化详细设计](../INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)与[数据模型](../INTERNATIONALIZATION_DATA_MODEL_V1.0.md)，M0实现LocaleController/四域Repository/完整ARB资源与类型化key，系统/显式/script回退、快速切换最新胜、原子偏好和失败提示；全页面/弹窗/语义覆盖，未实现模型明确演示/禁用。按原UI0-09完成中英/伪长文/RTL/100-130-200%字体/焦点读屏。

这是未来阶段开发要求，不是当前派发；主里程碑不变，集中整包开发测试规则保持，项目继续暂停。

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。本条覆盖下文此前“暂不自建 Theme”“M0 必须实接 SkinKit”等旧要求；供应方资料与历史要求保留供将来评审，不作为当前强制任务。完整现行范围见 [Flutter Theme 与延后集成决定](../FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前 D1 冻结任务不变，M0 未启动。


## M0 起交付批次规则（2026-10-20）

负责人每批选择 1–3 个完整里程碑并向用户汇报范围与理由；coder 整批开发、自测、冻结后统一交 tester，tester 整批测试并集中报告，缺陷集中回交修复及回归。阶段需求与验收分栏保留，禁止逐问题反复交接，不以合批冒充阶段通过。详见 [协调规则](../MILESTONE_COORDINATION_V1.0.md)。此规则覆盖下文单里程碑立即交测的冲突表述，当前 D1 及 M0 未启动状态不变。


日期：2026-10-20。状态：M0未来正式范围，当前D1未退出、不派发产品编码。与 [原M0开发要求](M0_CODER_REQUIREMENTS_V1.0.md) 同时执行，覆盖原“M0不做完整产品UI”表述。主规范：[M0完整UI要求](../M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md)。

1. 保留API/core/Fake/TestKit/原生sample-host全部范围，新增正式Flutter App同工程全路由/公共组件/Controller与服务注入；不另做废弃Demo。
2. 按PPT样式完成UI0-01–10全页面和必要空/加载/错误/取消/成功状态；手机平板布局、播放/图片/多画面/工程时间线/跟踪纠正/导出/设置可交互。
3. M0真实集成SkinKit default/contract/Core，复用既有主题/默认/Token及合法参数，用最小Flutter Adapter表达PPT视觉；不新建自有Theme/解析器/主题包/商城编辑器。差异逐组件提交评审，不静默偏离PPT或用Fake替代SkinKit。
4. 实现UI0-11–16固定seed测试数据/场景、可控时钟/重置、Demo标识、Debug/Release隔离；所有模拟媒体/跟踪/导出明确演示，不输出假真实文件或覆盖原件。
5. 同一稳定VideoKit服务端口接Fake和未来真实Adapter，给M1–M6逐页接回矩阵；真实模式禁止静默fallback Fake；纯核心不依赖Flutter/SkinKit/Browser。
6. 集中自检导航、关键操作、主题实接/快照/回退、适配国际化/无障碍及模拟边界；实际SDK/工具链许可缺口列BLOCKED，不能只编译报全完成。
7. 全批完成后必要集中构建、自检冻结，交一个candidate及APK/组件清单/源码锁与hash、演示数据manifest、PPT映射、所有页面截图/交互录屏、真实与演示分栏报告；保留失败，避免每按钮/每页编译交接。

后续功能原P0不删，M0 UI演示完成不表示真实播放器/编辑/导出完成。未经D1退出与负责人正式派单不提前开工。
