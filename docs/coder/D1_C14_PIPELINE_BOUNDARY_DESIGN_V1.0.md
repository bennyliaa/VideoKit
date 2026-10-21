# C14 单APK真实帧接续边界设计

日期：2026-10-16。沿用C13裸数据/PTS/内容/EOF边界，编码选择变更见D1_C14_ENCODER_NEGOTIATION_DESIGN；D1未通过，不进入M0。C12平板52 PASS仅作为已覆盖路径基线，手机52环境阻断；历史status0/ordinary UNKNOWN/trace缺失不改判。

## 有限实验与预算（先冻结实验约束，再实现）

这是一条Debug视频专用可行性探针：6帧、256×144、RGBA8888、旋转0，每帧147456字节；原MP4/H264或AVI/MPEG4只读源，目标从2秒开始每200000微秒取得一帧，记录实际解码PTS和原时间基。每次调用复用C12单帧CPU隔离链，串行创建/实际释放任务，不增加并发解码许可；不是连续实时decoder产品或合成图案编码。原始PTS必须严格递增，无法区分的静态片段不作为“画面接续成功”证据。

| 资源 | 硬性实验上限与证明 |
|---|---|
| CPU任务 | 复用C12宿主进程内2槽，producer任意时刻最多1个CPU任务；另一个实际任务可继续。多宿主/跨进程全局预算仍OPEN |
| 源/FFmpeg | 原codec/容器白名单、64MiB累计申请/4096记录、16MiB单次、读/packet/像素和VMS边界不扩；每个读句柄真实关闭后才推进 |
| 裸数据 | 队列2帧、消费者1帧、producer候选1帧，包括C12 Frame及复制中瞬时副本，保守至多8个宿主拥有的可达RGBA数组1179648字节（不是整个RSS或ART未回收堆上限），固定YUV420 scratch55296字节，6个小缩略/哈希记录；不共享可变内存 |
| 帧协议 | 固定尺寸/步幅/长度/乘法、task/epoch/内核PID/UID/序号/原始时间基/PTS/旋转检查；metadata先验证才分配额外复制。旧代、伪造、乱序、截断、旋转和总量溢出拒绝 |
| 编码/输出 | 独立1个编码/输出实验许可；最多6个编码输入和输出样本，每样本≤262144字节、codec CSD总≤65536字节；单输出≤2097152字节，写通道对包含容器头在内的每次写实施硬限额；专用目录最多24 journals、累计4MiB输出，创建前预留完整2MiB |
| 系统编码 | 公开MediaCodec AVC ByteBuffer输入，支持标准YUV420Planar/SemiPlanar或公开Flexible YUV_420_888 Image三平面，检查base/limit/rowStride/pixelStride，先清padding再写逻辑像素；只有无支持格式才CAPABILITY_BLOCKED；已选configure/start实际拒绝仍失败，close未证为PENDING，无Surface/GPU/宿主源解码回退。Media3 1.9.3 FragmentedMp4Muxer封装，明确为无音频fMP4/AVC实验 |
| 等待 | 帧队列offer≤500ms；单输入/输出codec轮询有deadline；整任务预算≤60秒。超时返回PENDING/失败意图，实际native/回调未返回不得释放许可、FD或声称终态完成 |

颜色转换仅为固定小RGBA到标准YUV420的自编数据适配，不实现codec。源PTS减去第一源帧PTS得到编码输入PTS，不按名义帧率伪造源时间。记录每帧原身份/PTS/摘要→编码输入PTS→编码输出PTS→隔离验证解码PTS，以及画面误差和至少两个不同真实帧。压缩误差门槛只用于此低分辨率可行性探针，不是打码质量、色彩保真或正式输出预设。

## 实际调用与信任边界

