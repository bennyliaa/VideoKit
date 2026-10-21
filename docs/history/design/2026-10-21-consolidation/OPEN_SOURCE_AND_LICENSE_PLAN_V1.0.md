# 开源复用与闭源发行许可计划

## 2026-10-21 最新播放子系统设计基线

2026-10-21 用户确认：播放复用 Media3/平台播放器，保留统一 PlaybackBackend 隔离平台实现，libmpv不再列正式选型/对照或计划内验证。识别独立模块优先验证whisper.cpp，翻译独立模块评估llama.cpp+适用模型并可替换，平台适配位于各能力底层。自有开发集中统一API/宿主输入/生命周期/预算/字幕时间轴/取消/Flutter UI与编排，不重造解码/音画同步/推理引擎。

whisper.cpp代码MIT，官方Whisper代码/权重官方说明MIT；llama.cpp代码MIT，但翻译权重须另审。保留版权/许可，精确版本、模型hash、加速依赖和SBOM实施前冻结；不下载latest充已准入。官方来源见[《VideoKit 播放子系统详细设计》](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)第11节。Media3现有锁定版本不得被本设计默认升级。原libmpv/LGPL内容仅保留历史合规参考，不再构成候选或派发任务；FFmpeg/其他受限组件仍不得未经批准进入产品。

