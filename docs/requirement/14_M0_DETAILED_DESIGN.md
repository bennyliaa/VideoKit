# 14 VK-M0 详细设计：Flutter UI 框架、Fake 与通道

版本：V1.0；日期：2026-11-06；状态：设计评审稿。对应里程碑 [12](12_MILESTONES.md) VK-M0；上位文档 [02](02_SYSTEM_ARCHITECTURE.md)、[03](03_UI_FRAMEWORK_DESIGN.md)、[04](04_PUBLIC_API_CONTRACT.md)、[13](13_ENGINEERING_CONVENTIONS.md)。

> 本文件把 03 的框架设计细化到可以直接开工的程度：每个包的目录与类、UI 内部的状态组织、组件拆分、Fake 的实现方式、Pigeon 通道定义、插件与 add-to-app 桥接的类结构，以及 M0 内需要冻结的默认值。
> 若本文件与 03/04 冲突，以 03/04 为准并回改本文件；本文件新增的决定在 VK-M0 评审时一起冻结。

## 1. 范围

| 本文件覆盖 | 不覆盖（后续里程碑补详细设计） |
| --- | --- |
| `videokit_api`（Dart）类型与接口细化 | Media3 播放与 DataSource 实现（VK-M1） |
| `videokit_ui` 内部架构、全部组件拆分、主题 Token 取值 | 图片解码与分块（VK-M2） |
| `videokit_fake` 时钟、场景、演示画面、演示数据 | 资源预算算法、隔离进程协议（VK-M3） |
| Pigeon 通道定义、`videokit_flutter` 插件骨架（连接 Kotlin Fake） | 导出管线组装（VK-M4/M6） |
| `videokit-ui-android` add-to-app 桥接、`sample-host` 最小示例 | 跟踪实现（Spike 结论后） |
| `videokit_example` 示例 App 结构、M0 测试实现方式 | |

M0 交付后的数据路径：

```text
路径 1（纯 Dart，任意平台）  videokit_ui ─▶ videokit_api ◀─ videokit_fake（Dart Fake）
路径 2（经通道，Android）    videokit_ui ─▶ videokit_api ◀─ videokit_flutter ══Pigeon══▶ Kotlin Fake（videokit-testkit）
路径 3（原生宿主嵌入）       sample-host ─▶ videokit-ui-android ─▶ FlutterEngine(videokit_ui) ─▶ 路径 2
```

路径 2 和 3 在 M0 就打通，目的是让通道协议、纹理注册、生命周期在没有真实媒体能力时先经过测试；M1 起只把 Kotlin Fake 换成真实会话。

## 2. 工作区与包目录

### 2.1 Flutter 工作区

```text
flutter/
├── pubspec.yaml                 # workspace: [videokit_api, videokit_ui, videokit_fake, videokit_flutter, videokit_example]
├── analysis_options.yaml        # 共享规则，见 §11.3
├── videokit_api/lib/
│   ├── videokit_api.dart        # 唯一公共导出
│   └── src/
│       ├── videokit.dart        # VideoKit, VideoKitConfig, VideoKitApiVersion
│       ├── session/             # session.dart, session_state.dart, command.dart, command_result.dart, event.dart
│       ├── media/               # media_source.dart, media_kind.dart, transform.dart, track_info.dart
│       ├── edit/                # edit_project.dart, edit_state.dart, edit_command.dart, timeline.dart, mask.dart, tracking.dart
│       ├── export/              # export_request.dart, export_progress.dart, export_result.dart, precheck.dart
│       ├── host/                # host_action.dart, host_callbacks.dart, navigation.dart
│       ├── error/               # stable_error.dart, error_code.dart
│       ├── capability/          # capabilities.dart
│       └── util/                # value_listenable_stream.dart（ValueListenable ↔ Stream）
├── videokit_ui/lib/
│   ├── videokit_ui.dart
│   ├── l10n/                    # app_en.arb, app_zh.arb, app_zh_Hans.arb；生成代码输出到 src/l10n/gen
│   └── src/
│       ├── theme/               # tokens/, theme_source.dart, theme_scope.dart, default_theme_source.dart, icons.dart
│       ├── foundation/          # selector.dart, command_dispatcher.dart, layout_class.dart, auto_hide.dart, time_format.dart
│       ├── common/              # 公共小组件：vk_icon_button, vk_slider, vk_sheet_host, vk_badge, vk_toast, demo_badge
│       ├── state_view/          # UI-09
│       ├── player/              # UI-01、UI-02
│       ├── image_viewer/        # UI-03
│       ├── host_action/         # UI-04
│       ├── multiview/           # UI-05
│       ├── editor/              # UI-06
│       ├── mask/                # UI-07
│       ├── export/              # UI-08
│       └── shortcuts/           # Intent 与快捷键表
├── videokit_fake/lib/src/       # fake_videokit.dart, fake_session.dart, fake_edit_project.dart, clock/, scenario/, demo/, contract/
├── videokit_flutter/
│   ├── pigeons/videokit_messages.dart
│   ├── lib/src/                 # 生成的 messages.g.dart + 手写适配：flutter_videokit.dart, channel_session.dart, ...
│   └── android/src/main/kotlin/com/videokit/flutter/   # 见 §8
└── videokit_example/lib/        # 见 §10
```

### 2.2 原生侧 M0 模块

| 模块 | M0 内容 |
| --- | --- |
| `kit/videokit-api` | 04 的全部 Kotlin 接口与数据类型 |
| `kit/videokit-testkit` | Kotlin Fake（`FakeVideoKit`、`FakeSession`、`FakeEditProject`、场景脚本、测试图案渲染器）、`VideoKitContractSuite` 初版 |
| `kit/videokit-ui-android` | add-to-app 桥接，见 §9 |
| `flutter/videokit_flutter/android` | 插件，依赖 `videokit-api`；M0 运行时注入 testkit 的 Fake，见 §8.4 |
| `sample-host` | 原生示例宿主：纯引擎页（直接用 Kotlin Fake 画到 SurfaceView）+ add-to-app 嵌入页 |

## 3. `videokit_api`（Dart）细化

### 3.1 通用约定

- 全部数据类为 `@immutable final class`，字段 `final`，提供 `copyWith`、`==`、`hashCode`、`toString`。不引入 `freezed` 等代码生成（减少宿主依赖）；由单元测试覆盖相等性。
- 集合字段对外为 `List.unmodifiable`。
- 时间 `int` 微秒，命名以 `Us` 结尾；坐标 `double` 归一化 0–1。
- 枚举都带一个“未知”回退值（如 `ErrorCode.internalErrorRedacted`、`SessionPhase.unknown` 不提供——状态机枚举不允许未知，协议不匹配时初始化失败）。
- 包内只依赖 `package:flutter/foundation.dart`（`ValueListenable`、`immutable`），不依赖 widgets 层。

### 3.2 会话