| 环节 | 进程/权限/依赖 | 本批状态与残留风险 |
|---|---|---|
| Source broker | 普通宿主UID，只按授权readAt传字节；无凭据/源路径进Binder | 复用C12；宿主接触不透明压缩字节但不调用源Extractor/decoder |
| 容器/压缩解码/缩放 | 同APK ordinary isolated UID，受限FFmpeg8.0.3 | 新探针仍仅MP4/H264、AVI/MPEG4；旋转矩阵非单位阵拒绝，不暗中导出错方向 |
| 裸帧接收/队列/颜色适配 | 宿主Java，校验后受控复制 | Binder复制及不可变Frame；无SharedMemory、無FD裸帧TOCTOU。宿主仍信任经过限界的裸数据布局，不声称所有像素输入都使系统encoder无漏洞 |
| 系统编码与封装 | 宿主MediaCodec公开API→系统/vendor服务，Media3 Java fMP4 muxer | 输入只有受控裸数据；CodecList/configure/MediaCodec JNI仍在宿主，属于完整危险链OPEN，系统服务不是完整隔离证明 |
| 临时Sink/事务 | 宿主显式授权目录、既有FencedTask/AndroidLease与SinkCoordinator | 有界顺序写、实际close/fsync/租约、READY/abort/query；READY不等于业务提交。同UIDowner锁不是权限隔离 |
| 输出独立验证 | 同APK ordinary isolated CPU，授权临时输出只读broker | 新受限验证模式要求仅1条H264视频轨、256×144/旋转0、恰6帧、严格PTS、完整decode至EOF及小画面摘要；宿主不使用MediaExtractor解析此探针输出 |
| 字幕/图片/跟踪/遮罩 | 现有宿主Media3/平台图片/FaceDetector/自有模板等 | 不进入本视频专用探针；不可信解析/JNI隔离及真实效果仍OPEN。不能把ByteBuffer接收称真实显示/声音 |
| 显示/PCM/音频 | 本批未创建Surface/AudioTrack，视频输出audioPresent=false | 后续有限设计分别验证Surface/GL/Texture真实显示、PCM有界时基/单音频epoch/焦点与实际声音；系统/同UID分进程不冒充权限隔离 |

新输出验证不得调用旧AndroidOutputValidator作为快捷通过。旧host双轨验证继续原7项回归，路径在宿主的风险仍OPEN；不能删除或把它外推为新隔离验证成功。压缩输出的FFmpeg验证仍具有解析器自身风险，隔离结果是有界技术证据，不是抵御已被攻陷worker伪造结果的绝对证明。

## 所有权、取消与失败终态

管线对象保留Provider直到producer不再可能打开后续句柄。本探针没有产品源移动/删除通知API或源文件强制锁；调用方须在整管线实际释放前保持授权源只读。单个CPU句柄关闭不是整管线完成通知。每帧复制后归队列/FrameLease；消费者finally归还，取消清空仅仍属队列的帧，不回收仍在途消费者。生产者当前CPU任务须实际death/Source/回调/解绑/槽回收；raw数组转交后的生命周期由独立帧预算记录。

codec、muxer与Sink调用均由同一编码owner线程执行；cancel只设置意图、撤销Source/队列，不跨线程强行release codec。消费者慢/失联、队列满、解码失败、伪帧、编码输入拒绝/错误、写/flush/验证失败都不能READY。只有所有输入已释放、codec与writer真实归还、输出租约清零、隔离完整验证和画面/PTS检查通过才请求READY。

失败在实际writer关闭前保留ABORT_PENDING；超时/close异常保留引用与quarantine，不能靠GC或末尾ps空证明释放。READY丢响应继续同一exportId query/reconcile，不开第二输出；宿主恢复复用FencedTask持久epoch/owner/worker lease，WRITING重新由获权owner幂等abort，READY查询同一token。新的owner-drop恢复试验与既有真实宿主进程死亡legacy回归分别记录，不冒充本批新管线实际宿主SIGKILL已测。

不在ordinary isolated重复已知不可用MediaCodec/GPU探针，不增加companion或高权限绕行。正式Flutter＋独立Kit/AAR/C ABI、多宿主、原文所有P0和§29十二项仍须后续明确决定；本批不能直接进入M0。

C14至多四个原生创建尝试且仅在上一codec/Image/owner calls已实际归还后下一，配置期间不创建Source producer或输出writer。候选失败历史不被后续选中抹去；运行期错误不重选。runtime账本新增queued/offers、保留CPU任务、codec/Image/转换RGBA/YUV引用、creating和owner calls；这些逻辑持有计数不代表ART堆/RSS实测峰值。统一8份RGBA1179648B＋YUV55296B，无5份预算。
