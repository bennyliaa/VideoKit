# D1 C08 源码、许可与构建审核

2026-10-05。范围仅本机有限 Debug 实验。结论：交叉编译成功；严格组件白名单未闭合，停止引入。不是许可违规已被证实，也不是 CPU 解码准入或可安装候选通过。

## 来源与完整许可

官方来源：https://ffmpeg.org/releases/ffmpeg-8.0.tar.xz 。源码包 SHA-256：`b2751fccb6cc4c77708113cd78b561059b6fa904b24162fa0be2d60273d27b8e`。官方 detached signature 和公钥均保存在 `d1c08/upstream`。GPG VALIDSIG 指纹为 `FCF986EA15E6E293A5644F10B4322F04D67658D8`，与 [官方下载页](https://ffmpeg.org/download.html) 公布的指纹一致。签名验证成功；GPG trust database 的 TRUST_UNDEFINED 不是 Web of Trust 身份认证，不记为 fully trusted。

完整上游源码保存在 `d1c08/upstream/source/ffmpeg-8.0`；9888 个普通文件逐项 hash 在 `evidence/ffmpeg-source-identity.json`。完整 `LICENSE.md`、`COPYING.LGPLv2.1`、`COPYING.LGPLv3`、`COPYING.GPLv2`、`COPYING.GPLv3` 均原样保留。上游源码包中存在可选 GPL 文件，不能据此判断这些代码已编入本实验。上游 patch 列表为空；没有改动上游源码。

## 实际构建

NDK 30.0.16248370，目标 AArch64 Android API31，动态库，16KiB 链接页对齐参数。配置和两次构建调用脚本、失败日志、成功日志及完整生成 config/config.log 已保留。首次 configure 因没有 Windows host C 编译器而失败；改用 target clang 作 host C11 语法探测并启用 hardcoded tables。实际 make 成功日志没有 HOSTCC/HOSTLD 调用，因此没有声称执行 Android host generator 或验证原生 Windows generator。

首次 make 因 Windows native make 不识别 `/d/...` include 路径失败；第二次通过显式指定上游 Makefile 和相对 SRC_PATH/SRC_LINK 构建成功，没有修改上游文件。此修正保存在 `tools/make_ffmpeg.sh`。

已编译 libavcodec、libavformat、libavutil、libswscale，共267个 object。完整 object hash、编译依赖记录、ELF headers/program headers/dynamic section 已保留。DT_NEEDED 仅出现本次 FFmpeg 内部库及 Android libc/libm；ABI 静态检查为 AArch64。未验证 Android 运行、isolated 加载或真实解码。

生成配置 GPL、NONFREE、VERSION3、NETWORK 均为0；encoder/muxer/protocol/hwaccel 均为空，demuxer 为 AVI/MOV。configure 宣告 LGPL 2.1 or later。这些是配置事实，不代替逐编译源/对象许可审核或最终分发许可结论。

## 组件阻断

请求 decoder 白名单 H264/MPEG4，parser 白名单 H264/MPEG4VIDEO。实际额外启用 H263 decoder 和 H263 parser。可复核原因：上游 `configure` 的 `mpeg4_decoder_select="h263_decoder"`，而 `h263_decoder_select` 进一步选择 `h263_parser`。没有把该依赖静默纳入已审白名单，也没有假装只产出了两个 decoder。

状态 `BLOCKED_STRICT_WHITELIST` / `NOT_ADMITTED`。库只作为不准入的本机构建证据 ZIP 存放在候选 artifacts；没有复制到 App 的 jniLibs，没有新增 CPU JNI、service 或 APK，也没有进入 release。完整编译源许可闭合、JNI包装对象、NOTICE在APK中打包及最终分发条件未完成。

恢复后的可执行下一步：审查并记录可复现的上游依赖/注册配置 patch，保留 MPEG4 所需的共享实现，同时阻止额外 H263 decoder/parser 对外注册；重新检查生成组件名单、构建结果、逐对象来源与许可、ELF依赖；闭合后才进入 Debug CPU adapter 和服务实现。若选择扩大白名单，应由用户明确决定，不能据此次配置自行扩范围。当前已按用户安排停止，不执行该下一步。

## 已知漏洞与边界

官方 [安全公告](https://ffmpeg.org/security.html) 的后续 8.0.x 修复列表包含 CVE-2025-69693、CVE-2025-63757、CVE-2025-67306、CVE-2026-8461、CVE-2026-30999。此次固定 n8.0，没有自动升级或套用补丁。各漏洞对这267个对象的可达性、利用条件和修复适配尚未逐项评估，记录为 NOT_ASSESSED；不能声称 n8.0 无已知漏洞或本裁剪构建不受影响。仅本机留存，禁止外部分发。

宿主系统显示/编码、宿主JNI、P0完整媒体/人脸管线、模型及其他权利边界未由这次编译关闭。