`VideoKitSession`、`VideoKitSessionState`、`VideoKitCommand`、`VideoKitCommandResult` 按 [04](04_PUBLIC_API_CONTRACT.md) §3–§4 与 §12 一一对应，Dart 写法示例：

```dart
sealed class VideoKitCommand { const VideoKitCommand(); }
final class Play extends VideoKitCommand { const Play(); }
final class SeekTo extends VideoKitCommand {
  const SeekTo(this.positionUs, {this.mode = SeekMode.closestSync});
  final int positionUs; final SeekMode mode;
}
// Pause, SetSpeed, SetMuted, SetVolume, SelectAudioTrack, SelectSubtitleTrack,
// SetTransform, SetOrientation, SetFullscreen, SetVisibility, SetActiveAudio, HideContentForLock, Release

sealed class VideoKitCommandResult { const VideoKitCommandResult(); }
final class Executed extends VideoKitCommandResult { const Executed(); }
final class Rejected extends VideoKitCommandResult { const Rejected(this.error); final VideoKitStableError error; }
final class Superseded extends VideoKitCommandResult { const Superseded(); }
final class Unsupported extends VideoKitCommandResult { const Unsupported(this.reason); final UnsupportedReason reason; }
final class SessionReleased extends VideoKitCommandResult { const SessionReleased(); }
```

补充 04 未细化、UI 需要的字段：

| 类型 | 字段 | 说明 |
| --- | --- | --- |
| `VideoKitSession` | `ValueListenable<int?> textureId` | 改为可监听：Surface 被回收重建后纹理 ID 可能变化；Fake 为 `null` |
| | `ValueListenable<Size?> videoSize` | 显示方向校正后的画面尺寸，供适配与遮罩坐标换算 |
| | `bool get isDemo` | Fake 实现返回 `true`，UI 据此常驻演示标识（§7.4） |
| `VideoKitSessionState` | `seekingToUs: int?` | 正在执行的 Seek 目标，UI 拖动结束后显示该值直到完成 |
| | `List<HostActionState> hostActions` | 当前动作及其 pending/结果，由会话维护（pending 合并在会话侧做，04 §7） |
| `VideoKitEvent` | `sealed`：`PlaybackEnded`、`SourceReleased`、`HostActionFailed(actionId, error)`、`TransientNotice(code)`、`ErrorRaised(error)` | UI 只把事件用于一次性提示，不从事件重建状态 |

### 3.3 编辑工程（UI 所需部分）

按 [08](08_EDIT_TIMELINE_AND_EXPORT_DESIGN.md) §2 的 Schema 建模，M0 冻结 UI 依赖的只读视图：

```dart
final class VideoKitEditState {
  final EditPhase phase;              // created/preparing/ready/tracking/exporting/completed/failed/cancelling/cancelled/releasing/released
  final int revision;                 // 每次成功的编辑命令 +1；所有异步结果带 revision，过时结果丢弃
  final Timeline timeline;            // 输入、片段、总时长
  final List<MaskTrack> masks;        // 手动/人脸/物体遮罩及关键帧
  final Map<String, TrackingRun> tracking;  // maskId → 进度与 CoverageReport
  final ExportProgress? export;       // 阶段、可估算时的比例、可取消标志
  final bool canUndo, canRedo;
  final EditEstimate estimate;        // 预计时长、预计大小（可能为 null 表示无法估算）
  final VideoKitStableError? error;
}
```

`VideoKitEditCommand`（sealed）：`AddClip`、`SplitAt`、`TrimClip`、`RemoveClip`、`MoveClip`、`AddMask`、`UpdateMaskKeyframe`、`RemoveMaskKeyframe`、`SetMaskStyle`、`SetMaskEnabled`、`RemoveMask`、`StartTracking`、`CorrectTracking`、`CancelTracking`。拖动等连续操作在 UI 侧只在手势结束时提交一次命令（§6.3），中间态是 UI 本地视觉状态。

## 4. `videokit_ui` 内部架构

### 4.1 分层

```text
公开组件（VideoKitPlayer、VideoKitEditor …）  —— 宿主唯一可见的 Widget，参数稳定
    │ 创建并持有
控制器（PlayerController、EditorController …） —— ChangeNotifier；组合“会话状态 + UI 本地视觉状态”
    │ 订阅 / 发命令
videokit_api（会话、工程）                     —— 状态唯一权威
```

- 控制器是 `videokit_ui` 内部类，不导出；宿主只操作会话或工程。需要从外部控制 UI 的场景（如宿主按钮“显示控件”）通过公开组件的 `VideoKitPlayerHandle`（`GlobalKey` 获取的有限方法：`showControls()`、`hideControls()`、`openPanel(PanelId)`）提供。
- 不使用 Provider/Riverpod/Bloc；用 `InheritedNotifier` 把控制器下发给子组件，子组件用 `VkSelector` 订阅需要的片段。

### 4.2 选择性重建 `VkSelector`

会话状态每秒多次变化（进度），整个控制栏重建代价高。

```dart
class VkSelector<S, T> extends StatefulWidget {
  const VkSelector({required this.listenable, required this.select, required this.builder, this.equals});
  final ValueListenable<S> listenable;
  final T Function(S state) select;          // 只取需要的字段
  final Widget Function(BuildContext, T value) builder;
  final bool Function(T a, T b)? equals;     // 默认 ==
}
```

- 进度条、时间文字单独订阅 `positionUs`/`bufferedUs`；按钮组只订阅 `phase`/`muted` 等，进度变化不重建按钮。
- 进度刷新上限：UI 侧不做额外节流，原生侧已采样（默认 4 Hz，拖动时 15 Hz，见 §12）。进度条动画在两次采样间用 `Ticker` 按当前速度插值，避免跳动；收到真实值即校正。

### 4.3 命令派发 `CommandDispatcher`

每个控制器持有一个派发器，统一处理：

| 规则 | 实现 |
| --- | --- |
| 按钮防抖 | 同一命令类型在上一次未返回前再次点击：播放/暂停这类切换命令以最后一次意图为准（合并），其他命令忽略 |
| 连续 Seek | 拖动中每 ≥100 ms 发一次 `SeekTo(mode: preview)`；松手发 `SeekTo(mode: closestSync)`；之前的返回 `Superseded` 时静默 |
| 结果反馈 | `Rejected` → 轻提示（错误码文案）；`Unsupported` → 按钮置灰并显示原因（不再次可点）；`SessionReleased` → 控制器进入只读并显示状态视图 |
| 异常 | Future 抛出的异常转成 `INTERNAL_ERROR_REDACTED` 提示，不向上抛 |
| 生命周期 | 控制器 `dispose` 后到达的结果直接丢弃 |

### 4.4 控件显隐 `AutoHidePolicy`

