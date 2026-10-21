# VideoKit 开源框架技术与开发工作量节省估算

## 2026-10-21 国际化详细设计补充（当前有效）

依据[《VideoKit 国际化详细设计》](INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)及[国际化数据模型](INTERNATIONALIZATION_DATA_MODEL_V1.0.md)，首轮界面支持en/zh-Hans，SYSTEM/EXPLICIT切换与确定性script回退，资源离线完整；界面、字幕、识别、翻译四类语言分别设置，不隐式互改。UI localeGeneration不改变媒体generation/epoch，不重建播放或取消模型任务。

复用flutter_localizations/gen_l10n/intl，版本实施前固定，不采用any/latest。人工翻译审校与真实UI验收仍需完成，不把原节省估算改称实测。

仅文档更新，主阶段/原P0/冻结证据保持，项目PAUSED_WAITING_USER，D1未过/M0未启。

## 2026-10-21 最新播放子系统设计基线

2026-10-21 用户确认：播放复用 Media3/平台播放器，保留统一 PlaybackBackend 隔离平台实现，libmpv不再列正式选型/对照或计划内验证。识别独立模块优先验证whisper.cpp，翻译独立模块评估llama.cpp+适用模型并可替换，平台适配位于各能力底层。自有开发集中统一API/宿主输入/生命周期/预算/字幕时间轴/取消/Flutter UI与编排，不重造解码/音画同步/推理引擎。

新增语音/翻译模块需另做模型及设备评估，本次不编造节省百分比/工期，不把原25%–40%估算视为新增范围已覆盖。libmpv退出正式候选与对照。whisper.cpp/llama.cpp为复用验证方向，模型、二进制、性能仍未冻结。详见[《VideoKit 播放子系统详细设计》](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)。

