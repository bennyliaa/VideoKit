# C09 源码、必要依赖、漏洞与有限准入

2026-10-16。仅批准本机/项目内 Debug D1 实验；不批准正式产品、商店、专利或独立SDK外部分发。C08严格白名单阻断作为历史事实保留；C09明确允许审查必要H263传递依赖。

## 精确来源

采用官方8.0维护线 **8.0.3**，替换C08的8.0。官方[下载页](https://ffmpeg.org/download.html)与[安全页](https://ffmpeg.org/security.html)完整快照已保留。源码 `https://ffmpeg.org/releases/ffmpeg-8.0.3.tar.xz`，11407656字节，SHA256 `6136812ea6d4e68bdba27e33c2a94382711cdf4f8602ffef056ff792bd6f9818`。签名VALIDSIG指纹 `FCF986EA15E6E293A5644F10B4322F04D67658D8`，与官方下载页一致。GPG第一次导入已导入公钥但agent启动报错，原日志保留；公开签名验证使用不启动agent模式成功。TRUST_UNDEFINED不被写成Web of Trust完全信任。

9893个上游普通文件及完整LICENSE/COPYING原样保存；上游源码无本地patch。8.0到8.0.3有630项源文件差异，逐项旧/新hash见 `ffmpeg-8.0-to-8.0.3-delta.json`。不以维护版本名代替差异/对象审核。

## 组件和许可闭合

| 请求/依赖 | 实际编译与注册 | 实验输入限制及许可 |
| --- | --- | --- |
| AVI、MOV-family demux | 生成注册表AVI/MOV；无其他demux | kind1 AVI/MPEG4，kind2采用MOV-family解析已声明的MP4/H264；不宣称已测试所有MOV-family变体 |
| MPEG4 decoder | 上游select H263 decoder，后者select H263 parser；实际包含独立注册入口 | 保留必要实现，不破坏上游；native实际codec_id必须是MPEG4，H263输入反例准备拒绝 |
| H264 decoder/parser | 注册H264，MPEG4VIDEO/H263 parser亦存在 | kind2实际codec_id必须H264，不能传任意decoder名 |
| avutil/swscale | 固定RGBA256×144输出 | LGPL组合；不是将容器/压缩图像交回宿主解析 |
| 编码/网络/硬件/外部codec | encoder/muxer/protocol/hwaccel为空；GPL/NONFREE/VERSION3/NETWORK均0 | 不引入x264/x265/OpenH264或其他未审库，不代表音频/编码已完成 |

266个实际object、608个编译依赖文件逐项映射/hash，包含头文件和生成文件。分类：588项LGPL文件、10项生成文件、4项无相反条款的上游默认LGPL薄文件、3项IJG、ISC/Zlib/MIT各1项。四项默认薄文件是包含已审表文件的log2/reverse包装；没有用默认规则覆盖faandct或Adler32的特别条款。完整原文和依赖图保留，不只给汇总SBOM。

特别保留IJG三文件完整原始声明和精确署名句、faandct ISC、Adler32 Zlib及avsscanf MIT。三项IJG文件相对于签名8.0.3没有本地修改；上游已有修改仍由完整原文识别。完整上游许可文本及六项特别notice实际进入debug APK，逐字节核验。全源码内包含可选GPL代码/许可证文本不等于启用GPL组件。

独立项目胶水 `native/cpu.c`、`native/quota.c`、旧lease适配器及其NDK构建命令/依赖/hash保留。通过上游已有 `--malloc-prefix=vk_c09_` 接口动态链接自有配额库，没有重写解码器或改上游源。libavutil实际未解析符号引用及对应配额库导出符号已核验；新配额库仅系统libc/libdl依赖。NDK30.0.16248370/API31的完整NOTICE、toolchain NOTICE和属性保留。AndroidX/Media3依赖锁与C07逐字节一致，原有AndroidX graphics path四ABI native文件亦与C07一致。

## 8.0.1至8.0.3累计漏洞覆盖

| CVE | 精确官方修复提交前缀 | 当前对象/可达性与修复依据 |
| --- | --- | --- |
| 2025-69693 | 5a6e2b0a | RV60源未编译/未注册；官方补丁反向check成功 |
| 2025-63757 | 716cf25e | swscale/output.c确已编译；YA16受影响输出路径不同于本适配RGBA，但不据此跳过修复；官方补丁反向check成功 |
| 2025-67306 | b5996929、fe72a878 | iamf_parse.c确已编译，MOV元数据入口不能因无音频decoder就假定不可达；8.0.3后续上下文变化使原补丁反向check失败，但同一scalable_channel_layout_config内两项精确拒绝条件均存在，完整函数及检查保留 |
| 2026-8461 | 24b452cd、31c9c550、3e8f3537 | MagicYUV未编译/注册；三项官方补丁反向check成功 |
| 2026-30999 | 5c8a8750 | zmqsend工具未构建；官方补丁反向check成功 |

8份官方patch、完整提交hash、源/对象对应和原始check退出值在 `ffmpeg-security-coverage.json` 及 `security-patches`。没有把反向check失败写成成功，也没有把裁剪或进程隔离等同无漏洞。以上逐项覆盖已记录的8.0维护线公告，不是穷尽漏洞、漏洞利用验证或fuzz通过；其他分支CVE不自动判定本版本不受影响。

## 构建、实际包及限制

NDK交叉编译、JNI编译通过。源码配置、编译依赖、全部新ELF headers/LOAD/NEEDED/SONAME及hash保留。七个C09 native库均AArch64、LOAD至少16384对齐；APK所有native项ZIP_STORED且数据偏移16384对齐，zipalign检查通过。库原始hash与APK内内容一致；继承AndroidX库独立与C07比对。CPU只支持ARM64 API31+，其他ABI的继承UI库不能被当作CPU其他ABI支持。

对应完整源码、无修改patch声明、配置/脚本、未剥符号动态库、NOTICE、SBOM在同一冻结交付。动态链接不自动完成外发替换/再链接、EULA/商店或专利条件。正式release包hash与C07完全一致，没有CPU类/服务/库/notice；其中原有AndroidX库保持原样。**准入结论仅 DEBUG_EXPERIMENT_ADMITTED；Android加载与实际16KiB页设备运行均NOT_RUN。**
