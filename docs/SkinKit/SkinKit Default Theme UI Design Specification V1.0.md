# SkinKit Default Theme UI Design Specification

**版本：V1.0**  
**中文名称：SkinKit 默认主题 UI 设计规范**  
**文档序号：第四份正式规范**  
**首次发布日期：2026-10-05**  
**更新日期：2026-10-07**  
**实现基线：2ee5c29d，集成交付 0.3.0-integration-r1**  
**适用对象：各 App coder、UI 开发者、设计师、组件维护者与评审者**  
**配套规范：《SkinKit Ready 开发规范 V1.0》**

> **Git 提醒——开始 UI 开发前必须执行。** 检查 `git status`、当前分支与最近稳定提交，确认已有变更的归属，不覆盖他人工作、不破坏历史。公共组件、Theme Token、页面 UI 按阶段小步 commit；每个可以独立验证的节点完成检查后提交。禁止为整理 UI 使用未经授权的历史重写或破坏性重置。提交说明应描述具体行为变化，并保留回退依据。

## 0. 本次修订的依据与阅读方式

本次以用户提供的同名原文为基础，保留 Clean Minimal 设计基准、Token 治理、全部组件要求与验收标准；修订过时接口、Token 示例和“未来未实现”的阶段描述。原文为 485 行、32,514 字节，SHA-256 为 `96c0b40da7b2b642539bb0dcbc4affa271331621457e6aa33e5e4f02aa464e44`。

第 1–26、29–31、33 节的“必须”是设计与宿主验收要求，不能理解为 SDK 已生成全部控件或全部测试通过。第 27–28 节使用真实 Contract/Default API；第 32、34–36 节列出当前交付、图片规则及验证边界。本文保留的初始视觉建议不是当前 Demo 的逐像素规格，也不要求把各 App 品牌色统一成 Demo 的绿色。

当前为 Android 原生 Views 与 JVM 开发版 SDK，未交付通用 Compose/Swift/桌面组件库。Glass、完整导航/弹层 Design System、任意 Token 引用计算、全平台响应式和完整无障碍认证仍由宿主实现与验收。设计层名称若不属于已注册的七类 Token，必须通过受支持的类型化宿主扩展或宿主组件策略落地，不能假定任意名字都是 SDK API。

## 1. 文档目的、适用范围与配套关系

本规范将 Clean Minimal / 清爽极简型转化为可执行的 Design System、Token、组件规则和验收标准。各 App 从 UI 开发第一天执行，不应在页面完成后再集中替换硬编码。

适用于手机、平板、桌面及横竖屏 UI；包含 Light/Dark、公共组件、业务专属组件、交互状态与无障碍。平台已有交互与辅助功能约定应得到尊重。

本文件是此前三份 SkinKit 文档的第四份配套文档：此前文档负责平台设计、架构与接入等既有约束；本文件负责 AppDefaultTheme 的视觉落地。已明确的《SkinKit Ready 开发规范 V1.0》负责就绪开发与 Contract 接入，本文件补充视觉 Token、组件行为与验收要求。既有产品与架构要求仍由《SkinKit 用户需求文档 V1.0》《SkinKit 系统架构设计 V1.0》管理；本文按实际 SDK 更新视觉接入，不替代它们的产品范围或把未实现要求视为已交付。

如既有 Contract 与本文示例不一致，采用正式 Contract 的名称与类型，同时保持本文要求的主题职责、集中取值与覆盖语义。发现实质冲突时记录并协调修订，不在 App 内另建一套不兼容 Contract。

规范用语：**必须**为验收要求；**建议**为初始设计参考；**允许**为满足约束后的可选实现。表格中的建议数值不是允许在页面中写字面量的例外：最终采用的值必须进入 AppDefaultTheme Token。

## 2. 正式主题定位与设计目标

**AppDefaultTheme 是每个 App 自己实现、长期维护并永久保留的正式主题，不是临时占位、过渡方案或 SkinKit 上线后删除的代码。** 每个 App 必须先实现自己的 Clean Minimal AppDefaultTheme，可保留品牌色、内容结构与业务特征；已经接入 Core 的宿主可另外选择内置或个人主题。

视觉关键词：**干净、轻盈、克制、现代、柔和、层级清晰、留白充足**。

建议视觉比例概念为 **70% Clean Minimal + 20% Soft & Friendly + 10% Glass & Layered**。该比例表达设计倾向，不是像素面积配额，也不是要求实现三套主题。清晰的中性结构是主体；柔和来自圆角、留白与语气；Glass 仅用于少量必要的局部层次。

设计目标：高可读性、长期使用舒适、完整状态、稳定响应式、品牌可辨识，以及足够中性的基础结构，使未来 Skin 能明显改变产品观感。

非目标：强卡通、强科技、游戏、复古、拟物、重玻璃、Neo-Brutalism、炫光或过度装饰。这些方向属于可选 Skin，不作为 AppDefaultTheme 的基础语言；目前已实现的卡通、怀旧等演示主题不改变此默认设计原则。

## 3. 主题架构与永久回退原则

不启用 Core 时的调用链：

```text
业务页面
  → 公共 UI Components
  → ThemeProvider Contract
  → DefaultThemeProvider
  → AppDefaultTheme（Light / Dark）
```

启用当前 Core 时的调用链：

```text
业务页面 → 公共 UI Components → ThemeProvider Contract
  → CoreThemeProvider / Theme Resolution
      → SkinKit Theme 有效 override
      → 未覆盖值回退至 DefaultThemeProvider → AppDefaultTheme
```

业务页面不得直接依赖 DefaultThemeProvider 的实现类，也不得直接读取某个皮肤包。公共组件通过统一 SkinKit Contract 获取主题值；AppDefaultTheme 实现该 Contract 所需的完整基础主题。

