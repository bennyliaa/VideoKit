# VideoKit 图片子系统详细设计

V1.0；2026-10-21；当前设计基线，非实现/性能/许可验收证明。项目PAUSED_WAITING_USER，D1未过/M0未启；仅文档更新，不派开发、补测、设备或恢复自动跟进。

## 1. 架构与接口

复用现有单媒体Session；mediaKind映射静态VIEWING或动态图PLAYING/PAUSED，不另建宿主API。ImageBackend通过平台成熟解码器适配（Android候选Coil/ImageDecoder，Apple ImageIO/候选SDWebImage，Windows WIC待M9），候选不是版本/功能通过，插件与格式逐项核许可，不重新开发完整图片编解码器。

接口：probe(readLease)→ImageInfo；openDecode(request,resourceLease)→ImageDecoder；decodeStill/decodeRegion/decodeFrame→FrameLease；cancel(opId)/queryReturn/release。只声明实际可用操作，解码region不支持不得拿全图巨额解码冒分块；对必需场景先评审成熟替代/安全降级，不能删原格式P0。

## 2. 模型与方向

ImageInfo={sourceFingerprint,width,height,orientation,colorProfile?,hasAlpha,animated,frameCount?,loopCount?,durationUs?,capabilities}；ImageViewSnapshot={snapshotSchema,mediaFingerprint,zoom,pan,rotation,fitMode,animationPositionUs?,animationPaused,loopPolicy}。未知帧数/时长null，静态不暴露无意义视频音轨/倍速字段。

TileKey={sourceFingerprint,bindingGeneration,orientationApplied,colorPolicy,sampleLevel,region}，region合法/溢出核验；TileLease含实际像素格式/rowStride/byteSize/CPU-GPU占用与原返状态。EXIF方向只在M空间应用一次，用户观看变换在V；颜色/透明alpha沿平台能力报告，不能仅文件后缀当HEIC/AVIF已支持。损坏ICC/超大声明尺寸在分配前拒绝并稳定错误。

## 3. 静态/长图与缓存

按viewport和缩放采样，长图/超大图仅解当前tile及有界预取；像素/解码尺寸/CPU-GPU字节/帧数/队列均先预留。cache按成本LRU，活跃FrameLease引用不可被evict释放；只淘汰引用归零项，OOM不清掉其他会话仍使用纹理。离屏可降低预取/暂停，宿主决定是否释放并保存快照。

## 4. 动画

解码帧延迟/循环元数据走媒体动画时钟（单调锚点+播放位置），暂停保存当前位置，恢复不跳回首帧。极短/零/异常延迟按明确冻结的安全政策处理并留warning，不能无界紧循环。跳帧为呈现降级，不能跳过必须的dispose/blend合成状态；优先成熟库动画合成。缓存上一合成帧/必要依赖帧受预算，不预解完整动态图。

解码结果附requestId/bindingGeneration；旧viewport请求过期时丢显示结果但等原buffer返，重绑不沿旧路径重开。cancel/release按统一原调用归还协议，动态图帧buffer仍被GPU持有时不得复用。图片导航只发HostAction由宿主换源，无固定上一下一业务。

## 5. 验收与阶段

IMG-01原需求7/26.2全部格式含大小写/真实容器、静态/动态/透明/EXIF；IMG-02长图分块/放大/预算/恶意尺寸/坏图；IMG-03GIF/WebP帧延迟/循环/暂停恢复/合成；IMG-04快速重绑/离屏/viewport晚返/原buffer；IMG-05快照/HostAction/国际化与读屏。M0仅演示，M2真实、M3混排资源、M8App、M9平台；具体像素/缓存和帧延迟政策按指标表实施前冻结。图片不占硬件视频实例但占内存/解码工作；不可仅“打开首帧”标动画PASS。
