# C14 框架与胶水映射 V1.0

2026-10-16。Media3 1.9.3锁与FFmpeg8.0.3准入不变，无新依赖/codec/模型/权限/crash handler。

| 路径 | 复用 | C14变化与限制 |
|---|---|---|
| 公开编码能力 | Android MediaCodecList/MediaCodecInfo/MediaFormat | EncoderCapabilities保存属性/ranges/alignment/colors/profiles；检查isFormatSupported与独立颜色/几何范围。系统元数据不是配置成功证据 |
| 有限配置 | 公开MediaCodec create/configure/start/release | 自有EncoderNegotiation共享纯规则，≤2 codec×2 variants，最多4次，实际关闭后下一；默认profile与声明Baseline，标准19/21/Flexible；无Surface回退 |
| 错误诊断 | CodecException公开getErrorCode/getDiagnosticInfo/isRecoverable/isTransient | EncoderDiagnostics固定键、阶段、首错；不给任意message或URI进日志。recoverable/transient只记录，不触发运行期自动恢复 |
| 源解码/输出验证 | 既有受限FFmpeg8.0.3/CPU mode10/11 | CPU算法与C13同源，仅JNI身份重编；六真实snapshot/原时基/完整EOF/内容阈值保持，不宿主解压缩源 |
| 像素/队列/生命周期 | C13 PipelineRules/Packet/BoundedFrameQueue/CpuTaskClient | 队列与8数组预算不扩；新增encoder实际引用/在途诊断，保留CPU2/encoder1及超时PENDING |
| 无音频fMP4 | 既有Media3 FragmentedMp4Muxer 1.9.3 | 继续sample-copy、bounded WritableByteChannel；2MiB含头与finalize，错误有MUX阶段诊断 |
| Sink与恢复 | 既有FencedTask/AndroidLease/SinkCoordinator | 原协议不变；配置完成后才开writer，READY前仍须实际释放和隔离验证，运行期失败不新开输出 |

参考锁定[DefaultEncoderFactory 1.9.3](https://raw.githubusercontent.com/androidx/media/1.9.3/libraries/transformer/src/main/java/androidx/media3/transformer/DefaultEncoderFactory.java)的能力选择思路；其Surface编码路径不适合直接替代本受限裸ByteBuffer探针。未复制或改造其编码器作为新后端。实际复用fMP4封装，无新第三方算法。

精确官方API/本机SDK版本、文件hash和行引用在encoder-official-reference-review.json；API考虑键随版本不同，故声明色彩成员、尺寸/率/码率/对齐另查，isFormatSupported仍必须实际调用。C13两个configure错误不凭文档唯一归因；设备实际结果NOT_RUN。正式Flutter＋独立Kit/AAR/C ABI、多宿主、完整危险链与所有P0见剩余十二项门禁。
