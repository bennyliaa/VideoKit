# VideoKit 立项需求基线与范围

## 2026-10-21 国际化详细设计补充（当前有效）

依据[《VideoKit 国际化详细设计》](INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)及[国际化数据模型](INTERNATIONALIZATION_DATA_MODEL_V1.0.md)，首轮界面支持en/zh-Hans，SYSTEM/EXPLICIT切换与确定性script回退，资源离线完整；界面、字幕、识别、翻译四类语言分别设置，不隐式互改。UI localeGeneration不改变媒体generation/epoch，不重建播放或取消模型任务。

国际化补齐运行切换/偏好失败/原子保存/资源/RTL/无障碍。繁体及其他UI语言、模型语言不自动成为交付承诺。在线翻译默认关闭，不自动上传内容。

仅文档更新，主阶段/原P0/冻结证据保持，项目PAUSED_WAITING_USER，D1未过/M0未启。

## 2026-10-21 最新播放子系统设计基线

2026-10-21 用户确认：播放复用 Media3/平台播放器，保留统一 PlaybackBackend 隔离平台实现，libmpv不再列正式选型/对照或计划内验证。识别独立模块优先验证whisper.cpp，翻译独立模块评估llama.cpp+适用模型并可替换，平台适配位于各能力底层。自有开发集中统一API/宿主输入/生命周期/预算/字幕时间轴/取消/Flutter UI与编排，不重造解码/音画同步/推理引擎。

原P0不减；ASR/翻译新增为独立扩展规划，尚未指定原D1/M1必过或某版本强制上线。在线翻译只留可选接口，默认关闭，不自动上传文本/音频，本机处理基线不因模型失败偷偷改变。详见[《VideoKit 播放子系统详细设计》](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)及[阶段映射](PLAYBACK_MILESTONE_MAPPING_V1.0.md)。

