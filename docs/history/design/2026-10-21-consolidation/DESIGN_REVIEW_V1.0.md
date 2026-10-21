# VideoKit 设计评审入口

## 2026-10-21 国际化详细设计补充（当前有效）

依据[《VideoKit 国际化详细设计》](INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)及[国际化数据模型](INTERNATIONALIZATION_DATA_MODEL_V1.0.md)，首轮界面支持en/zh-Hans，SYSTEM/EXPLICIT切换与确定性script回退，资源离线完整；界面、字幕、识别、翻译四类语言分别设置，不隐式互改。UI localeGeneration不改变媒体generation/epoch，不重建播放或取消模型任务。

评审核四域隔离、script回退、切换事务与原子偏好、语言中立错误、RTL媒体语义和I18N-01–15。具体SDK/资源清单/存储实现/人工术语审校实施前冻结。

仅文档更新，主阶段/原P0/冻结证据保持，项目PAUSED_WAITING_USER，D1未过/M0未启。

## 2026-10-21 最新播放子系统设计基线

新增技术评审入口：[《VideoKit 播放子系统详细设计》](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)、[播放数据模型](PLAYBACK_DATA_MODEL_V1.0.md)、[播放阶段映射](PLAYBACK_MILESTONE_MAPPING_V1.0.md)。用户已确认Media3/平台路线、取消libmpv候选、ASR独立/能力底层适配、whisper.cpp优先和llama.cpp可替换评估。仍需冻结具体接口/模型/性能预算与扩展实施阶段；不把设计完成代当前D1退出。

