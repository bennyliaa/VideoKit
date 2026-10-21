# D1 RENDER01 呈现、PCM、源与后端决定

2026-10-20；候选 `D1-20261020-RENDER01`。这是一套有限 Android 可行性实现，不是正式播放器、Flutter App、AAR或D1退出批准。本文只依据已冻结工程材料与本批实际源码；没有设备或最新法律/版本结论。

## 1. 实际路线与隔离边界

新目录为 `docs/coder/d1render01`。实验包 `com.videokit.d1present`、版本1，Activity与instrumentation限定在 `:presentation`；只读CPU服务仍为同APK的 ordinary isolated `:d1_cpu_worker`、`exported=false`。默认主进程为空壳。这是独立、空数据沙箱的实验候选，**不是现有com.videokit.app的升级包，也不读写旧registry、账本、guard、once或现场。不得用此包绕过手机禁用、旧任务UNKNOWN、设备占用或已停止scope。** 本批没有安装；负责人须先审定这个具体身份及独立fixture准备，之后才可能另派设备范围。若要求回到原同包链，应先另审最小集成，不能拿新UID替换旧归还。

保留成熟平台实现：Canvas/Bitmap/Surface/TextureView处理有限原始RGBA，AudioTrack/AudioManager处理合法生成PCM；没有自制GL、codec、容器、编辑或控制框架。C14只读随机输入、task/epoch/Binder身份、原CPU死亡/租约门与受限FFmpeg取帧复用。未带入旧输出/迁移/activation框架；不是删旧门后在旧数据上运行。此选择只适用于这个新空沙箱的只读有限实验。

同UID的`:presentation`只能提供地址空间故障边界，不能宣称RCE/权限隔离。Bitmap、Surface、图形驱动、AudioTrack和音频系统仍有原生危险链；放进真正宿主Kit后会重新获得那个宿主的权限，当前空沙箱不能证明Browser受保护。C14 CPU隔离也不覆盖这些部分。**J11全链权限/恶意输入/故障隔离继续BLOCKED**；不做已知不可用ordinary isolated codec/GPU探针，不注入平台崩溃/卡死或系统OOM求证。

## 2. 原帧、PTS与呈现

`RawSources`有两个明确不同入口。GENERATED生成六个256×144 RGBA控制画面，旋转90°供效果核查，固定时间只属于生成fixture；不冒充真实解码。EXISTING_MP4只接受候选私有 `files/d1_render_fixtures/basic.mp4`，349102B、SHA256 `720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9`；无fixture即拒绝，不猜旧包路径、不重用旧权限。

真实入口直接复用C14 `CpuTaskClient` 的MP4/H264/PIPELINE_FRAME，最多六次、前一原CPU实际停止/死亡/源归还后才下一次。C14已有frame身份/布局/PTS/方向门保持。`RawFrame`保存呈现task/sourceVersion/源epoch，以及原CPU producer task/epoch、真实raw timestamp/timebase/PTS、布局/rotation。真实PTS不按帧序号重造。当前原始来源固定256×144、方向已规范为0；通用接入上限1920×1080不等于这些分辨率已实测支持。

呈现队列是2个等待描述符、1个在途；像素只在原render线程读取和转换。RGBA→ARGB转换后调用Bitmap.setPixels及Canvas，按rotation和目标视口等比适配，没有重采样来源以绕过上限。六帧是snapshot序列，不是连续decode/任意Seek或音画同步。总共最多六个呈现工作位；控制变更拒绝旧工作，再按当前已接受意图和原始帧创建有限新准入，不无限重播。

选择TextureView是为了明确SurfaceTexture归属：UI回调只提交可用/销毁意图；生产者仍持有时，onSurfaceTextureDestroyed返回false，将该原texture交给原render owner。原Canvas调用/unlock返回后，该owner释放原Surface，再释放被转交的原SurfaceTexture。新代ACK与UI意图分开，需原producer退役后由owner确认；不以UI回调到达冒资源返回。尚由View拥有、从未转交的texture由View释放，render owner只归还自己的Surface和借用关系。