当前完整解析顺序：已验证的当前 App Extension → Common（扩展 Token 必须显式声明兼容映射）→ 当前模式 AppDefaultTheme → Safe Built-in Default。回退必须按 Token 或结构字段执行，而非整体替换一个不完整对象。缺失、类型错误或不可用的覆盖值使用默认值；禁止把合法的 `0`、`false` 或透明色当作缺失。主题切换应发布一致的解析快照，避免一帧内混用新旧颜色。

AppDefaultTheme 永不删除；禁用皮肤、皮肤加载失败或部分覆盖时仍应得到完整可用的 UI。默认模式不要求启用 Core；需要皮肤包时使用已交付的 Core 加载与解析，不复制解析器，也不绕过 Contract。

## 4. Token 治理、命名与取值规则

所有由 App 控制的视觉值必须来自统一 ThemeProvider/Token：颜色、字体、字号、字重、行高、圆角、间距、边框、阴影、透明度、图标、组件尺寸与动画参数。系统安全区、窗口尺寸、字体缩放等运行时数据由平台提供，再与主题规则共同计算布局，不应伪装成固定主题常量。

建议采用三层结构：基础 Token → 语义 Token → 组件 Token。页面消费语义或组件值，不直接引用原始色板。基础数值集中在 AppDefaultTheme 的定义或生成源中；公共组件不重新定义一套常量。

| 层级/用途 | 命名示例 | 约束 |
|---|---|---|
| 色彩语义 | `color.background`、`color.surface`、`color.text.primary` | 根据模式解析 |
| 品牌语义 | `color.primary`、`color.onprimary`、`color.primarycontainer` | 每个 App 自己定义并验证配对 |
| 字体 | `typography.title`、`typography.body` | 包含字号、字重、行高等完整样式 |
| 基础尺寸 | `dimension.corner.medium`、`space.4` | 仅在主题定义层绑定实际数值 |
| 组件样式 | `component.button.primary`、`component.card.default` | 引用语义 Token，包含状态 |
| 资源与导航 | `icon.search`、`navigation.topBar` | 图标资源及导航样式可替换 |
| App Extension | `apps.player.component.progressbar` | 显式命名、类型化、注册与默认值 |

`space.4` 与 `space.16` 是原设计尺度的名称，分别表示 4dp 与 16dp，不能直接注册为 SDK Token。实际代码使用 `dimension.spacing.s4` / `dimension.spacing.s16` 等合法键，类型安全属性由宿主保存。`color.text.primary` 与品牌 `color.primary` 不得混用。

设计源可引用基础 Token；当前 SDK 接受的是构建阶段已算好的类型化最终值，不提供任意运行时表达式或通用引用求值器。禁止在组件里拼接字符串、猜测字段或通过不受约束的任意 Map 隐藏视觉常量。任何新增字段需要用途、类型、默认值、Light/Dark 值、覆盖策略与维护归属。

实际注册键必须匹配全小写点分段，并使用 color / typography / dimension / drawable / icon / animation / component 七类前缀，或 apps.<appId>.<对应类型>。例如设计尺度 space.16 应映射到合法的 `dimension.spacing.s16`，layout、glass、navigation、motion 是设计分类而非 SDK 已存在的 getter。当前 Registry 不自动把旧键转换成别名；自定义组件 schema 必须属于本 App namespace。Theme Token 不能让皮肤重排业务页面、改变导航或缩小触控目标。

## 5. Light / Dark 双主题

每个 App 必须提供完整 Light 与 Dark AppDefaultTheme，支持系统模式与产品允许的显式选择。两种模式共享语义结构，分别定义色值与必要的透明度、阴影、Glass 参数。

Dark 必须独立设计，禁止简单反色、整页套黑色蒙层或只修改 background。检查文本、图标、边框、选中态、输入框、弹层、图片占位与系统栏。品牌色在 Dark 中可调整亮度或饱和度，但必须维持识别与可读性。

## 6. Color Token

下表是初始建议，最终值可在实际设计阶段校准；调整仅发生在主题定义层。

| Token | Light 初始建议 | Dark 初始建议 | 用途 |
|---|---|---|---|
| `color.background` | `#F7F8FA` | `#0F1012` | 页面底色 |
| `color.surface` | `#FFFFFF` | `#1C1C1E` | 内容与组件表面 |
| `color.surfacevariant` | `#F0F1F4` | `#26272B` | 次级表面 |
| `color.text.primary` | `#1C1C1E` | `#F5F5F7` | 主文字 |
| `color.text.secondary` | `#6E6E73` | `#A1A1AA` | 次级文字 |
| `color.divider` | `#E5E5EA` | `#34353B` | 低强调分隔 |
| `color.disabled` | `#AEAEB2` | `#62636B` | 禁用视觉基准 |
| `color.primary` | App 定义 | App 独立定义 | 主操作与关键选中态 |
| `color.onprimary` | 与 primary 配对定义 | 与 primary 配对定义 | 主操作上的文字/图标 |
| `color.primarycontainer` | App 定义浅容器 | App 定义深容器 | 低强调品牌表面 |
| `color.onprimarycontainer` | 配对定义 | 配对定义 | 品牌容器内内容 |

还必须定义 `color.border`、`color.focusring`、`color.scrim`，以及 `color.status.success/warning/error/info` 与各自的内容色和容器色。状态色的最终值由 App 校准，不得仅使用红/绿区别状态。

`color.disabled` 不是所有禁用组件通用的填充色：组件应具有独立的 disabled 内容、背景与边框 Token。divider 的浅色不应被用于需要足够对比度的输入边界或焦点轮廓。

整个页面以中性色为主体。品牌色集中用于主操作、链接、选中态和少量业务强调，禁止每个标题、图标、卡片边框都染成品牌色。所有文本/背景组合需实测对比度，初始色值不是合格证明。

