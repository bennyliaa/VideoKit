# D1 R1 架构准入材料独立评审报告 V1.0

日期：2026-10-16；评审方式：离线文档、历史证据与冻结源码交叉审查。**R1材料可作为负责人决策输入，但不构成D1通过、公共API冻结或M0启动批准。** 本轮未操作设备/ADB、未运行Gradle或本机/设备功能测试，未改产品、候选、原需求、门槛或历史结果。

## 结论和判定口径

19项审阅记录：14 SUPPORTED、1 CONTRADICTED、4 MISSING。这是材料主张/决策完备性分类，不是19项功能测试结果。

- SUPPORTED：已核来源支持该项在文中限定范围内的表述，不表示产品能力通过。
- CONTRADICTED：引用版本与实际文件不符；本轮仅发现一处证据锚点问题，没有据此否定实际环境统计。
- MISSING：进入下一次E2/E3契约封口/实验前仍缺少明确语义或可复核判据。R1本身未冒称这些已经实现；下列问题是待补的决策输入，不是新设备FAIL，也不要求本轮实现M0。

总体支持R1维持全部P0、停止无改变信号重跑、保留C14冻结等待、区分D1可行性与M0–M8产品交付的方向。需补充聚合源租约、通用Sink及其验证/恢复标识、E2真实provider判据、E3宿主JNI故障边界四项决策细节，并修正一处引用版本。不能仅将这些继续写成OPEN后宣告D1或基础契约已经通过。

## 输入身份与独立核查范围

| 材料 | 本轮实际SHA256 | 结果 |
| --- | --- | --- |
| D1_R1_ARCHITECTURE_ADMISSION_REVIEW_V1.0.md | 1d9ef7be748f8eb2eb14ba101443613e09ea1937b4c17ca35b610fe477c489e0 | 与正式交接一致 |
| D1_R1_REQUIREMENT_GATE_MATRIX_V1.0.md | 765540887c91258933a8fd71c36b316eca1d9d2bf1837d89ba7e8b95b94571b3 | 与正式交接一致 |
| D1_R1_DELIVERY_V1.0.md | 2fcdbf560943a74645ab34724b5a96f73c56e28f718b676e7f10a70d62b436c7 | 本轮记录的回执身份；没有预给hash，不称其与预给值匹配 |

两主体文档36处本地链接、35个唯一目标均存在，所带行号均在文件范围内；“可打开/行号有效”不等于语义、时点和结论正确。15个关键源码逐个比较C14源ZIP、source-manifest和当前文件，字节一致，已保存审阅副本；包括AsyncReadBridge、LeaseRegistry、CpuTaskClient、RealFramePipeline、两种Sink、SinkCoordinator、FencedTask、验证收据、旧双轨验证器与大offset自检源码。没有重新执行871条断言或重新构建C14。

另核原文§13–19及§26–31、已决事项、系统/API/编辑/集成/许可/测试/里程碑文档、C05/C06追加要求、既有架构门禁、C12/C13报告及C14环境中间报告。既有C07媒体inventory的45条/14 JPEG/9 UNRECOGNIZED与SRT记录一致；这是读取历史清单，不是本轮重新播放、探测或证明素材权利。7份模型文字基线按记录hash核对，C14标注模板确为EMPTY_TEMPLATE、frames=[]。

原始输入副本、hash与链接检查、15份源码比对、引用锚点、模型/清单核查均保存于 [D1_R1_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_R1_EVIDENCE)。本报告的代码判断均为静态事实，不伪装运行结果。

## 逐项独立判定