本节覆盖下文相冲突的历史候选说明；原P0、冻结报告和历史证据保持。仅文档更新，项目继续暂停。

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。本条覆盖下文此前“暂不自建 Theme”“M0 必须实接 SkinKit”等旧要求；供应方资料与历史要求保留供将来评审，不作为当前强制任务。完整现行范围见 [Flutter Theme 与延后集成决定](FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；当前 D1 冻结任务不变，M0 未启动。


## M0 UI 优先实施要求（2026-10-20 最新）

用户最新决定（2026-10-20）：M0 在保留 API/Fake/TestKit/sample-host 原范围的同时，先搭建整个正式 Flutter App 的 UI 框架，按既有 18 页 PPT 的视觉与交互样式实现，并真实集成 SkinKit。允许生成带明确“演示模式·模拟数据”标识的本地测试数据演示全部主要页面与状态；演示不能冒充真实播放、跟踪或导出通过。后续 M1–M6 功能逐批实现并接回同一 UI，M7 保持独立宿主接入，M8 完成全功能真实集成与发布级验收，不再首次重建 UI。继续复用 SkinKit 默认/标准样式与合法最小宿主适配，不另建独立 Theme 系统、主题包或编辑器；通过既有配置与受支持的最小覆盖实现 PPT 样式，无法表达的差异列明评审。

完整范围与退出门槛：[M0 App UI 框架要求](M0_APP_UI_FRAMEWORK_REQUIREMENTS_V1.0.md)。本次为规划更新；D1 尚未通过，M0 尚未启动，不改变已冻结候选或当前设备批次。


## SkinKit 闭源第三方 SDK 补充（2026-10-20）

用户已指定SkinKit用于App外观集成，采用资料和准确ZIP hash见 [来源记录](ui/SKINKIT_SOURCE_EVIDENCE_V1.0.json)，要求见 [SK-17–20](SKINKIT_INTEGRATION_REQUIREMENTS_V1.0.md#6-商用许可与依赖发行门)。SkinKit 1.1.0是专有闭源二进制，不能列为开源复用；该项是本项目“合法复用第三方组件”中的明确商用SDK选择。

本地LICENSE标题仍为1.0.0 engineering draft，主体法定姓名未补，正式1.1.0适用/合法获取/商业宿主与商店分发权待核；不以收到ZIP代替正式授权，也不宣称法律审查通过。许可草案拟允许商业宿主随App发行，但对素材/示例单独售卖及同类商业主题包有限制。适配封装可用不等于SDK本体可随VideoKit核心AAR对外再分发，当前只留App UI依赖。第三方原许可与NOTICE保留，实际传递依赖/资源逐项锁定，供应方demo许可/签名/性能记录不代VideoKit验收。不得自动引入支付/商城权限或购买动作。

版本：V1.0；日期：2026-10-05；状态：候选组件初筛，非发布合规结论。

## 1. 原则与优先级

优先合法复用成熟开源代码、交互与组件，不从零实现解封装、解码、推理或系统文件选择。独立 SDK 接口、资源租约、宿主回调、输出事务、安全门禁及业务隔离仍需由本项目封装。复用量不是质量指标；许可证明确且满足契约才可采用。

用户闭源发行要求和原文第 23/27 节同时有效：GPL/AGPL/SSPL/无许可及不清许可代码不得进入产品模块；FFmpeg 需明确批准。把代码套进 adapter、动态加载、FFI 或单独进程并不能自动消除许可义务。

## 2. 候选及禁止范围

| 项目 | 当前查到的许可 | 计划 | 未完成门禁 |
| --- | --- | --- | --- |
| Flutter framework | BSD-3-Clause | App UI 候选 | engine/插件传递依赖与 NOTICE |
| AndroidX Media3 | Apache-2.0 | Android 播放/编辑首选 | 固定版本、选用 artifact 及解码扩展逐项核查 |
| Coil | Apache-2.0 | Android 图片候选 | 动图、大图、外部解码器依赖 |
| SDWebImage | MIT | Apple 图片候选 | coder 插件和格式实现依赖 |
| OpenCV 4.5+ | Apache-2.0 | 精简效果/跟踪候选 | contrib 与第三方清单 |
| ONNX Runtime | MIT | 推理运行时备选 | provider 依赖、遥测、模型许可 |
| media_kit | Dart 框架 MIT | 可合法适配 UI/交互，不默认装入原生库 | libmpv/FFmpeg 构建及绑定依赖 |
| iPlay | GPL-3.0 | 不复制或移植其代码/资源到闭源产品 | 除非合法权利人另授适用许可，且覆盖第三方代码 |
| Lan3 Player | GPL-3.0-or-later | 同上 | 同上 |
| VLC 成品 | 主项目 GPL；iOS 有不同授权组合 | 不直接 fork 作为闭源底座 | 不能用 libVLC 许可替代整个 App 许可 |
| libmpv | 历史GPL/LGPL构建合规参考 | 已退出正式候选/对照，不计划集成 | 不再安排对照构建；历史合规材料保留 |
| libVLC | LGPL 引擎，具体模块另审 | 条件式备选 | 构建组成、wrapper、plugins、分发义务 |
| FVP / MDK | FVP BSD-3-Clause；MDK 独立密钥授权 | 商业授权备选 | 原生 SDK、多个宿主及四平台分发授权 |

GPL 可以收费商业使用，但其源码义务与当前闭源衍生产品目标冲突；不是“禁止商业使用”。模型、字体、图标、测试视频和示例资源也必须核查，不能只审代码。

## 3. LGPL/FFmpeg 特别门禁

若以后评估 LGPL libmpv/libVLC/FFmpeg：逐版本保存 source commit、完整构建脚本、依赖版本、patch、准确 license expression、二进制 hash；无 enable-gpl/enable-nonfree 不能单独证明整个产物许可安全，依赖可能改变有效许可版本。

需提供对应源及修改、NOTICE/license、必要的用户替换或重新链接材料，并调整 EULA 中相关修改/调试逆向权利限制。静态链接可以存在合规路径但有额外材料要求；动态 framework/DLL 也不自动满足用户替换条件。iOS 签名、商店条款与实际分发方案须一并审查；未核实不能承诺可上架。

FFmpeg 官方不提供通过付费购买另一专有许可来免除其开源义务；支付给打包 SDK 厂商也不自动免除 FFmpeg 或其他第三方义务。H.264/HEVC/AAC、杜比等专利/品牌授权另审，系统调用也不能被描述为全球专利免责。

## 4. 二次开发记录与供应链

每项复用记录 upstream URL、精确 release/commit、源码 hash、许可文件、复制文件/资源清单、修改 patch、用途、传递依赖、NOTICE、漏洞检查和维护负责人。采用 package 也记录精确版本；不在设计阶段以 main/latest 作为实现依赖。

当前表仅初筛，全部版本未冻结。coder 实现前提交 dependency manifest；Android Version Catalog/lock/verification、Flutter pubspec.lock、CMake/原生依赖 hash、Apple/Windows 固定来源统一生成 SBOM。安全修复升级亦执行许可与契约回归。

模型另建 model manifest：权重 hash、来源、代码与权重许可、训练数据来源、商用/再分发、修改/量化条件。信息缺失标 BLOCKED，不因为 GitHub 仓库为 MIT 就推断所有权重可商用。

## 5. 四平台发行资料

Android/iOS/macOS/Windows 各包生成自身 SBOM、许可证页、NOTICE、模型说明、已知漏洞报告、二进制 hash、隐私和权限清单。闭源 Kit 外发的 obligations 要随 SDK 文档传递给其他宿主。商店审核不代替许可证合规；仅发布 SDK artifact 不等于 Kit 自身要作为应用上架。

## 6. 官方证据（核查日 2026-10-05）

- [Flutter 许可与依赖说明](https://docs.flutter.dev/resources/faq)
- [Media3 LICENSE](https://github.com/androidx/media/blob/release/LICENSE)
- [Coil LICENSE](https://github.com/coil-kt/coil/blob/main/LICENSE.txt)、[SDWebImage LICENSE](https://github.com/SDWebImage/SDWebImage/blob/master/LICENSE)
- [OpenCV 许可](https://opencv.org/license/)、[ONNX Runtime LICENSE](https://github.com/microsoft/onnxruntime/blob/main/LICENSE)
- [media_kit LICENSE](https://github.com/media-kit/media-kit/blob/main/LICENSE)、[mpv 许可说明](https://github.com/mpv-player/mpv#license)
- [iPlay](https://github.com/saltpi/iPlay)、[Lan3 Player](https://github.com/Taa965/Lan3-Player)、[VLC](https://github.com/videolan/vlc)、[VLC iOS](https://github.com/videolan/vlc-ios)
- [FVP LICENSE](https://raw.githubusercontent.com/wang-bin/fvp/master/LICENSE)、[MDK 条款](https://github.com/wang-bin/mdk-sdk#license)
- [FFmpeg 法律说明](https://www.ffmpeg.org/legal.html)、[FFmpeg 构建许可](https://ffmpeg.org/doxygen/trunk/md_LICENSE.html)、[LGPL 2.1 文本](https://opensource.org/license/lgpl-2-1)

这些链接为证据入口；选定版本须保存对应快照，不把未来分支变化视为已审核。
