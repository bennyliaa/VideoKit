# 10 开源与许可计划

版本：V1.1；日期：2026-11-06；对应原需求 §23、§25、§27。本文件是选型与准入清单，不是法律意见；正式发行前需完成第 6 节材料。

## 1. 原则

- 优先采用成熟、仍在维护、许可适合闭源商业产品的组件（MIT、BSD、Apache-2.0 优先）。
- GPL、AGPL、SSPL、无许可或许可不清的代码不得进入产品模块；把代码放进适配层、动态加载或独立进程并不能消除许可义务。
- FFmpeg：未经明确批准不集成。若将来评估，必须先说明构建配置、LGPL/GPL 组件、链接方式、NOTICE、源码提供义务和对宿主闭源的影响。
- AI 模型：代码许可、模型权重许可、训练数据来源、商用与再分发、隐私分别核查；仓库是 MIT 不代表权重可商用。
- 可以参考或合法移植明确允许的播放器交互实现，必须记录来源 commit、许可与修改内容。

## 2. 候选清单

| 组件 | 用途 | 许可（初查） | 状态 | 准入前需完成 |
| --- | --- | --- | --- | --- |
| AndroidX Media3（ExoPlayer、Transformer、Effect、Muxer） | 播放、编辑导出 | Apache-2.0 | 采用 | 固定版本；所用 artifact 及传递依赖清单 |
| Flutter SDK（framework + engine，stable 3.47.7） | UI | BSD-3-Clause（engine 内第三方组件各自许可） | 采用 | 汇总 engine 第三方许可到 NOTICE |
| Dart SDK 3.13.5、`flutter_localizations`、`intl` | UI 语言与国际化 | BSD-3-Clause | 采用 | 固定版本（`pubspec.lock`） |
| Pigeon | Dart ↔ 原生通道代码生成 | BSD-3-Clause | 采用（开发期） | 生成代码入库 |
| AndroidX 基础库 | 原生基础设施、Flutter 嵌入 | Apache-2.0 | 采用 | 固定版本 |
| Kotlin、kotlinx.coroutines、kotlinx.serialization | 语言与并发、工程 JSON | Apache-2.0 | 采用 | 固定版本 |
| Android 平台 ImageDecoder / BitmapRegionDecoder | 图片解码 | 平台 API | 采用 | 无额外依赖 |
| Coil | 图片加载（候选） | Apache-2.0 | 候选 | 验证动图暂停、大图分块后决定 |
| OpenCV（精简构建） | 图像处理、传统跟踪、DNN | Apache-2.0（4.5+） | Spike | 所选模块与第三方组件清单；contrib 模块逐项核查 |
| YuNet（OpenCV Zoo） | 人脸检测 | 目录标 MIT | Spike | 模型 hash、训练数据来源、商用/再分发权利 |
| ViTTrack（OpenCV Zoo） | 物体跟踪 | 目录标 Apache-2.0 | Spike | 同上 |
| ONNX Runtime | 推理运行时（对照） | MIT | Spike | provider 依赖、遥测关闭、包体积 |
| JUnit、Turbine、kotlinx-coroutines-test | 原生测试 | EPL/Apache | 仅测试 | 不进入产品 artifact |
| `flutter_test`、`integration_test` | Flutter 测试（含 golden 截图） | BSD-3-Clause | 仅测试 | 不进入产品 |
| 其他 pub 包 | — | 逐个审查 | 默认不引入 | 新增需许可审查、固定版本 |
| FFmpeg | — | LGPL/GPL | 不集成 | 需用户明确批准 |
| libVLC、libmpv | — | LGPL/GPL | 不集成 | — |
| SkinKit v2.0（Flutter 包） | 后期主题来源 | 待核 | 后期（SkinKit v2.0 支持 Flutter 后） | 收到接口文档后核查许可、版本与分发条款 |

测试依赖只用于测试配置，不进入发布的 AAR。

## 3. 供应链控制

- 原生依赖版本写在 Gradle Version Catalog（`gradle/libs.versions.toml`），Dart 依赖写精确版本并提交 `pubspec.lock`；禁止动态版本（`+`、`latest`、`any`、`^` 范围用于发布包时须锁定）和 Snapshot。
- 开启依赖锁定（`dependencyLocking { lockAllConfigurations() }`）与依赖校验（`gradle/verification-metadata.xml`，校验 SHA-256）。
- 原生库与模型文件记录来源 URL、版本或 commit、SHA-256，存入 `third_party/MANIFEST.json`。
- 每次升级依赖：更新锁文件与校验文件，重跑许可检查与契约测试。
- CI 生成 SBOM（CycloneDX 格式）并执行已知漏洞扫描。

## 4. 模型准入

每个模型在 `third_party/models/MODEL_MANIFEST.json` 中登记：名称、版本、来源 URL、权重 SHA-256、代码许可、权重许可、训练数据来源说明、是否允许商用、是否允许再分发、是否允许修改/量化、隐私影响。任一项未知标记为 BLOCKED，BLOCKED 模型不能进入发布构建。

## 5. 资源与素材

演示素材、图标、字体、测试视频同样需要许可记录；`test_media` 只用于本地测试，不打包、不上传；演示数据只用原创生成素材。

## 6. 发行材料（§25）

每个发布版本交付：

- SBOM（含传递依赖）与 BOM。
- 第三方 NOTICE 与许可证文本（汇总到 AAR 的 `META-INF` 和文档）。
- 模型说明（MODEL_MANIFEST 摘要）。
- 已知漏洞检查结果。
- 各 AAR、Flutter 包与示例 App（`videokit_example`、`sample-host`）的 SHA-256。
- 闭源宿主需履行的义务说明（随 SDK 文档提供）。

## 7. 检查

| 检查 | 时机 | 失败处理 |
| --- | --- | --- |
| 许可白名单扫描 | 每次 CI | 出现非白名单许可时构建失败 |
| 依赖锁与校验 | 每次构建 | 校验不符构建失败 |
| 模型 MANIFEST 完整性 | 发布构建 | BLOCKED 模型阻止发布 |
| SBOM 与漏洞扫描 | 每个里程碑交付 | 高危漏洞需处置记录 |