- 默认显示 3 s 后自动隐藏（宿主可配，§12）。
- 不自动隐藏的条件（任一成立）：暂停/结束/错误状态；正在拖动；面板打开；键盘或读屏焦点在控件内（`FocusNode.hasFocus` 与 `MediaQuery.accessibleNavigation`）；鼠标悬停在控件区域；HostAction pending。
- 控件可见性是 UI 状态，不是会话命令：显隐变化时通过回调 `onControlsVisibilityChanged` 通知宿主，并在 add-to-app 下经桥接发给原生宿主；`VideoKitSessionState.controlsVisible` 由插件同步写回，供原生纯引擎宿主读取。

### 4.5 面板与浮层，不依赖 Navigator

VideoKit 组件可能被放进宿主任意页面，不能假设有 `Navigator`、`Overlay` 或 `Scaffold`。

- 每个公开组件内部自带 `VkSheetHost`（`Stack` + 自管理的面板栈）：底部面板（紧凑布局）、侧边面板（中等及以上）、菜单、轻提示都在组件自己的边界内显示。
- 返回键/Esc：组件内部用 `PopScope`（有面板时拦截并关闭面板）；无面板时不拦截，交给宿主。
- 全屏：组件不自己切换路由，只发 `SetFullscreen` 并回调宿主 `onFullscreenRequested`；Flutter 宿主示例中由示例 App 推一个全屏路由并把同一会话传进去（会话不重建）。

### 4.6 布局分级 `VkLayoutClass`

```dart
enum VkLayoutClass { compact, medium, expanded }   // <600, 600–839, ≥840（逻辑像素，按组件自身约束宽度，不按屏幕宽度）
```

用组件自己的 `LayoutBuilder` 约束判断，这样多画面里的小槽、分屏、宿主侧栏中的播放器都按实际可用空间排版。字体放大时（`textScaler` > 1.3），控制栏在同一分级下进一步把次要按钮移入溢出菜单（按 `displayPriority`）。

## 5. 组件拆分

### 5.1 UI-01 播放器 `VideoKitPlayer`

公开参数：

```dart
VideoKitPlayer({
  required VideoKitSession session,
  List<VideoKitHostAction>? hostActions,            // 也可经会话 updateHostActions
  Widget Function(BuildContext, bool controlsVisible)? hostPanel,
  ValueChanged<bool>? onControlsVisibilityChanged,
  ValueChanged<NavigationRequest>? onNavigationRequested,   // 上一个/下一个
  ValueChanged<bool>? onFullscreenRequested,
  VoidCallback? onEditRequested,                    // 编辑入口；为 null 时不显示按钮
  VideoKitPlayerOptions options = const VideoKitPlayerOptions(),   // 自动隐藏时长、手势开关、可见按钮集合
})
```

内部层次（`Stack`，自下而上）：

| 层 | 组件 | 说明 |
| --- | --- | --- |
| 1 画面 | `VkMediaSurface` | `textureId != null` → `Texture`；否则 `DemoPicture`（Fake 演示画面）；外包 `VkTransformView`（适配/缩放/平移/旋转矩阵） |
| 2 手势 | `PlayerGestureLayer` | 轻触显隐、双击切换适配、双指缩放、平移；左右区域横向拖动 Seek（可关）；手势进行中的预览值是本地状态 |
| 3 状态 | `VideoKitStateView`（UI-09） | 加载/缓冲/错误层，按 `phase` 与 `error` 选择，见 §5.9 |
| 4 控件 | `PlayerControls` = `PlayerTopBar`（返回占位、标题、`HostActionBar`、更多）+ `PlayerCenterControls`（快退/播放暂停/快进）+ `PlayerBottomBar`（`VkSeekBar`、时间、倍速、音量、轨道、方向、全屏、编辑） | 按 `VkLayoutClass` 选择按钮集合 |
| 5 宿主面板 | `HostPanelSlot` | 调用 `hostPanel(controlsVisible)`；显隐动画与控件同步 |
| 6 面板 | `VkSheetHost` | `TrackSettingsSheet`（UI-02）、更多菜单 |
| 7 标识 | `DemoBadge` | `session.isDemo` 时常驻，不随控件隐藏 |

`VkSeekBar`：自绘（`CustomPainter`），显示已播放、缓冲、拖动预览值；悬停/拖动时上方显示时间气泡；无障碍提供 `increase/decrease`（步长 10 s）与 `Semantics.value`（“1 分 05 秒，共 12 分 30 秒”）。

### 5.2 UI-02 轨道与设置面板 `TrackSettingsSheet`

三个分组：音轨（单选）、字幕（单选，含“关闭”）、倍速（0.5/0.75/1/1.25/1.5/2，按能力过滤）。列表为空时显示“此视频没有可选音轨/字幕”，不显示空白面板。选择后立即发命令，面板保持打开，选中态以会话状态回显为准（命令被拒时自动回到原选中项并提示）。

### 5.3 UI-03 图片查看器 `VideoKitImageViewer`

- 结构与播放器相同的分层，但控件集合不同：顶栏（标题、宿主动作、信息）、底栏（适应/原尺寸、旋转、动图播放暂停、页码）。不包含任何视频专属控件（由组件类型保证，而不是隐藏）。
- 缩放：`VkTransformView` 共用；缩放到超过“适应”时显示小地图 `MiniMap`（右下）。
- 翻页：左右滑动或按钮发 `onNavigationRequested(previous/next)`，宿主决定是否有下一张；到达边界时宿主返回 `NavigationResult.unavailable`，UI 回弹并轻提示。

### 5.4 UI-04 宿主动作条 `HostActionBar`

布局算法：

1. 过滤 `placement`，按 `displayPriority` 降序、同优先级按传入顺序。
2. 可用宽度 ÷ 按钮宽（48 dp 最小触控 + 间距）得出可放数量 n；超出部分与 `OVERFLOW` 的动作一起进溢出菜单。
3. 字体放大或紧凑布局时 `SECONDARY_BAR` 整组并入溢出菜单。

状态：`enabled=false` 置灰且读屏说明“不可用”；`selected` 填充主色；`pending` 显示环形进度并合并重复点击；`badgeText` 显示角标（最多 3 字符，超出显示“…”）。失败事件 `HostActionFailed` → 轻提示带“重试”按钮。

### 5.5 UI-05 多画面 `VideoKitSlot` / `VideoKitSlotGrid`

- `VideoKitSlot(session, {onActivateAudio, onTap, onLongPress})`：画面 + 角标（发声/静音、加载、降级、错误）。不含控制栏；点击行为由宿主决定（进入单屏或切换发声）。
- `VideoKitSlotGrid(slots, {layout: auto|2x2|3x3|3x4})`：`auto` 按数量与 `VkLayoutClass` 选择列数；最多 12 槽。
- 发声：点击“发声”角标调用 `onActivateAudio(sessionId)`，由宿主/资源协调方决定后对目标会话发 `SetActiveAudio(true, epoch)`（唯一音频规则在 07 §4，UI 不自己互斥）。
- 单槽错误只影响该槽：显示紧凑错误占位（图标 + 一行原因 + 重试），网格其他槽不重建（每槽独立 `VkSelector`）。
- 降级角标读 `resourcesHeld`/能力结果，例如“已降为低分辨率”“已暂停以释放解码器”。

