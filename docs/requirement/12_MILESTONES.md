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
  ├─ VK-A1  App 媒体库（App 业务，与模块里程碑并行，在 VK-FT 前完成）
  ├─ VK-FT  全功能测试（M0–M6 与 VK-A1 全部完成后，经用户确认开始；通过后才进入 M7、M8）
  ├─ VK-M7  模块发布（AAR + Flutter 包）+ LocalVideoBrowser 真实适配
  └─ VK-M8  VideoKit App 发布（App 外壳自 M0 起并行搭建）
```

### 1.1 UI 先行与真实能力接入顺序（2026-11-06 确认）

1. UI 实现阶段先用模拟数据演示；真实功能随开发进展逐个接入 UI，UI 只依赖 `videokit_api`，换后端不改界面。
2. Fake 与真实实现通过同一套契约测试，场景必须包含慢加载、缓冲、断线、不支持、资源不足、失败、取消等，不做“理想化”的 Fake。
3. VK-M0 内打通“Flutter → 通道 → 原生 Fake → 纹理”路径，提前验证纹理与 Surface 生命周期。
4. 测试机到位后先完成 S1、S2，然后**优先让播放器（UI-01）接入真实播放**，作为第一个真实能力。
5. 每个里程碑交付“UI 接入矩阵”（哪些界面接真实实现、哪些仍为模拟）；示例 App 保留模拟/真实后端切换，便于对比。
6. **国际化机制从第一天建好，暂缓的只是翻译**：第一版只维护简体中文；任何界面文字从第一次提交起就走 ARB 资源，不允许“先写死中文、以后再抽取”。英文作为独立批次在 VK-M6 完成后、VK-M7 之前整批加入（翻译 + 英文 golden + 走查），宿主需要更早时提前；其他语言之后按需增加（规则见 [13](13_ENGINEERING_CONVENTIONS.md) §3.1）。

## 2. 里程碑明细

### VK-M0 UI 框架与基础契约

| 项 | 内容 |
| --- | --- |
| 范围 | 工程骨架（Gradle 多模块 + Flutter 包工作区、Version Catalog 与 `pubspec.lock`、锁定与校验、CI）；许可证审查初版；多平台分层骨架（`kit/common` 平台无关层为 KMP `commonMain`、`kit/android` 平台实现层、`spec/` 规格与测试向量目录、SPI 接口草案，见 [02](02_SYSTEM_ARCHITECTURE.md) §4）；Kotlin `videokit-api`（无 Android 类型）+ `videokit-api-android` 与 Dart `videokit_api` 全部接口草案（[04](04_PUBLIC_API_CONTRACT.md)）；`videokit_fake`（Dart Fake、场景、演示数据、Dart 契约测试）与 `videokit-testkit`（Kotlin Fake、契约测试初版）；**`videokit_ui` 全部 Flutter 界面 UI-01–UI-09**（[03](03_UI_FRAMEWORK_DESIGN.md)），VideoKit 自有 Theme（Token、浅深色、宿主覆盖）；中文 ARB 资源与国际化机制、RTL、无障碍语义；`videokit_flutter` 联邦插件骨架（platform_interface + Android 平台包：通道协议、纹理注册，连接原生 Fake）；`videokit_example` Flutter 示例 App 与原生 `sample-host`（add-to-app 嵌入最小示例），均含模拟 Browser 宿主（假源、标签/收藏动作、邻近列表、多画面网格、临时 Sink） |
| 详细设计 | [14 VK-M0 详细设计](14_M0_DETAILED_DESIGN.md) |
| 视觉基准 | UI 开发与验收以 [VideoKit_UI_Design_V1.0.pptx](VideoKit_UI_Design_V1.0.pptx) 为准（[03](03_UI_FRAMEWORK_DESIGN.md) §5.4） |
| 不含 | 任何真实解码、编码、跟踪 |
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

### VK-M5A 头像替换（REQ-ED-07，用户 2026-11-07 加入）

| 项 | 内容 |
| --- | --- |
| 前置 | 头像抠图验证 S7 通过；VK-M5 跟踪可用（随跟踪移动的部分） |
| 范围 | ① 头像准备：用户图片 → 人脸检测 → 扩到头部（含头发）裁剪 → 人像分割/抠图去背景与边缘 → 透明边缘头像（PNG），可微调（缩放、偏移、擦除/恢复），内置默认头像；② 遮罩样式新增 `IMAGE`（工程 schema v1.1，schemaMinor+1，旧读取端按 R4 回退为马赛克）；③ 头部框与转角：由跟踪框扩展，转角取人脸关键点（双眼连线，`rollDeg`）；④ 预览与导出共用同一套计算（`videokit-effects` 新增头像合成）；⑤ UI：Kit 编辑器中的头像样式（设计稿第 25 页第三图）先接 Fake；选择头像、调整头像页面（第 25 页前两图）由 VideoKit App 业务层实现，作为宿主示例（04A E5、E6） |
| 退出条件 | 抠图质量在测试图集上达标（S7 阈值）；导出中头像位置、大小、转角与预览一致（黄金图像）；多人场景不换错人（09 §3）；源文件不变；不上传 |
| 不做 | AI 换脸（深度合成）；如以后要做须单独立项并完成许可与合规评估 |

### VK-M6 导出与安全收尾

| 项 | 内容 |
| --- | --- |
| 范围 | Sink 能力协商（FD/随机写/顺序写方案）；导出隔离 worker；阶段进度；有界取消；输出校验；故障恢复（进程被杀、断线、空间不足）；性能与资源统计；安全与日志审查；UI-08 接真实导出 |
| 退出条件 | 输出协议、资源释放与许可检查通过；[11](11_TEST_AND_ACCEPTANCE_PLAN.md) §7 阻断项中与导出相关的全部 PASS |

### VK-FT 全功能测试（用户 2026-11-08 加入）

| 项 | 内容 |
| --- | --- |
| 前置 | VK-M0–M6（含 VK-M5A）与 VK-A1 媒体库全部开发完成并冻结；负责人检查开始条件、样本与测试机后，**先与用户确认可以开始** |
| 范围 | 按 [16](16_FULL_FUNCTION_TEST_PLAN.md) 的 FT-01–FT-14 分批有序执行：全部功能、UI 布局与设计稿逐页、细节与边界、可预期错误（损坏的视频和图片、断线、空间不足、进程被杀等）、安全隐私、稳定性与性能；之后修复并做回归轮 |
| 退出条件 | 16 §5 全部满足（真机上 P0 用例 PASS、无未关闭 P1/P2、源文件不变、无上传、release 隔离通过、NOT_RUN 经用户确认）；《全功能测试报告》经用户确认 |
| 说明 | 全功能测试通过，才表示项目功能经过验证；之后才进入 VK-M7、VK-M8 打包发布。英文翻译批次（本文 §0 第 6 条）在全功能测试之前完成，以便一并测试 |

### VK-M7 发布与宿主接入

| 项 | 内容 |
| --- | --- |
| 范围 | 多 artifact 发布到受控 Maven 仓库，Flutter 包发布到受控 pub 仓库（或私有 Git 依赖）；API 参考文档与变更记录；Consumer R8 规则；SBOM/NOTICE；版本兼容测试；LocalVideoBrowser 真实适配配合与契约测试；移除/替换 AAR 回退验证 |
| 退出条件 | 可移除/替换 AAR，宿主仍可降级运行；[11](11_TEST_AND_ACCEPTANCE_PLAN.md) §7 全部阻断项 PASS；原需求 §31 成功标准逐项有证据 |

### VK-A1 App 媒体库（REQ-APP-09–13，用户 2026-11-08 加入）

| 项 | 内容 |
| --- | --- |
| 性质 | VideoKit App 业务层功能，不属于模块，不改 Kit API；与模块里程碑并行开发，在全功能测试（VK-FT）之前完成 |
| 范围 | 媒体库存储（App 内部私有目录、索引数据库；不加密；排除备份）；卸载保留选项（hasFragileUserData）、卸载警告、导出到相册（REQ-APP-14）；密码、生物识别解锁、自动上锁、防截屏；导入（多选、进度、取消、可选删除原文件）；全部/视频/图片筛选与分页（默认 20，可设 10/20/50/100 或 5–200）；一层文件夹的新建、改名、删除与媒体移动；文件夹栏隐藏/显示；从媒体库打开走模块播放器与查看器，导出存回当前文件夹；设计稿第 26、27 页 |
| 退出条件 | 设计稿第 26、27 页逐项对照通过；私密媒体不出现在“最近播放”、系统相册与多任务缩略图；导入失败逐项报告；分页边界正确；源文件仅在用户确认“删除原文件”时才删除 |

### VK-M8 VideoKit App 发布

| 项 | 内容 |
| --- | --- |
| 范围 | VideoKit App（`flutter/videokit_app`）以 VideoKit 模块为内核的正式版本：App 外壳（启动、导航、打开媒体入口、权限、设置、关于）、全部功能接真实模块、Release 构建（无 Fake、无演示资源）、签名与发布材料；SkinKit 宿主接入在 SkinKit v2.0 支持 Flutter 后另行安排 |
| 退出条件 | UI 逐页对照设计稿验收通过；App 只经公共 API 使用模块；Release 隔离检查通过；App 自身的测试与发布清单通过 |

VideoKit App 的外壳从 VK-M0 起与模块并行搭建（先接 Fake，随各里程碑接入真实能力），VK-M8 只做收尾与发布；App 需要的能力一律先补进模块公共 API。

## 3. 并行工作

| 并行项 | 时间 | 说明 |
| --- | --- | --- |
| 聚焦验证 S1–S5 | 与 VK-M0 并行 | S1、S2 在 VK-M1 前；S5 在 VK-M3 前；S3、S4 在 VK-M4 前（[15](15_MEDIA_TECHNOLOGY_DECISIONS.md) §4） |
| 跟踪 Spike（S6） | 与 VK-M0–M3 并行 | P0 风险最高，必须提早；结果决定 VK-M5 方案；含多人身份保持（09 §3） |
| 头像抠图验证（S7） | 与 S6 并行（2026-11-07 加入） | 候选模型的抠图质量、速度、许可；结果决定 VK-M5A 的头像准备方案（[15](15_MEDIA_TECHNOLOGY_DECISIONS.md) §2.9） |
| UI 设计稿修订 | 按需 | 以 V1.0 设计稿为基准；修订只更新 Token 与组件样式，不影响功能里程碑 |
| 测试样本补充 | VK-M0 起持续 | 按 [11](11_TEST_AND_ACCEPTANCE_PLAN.md) §4 缺口补充 |
| SkinKit 接入 | SkinKit v2.0 支持 Flutter 后，且自有 Theme 稳定、收到接口文档后 | 作为可选主题来源包 `videokit_theme_skinkit`（[03](03_UI_FRAMEWORK_DESIGN.md) §5.5），排期另定 |

里程碑并行的前提是公共 API 已评审冻结（原需求 §28）；跟踪与导出可在播放/图片之后并行开发。

## 3A. 角色与测试节奏（2026-11-07 用户确认）

| 角色 | 职责 |
| --- | --- |
| 负责人 | 设计与文档、派单、代码审查、缺陷裁定、提交与同步；需要用户决定的事项整理后提交用户 |
| coder | 按整批开发并自测，冻结后提交交付报告；问题集中汇总给负责人 |
| tester | 在冻结快照上独立做整包测试：全部自动化测试、按 UI 设计稿逐页验收、可访问性与国际化检查、补充用例；不修改产品代码；缺陷一次性汇总给负责人 |

原则：**集中开发 → 集中测试 → 集中反馈 → 集中修复**，测试等一批功能完成后再做，避免为小问题频繁往返。

- 测试轮次按“功能批”划分，一轮可以覆盖多个开发批；第一轮 = M0-B1（API / Fake / Theme 基础）+ M0-B2（首批 UI 组件）。
- tester 只测冻结快照：用 `git worktree` 检出到 `D:\CodexProjects\VideoKit test-workspace\verify\<轮次>`，不测 coder 正在修改的工作区。
- 缺陷由负责人裁定后整批交回 coder；修复后的回归随下一轮测试一起进行，除阻断问题外不单独开轮。
- 测试机分配前不做真机测试，相关项标 NOT_RUN。

### 3B. 开发先行、测试后补（2026-11-07 用户确认）

- VK-M0 开发完成后**直接继续开发 VK-M1、VK-M2**，不等待测试资源；有测试资源（测试机、tester）时再回头集中测试。
- 因此聚焦验证 S1、S2 暂不作为 VK-M1 的开工前置：M1 先按 [15](15_MEDIA_TECHNOLOGY_DECISIONS.md) 的“待验证”方案实现，S1/S2 有结果后若需调整，作为独立修正批处理。
- 每批仍要求：编译通过、JVM/主机侧测试通过、Fake 契约与 `spec` 向量通过；需要设备的项标 NOT_RUN，并写入 `D:\CodexProjects\VideoKit test-workspace\reports\PENDING_TESTS.md`（待测清单：里程碑、项目、需要的资源、对应需求编号），测试资源到位后按清单集中补测。
- 里程碑的“开发完成”与“验收通过”分开记录：未经真机与独立测试的里程碑只能标为“开发完成，待测”，不得写成通过。

## 4. 每个里程碑的交付物

1. 源码（Git commit）与构建产物（AAR、Flutter 包、`videokit_example` 与 `sample-host` APK）及 SHA-256。
2. 范围完成矩阵：每项 DONE / NOT_DONE；UI 接入矩阵：哪些界面已接真实实现、哪些仍为 Fake。
3. 自测结果与测试报告（[11](11_TEST_AND_ACCEPTANCE_PLAN.md) §6）。
4. 依赖变更、许可检查与 SBOM 更新。
5. 已知问题与不支持能力清单。
6. 已冻结的待定项与指标（[02](02_SYSTEM_ARCHITECTURE.md) §7）。

## 5. 后续版本

- 其他平台（iOS、macOS、Windows）：新增对应原生 Kit 与插件实现，复用同一套 Flutter UI 与 Dart API；范围与时间另立需求，当前不承诺。
