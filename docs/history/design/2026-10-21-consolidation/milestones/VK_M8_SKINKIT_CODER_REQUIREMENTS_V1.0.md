# VK-M8 SkinKit 集中集成开发要求 V1.0

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。本条覆盖下文此前“暂不自建 Theme”“M0 必须实接 SkinKit”等旧要求；供应方资料与历史要求保留供将来评审，不作为当前强制任务。完整现行范围见 [Flutter Theme 与延后集成决定](../FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前 D1 冻结任务不变，M0 未启动。


## M0 起交付批次规则（2026-10-20）

负责人每批选择 1–3 个完整里程碑并向用户汇报范围与理由；coder 整批开发、自测、冻结后统一交 tester，tester 整批测试并集中报告，缺陷集中回交修复及回归。阶段需求与验收分栏保留，禁止逐问题反复交接，不以合批冒充阶段通过。详见 [协调规则](../MILESTONE_COORDINATION_V1.0.md)。此规则覆盖下文单里程碑立即交测的冲突表述，当前 D1 及 M0 未启动状态不变。


## 阶段调整（2026-10-20）

首次真实 SkinKit 集成与全页 UI 提前到 M0；本工作单的 SDK 安全/许可/主题约束仍有效，M8 负责在 M0 已建框架上完成全真实功能与主题回归，不将首次接入延后到 M8。详见 [M0 UI 总要求](../M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md) 及 M0 开发/测试工作单。


## 用户最新范围约束（2026-10-20，覆盖下文冲突表述）

本阶段实现集成 SkinKit，直接复用其已交付默认外观、主题、Token 和标准样式；**暂不自行设计或新建 VideoKit Theme**，不开发独立主题系统、主题编辑器或自有主题包。SDK 若要求宿主 AppDefaultTheme/Registry/default 数据，仅复用供应方已提供的 hostDefaults/默认值和合法样例做最小必需接线，不新增品牌配色、独立 Token 体系或默认主题设计任务；必需业务控件缺口先列出并用已有标准样式/组件适配，确需新样式范围另评审。

现有 UI PPT 仅保留页面结构与交互参考，里面的深空蓝/青绿等自拟外观不作为当前实现要求，最终样式优先使用 SkinKit 已有方案。下文“永久 AppDefaultTheme”“Light/Dark”“扩展 Token”等要求仅表示真实 SDK 的完整默认回退/适配义务，不代表批准另造一套主题。四级回退和独立核心边界保持，Flutter 桥接仍待实现，文档更新不代表集成验收通过。

日期：2026-10-20。状态：未来 M8 工作单，**当前未派发编码**；不打断 D1 冻结候选。依据 [主要求](../SKINKIT_INTEGRATION_REQUIREMENTS_V1.0.md) SK-01–20 与 [UI 映射](../ui/VIDEOKIT_SKINKIT_UI_MAPPING_V1.0.md)。

1. 先核本地 SDK/许可证/合法获取/实际模块 POM 与构建兼容；只读保留供应方交付。开始实现前确认 Git/分支/工作区状态并保留已有修改，无 Git 时先提交负责人确定追踪方式，不擅自 init/reset/重写历史。
2. Flutter 路线不变，最小依赖 default/contract + Core；按实际功能审 Appearance 等可选模块。集成仅 App UI，纯核心/对外 AAR 不传递 SkinKit，Browser 不强制接入。
3. 接入单一 Registry，复用 SkinKit 已有默认/标准主题、Token、ComponentStyle 和默认构造器；宿主接口需要时只做最小默认数据组装，不新建自有主题/品牌样式体系。冻结稳定 appId/桥接schema，公共组件通过真实 Provider 与 Flutter Adapter 使用解析快照。
4. 实现按 generation 的快照/订阅/read view/异步资源 lease 及原 owner 生命周期；一次渲染一致，不在 UI 主线程同步 IO/重解码，不复制主题解析器。
5. 完成本地包校验/安装/隔离预览/显式应用/恢复默认与模式持久化，四级逐字段回退。默认不依赖 Core/网络/账号。未获批可选模块不加商城/支付/创作等新功能。
6. 首页、播放、图片、多画面、编辑/跟踪、导出、设置及错误/权限页全状态接线；换肤不重建媒体或更改工程/输出，UI 叠加样式不修改导出像素。
7. 手机平板/旋转分屏/中英RTL大字体/键鼠读屏/触摸区/减少动画实测；Glass Solid 明示。Android 构建与真实Release/R8/资源收缩、依赖锁/最终SBOM/NOTICE和许可页一起交付。
8. 集中多功能实现、自检后一次整包冻结交 tester；仅在源码/依赖实际变化或失败修复时必要构建，不按小控件频繁编译交接。附来源hash、源码差异、Token映射、实际测试、失败/未完成项及回退方案。

四平台桥接缺口按 M9 明确方案/权利/验收，Android 集成不宣称其他平台 PASS。所有原 P0、许可证及源只读/安全输出约束不变。
