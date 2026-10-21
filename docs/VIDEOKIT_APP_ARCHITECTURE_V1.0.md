# VideoKit App 整体架构技术方案

## 2026-10-21 国际化详细设计补充（当前有效）

App shell增加LocaleController与LanguageSettingsRepository逻辑职责，使用Flutter成熟localizations/gen_l10n/intl及ARB，不自造资源引擎。界面SYSTEM/EXPLICIT、运行时最新切换、离线资源/原子偏好与UI错误映射按[《VideoKit 国际化详细设计》](INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)。四域设置互不隐式联动；保持页面草稿/焦点/播放状态。系统弹窗语言由系统决定，不能宣称随App手选即时切换。

本次仅文档更新，项目继续暂停；主里程碑、原P0与历史冻结证据保持，D1未过/M0未启。

## 2026-10-21 最新播放子系统设计基线

2026-10-21 用户确认：播放复用 Media3/平台播放器，保留统一 PlaybackBackend 隔离平台实现，libmpv不再列正式选型/对照或计划内验证。识别独立模块优先验证whisper.cpp，翻译独立模块评估llama.cpp+适用模型并可替换，平台适配位于各能力底层。自有开发集中统一API/宿主输入/生命周期/预算/字幕时间轴/取消/Flutter UI与编排，不重造解码/音画同步/推理引擎。

App字幕/识别/翻译页面通过公共SDK能力、状态和任务接口，模型/缓存/下载授权在独立扩展与宿主层协作，不让UI调用具体推理库。帧与PCM不按块跨Dart来回传。Flutter自有VideoKit Theme保持，SkinKit延后。详见[《VideoKit 播放子系统详细设计》](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)及[模型](PLAYBACK_DATA_MODEL_V1.0.md)。