本节覆盖下文相冲突的历史候选说明；原P0、冻结报告和历史证据保持。仅文档更新，项目继续暂停。

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。本条覆盖下文此前“暂不自建 Theme”“M0 必须实接 SkinKit”等旧要求；供应方资料与历史要求保留供将来评审，不作为当前强制任务。完整现行范围见 [Flutter Theme 与延后集成决定](FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前 D1 冻结任务不变，M0 未启动。


## M0 UI 优先实施要求（2026-10-20 最新）

用户最新决定（2026-10-20）：M0 在保留 API/Fake/TestKit/sample-host 原范围的同时，先搭建整个正式 Flutter App 的 UI 框架，按既有 18 页 PPT 的视觉与交互样式实现，并真实集成 SkinKit。允许生成带明确“演示模式·模拟数据”标识的本地测试数据演示全部主要页面与状态；演示不能冒充真实播放、跟踪或导出通过。后续 M1–M6 功能逐批实现并接回同一 UI，M7 保持独立宿主接入，M8 完成全功能真实集成与发布级验收，不再首次重建 UI。继续复用 SkinKit 默认/标准样式与合法最小宿主适配，不另建独立 Theme 系统、主题包或编辑器；通过既有配置与受支持的最小覆盖实现 PPT 样式，无法表达的差异列明评审。

完整范围与退出门槛：[M0 App UI 框架要求](M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md)。本次为规划更新；D1 尚未通过，M0 尚未启动，不改变已冻结候选或当前设备批次。



## SkinKit App 外观集成补充（2026-10-20）

正式 VideoKit App 必须集成 SkinKit，完整要求与追踪见 [SK-01–20](SKINKIT_INTEGRATION_REQUIREMENTS_V1.0.md)。永久默认Light/Dark、跟随系统/手选、真实统一Provider和Flutter适配、Core本地主题校验/预览/显式应用/恢复默认、四级回退与离线可用纳入完整V1.0。全部关键页面/业务状态覆盖；皮肤不控制导航/播放/导出，核心及Browser不强制引入主题依赖。

供应方当前为JVM/Android Views闭源SDK，不能假称已有Flutter/四平台组件。只提供二进制不等于许可核验完成，发布仍受主体/版本/获取/分发权与传递依赖门约束。商店/支付/社区/创作/动画等可选模块不自动转为新产品需求。SK测试见 [矩阵](SKINKIT_INTEGRATION_REQUIREMENTS_V1.0.md#8-验收矩阵)，现均NOT_RUN。

## 最新执行决定（2026-10-05）

当前实施范围更新：先开发和实测 Android；Windows/iOS/macOS 只做架构与技术兼容性分析，暂不开发。四平台总体目标保留，详见项目决定文件。

[项目决定与执行基线](PROJECT_DECISIONS_AND_EXECUTION_V1.0.md)为最新执行约束，优先于下文旧稿中相冲突的跨平台验证时点或待用户确认表述。


版本：V1.0；日期：2026-10-05；状态：设计评审草案，未批准实现。

## 1. 基线与变更优先级

原始基线为 [用户需求 v1.0](VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)，31 节全部有效。本文件补充范围与追踪，不替代或删减原文。

用户最新指令补充：VideoKit、VideoKit App 和 LocalVideosBrowser 面向 Android、iOS、macOS、Windows 商店发行；在许可允许范围内优先复用开源组件及合法二次开发。Android 12/API 31 是首个正式交付平台，不能据此将另外三个平台从架构目标删除。四平台发布日期与最低系统版本另行评审，不自行承诺同时上线。

产品仍为闭源。原文第 23 节禁止 GPL/AGPL/SSPL 或许可不明代码进入产品；FFmpeg 不得未经批准默认集成。此前libmpv候选建议已于2026-10-21撤销，不列正式选型、对照候选或计划内验证。

## 2. 三个交付对象

| 对象 | 所有权与职责 | 不承担的业务 |
| --- | --- | --- |
| VideoKit 原生 SDK | 视频/静态及动态图会话、控件、多实例资源报告、编辑工程、打码、跟踪、导出 | NAS 认证、标签、收藏、VideoBox、宿主数据库与文件事务 |
| VideoKit App | 自有四平台本地视频/图片播放器；文件选择、最近打开、设置、独立 UI；使用相同 SDK | 首版不复制 LocalVideosBrowser 的 NAS/HTTPS 浏览及综合业务 |
| LocalVideosBrowser | 本地/HTTPS/NAS 文件源、浏览、认证、组织、租约、业务状态、输出提交；调用 SDK | 不包含 VideoKit 源码树、不直接调用具体播放/AI 引擎 |

Kit 的编辑与跟踪仍为 P0。用户已确认 App 使用 Flutter，完整 V1.0 展示编辑入口与多画面 UI；全部需求功能按里程碑顺序完成，不拆分不同产品版本。sample-host 是契约验证工具，正式 App 是独立产品，二者分开。

## 3. P0 追踪

| 需求组 | 原文节号 | 设计责任文档 | 必须具备的验收证据 |
| --- | --- | --- | --- |
| API/Fake/版本与能力 | 13、19、25、26.1 | PUBLIC_API_CONTRACT | Fake 与真实 SDK 同套契约 |
| 单视频与偏好恢复 | 5、6、15 | PLAYBACK_AND_IMAGE_DESIGN | 格式/轨道/连续 Seek/方向/缩放真机矩阵 |
| 静态和动态图 | 7 | PLAYBACK_AND_IMAGE_DESIGN | 格式矩阵、大图预算、无视频无关控件 |
| HostAction/导航/控件同步 | 9、15、18 | LOCALVIDEOBROWSER_INTEGRATION | 回调超时隔离、宿主侧导航与持久化 |
| 多实例/唯一声音/降级 | 8、16 | SYSTEM_ARCHITECTURE | 1/4/9/12 槽混排、单槽错误、归零资源报告 |
| 片段重排及多视频拼接 | 10.1–10.3 | EDIT_TIMELINE_AND_EXPORT_DESIGN | 编辑恢复、异参数转码、源内容不变 |
| 手动打码与坐标 | 10.4 | EDIT_TIMELINE_AND_EXPORT_DESIGN | 预览/导出遮罩对照 |
| 人脸/物体自动跟踪 | 10.5–10.7 | TRACKING_TECHNICAL_SPIKE | 跟踪质量、纠正、漏码阻断报告 |
| 安全导出/取消/进程终止 | 11、12、17 | EDIT_TIMELINE_AND_EXPORT_DESIGN | Sink 故障、abort、未提交清理 |
| 隐私/许可证/可独立交付 | 20–27 | OPEN_SOURCE_AND_LICENSE_PLAN、TEST_AND_ACCEPTANCE_PLAN | SBOM/NOTICE、离线证据、独立构建/回退 |

每条原始子需求需在实现前分配测试用例 ID。上表是组级追踪，不代表子需求已验收。降级是运行时能力不足的反馈机制，不能用于把必需模块改成后续需求。

## 4. 不变约束

输入只读；输出仅经宿主临时 Sink；无全局单例播放器；一个会话一个当前媒体；全部本机处理；数据源不传凭据或完整 NAS 路径；宿主保有音频、导航、后台与业务事务决定权。Kit 接收不透明 token，不存宿主 scope 或播放次数数据库。

手机默认 4 槽、平板默认 9 槽、视频会话硬上限 12，由宿主编排。实际并发解码需预留资源，不能承诺任意设备 12 路视频同时运行。图片使用内存预算，不计视频解码器名额。

## 5. 评审规则

十份设计文档及 App 方案评审通过前，不开始大规模产品编码；只允许在获准的 Spike 范围内验证方案。未核实模型权利、未通过输出安全或故障隔离条件时阻断相应正式发布。P0 变更只能由用户明确批准并留下需求变更记录。
