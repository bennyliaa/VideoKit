# SkinKit 文档变更记录 V1.0

日期：2026-10-20。用户指定集成 SkinKit，并进一步明确暂不新建自有 Theme；后者为本次最新约束。直接复用已交付默认外观/主题/标准样式，只有 API 必需时才做最小宿主默认数据接线。

## 已同步的既有文档

- [PROJECT_DECISIONS_AND_EXECUTION_V1.0.md](../PROJECT_DECISIONS_AND_EXECUTION_V1.0.md)
- [PRODUCT_REQUIREMENTS_V1.0.md](../PRODUCT_REQUIREMENTS_V1.0.md)
- [VIDEOKIT_APP_ARCHITECTURE_V1.0.md](../VIDEOKIT_APP_ARCHITECTURE_V1.0.md)
- [SYSTEM_ARCHITECTURE_V1.0.md](../SYSTEM_ARCHITECTURE_V1.0.md)
- [OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md](../OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md)
- [TEST_AND_ACCEPTANCE_PLAN_V1.0.md](../TEST_AND_ACCEPTANCE_PLAN_V1.0.md)
- [DESIGN_REVIEW_V1.0.md](../DESIGN_REVIEW_V1.0.md)
- [OPEN_SOURCE_FRAMEWORKS_AND_DEVELOPMENT_EFFORT_ESTIMATE_V1.0.md](../OPEN_SOURCE_FRAMEWORKS_AND_DEVELOPMENT_EFFORT_ESTIMATE_V1.0.md)
- [VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md](../VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)

## 新增规范与工作单

- [SKINKIT_INTEGRATION_REQUIREMENTS_V1.0.md](../SKINKIT_INTEGRATION_REQUIREMENTS_V1.0.md)
- [MILESTONES_SKINKIT_ADDENDUM_V1.0.md](../MILESTONES_SKINKIT_ADDENDUM_V1.0.md)
- [ui/VIDEOKIT_SKINKIT_UI_MAPPING_V1.0.md](../ui/VIDEOKIT_SKINKIT_UI_MAPPING_V1.0.md)
- [ui/SKINKIT_SOURCE_EVIDENCE_V1.0.json](../ui/SKINKIT_SOURCE_EVIDENCE_V1.0.json)
- [milestones/VK_M8_SKINKIT_CODER_REQUIREMENTS_V1.0.md](../milestones/VK_M8_SKINKIT_CODER_REQUIREMENTS_V1.0.md)
- [milestones/VK_M8_SKINKIT_TESTER_REQUIREMENTS_V1.0.md](../milestones/VK_M8_SKINKIT_TESTER_REQUIREMENTS_V1.0.md)

## 保留与实际边界

旧 `MILESTONES_V1.0.md` 普通及提升写入均为 PermissionError；没有修改权限或替换原文件，采用补充文件作为有效新增要求。其余供应方交付、旧候选封包、PPT 和产品代码/依赖锁均未修改。

已核 SDK ZIP 及供应方7份资料身份、ZIP内外对应文档一致；集成测试/产品构建/设备操作均为0，未付款或批准正式发行许可。SDK现主要JVM/Android Views，Flutter/其他平台适配待实现验证；许可证工程草案的主体/1.1.0适用/合法获取和分发范围保留发布门。

M8工作单为未来整批要求，不派当前UI编码、不打断D1已冻结媒体验证。文档链接/文件存在与来源不变核查不是功能验收。后续coder/tester必须按真实阶段执行SK-01–20 / SK-T01–12。


## 2026-10-20 后续指令：M0 完整 UI 优先

用户最新决定（2026-10-20）：M0 在保留 API/Fake/TestKit/sample-host 原范围的同时，先搭建整个正式 Flutter App 的 UI 框架，按既有 18 页 PPT 的视觉与交互样式实现，并真实集成 SkinKit。允许生成带明确“演示模式·模拟数据”标识的本地测试数据演示全部主要页面与状态；演示不能冒充真实播放、跟踪或导出通过。后续 M1–M6 功能逐批实现并接回同一 UI，M7 保持独立宿主接入，M8 完成全功能真实集成与发布级验收，不再首次重建 UI。继续复用 SkinKit 默认/标准样式与合法最小宿主适配，不另建独立 Theme 系统、主题包或编辑器；通过既有配置与受支持的最小覆盖实现 PPT 样式，无法表达的差异列明评审。

新增 M0 总要求及独立开发/测试工作单；同步产品、架构、测试、M0–M8 各阶段工作单与可写里程碑补充。此前“PPT 仅结构参考”和“M8 首次集成”已由本要求覆盖；供应方原包、PPT 原文件及冻结候选不变。文档验收不代表实现通过。


## 最新决定：Flutter 自有 Theme 优先

用户改为先建立自有 VideoKit Theme，SkinKit 等正式 Flutter 支持后再集成；已新增现行决定并在产品、架构、许可、测试、M0 UI 和各阶段工作单顶部明确覆盖旧要求。旧供应方资料、PPT、冻结候选不变。仅文档调整，未构建或设备测试。