### 5.6 UI-06 编辑器 `VideoKitEditor`

```text
expanded：   [预览 + 传输控制]        [属性面板]
             [时间线（全宽）                  ]
compact：    [预览]
             [工具条：分割 裁剪 删除 打码 导出]
             [时间线]
             属性面板 → 底部面板
```

- `EditorController`：持有 `VideoKitEditProject` 与其 `previewSession()`；维护本地状态：选中片段、时间线缩放 `pxPerSecond`、拖动中的临时位置。
- 时间线 `TimelineView`：
  - 自绘 `TimelinePainter`（刻度、片段块、缩略图占位、遮罩区间行、播放头），横向滚动用 `Scrollable` + 自定义 `ViewportOffset`。
  - 坐标换算 `TimelineScale`：`x = (tUs / 1e6) * pxPerSecond - scrollX`；缩放范围 10–400 px/s，双指或 Ctrl+滚轮缩放时以焦点为中心保持时间不变。
  - 吸附：拖动边缘在 8 dp 内靠近播放头、片段边界、关键帧时吸附，并触发一次轻触觉反馈。
  - 片段操作：长按拖动重排（拖动中显示插入指示线，松手提交 `MoveClip`）；拖动片段两端裁剪（松手提交 `TrimClip`）；在播放头处“分割”提交 `SplitAt`。
- 撤销/重做按钮读 `canUndo/canRedo`；Ctrl+Z / Ctrl+Shift+Z。
- 多输入：“添加视频”调用宿主回调 `onPickSourcesRequested`（宿主选择文件后调用 `project.addSource`）；兼容性说明（快速拼接/需转码）读工程能力结果显示在属性面板。
- 预计时长与大小显示在底部状态行；`estimate` 为 null 时显示“无法预估”，不显示假数字。

### 5.7 UI-07 打码与跟踪 `MaskEditor`

在编辑器中作为模式切换进入（同一 `EditorController`，不新建页面）。

- `MaskOverlay`：叠在预览画面上，画遮罩框（归一化坐标 × `videoSize` 换算到 `VkTransformView` 内的显示矩形），手柄 8 个 + 移动区域；命中测试优先手柄，手柄触控区不小于 24 dp。
- 关键帧：在当前播放头位置修改框即生成/更新关键帧（松手提交 `UpdateMaskKeyframe`）；关键帧之间的插值由 API 给出（UI 不自行插值，保证与导出一致）。
- 遮罩列表 `MaskListPanel`：开关、样式（马赛克/模糊）、强度滑杆、删除。
- 人脸跟踪：“检测人脸”→ 画面上显示候选框（编号）→ 点选目标 → `StartTracking`；进度条显示 `TrackingRun.progress`；可取消。
- 物体跟踪：点选或框选画面区域 → `StartTracking(kind: object, seedRegion)`。
- 状态轨道 `CoverageStrip`：在时间线遮罩行下方按 `CoverageReport` 绘制四种状态，颜色 + 图案（LOW 斜线、AMBIGUOUS 点、LOST 叉）+ 图例，满足“不只靠颜色”。
- 纠正：在 LOST/AMBIGUOUS 区间点“纠正”→ 拖框 → `CorrectTracking`；之后区间显示“重新计算中”。
- 导出前检查：存在未覆盖区间时导出按钮进入 `CoverageCheckSheet`，列出区间并可逐个跳转；处理完或改为整段手动遮罩前不能确认导出。

### 5.8 UI-08 导出 `ExportPanel`

状态映射（读 `VideoKitEditState.export` 与 `phase`）：

| 条件 | 显示 |
| --- | --- |
| 未开始 | 预设选择（来自能力 `outputFormats`）、参数摘要、`checkExport` 预检结果（Sink 能力、空间、覆盖检查） |
| `exporting` | 阶段步骤条（准备/跟踪/编码/校验/写入），当前阶段有比例时显示百分比，否则显示不确定进度；“取消”按钮 |
| `cancelling` | “正在取消…”，按钮禁用 |
| `cancelled` | “已取消，未生成文件”（或“已删除部分输出”，取决于 Sink 报告） |
| `failed` | 错误码文案 + 建议操作按钮（释放空间/降低质量/重试） |
| `completed` | 成功摘要（时长、大小、格式）；宿主提供的“打开/分享”动作；Fake 时追加“演示模式：未生成真实媒体文件” |

导出进行中允许离开面板（宿主决定），面板重新打开时按工程状态恢复显示。

### 5.9 UI-09 状态视图 `VideoKitStateView`

纯函数映射 `(phase, error, mediaKind) → StateViewModel(icon, titleKey, detailKey, actions)`，集中放在 `state_view/state_mapping.dart`，便于测试和宿主文案覆盖：

| 错误码（示例） | 标题 | 动作 |
| --- | --- | --- |
| `SOURCE_DISCONNECTED`、`SOURCE_TIMEOUT` | 连接中断 | 重试 |
| `SOURCE_PERMISSION_DENIED` | 无权访问此文件 | 回调宿主（宿主处理授权） |
| `UNSUPPORTED_*` | 不支持此格式（附具体是容器/视频编码/音频编码） | 若有其他音轨：选择其他音轨 |
| `CORRUPT_MEDIA` | 文件已损坏或不完整 | — |
| `DECODER_RESOURCE_EXHAUSTED` | 资源不足，已暂停 | 重试 |
| `TRACKING_LOST` | 跟踪丢失 | 纠正目标 |
| `OUTPUT_SPACE_INSUFFICIENT` | 存储空间不足 | 释放空间（宿主动作）/ 降低质量 |
| 未知码 | 出现问题 | 重试（若 `retryable`） |

动作统一经 `onStateAction(StateAction)` 交给所在组件处理；表中没有动作时只显示说明，不放无效按钮。

## 6. 交互细则

### 6.1 手势冲突

- 画面层手势优先级：双指缩放 > 平移（仅已放大时）> 横向拖动 Seek（仅未放大时）> 轻触。
- 用 `RawGestureDetector` 组合 `ScaleGestureRecognizer` 与自定义横向拖动识别器；放大状态决定是否向外层 `PageView`（宿主翻页）让出横向手势。
- 编辑器时间线横向手势只在时间线区域，与预览互不干扰。

### 6.2 键盘

`shortcuts/vk_shortcuts.dart` 定义 Intent：`TogglePlayIntent`、`SeekByIntent(±5s/±30s)`、`VolumeByIntent(±0.1)`、`ToggleMuteIntent`、`ToggleFullscreenIntent`、`CloseOrExitIntent`、`UndoIntent`、`RedoIntent`、`SplitIntent`。组件根部包 `Shortcuts` + `Actions` + `FocusScope`；宿主可以传 `shortcutsOverride` 修改或禁用（避免与宿主快捷键冲突）。

### 6.3 连续操作只提交一次