## 7. Typography

优先平台系统字体，不为默认主题额外捆绑装饰字体；中文、英文、数字、长文本与 fallback 字体必须一起验证。

| Token | 建议字号 | 建议字重 | 建议行高 |
|---|---|---|---|
| `typography.display` | 28–32sp | Medium / Semibold | 1.2–1.3 倍 |
| `typography.titlelarge` | 22–24sp | Medium / Semibold | 1.25–1.35 倍 |
| `typography.title` | 18–20sp | Medium / Semibold | 1.3–1.4 倍 |
| `typography.body` | 15–16sp | Regular | 1.4–1.6 倍 |
| `typography.bodysmall` | 13–14sp | Regular | 1.4–1.6 倍 |
| `typography.caption` | 11–12sp | Regular | 1.3–1.5 倍 |

每个 App 在范围内选择确定值写入 Token，不在各页面随机选择。单个页面约保持 3–4 个明显字号层级；避免大量 Bold、过细字重和全大写装饰。Caption 仅用于辅助信息，不承担主要操作或关键错误说明。使用可缩放字体单位，不能用固定高度裁切放大后的文本。

## 8. Radius

| Token | 初始值 |
|---|---|
| `dimension.corner.small` | 6dp |
| `dimension.corner.medium` | 10dp |
| `dimension.corner.large` | 14dp |
| `dimension.corner.xlarge` | 20dp |
| `dimension.corner.full` | 999dp，语义为完整圆角 |

组件建议：Button 10–12dp；Card 12–16dp；Dialog 16–20dp；Input 10–12dp；Chip 使用 full。必要时增加明确的组件 Token，如 `dimension.corner.button`，不要在组件里通过基础 Token 加上字面量生成 12dp。

圆角以柔和为准，禁止所有矩形都变成大胶囊。`full` 在平台层应映射为完整圆角形状，不要求实际渲染一个超大半径。

## 9. Spacing 与尺寸

基础间距为 4/8/12/16/24/32dp，对应 `space.4/8/12/16/24/32`。手机主边距建议 16dp；同组信息间距建议 8–12dp；组件内部 padding 建议 12–16dp；内容分组间距建议 24–32dp。最终选值均写入对应 Token。

平板、桌面通过 `layout.pagePadding`、`layout.contentMaxWidth`、`layout.columnGap` 等响应式 Token 扩展。避免连续叠加父子 padding 造成无意留白。长文字、密集业务、键盘等可有受控密度变体，但必须通过组件或 Extension Token 表达。

## 10. Elevation / Shadow

优先使用背景色差、间距和 divider 建立层级。普通 Card 默认无阴影；浮动组件、Dialog、Popup、悬浮按钮允许极轻阴影。Dark 中可通过表面亮度与边框形成层级，不能依赖增加黑色阴影。

建议定义 `elevation.none/floating/modal`，每项封装平台所需参数；颜色、模糊、偏移与透明度也由主题控制。禁止大面积重黑阴影、高模糊发光以及每张 Card 都明显悬浮。实际阴影参数应在目标平台校准后固化进 Token。

## 11. Button

| 类型 | 外观规则 | 典型用途 |
|---|---|---|
| Primary | primary 背景、onPrimary 内容、Medium | 当前主要操作 |
| Secondary | 中性表面或轻边框 | 次要操作 |
| Text | 无背景、语义强调内容色 | 辅助操作 |
| Icon | 统一图标尺寸，独立触控区域 | 工具栏与紧凑操作 |

按钮建议触控高度 44–48dp；Android 默认至少 48dp，其他平台按自身可访问性要求映射。图标视觉尺寸不能替代触控尺寸。圆角、内容间距、描边、最小宽度、各状态颜色均由组件 Token 提供。

宿主按钮必须实现 default、pressed、disabled、loading、focus；存在悬停输入时实现 hover。当前 Contract 的 VisualState 为 NORMAL、PRESSED、FOCUSED、DISABLED、SELECTED、HOVERED，loading 由宿主业务状态映射，不得虚构 SDK 枚举。pressed 使用轻色层或轻 scale；disabled 不接收操作；loading 保持布局宽度，提供可读状态，并按业务规则阻止重复提交；键盘 focus 可见且不被裁切。禁止渐变、发光、重阴影和 3D 装饰。一个操作区应具有清晰的主次关系，避免并排堆满同等高强调按钮。

## 12. Card

Card 表示内容分组，不是默认给每一段内容加圆角盒子。建议 surface 背景、12–16dp 圆角、12–16dp padding、可选浅 border、无或极轻 shadow。列表优先考虑间距和分隔，而非满屏嵌套 Card。

`component.card.default` 定义背景、内容色、圆角、padding、边框与 elevation。只有可点击 Card 才展示 pressed/focus，并明确点击区域与辅助操作的关系。卡片不得吞掉内部按钮的可访问性语义。

## 13. Input / Search

输入框使用中性背景、10–12dp 圆角及清晰边界；建议单行控件触控高度 44–48dp，内容放大时允许增高。label、placeholder、输入文字和帮助信息使用独立语义 Token。placeholder 不能替代持久标签。

必须覆盖 empty、filled、focus、disabled、readOnly、error；错误含文本说明和必要图标，不只变红。focusRing 与 error border 不应相互遮蔽。多行输入允许内容扩展或滚动，明示计数规则。

Search 使用 `input.search` 与 `icon.search`；清除、取消、提交按钮具有明确标签。保证软键盘、桌面快捷键与输入法组合输入正常；禁止为装饰破坏选区、粘贴或系统菜单。

## 14. TopBar / Toolbar