本节覆盖下文相冲突的历史候选说明；原P0、冻结报告和历史证据保持。仅文档更新，项目继续暂停。

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。本条覆盖下文此前“暂不自建 Theme”“M0 必须实接 SkinKit”等旧要求；供应方资料与历史要求保留供将来评审，不作为当前强制任务。完整现行范围见 [Flutter Theme 与延后集成决定](FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前 D1 冻结任务不变，M0 未启动。


## M0 UI 优先实施要求（2026-10-20 最新）

用户最新决定（2026-10-20）：M0 在保留 API/Fake/TestKit/sample-host 原范围的同时，先搭建整个正式 Flutter App 的 UI 框架，按既有 18 页 PPT 的视觉与交互样式实现，并真实集成 SkinKit。允许生成带明确“演示模式·模拟数据”标识的本地测试数据演示全部主要页面与状态；演示不能冒充真实播放、跟踪或导出通过。后续 M1–M6 功能逐批实现并接回同一 UI，M7 保持独立宿主接入，M8 完成全功能真实集成与发布级验收，不再首次重建 UI。继续复用 SkinKit 默认/标准样式与合法最小宿主适配，不另建独立 Theme 系统、主题包或编辑器；通过既有配置与受支持的最小覆盖实现 PPT 样式，无法表达的差异列明评审。

完整范围与退出门槛：[M0 App UI 框架要求](M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md)。本次为规划更新；D1 尚未通过，M0 尚未启动，不改变已冻结候选或当前设备批次。


## SkinKit 评审入口补充（2026-10-20）

用户指定集成 SkinKit，并明确暂不新建自有 Theme。需要核Flutter宿主桥接、既有默认/标准主题复用、四级回退、独立核心、未交付平台Adapter及正式商用权利。PPT仅交互结构参考，不要求移植自拟配色成自有Theme。

完整要求与测试见 [SKINKIT_INTEGRATION_REQUIREMENTS_V1.0.md](SKINKIT_INTEGRATION_REQUIREMENTS_V1.0.md)，UI映射见 [补充说明](ui/VIDEOKIT_SKINKIT_UI_MAPPING_V1.0.md)。M8 [coder](milestones/VK_M8_SKINKIT_CODER_REQUIREMENTS_V1.0.md) / [tester](milestones/VK_M8_SKINKIT_TESTER_REQUIREMENTS_V1.0.md)工作单为未来阶段要求，当前仅文档更新，实际集成与测试NOT_RUN。SDK1.1.0无通用Flutter/Apple/桌面Adapter；正式许可适用/主体/获取/分发权待核，不称已通过。

## 最新执行决定（2026-10-05）

用户已同意 M0 前确认表的建议，并授权项目负责人自行推进实现与过程；当前只开发 Android，Apple/Windows 仅做设计兼容性分析。具体决定与测试资源见项目决定文件。

[项目决定与执行基线](PROJECT_DECISIONS_AND_EXECUTION_V1.0.md)为最新执行约束，优先于下文旧稿中相冲突的跨平台验证时点或待用户确认表述。


日期：2026-10-05；版本：V1.0；状态：草案，等待用户讨论/评审。

原始 [需求基线](VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md) 条款保留，2026-10-20 已追加用户指定的 SkinKit 集成补充，未删除原 P0。四平台、闭源和优先合法开源复用的补充已纳入以下文档，原始 P0 未降级。用户已确认 App 使用 Flutter、展示编辑入口与多画面 UI；全部需求功能按顺序完成于一个完整 V1.0。文档 V1.0 表示此次评审稿的版本号，不代表整体设计已批准或产品已实现。

## 文档清单

[每阶段开发/测试需求与协调规则](MILESTONE_COORDINATION_V1.0.md)已提供，包含D1、M0–M10共24份需求。当前只派发Android D1，Apple/Windows实现阶段暂不启动。

| 文档 | 评审主题 |
| --- | --- |
| [PRODUCT_REQUIREMENTS](PRODUCT_REQUIREMENTS_V1.0.md) | 基线、平台与 P0 追踪 |
| [SYSTEM_ARCHITECTURE](SYSTEM_ARCHITECTURE_V1.0.md) | 分层、平台后端、资源与故障隔离 |
| [PUBLIC_API_CONTRACT](PUBLIC_API_CONTRACT_V1.0.md) | 输入、命令、状态、输出与版本 |
| [LOCALVIDEOBROWSER_INTEGRATION](LOCALVIDEOBROWSER_INTEGRATION_V1.0.md) | 无凭据随机读、租约、scope、HostAction 与回退 |
| [PLAYBACK_AND_IMAGE_DESIGN](PLAYBACK_AND_IMAGE_DESIGN_V1.0.md) | 播放/图片、变换、并发与格式 |
| [EDIT_TIMELINE_AND_EXPORT_DESIGN](EDIT_TIMELINE_AND_EXPORT_DESIGN_V1.0.md) | 时间线、拼接、打码、安全 Sink |
| [TRACKING_TECHNICAL_SPIKE](TRACKING_TECHNICAL_SPIKE_V1.0.md) | 检测/跟踪复用、模型权利与效果实验 |
| [OPEN_SOURCE_AND_LICENSE_PLAN](OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md) | 候选许可、再链接、供应链及商店发行 |
| [TEST_AND_ACCEPTANCE_PLAN](TEST_AND_ACCEPTANCE_PLAN_V1.0.md) | Fake/真实/真机/安全/跟踪验收 |
| [MILESTONES](MILESTONES_V1.0.md) | 第 29 节十二项冻结、开发门禁 |
| [VIDEOKIT_APP_ARCHITECTURE](VIDEOKIT_APP_ARCHITECTURE_V1.0.md) | 正式 App 四平台整体方案 |

## 需要先评审的风险

1. 原生媒体后端不保证所有容器与字幕能力，兼容后端尚未批准。
2. 自定义随机输入及临时 Sink 能否贯通 Media3/Apple/Windows 全链路，不能靠隐藏下载绕过契约。
3. 代码/目录许可不等于模型训练来源权利完整，自动跟踪质量尚未证明。
4. 原生崩溃不是普通异常，Apple 与 Android/Windows 的隔离边界不同。
5. App Flutter 已确认；Flutter UI 与原生 Kit UI 的绑定、视图维护成本及纹理/多实例集成仍需验证。

## 本轮实际交付

仅设计文档和官方来源初筛；未修改 Android 产品代码或构建；未运行性能/跟踪/跨平台编译；未冻结依赖版本；未取得任何商业引擎新授权；未启动 coder/tester 开发。草案可讨论不等于完成技术验证或批准发行。