| ID | 审阅对象 | 判定 | 具体证据与限界 |
| --- | --- | --- | --- |
| R01 | 两主体身份、回执内容身份 | SUPPORTED | 两hash与交接一致，回执另记实际hash；输入副本保留，见input-and-link-audit.json |
| R02 | 36处本地引用可访问/行号有效 | SUPPORTED | 逐链接/行号检查通过；不替代R03的语义时点核对 |
| R03 | W14明确引用“12:38:18快照”的版本 | CONTRADICTED | [矩阵:18](D:/CodexProjects/VideoKit/docs/coder/D1_R1_REQUIREMENT_GATE_MATRIX_V1.0.md:18)链接batch-status.json，实际at为12:41:14、ENVIRONMENT_HOLD；真正12:38:18快照另有文件。见问题R1-R05 |
| R04 | 原文P0、§26–31与§29不因实验删减 | SUPPORTED | P01–P11及§29十二项均有组级归属；原文§27是正式发布/集成阻断，§28将完整功能分阶段。没有把六快照当M5或把手机缺测当通过。组级矩阵仍不是全部子用例已覆盖 |
| R05 | App精确信号/trace与故障后果安全分开 | SUPPORTED | [原文§27](D:/CodexProjects/VideoKit/docs/VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md:1021)没有逐字要求App每次读到11；[C05第2项](D:/CodexProjects/VideoKit/docs/milestones/D1_C05_CODER_REQUIREMENTS_V1.0.md:6)、[C06第1项](D:/CodexProjects/VideoKit/docs/milestones/D1_C06_CODER_REQUIREMENTS_V1.0.md:5)和后续严格方法是有效追加门槛。R1两选项仅建议，不使C13 signal0变PASS，不自行放宽P0 |
| R06 | C12/C13/C14实际结果及未运行范围 | SUPPORTED | C12平板52 PASS；C13平板52/3/14、手机69环境阻断；C14仅环境预检，无安装/功能测试，73待调度另2信号NOT_RUN。核对三份tester报告及C14 phone/results、not-run-plan。C14本机871不是设备PASS |
| R07 | D1与M0–M8边界、E1等待C14 | SUPPORTED | 原文§28、最新执行决定、MILESTONES均区分有限可行性与产品阶段；R1没有以“以后实现”解除Source/Sink、合法组件路线或核心隔离不可行。C14未实机，不应另造候选掩盖等待 |
| R08 | 单APK/Kit/Flutter/Media3及完整危险链 | SUPPORTED | 冻结PipelineEncoder调用宿主MediaCodec；旧AndroidOutputValidator、字幕处理仍在宿主。新验证收据只适用六帧视频。图明确未贯通，不以系统服务、同UID或companion等同完整权限/故障隔离 |
| R09 | 未知长度、提前EOF、大offset的当前限制 | SUPPORTED | AsyncReadBridge.open支持未知长度；CpuFrameRules/CpuTaskClient实验后端要求正长度。read:113允许n=-1，未在该处分类“已知remaining仍正的提前EOF”。CpuSourceSelfCheck在逻辑16GiB provider的8GiB+17读1字节，不是实际大媒体/NAS播放 |
| R10 | 当前只有单任务/管线资源账本，没有产品聚合租约 | SUPPORTED | [CpuTaskClient:59](D:/CodexProjects/VideoKit/docs/coder/d1c14/android/com/videokit/spike/c14/CpuTaskClient.java:59)各自new LeaseRegistry；[RealFramePipeline:87](D:/CodexProjects/VideoKit/docs/coder/d1c14/android/com/videokit/spike/c14/RealFramePipeline.java:87)等待整个producer而非单句柄关闭。无全Kit源身份聚合接口，R1如实列差距 |
| R11 | 可直接据A05冻结聚合SourceReleased语义 | MISSING | 未定物理源/源版本与opaque token等价关系、未来open的消费者预留、禁止新引用与最终通知的原子边界；仅“双消费者”口号仍不足。见R1-R01 |
| R12 | 可直接据A07–A09冻结通用Sink能力/验证/query | MISSING | 现两Sink是本地文件具体实现；产品缺capability schema、FD归属、验证lease及export/handle/owner epoch对应。存在内部query不等于公共契约完成。见R1-R02 |
| R13 | E2有限真实provider/负例已足以直接派测 | MISSING | 未绑定provider类型/来源版本、故障可控性、预期错误/终态/资源证据；未知长度/提前EOF决定尚未选定，不能先写死验收。见R1-R03 |
| R14 | E3宿主JNI故障边界可仅凭风险记录关闭 | MISSING | 风险识别有据，但尚无危险调用→故障触发→宿主/他槽后果→回收证明的最小可证计划。不能以“系统接口/输入有界”直接放行。见R1-R04 |
| R15 | 模型代码/二进制/权重/训练/分发分层 | SUPPORTED | 固定文本与LFS指针未当实权重；空模板未当标签；没有上游目录许可等同全权利的断言。本轮仅核既有证据，不给新法律保证 |
| R16 | 45素材可技术使用，但不自动成为跟踪质量/发行集 | SUPPORTED | 原授权是本地只读技术测试；历史inventory中的UNRECOGNIZED包含SRT，不能判成9坏视频。没有新用途权利、有效全格式或跟踪质量结论 |
| R17 | 用户协助最小化与团队责任 | SUPPORTED | 设备窗口待通知、团队先盘点具体场景/用途缺口；不让用户补上游全部训练授权或承包1000帧标注，不询问NAS凭据，不重复找不存在按钮 |
| R18 | §29十二项、已定命名和Android先行 | SUPPORTED | 12项保留；com.videokit等已定事项按PROJECT_DECISIONS，不沿旧草稿重问；Apple/Windows只分析、后续M9。artifact兼容/质量阈值未被假装已定 |
| R19 | 独立AAR/Fake/Flutter边界仍为待验 | SUPPORTED | 原文§26.1、26.7和§31.9/10要求Fake/真实同套及可移除AAR；R1未把Debug目录、legacy签名、文档/图当这类实证，也没有引Browser业务 |