使用 `navigation.topBar` 定义背景、内容色、高度、padding、分隔和可选 Glass。标题优先 title，避免过大标题挤压操作。返回、主操作与溢出操作层级清晰，图标命名与位置遵守平台约定。

安全区与系统栏 inset 来自平台。标题过长时省略或调整布局，关键操作不能被截断。滚动前后的透明/实色变化通过主题状态定义，禁止页面临时写透明度。

## 15. Bottom Navigation / Tab

使用 `navigation.bottomBar` 与 `navigation.tab` 定义选中/未选中/pressed/focus/disabled 样式。选中态至少具有文字、图标形态、指示条或背景中的另一种辨识方式，不能仅靠颜色。

主导航入口数量应适合窗口宽度；空间不足时调整导航结构，不能压缩触控目标。Tab 表达同层内容切换；底部导航表达主要目的地。键盘与辅助技术应能感知角色、标签、选中状态和焦点。

## 16. Dialog / Sheet / Popup

Dialog 建议 16–20dp 圆角；Sheet、Popup 的圆角、宽度、内边距、scrim 与 elevation 通过各自组件 Token 提供。内容先建立标题、正文和操作层级，主操作克制，危险操作有明确语义。

弹层在小窗口和字体放大时允许滚动；操作不能落在不可见区域。支持适用的返回、Escape、焦点进入/约束/恢复与辅助技术播报。模态关闭方式需符合业务要求，不能假设点击遮罩一定关闭。Popup 要处理窗口边界与锚点变化。

## 17. List / ListItem

定义 `list.default` 与 `listItem.default`，统一 leading 图标/缩略图、标题、副标题、trailing 信息和操作的对齐。行高由文本与最小点击目标共同决定，禁止固定高度截断内容。

同类项具有一致密度；divider 位置统一。可点击项支持 pressed/focus/selected/disabled。复选、拖动、滑动等业务交互需有可访问的替代操作。大量内容使用适合平台的虚拟化，并保留主题解析的正确更新。

## 18. Icon

以 Outline / Soft Rounded 为主，16/20/24dp 建立统一尺寸语言。统一线宽、圆角、视觉重量和对齐，避免混用线性与厚重填充图标；选中态的填充变体必须成体系。

图标从 `icon.search` 等资源 Token 获取，语义色来自主题。交互图标必须有可访问名称；纯装饰图标从辅助技术树中排除。图标尺寸与触控区域分别定义。

## 19. 图片、缩略图与空状态

图片使用组件 Token 定义比例、圆角、裁切模式、占位与失败样式。同类缩略图保持一致比例；加载前保留布局空间，避免内容跳动。品牌或内容图片可保留自身颜色，周围 UI 不因此增加装饰。

空状态由简洁图形或图标、说明及必要操作组成，避免大型强风格插画主导默认界面。区分首次使用、无搜索结果、权限不足和加载失败。图片替代文本根据内容意义提供；纯装饰不重复播报。

## 20. Motion

| Token | 建议时长 | 用途 |
|---|---|---|
| `motion.press` | 80–120ms | 按压反馈 |
| `motion.small` | 150–180ms | 小组件与状态变化 |
| `motion.normal` | 200–250ms | 一般进入/退出 |
| `motion.page` | 250–300ms | 页面转换 |

时长、缓动、scale 幅度、slide 距离均进入 Token。以 fade、轻 scale、小 slide 为主，不用默认弹跳、大旋转、粒子爆炸或闪光。动画不阻止操作，也不替代加载状态。尊重系统减少动态效果设置，降级为淡入淡出或立即切换；连续播放动画应可停止且不影响阅读。

## 21. Glass 局部使用与 fallback

仅允许在 TopBar、BottomBar、Floating Panel、Player Controls 等局部使用轻量 Glass；普通正文、列表和输入面板以稳定实色为主。禁止全局重毛玻璃、多层叠加 blur 或通过透明表面让内容难以辨识。

`glass.local` 至少包含 enabled、tint、opacity、blur、border 和 `fallbackSurface`；由 AppDefaultTheme 按模式定义。前景文字与图标必须在实际背景变化下保持可读，必要时增加主题定义的实色底层。

平台不支持、减少透明度设置开启、渲染性能不足或背景不可控时，使用语义实色 fallback。fallback 保持布局、操作与层级一致；不能只去掉 blur 而留下不可读的透明背景。blur 只作用于指定背景，不能模糊前景文字。

## 22. 响应式布局

根据可用窗口宽度和内容需求决定 compact/medium/expanded，不根据设备型号写死。断点和布局参数进入 `layout.*` Token；安全区、折叠遮挡和窗口大小来自平台。

| 场景 | 布局要求 |
|---|---|
| 手机竖屏 | 单列为主，主边距建议 16dp，主操作易触达 |
| 手机横屏 | 调整信息区与操作区，避免固定竖屏高度 |
| 平板 | 使用双栏、主从结构或受控内容宽度 |
| 桌面 | 限制阅读宽度，利用侧栏、工具栏和多列内容 |
| 分屏/缩放窗口 | 按当前可用空间重新布局，保持核心操作可见 |

禁止把手机 UI 简单拉伸至桌面或横屏。旋转、窗口变化与导航形态切换应保留业务状态、输入内容和合理焦点位置。

## 23. 可访问性

必须支持系统字体缩放，至少验证默认字号与 200% 放大；对平台更高可用档位进行关键流程检查。关键信息可换行，操作区可增长，不以截断解决可读性问题。

将 WCAG AA 的普通文本 4.5:1、大文本 3:1 作为对比度验收基准；关键控件边界与状态指示目标为 3:1。大文本资格按标准和实际字体评估，不能简单把所有 18sp 标题当作大文本。初始 Token 需针对真实组合测量，尤其是次级文字、品牌按钮与 Glass。

