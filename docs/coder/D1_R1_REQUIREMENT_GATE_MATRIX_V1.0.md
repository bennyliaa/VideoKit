# D1 R1 需求与准入来源矩阵 V1.0

2026-10-16。只读审查与建议，D1未通过、M0未启动。原始P0、已确认决定、历史FAIL和C14冻结均保持。本表中的“建议退出证据”须负责人审定；没有修改当前用例、阈值或许可准入。

## 1. 来源索引与证据时点

| 代号 | 精确来源与用途 |
|---|---|
| U | [原始需求](D:/CodexProjects/VideoKit/docs/VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)；重点§26测试、§27正式发布/集成阻断、§28阶段、§29十二项、§30交接、§31成功标准；以下保留具体小节 |
| D | [PROJECT_DECISIONS](D:/CodexProjects/VideoKit/docs/PROJECT_DECISIONS_AND_EXECUTION_V1.0.md:5) §1–3、5；Android先行/Flutter/独立Kit/C ABI/命名及负责人权限。旧设备连接段落由本次R1派发的最新事实覆盖 |
| S/A | [SYSTEM_ARCHITECTURE](D:/CodexProjects/VideoKit/docs/SYSTEM_ARCHITECTURE_V1.0.md) §1–6；[PUBLIC_API](D:/CodexProjects/VideoKit/docs/PUBLIC_API_CONTRACT_V1.0.md) §1–8，仍是未冻结草案 |
| E/T/L/M | [EDIT](D:/CodexProjects/VideoKit/docs/EDIT_TIMELINE_AND_EXPORT_DESIGN_V1.0.md) §1–6；[TRACKING](D:/CodexProjects/VideoKit/docs/TRACKING_TECHNICAL_SPIKE_V1.0.md) §1–6；[LICENSE](D:/CodexProjects/VideoKit/docs/OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md) §1–5；[MILESTONES](D:/CodexProjects/VideoKit/docs/MILESTONES_V1.0.md) §1–4 |
| G | [既有D1准入评审](D:/CodexProjects/VideoKit/docs/coder/D1_ARCHITECTURE_GATE_REVIEW_V1.0.md) §2–5、7–8：C06时期的来源分析和退出建议；其旧证据不覆盖C12–C14新事实 |
| B | [D1初始派发](D:/CodexProjects/VideoKit/docs/milestones/D1_CODER_REQUIREMENTS_V1.0.md) 完整范围2–7/退出条件；[C03](D:/CodexProjects/VideoKit/docs/milestones/D1_C03_CODER_REQUIREMENTS_V1.0.md) 1/3/5/6；[C04](D:/CodexProjects/VideoKit/docs/milestones/D1_C04_CODER_REQUIREMENTS_V1.0.md)末段；[C05](D:/CodexProjects/VideoKit/docs/milestones/D1_C05_CODER_REQUIREMENTS_V1.0.md)2；[C06](D:/CodexProjects/VideoKit/docs/milestones/D1_C06_CODER_REQUIREMENTS_V1.0.md)1；用于区分实验追加约束 |
| R12 | [C12报告](D:/CodexProjects/VideoKit/docs/tester/D1_C12_TEST_REPORT_V1.0.md)：平板52 PASS、手机52环境阻断；注册/解绑/代次/特定真实CPU帧、host双轨与legacy证据；两次OS11、trace缺失 |
| R13 | [C13报告](D:/CodexProjects/VideoKit/docs/tester/D1_C13_TEST_REPORT_V1.0.md:111)：52 PASS/3 FAIL/14 BLOCKED；两configure失败、self OS0严格FAIL、独立双槽OS11，资源终态分栏 |
| C14 | [C14交付](D:/CodexProjects/VideoKit/docs/coder/D1_DELIVERY_D1-20261016-C14.md)、[协商设计](D:/CodexProjects/VideoKit/docs/coder/D1_C14_ENCODER_NEGOTIATION_DESIGN_V1.0.md)、[设备附录](D:/CodexProjects/VideoKit/docs/coder/D1_C14_DEVICE_APPENDIX_V1.0.md)、[剩余门禁](D:/CodexProjects/VideoKit/docs/coder/D1_C14_REMAINING_GATE_REVIEW_V1.0.md)：833 JVM＋38脚本，非设备成功 |
| W14 | [tester batch-status](D:/CodexProjects/VideoKit/docs/tester/D1_C14_EVIDENCE/batch-status.json) 2026-10-16 12:38:18及[手机环境](D:/CodexProjects/VideoKit/docs/tester/D1_C14_EVIDENCE/phone/environment.json)：73环境阻断、平板未检测到、0 instrumentation、无在途；该快照明确finalReportNotWritten。本次[R1正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_R1_CODER_REQUIREMENTS_V1.0.md)补充用户暂不能连接、测试任务结束等待。未虚构C14正式测试报告 |
| K | 当前冻结源码[AsyncReadBridge](D:/CodexProjects/VideoKit/docs/coder/d1c14/src/com/videokit/spike/c14/AsyncReadBridge.java)、[LeaseRegistry](D:/CodexProjects/VideoKit/docs/coder/d1c14/src/com/videokit/spike/c14/LeaseRegistry.java)、[CpuTaskClient](D:/CodexProjects/VideoKit/docs/coder/d1c14/android/com/videokit/spike/c14/CpuTaskClient.java)、[RealFramePipeline](D:/CodexProjects/VideoKit/docs/coder/d1c14/android/com/videokit/spike/c14/RealFramePipeline.java)、[SinkCoordinator](D:/CodexProjects/VideoKit/docs/coder/d1c14/src/com/videokit/spike/c14/SinkCoordinator.java)；以下按方法名定位，不把阅读当运行测试 |

