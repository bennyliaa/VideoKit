# 12 里程碑

版本：V1.1；日期：2026-11-06；对应原需求 §28，并按开发总原则“先开发完整的 UI 框架，再逐项补充具体功能”调整 VK-M0 的范围。不承诺日历工期；工期在 VK-M0 完成后根据实际速度估算。

## 1. 总体路线

技术方案与 D1 重新划定见 [15 媒体技术路线决定](15_MEDIA_TECHNOLOGY_DECISIONS.md)：D1 改为聚焦验证 S1–S6，与 VK-M0 并行；各功能里程碑开始前须具备对应验证结论（15 §5）。原“D1 通过后才能推进 M0”的顺序由用户 2026-11-06 决定调整。

```text
VK-M0  Flutter UI 框架 + API/Fake/TestKit + 示例宿主   ← 先把完整 UI 跑起来；同时进行 S1–S6
  │
  ├─ VK-M1  单视频播放（真实）            ┐
  ├─ VK-M2  图片 + HostAction（真实）       │ 逐项把 Fake 换成真实实现
  ├─ VK-M3  多实例 + 资源 + 音频（真实）    │ UI 复用，不重写
  ├─ VK-M4  时间线 + 拼接 + 工程（真实）    │
  ├─ VK-M5  打码 + 自动跟踪（真实）         │   ← 跟踪 Spike 与 M1–M3 并行
  ├─ VK-M6  导出 Sink + 取消 + 安全收尾     ┘
  └─ VK-M7  AAR 发布 + LocalVideoBrowser 真实适配
```

## 2. 里程碑明细

### VK-M0 UI 框架与基础契约

| 项 | 内容 |
| --- | --- |
| 范围 | 工程骨架（Gradle 多模块 + Flutter 包工作区、Version Catalog 与 `pubspec.lock`、锁定与校验、CI）；许可证审查初版；Kotlin `videokit-api` 与 Dart `videokit_api` 全部接口草案（[04](04_PUBLIC_API_CONTRACT.md)）；`videokit_fake`（Dart Fake、场景、演示数据、Dart 契约测试）与 `videokit-testkit`（Kotlin Fake、契约测试初版）；**`videokit_ui` 全部 Flutter 界面 UI-01–UI-09**（[03](03_UI_FRAMEWORK_DESIGN.md)），VideoKit 自有 Theme（Token、浅深色、宿主覆盖）；中英 ARB 资源、RTL、无障碍语义；`videokit_flutter` 插件骨架（通道协议、纹理注册，连接原生 Fake）；`videokit_example` Flutter 示例 App 与原生 `sample-host`（add-to-app 嵌入最小示例），均含模拟 Browser 宿主（假源、标签/收藏动作、邻近列表、多画面网格、临时 Sink） |
| 详细设计 | [14 VK-M0 详细设计](14_M0_DETAILED_DESIGN.md) |
| 不含 | 任何真实解码、编码、跟踪；视觉设计取值（待用户通知 UI 设计后更新 Token） |
| 退出条件 | ① [03](03_UI_FRAMEWORK_DESIGN.md) §9 全部 UI 退出条件；② API（Kotlin 与 Dart）评审通过并冻结 1.0.0（允许后续次版本增加）；③ 两侧 Fake 通过各自契约测试；④ LocalVideoBrowser 可只用 Fake 完成契约集成（原需求 VK-M0 退出条件）；⑤ add-to-app 嵌入的包体积与首帧耗时实测并记录；⑥ 追踪表 TRACEABILITY.csv 建立 |

### VK-M1 单视频播放

| 项 | 内容 |
| --- | --- |
| 范围 | `videokit-core` 会话与命令执行器；`videokit-playback` + `videokit-media3`；宿主 readAt 桥接（HostDataSource）；能力探测；Seek、倍速、音量、音轨、字幕、方向、缩放平移；播放事件与观看时间；状态快照恢复；锁定与后台命令；UI-01/UI-02 经 `videokit_flutter` 接真实会话（纹理显示） |
| 退出条件 | Android 12 手机及真机大视频（含 2GiB 以上）播放通过；[06](06_PLAYBACK_AND_IMAGE_DESIGN.md) §8 播放项；真实实现通过契约测试；释放后句柄归零 |

### VK-M2 图片与宿主交互

| 项 | 内容 |
| --- | --- |
| 范围 | `videokit-image`：静态/动态图、大图分块、EXIF 方向、内存额度；左右导航请求；HostAction 真实回调、超时与去重；控件可见性与宿主面板同步；UI-03/UI-04 经 `videokit_flutter` 接真实会话 |
| 退出条件 | 图片格式矩阵与标签/收藏回调通过；图片界面无视频控件 |

### VK-M3 多实例

