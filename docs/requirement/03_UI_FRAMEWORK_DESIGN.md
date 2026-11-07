# 03 UI 框架设计

版本：V1.1；日期：2026-11-06；对应原需求 §6–§10、§15.2、§17.4、§20。

> 技术决定：**VideoKit 一开始就使用 Flutter 开发 UI**，以便全平台开发。媒体能力仍由原生 Kit 提供（Android：Kotlin + Media3），Flutter UI 通过插件调用。
>
> 范围：本文件确定 **UI 框架层**——包结构、界面清单、宿主扩展点、主题机制、自适应布局、国际化与无障碍、演示模式。视觉设计（视觉稿、配色与字体取值、图标、动效和细节交互）由用户另行通知后重新设计，届时补入第 5.4 节，框架不需要推倒重来。

## 1. 目标与原则

1. VK-M0 交付完整的 VideoKit Flutter UI 框架：所有界面可运行、可操作、状态反馈完整，由 Fake 实现驱动，在示例 App 中完整演示。
2. UI 只依赖 Dart 版公共 API（`videokit_api`）：订阅会话状态、发送命令，不接触任何实现细节。后续里程碑把 Fake 换成真实原生实现，UI 不改。
3. 原生会话是播放/编辑状态的唯一权威；Dart 侧不维护第二套状态机，UI 本地状态只限于纯视觉（面板展开、手势进行中）。
4. 视频帧通过 Flutter `Texture` 直接显示，媒体字节和帧不经 Dart 消息复制。
5. UI 不包含任何宿主业务：不出现 LocalVideoBrowser 名称、标签名、NAS 概念（§20）；宿主业务只以 HostAction 和宿主面板插槽进入。

## 2. 包结构

| 包 | 语言 | 职责 |
| --- | --- | --- |
| `videokit_api` | Dart | Dart 版公共 API：接口、数据类型、状态、命令、错误、能力；与原生 `videokit-api` 语义一一对应，纯 Dart，无平台依赖 |
| `videokit_flutter` | Dart + Kotlin | Flutter 插件：用 Pigeon 生成的类型安全通道把 `videokit_api` 接到原生 Kit；通过 `TextureRegistry` 提供视频画面 Surface；Android 实现包装原生 AAR |
| `videokit_ui` | Dart | 全部 UI 组件、VideoKit Theme、国际化资源；只依赖 `videokit_api` |
| `videokit_fake` | Dart | Dart 版 Fake 实现、场景脚本、演示数据生成器、Dart 契约测试；UI 开发与测试用 |
| `videokit_example` | Flutter App | 示例 App：演示全部界面与宿主扩展点，内含模拟 LocalVideoBrowser 宿主 |

依赖方向：`videokit_ui → videokit_api ← videokit_flutter / videokit_fake`。`videokit_ui` 可以在不连接原生的情况下（只用 `videokit_fake`）运行在任何 Flutter 支持的平台上，便于 UI 先行开发和截图测试。

## 3. 宿主接入方式

| 宿主类型 | 接入方式 |
| --- | --- |
| Flutter App | 直接依赖 `videokit_ui` + `videokit_flutter`，把组件放进自己的页面 |
| 原生 Android App（如 LocalVideoBrowser） | 方式 A：通过 Flutter add-to-app 嵌入 VideoKit UI，VideoKit 提供 `videokit-ui-android` 桥接（`VideoKitFlutterFragment` / `VideoKitFlutterView`，预热并复用 FlutterEngine）；方式 B：只用原生纯引擎（原生 `videokit-api`），自己画控件 |
| 纯引擎 | 不用任何 UI，原生或 Dart 端直接调用 API，渲染到自己提供的 Surface/Texture |