## 2. 原始P0、决定与追加门槛分开追踪

| 项/类别、精确来源 | 已证范围与缺证/矛盾 | D1有限退出建议、下一步与责任阶段 |
|---|---|---|
| P01 输入只读/授权/凭据隔离；U§11.1、13.1、14、22、27、31.1/8 | R12/R13指定只读fixture hash不变，broker传opaque身份与字节；K HostFixtures仅r打开。没有真实NAS/产品source resolver全链路证据 | 负责人确认授权/源版本/能力失败语义；coder/tester按评审E2验证真实provider迟到取消和大偏移。D1定机制，M0统一契约，M1实际NAS与大视频，M6/M7安全/集成 |
| P02 会话故障不影响宿主/他槽；U§2.2、16.2、26.4/7、27 | R12限定CPU/native crash另一槽存活、资源归还；R13 self信号FAIL但原代资源归还。宿主codec JNI、旧验证/字幕/图片/显示/跟踪链未闭合 | E1先证真实处理接续，E3列宿主JNI可接受边界/不可行替代，并以实际受控故障和释放证明机制。D1路线必须处置，M3/M6验完整产品；精确signal分类另列X01 |
| P03 新输出只入临时Sink/源不变/失败不READY；U§11、17、26.5、27、31.7/8 | R12/R13 host7/legacy8限定H264/AAC、故障/恢复PASS；新单APK六帧在C13 configure失败，C14未运行 | E1正常六帧及原14反例一次完整验证；E2明确可读验证租约、顺序/随机/FD能力。D1证明机制，M4/M6完整编辑/输出，M7业务COMMIT |
| P04 稳定错误/能力反馈；U§5、19.3/4、26.1 | C14阶段诊断本机可查；C13 configure错误不能唯一认定颜色/profile/权限。Debug CPU_*、PIPE_*尚未成为正式公共码表 | 负责人接受UNKNOWN为真实诊断状态的候选语义，但现严格FAIL不改；M0映射U§19.3稳定码/阶段/retryable，E1保留逐尝试真实错误与终态 |
| P05 随机读取/取消/实际SourceReleased；U§14.2/4、17.4、21、26.1/2/7、30 | K有64位、短读、取消与迟到计账；R12有真实CPU句柄释放。逻辑大偏移fake不是大视频播放；单CPU关闭不是源所有消费者归零 | E2有限真实provider/aggregate lease验证，见§4差距。D1必须定清释放含义；M0 Fake/TestKit，M1/M4产品输入，M7宿主移动队列 |
| P06 多实例/唯一音频/有界降级；U§8、16、21、26.4、27 | 进程内CPU2、encoder1已编码；不等于跨宿主全局预算、真实1/4/9/12混排或系统OOM隔离 | D1证两任务独立/超额拒绝和不可释放保留，决定宿主注入预算及audioEpoch权威；M3完成混排、热/压力/唯一发声。12不是任意设备12路硬编保证 |
| P07 播放/字幕/图片/宿主动作/UI；U§4–9、15、18、20、26.2/3/7/8、31.2–6 | 旧限定媒体/平板反馈不证明手机AVI挂起/MKV无声已修复，也没有Flutter产品UI；C14只解码MP4/H264与AVI/MPEG4 | D1列实际可行后端与正式格式缺口，E3有限显示/声音边界；M1/M2真实播放图片与回调，M8 Flutter/语言/无障碍。缺样本NOT_RUN，不把所有图片UI矩阵塞D1 |
| P08 编辑拼接/打码与自动人脸/物体跟踪；U§10、26.5/6、27、31.7 | 时间线/遮罩设计有草案，真实跟踪标签0，FaceDetector数量/模板不能代替自动P0；六快照不是实时编辑器 | E4确定合法候选/最小真实纠正与LOST可行性及资源量级；M4时间线，M5全部跟踪/质量，M6输出逐帧保护。原P0不删除，D1不要求先造完整M5 |
| P09 隐私/闭源许可/发行；U§22–25、27；L§1–5 | Media3锁定、受限FFmpeg Debug source/NOTICE/SBOM有证据；外发替换/再链接/专利/模型权利不同层未闭合 | E4由负责人裁定具体使用/分发边界；M0只能使用已准入依赖，M6/M7/M10完成实际产品义务。不能把目录许可、动态链接或单独进程当免责 |
| P10 独立AAR/可移除回退；U§13、24/25、26.7、27、31.9/10 | 当前app的Debug源目录不是独立Kit；companion证明协议不证明单APK产品；多宿主Manifest/签名/R8未实测 | D1先定无硬编码宿主/无另装产品路线；M0最小两个样例宿主与Fake契约，M7实际AAR独立构建/移除/升级。不得等待到M7才发现接口依赖Browser |
| P11 设备/语言矩阵；U§26.8、D§1、M§2 | R12/R13为API31/ARM64/4KiB页的限定设备，手机环境阻断；C14无实机。没有中间/当前Android、字体100/130/200%、中英/伪本地化/RTL产品证据 | D1先在合格设备取得所选路线证据并列手机关键差异；M1/M3/M6/M8逐步完成原系统/手机平板/窗口/字体语言矩阵。不能以一台平板或静态16KiB对齐外推全设备通过 |
| D01 已定架构；D§1–3；S§1–5 | Flutter App、无Flutter依赖的原生Kit、C++编辑领域/C ABI、原生播放状态单一权威、Media3薄适配已定方向；bridge未实现 | 负责人维持决定；M0写API/绑定/预算所有权决定和依赖图，M7/M8验各宿主。R1不再向用户重问选Flutter或内部命名 |
| D02 Android先行；D§2；S顶部最新决定；M§2 | S§7旧稿仍写跨平台架构冻结前实测，与新执行决定时点冲突 | 采用最新决定：D1–M8聚焦Android，Apple/Windows只设计、M9阶段再实测；负责人登记时点解释，无需改冻结原稿或将未实现标支持 |
| X01 App精确native cause/signal；B中C05-2、C06-1；后续[C10](D:/CodexProjects/VideoKit/docs/milestones/D1_C10_CODER_REQUIREMENTS_V1.0.md)/[C11](D:/CodexProjects/VideoKit/docs/milestones/D1_C11_CODER_REQUIREMENTS_V1.0.md)及R13§C13-T02 | 原文U§27要求故障后果安全，不逐字要求App每次读到11/tombstone；现追加严格方法有效，R13系统0 FAIL与外部raw11/实际death分别成立；R12 OS11不覆盖R13 | 负责人选择：保持硬门槛并等待具体可改变的采集条件；或另立书面版本，将可观测性和功能隔离分别裁定、保留历史FAIL。当前不批准任一变更，C14两项NOT_RUN，不同条件新假设前禁止循环重跑 |
| X02 单APK/UID边界；B中C04末段、G§4；[C13正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_C13_CODER_REQUIREMENTS_V1.0.md)1/5/7 | 原文要求独立Kit/故障安全，具体ordinary isolated与不另装companion是已派实施约束；同UID多进程只可称故障边界 | D1必须证明符合当前约束的组合路线或交不可行决定；若残留JNI需换进程形态，先由负责人另审，不自行放宽或把实验companion产品化 |
| X03 六帧/色差/队列/编码尝试；C13需求2–5、C14需求1–6及协商设计 | 6帧/256×144/≤1ms/luma24/差异4与2、queue2、encoder1、4尝试/12秒、8数组是当前实验约束；C13未进入，C14未实测 | E1沿冻结门槛测，不能调阈值求通过。通过只关闭该有限接续假设；正式清晰度/持续性能/高分辨率按U§29.7及M3/M5/M6另冻结 |
| X04 跟踪10clip/1000标签；[C03样本协议](D:/CodexProjects/VideoKit/docs/coder/D1_C03_TRACKING_SAMPLES_AND_LABELS_V1.0.md:18)、G§7 | U§26.6要求场景与质量，无指定10×100数量；该D1实验计划仍有效，当前0实际标注，团队组织责任不全推用户 | 先盘点现有素材可覆盖场景再补差；负责人可书面决定分层先做有限技术筛查，但未经决定不缩减原计划、不称样本完成。M5/M6仍验完整真实保护 |

