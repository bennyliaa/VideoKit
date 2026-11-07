# VideoKit

VideoKit 是可独立发布的 Android 媒体组件：视频播放、图片查看、多画面、剪辑拼接、打码与跟踪、导出。媒体能力由原生 Android Kit（Kotlin + Media3）提供，UI 用 Flutter 开发，原生宿主可通过 add-to-app 嵌入。首个宿主为 LocalVideoBrowser。

## 当前状态（2026-11-06）

- 设计评审稿阶段，正式工程尚未建立。
- 下一步：VK-M0（Flutter UI 框架 + API + Fake）与聚焦验证 S1–S6 并行。
- 当前没有可运行的产品代码；旧 Android 原型已移出项目（见下文“历史资料”）。

## 文档

- [开发文档索引](docs/requirement/00_DEV_DOCS_INDEX.md)：从这里开始
- [原始需求](docs/requirement/VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)
- [媒体技术路线决定](docs/requirement/15_MEDIA_TECHNOLOGY_DECISIONS.md)
- [里程碑](docs/requirement/12_MILESTONES.md)
- [VK-M0 详细设计](docs/requirement/14_M0_DETAILED_DESIGN.md)
- [UI 设计稿](docs/requirement/VideoKit_UI_Design_V1.0.pptx)
- [SkinKit 规范](docs/SkinKit/)（后期主题接入参考）

## 工作规则

见 [AGENTS.md](AGENTS.md)。仓库结构与提交规范见 [13 工程规范](docs/requirement/13_ENGINEERING_CONVENTIONS.md)。

## 历史资料（不在仓库中）

- D1 验证证据：`D:\CodexProjects\VideoKit test-workspace\D1`
- 旧 Android 原型（app、spikes/d1c14、Gradle 配置）与交接文档：`D:\CodexProjects\VideoKit test-workspace\archive`
- 测试样本（只读，不入库）：`D:\CodexProjects\VideoKit test-workspace\test_media`
