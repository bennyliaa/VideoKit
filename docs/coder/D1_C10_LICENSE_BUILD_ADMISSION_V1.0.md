# C10 许可、来源和构建准入

2026-10-16。仅有限D1 Debug实验，产品/SDK外发、专利、商店和全P0仍未准入。

## 不变的开源与原生算法

继承冻结C09，摘要SHA256 `cdc48afed4f10e38fca5ad5efaf3fb4602947acc2166caa1f08d255bb89ce4fa`。FFmpeg保持官方签名8.0.3，源码包SHA256 `6136812ea6d4e68bdba27e33c2a94382711cdf4f8602ffef056ff792bd6f9818`，11407656字节。完整压缩源码含9893个上游普通文件，C10不重复展开归档；对应逐文件身份、签名、公钥及C09已验证VALIDSIG回执均保存。没有声称C10再次运行GPG。

`libavcodec.so/libavformat.so/libavutil.so/libswscale.so/libvideokit_alloc.so` 与C09原始库逐字节相同，quota.c也相同。必要H263传递依赖/注册、实际MPEG4/H264输入限制、32/64位安全边界、16MiB单次和64MiB累计申请/4096记录配额、读取/packet/帧预算保持。未重写解码器、修改上游源码、升级FFmpeg或引入外部codec/权重。GPL/NONFREE/VERSION3/NETWORK仍0；无encoder/muxer/protocol/hwaccel扩入。

C09的266对象、608实际依赖、源码许可映射、630项8.0→8.0.3维护差异、8份累计安全补丁/精确条件核验及生成配置被校验后保存于 `evidence/inherited-c09`。原map scope文字267只在C10改为实际266，对象/依赖数组不变，C09冻结未改。

特别许可和归属保留：588 LGPL文件、10生成文件、4上游默认薄文件、3 IJG、ISC/Zlib/MIT各1项；三项IJG归属句和六项特别声明及完整LICENSE/COPYING实际进入Debug APK。完整许可文本中保留可选GPL条款，不代表编入GPL代码。SBOM与实际APK库、继承AndroidX native库的来源分开记录；Media3 1.9.3及app依赖锁与C09完全一致。

## 累计漏洞覆盖沿用的精确范围

| CVE | 已核验的8.0.3修复/实际路径 |
| --- | --- |
| CVE-2025-69693 | RV60未编译，官方修复反向check回执成功 |
| CVE-2025-63757 | swscale/output.c实际编译，已含修复；不因RGBA不同于YA16就省略审核 |
| CVE-2025-67306 | IAMF元数据源实际编译，MOV入口不判定天然不可达；两patch上下文变化导致反向check失败，同一函数的精确拒绝条件已核验存在 |
| CVE-2026-8461 | MagicYUV未编译/注册，三patch反向check成功 |
| CVE-2026-30999 | zmqsend工具未构建，修复反向check成功 |

完整提交hash/patch/源与对象映射仍见继承证据。不是穷尽漏洞扫描、利用验证或fuzz通过，不以隔离或版本号推断绝对安全。

## C10重新构建的部分

只重建JNI包身份对应的CPU与lease库；CPU C文件与C09比较仅 `com_videokit_spike_c09`→`com_videokit_spike_c10`，原生算法不变。JNI需要的头文件从本候选完整源码包和已核验生成配置提取，逐项校验，不依赖浮动旧输出。编译命令、依赖、ABI/SONAME/NEEDED/符号和hash保留。NDK30.0.16248370/API31及完整NDK/工具链NOTICE保持。

CPU callback descriptor与实际编译的C10 Java类逐项核对。实际APK七项C10 native与原始库hash相符，继承四ABI AndroidX graphics path与C07相符；全部native项ZIP_STORED且偏移/ELF LOAD至少16384对齐，签名和zipalign检查通过。此为静态证据，不是C10 Android加载或16KiB页设备运行通过。

对应源码压缩包、完整许可、原始动态库、配置/构建脚本、源码hash/SBOM均在本冻结。历史完整FFmpeg脚本原文留作证据，C10参考重建脚本默认不执行，需完整展开上游源码、先构建同源quota，并显式开启参考重建；C10没有重建FFmpeg。动态链接不自动关闭外部分发的替换/再链接、EULA和商店义务。

**结论：DEBUG_EXPERIMENT_ADMITTED，正式产品准入未批准。** 正式release包与C07/C09完全相同，未含C10 CPU类、服务、库、notice；原有AndroidX库保持不变。