## 3. 原文§29十二项：现在可决定什么

每项均来自U§29、M§3及C14剩余门禁；本列为评审候选，不是已冻结公共API。

| 项 | 当前证据/缺口 | 建议决定或最小验证；责任阶段 |
|---|---|---|
| 1 命名/版本 | D§3内部com.videokit/`com.videokit.<module>`/com.videokit.app已定；C13“未定”旧文字不撤销它 | 负责人沿内部命名，M0决定artifact/API与schema分版/SemVer规则；M7测实际兼容/仓库，不申请公共发布 |
| 2 播放/编辑拆包 | S§3和D§3有模块计划，当前只有Debug | M0依赖图保证playback不拉tracking/export/UI；M7用实际可移除artifact验 |
| 3 框架/许可 | Media3 1.9.3与FFmpeg8.0.3受限Debug已锁；图片/正式兼容后端未准入 | E1/E4据实际能力和义务裁定后端候选；M1/M2/M6覆盖格式，M7发行审计 |
| 4 跟踪/设备 | YuNet/ViTTrack只有固定指针和目录证据，无实权重/标签 | E4固定许可/实际权重/最小真实路线与最低设备假设；M5完整质量 |
| 5 输出预设 | D§3首轮MP4/H264/AAC/SDR；旧host通过，新video-only未证 | E1验证无音频接续不代替双轨；负责人冻结首轮预设能力失败语义，M6验正式组合 |
| 6 remux | E§3列参数/关键帧/PTS要求，六快照重编码无证 | 先采用保守“全条件匹配才允许remux”的设计候选；M4/M6正反例与实际边界，不以同后缀判兼容 |
| 7 指标 | 当前有限配额非正式速度/热/漏码阈值 | D1给资源量级与测法；M3/M5/M6按设备/场景数据审定，不先要求全量性能实现 |
| 8 UI/引擎组合 | D/S已定无UI原生Kit＋可选View/Compose＋Flutter App | E3先有限显示/销毁可行性；M0接口不含Flutter/Media3类型，M1/M7/M8测平台目标/engine生命周期 |
| 9 Sink能力 | host seekable本地文件与fMP4 sequential channel各有实现；通用FD未证 | E2决定能力声明和验证只读租约；M0 Fake分别拒绝不支持模式，M6真实容器/Sink |
| 10 schema/恢复 | E§1/5工程revision、源指纹、编码可重启；实验journal不是项目schema | M0决定版本/未来主版拒绝，M4迁移/重绑定，M6编码恢复/所有权；不默认续编码字节 |
| 11 控件/overlay | U§20与S§3描述方向，未有产品API | M0冻结低频交互/坐标语义候选，M1/M2/M5/M8实际主题/无障碍/遮罩，D1不造全套UI |
| 12 资源池算法 | K static CPU2/encoder1是进程内实验；S§5要求宿主注入 | M0定宿主预算对象/释放证明/拒绝原因；E3最低2任务边界，M3热/公平/1–12混排，M7多宿主 |