拖动进度、裁剪、重排、遮罩框拖动、音量拖动：手势中只改 UI 本地视觉状态，结束时提交一次命令；命令被拒绝时动画回到会话状态中的值。这样会话侧不会收到大量中间命令，撤销栈也只有一条记录。

## 7. 主题实现

### 7.1 类结构

```dart
abstract interface class VideoKitThemeSource {
  int get themeSchemaVersion;                    // 当前 1
  VideoKitThemeData resolve(Brightness brightness, VideoKitThemeOverrides? overrides);
  Listenable? get changes;                       // 主题源变化（宿主换肤、SkinKit）时通知
}

@immutable
final class VideoKitThemeData {
  final VkColors colors; final VkTypography typography; final VkSpacing spacing;
  final VkRadii radii; final VkMotion motion; final VkSizes sizes;
  final VideoKitIcons icons;
  ThemeData toMaterialTheme(ThemeData base);     // 把 Vk* 作为 ThemeExtension 注入，并设置 colorScheme
}

class VideoKitThemeScope extends StatelessWidget { ... }   // 宿主可放在任意层级；未放置时组件使用 DefaultThemeSource
```

- 组件读取：`VkTheme.of(context).colors.primary`（扩展方法，内部从 `Theme.of(context).extension<VkColors>()` 取，缺失时回退默认）。
- 宿主覆盖 `VideoKitThemeOverrides`：每个 Token 可选覆盖；只给主色时，派生色（`primarySoft`、`onPrimary`）按对比度规则自动计算（WCAG AA 4.5:1，不满足时选黑/白）。
- `themeSchemaVersion` 变化时新增 Token 必须有默认值；`DefaultThemeSource` 覆盖全部 Token。

### 7.2 Token 取值（UI 设计稿 V1.0 建议值，评审后冻结）

来源：[VideoKit_UI_Design_V1.0.pptx](VideoKit_UI_Design_V1.0.pptx) 第 4 页。冻结后替换 03 §5.4 的“中性占位取值”。

| Token | 深色 | 浅色 |
| --- | --- | --- |
| `background` | `#0E1015` | `#F4F5F7` |
| `surface` | `#171A21` | `#FFFFFF` |
| `surfaceVariant` | `#1F232C` | `#F0F1F4` |
| `surfaceHigh` | `#2A2F3A` | `#E3E6EB` |
| `outline` | `#343A46` | `#D5D9E0` |
| `textPrimary` / `textSecondary` / `textTertiary` | `#EEF0F4` / `#A3A9B5` / `#6E7582` | `#15181E` / `#4B5260` / `#8A909B` |
| `primary` / `onPrimary` / `primarySoft` | `#FF7A45` / `#1A0E08` / `#3A2219` | `#E8590C` / `#FFFFFF` / `#FFE8DC` |
| `selection` | `#4CC9F0` | `#4CC9F0` |
| `success`（TRACKED） | `#34D399` | 同左 |
| `warning`（LOW_CONFIDENCE） | `#FBBF24` | 同左 |
| `trackAmbiguous` | `#A78BFA` | 同左 |
| `error`（LOST） | `#F87171` | 同左 |
| `demoBadge` | `#EC4899` | 同左 |
| `scrim` | 黑 60% | 黑 60% |
| 画面背景（播放器） | 始终 `#000000`，不随主题 | — |

其他 Token：

| 组 | 取值 |
| --- | --- |
| 文字 | title 20/28 SemiBold；body 14/20；label 13/18 Medium；caption 12/16；timecode 13 等宽数字（`FontFeature.tabularFigures()`）。字体族默认跟随平台（Android Roboto / Noto Sans CJK），不打包字体 |
| 间距 | xs 4、sm 8、md 12、lg 16、xl 24 |
| 圆角 | sm 6、md 10、lg 16、full 999 |
| 动效 | fast 120 ms、normal 200 ms、slow 320 ms，曲线 `easeOutCubic`；减少动画时全部为 0（显隐改为直接切换） |
| 尺寸 | 最小触控 48；控制栏图标 24；进度条 4（拖动时 6，拇指 14）；时间线片段行 56、遮罩行 20、覆盖条 8；遮罩框线宽 2、手柄 10（触控区 24） |

## 8. 通道与插件（`videokit_flutter`）

### 8.1 设计要点

- Pigeon 版本在工程初始化时锁定为当时最新稳定版，写入 `pubspec.lock`；生成 Dart + Kotlin，生成物入库（13 §2.1）。
- 全部 ID 为字符串；会话、工程在原生侧由 `VideoKitRegistry` 按 ID 持有，Dart 侧对象只是代理。
- **命令采用“每命令一个方法”**而不是一个带 sealed 参数的方法：不依赖 Pigeon 对 sealed 类的支持程度，类型最直接；新增命令 = 新增方法（次版本）。
- **状态和事件**走每个对象一条 EventChannel（Pigeon `@EventChannelApi`，若锁定版本不支持则手写 `EventChannel` + 标准编解码，消息体相同）。每条消息是 `SessionUpdateMessage`：完整状态快照（采样后）或一个事件，二者至少一个。Dart 侧收到快照后整体替换 `ValueNotifier` 值（不做增量合并，避免两侧状态不一致）。
- 原生回调 Dart（宿主回调、导航）用 `@FlutterApi`，原生侧带超时。

### 8.2 Pigeon 定义（节选，完整文件 `pigeons/videokit_messages.dart`）

