# D1 E13 renderer/audio/source 与 Kit 可行性决定 V1.0

日期：2026-10-18。具体工程路线与缺口供负责人审定，不是这些功能已实现/实测。本批六方法是权限/source生命周期，未创建Surface/AudioTrack、未编译Flutter/独立AAR、未引入音频decoder或新模型。D1整体继续NOT_PASSED。

## 输入、raw frame与真实显示

保留Media3为Android成熟后端薄适配首选，不自制容器/编解码器或再造编辑框架。当前isolated FFmpeg仅已审MP4/H264、AVI/MPEG4的有限snapshot/验证闭包，不是持续播放/全格式后端；旧宿主Media3播放器的危险解析/字幕/图片边界仍需处置，不能直接将旧代码恢复为“全链隔离产品”。ordinary isolated直接codec/GPU既有不可用条件不重复探针。

下一有限显示路线选用既有isolated raw RGBA来源、受控codec服务owner线程可复用的Android软件Canvas/Bitmap/Surface薄适配；不先造自有GL渲染器。host/UI只提交Surface generation和销毁意图；实际producer detach、最后在途提交/回调归还、Bitmap/Surface原owner release后才完成该consumer。若仍需host创建Texture/Surface，其JNI残留明确单列，不能以service分进程声称host零JNI或驱动故障完全隔离。同UID进程仅地址空间边界，资源和权限不扩大。

后续具体契约需frame携带原sourceVersion/task/epoch、实际PTS/布局/rotation、独占FrameLease/Surface generation；旧代/销毁后帧拒绝，队列沿已有有限能力协商，禁止用固定PTS推算VFR。真实截图/方向/销毁重建与原producer归还才算显示可行性，ByteBuffer被接收不算画面。**当前显示实现NOT_RUN；持续decode→renderer及J11可行性尚未通过，不能在D1退出时跳过。**

## 合法PCM来源与唯一声音

当前受限FFmpeg没有获准的音频解码白名单，明确不扩。真实压缩音轨→合法PCM的产品路线仍BLOCKED；优先审既有Media3/系统音频后端在受控进程的宿主随机读、权限/故障与生命周期适配，不在E13新增decoder或假称系统组件全球专利免责。

可供下一有限AudioTrack输出可行性研究的PCM来源，只限权利明确、精确hash的原始PCM16测试样本或明确标注的本地生成PCM；这只能证明PCM到声音/焦点/释放，不替代正式MP4/AVI/MKV音轨支持，也不将产品解码责任转给Browser。PCM候选48kHz/双声道/PCM16、≤20ms/3840B块是既有C14设计候选，仍须实际设备与正式派单决定；不能无记录当最终公共API阈值。

单audio owner持AudioTrack/焦点/PCM队列/在途write，宿主以audioEpoch决定唯一发声及全静音。seek/pause/detach先撤旧epoch，后确认write/stop/flush/release与原缓冲归还；UI不持锁等IPC。真实听音或可审回环与外部证据独立于“write返回”。**当前音频运行NOT_RUN、压缩音频合法接续BLOCKED**；未取得合法PCM与后端决定前不派无限声音探针。

## SourceReleased与HostAction

E13两consumer共享一个真实LeaseRegistry generation，证明第一个退役不得影响第二个，原Released条件retired && consumers==0 && operations==0 && !closeFailed成立且runtime线程真返后才归还。本批只证明此D1生产source聚合机制，尚未接入真实播放、图片、字幕、跟踪、导出、renderer及audio全产品消费者。

M0公共契约应由宿主源租约管理器按opaque mediaToken/sourceVersion聚合所有consumerId/epoch，播放/编辑/跟踪/验证/显示/PCM消费者在实际detach/原引用归还后各自退租。任何未知保持计账，不能以一个CPU死/一个Handle.close/取消响应发全源SourceReleased。HostAction移动/复制队列只在宿主确认全部相关消费者释放后运行；query可重读真实释放状态，回调丢失不能重开文件。Kit不接NAS凭据、完整路径或Browser数据库类型。

## 独立Kit的可提取依赖与必须移除的实验耦合

| 当前构件 | 可复用部分 | 独立Kit前必须完成/阶段 |
|---|---|---|
| SourceAdmission/AsyncReadBridge/LeaseRegistry/SourceGroup | 原opaque授权输入、实际ticket/consumer/在途计账 | SourceGroup是D1实现，公共错误/版本/释放协议由M0冻结；不对外暴露实验UID/PID作为宿主业务字段 |
| E4Session/codec service/CPU isolated | 有限原端点、owner与FD/raw边界 | 服务类可放库；Manifest名称/进程后缀由SDK namespace/受审placeholder避免冲突，不能硬编码宿主com.videokit.app；M0设计/M7双宿主实证 |
| E9/E13部署policy | 精确实验制品/设备/UID保护 | HA1Q6WXR、10221/10222、data inode及测试fixture都是D1部署约束，不进入通用Kit API；不能只删pin就称可多宿主 |
| Media3 muxer与受限FFmpeg/native | 成熟组件薄适配、已锁7库/35坐标 | playback、export与可选受限后端依赖拆开；Fake/api不拉FFmpeg/模型/UI。许可/对应源/NOTICE/替换与发行权利继续硬门 |
| 当前Gradle :app | 明确真实Android代码可构建 | 不是AAR。M0 api/core等无Browser/Flutter业务依赖和Fake契约、M7版本化独立AAR/两个签名宿主/可移除与升级回退，不能等待M7才发现源码依赖 |
| Flutter/C ABI | 已确认原生状态单一权威、低频控制和opaque handle方向 | 未实现。媒体/逐帧裸数据不经过Dart往返；M0冻结线程/retain-release/代次，后续App阶段验真实engine销毁重建 |

当前Java依赖是平台/Media3及本项目实验类型，没有引入Browser数据库实现；这不等正式公开API/适配器已独立验收。D1必须交清源/Sink/取消、合法后端和这些封装边界可行性；M0实现基础契约，M7才做正式分发与真实Browser回退。全部13项P0、模型/权重/样本与长期/设备/许可门继续保留，不以设计材料关闭运行门。