## 4. 公开API/源/Sink可冻结差距

建议接受下列安全不变量进入评审基线：opaque token、int64时间/偏移、代次拒旧结果、只读输入、取消≠完成、真实消费者/在途/close全部归还、输出先close/验证后READY、同ID查询未知结果、业务COMMIT归宿主。**当前整体仍不可宣布基础契约冻结**；下表差距需要负责人作决定及有限验证。

| 差距/来源 | 当前代码与证据边界 | 具体决定候选/下一步/阶段 |
|---|---|---|
| A01 未知长度/非seekable；A§3、U§14.2 | AsyncReadBridge.open可返回-1；CpuTaskClient构造及CpuFrameRules.sourceLength要求1..1TiB并seek，C12拒绝未知/空是该后端证据，不是全Kit支持 | 单独声明knownLength、seekability、并发读能力；不能把-1当空源。E2测可顺序读取与不可seek的稳定反馈，M0/M1决定适用后端；不得偷偷全量暂存或删原随机读P0 |
| A02 真实provider取消/迟到；A§3/6、K.invoke/close/CloseTicket | privateBuffer、在途计数、迟到open清理和≤3close尝试有代码/本机反例；R12真实本地Source取消通过；无真实SMB/SAF全组合 | E2选择一个授权真实provider做阻塞read、迟到open、close失败/恢复各有限一次，取消立即响应而未证资源继续保留。超时预算按provider可取消性分开，M0 Fake/M1真实实现同套契约 |
| A03 长度冲突/源变化；A§3；K.read | 当前read校验0/越界/溢出，但n=-1在已知remaining>0时未在该方法显式分类；静态差异，不据此伪造设备FAIL | 决定提前EOF映射CORRUPT_MEDIA或新增SOURCE_CHANGED公开码及source fingerprint语义；M0契约反例、M1真实变化。不可从“已知长度”推出内容稳定 |
| A04 2GiB偏移；U§26.2、A§3；C14CpuSourceSelfCheck | 自检用逻辑16GiB provider在8GiB+17读1字节，不是大视频/NAS播放；45素材有3,212,959,911B MKV | E2经实际ReadHandle读2GiB边界前后固定小块并对照宿主hash；不让只支持MP4/AVI的CPU偷解MKV。M1再测完整seek/播放，不改样本 |
| A05 SourceReleased所有消费者；U§14.4/26.7、A§6、K.LeaseRegistry | 每个CpuTaskClient自己的generation/registry，RealFramePipeline保留Provider；没有产品级按mediaToken/源版本聚合播放+编辑+跟踪租约和宿主移动队列 | 建议由宿主源租约管理器聚合consumerId/代次，通知丢失可查询；不得一个CPU关闭就移动文件。E2最小双消费者＋迟到操作，M0接口/M1/M4/M7集成 |
| A06 输入授权；U§22/27、S§6、K.CpuTaskClient/HostFixtures | binder内核身份/task/epoch校验与r文件句柄有证据；uri是实验opaque路由，未有跨宿主token resolver/源撤销协议 | M0把sourceFactory权限留宿主，token不当永久文件权限；E2撤销后旧代拒绝、无凭据/原路径穿透，M7多宿主授权 |
| A07 顺序/随机/FD Sink；U§17.2、A§7、E§2/5 | AuthorizedSink为授权本地FileOutputStream/Mp4Muxer；PipelineOutputSink为本地文件外包bounded sequential channel。后者不是任意非seekable宿主Sink | 候选显式capabilities/flush-close/durability及可读验证lease；所需能力不符在写前OUTPUT_CAPABILITY_UNSUPPORTED。E2最小纯顺序/可seek/FD各对照，M0接口/M6真实空间权限失败 |
| A08 markReady未知/业务COMMIT；U§17.3、A§7、E§5、K.SinkCoordinator | READY_UNKNOWN同ID query/reconcile/abort仲裁有实现和旧host实测；产品Host接口的query未体现在原最小Sink三方法 | 评审补显式query(exportId)、幂等token与取消竞争终态；不重开输出、不把READY当替换/删除许可。M0 Fake/TestKit、M6真实持久化、M7宿主COMMIT |
| A09 验证与恢复所有权；E§5、K.PipelineValidationReceipt/FencedTask | 新隔离验证只视频6帧且未实机，旧双轨验证在宿主；flock/FD lease不是撤销恶意writer的能力 | E1验证新路径；E2决定验证临时只读租约和writer实际死/close后才采信，M6多轨/真实host death。持久task/epoch不替代跨宿主授权 |
| A10 多宿主签名/服务命名；U§25/27、S§7、Debug/worker manifests | CpuIsolatedService exported=false且按context包绑定，但实验进程名固定、static预算进程内；legacy硬编码worker包和signature权限。无两个独立宿主AAR证据 | M0先定AAR服务命名/manifest placeholder与每应用授权；M7两个不同签名样例宿主各独立运行/移除，不能要求它们共享实验签名或安装companion |
| A11 Flutter控制与C ABI；D§3、S§3/4、A§4/8 | 平台会话权威是设计决定，当前Debug Java不是C ABI/Flutter实现 | M0定opaque handle/固定宽整数/retain-release/线程与generation；控制/低频事件走binding，媒体与逐帧裸数据不经Dart往返。E3有限显示目标生命周期，M7/M8真正engine销毁/重建 |
| A12 取消/终态数值；U§21、A§4/6、C14设计 | 5秒/12秒/60秒等属于当前实验，native卡住可能持续PENDING；不是“调用一定可被中断”的保证 | M0区分响应deadline与实际回收状态，暴露可查询资源报告和新任务拒绝原因；M3/M6按设备验证。期限到而资源未证仍不能发SourceReleased/复用许可 |

后续实验E1–E4、成功/失败退出与负责人决定在[架构准入评审](D:/CodexProjects/VideoKit/docs/coder/D1_R1_ARCHITECTURE_ADMISSION_REVIEW_V1.0.md)。R1仅提供评审入口，不实施新接口、用例或门禁修改。