- 方式 A 中，HostAction、导航请求、控件可见性等回调通过原生 API 交给宿主（宿主不需要写 Dart）；宿主面板插槽在 add-to-app 下以“宿主原生视图叠加 + `controlsVisible` 同步”实现。
- add-to-app 会增加包体积与首次启动时间（引擎初始化），通过预热引擎与缓存降低；具体数值在 VK-M0 实测并写入能力说明。这是选用 Flutter 的已知代价，评审时确认。
- VideoKit 不提供 Activity 或导航框架；全屏、路由、返回栈由宿主决定，不假设只有一个 Activity 或窗口（§2.2）。

## 4. 界面清单

| ID | 界面 / 组件 | 框架级内容 | 真实能力接入 |
| --- | --- | --- | --- |
| UI-01 | 视频播放器 `VideoKitPlayer` | 画面层（Texture）、手势层（轻触显隐、双指缩放、拖动平移、双击切换适配）、控制栏（播放暂停、快退快进、进度与缓冲、时间、倍速、音量/静音、字幕与音轨面板、方向切换/锁定、全屏、编辑入口）、宿主动作区、宿主面板插槽、加载/缓冲/重试/错误层 | VK-M1 |
| UI-02 | 轨道与设置面板 | 音轨列表、字幕轨列表与开关、倍速档位；无对应轨道时显示“不可用”原因 | VK-M1 |
| UI-03 | 图片查看器 `VideoKitImageViewer` | 静态/动态图、缩放平移旋转、适应/原尺寸、动图播放/暂停/循环、左右翻页与导航请求、图片信息；不出现视频专属控件 | VK-M2 |
| UI-04 | 宿主动作条 `HostActionBar` | 按 placement 与 displayPriority 排列；enabled/selected/pending/badge；溢出菜单；超时/失败提示与重试 | VK-M2 |
| UI-05 | 多画面 `VideoKitSlot` / `VideoKitSlotGrid` | 单槽画面与状态角标（加载、错误、降级、静音/发声）、错误占位、点击发声意图；可选网格组件（2×2、3×3、最多 12 槽），宿主也可自己排列 | VK-M3 |
| UI-06 | 编辑器 `VideoKitEditor` | 预览、播放头、时间线（片段块、缩放、吸附）、片段添加/分割/裁剪/删除/拖动重排、多输入排序、属性面板、撤销/重做、预计时长与空间 | VK-M4 |
| UI-07 | 打码与跟踪 `MaskEditor` | 遮罩列表（开关、删除）、马赛克/模糊与强度、区域框编辑、关键帧轨道；人脸检测结果与选择；物体点选/框选；跟踪进度；TRACKED / LOW_CONFIDENCE / AMBIGUOUS / LOST 区间标示；纠正关键帧；未覆盖区间检查 | VK-M5 |
| UI-08 | 导出流程 `ExportPanel` | 预设与参数、Sink 能力预检、阶段进度（准备/跟踪/编码/校验/写入）、取消中/已取消、失败原因与建议、成功摘要 | VK-M6 |
| UI-09 | 状态视图 `VideoKitStateView` | 统一的加载、缓冲、空、格式/编码不支持、损坏、权限/断线、资源不足降级、跟踪丢失、导出失败状态，均给出可执行的下一步 | 各里程碑 |

## 5. 主题

### 5.1 机制

- **先实现 VideoKit 自有 Theme**；SkinKit v2.0 支持 Flutter 后接入（5.5），当前不依赖 SkinKit。
- 用 Flutter `ThemeData` + 一组 `ThemeExtension`（如 `VkColors`、`VkTypography`、`VkSpacing`、`VkRadii`、`VkMotion`、`VkPlayerTheme`、`VkTimelineTheme`）组成 `VideoKitTheme`，通过 `VideoKitThemeScope` 下发。
- 主题值来自 `VideoKitThemeSource` 接口：V1.0 提供内置 `DefaultThemeSource`（浅色、深色）和宿主覆盖实现；SkinKit 将来作为另一个 `ThemeSource` 接入，组件代码不变。
- 宿主可覆盖颜色、图标（`VideoKitIcons`）、部分文案（`VideoKitStrings` 覆盖表）（§20）；覆盖不改变状态逻辑与无障碍语义（`Semantics` 始终由 VideoKit 设置），缺失时回退默认值。
- 浅色、深色、跟随宿主/系统；“减少动画”跟随系统（`MediaQuery.disableAnimations`），宿主也可显式指定。

