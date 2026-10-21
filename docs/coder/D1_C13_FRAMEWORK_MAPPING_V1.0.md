# C13 框架与自有胶水映射 V1.0

2026-10-16，Debug-only。app/gradle.lockfile与C12逐字节对照；无依赖升级。

| 功能 | 复用框架/来源 | 自有新增适配与界限 |
|---|---|---|
| 源压缩读取/解码/缩放 | 固定受限FFmpeg8.0.3，C09签名准入与C12五二进制不变 | cpu.c同一decode_impl新增rotation identity检查、六帧全EOF输出验证；不自制codec，不扩白名单 |
| 裸帧协议 | C12 Binder固定元数据、内核身份、Source broker、2 CPU slots | PipelineRules/Packet/BoundedFrameQueue；固定复制、帧序/PTS/alpha/总量/时基，mode10/11小协议 |
| 编码 | Android公开MediaCodec/CodecCapabilities，宿主UID | PipelineEncoder只接固定裸RGBA，转标准YUV；public Image三平面限界；单owner/单许可，无音频或Surface |
| 封装 | 已锁Media3 1.9.3 FragmentedMp4Muxer | WritableByteChannel包裹既有授权文件，含容器头2MiB硬上限；不增加FFmpeg muxer |
| Sink恢复 | 既有FencedTask/AndroidLease/SinkCoordinator | PipelineOutputSink/typed ValidationReceipt，fsync/close/lease、READY丢响应query；原host/legacy规则保留 |
| 独立验证 | 同APK ordinary isolated CPU，受限MP4/H264 | 完整6帧EOF、唯一视频轨/无音频、实际尺寸/PTS、16×9 luma摘要/合理误差及可区分画面；不是宿主Extractor替代通过 |
| 调度/账本 | Java有界线程池/已有C12生命周期 | RealFramePipeline顺序六snapshot、queue2/consumer1，超时PENDING不假释放，源/codec/FD/租约分别证明 |

Media3 [1.9.3 fMP4公开源码](https://raw.githubusercontent.com/androidx/media/1.9.3/libraries/muxer/src/main/java/androidx/media3/muxer/FragmentedMp4Muxer.java)支持WritableByteChannel；启用sample copying后立即归还codec输出缓冲。BufferInfo(long,int,int)与本地锁定AAR实际javap核对。没有新crash handler、权限、companion产品依赖或Browser业务。旧companion仅完整回归。

本地架构为能力探针，非正式独立AAR/C ABI；Kit多宿主、Flutter/主题/控件、显示/PCM/跟踪/图片/字幕完整隔离与所有P0见剩余门禁报告。新增自有颜色/协议/队列/哈希胶水不宣称重写第三方算法。
