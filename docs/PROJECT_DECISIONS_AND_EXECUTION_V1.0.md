# 项目决定与执行基线

## 2026-10-21 国际化详细设计补充（当前有效）

依据[《VideoKit 国际化详细设计》](INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)及[国际化数据模型](INTERNATIONALIZATION_DATA_MODEL_V1.0.md)，首轮界面支持en/zh-Hans，SYSTEM/EXPLICIT切换与确定性script回退，资源离线完整；界面、字幕、识别、翻译四类语言分别设置，不隐式互改。UI localeGeneration不改变媒体generation/epoch，不重建播放或取消模型任务。

用户授权仅设计/文档更新，不恢复coder/tester、补测/设备/安装依赖或自动跟进。

仅文档更新，主阶段/原P0/冻结证据保持，项目PAUSED_WAITING_USER，D1未过/M0未启。

## 2026-10-21 最新播放子系统设计基线

2026-10-21 用户确认：播放复用 Media3/平台播放器，保留统一 PlaybackBackend 隔离平台实现，libmpv不再列正式选型/对照或计划内验证。识别独立模块优先验证whisper.cpp，翻译独立模块评估llama.cpp+适用模型并可替换，平台适配位于各能力底层。自有开发集中统一API/宿主输入/生命周期/预算/字幕时间轴/取消/Flutter UI与编排，不重造解码/音画同步/推理引擎。

用户授权本次设计/文档更新；项目PAUSED_WAITING_USER保持，不通知coder/tester恢复、不开发/测试/设备/安装依赖、不重建自动跟进。D1未通过、M0未启。主里程碑不变，播放按[《VideoKit 播放子系统详细设计》](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)拆阶段内子任务/验收，见[映射](PLAYBACK_MILESTONE_MAPPING_V1.0.md)。

本节为当前设计；被撤销指令已从执行正文移出，修改前原文见history/design/2026-10-21-consolidation/。历史证据保持，项目继续暂停。

> 2026-10-20 最新用户要求：设备占用不再让双方停工。正式派D1_INPUT_SINK01：coder在新目录集中开发实际Media3 DataSource/宿主readAt与临时Sink薄适配及有限本机验证；tester并行只测已冻结读取桥/Sink基线并准备独立回归，不审浮动源码、不并发Gradle。完整新包冻结后再整包审查/集中修复。详见OFFLINE_PROGRESS_DURING_DEVICE_WAIT及独立CODER/TESTER需求。旧设备scope停止、候选与UNKNOWN不改，真机门仍等待准确安排，D1未过M0未启。


## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。旧SkinKit实接与禁止自有Theme要求已归档，不作为当前任务；未来仅在正式Flutter支持和新批准范围下评估。完整现行范围见 [Flutter Theme 与延后集成决定](FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；D1未通过、M0未启动；当前项目暂停。


## M0 起交付批次规则（2026-10-20）

负责人每批选择 1–3 个完整里程碑并向用户汇报范围与理由；coder 整批开发、自测、冻结后统一交 tester，tester 整批测试并集中报告，缺陷集中回交修复及回归。阶段需求与验收分栏保留，禁止逐问题反复交接，不以合批冒充阶段通过。详见 [协调规则](MILESTONE_COORDINATION_V1.0.md)。此规则覆盖下文单里程碑立即交测的冲突表述，当前 D1 及 M0 未启动状态不变。


## 1. 授权与已确认决定

用户已同意 M0 前确认表中的建议，并授权需求助理负责项目实现方式、过程和必要沟通。常规架构细化、实现、测试与修复不重复请求批准；需要用户设备操作、外部付费授权、不可逆发布或需求范围改变时及时沟通。授权不表示技术验证已通过，也不自动批准不清许可组件。

Flutter 为正式 App UI，包含编辑入口与多画面 UI；Android 支持手机/平板、API31+；多语言首轮资源为简体中文与英文，保留扩展语言、RTL、长文本和大字体适配。Kit 全部 P0 保留，按里程碑顺序完成同一完整 V1.0，不发布功能删减版本。

## 2. 当前阶段边界