### 5.2 Token 分类（框架确定）

| 组 | 内容 |
| --- | --- |
| 颜色 | primary、onPrimary、accent、selection、surface、surfaceVariant、scrim、error、warning、success、trackLowConfidence、trackAmbiguous、trackLost、demoBadge |
| 文字 | title、body、label、caption、timecode（等宽数字） |
| 间距 / 圆角 | xs–xl；sm、md、lg、full |
| 动效 | fast、normal、slow，以及减少动画时的替代值 |
| 组件尺寸 | 控制栏高度、最小触控目标 48dp、进度条、时间线轨道、遮罩框线宽 |

### 5.3 规则

- 组件中禁止写颜色、字号、尺寸、字符串字面量，全部读 Token 与本地化资源（静态检查）。
- 状态不能只靠颜色区分（如 LOST），同时有图标或文字。

### 5.4 视觉取值（待 UI 设计）

具体配色、字体、图标风格、圆角与动效取值，在用户通知的 UI 设计阶段确定。VK-M0 先使用中性占位取值（Material 3 默认色板派生），保证 Token 结构可用；视觉确定后只更新 Token 值与少量组件样式。

### 5.5 SkinKit 后期接入（预留）

- 时机：SkinKit v2.0 支持 Flutter 后，且 VideoKit 自有 Theme 已稳定；SkinKit 接口文档由用户提供，收到后补充映射设计与里程碑。
- 方式：新增可选包 `videokit_theme_skinkit`，依赖 SkinKit v2.0 的 Flutter 包，实现 `VideoKitThemeSource`，把 SkinKit 主题数据映射为 VideoKit Token；`videokit_ui` 与原生 Kit 不直接依赖 SkinKit。不为 SkinKit 早期原生版本做原生到 Flutter 的桥接。
- 约束：不接入 SkinKit 的宿主行为不变；SkinKit 无法表达的 Token 回退默认值并列入映射表；切换主题不改变会话状态、不破坏对比度与读屏语义；接入前核查许可、版本与分发条款。
- V1.0 必须做到：组件只读 Token；Token 集合带 `themeSchemaVersion`，新增 Token 有默认值。

## 6. 宿主扩展点

| 扩展点 | Flutter 宿主 | 原生宿主（add-to-app） | 原需求 |
| --- | --- | --- | --- |
| HostAction | 传入动作列表，组件回调点击 | 原生 API 传入，点击经原生回调返回 | §9.1 |
| 宿主面板插槽 | `hostPanel: Widget Function(bool controlsVisible)` | 宿主原生视图叠加，随 `controlsVisible` 同步显隐 | §15.2 |
| 控件可见性 | `onControlsVisibilityChanged` | 原生回调 | §6.3、§15.2 |
| 导航请求 | `onNavigationRequested` | 原生回调 | §7、§15.2 |
| 错误文案 | `VideoKitStrings` 覆盖 | 原生 API 传入覆盖表 | §9.4 |
| 主题覆盖 | `VideoKitThemeSource` | 原生 API 传入 Token 覆盖值 | §20 |

## 7. 自适应、输入与无障碍

### 7.1 布局

| 条件 | 行为 |
| --- | --- |
| 宽度 < 600dp | 紧凑控制栏，次要按钮进溢出菜单 |
| 600–839dp | 中等布局，轨道面板为侧滑面板 |
| ≥ 840dp（平板/宽窗口） | 展开布局，编辑器时间线与属性面板并排 |
| 横竖屏、分屏、窗口变化 | 用 `LayoutBuilder`/`MediaQuery` 实时重排，会话状态不丢失 |
| 安全区 | `SafeArea`/`MediaQuery.padding` 避让刘海、圆角、系统手势区 |

