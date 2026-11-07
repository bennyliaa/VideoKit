# VideoKit 开发文档索引

版本：V1.1；日期：2026-11-06；状态：设计评审稿，评审通过后冻结。

V1.1 变更：为方便全平台开发，**UI 优先使用 Flutter 开发**（Flutter stable 3.47.7 / Dart 3.13.5）；媒体能力仍为原生 Android Kit。

## 1. 依据

- 唯一需求来源：[VideoKit 用户需求与 LocalVideoBrowser 接口需求 V1.0](VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)（下称“原需求”，§1–§31 全部有效）。
- 交付形态（原需求文首）：独立 Android Library（AAR/Gradle 模块）+ 示例宿主 App + Fake/TestKit；首期平台 Android 12 / API 31 及以上。UI 部分以 Flutter 包实现，并为原生宿主提供 add-to-app 嵌入桥接（[02](02_SYSTEM_ARCHITECTURE.md) 第 1 节）。
- 用户决定（2026-11-06）：VideoKit 一开始就使用 Flutter 开发 UI；先实现自有 Theme；SkinKit v2.0 支持 Flutter 后再接入。
- 本套文档覆盖原需求 §30 要求的十份设计文档，并补充 UI 框架设计、多实例资源设计和工程规范三份。

## 2. 开发总原则

**先开发完整的 UI 框架，再逐项补充具体功能。**

1. 第一阶段（VK-M0）交付完整的 VideoKit Flutter UI 框架：播放器、图片查看、多画面、编辑器、打码跟踪、导出流程全部界面可运行、可操作，由 Dart Fake 和标识清楚的演示数据驱动，并在 Flutter 示例 App 中可完整演示。
2. 之后每个功能里程碑（VK-M1 起）只把对应的 Fake 实现替换成真实实现，UI 组件和页面复用，不重写。
3. 演示数据永远不能冒充真实播放、跟踪或导出通过；测试报告中 UI 演示结果与真实能力结果分开记录。
4. 原需求 P0 不因 UI 优先而删减、降级或延后。

## 3. 文档清单

| 编号 | 文档 | 内容 | 原需求章节 |
| --- | --- | --- | --- |
| 01 | [产品需求](01_PRODUCT_REQUIREMENTS.md) | 范围、需求编号与优先级、不做事项 | §1–§5、§27、§31 |
| 02 | [系统架构](02_SYSTEM_ARCHITECTURE.md) | 分层（V1.2：平台无关层 / 平台引擎接口 SPI / 平台实现层，多平台复用）、模块、技术选型、§29 待定项决定、§30 必答问题 | §2、§13、§21、§24、§25、§29、§30 |
| 03 | [UI 框架设计](03_UI_FRAMEWORK_DESIGN.md) | Flutter 包结构、宿主接入方式、界面清单、主题、自适应、国际化与无障碍、演示模式 | §6–§10、§20 |
| 04 | [公共 API 契约](04_PUBLIC_API_CONTRACT.md) | 接口、DTO、状态机、命令、错误、能力、版本规则 | §13、§14、§18、§19 |
| 05 | [LocalVideoBrowser 集成](05_LOCALVIDEOBROWSER_INTEGRATION.md) | 适配器、映射、HostAction、租约、编辑提交、回退 | §9、§12、§15–§18 |
| 06 | [播放与图片设计](06_PLAYBACK_AND_IMAGE_DESIGN.md) | 视频会话、Media3、随机读取、事件、图片会话 | §5–§7、§14、§15 |
| 07 | [多实例与资源设计](07_MULTI_INSTANCE_AND_RESOURCE_DESIGN.md) | 多会话、资源预算、唯一音频、可见性、故障隔离 | §8、§16、§21 |
| 08 | [编辑时间线与导出设计](08_EDIT_TIMELINE_AND_EXPORT_DESIGN.md) | 工程模型、片段与拼接、打码、OutputSink、导出流程 | §10.1–§10.4、§11、§17 |
| 09 | [跟踪技术 Spike](09_TRACKING_TECHNICAL_SPIKE.md) | 人脸/物体跟踪方案、测试集、指标、退出材料 | §10.5–§10.7 |
| 10 | [开源与许可计划](10_OPEN_SOURCE_AND_LICENSE_PLAN.md) | 依赖选型、许可门禁、模型权利、SBOM | §23、§27 |
| 11 | [测试与验收计划](11_TEST_AND_ACCEPTANCE_PLAN.md) | 测试层次、矩阵、追踪方式、阻断检查 | §26、§27、§31 |
| 12 | [里程碑](12_MILESTONES.md) | UI 优先的阶段划分、范围、退出条件、交付流程 | §28 |
| 13 | [工程规范](13_ENGINEERING_CONVENTIONS.md) | 仓库结构、构建、编码、日志、版本与提交 | §22、§23、§25 |
| 14 | [VK-M0 详细设计](14_M0_DETAILED_DESIGN.md) | Flutter UI 内部架构与组件拆分、Theme Token 取值、Dart Fake、Pigeon 通道、插件与 add-to-app 桥接、M0 默认值与开发顺序 | §6–§10、§13、§20 |
| 15 | [媒体技术路线决定](15_MEDIA_TECHNOLOGY_DECISIONS.md) | **现行技术路线**：播放、解码、图片、剪辑拼接、合成、导出封装、渲染、隔离、跟踪的方案决定；D1 重新划定为聚焦验证 S1–S6；路线图 | §5–§7、§10、§11、§14、§16、§21、§23、§29 |

