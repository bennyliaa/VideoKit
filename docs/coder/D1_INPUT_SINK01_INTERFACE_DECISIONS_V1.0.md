# INPUT_SINK01 候选接口与M0未决决定

2026-10-21；记录可沿用的不变量及候选限制，**不冻结最终M0公共API**。

| 可沿用的不变量 | 本候选接线 |
|---|---|
| 宿主授予opaque源，不向SDK暴露真实path/URL/凭据 | Provider capability对象身份+opaque sourceVersion；对外随机`videokit-source:` URI，直接DataSource.Factory，不路由HTTP |
| known/unknown length与requested range准确 | 真实DataSpec.position/length，长offset不截32位；每块64KiB，未知不猜总长，越界/整数溢出失败 |
| 取消与原归还独立 | 原bridge/registry及原E13 worker-return仍为唯一权威；raw registry快照不单独当完整SourceReleased |
| 同一实际源共享准入 | 相同Provider不能双factory，同factory两个consumer共享一次在途门，queue0；不把原executor queue16当新承诺 |
| sink先协商能力 | 不支持random/flush/close/reopen在写前拒绝；顺序fMP4使用成熟Media3/E6绑定，不实现codec/容器 |
| 原写实际量/UNKNOWN独立 | successful partial ACK可推进；抛错只保留已确认下界、attempt/reservation与UNKNOWN，首错sticky，不rewind重发 |
| 输出状态不混同 | producer关闭、flush/close、原任务归还、reopen/hash、独立格式receipt、READY、明确host COMMIT分别留证 |
| 业务提交属于宿主 | 原SinkCoordinator只仲裁READY/ABORT；COMMIT必须显式宿主动作和原ACK，不由SDK关闭文件代替 |

本候选全局2个宿主source capability、每factory最多2个DataSource/每代最多2 consumer，旧代真实归还后才能复用；每源read queue0、候选输出16MiB。它们是本批有限预算，不是最终产品阈值。成熟muxer薄绑定保持原单video/avc、256×144、6样本、≤2秒PTS、单sample≤262144B及原EOS规则；host I/O仍分64KiB块。真实媒体/muxer路径仅编译，不能据此扩大格式/持续播放能力。

M0之前尚需决定并验证：

- 跨进程/Flutter边界的实际capability identity、sourceVersion/epoch和Provider alias规范；当前Java对象身份不是最终跨语言协议。
- Media3长寿命Factory/多次创建DataSource、连续seek/断线恢复/缓存策略、UI线程生命周期与listener失败政策；当前只覆盖有限原代复用与工作线程门。
- 实际宿主OutputSink授予/能力证明及原异步worker归还契约，random输出内容基准由宿主独立validator判定；不缓存整文件推导随机最终hash。
- 实际C14隔离验证receipt与新host port接合：真实worker death/slot/source/EOF/内容/timeline等门保持，当前受控validator不等于实现/验证了这些门。
- Android FD/MediaCodec/FragmentedMp4Muxer/真实容器和故障路径的设备证据，host业务COMMIT/发布原子性和失败恢复。
- 新datasource/database/exif使用的独立身份/许可准入、完整危险链/独立Kit等原P0、模型/媒体与发行许可。

仅现有`E13SourceGroup`副本增加range open委托，`SinkCoordinator`副本增加原callback线程join；原桥/registry、成熟muxer、旧冻结代码未改。差异和原hash随包提供。D1整体未通过、M0未启动；Flutter自有Theme/既定18PPT UI与SkinKit延期等原规划保持。