本节为当前设计；被撤销指令已从执行正文移出，修改前原文见history/design/2026-10-21-consolidation/。历史证据保持，项目继续暂停。

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。旧SkinKit实接与禁止自有Theme要求已归档，不作为当前任务；未来仅在正式Flutter支持和新批准范围下评估。完整现行范围见 [Flutter Theme 与延后集成决定](FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；D1未通过、M0未启动；当前项目暂停。


## 1. 产品与平台目标

VideoKit App 为 Android/iOS/macOS/Windows 本地视频和图片播放器。LocalVideosBrowser 为本地/HTTPS/NAS 综合播放器，未来同样四平台上架；本设计约束 Kit 能被它的原生或跨平台 UI 独立调用，但不替它决定技术栈。Android 原生接入是当前必须满足的契约。

Kit 是可独立发行的 SDK，不直接“上架应用商店”；真正上架的是 VideoKit App 与 LocalVideosBrowser。SDK 在两个应用的商店发行中都必须满足许可、隐私、资源和兼容要求。用户已确认 App 使用 Flutter、展示编辑入口与多画面 UI，全部需求功能按顺序完成于一个完整 V1.0，不划分功能不同的发布版本。

App 简单不等于 Kit 简化：Kit 的视频/图片、多实例、编辑、打码、人脸/物体跟踪、安全导出全部 P0 保留。App V1.0 提供编辑入口和多画面 UI，并连接相应 Kit 能力；示例宿主必须能验证全部 Kit 能力。

## 2. 首选技术组合

Flutter：App 页面、控件、设置、触摸/键盘/窗口适配；C++：共享时间线、变换、遮罩与编辑计划；Kotlin/Swift/C++：平台会话、媒体后端、资源与输入/输出。Android 首选 Media3；Apple 首选 AVFoundation；Windows 原生后端评估 Media Foundation。OpenCV 与有许可的模型优先复用，ORT 为推理备选。

不是从零造四套媒体引擎：复用成熟库和平台能力，自己开发统一契约、安全管线与需求缺口。跨平台模型和计划共享，平台加速和纹理单独适配。原生后端缺格式/字幕时，先在Media3/平台路线内记录并评审缺口，不默认引入替代后端；libmpv不再列正式候选或对照。

Flutter 已由用户确认，优势是四平台页面/交互共享；代价是 Kit 外需要维护 Flutter binding 和原生宿主 UI adapter。现有仓库为 Compose 骨架，后续迁移方案仍需评审；Spike 验证多实例渲染、原生接入、编辑时间线、包大小和无障碍，不再用于重新选择 App UI 技术栈。本轮不迁移仓库。

## 3. App 内部模块

| 模块 | 功能 | 与 Kit 边界 |
| --- | --- | --- |
| app-shell | 启动、窗口、路由、主题、中英及许可证页 | 不执行解码/跟踪 |
| local-source | 系统文件选择、权限租约、只读句柄 | App 作为普通宿主提供 SourceFactory |
| player-screen | 单媒体控件、变换、轨道、快捷键 | 使用 Kit state/command/controlsVisible |
| image-screen | 静态/动态图查看与导航 | 仍使用同一种会话，不显示视频控件 |
| recent/settings | 最近文件、媒体偏好和产品设置 | 只持久化 App 自己的状态，不写入 Kit |
| editor-screen | 时间线、目标选择、纠正、导出 | 完全复用 Kit 的编辑工程/效果/跟踪/导出 |
| multi-view-screen | 多画面布局、独立槽位、声音选择、可见性与降级 | App 作为宿主编排独立 Kit 会话，不依赖 VideoBox 业务 |
| local-output | 用户保存位置、临时文件、验证及最终提交 | 提供 Sink；原件默认保持不变 |
| videokit-binding | 原生 SDK/texture/事件桥接 | 不嵌入 Browser 类型或 NAS 认证 |

## 4. UI 与资源

手机优先沉浸播放，平板允许控制面板，桌面支持文件拖入、鼠标、键盘和窗口尺寸变化；默认控件不固定上一/下一，App 自有导航通过通用宿主回调。多实例能力来自 Kit；App V1.0 展示多画面 UI，宿主层编排布局、唯一声音来源和能力不足时的降级。

视频帧不经 Dart ByteArray 逐帧搬运；使用 Flutter texture/适用平台显示目标。高频播放位置合并，HostAction/error/release 保持顺序。播放 UI 不包含商业后端名、构建参数或实现异常。

原生 Kit UI 分离为可选 artifact；可复用 media_kit MIT 控件的合法交互实现，但须清除其对直接 libmpv 操作和单例语义的依赖。复用记录精确 commit/license/patch；不从 GPL App 复制代码或素材。

## 5. 数据与文件安全

App 自己保存最近打开和 PlaybackSnapshot，工程通过独立 repository 保存。稳定本地身份不只用绝对路径；权限失效时提示重新选择。Android SAF/Content URI、Apple security-scoped 文件访问、Windows 授权句柄均在 App 层处理，Kit只读句柄。

导出目标由 App 的 local-output 宿主模块提供临时 Sink；Kit 完成后 App 重新验证并让用户保存新文件。用户选择与源同名目标时也不得绕过只读源规则。默认本机处理、无媒体上传、无永久人脸库与操作日志；模型更新另作产品/商店方案，不能默认联网。

## 6. 四平台上架

各平台独立编译/签名/商店测试，Apple 在 macOS 构建并真机验证；当前 Windows 工作区不能证明 Apple 构建通过。分别输出自己的 SBOM、NOTICE、权限、隐私资料与依赖 hash。商店政策按提交时最新官方规则复核，不承诺草案即可通过审核。

SDK 二进制版本与 App 版本分开。App CI 引用已发布 SDK；源代码联调为明确开发配置，不使日常 UI 改动重编全部媒体/AI。Android sample-host 保留为验收工具，不直接改名冒充完整四平台 App。

## 7. 当前决定与待冻结项

App Flutter、编辑入口、多画面 UI 及一个完整 V1.0 的范围已确认。共享内核、平台后端、具体版本及高风险 Spike 仍等待设计评审。后续需讨论：格式不足时是否允许审查 LGPL 构建、是否接受商业授权费用；四平台最低 OS/CPU、实现顺序与商店提交安排。商店提交可受各平台流程影响，但不据此拆成功能删减的不同版本。

不需要重新确认已经确定的闭源、四平台、P0 和宿主业务隔离；未决定的数值和后端保持显式待定。完整决策/风险见 [系统架构](SYSTEM_ARCHITECTURE_V1.0.md)、[里程碑](MILESTONES_V1.0.md) 和 [许可计划](OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md)。

## 集中整理后的执行依据（2026-10-21）

[NATIVE_BINDING_AND_MODULE_BOUNDARIES](NATIVE_BINDING_AND_MODULE_BOUNDARIES_V1.0.md)；[API_DATA_CONTRACT](API_DATA_CONTRACT_V1.0.md)。

以上补充现有职责、接口和验收追踪，不新增主阶段或删除原P0。历史设计原文已归档，不再作为并行指令；当前项目暂停，不能以本文触发开发测试。