| 项 | 内容 |
| --- | --- |
| 范围 | ResourceBudget 与能力探测；1/4/9/12 槽；唯一音频与 epoch；可见性策略；探测隔离进程与故障注入；UI-05 接真实会话（多纹理） |
| 退出条件 | 单槽故障隔离；多槽稳定释放；资源不足时降级而非循环创建；[07](07_MULTI_INSTANCE_AND_RESOURCE_DESIGN.md) §6 |

### VK-M4 时间线与拼接

| 项 | 内容 |
| --- | --- |
| 范围 | `videokit-timeline`：工程 Schema、命令、撤销重做、snapshot/restore 与迁移；单视频片段与多视频拼接；快速拼接与转码路径选择；方向与音视频同步处理；临时导出（基础 Sink）；UI-06 接真实工程 |
| 退出条件 | 新输出正确（时长、方向、PTS、音视频同步），源文件 hash 不变；工程保存与恢复通过 |

### VK-M5 打码与自动跟踪

| 项 | 内容 |
| --- | --- |
| 前置 | 跟踪 Spike 通过并冻结方案与阈值（[09](09_TRACKING_TECHNICAL_SPIKE.md) §7） |
| 范围 | `videokit-effects`：马赛克/模糊、关键帧、坐标映射；`videokit-tracking`：人脸检测与选择、物体跟踪、多目标、重关联、置信状态、纠正与重算、覆盖报告；隔离 worker；UI-07 接真实实现 |
| 退出条件 | 跟踪质量报告达到冻结阈值；未覆盖区间检查阻止静默漏码；预览与导出遮罩一致（黄金图像） |

### VK-M6 导出与安全收尾

| 项 | 内容 |
| --- | --- |
| 范围 | Sink 能力协商（FD/随机写/顺序写方案）；导出隔离 worker；阶段进度；有界取消；输出校验；故障恢复（进程被杀、断线、空间不足）；性能与资源统计；安全与日志审查；UI-08 接真实导出 |
| 退出条件 | 输出协议、资源释放与许可检查通过；[11](11_TEST_AND_ACCEPTANCE_PLAN.md) §7 阻断项中与导出相关的全部 PASS |

### VK-M7 发布与宿主接入

| 项 | 内容 |
| --- | --- |
| 范围 | 多 artifact 发布到受控 Maven 仓库，Flutter 包发布到受控 pub 仓库（或私有 Git 依赖）；API 参考文档与变更记录；Consumer R8 规则；SBOM/NOTICE；版本兼容测试；LocalVideoBrowser 真实适配配合与契约测试；移除/替换 AAR 回退验证 |
| 退出条件 | 可移除/替换 AAR，宿主仍可降级运行；[11](11_TEST_AND_ACCEPTANCE_PLAN.md) §7 全部阻断项 PASS；原需求 §31 成功标准逐项有证据 |

## 3. 并行工作

| 并行项 | 时间 | 说明 |
| --- | --- | --- |
| 聚焦验证 S1–S5 | 与 VK-M0 并行 | S1、S2 在 VK-M1 前；S5 在 VK-M3 前；S3、S4 在 VK-M4 前（[15](15_MEDIA_TECHNOLOGY_DECISIONS.md) §4） |
| 跟踪 Spike（S6） | 与 VK-M0–M3 并行 | P0 风险最高，必须提早；结果决定 VK-M5 方案 |
| UI 视觉设计 | 用户通知后 | 只更新 Token 与组件样式，不影响功能里程碑 |
| 测试样本补充 | VK-M0 起持续 | 按 [11](11_TEST_AND_ACCEPTANCE_PLAN.md) §4 缺口补充 |
| SkinKit 接入 | SkinKit v2.0 支持 Flutter 后，且自有 Theme 稳定、收到接口文档后 | 作为可选主题来源包 `videokit_theme_skinkit`（[03](03_UI_FRAMEWORK_DESIGN.md) §5.5），排期另定 |

里程碑并行的前提是公共 API 已评审冻结（原需求 §28）；跟踪与导出可在播放/图片之后并行开发。

## 4. 每个里程碑的交付物

1. 源码（Git commit）与构建产物（AAR、Flutter 包、`videokit_example` 与 `sample-host` APK）及 SHA-256。
2. 范围完成矩阵：每项 DONE / NOT_DONE；UI 接入矩阵：哪些界面已接真实实现、哪些仍为 Fake。
3. 自测结果与测试报告（[11](11_TEST_AND_ACCEPTANCE_PLAN.md) §6）。
4. 依赖变更、许可检查与 SBOM 更新。
5. 已知问题与不支持能力清单。
6. 已冻结的待定项与指标（[02](02_SYSTEM_ARCHITECTURE.md) §7）。

## 5. 后续版本

- 其他平台（iOS、macOS、Windows）：新增对应原生 Kit 与插件实现，复用同一套 Flutter UI 与 Dart API；范围与时间另立需求，当前不承诺。