触控目标约 44dp 起，按平台要求执行；Android 至少 48dp，Apple 平台通常按 44pt 目标映射，桌面同时支持键盘和指针。不得把 dp、pt 和 CSS px 直接视为同一物理尺寸。

状态不能只靠颜色表达。支持语义标签、正确阅读顺序、可见 focus、键盘访问、减少动态效果和减少透明度。禁用内容也应可辨识，不能用低透明度隐藏关键解释。

## 24. 状态规范

| 状态 | 必须表达的内容与行为 |
|---|---|
| loading | 稳定布局、可感知进度/忙碌语义；按需防重复操作 |
| empty | 说明空的原因，提供合理下一步 |
| error | 可理解原因与恢复操作；不直接展示内部堆栈 |
| offline | 清晰说明连接状态、缓存可用性与重试方式 |
| disabled | 不接收操作，必要时解释不可用原因 |
| focus | 可见轮廓或等效提示，支持键盘与辅助技术 |
| selected | 语义选中与视觉提示一致，不能仅依赖颜色 |

状态使用公共反馈组件与对应 Token，不能由各页独立拼装颜色和尺寸。恢复后及时更新状态；错误重试保留可恢复的用户输入。

## 25. App 专属组件与 Extension

允许在同一风格基准下扩展业务组件，如 `player.progressBar`、`browser.mediaCard`、`keyboard.key`。通过正式 Extension 注册，建议命名为 `apps.player.component.progressbar` 等；提供类型、默认值、Light/Dark、状态和覆盖规则。

例如进度条定义 track、filled、thumb、height 与可访问操作；媒体卡定义比例、元信息和占位；键盘按键定义 keycap、标签、pressed 与布局间距。不可在业务组件内部写死品牌色、圆角或特殊动画。业务行为不属于皮肤 Token，皮肤覆盖不能改变播放权限、输入规则或导航业务逻辑。

## 26. 禁止事项

- 页面或公共组件硬编码色值、字号、字重、间距、圆角、阴影、透明度、动画参数和可主题化资源。
- 用局部复制的常量或平台主题默认值绕过 SkinKit Contract；平台主题适配必须显式映射解析后的 Token。
- 业务页面直接创建 AppDefaultTheme、实例化 provider 或读取具体 Skin 包。
- 删除 AppDefaultTheme，或把未覆盖字段解析为透明、零尺寸、空字体等无效值。
- 将 Light 简单反色生成 Dark；单靠颜色表达状态；隐藏 focus。
- 全局重 Glass、渐变发光、大面积重阴影、强拟物、强卡通或满屏圆角盒子。
- 固定行高/容器高度裁切放大文字；以减小按钮目标解决空间不足。
- 为多套皮肤在各 App 复制多套业务页面/组件；或仅为使用本地主题强制接入商店。
- 将「建议值可校准」理解为允许页面各自任意调值；未经评审增加不受约束的 Token。

## 27. 公共组件使用真实 Contract

页面提供文案、业务状态与回调；公共组件接收原始 Token 实例，并通过固定 generation 读取视觉值。不能创建自定义 `resolvedTheme()` 接口替代当前七类 getter，也不能把 Compose 伪代码当成已交付 Adapter。

```kotlin
import dev.skinkit.contract.*

fun readPrimaryButton(
    source: PinnedThemeSource,
    token: ComponentToken<ButtonStyle>
): ButtonStyle = source.pin().use { view ->
    view.getComponentStyle(token)
}
```

这里返回的是不可变样式；资源异步工作仍须在 pin 有效时取得自己的 lease，并按当前 generation 检查回调。真实组件同时消费多个 Token 时，应在同一个 `use` 内读取，不能每个 getter 各自 pin 后声称快照一致。

Android 控件渲染、loading、点击防重、焦点、语义与布局由宿主负责。为主题化设置原生 View 背景时要避免平台 background tint 再次给原图染色。ThemeSurfaceDrawable 的文字保护区域须随文字、布局和字体缩放更新。

## 28. 使用真实 AppDefaultTheme 与 DefaultThemeProvider

以下是仅含两个颜色 Token 的完整最小示例；用于说明真实构造 API，不代表完整 App Design System。

```kotlin
import dev.skinkit.contract.*
import dev.skinkit.defaults.*

val appId = "example.app"
val builder = TokenRegistry.builder(appId)
val background = builder.color("color.background", ColorRole.BACKGROUND)
val text = builder.color("color.text.primary")
builder.contrastPair(text, background, 4.5)
val registry = builder.build()

val defaults = AppDefaultTheme.builder(appId, "1.0.0")
    .put(ColorMode.LIGHT, background, ColorValue.argb(0xFFF7F8FA.toInt()))
    .put(ColorMode.LIGHT, text, ColorValue.argb(0xFF1C1C1E.toInt()))
    .put(ColorMode.DARK, background, ColorValue.argb(0xFF0F1012.toInt()))
    .put(ColorMode.DARK, text, ColorValue.argb(0xFFF5F5F7.toInt()))
    .build()

val provider = DefaultThemeProvider(defaults, registry)
provider.completenessReport.requireComplete()
provider.pin().use { view ->
    val canvasArgb = view.getColor(background).toArgb()
    val textArgb = view.getColor(text).toArgb()
    // 将这两个值交给宿主控件；此处不执行资源 I/O。
}
provider.updateConfiguration(VisualConfiguration(colorMode = ColorMode.DARK))
```

`AppDefaultTheme` 是不可变数据，不是可实现的 interface。`DefaultThemeProvider` 不接收旧草案的 safeDefaults 参数。实际 App 应在冻结同一 Registry 前注册所有必要视觉，并在两模式补齐值、组件字段/状态及本地资源目录；完整性失败必须修正，不能靠第四级兜底掩盖。

