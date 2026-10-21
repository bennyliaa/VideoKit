# 编辑时间线、打码与安全导出设计

版本：V1.0；日期：2026-10-05；状态：设计草案，编码器/输出预设待冻结。

## 1. 工程与时间模型

工程使用 version、projectId、opaque sourceTokens、source technical fingerprints、clips、masks、trackingData、exportPreset；不序列化路径、读句柄和凭据。恢复由宿主 source resolver 重新绑定；源指纹变化必须重新验证轨迹与编辑区间。

Clip 保存 sourceId、sourceInUs、sourceOutUs、outputOrder，区间 [in,out)，使用 int64 微秒和有理帧率，按实际 PTS 处理可变帧率。源区间→输出区间的映射显式可查询；同一源重复片段或重排不能错误沿用输出时间的打码轨迹。

原文单视频片段增删裁剪重排、多输入裁剪拼接都是 P0。预览用不可变 EditPlan revision；导出捕获 revision，后续用户修改不能悄悄改变在途输出。工程可恢复，首版在途编码允许从头重启。

## 2. 复用管线

Android 评估 Media3 Transformer/Composition、Codec/Effects/Muxer 扩展；Apple 评估 AVComposition、AVVideoCompositing、Reader/Writer；Windows 评估 SourceReader/SinkWriter 和平台变换。共享时间线与遮罩计划；解码器、编码器与 GPU 调用由平台适配。

Media3 自定义输入通过 AssetLoader/MediaSource factory 接入宿主读取；输出是否可直接使用 WriteHandle 由 Muxer factory Spike 验证。若当前 API 仅接受路径，不得绕过 Sink 创建任意本地临时文件；需要实现受控 muxer 或由宿主 Sink 明确授权暂存及拷贝阶段，否则导出前返回 OUTPUT_CAPABILITY_UNSUPPORTED。这不是删减安全导出 P0。

参考：[Composition](https://developer.android.com/media/media3/transformer/composition)、[AssetLoader 扩展](https://developer.android.com/reference/androidx/media3/transformer/DefaultAssetLoaderFactory)、[Apple 合成](https://developer.apple.com/documentation/avfoundation/avvideocompositing)、[Windows 管线](https://learn.microsoft.com/en-us/windows/win32/medfound/media-sinks)。

## 3. 快速拼接与转码

快速 remux 仅在容器/codec/profile/extradata、尺寸、色彩、方向、timebase、音频采样与声道、轨道布局兼容，时间戳连续且裁切关键帧安全时启用；任何打码/像素效果必转码。不能因同后缀或同分辨率就认定可无损拼接。

非关键帧精准裁切默认转码或受验证的局部重编码；如需要关键帧对齐，展示实际裁切边界并取得用户选择，不能静默改变范围。混合输入统一方向、尺寸、帧率和音频；无音频片段补静音或统一无音轨的策略需预设声明。音视频严重错位失败，不静默输出。

首选评审候选 MP4/H.264/AAC、SDR、安全设备编码范围，非已批准最终格式。HEVC/HDR/音频直通逐项评审；播放可用不代表可编码。FFmpeg 仍是获批后的扩展候选，当前不集成。

## 4. 遮罩与跟踪

Mask 保存 targetId、源时间范围、归一化区域、效果参数和关键帧；预览与导出同一评估器，像素 shader 平台实现通过黄金图验证。多目标顺序、边缘外扩和模糊/马赛克强度有明确规则。

遮罩基于媒体空间，播放缩放不等于编辑裁剪。跟踪数据含每段置信度、有效范围、丢失及歧义状态。纠正点覆盖后续计算的起点；旧 revision 的结果不得覆盖用户修正。

存在未覆盖/低置信/歧义区间时阻止以“完整保护”导出：必须人工纠正或明确切换为保守全帧遮罩等已验证策略。不得以用户忽略警告就将未保护区间标记为安全。

## 5. 输出状态与任务生命周期

校验全部源和权限 → 预估资源与空间 → preflight Sink 能力 → openTemporary → 编码/封装 → finalize → flush/close → 验证可打开/结构/尺寸/时长及遮罩覆盖 → markReady → 返回结果。宿主后续验收与 COMMIT 独立。

编码器要求 seek/randomWrite 时必须在开输出前确认；未知剩余空间可边写边反馈风险并处理不足，不伪造准确预计体积。Sink 不支持读取验证时，需宿主提供临时只读验证租约或等价回调，具体接口待评审；无法验证不能宣称输出已验证。

失败/取消必须停止读写、取消任务、关闭所有句柄，再调用幂等 abort。markReady/取消通过任务状态仲裁，仅产生一个终态；markReady 结果未知时查询/重试同一 ID。资源报告在真实归零后发出，不以 UI 关闭代替释放。

取消时限须 Spike 冻结。编码器不支持可靠暂停则 UI 仅提供取消；已批准 worker 的硬终止由宿主完成，触发 abort，不影响源文件。进程死亡由宿主按 exportId/OutputToken 所有权回收未提交临时文件。

## 6. 输出与验收

返回原文第 11.2 节全部技术元数据、来源列表、projectId/presetId/warnings，增补 planRevision 与验证摘要供宿主检查。Kit 不改名/替换/删除源。源前后 hash/路径、partial output 未 ready、Sink 故障和不同参数拼接是发布阻断测试。
