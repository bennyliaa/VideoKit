# 开源复用与闭源发行许可计划

## 2026-10-21 最新播放子系统设计基线

2026-10-21 用户确认：播放复用 Media3/平台播放器，保留统一 PlaybackBackend 隔离平台实现，libmpv不再列正式选型/对照或计划内验证。识别独立模块优先验证whisper.cpp，翻译独立模块评估llama.cpp+适用模型并可替换，平台适配位于各能力底层。自有开发集中统一API/宿主输入/生命周期/预算/字幕时间轴/取消/Flutter UI与编排，不重造解码/音画同步/推理引擎。

whisper.cpp代码MIT，官方Whisper代码/权重官方说明MIT；llama.cpp代码MIT，但翻译权重须另审。保留版权/许可，精确版本、模型hash、加速依赖和SBOM实施前冻结；不下载latest充已准入。官方来源见[《VideoKit 播放子系统详细设计》](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)第11节。Media3现有锁定版本不得被本设计默认升级。原libmpv/LGPL内容仅保留历史合规参考，不再构成候选或派发任务；FFmpeg/其他受限组件仍不得未经批准进入产品。

本节为当前设计；被撤销指令已从执行正文移出，修改前原文见history/design/2026-10-21-consolidation/。历史证据保持，项目继续暂停。

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。旧SkinKit实接与禁止自有Theme要求已归档，不作为当前任务；未来仅在正式Flutter支持和新批准范围下评估。完整现行范围见 [Flutter Theme 与延后集成决定](FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；D1未通过、M0未启动；当前项目暂停。


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

若未来另获批准评估libVLC/FFmpeg等LGPL组件：逐版本保存 source commit、完整构建脚本、依赖版本、patch、准确 license expression、二进制 hash；无 enable-gpl/enable-nonfree 不能单独证明整个产物许可安全，依赖可能改变有效许可版本。

需提供对应源及修改、NOTICE/license、必要的用户替换或重新链接材料，并调整 EULA 中相关修改/调试逆向权利限制。静态链接可以存在合规路径但有额外材料要求；动态 framework/DLL 也不自动满足用户替换条件。iOS 签名、商店条款与实际分发方案须一并审查；未核实不能承诺可上架。

FFmpeg 官方不提供通过付费购买另一专有许可来免除其开源义务；支付给打包 SDK 厂商也不自动免除 FFmpeg 或其他第三方义务。H.264/HEVC/AAC、杜比等专利/品牌授权另审，系统调用也不能被描述为全球专利免责。

## 4. 二次开发记录与供应链

每项复用记录 upstream URL、精确 release/commit、源码 hash、许可文件、复制文件/资源清单、修改 patch、用途、传递依赖、NOTICE、漏洞检查和维护负责人。采用 package 也记录精确版本；不在设计阶段以 main/latest 作为实现依赖。

当前表是设计选型/发行准入清单，不覆盖既有Spike候选已锁版本；各候选精确版本按其manifest，正式发行另冻结。coder 实现前提交 dependency manifest；Android Version Catalog/lock/verification、Flutter pubspec.lock、CMake/原生依赖 hash、Apple/Windows 固定来源统一生成 SBOM。安全修复升级亦执行许可与契约回归。

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

## 集中整理后的执行依据（2026-10-21）

[CURRENT_DESIGN_BASELINE](CURRENT_DESIGN_BASELINE_V1.0.md)；[METRIC_FREEZE_REGISTER](METRIC_FREEZE_REGISTER_V1.0.md)。

以上补充现有职责、接口和验收追踪，不新增主阶段或删除原P0。历史设计原文已归档，不再作为并行指令；当前项目暂停，不能以本文触发开发测试。

## 7. 实施前依赖/模型准入登记

| 项 | 设计决定 | 当前准确版本/产物状态 | 正式准入责任/时间 |
| --- | --- | --- | --- |
| Android Media3 | 已确定路线，不做libmpv对照 | 既有D1候选锁版本只适用原候选，按原manifest；本次无升级 | 对应coder精确artifact/传递依赖/构建hash，tester独立核，正式产品阶段冻结 |
| whisper.cpp/官方Whisper | ASR优先验证，代码/官方权重MIT来源已记录 | 本次未选择源码commit/模型尺寸/量化/加速包，无下载 | EXT-ASR准入前提交manifest/NOTICE/性能语料与权重分发证据 |
| llama.cpp/翻译模型 | 可替换本地Provider评估 | runtime许可不代模型权利；本次未选择模型/语言对 | EXT-TR准入前逐模型权利/质量/依赖/ggml符号边界 |
| 图片/跟踪候选 | 按原OpenCV/平台方案及模型记录 | 设计表不是全部产物许可冻结；历史结果不改 | 各阶段准确依赖/模型manifest+MET-IMG/MET-TRACK |
| SkinKit | 延后，不列当前M0/M8门 | 供应方目录当前SOURCE_UNAVAILABLE；原索引hash只是历史 | 正式Flutter支持后另确认来源/正式许可，不据缺文件补造 |

发行前SBOM/NOTICE、source/weight hash、patch和授权范围分别绑定SDK/App/宿主，不能把本次文档整理当法律或商店验收。历史许可文本完整归档，不重复开启后端选型。