需要换肤时在依赖注入入口换用 `CoreThemeProvider` 和 `CoreThemeSession`，公共 getter 不变。App Extension 与 Common 的字段覆盖由 Core 执行。覆盖 primary 不会自动重算任意其它 Token；主题作者必须提供一致的最终组件状态值，或由明确的宿主配色适配器重新生成相应值。不得承诺不存在的通用依赖图求值。

## 29. UI Code Review Checklist

- [ ] 检查了工作区、分支和最近稳定提交；没有覆盖已有工作或破坏历史。
- [ ] 页面只表达业务结构，视觉由公共组件与统一 Contract 提供。
- [ ] 没有散落视觉字面量、伪装为局部常量的硬编码或未映射的平台默认样式。
- [ ] 新 Token 有语义、类型、默认值、Light/Dark、覆盖规则与维护归属。
- [ ] AppDefaultTheme 是完整正式主题；未来缺失覆盖能够逐字段回退。
- [ ] 字体层级、间距、圆角、图标、颜色和阴影遵守本规范。
- [ ] 组件所需的 pressed/loading/disabled/focus/selected 等状态齐全。
- [ ] 输入框错误、离线、空内容和加载失败有明确恢复方式。
- [ ] 字体缩放、对比度、触控目标、语义标签和键盘焦点得到验证。
- [ ] 手机/平板/桌面、横竖屏和窗口变化可用，未简单拉伸。
- [ ] Glass 有局部范围、性能依据、减少透明度支持与实色 fallback。
- [ ] App 专属组件通过 Extension，未增加私有主题旁路。
- [ ] 默认主题、可选皮肤与模块变更范围清晰；没有为风格复制业务页面，未把未配置服务标为可用。
- [ ] 每个可验证节点已有清晰提交与验证记录。

## 30. Definition of Done

只有同时满足以下条件，才可声明某 App 的 Default Theme UI 完成：

1. Light/Dark AppDefaultTheme 具备完整 Token；组件无直接设计字面量，正式 Contract 接入完成。
2. 主要公共组件及业务 Extension 具备所需交互状态，页面正确复用。
3. 核心流程与 loading/empty/error/offline 等异常场景可操作、可理解、可恢复。
4. 验证目标窗口与横竖屏，默认及放大字体无关键内容裁切或操作丢失。
5. 对比度、焦点、触控目标与语义检查通过；减少动态效果/透明度可用。
6. 提供代表性页面的 Light/Dark 截图、关键状态截图与验证记录。最低覆盖首页、内容列表、详情、输入/搜索及弹层；按 App 实际功能调整。
7. 完成 UI Code Review，处理阻断问题；Token 源、组件说明与必要变更记录一致。
8. 公共组件、Token 与页面 UI 按节点提交，存在可识别的稳定提交与回退依据。

适当验证包括主题完整性检查、硬编码扫描、主题切换检查、关键交互与视觉验收。自动化主题检查应验证完整性和解析行为；不为每个建议常量编写镜像测试。启用当前 Core 的宿主须补充实际 override 解析器的回退、类型、资源失败、预览隔离与生命周期测试。

## 31. 视觉验收标准

默认主题必须本身完成度高、舒服耐看，不能以「以后会有皮肤」为理由留下粗糙样式或缺失状态。验收使用真实内容、长文本、空内容、图片失败、Light/Dark 和不同窗口，不只评审一张理想截图。

| 维度 | 通过标准 | 典型不通过表现 |
|---|---|---|
| 信息层级 | 主操作、标题、正文和辅助信息清楚 | 全部粗体、全部品牌色 |
| 留白与密度 | 分组清晰，内容紧凑度适合业务 | 到处套盒子或无规律空隙 |
| 柔和与克制 | 统一圆角、少阴影、有限强调 | 大胶囊、发光、重阴影 |
| 品牌与中性 | 保留品牌识别，基础表面中性 | 默认主题已被强风格主导 |
| 状态与可用性 | 真实状态清楚且可恢复 | 禁用难辨、错误只变红 |
| 可扩展性 | 主题化属性集中且有完整回退 | 固定图标、固定字体和局部色值 |

默认主题应为未来小世界、卡通、复古、科技、暗黑等 Skin 留出显著改变产品观感的空间。当前已有五套演示皮肤验证部分可覆盖能力；其它视觉方向仍是可选设计计划，不能要求每个宿主为此复制多套业务页面。

## 32. 当前交付与后续边界

### 32.1 当前可用内容

- 永久 AppDefaultTheme 与 Contract / Default 0.0.1。
- Core dev.12 的本地包验证、四级回退、隔离预览、显式应用、恢复默认与租约保护。
- Appearance / Android Appearance dev.3 的窗口、按钮、表单、卡片四类外观及独立配色。
- Personal / Personal Android dev.2 和 Photo Android dev.1 的本地照片主题、可复用编辑页、角色级图片布局和持久化。
- “SkinKit 演示” `dev.skinkit.testlab` code10，以及独立的二进制接入 sample-host。两者均不是正式上架产品验收结论。

### 32.2 五套内置风格

| 风格 | 主题 ID | 当前包版本 | 主要外观 |
|---|---|---|---|
| 常用 App | local.testlab.everyday | 1.1.1 | 资源为零的普通纯色界面；四角色明确 Solid，无装饰空白 |
| 怀旧 | local.testlab.retro | 1.1.0 | 暖纸、复古配色与插画条纹 |
| 卡通 | local.testlab.cartoon | 1.1.0 | 明亮配色、圆润控件与原创插画 |
| 田园花草 | local.testlab.garden | 1.1.0 | 全窗口田园场景与花草细节 |
| 可爱宠物 | local.testlab.pets | 1.1.0 | 全窗口宠物场景、控件插画及可选受限动画 |