```dart
@ConfigurePigeon(PigeonOptions(
  dartOut: 'lib/src/gen/messages.g.dart',
  kotlinOut: 'android/src/main/kotlin/com/videokit/flutter/gen/Messages.g.kt',
  kotlinOptions: KotlinOptions(package: 'com.videokit.flutter.gen'),
))

const int kChannelProtocolVersion = 1;

class HandshakeRequest  { late int protocolVersion; late String dartPackageVersion; }
class HandshakeResponse { late int protocolVersion; late String nativeKitVersion; late bool demoBackend; }

enum MediaKindMsg { video, imageStatic, imageAnimated, imageUnknown }
enum SessionPhaseMsg { created, binding, ready, playing, paused, buffering, ended, errorRecoverable, errorFatal, releasing, released }
enum SeekModeMsg { preview, closestSync, exact }
enum CommandResultKind { executed, rejected, superseded, unsupported, sessionReleased }

class StableErrorMsg { late String code; late String stage; late bool retryable; late String suggestedAction; String? diagnostic; }
class CommandResultMsg { late CommandResultKind kind; StableErrorMsg? error; String? unsupportedReason; }
class TrackInfoMsg { late String id; String? language; String? label; late bool supported; }
class TransformMsg { late double scale; late double panX; late double panY; late int rotationDeg; late String fit; }

class SessionStateMsg {
  late SessionPhaseMsg phase; MediaKindMsg? mediaKind;
  late int positionUs; int? durationUs; int? bufferedUs; int? seekingToUs;
  late bool playWhenReady; late double speed; late double volume; late bool muted;
  late List<TrackInfoMsg> audioTracks; late List<TrackInfoMsg> subtitleTracks;
  String? selectedAudioTrackId; String? selectedSubtitleTrackId;
  late TransformMsg transform; late String orientation; late String visibility;
  late bool activeAudio; late bool controlsVisible; late bool resourcesHeld;
  StableErrorMsg? error; late List<HostActionStateMsg> hostActions;
  int? videoWidth; int? videoHeight;
}

class EventMsg { late String type; String? actionId; StableErrorMsg? error; String? noticeCode; }
class SessionUpdateMessage { late String sessionId; late int seq; SessionStateMsg? state; EventMsg? event; }

class MediaSourceMsg {
  late String mediaToken; late MediaKindMsg mediaKind; String? displayName;
  int? knownLength; String? mimeType; String? extension; late bool randomAccess;
  late String sourceRef;     // 原生侧已注册的 SourceFactory 引用：uri:/fd:/registered:<id>/demo:<scenario>
}

@HostApi()
abstract class VideoKitHostApi {
  HandshakeResponse handshake(HandshakeRequest request);
  @async CapabilitiesMsg capabilities(CapabilityRequestMsg request);

  // 会话
  String createSession(SessionConfigMsg config);
  @async CommandResultMsg bind(String sessionId, MediaSourceMsg source, PlaybackStateMsg? initial, List<HostActionMsg> actions);
  @async CommandResultMsg play(String sessionId);
  @async CommandResultMsg pause(String sessionId);
  @async CommandResultMsg seekTo(String sessionId, int positionUs, SeekModeMsg mode);
  @async CommandResultMsg setSpeed(String sessionId, double speed);
  @async CommandResultMsg setMuted(String sessionId, bool muted);
  @async CommandResultMsg setVolume(String sessionId, double volume);
  @async CommandResultMsg selectAudioTrack(String sessionId, String? trackId);
  @async CommandResultMsg selectSubtitleTrack(String sessionId, String? trackId);
  @async CommandResultMsg setTransform(String sessionId, TransformMsg transform);
  @async CommandResultMsg setOrientation(String sessionId, String request);
  @async CommandResultMsg setFullscreen(String sessionId, bool fullscreen);
  @async CommandResultMsg setVisibility(String sessionId, String visibility);
  @async CommandResultMsg setActiveAudio(String sessionId, bool active, int audioEpoch);
  @async CommandResultMsg hideContentForLock(String sessionId, bool hidden);
  void setControlsVisible(String sessionId, bool visible);       // UI → 原生同步，见 §4.4
  @async void updateHostActions(String sessionId, List<HostActionMsg> actions);
  @async PlaybackStateMsg captureState(String sessionId);
  @async PlaybackStateMsg release(String sessionId);

  // 纹理
  int createTexture(String sessionId);          // 返回 textureId；内部创建 SurfaceProducer 并 attachSurface
  void resizeTexture(String sessionId, int width, int height);
  void disposeTexture(String sessionId);

  // 编辑工程：createEditProject / addSource / applyEdit(EditCommandMsg) / undo / redo / snapshot /
  // previewSession / checkExport / export / cancelExport —— 同样每操作一个方法，EditCommandMsg 为 kind + 可选字段
}

@FlutterApi()
abstract class VideoKitCallbacksApi {
  @async HostActionResultMsg onHostActionRequested(HostActionRequestMsg request);
  @async NavigationResultMsg onNavigationRequested(NavigationRequestMsg request);
  @async String onRecoverableError(StableErrorMsg error);   // RecoveryDecision 名称
  void onTextureChanged(String sessionId, int? textureId); // Surface 被回收/重建
}

@EventChannelApi()
abstract class VideoKitEventsApi {
  SessionUpdateMessage sessionUpdates();        // Dart 侧按 sessionId 分发；或每会话一个具名通道
  EditUpdateMessage editUpdates();
}
```

### 8.3 协议规则

| 项 | 规则 |
| --- | --- |
| 握手 | 插件初始化第一个调用 `handshake`；`protocolVersion` 主号不同 → Dart 侧抛 `VideoKitInitException(protocolMismatch)`，UI 显示明确错误，不尝试继续 |
| 顺序 | 每会话 `seq` 单调递增；Dart 丢弃 `seq` 不大于已处理值的消息 |
| 快照 | 原生侧采样：播放中 4 Hz，Seek 拖动中 15 Hz，状态相变立即发送；释放时发送最终快照后关闭该会话的分发 |
| 错误 | 原生方法内部异常一律转成 `CommandResultMsg(rejected, INTERNAL_ERROR_REDACTED)`；只有协议错误（未知 sessionId 之外的编程错误）才以 `PlatformException` 抛出，Dart 适配层转为 `INTERNAL_ERROR_REDACTED` |
| 未知 sessionId | 返回 `sessionReleased`，不抛异常（会话已释放后的迟到调用是正常情况） |
| 线程 | Pigeon 调用在主线程进入；`VideoKitPlugin` 立即切到插件自己的 `CoroutineScope(SupervisorJob() + Dispatchers.Default)` 执行，完成后回主线程回复；任何 I/O 不在主线程 |
| 回调超时 | `@FlutterApi` 调用超时（默认见 §12）→ 记 `HOST_CALLBACK_FAILED`，HostAction 退出 pending 并发出 `HostActionFailed` 事件 |
| 媒体字节 | 不经通道。`MediaSourceMsg.sourceRef` 指向原生已能访问的源；Dart 实现 `readAt` 的情况（04 §12.3）在 M0 不实现，只保留 `registered:` 引用形式 |

### 8.4 Android 插件类结构

```text
com.videokit.flutter
├── VideoKitPlugin            : FlutterPlugin, ActivityAware；注册 HostApi/EventChannel；持有 Registry
├── VideoKitBackendProvider   : 选择后端 —— M0 默认 FakeBackend（来自 videokit-testkit），M1 起 RealBackend；
│                               宿主可通过 VideoKitFlutter.setBackend(...) 在 Application 中指定
├── VideoKitRegistry          : sessionId → SessionHolder；projectId → ProjectHolder；进程内唯一
├── SessionHolder             : 包装 VideoKitSession；收集 state/events → 采样 → SessionUpdateMessage
├── TextureBinding            : 一个 SurfaceProducer；setCallback(onSurfaceAvailable → attachSurface,
│                               onSurfaceCleanup → detachSurface)；尺寸随 videoSize 与组件尺寸更新
├── Mappers.kt                : 原生类型 ↔ *Msg 双向转换（纯函数，单元测试覆盖全部字段）
└── gen/Messages.g.kt         : Pigeon 生成
```