## 集中问题与可执行补充

### R1-R01　MISSING｜P1设计封口前提：聚合租约的身份和最终释放边界

来源：[矩阵A05](D:/CodexProjects/VideoKit/docs/coder/D1_R1_REQUIREMENT_GATE_MATRIX_V1.0.md:72)、[E2](D:/CodexProjects/VideoKit/docs/coder/D1_R1_ARCHITECTURE_ADMISSION_REVIEW_V1.0.md:88)、原文§14.4/26.7、[集成设计租约流程](D:/CodexProjects/VideoKit/docs/LOCALVIDEOBROWSER_INTEGRATION_V1.0.md:11)。将宿主作为物理源租约权威是有依据的；问题不在归属，而是缺少可裁定的最小语义表。

可核反例：两个不同mediaToken实际指向同一fileInstance/源版本；一个播放句柄关闭，另一个编辑/跟踪任务尚在途。再考虑管线当前句柄已关闭但producer仍可打开后续快照：只数已打开句柄为0，仍可能过早允许移动。冻结RealFramePipeline特意等producer完成，证明这个差别不是理论名称争议。

建议负责人在E2前决定以下字段语义，不要求本轮实现API：宿主如何把opaque token归并为同一源租约/版本；consumerId、bindingGeneration与整个任务预留的生命周期；何时停止接纳新消费者；何种实际open/read/close/callback归零后才发会话SourceReleased，以及宿主何时认定全源可移动；通知丢失/迟到如何按版本查询，源更换后旧Provider不得自动复开。SDK不接收Browser数据库/真实路径作为解决办法。

最低可验证反例需包含“不同token同物理源＋一个消费者晚open”和“聚合归零后移动/新版本，再到达旧open”。回调/查询都不能误报当前版本可移动。未决定这些之前，不冻结完整SourceReleased/资源报告契约；这不否定已有单任务Source账本。

### R1-R02　MISSING｜P1设计封口前提：Sink能力与验证/恢复标识尚未成表

来源：[矩阵A07–A09](D:/CodexProjects/VideoKit/docs/coder/D1_R1_REQUIREMENT_GATE_MATRIX_V1.0.md:74)、原文§17.2/17.3、[SinkCoordinator.Host](D:/CodexProjects/VideoKit/docs/coder/d1c14/src/com/videokit/spike/c14/SinkCoordinator.java:11)、[PipelineOutputSink.validationSource](D:/CodexProjects/VideoKit/docs/coder/d1c14/android/com/videokit/spike/c14/PipelineOutputSink.java:46)。内部query确实存在，READY_UNKNOWN确实同ID reconcile；但产品public Sink三方法没有这份协议，两个具体本地Sink不证明任意顺序/NAS/FD能力。

建议补一页能力/所有权/状态表：sequential、seek/randomWrite、offset/length、flush/close含义与是否承诺持久性；FD传递是借用、复制还是转移、谁关闭；独立只读验证lease由谁创建和撤销、何时允许读、不可读时如何稳定失败；不兼容能力在有写副作用前如何反馈，禁止暗建未授权暂存。stream.close、FD dup关闭与fsync不能合并为单一布尔“已安全”。

另需把exportId、openTemporary返回handleId、owner/attempt epoch、plan/source版本与query的幂等键对应起来。固定本地FencedTask的epoch拒旧机制可作证据，不能未经映射直接当公共跨宿主协议。最小对照包括：READY持久化后丢回复仍同token；旧owner的ready与新owner abort交错只有一个合法终态；writer/验证lease未归还时不READY；不支持验证读取时不能以“写成功”放行。具体方法名/公开错误码仍由负责人裁定。