本节覆盖下文相冲突的历史候选说明；原P0、冻结报告和历史证据保持。仅文档更新，项目继续暂停。

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。本条覆盖下文此前“暂不自建 Theme”“M0 必须实接 SkinKit”等旧要求；供应方资料与历史要求保留供将来评审，不作为当前强制任务。完整现行范围见 [Flutter Theme 与延后集成决定](FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前 D1 冻结任务不变，M0 未启动。


## M0 UI 优先实施要求（2026-10-20 最新）

用户最新决定（2026-10-20）：M0 在保留 API/Fake/TestKit/sample-host 原范围的同时，先搭建整个正式 Flutter App 的 UI 框架，按既有 18 页 PPT 的视觉与交互样式实现，并真实集成 SkinKit。允许生成带明确“演示模式·模拟数据”标识的本地测试数据演示全部主要页面与状态；演示不能冒充真实播放、跟踪或导出通过。后续 M1–M6 功能逐批实现并接回同一 UI，M7 保持独立宿主接入，M8 完成全功能真实集成与发布级验收，不再首次重建 UI。继续复用 SkinKit 默认/标准样式与合法最小宿主适配，不另建独立 Theme 系统、主题包或编辑器；通过既有配置与受支持的最小覆盖实现 PPT 样式，无法表达的差异列明评审。

完整范围与退出门槛：[M0 App UI 框架要求](M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md)。本次为规划更新；D1 尚未通过，M0 尚未启动，不改变已冻结候选或当前设备批次。


## SkinKit 第三方样式SDK补充（2026-10-20）

用户指定集成 SkinKit，并明确暂不新建自有 Theme。SkinKit是闭源商用SDK，不归入开源比例。复用既有Default/Contract/Core，不新建主题，仍需Flutter桥接/宿主接线/真实验收；现有工时估算未含此项，不虚构节省百分比。

完整要求与测试见 [SKINKIT_INTEGRATION_REQUIREMENTS_V1.0.md](SKINKIT_INTEGRATION_REQUIREMENTS_V1.0.md)，UI映射见 [补充说明](ui/VIDEOKIT_SKINKIT_UI_MAPPING_V1.0.md)。M8 [coder](milestones/VK_M8_SKINKIT_CODER_REQUIREMENTS_V1.0.md) / [tester](milestones/VK_M8_SKINKIT_TESTER_REQUIREMENTS_V1.0.md)工作单为未来阶段要求，当前仅文档更新，实际集成与测试NOT_RUN。SDK1.1.0无通用Flutter/Apple/桌面Adapter；正式许可适用/主体/获取/分发权待核，不称已通过。

版本：V1.0  
日期：2026-10-05  
用途：系统开发参考文件  
状态：初步选型与工程估算，非已冻结依赖清单或工期承诺

初步估计，合理复用开源组件可以减少约 **25%～40% 的整体开发与测试人力**。目前只有 Flutter 已确定，其他组件需要通过许可证和技术验证后冻结。

以下百分比是工程估算，表示对应模块相对自行实现同等能力的净节省，已考虑接入、适配和测试成本；不是项目实测数据，也不能直接相加。官方链接支持组件能力和许可证说明，不支持本项目的节省百分比；百分比由需求助理估算。

## 1. 开源框架与组件清单

| 开源框架／组件 | 使用位置与用途 | 许可证初筛 | 当前选择状态 | 对应模块预计节省 |
| --- | --- | --- | --- | --- |
| [Flutter](https://docs.flutter.dev/resources/faq) | 四平台 App UI、手机／平板布局、手势、窗口与无障碍基础 | 框架 BSD-3-Clause；依赖另审 | **已确定** | 四平台 UI：**35%～55%** |
| [flutter_localizations、gen_l10n、intl](https://docs.flutter.dev/ui/internationalization) | 多语言资源、复数、日期数字格式、RTL 基础 | Flutter 许可；[intl 为 BSD-3-Clause](https://pub.dev/packages/intl/license) | 计划采用 | 国际化基础设施：**50%～70%**，不含翻译与语言验收 |
| [AndroidX Media3 ExoPlayer](https://github.com/androidx/media) | Android 播放、音轨、字幕、倍速、Seek；包装为独立 Kit | Apache-2.0；扩展依赖另审 | 首选 | Android 播放模块：**40%～60%** |
| [Media3 Transformer／Composition](https://developer.android.com/media/media3/transformer/composition) | Android 裁剪、片段重排、拼接、效果与编码导出 | Apache-2.0 | 首选，需验证输入与 Sink | Android 编辑导出管线：**25%～45%** |
| [Coil](https://github.com/coil-kt/coil) | Android 图片加载、缓存及图片 UI 接入 | Apache-2.0 | 候选 | Android 图片模块：**25%～45%** |
| [SDWebImage](https://github.com/SDWebImage/SDWebImage) | iOS／macOS 图片缓存、动画与格式扩展 | MIT；格式插件另审 | 候选 | Apple 图片模块：**25%～45%** |
| [OpenCV](https://opencv.org/license/) | 图像预处理、几何变换、传统跟踪及效果辅助 | 4.5+ Apache-2.0；具体模块另审 | 首选验证 | 图像处理／跟踪基础：**30%～50%** |
| [YuNet](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet) | 人脸检测，供用户选择打码目标 | 对应目录 MIT；模型来源权利继续核查 | 模型候选 | 人脸检测子模块：**60%～80%**，不代表人脸跟踪完成 |
| [ViTTrack](https://github.com/opencv/opencv_zoo/tree/main/models/object_tracking_vittrack) | 用户指定物体的基础跟踪 | 对应目录 Apache-2.0；模型来源权利继续核查 | 模型候选 | 物体跟踪整体模块：**20%～40%** |
| [ONNX Runtime](https://github.com/microsoft/onnxruntime) | 跨平台运行模型，评估设备加速 | MIT；执行后端依赖另审 | 与 OpenCV DNN 对照选择 | 推理接入与优化：**30%～50%** |
| [media_kit 的 MIT 控件代码](https://github.com/media-kit/media-kit) | 合法复用播放控制交互，改接 VideoKit API | Dart 框架 MIT；底层原生库另审 | 选择性复用候选 | 播放控件子模块：**15%～30%** |

Coil、SDWebImage 等图片库仍需验证动态图暂停、大图分块和各格式支持；现成模型也不会自动解决多目标、遮挡重关联、人工纠正和漏码检查。

## 2. 其他重要技术

以下技术不应算作开源框架：

| 技术 | 用途 |
| --- | --- |
| Apple AVFoundation／ImageIO | iOS、macOS 的系统播放、图片与编辑能力 |
| Windows Media Foundation／WIC | Windows 的系统媒体处理与图片能力 |
| C++／C ABI | 共享领域内核及原生绑定的实现方式 |

它们能够减少底层开发，但仍需要平台适配和完整验收。

## 3. 整体节省估算

按相同功能、相同质量标准比较：

| 范围 | 预计净减少人力 |
| --- | --- |
| Android Kit + App，包含手机／平板、编辑、多画面和国际化 | **20%～35%** |
| 完整四平台 Kit + App V1.0 | **25%～40%** |

例如，某份经拆解估算为 **100 人周**的工作，复用后可能降到 **60～75 人周**。这是比例示例，不是当前项目工期承诺。

上述范围用于分别评估 Android 工作与完整四平台工作，不代表拆分为不同功能版本。项目仍按用户确认的原则，在同一个完整 V1.0 中依次完成全部需求功能。

## 4. 仍需自行完成的工作

剩余工作主要集中在本项目的特有要求：

- 宿主随机读取与媒体租约。
- 统一公共 API 与平台绑定。
- 多实例资源预算与唯一音频。
- 编辑 UI 与安全 OutputSink。
- 跟踪纠正与漏码验收。
- 手机／平板及四平台适配。
- 国际化文案、翻译与语言验收。

这些要求决定了不能把成熟组件拼起来就视为产品完成。App 使用 Flutter，展示编辑入口和多画面 UI；Kit 全部 P0 不因组件能力或估算而弱化。

## 5. 暂不计入节省量的方案

libmpv、libVLC、FFmpeg 和 MDK 暂不计入节省量：它们尚未获准采用，也未完成实际构建与分发许可审查。

完成首轮技术验证后，才能把以上范围进一步收敛为可靠的人周估算。届时结合固定依赖版本、真实设备、模型权利、输入／输出适配结果和质量验收数据重新估算；开发人力节省不等于按同一比例缩短日历工期。

## 6. 关联开发文件

- [立项需求与范围](PRODUCT_REQUIREMENTS_V1.0.md)
- [系统架构](SYSTEM_ARCHITECTURE_V1.0.md)
- [App 整体架构](VIDEOKIT_APP_ARCHITECTURE_V1.0.md)
- [开源与许可证计划](OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md)
- [自动跟踪技术验证计划](TRACKING_TECHNICAL_SPIKE_V1.0.md)
- [测试与验收计划](TEST_AND_ACCEPTANCE_PLAN_V1.0.md)
- [里程碑](MILESTONES_V1.0.md)

本文件记录此次讨论的组件清单与估算，未批准大规模产品编码，也不替代需求基线和设计评审。