- 插件被多个 FlutterEngine 加载（add-to-app 多实例）时，`VideoKitRegistry` 进程内共享，`VideoKitPlugin` 每引擎一个；每个会话记录所属引擎，引擎销毁（`onDetachedFromEngine`）时释放其全部会话与纹理。
- M0 的 `FakeBackend` 把 Kotlin Fake 会话的测试图案（色块 + 时间码 + 会话 ID 后 4 位）用 `Surface.lockHardwareCanvas` 按 30 fps 画到纹理上，用来验证纹理路径、Surface 回收与重建、多画面多纹理。

### 8.5 Dart 侧适配

`FlutterVideoKit implements VideoKit`（`videokit_flutter`）：

- `ChannelSession implements VideoKitSession`：`state` 为 `ValueNotifier<VideoKitSessionState>`，由 `SessionUpdateMessage.state` 替换；`events` 为 `StreamController.broadcast`；`execute` 按命令类型 `switch` 调对应 HostApi 方法（Dart 3 sealed `switch` 穷尽检查，新增命令时编译器提示）。
- `textureId`：会话首次被 `VkMediaSurface` 显示时惰性 `createTexture`；组件全部卸载后延迟 2 s 再 `disposeTexture`（避免宿主页面切换抖动导致反复重建）。
- `isDemo`：取握手结果 `demoBackend`，M0 下为 `true`，因此经通道路径也常驻演示标识。

## 9. add-to-app 桥接（`videokit-ui-android`）

### 9.1 对外 API（原生宿主）

```kotlin
object VideoKitFlutter {
    fun initialize(app: Application, config: VideoKitFlutterConfig)   // 在 Application.onCreate；可选预热
    fun prewarm()                                                     // 提前创建并缓存引擎组与首个引擎
}

class VideoKitFlutterConfig(
    val videoKit: VideoKit,                       // 宿主创建的原生 VideoKit（M0 为 Fake）
    val prewarmOnInit: Boolean = true,
    val theme: VideoKitThemeOverrides? = null,    // 原生侧传入的 Token 覆盖（颜色以 ARGB Int）
    val strings: Map<String, String> = emptyMap(),// 文案覆盖表，key 同 ARB
)

class VideoKitPlayerFragment : Fragment() {
    companion object { fun newInstance(sessionId: String, options: PlayerEmbedOptions): VideoKitPlayerFragment }
    var listener: VideoKitEmbedListener?          // 控件可见性、导航请求、全屏请求、编辑入口
}
// 同理：VideoKitImageViewerFragment、VideoKitEditorFragment；以及 VideoKitFlutterView（嵌入 View 层级的版本）
```

宿主流程：宿主用原生 API 创建并 `bind` 会话 → 把 `sessionId` 交给 Fragment → Flutter 侧通过 `videokit_flutter` 找到同一会话代理并显示。会话归宿主所有，Fragment 销毁不释放会话（宿主决定何时 `release`），以便旋转、全屏切换时会话不中断。

### 9.2 引擎管理

- 使用 `FlutterEngineGroup` 创建引擎，多个嵌入实例共享 Dart VM 与资源，单个附加引擎的额外内存小于独立引擎。
- 预热：`initialize` 时创建一个引擎运行 `videokitEmbedMain` 入口并放进 `FlutterEngineCache`；第一个 Fragment 直接使用，后续实例从引擎组派生。
- Dart 入口：

```dart
@pragma('vm:entry-point')
void videokitEmbedMain(List<String> args) => runApp(const VideoKitEmbedApp());   // 等待原生经 EmbedApi 下发要显示的组件与 sessionId
```

- 每个引擎一个 `EmbedHostApi`（Pigeon，原生 ↔ Dart）：`showPlayer(sessionId, options)`、`showImageViewer`、`showEditor`、`setTheme`、`setStrings`、回调 `onControlsVisibilityChanged`、`onNavigationRequested`、`onFullscreenRequested`、`onEditRequested`。
- 宿主面板插槽：Fragment 的根布局是 `FrameLayout`（FlutterView + 宿主面板容器），宿主把原生面板 View 加到容器；`onControlsVisibilityChanged` 时桥接按主题动效时长同步显隐。
- 背景透明：`FlutterView` 使用 `TransparencyMode.opaque`（播放器背景为黑，避免透明合成开销）；图片查看器同样不透明。

### 9.3 M0 需实测记录的指标

| 指标 | 方法 |
| --- | --- |
| 包体积增量 | `sample-host` 分别构建“纯引擎”与“嵌入 Flutter UI”两个 release 变体，比较 APK（按 ABI 拆分）与 AAB 下载大小 |
| 首帧耗时 | 冷启动后首次打开播放器 Fragment：从 `newInstance` 到 Flutter 首帧回调（`FlutterUiDisplayListener`），分别测预热与不预热，各 20 次取中位数与 P90 |
| 多实例内存 | 2×2 多画面四个嵌入实例 vs 一个引擎内的 `VideoKitSlotGrid`，`dumpsys meminfo` PSS 对比（用于决定多画面推荐方案） |

记录到能力说明与 M0 测试报告；测试机型按 11 的设备矩阵至少一台中端机。

## 10. 示例 App（`videokit_example`）

```text
lib/
├── main.dart                  # 选择后端：Dart Fake（默认）/ 通道 Fake（Android）
├── mock_host/                 # 模拟 Browser 宿主：假媒体列表、标签/收藏动作、邻近列表、临时 Sink
│   ├── mock_library.dart      # 固定 seed 生成的媒体条目（视频/静态图/动图/损坏/不支持）
│   └── mock_host_actions.dart # 收藏（切换 selected）、加标签（pending 1.5 s 后成功）、删除（总是超时）
├── pages/
│   ├── home_page.dart         # 媒体网格 → 打开播放器/图片
│   ├── player_page.dart       # 单屏播放 + 宿主面板示例（邻近媒体条）
│   ├── multiview_page.dart    # 2×2 / 3×3 / 12 槽
│   ├── editor_page.dart       # 编辑 + 打码 + 导出
│   └── gallery_page.dart      # 组件画廊：每个组件 × 每个状态，供人工走查与 golden 对照
└── debug/
    ├── scenario_panel.dart    # 场景切换、时钟控制（暂停/快进/×10）、重置；仅 debug 构建
    └── settings_panel.dart    # 主题（浅/深/宿主主色）、语言（中/英/伪本地化/RTL）、字体缩放、减少动画
```

- `scenario_panel` 与 `videokit_fake` 只在 `kDebugMode` 下导入（`debug/` 目录通过条件导入在 release 中替换为空实现）；release 构建检查见 §11.4。

## 11. Fake 与测试实现

### 11.1 `videokit_fake`