每套均有 Light / Dark。常用 App 的纯色风格是成功应用的 Common 包，不能与“恢复应用默认”的 APP_DEFAULT 混为一谈。当前确实是五套内置包；原文的 Clean Minimal、Soft & Friendly、Glass & Layered、Premium Dark、Neo-Brutalism、Retro Digital 六种方向仍是设计参考，不是又一组已交付六套皮肤。

AppDefaultTheme 始终采用克制的默认基准，不因可选插画皮肤存在而删除。宿主不为五套风格复制五套页面；同一组公共组件从包和默认值解析外观。升级 APK 不应偷偷启用新包版本；版本更新须显式操作并保留对应的配色选择。

### 32.3 未完成或未承诺

Store / Commerce / Community 有接口与测试路径，但本文不声称已连接线上商城、真实支付、社区发布或账户系统。当前个人照片编辑没有服务器、AI 分割、AI 生成或公开分享入口。微信专有 Android 适配器不在本次闭源二进制交付包中。

图像主题不提供九宫格拉伸、任意动画/Lottie、SVG/GIF/WebP 皮肤资源或任意布局代码；照片导入可接受受限 WebP 后规范化成 PNG，与 skinpack 直接接受 WebP 是不同能力。Compose、iOS、桌面、生产发行者签名、全面无障碍/性能认证均不能从本次交付推定。

## 33. 长期维护与变更记录

Token 源集中维护；业务页面不持有设计副本。视觉修订应先修改默认主题与公共组件，再检查受影响页面；记录 Token 新增、重命名、弃用、默认值变化和 Extension 兼容性。破坏性 Contract 变更需要迁移方案，不能通过静默回退掩盖。

品牌调整同时评审 Light/Dark 与全部状态；组件新增时补齐状态、可访问性和响应式要求。未来皮肤接入不得破坏 AppDefaultTheme 的独立可用性，也不得让皮肤缺失成为核心业务不可用的原因。

| 版本 | 日期 | 变更 |
|---|---|---|
| V1.0 | 2026-10-05 | 原始设计基准、永久默认主题、Token/组件与验收要求 |
| V1.0 实现修订 | 2026-10-07 | 对齐真实 Contract/Default/Core API、五套内置风格、可选个人照片主题、二进制集成与明确测试边界 |

## 34. 当前图片表面与配色规则

### 34.1 统一四角色

`AppearanceTokens` 在宿主 Registry 冻结前一次注册四个 Common Drawable Token：`drawable.appearance.button`、`drawable.appearance.window`、`drawable.appearance.form`、`drawable.appearance.card`。注册后每个角色都必须有完整 Light / Dark 默认与后备。未启用模块的宿主不必增加这些 Token。

值为 Solid 时采用普通色块和紧凑布局；值为 Local 时使用经过校验的资源引用和实色 fallback。必须根据实际 Drawable 类型决定布局，不能根据“常用 App”等显示名硬编码。全局图片、每角色图片、图片模式与配色分别管理。

### 34.2 宿主布局与文字保护

| 角色 | 当前共享渲染策略 | 宿主必须保留的安全区域 |
|---|---|---|
| BUTTON | 整个按钮背景；等比例绘制，内置插画 TILE 横向重复 | 原生最小触控尺寸与文字矩形实色底；不增加空白插画行 |
| WINDOW | 全内容区域；场景按比例 FILL，纹样按 TILE | 文字置于可读实色表面；系统栏/刘海使用实色保护 |
| FORM | 逻辑末端 48dp 装饰区域，默认 FIT | 有图时至少 64dp 末端 padding；无图恢复普通 padding |
| CARD | 顶部 64dp 装饰带 | 有图时正文 top padding 至少 80dp；无图通常恢复 16dp |

当前 `SurfaceLayoutPolicy` 为这些策略提供默认值；它们是共享 Renderer 的安全/布局约束，不代表皮肤可重排业务页面。按钮默认最小高度 48dp、上下内容 padding 各 14dp；字号放大可自然增加高度，不能挤压触控区。文字保护矩形额外使用横向 8dp、纵向 4dp 安全边距并裁剪在按钮内。

内置按钮插画可以在绘制时排除透明外边距后等比例铺满高度，保持原文件不变；个人照片的“完整平铺”必须保留完整源图及透明留白，不能沿用该裁边策略。图片不拉伸、不染色。Light / Dark 使用同一图片字节，切换配色仅改变底色/文字和状态值；深色窗口可有共享 Renderer 的轻量遮罩，不等于用遮罩代替完整 Dark 主题。

### 34.3 独立配色

`AccentChoice` 的稳定 ID 为 blue / green / purple / rose / amber，空值表示使用主题自身默认。保存 ID，不保存枚举 ordinal。恢复配色只清除 override，不换图、不提交隔离预览。

`AccentPalette.from(seed, darkMode, canvasArgb, surfaceArgb)` 生成正常/按压/焦点/禁用成对的背景与文字；传入的 canvas / surface 必须是已确定的不透明实色。每对前景/背景保证至少 4.5:1，并不证明图片上任意位置都有同样对比度。必要时 canvas 与 surface 使用不同 accent；不能把同一前景色任意复用到所有背景。

## 35. 当前个人主题编辑体验

### 35.1 操作与三态

入口“我的主题 / 创建主题”允许创建和编辑本地草稿。用户可选全局图片，各角色分别“跟随全局”“独立图片”“不用图片，仅用颜色”。清除全局只影响继承角色，独立图片和显式无图角色保持。无图必须实际输出 Solid，不能回退露出其他主题旧图。

配色独立于图片。图片水平/垂直位置使用规范化 focus；继承全局的角色共享该图片 focus，独立图片保留自己的 focus。每角色图片模式和大小则完全独立，即使共享同一张全局图片也不互相修改。