暂停/seek/surface generation/取消都先撤销准入。已进入平台的调用可能晚返；本实现不承诺撤销已提交像素，也不把意图当有效ACK。销毁后的旧texture不会成为新代的目标；在途Canvas仍由原owner持有直到unlock真实返回。Surface或texture释放异常为sticky UNKNOWN，不自动二次release。元数据最多8次surface availability事件；之后拒绝新准入并取消，而非扩大持有队列。

## 3. PCM、焦点与唯一声音

PCM是项目本地整数生成器的独立测试声，不是从MP4提取的音轨。PCM16 little-endian、48kHz双声道、3秒/576000B，seed `1447764006`，SHA256 `268d0e111f05ef5ad7ba405df6b78e5e8f6b3a43ebd926c48429d139a27da4ff`。峰值257/32768，头尾10ms渐变，双声道相同。实际源及再生成一致性已经本机核验；无录音、人物、外部作品或模型权重。

AudioTrack由单一原audio线程创建/调用/停止/flush/release；等待队列4、在途1、每块≤3840B，总提交≤576000B，配置stream buffer15360B。每个候选进程只允许一个WorkSession，AudioTrack另有单owner许可；**这不是跨宿主或12槽全局音频算法**。默认setVolume(0)，不请求焦点；测试正常入口保持静音。只在明确点击“Listen”后请求焦点，成功且未丢失时使用低增益0.15，系统音量不改。

实际适配使用本机已测的AudioFocusPolicy：一次显式静音→听音意图只请求一次，拒绝后不逐PCM块重试，焦点丢失后不自动恢复，最多四次显式请求；新的焦点请求前必须实际放弃原请求。放弃焦点异常或未证成功sticky保留，不自动重试。焦点回调在该owner创建的独立HandlerThread上，仅更新策略；close在abandon成功后quitSafely并join同原回调线程，再归还许可。UI不持锁等待这些动作。

epoch变化由audio owner先pause/flush原缓冲后确认；write与drain阶段均处理静音、暂停、失焦和取消。WRITE_NON_BLOCKING的实际返回与播放头排空分开核对。API返回/播放头前进不能代替实际听音；当前所有AudioTrack、焦点、真实声音结果均NOT_RUN。PCM与视频只共享有限生命周期意图，**没有正式AV时钟或压缩音轨同步证明**。

## 4. 共享源与原归还

PresentationSource是只读的、有限raw帧加生成PCM的分段内存视图，不是新媒体容器。两个真实AsyncReadBridge consumer打开同一个provider/sourceVersion，有独立原handle和读位置，共用同一个E13SourceGroup/LeaseRegistry generation。第一consumer结束不retire整代，第二原consumer及所有原操作/close完成后才满足 `retired && consumers==0 && operations==0 && !closeFailed`。

原render/audio线程分别关闭自己的平台对象；coordinator外部join同两线程后才关闭各自源consumer。它还等原loader线程及同原bridge executor线程真正退出；最后释放实际raw数组引用和PCM引用。WorkSession自身的返回也由外部观察并join同coordinator后成立，线程体内的bodyCompleted不自证线程归还。有限checkpoint记录的是实际registry快照，非另一套释放计数。

checkpoint中的`CONSUMER_CLOSED`只表示该consumer的关闭入口已返回，**不是底层Handle.close回调已返**。异步清理仍计入同原registry的operations/failedCloses；物理源操作及线程归还须以最终awaitOriginalReturns与外部join门为准，不能只凭这条checkpoint登记SourceReleased。

本批在副本中补强了bridge Runtime：ThreadPoolExecutor.isTerminated不能代替原Thread退出，登记每个原helper，外部join它们。C14 adapter增加只等待原input线程的接口，不发新STOP/query/重试/创建。实际生产executor的有限未捕获异常尾部用例证明：executor已TERMINATED但原线程仍活时返回门拒绝，原尾释放并join后才通过。旧冻结不改，不把这条本机结论回填旧任务。