恢复后仍只按已批准Android范围开发/构建/实测；当前暂停不执行。Windows、iOS、macOS 保留为总体目标，但目前只做架构和技术兼容性分析，不开发其实现或以缺少 Apple/Windows 真机阻断 Android M0。跨平台未实现能力标记 NOT_RUN，不能宣称已支持。

先进行 Android D1：随机读取与取消、输出 Sink、格式/轨道、跟踪权利与可行性、资源预算及故障隔离验证。D0 方向视为用户认可；细节由项目负责人记录，M0 基础契约只有在有关验证通过后才冻结。跟踪效果、性能和设备门禁不能以此次授权代替实际验收。

后续桌面与 Apple 实现何时启动，根据用户安排更新执行计划；四平台目标和 Kit 公共边界保持不变。当前不要求一次完成四平台实现，也不因此弱化 Android 的任何 P0。

## 3. 实施决定

| 项目 | 决定 | 状态 |
| --- | --- | --- |
| UI | Flutter App；SDK 原生无 UI 可独立调用，Compose/View 为可选原生 UI | 已确认路线，具体桥接待验证 |
| 共享模型 | C++ 共享时间线/变换/编辑计划、稳定 C ABI；原生播放状态单一权威 | 已采纳，避免 M0 同时维护两套播放状态 |
| Android 后端 | 确定Media3，图片与跟踪按许可和技术结果选择 | 已确定路线；候选已有锁定各自保留，正式发行另准入 |
| SDK 分包 | api/core/playback/image/ui/timeline/effects/tracking/export/testkit 与薄后端 | M0 模块边界，具体依赖图记录后冻结 |
| 命名 | 内部 Maven group `com.videokit`；SDK namespace `com.videokit.<module>`；保留 App `com.videokit.app` | 项目内部决定，不声称拥有外部域名/商标 |
| 分发 | 首先受控本地 Maven 仓库，API 与可选 AAR 分发，语义版本 | 已采纳，不自动上传公开仓库 |
| 输出 | MP4/H.264/AAC/SDR 为首轮验证预设 | 验证候选，不承诺任意设备可编码 |
| 许可 | 优先 MIT/BSD/Apache；FFmpeg/LGPL/商业引擎按许可计划单独审查 | 不自动引入或购买 |

## 4. 测试资源（暂停期间不操作）

样本目录test_media只读，不能覆盖/改名/删除、不打包上传；语料格式/动画/标注覆盖以实际manifest与授权为准，不从存在后缀推断覆盖。用户持续真机一般授权保留，但当前不查ADB/占用/设备。恢复后需负责人准确新批次/fresh身份与空闲门；其他项目占用稍后再试，不操作其他项目或连续轮询。设备物理状态只由将来准确检查证明，不沿用历史“已连接/恢复手机”等指令。

Android12手机/平板与其他平台设备差异按原阶段矩阵；Apple/Windows当前不开发实测，归M9。历史连接/延期与样本枚举记录完整归档，保留其时间点事实，不作为当前派单。

## 5. 用户恢复后的工作与沟通方式

用户进一步要求负责人协调现有 VideoKit coder/tester，为每个里程碑分别提供开发和测试需求。coder完整完成并自检后整包交接，编译按功能批次集中执行，tester集中验收、批次反馈与修复回归。最新流程及全部需求文件见 [里程碑协调规则](MILESTONE_COORDINATION_V1.0.md)。

用户明确恢复后，先审已得完整结果和剩余D1门，再安排准确范围；D1未过不能冻结其未证部分或进入M0。每个阶段报告实际完成、测试证据、失败和下一步；文档写完不等于功能完成。

重大设计变更保留决定与原因；P0 不得自行删除。需要手机/平板操作时明确说明设备、测试内容与操作步骤。不会因 Windows/Apple 当前未开发而反复要求用户提供这些环境。

## 当前唯一状态与归档

[当前设计基线](CURRENT_DESIGN_BASELINE_V1.0.md)为设计状态入口，[协调规则](MILESTONE_COORDINATION_V1.0.md)为未来恢复工作流。旧时间点“当前工作/推进”不构成暂停期间派发；历史原文完整归档。新增接口/模型/指标仍需阶段冻结，不替代原D1结果。