| 部件 | 实现 |
| --- | --- |
| `FakeClock` | 基于 `Ticker` 的可控时钟；`pause()`、`advance(Duration)`、`speed`；测试中用 `fakeAsync` 驱动，示例 App 中跟随真实帧 |
| `FakeSession` | 实现完整会话状态机（04 §3.1）；非法转换返回 `Rejected`；Seek 延迟、缓冲区间按场景脚本 |
| `FakeEditProject` | 内存中的工程模型与撤销栈；跟踪按场景生成 `CoverageReport`；导出按阶段推进，可取消 |
| `Scenario` | 声明式脚本：`Scenario.normal()`、`.slowLoad(3s)`、`.buffering(at: 20s, for: 2s)`、`.unsupported(videoCodec)`、`.corrupt(at: 45s)`、`.disconnect(at: 30s)`、`.resourceExhausted()`、`.hostActionTimeout('delete')`、`.trackingLost(ranges)`、`.exportFails(stage: encode, code: OUTPUT_SPACE_INSUFFICIENT)`、`.exportCancelSlow()`；可组合 |
| `DemoPicture` | `CustomPainter` 画演示画面：按媒体 seed 生成的渐变色块 + 移动图形 + 时间码 + “DEMO” 水印；GIF 演示为循环图形；不解码任何文件 |
| `DemoDataGenerator` | 固定 seed 生成媒体描述、轨道、片段、遮罩、跟踪区间；输出 `manifest.json`（seed、参数、内容 hash） |
| `contract/` | `runVideoKitContractTests(VideoKit Function() create)`：同一套用例供 Dart Fake 与 `FlutterVideoKit`（`integration_test`）使用 |

### 11.2 测试分层

| 层 | 工具 | M0 内容 |
| --- | --- | --- |
| 单元 | `flutter_test` | 数据类相等性；`state_mapping` 全错误码映射；`TimelineScale` 换算与吸附；`HostActionBar` 布局算法；`Mappers.kt`（JVM 单元测试）全字段往返 |
| 组件 | `testWidgets` + `fakeAsync` | 每个组件在每个场景下的交互与状态；自动隐藏条件；连续 Seek 只提交最后一次；面板返回键行为 |
| Golden | `matchesGoldenFile`，字体固定为测试字体包 | 矩阵：组件 × {浅, 深} × {en, zh, 伪本地化, RTL} × {1.0, 1.3, 2.0} × {compact, expanded}；按组件拆分文件，只在固定 CI 镜像上更新基线 |
| 契约 | `videokit_fake/contract` | Dart Fake 全部通过；`FlutterVideoKit` 在设备上通过（经 Kotlin Fake） |
| 集成 | `integration_test` | 示例 App 主流程（打开 → 播放 → 拖动 → 轨道 → 全屏 → 编辑 → 打码 → 导出 → 取消）；纹理回收与重建（切后台再回来） |
| add-to-app | `sample-host` instrumented test | Fragment 嵌入显示、宿主面板同步显隐、旋转后会话不中断、引擎销毁释放会话 |
| 无障碍 | `meetsGuideline(androidTapTargetGuideline / labeledTapTargetGuideline / textContrastGuideline)` | 每个组件页面运行一遍；读屏与键盘人工走查记录 |

### 11.3 静态检查

- `analysis_options.yaml`：`flutter_lints` + `strict-casts`、`strict-raw-types`、`strict-inference`。
- 自定义 lint（`custom_lint` 插件，放在 `tools/vk_lints`）：`videokit_ui/lib/src/**` 中禁止 `Color(`、`Colors.`、`TextStyle(fontSize:`、数字字面量作为 `EdgeInsets`/`SizedBox` 尺寸、`Text('…')` 字符串字面量；例外只允许在 `theme/` 与 `l10n/` 下。
- 依赖检查：`videokit_ui/pubspec.yaml` 只允许依赖 `flutter`、`flutter_localizations`、`intl`、`videokit_api`（CI 脚本读取 pubspec 校验）。

### 11.4 Release 隔离检查

- 构建 `videokit_example` 与 `sample-host` release 产物后，CI 脚本检查：Dart AOT 符号表（`--split-debug-info` 产物）中不出现 `videokit_fake` 库；APK 中不含演示资源目录；`videokit_flutter` release 构建未指定后端时初始化失败而不是悄悄使用 Fake（M0 的 `FakeBackend` 只在 debug 依赖中提供）。

## 12. M0 冻结的默认值（建议）

| 项 | 建议值 | 可配置 |
| --- | --- | --- |
| 控件自动隐藏 | 3 s | 宿主 `VideoKitPlayerOptions` |
| 状态快照采样 | 播放 4 Hz；拖动 15 Hz；相变立即 | 否 |
| 拖动预览 Seek 间隔 | ≥100 ms | 否 |
| 快退/快进步长 | 10 s（键盘左右 5 s，Shift 30 s） | 宿主 |
| 回调超时：HostAction | 10 s（期间 pending） | 宿主 |
| 回调超时：导航请求 | 3 s | 宿主 |
| 回调超时：其他通知类 | 2 s | 宿主 |
| 纹理延迟销毁 | 2 s | 否 |
| 倍速档位 | 0.5、0.75、1、1.25、1.5、2 | 宿主可裁剪 |
| 时间线缩放范围 | 10–400 px/s；吸附阈值 8 dp | 否 |
| 多画面最大槽数 | 12 | 宿主可降低 |

## 13. 开发顺序

| 步 | 内容 | 完成标志 |
| --- | --- | --- |
| 1 | 工作区骨架、分析规则、自定义 lint、CI 跑通空包 | `flutter analyze` 与 Gradle 构建绿 |
| 2 | `videokit_api` 全部类型；Kotlin `videokit-api` 同步 | 两侧评审稿可读；数据类单元测试 |
| 3 | `videokit_fake`（时钟、会话、场景、演示画面）+ Dart 契约测试 | 契约测试全绿 |
| 4 | 主题与 l10n 基础、`common/` 组件、`VkSelector`、`CommandDispatcher` | 画廊页可切主题/语言/字体缩放 |
| 5 | UI-09 → UI-01/02 → UI-04 → UI-03 → UI-05 | 每完成一个组件补组件测试与 golden |
| 6 | UI-06 → UI-07 → UI-08 | 示例 App 编辑主流程可走通 |
| 7 | Pigeon 定义、插件、Kotlin Fake 与测试图案、`FlutterVideoKit` | 设备上契约测试经通道全绿 |
| 8 | `videokit-ui-android` 桥接与 `sample-host` | 嵌入测试通过；§9.3 指标记录 |
| 9 | 整批自测：golden 矩阵、无障碍、release 隔离检查、测试报告（真实能力标 NOT_RUN） | 满足 03 §9 与 12 VK-M0 退出条件 |

步骤 2–6 与 7–8 只依赖步骤 2 的 API 草案，可以并行；按项目规则，M0 以整批冻结后再交独立测试。

## 14. 评审时需要确认

1. 命令“每命令一个通道方法”的做法（§8.1）。
2. 原生宿主嵌入时会话归宿主所有、Fragment 不释放会话（§9.1）。
3. UI 设计稿配色作为 Token 默认值（§7.2）。
4. §12 全部默认值。
5. 多画面在 add-to-app 下的推荐方案，在 §9.3 实测后确定：一个引擎内的 `VideoKitSlotGrid`（预期）还是多个嵌入实例。