### R1-R03　MISSING｜P1实验准备项：E2需绑定真实provider和可判定结果

R1正确承认当前本地文件/逻辑大offset不是SMB实证。现行源句柄只有nullable length/readAt/closeAsync，没有产品seekability声明；已知长度的提前EOF也没有所建议的SOURCE_CHANGED公开选择。因此“一个真实provider覆盖”还不能直接替代一份可执行计划。

建议在正式派E2前列出实际授权provider类型、固定输入/版本/只读范围、哪些延迟/失败可真实控制、哪些只是包装注入，以及所选稳定结果。以下为有限候选，不是本轮新用例执行或自行降低门槛：

| 候选 | 应决定/保留的判据 |
| --- | --- |
| 双消费者和未来open | 采用R1-R01的版本/预留模型；一方关闭不等全源可移动 |
| 迟到open与取消中的read | 取消响应和实际回收分开；晚句柄必须close，PENDING不能SourceReleased或复用许可 |
| close失败/恢复 | 明确最大尝试与非重叠；原失败和持有引用保留，成功只能据实际完成 |
| 未知长度、空源、提前EOF/0进展 | 先决定三类语义和错误；不可把未知当空源、短读当变化或提前EOF静默当完整内容 |
| 实际2GiB边界小块对照 | 由真实ReadHandle在边界前后读固定小块，与授权宿主同一源版本对照；不让仅MP4/AVI CPU后端偷解MKV；不称NAS完整播放 |
| 顺序/seek/FD Sink与验证读取 | 使用R1-R02决定的能力表，明确写前拒绝、只读验证lease及零/未知空间反馈 |
| 未知READY/abort/恢复交错 | 固定同一幂等键与owner epoch；不新开输出，任何返回未知保留账本 |
| 源撤销/权限变化与旧代迟到 | 不凭路径重连；旧代不能覆盖新版本状态或触发物理事务 |

这只补足D1关键接口判据，不要求先完成真实NAS产品、全部格式或M0实现。provider无法控制某故障时应明确NOT_RUN/注入范围，不用本机fake补真实provider PASS。

### R1-R04　MISSING｜P1路线准入前提：E3需以机制证明宿主JNI风险已处置

来源：[矩阵P02](D:/CodexProjects/VideoKit/docs/coder/D1_R1_REQUIREMENT_GATE_MATRIX_V1.0.md:26)、[E3](D:/CodexProjects/VideoKit/docs/coder/D1_R1_ARCHITECTURE_ADMISSION_REVIEW_V1.0.md:89)、原文§27。R1已准确标出MediaCodecList/configure/MediaCodec、旧验证、图片/字幕、显示/PCM等宿主风险；这条识别结论SUPPORTED。缺的是下一有限实验要如何产生足以关闭“会话故障不拖垮宿主/他槽”的证据，而不只是成功截图/听音加一张风险表。

建议负责人先确定当前信任/故障模型和危险调用清单，每项列进程/UID、输入权威、资源owner、可控触发点、观察者和退出标准。普通Java异常、worker退出、native故障、OOM/系统压力应分开；不能拿异常捕获或CPU worker原raw11证明宿主MediaCodec JNI安全。验证至少关联实际调用阶段、宿主与另一真实任务的存活/结果、有限取消响应及实际Source/Surface/AudioTrack/codec/FD回收；未证回收保留PENDING。

如果仍存在按当前机制无法隔离的宿主致命调用，应继续BLOCKED并给负责人可审替代，不能以“公开API、系统服务、受控小像素”或泛化风险接受关闭原P0。若提出同APK不同进程/UID形态变动，须先审当前单APK/权限约束；本报告不批准该变动，不要求在ordinary isolated重复已知不可用codec/GPU探针，也不规定不可实现的“抵抗系统强杀/失电绝对存活”。

### R1-R05　CONTRADICTED｜P2引用修订：W14链接不是所述12:38快照

矩阵:18明确标12:38:18，却链接当前 [batch-status.json](D:/CodexProjects/VideoKit/docs/tester/D1_C14_EVIDENCE/batch-status.json)，该文件已为12:41:14的ENVIRONMENT_HOLD_AWAIT_COORDINATOR。真正12:38:18的WAITING快照保存于 [batch-status-20261016T123818.json](D:/CodexProjects/VideoKit/docs/tester/D1_C14_EVIDENCE/batch-status-20261016T123818.json)。两文件本轮均已复制留证，差异可复现。