### 35.2 图片布局

- 原布局：一般为“铺满”，FORM 为“适应”；大小为 100%–200%。FILL 放大允许裁切，通过 focus 调整取景并约束边缘。
- 完整平铺：25%–100%。保留整张源画布与比例。按钮单行重复，100% 先适配高度，极宽图也适配宽度；缩小增加横向副本，行在剩余空间内上下移动。顶部/底部保持完整，左右末端副本可被边界裁切。
- 其它角色在自己的绘图区双轴平铺，基准图案高度上限 80dp。仅绘图区边界副本允许部分裁切。
- 切换模式回到该模式 100%；“恢复默认布局 · 100%”回原布局，保留图片、focus、配色和其他角色设置。
- 未保存调整立即更新预览；已有可用预览的普通 slider 拖动无需重新解码。每帧最多 4096 tile，极端比例超预算时显示实色后备。

### 35.3 预览、保存与生命周期

“仅保存草稿”不改变当前主题；“保存并应用”保存新版本、验证安装并显式激活；隔离预览不发布当前快照。Cancel / Back 丢弃未保存副本，保留已应用外观。保存后应用失败应清晰告知“已保存、未应用”，避免用户误判数据丢失。

旋转保留未保存名称、配色、角色、图片绑定、focus、mode/scale 和编辑位置；其边界是配置变更内存保留，进程死亡不会自动保存。旧页面与存储所有者排空后才能启动替代页面。中断的选图不得把旧返回值绑定到新请求；已开始提交时排空并恢复当前列表，不重复提交旧版本。

已应用的图片/配色/布局按 themeId/version 冻结，编辑草稿不回写当前版本。删除可编辑草稿不等于删除当前使用的 Core 副本。受保护的当前/恢复/租约版本不被自动清理；容量不足明确报错，不清空用户数据。

### 35.4 照片格式与隐私

仅从系统文件选择器读取用户选定文件，本地处理。输入限制为 16 MiB、单边 8192、16,777,216 像素；支持受限 baseline JPEG、静态 RGB/RGBA PNG 与静态 VP8/VP8L WebP，处理八种 EXIF 方向。HEIC/HEIF、GIF、AVIF、渐进或 CMYK JPEG、动画文件及不支持的色彩/元数据声明明确拒绝。

输出为去元数据 sRGB 静态 PNG，单边至多 1024、单图至多 4 MiB，保留透明度；主题包仍受独立总量预算限制。不扫描图库、不上传、不保存源 URI、不请求持久选图权限；日志不写原图片、路径、EXIF 或位置。私有照片只声明个人本地使用，不能自动改成 CC0 或公共资源。

个人存储 v2 读取 v1 时采用 ORIGINAL / 100% 默认；写入 v2 后不支持旧 code8 反向读取。升级不要求重置。源码回退标签不是用户数据降级工具，不得建议常规清数据或降级 APK 解决布局问题。

## 36. 本次验证结论与验收缺口

基线 RC5 记录了 164 项 focused JVM 测试通过，并保持 Contract / Default 类清单和既有 ABI；旧 Kotlin / Java consumer 的未改字节码运行通过。本次独立二进制 sample-host 基础与可选动画依赖变体分别通过 3 项 JVM 测试和 R8/resource shrink release 构建；基础变体另通过 debug lint，两种 release 均通过随构建执行的 lintVital。该 release 未签名，动画变体检查依赖闭包，不证明屏幕上的动画播放通过。

Android 12 code9 的局部回归已报告按钮 100/50/25% 完整平铺、仅 25% 的上下位置端点、未保存旋转与取消、按钮/卡片缩放独立、恢复布局、测试中的保存应用重启通过。原始报告和像素未收录于云端证据，不在本文冒充独立视觉复核。

尚未建立的设备结果包括 100/50% 位置端点、code9 窗口/表单复测、卡片 25% 单独重启、大字体、TalkBack、所有原生格式与八方向像素、资源压力/超时、实体机、其它 Android 版本和第二宿主实际 UI。code10 的 SDK 集成包装、开发者资源导出入口和 APK 需要对应设备验收，不能由 code9 记录直接推定。

以上只说明已知范围；第 30 节 Definition of Done 的每项仍须针对实际宿主执行。闭源 SDK 指不随包提供 SDK 实现源码，不保证无法反编译、不自动提供商业授权或消除第三方许可证义务。生产接入还需最终依赖、安全、签名、数据升级和目标设备验收。

## 37. 一次付费下载、商用授权与演示边界

正式 App 采用应用商店一次付费购买并下载的方式，不提供应用内购买，不设置额外的 SDK 或接口文档导出购买。安装后提供演示及导出功能。合法购买后允许将 SDK 用于商业项目，不再缴纳后续使用费。

该授权包含以后发布的 SkinKit 集成 App、SkinKit SDK 和接口说明文档的全部更新，无须另付更新费用。价格、目标商店和正式发行条款仍待确定；本文不额外承诺无关 App、定制开发或支持 SLA，也不创设未讨论的转售/转授权安排。第三方依赖和素材的许可证义务继续适用。

当前 code10 是可演示、可导出的开发预览，尚未成为付费商店构建；本次没有市场提交、生产签名或新增支付 SDK/账号/后端。应用介绍页应充分说明实际能力、限制和接入方式，并使用真实的界面截图展示效果；这不代表已创建商店页面或已有本次实机截图。

当前 SDK ZIP 与文档明文嵌入 APK，可直接提取，购买用户也可正常导出。商店付费下载控制初次获取，不保证阻止 APK/导出文件被复制。闭源只表示不提供 SDK 实现源码，不能保证无法反编译。本演示不是 DRM 或应用内购买解锁系统，也不会导出密钥、用户照片或个人主题。