### 7.2 输入

- 触摸：轻触显隐、双指缩放、拖动平移、双击切换适配、长按（编辑器）。
- 鼠标/触控板：点击、滚轮缩放（带修饰键）、拖动、悬停显示控件（`MouseRegion`）。
- 键盘（`Shortcuts`/`Actions`）：空格播放/暂停，左右方向键 Seek，上下方向键音量，M 静音，F 全屏，Esc 退出全屏或关闭面板；焦点可见（`FocusTraversalGroup`）。

### 7.3 无障碍

- 所有可操作元素有 `Semantics`（标签、角色、状态，如“播放中”“已选中”“等待中”）。
- 焦点顺序符合视觉顺序；读屏或键盘焦点在控件上时不自动隐藏。
- 字体 100%/130%/200%（`textScaler`）下关键按钮不重叠、可达，必要时换行或进入溢出菜单。
- 进度条、时间线支持无障碍增减动作。

### 7.4 国际化

- 使用 `flutter_localizations` + `gen_l10n`（ARB 资源）；第一版只维护简体中文（模板 `app_zh.arb`）；英文在 VK-M6 后整批加入，其他语言按需（见 [13](13_ENGINEERING_CONVENTIONS.md) §3.1）。
- 时间、数字、文件大小按当前 Locale 格式化（`intl`）；时间码用等宽数字。
- RTL：布局用 `EdgeInsetsDirectional` 等方向无关写法；时间轴始终左到右，其余镜像。
- 伪本地化（加长文本、RTL 伪语言）用于检查截断与镜像。
- 错误对象只带稳定 code 与参数，文案由 `videokit_ui` 按 Locale 解析；原生 Kit 不含文案。

## 8. Fake 驱动与演示模式

### 8.1 Fake

`videokit_fake` 实现完整 `videokit_api`：

- 可控时钟：进度、缓冲、结束、Seek 由脚本驱动。
- 场景脚本：正常、慢加载、缓冲、格式不支持、损坏、断线、资源不足、HostAction 超时、跟踪 LOST、导出失败、取消。
- 演示画面：用 Flutter 绘制生成的测试图案（色块、时间码），不解码真实媒体。
- 遵守与真实实现相同的契约，由同一套 Dart 契约测试检查；原生侧另有 Kotlin Fake（`videokit-testkit`）供原生宿主 CI 使用。

### 8.2 演示数据

固定 seed 生成器产生媒体描述、时长、轨道、片段、遮罩与跟踪区间、导出阶段，附 manifest 记录参数与 hash；只用原创生成素材，不打包 `test_media`、私人照片或凭据。

### 8.3 标识与隔离

- Fake 驱动时画面常驻“演示模式 · 模拟数据”标识；模拟导出成功明确提示“未生成真实媒体文件”。
- `videokit_fake` 只作为示例 App 与测试的依赖，不进入宿主 Release 构建；示例 App 的演示场景只在 debug 构建提供。
- 构建检查：Release 产物不含 Fake 与演示资源。

## 9. VK-M0 UI 退出条件

1. UI-01 至 UI-09 全部组件在示例 App 中可操作，主要操作都有状态反馈；Fake 场景可触发、可重置。
2. 宿主扩展点在示例 App 中各有示例；原生 add-to-app 嵌入有一个最小可运行示例，并记录包体积与启动耗时。
3. 手机与平板、竖横屏、分屏、窗口变化下布局正确。
4. 中文、伪本地化、RTL 冒烟，以及字体 100%/130%/200% 有截图（golden）证据；基础读屏与键盘操作走查通过。
5. 组件中无硬编码样式与文案（静态检查）；Theme 浅深色与宿主覆盖演示。
6. 演示标识常驻；Release 构建不含 Fake 与演示资源的检查通过。
7. 测试报告中 UI 结果与真实媒体能力分栏，真实能力全部标 NOT_RUN。
