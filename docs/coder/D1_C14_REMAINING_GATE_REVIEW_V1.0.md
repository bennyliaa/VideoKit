# C14 剩余架构门禁评审 V1.0

2026-10-16。原始需求全P0保持；正式Flutter App＋独立Kit/AAR、多宿主与C ABI方向保持。C14是Debug可行性候选，设备执行NOT_RUN；D1未通过，不进入M0。C12平板52 PASS、手机52 ENVIRONMENT_BLOCKED只属于C12已覆盖路径。C13 self SIGSEGV App系统signal0严格FAIL，独立双槽方法signal11 PASS；App trace缺失/ordinary UNKNOWN OPEN。C14退出采集不变，两项明确NOT_RUN_UNCHANGED_PLATFORM_LIMIT。

## 原文§29十二项逐项对应

| 项 | 现有证据与本批决定 | 未证/后续阶段 |
|---|---|---|
| 1 group/artifact/namespace/version | 内部Maven group com.videokit、SDK namespace com.videokit.<module>、App com.videokit.app已由PROJECT_DECISIONS决定；Debug c14独立、逐文件hash | 内部命名不撤销；正式artifact/语义版本/兼容与迁移待验证；M0契约、M7独立AAR |
| 2 播放/编辑产物拆分 | 实验目录隔离，不引Browser业务 | core/playback/edit/export薄适配拆分及依赖边界待M0/M7；不是当前App目录即SDK |
| 3 Media3/图片/编码/FFmpeg替代与许可 | Media3 1.9.3、受限FFmpeg8.0.3及五库不变；新增公开系统AVC和既有fMP4封装胶水 | 完整危险链、发行/替换/专利条件、图片方案性能OPEN；M1/M2/M6/M7 |
| 4 人脸/物体技术/模型/许可/最低设备 | YuNet/ViTTrack候选精确commit与LFS身份复核，未下载权重；见跟踪证据报告 | 训练/权重再分发/样本人物权利与真实标注、质量/最低设备均OPEN；M5前有限实验 |
| 5 输出容器/codec/preset | 既有host H264/AAC双轨C12 PASS；C13两新管线正例configure FAIL，14反例BLOCKED；C14有限四配置协商保持六帧无音频fMP4/AVC | 设备新路径NOT_RUN，不能代替正式MP4/H264/AAC预设；分辨率/码率/HDR/颜色/音频矩阵M6 |
| 6 remux兼容 | 历史受限容器读取/host输出证据保留 | 时间戳/edit-list/旋转/音频/字幕/不可无损条件与明确fallback待M6；六帧重编码不证明remux |
| 7 跟踪/导出/内存/发热阈值 | C14硬限额：CPU2、encoder1、queue2、147456B/帧、6帧、2MiB输出；实际Android RSS/耗时/热NOT_RUN | 完整多轨/分辨率/长时与最低设备分级、超温降级、跟踪质量阈值待M3/M5/M6 |
| 8 Compose/View/engine组合 | 原生Debug方法可编译，未交Flutter UI | View/Compose/Flutter texture/engine生命周期与多实例矩阵待M0/M1/M7/M8 |
| 9 Sink顺序/随机/FD | 复用FencedTask/租约/READY/abort/reconcile；新通道顺序写硬限额，close/fsync后独立验证 | 产品宿主Sink协议、跨宿主FD代理/替换/随机访问能力协商待M0/M6/M7；READY不是业务COMMIT |
| 10 schema/迁移/恢复 | 既有journal/epoch恢复回归保留；新管线owner-drop反例，未冒充新管线实际宿主死亡实测 | 正式工程schema、版本迁移、undo/revision、跨设备恢复待M0/M4/M6 |
| 11 控件/主题/overlay API | 现有实验不修改产品UI | 可嵌入控件/主题/无障碍/坐标变换/遮罩编辑契约与Flutter接入待M0/M1/M2/M5/M8 |
| 12 共享池/hw codec预算算法 | 复用每宿主进程CPU2槽，新增encoder/output1许可；实际未释放保留PENDING | 不是跨进程/跨宿主全局池；公平性/抢占/显示音频/多路硬codec能力算法待M0/M3/M7 |

无一项因本机断言数自动升级为完整产品通过。M0 API/Fake/TestKit未完成；M1播放、M2图片/宿主操作、M3多槽音频、M4时间线、M5跟踪遮罩、M6导出隐私、M7独立Kit、M8 Flutter仍需原P0验收；Apple/Windows不启动。

## 显示与PCM下一项有限能力设计

显示：沿用隔离解码固定RGBA，宿主专用render线程接受不可变FrameLease，队列2、在途1；先做公开Canvas/Bitmap软件显示的有限六帧探针，检查真实截图方向/画面和首帧/seek代次，随后单独评估Texture/GL/Surface。UI只提交Surface generation与销毁意图，render线程停止提交并实际释放Surface/Bitmap后归还许可；Surface销毁/消费者失联/迟到旧帧须拒绝。系统Graphics JNI、驱动与宿主显示权限风险仍列OPEN；不在已知不可用的ordinary isolated重复GPU探针。

音频：另批仅许可通过的离线输入，经隔离解码产生固定48kHz/双声道/PCM16块，按实际sample-index/原时基携带task/epoch，单块≤20ms=3840B、队列4、在途1；总时长/字节预先有限。宿主单AudioTrack owner线程检查声道/采样格式/长度与时基，实际write返回、音频焦点、暂停/seek清空与stop/flush/release分开记账，UI不持锁等IPC。以回环/外部录音或可审人工听音证明真实声音，缓冲接收不是声音。AAC/HE-AAC/AC3支持及授权另审，不扩本批受限FFmpeg白名单；C14不含音频解码接续实现。

## 完整危险链与剩余证据

详见边界设计逐环节表。新管线压缩源与压缩输出解析位于ordinary isolated；宿主仍有MediaCodecList/configure/MediaCodec/图像平面及AndroidLease JNI，旧双轨MediaExtractor验证、字幕/图片/跟踪遮罩/Surface/PCM隔离尚未闭合。同UID分进程和系统服务均不是完整权限隔离。短六帧实验不证明持续播放、真正实时帧流、任意恶意输入安全或被攻陷worker不能伪造结果。

下一步只由负责人安排完整候选设备测试；先实际环境和CPU MP4/AVI，再新管线两正例，按依赖执行反例、完整host/legacy回归。手机禁用保持ENVIRONMENT_BLOCKED，不换包名、卸载、清数据或强启绕过。失败/能力不支持/未知执行分别保留，不能用清理完成或末尾进程空补成功。

C14新增能力选择和分阶段诊断，不改变任何质量/PTS/EOF阈值；所有本批设备方法NOT_RUN。完整C13报告52 PASS/3 FAIL/14 BLOCKED保持，不用本机纯规则通过覆盖失败。设备候选是73可调度＋2原信号门禁明确未重跑，不将后者计PASS。