取消只提交有限意图并停新准入。已准入source调用、Canvas、write、close、focus或原线程若未返，原WorkSession/Factory/CPU对象及预算持续强持有，后继被拒；30秒不是强finish/杀进程/二close或退款依据。永久UNKNOWN设备分支没有被本机受控late-return测试关闭。

这里证明的是**有限presentation source及其CPU生产者生命周期**。它不是物理NAS文件、图片、字幕、跟踪、导出、后台等所有产品consumer的聚合，也不发HostAction移动/复制许可。

## 5. 预算与仍不能计量的部分

准入窗最长30秒，包括本session加载/排队/呈现/PCM；最多6帧，单帧≤1920×1080、RGBA≤8294400B；不静默降低来源以过门。已知自持有raw原结果、复制、read buffer、ARGB和bitmap像素均计入64MiB reservation。Bitmap分配前保守预留2倍像素，分配后读取getAllocationByteCount核对并归还余量；不能满足则拒绝。释放前必须先丢弃实际引用/回收原bitmap，不只减计数。

该counter的peak是保守**预留峰**，不是RSS。Bitmap平台对象头、Binder Parcel、Surface/BufferQueue/graphics driver、AudioTrack/AudioServer和内核分配不能据其推算；它们的真实峰值、温度、长期、设备差异仍NOT_RUN。当前CPU source的额外读/分配/停止上限保持C14原门，不宣称64MiB是整个App/系统总内存。

## 6. 压缩音频、持续源、Sink与Kit的实际决定

| 对象 | 本批具体决定 | 尚不能冻结/不能宣称 |
|---|---|---|
| 压缩音频 | 当前不准入新解码链；仍以既定Media3/平台后端为首选待审，保留受控进程、宿主随机读、权限和故障owner要求 | 当前受限FFmpeg没有获准音频白名单；禁止扩音频codec，生成PCM不关闭AAC/AC3/MKV/AVI音轨门。已知ordinary isolated codec/GPU不可用路线不重探 |
| 持续播放与Seek | 本批只消费既有真实raw snapshot；真实时间戳和原来源身份向呈现端完整传递 | 没有连续ExoPlayer输入、VFR连续解码/AV同步、NAS异步provider/断线/seek全矩阵；UI“撤旧代”是有限snapshot代次控制 |
| 输入接口 | 内部consumer复用同原AsyncReadBridge增加受检seek/read range，未知/并发读仍遵循原桥门 | 不是M0公共Source API；真实NAS provider、所有业务consumer与完整错误映射仍需契约评审 |
| OutputSink | 保留已审E11/E6限定顺序FD→Media3 fMP4→flush/close→isolated reopen验证事实；本批不创建媒体导出或旧输出恢复 | 不能据此认定Transformer完整输入/Sink、随机写协商、path-only适配、全音轨/长时/空间权限/持久性完成。READY不是宿主业务COMMIT |
| 独立Kit | 新core包不导入Android/Flutter/Browser类型，平台端与技术Activity分目录；C14 JNI绑定包名因旧ABI保留。未来应提取api/core/backend/platform与独立host适配 | 当前仍android.application，不是AAR；Manifest service/进程命名和宿主占位需M0审定，M7独立构建/双宿主/卸载替换/升级回退未验 |
| 公共契约/Flutter | 保持opaque token/sourceVersion、原生单一状态权威、C ABI固定宽/retain-release/代次方向，媒体字节不逐帧往返Dart | 本批的Java内部public方法不是正式稳定API。M0自有Flutter Theme及18页PPT完整UI仍未开始，SkinKit当前不接 |

跟踪模型/权重/人物/样本权利、0真实标注与质量门继续原样BLOCKED；全P0不减项。E11四方法的历史有限PASS、手机差异、C13 signal FAIL/C14未跑项及旧行政false/UNKNOWN不因本候选变化。
