# VideoKit App 集成 SkinKit 要求 V1.0

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。本条覆盖下文此前“暂不自建 Theme”“M0 必须实接 SkinKit”等旧要求；供应方资料与历史要求保留供将来评审，不作为当前强制任务。完整现行范围见 [Flutter Theme 与延后集成决定](FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前 D1 冻结任务不变，M0 未启动。


## M0 UI 优先实施要求（2026-10-20 最新）

用户最新决定（2026-10-20）：M0 在保留 API/Fake/TestKit/sample-host 原范围的同时，先搭建整个正式 Flutter App 的 UI 框架，按既有 18 页 PPT 的视觉与交互样式实现，并真实集成 SkinKit。允许生成带明确“演示模式·模拟数据”标识的本地测试数据演示全部主要页面与状态；演示不能冒充真实播放、跟踪或导出通过。后续 M1–M6 功能逐批实现并接回同一 UI，M7 保持独立宿主接入，M8 完成全功能真实集成与发布级验收，不再首次重建 UI。继续复用 SkinKit 默认/标准样式与合法最小宿主适配，不另建独立 Theme 系统、主题包或编辑器；通过既有配置与受支持的最小覆盖实现 PPT 样式，无法表达的差异列明评审。

完整范围与退出门槛：[M0 App UI 框架要求](M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md)。本次为规划更新；D1 尚未通过，M0 尚未启动，不改变已冻结候选或当前设备批次。



更新日期：2026-10-20。依据：用户明确指定 `docs/ui/SkinKit/Third-party-Kit`，要求将 App 集成 SkinKit 纳入项目文档。**产品决定：必须集成；当前仅完成文档基线，不表示 SDK 已接入、授权已完备或平台验证通过。** 本补充与原全部 P0 同时生效。

## 1. 来源、版本与已知事实

- 第三方交付目录：[SkinKit 资料](ui/SkinKit/Third-party-Kit/)。原 ZIP、许可证及供应方文档只读保留，不修改供应方材料。
- SDK：`SkinKit-Closed-SDK-1.1.0.zip`，15,862,645 B，SHA-256 `0751dbe8606a97fedc07876970784d433789b7b85e8eb3f9f040168c90dd19e2`。
- Maven group `dev.skinkit`，本包模块版本 `1.1.0`；Contract 协议 `0.0.1`、静态 skinpack schema `0.1.0`、动画 schema `0.2.0-animation-dev.1` 独立管理，不能统一替换成 SDK 版本。
- 当前包提供 17 个模块：13 JAR、4 AAR，含二进制及宿主接线示例，不含 SDK 实现源码。优先消费随包 Maven/POM，禁止复制全部 AAR 后忽略传递依赖。
- 当前已交付 JVM/Android 原生 Views 能力；**没有交付通用 Flutter、Compose、Swift、Windows/macOS Adapter**。四平台可用性不能从 Android 包推断。
- Android 模块声明 minSdk 26、compileSdk 36、Java 17 字节码；sample-host 使用的 Gradle/AGP/JDK 版本只是样例工具链。VideoKit 保持 API31+，实际工具链兼容、R8、资源收缩和离线构建另测，不能直接替换整个工程构建配置。
- 供应方已有 Windows 文件系统失败、完整交互/200% 无障碍/性能未完成记录；Glass 当前仅 Solid。这些记录必须保留，供应方 demo 的通过不等于 VideoKit 验收通过。
- 来源核对记录：[本地交付清单](ui/SKINKIT_SOURCE_EVIDENCE_V1.0.json)。该记录只证明本次资料身份及 ZIP 内外文档一致，不证明 SDK 运行结果。

## 2. 集成范围与产品边界

| 需求 ID | 强制要求 |
| --- | --- |
| SK-01 | 正式 Flutter App 使用 SkinKit 的统一外观契约与默认执行器，通过宿主适配层驱动公共 UI 组件；禁止只写依赖声明或展示一页 demo 就宣称集成完成。 |
| SK-02 | Android 接入 `skinkit-default:1.1.0`（由 POM 传递 contract），复用供应方已提供的默认主题数据，满足 SDK 完整默认回退契约（不新建自有主题）。本地主题安装、预览、切换及恢复默认采用 `skinkit-core:1.1.0`，不自行复制一套主题包解析器。 |
| SK-03 | SkinKit 只负责外观。页面结构、导航、媒体授权、播放/编辑状态、触控区域、无障碍及文件事务仍归 App；不能用主题修改业务布局树或播放行为。 |
| SK-04 | VideoKit 核心及公共媒体 API 不依赖 SkinKit、Flutter 或任何主题。纯播放 Kit 可独立构建和调用；宿主不接 SkinKit 仍可使用核心。 |
| SK-05 | LocalVideosBrowser 不因 VideoKit App 接入而被强制引入 SkinKit。它的主题选择、AppDefault 与依赖由其自身工程决定，VideoKit 不读取它的主题数据库、账号或业务状态。 |

本地主题切换是此次集成的基础范围，先完成默认模式，再接 Core，均属于同一完整 V1.0，不拆成功能删减版本。默认完整性和故障回退任何时候不得依赖 Core、网络或账号。

Appearance / Appearance Android 在需要四类图片表面时接入；Personal / Personal Android / Photo / Creator、Animation、Store、Commerce、Community 为可选能力，不因本次指令自动增加主题创作、商城、支付、社区、角色动画、账号或远程服务需求。不得将不存在的通用 `skinkit-ui` 模块写入依赖。

九个 demo 主题是供应方样例，不要求全部进入 VideoKit 正式包。实际分发清单须逐主题审查 ID、版本、资源许可、能力、大小与兼容性。不能将 Graphite Cyan 等皮肤自动设为 VideoKit 的默认主题。

## 3. Flutter 与平台适配架构

```text
Flutter 业务页面
  → VideoKit 公共 UI Components
  → VideoKit SkinKit UI Adapter（宿主适配，不是另一套 Provider）
  → SkinKit ThemeProvider / PinnedThemeSource
  → DefaultThemeProvider + SkinKit 已有默认数据/最小宿主接线
    或 CoreThemeProvider + 原契约四级回退

VideoKit 播放 / 图片 / 编辑 / 导出核心：独立，不进入主题依赖链
```

Android 在 App UI 依赖注入入口管理原生 Provider、Registry、Theme Session 和资源服务。Flutter Adapter 将供应方已解析的类型化最终值映射到 ThemeData / ThemeExtension 及公共组件参数。桥接载荷可序列化，但边界必须有确定的 schema、值类型、范围、错误及版本校验，不能给业务页面开放 `get(String): Any` 或不受约束 Map，也不能自建优先级解析器。

桥接是**待实现的宿主工作**，不是供应方现成 Flutter 插件。Dart 只消费解析快照，不逐 token 同步跨通道调用、不在 getter 中做磁盘/网络/重解码。一次渲染使用同一 generation，旧回调按页面 ticket 与 generation 拒绝；原生 read view、异步资源 lease、订阅各有实际 owner/释放时点，不跨异步持有失效 view。

可选原生 VideoKit UI 通过它自己的薄 Adapter 消费同一契约；当前没有通用 Compose Adapter，不能假定 SkinKit Views 能直接为 Compose 或 Flutter 全部控件换肤。采用原生 Views 组件不构成将正式 App 技术栈从 Flutter 改回原生。

| 平台 | 当前交付事实 | VideoKit 要求及退出证据 |
| --- | --- | --- |
| Android | 有 JAR/AAR 与 Views 接线样例 | Flutter Adapter、手机/平板、生命周期及 Release/R8 实测；未实现前 NOT_RUN。 |
| iOS/iPadOS | 未交付 Swift/Flutter Adapter | M9 前确认供应方兼容实现或获许可的宿主适配方案，完成同契约/主题模式/资源验证；不得装入 Android AAR。 |
| macOS | 未交付桌面 Adapter | 同上，另测窗口、鼠标、键盘和显示缩放。 |
| Windows | JVM 包不等于 Flutter Windows 支持，已有目录持久性失败 | 评估二进制运行/打包方案与存储语义，明确权利和适配成本，实际验证前不得称已集成。 |

平台门未满足则阻断相应平台发布，不将 SkinKit 从需求静默删除、不复制并独立演化另一套 Contract。当前仍仅实现 Android，另外三平台保留兼容设计与 M9 实施安排。

## 4. 默认主题、设计效果图与 Token

| 需求 ID | 强制要求 |
| --- | --- |
| SK-06 | 仅在真实 API 必需时，用供应方已提供的 hostDefaults/标准默认值组装不可变 `AppDefaultTheme.builder(appId, version)` 数据，不自主设计视觉数据，Registry 使用同一批原始 Token 实例并冻结；`DefaultThemeProvider.completenessReport.requireComplete()` 验证 Light/Dark、全部必需字段及组件状态。不能把 AppDefaultTheme 写成供应方未提供的 interface。 |
| SK-07 | 所有 App 可控制的外观值进入七类类型化 Token / ComponentStyle：颜色、字体、尺寸、drawable、icon、animation、component。系统窗口/安全区/字体缩放与业务状态不是皮肤常量。 |
| SK-08 | 宿主稳定 appId 在接入时确认；优先原样使用供应方已注册 Token/StandardStyleTokens 及类型。暂不新建专属主题 Token/schema。播放器/时间线优先由公共控件组合已有样式，确有必需缺口先列清单另评审，不把示例键当现成 API。 |
| SK-09 | 公共组件统一获取外观；业务页面不写散落色值、字号或圆角，不重新构造同名 Token。Light/Dark 独立设计，支持跟随系统/浅色/深色并持久化；本地一键恢复默认。 |
| SK-10 | 直接复用 SkinKit 已提供默认/标准主题与样式；不新建深空蓝/青绿品牌主题，也不为科幻效果单独制作皮肤。既有主题中选择与用户视觉方向相容的方案，实际能力不足明确记录，不自行增加主题设计范围。 |

现有 [18 页 PPT 提案](ui/VideoKit_UI_V1.0/output/VideoKit_APP_UI_Design_V1.0.pptx) 保持原文件，不把其设计值当已完成 Token 接线。PPT 样式是当前视觉依据，优先通过 SkinKit 既有能力和最小宿主适配实现，不新建独立主题系统。后续集成按 [UI 映射补充](ui/VIDEOKIT_SKINKIT_UI_MAPPING_V1.0.md) 落地；PPT 当前是接入前视觉稿，不是 SkinKit 完成证据。默认主题不采用重发光、渐变按钮或大面积 Glass；装饰媒体缩略图不属于按钮样式。

默认按钮提供 NORMAL / PRESSED / FOCUSED / DISABLED / SELECTED / HOVERED 适用状态，loading 由 App 状态映射，不虚构 SDK 枚举。Android 最小触摸目标 48dp；主题不得缩小热区、裁切焦点、遮住字幕/时间线/遮罩或降低必要对比度。默认模式以系统字体为主，保留中英、长文本、RTL、100/130/200% 字体。供应方有日/韩资源不自动扩大 VideoKit 已定产品语言承诺。

## 5. 四级回退、一致性与资源

| 需求 ID | 强制要求 |
| --- | --- |
| SK-11 | 逐 Token/组件字段按 当前 App Extension → 兼容 Common → 当前模式 AppDefaultTheme → Safe Built-in Default 回退；扩展没有显式 Common 映射则直接回 App 默认。不完整覆盖不替换完整默认对象。 |
| SK-12 | 缺失、错类型、不兼容版本/能力、越界或损坏资源触发下一候选；合法 0、false、透明色不能当作缺失。必需默认项用到第四级安全兜底仍为默认完整性 FAIL。 |
| SK-13 | 切换先验证后原子发布，失败保留上一可用快照或回默认。同步 getter 返回已解析非空值，不阻塞 UI。切换不能重新打开媒体、重建播放器、丢失进度/选区、取消在途导出或改变音轨。 |
| SK-14 | 观察订阅释放随页面/窗口；资源读取先取得 lease，再释放 read view；异步结果同时核 render ticket/generation。取消/过时/临时内存压力不冒资源损坏、不污染候选。 |
| SK-15 | 本地包在 worker 上串行安装/校验/预览/激活，预览句柄实际关闭；install 不隐式 activate，取消 future 不冒存储回滚。固定私有目录、路径/符号链接、包/图片/动画限额、安全解码及资源完整性均验证。SHA 不是发行者签名或购买证明。 |
| SK-16 | 离线、未登录、无 Core、Core 加载失败及可选模块缺席时，默认业务完整可用。不因主题切换上传媒体、带入 NAS 凭据、扩展支付/账号权限或联网启动。 |

Glass 只使用当前已交付 Solid 后备，未验证 Full/Reduced 时不显示已支持背景模糊；主题照片文字覆盖另验证实色保护层。角色装饰默认不拦触摸、不进读屏焦点，尊重减少动画、后台、电量与热限制。未选 Animation 模块时返回 Disabled/静态后备，不产生空值。

## 6. 商用许可与依赖发行门

| 需求 ID | 强制要求 |
| --- | --- |
| SK-17 | SkinKit 单列为闭源专有商用 SDK，不能写为 MIT/BSD/Apache 开源。提供目录不等于购买或正式发行权已证明；保存合法取得/授权证据、许可版本、授权主体与 VideoKit App 二进制/资源商业发行范围。 |
| SK-18 | 当前 `LICENSE-SKINKIT.txt` 标题为 SkinKit 1.0.0 engineering license draft，授权主体法定姓名待补；交付 SDK 为 1.1.0。依供应方文档记录拟允许商业宿主集成，但正式 1.1.0 适用性、主体、商店分发与获取依据在发布前核实，不宣称法律审核完成。 |
| SK-19 | 原文限制 SkinKit 自有素材/示例单独收费再分发及制作同类商业主题包；正常商业宿主/适配封装的拟许可不等于可把 SDK 本体嵌入对外 VideoKit AAR/SDK 再分发。当前依赖仅留 App UI 层；扩散分发范围须另核。第三方原许可/NOTICE不被覆盖。 |
| SK-20 | 生成实际选模块/传递依赖/资源清单与 hash，锁定本地 Maven、版本与校验；SBOM、许可页/NOTICE、Release/R8/资源收缩及最终 APK/AAB 内容逐项检查。不得将 demo 全部权限、支付 SDK 或测试依赖自动复制进产品。 |

本次不购买、不付款、不安装供应方 demo、不更换签名或上传任何资料。工程文档要求不代替商用授权完成；授权缺口阻断正式发行，不据此放弃必需集成。

## 7. 里程碑与交付

| 阶段 | 纳入内容 | 不得误报的状态 |
| --- | --- | --- |
| 当前 D1 | 记录资料身份、许可风险、Flutter/平台桥接与构建兼容性待验证项 | 文档完成不是 SDK 接入；不打断当前冻结的 RESUME01 媒体候选。 |
| M0 | 原 API/Fake/TestKit 范围 + 完整 Flutter App UI、真实 SkinKit Adapter、测试数据演示与隔离 | 全页/全状态与 PPT 对照验收；不把模拟媒体当真实能力通过。 |
| M1–M7 涉及可选 UI 时 | 提前沿用统一 Token 接口和默认模式，保持原生纯核心可移除 UI | 不要求原生调用方装 Flutter/SkinKit；不以演示控件代正式 App。 |
| M8 正式 Flutter App | 复用 M0 UI 和真实 SkinKit，验收 M1–M6 已接回功能与完整真实用户流程、Android 手机平板实测 | 无实现/实测项 NOT_RUN 或 BLOCKED，不能只默认模式就称整个集成完成。 |
| M9/M10 | 三个平台适配及对应发行验收、商用权利与完整供应链材料 | Android PASS 不外推四平台；未确认平台方案阻断对应平台发布。 |

M8 开发与测试工作单：[coder](milestones/VK_M8_SKINKIT_CODER_REQUIREMENTS_V1.0.md)、[tester](milestones/VK_M8_SKINKIT_TESTER_REQUIREMENTS_V1.0.md)。它们是未来阶段要求，当前未派发 UI 编码，不改变当前 D1 设备安排。按多功能集中开发、自检冻结、整包交测执行，避免频繁构建。

## 8. 验收矩阵

以下全部为未来验收要求，**本次实际结果均 NOT_RUN**。

| Case ID | 追踪要求 | 必须取得的证据 |
| --- | --- | --- |
| SK-T01 | SK-01/04/05 | 实际依赖图、核心无 SkinKit 构建；Flutter 页经 Adapter 使用真实 SDK，Browser 无强制依赖。 |
| SK-T02 | SK-02/06/09 | 仅 default/contract、无 Core/网络/账号冷启动；完整必需 Token/状态/本地资源检查，安全兜底计 FAIL。 |
| SK-T03 | SK-02/11/12/15 | Core 安装/预览/显式应用/恢复默认；Common-only、部分 Extension、错类型/越界/损坏/不兼容包与字段回退证据。 |
| SK-T04 | SK-07/08/10 | 全页 UI 与供应方已有 Token/类型/样式对应清单；不新建自有主题或独立 Token体系，PPT配色不直接写字面量。 |
| SK-T05 | SK-09/13 | 系统/浅/深模式与冷启动恢复，切换失败原快照保持，媒体/进度/选区/导出任务不重建。 |
| SK-T06 | SK-13/14 | 同帧 generation 一致，快速切换/旋转/页面退出、晚回调与资源失败；订阅/read view/lease 真释放、无已释放读取。 |
| SK-T07 | SK-09/10 | 手机和平板横竖屏/分屏/窗口，中英/伪本地化/RTL/100/130/200%字体、48dp、键鼠焦点/读屏、实际对比度。 |
| SK-T08 | SK-15/16 | 私有目录与路径攻击/包大小/坏图/离线/模块缺席/存储失败，不崩溃不空白；照片和装饰不遮挡控件/字幕/编辑标记。 |
| SK-T09 | SK-13/16 | 播放、图片、多画面、编辑/跟踪、导出/取消、错误/权限各页状态真实换肤回归；不改变媒体帧、字幕内容或导出像素。 |
| SK-T10 | SK-17–20 | 许可/合法获取/正式版本适用范围、SBOM/NOTICE/模块及资源 hash、真实 Release/R8/resource-shrink、最小权限与无隐式联网。 |
| SK-T11 | SK-01/03及平台表 | 各平台真实 Adapter/模式/资源/输入/窗口验证；未交付平台保留 BLOCKED/NOT_RUN。 |
| SK-T12 | SK-13/14/16 | 首屏、换肤时延、主线程阻塞、内存/CPU/电量实测；预算由样机结果冻结，不虚构已满足指标。 |

## 9. 本次变更记录

2026-10-20：新增强制集成及“不新建自有Theme”决定及本文、UI 映射、来源身份清单、M8 两份工作单；同步可写产品/架构/许可/测试文档，并以补充规范覆盖不可写历史基线/里程碑，具体见本次变更记录。未修改供应方交付、PPT、已冻结开发候选、SDK/API 产品代码或依赖锁；未运行集成/构建/设备/性能测试。

本次旧里程碑文件拒绝写入，原文保留；新增 [SkinKit里程碑有效补充](MILESTONES_SKINKIT_ADDENDUM_V1.0.md) 作为当前集成要求。其他已同步文档及此次修改清单见 [变更记录](ui/SKINKIT_DOCUMENTATION_CHANGELOG_V1.0.md)。