建议将引用改为固定快照并记录其hash，或引用 [C14环境中间报告](D:/CodexProjects/VideoKit/docs/tester/D1_C14_ENVIRONMENT_STATUS_V1.0.md)和当前状态各自时间。手机73环境阻断、平板0次instrumentation、未更新及无本轮在途的大意仍成立；这不是伪造设备结果，也不是C14功能失败。无需为修此引用重新连设备或重建候选。

## 原始P0、附加门槛与阶段的独立意见

原文§26–31和11条§27发布阻断均保持，包括输入源安全、输出/Sink/宿主验证、凭据/公共API、宿主/他槽故障后果、音频与资源降级、跟踪丢失不得宣称完整保护、失败不成功、ANR/OOM/泄漏/取消、产品许可、Release敏感/压力入口、独立AAR/宿主回退。R1的P01–P11是组级来源表，不能当逐子项已完成的验收矩阵；后续M0/TestKit和阶段测试仍需requirement→case→证据，尤其PlayHobby作用域、HostAction/controlsVisible及Release内容等不能因组级引用而漏测。

§29十二项可由负责人分层审定：内部命名/Flutter/Android先行已决；artifact/版本兼容、模块依赖、精确后端/许可、模型/最低设备、输出预设、remux、质量/性能/热、UI组合、Sink能力、schema/恢复、overlay与池算法仍各有指定缺口。R1没有撤销既有内部命名或将旧跨平台时点作为Android M0额外前置。E1/E2/E3/E4的先后与离线准备可以分开，但核心接口或合法路线不可行未处置，不能通过后移到M7/M8来宣布D1完成。

App精确信号是有来源且仍生效的追加门槛，不是原文逐字要求的唯一故障安全证明。负责人若决定拆分可观测性与功能隔离，需另立书面版本说明适用范围/新旧用例映射/所需证据，历史C13系统0 FAIL、trace/ordinary OPEN和已证资源事实保留；没有新平台或采集条件时不再重复同条件注入。本报告不选定或批准任何门槛变更，也不将方案建议追认为C14 PASS。

## 开源、权重与素材用途的独立意见

本轮核查的是既有记录，不做新法律保证：Media3已锁定集成与平台接口候选、受限FFmpeg本地Debug二进制/完整对应源/配置/NOTICE/SBOM、实际权重、训练来源、素材内部技术用途、产品分发/专利义务必须分别记账。目录许可与LFS指针不是实际权重hash验真或再分发准入；标签frames=[]不能产生质量结论。R1对此区分有据。

45素材已有本地只读技术授权，不能因此强索无关的全套商用发行权才继续既有测试；也不能把此授权自动扩大成人脸场景/人工标注用途或产品媒体外发。团队应先完成场景/用途/证据盘点，只把实际新增缺口合并给用户。上游权重/训练来源审查和标签组织应由团队/负责人承担，未准入不下载替代模型或伪造人物/质量证明。

E4可以书面决定分层有限筛查，但当前十类clip/1000实际PTS标签的计划没有被本报告缩减或宣告完成；M5/M6自动跟踪与真实保护质量P0不因手动回退删除。没有必要现在重复要求连接设备、找启用按钮、提供NAS凭据、付费或替上游补全部授权。

## 建议处理顺序与结束状态

1. 负责人先修正R1-R05引用，确认本材料的历史时点；不动C14和旧报告。
2. 将R1-R01/R02补成最小语义/能力/所有权决策表，明确R1-R03真实provider及有限case判据；尚未批准的字段/码保持候选，不先实施M0。
3. E3正式交接前补R1-R04调用/故障/观察/回收矩阵；若机制不满足P0，继续阻断并提出替代，而不是只记风险后准入。
4. C14维持设备等待；只有后续可用环境通知及负责人正式安排后继续73项，另2项仍NOT_RUN。E4可先整理现有来源/场景/用途缺口，不自行下载/测试模型。

上述为评审建议，没有自行派任务、批准设计、要求用户立刻操作或重启测试。R1独立评审已完成；所有本轮读取/比对命令已结束，没有设备/Gradle/功能执行在途。C14无本轮新增操作，环境等待与原计划不变。通过本报告和任务完成事件交付负责人，不重试跨窗口通知。**D1未通过，M0未启动。**