## 4. 阅读顺序

- 所有人：01 → 02 → 15 → 12。
- UI 开发：03 → 04 → 14 → 06/07/08 中与界面相关的章节。
- 能力开发：04 → 06/07/08/09 → 10。
- 测试：01 → 11 → 对应设计文档。
- 宿主集成：04 → 05。

## 5. 版本规划

| 版本 | 范围 |
| --- | --- |
| VideoKit V1.0（本套文档） | 原生 Android Kit（AAR）+ Flutter UI（`videokit_ui`、`videokit_flutter` 插件）+ 原生嵌入桥接 + TestKit/Fake + 示例宿主，原需求 §1–§31 全部 P0；只实现 Android |
| 后续版本 | 其他平台（iOS、macOS、Windows）：新增对应原生 Kit 与插件实现，复用同一套 Flutter UI 与 Dart API；范围与时间另立需求 |
| 主题 | VideoKit 先按 UI 设计稿实现自有 Theme（结构与键名已按 SkinKit 规范对齐，见 [03](03_UI_FRAMEWORK_DESIGN.md) §5.2）；SkinKit v2.0 支持 Flutter 后作为可选主题来源接入（03 §5.5）。SkinKit V1.0 规范见 `docs/SkinKit/`；SkinKit 为用户自有项目，无需另行授权 |
| 产品形态 | 嵌入组件（宿主 App 内使用）+ VideoKit 独立 App（[01](01_PRODUCT_REQUIREMENTS.md) §1；独立 App 的额外功能范围待定义） |

VideoKit 从一开始就使用 Flutter 开发 UI。全平台扩展约束见 [02](02_SYSTEM_ARCHITECTURE.md) 第 9 节。

## 6. 现状与说明

- 早期 Android 原型（`app/` Compose 模板与验证代码、`spikes/d1c14/` 隔离进程验证代码及其 Gradle 配置）已于 2026-11-06 移到 `D:\CodexProjects\VideoKit test-workspace\archive\d1-android-prototype`，只作技术参考；正式工程按 [13 工程规范](13_ENGINEERING_CONVENTIONS.md) 新建。
- Flutter SDK：`D:\CodexProjects\flutter`（stable 3.47.7，Dart 3.13.5）。
- 测试样本位于 `D:\CodexProjects\VideoKit test-workspace\test_media`，只读，不打包、不上传。
- UI 开发与验收效果以 [VideoKit_UI_Design_V1.0.pptx](VideoKit_UI_Design_V1.0.pptx) 为准（2026-11-07 用户确认，规则见 [03](03_UI_FRAMEWORK_DESIGN.md) §5.4）。
- 文档中“决定”是负责人建议，评审通过后冻结；“待定”项在对应里程碑开始前冻结。冻结后的变更必须记录原因和影响。
