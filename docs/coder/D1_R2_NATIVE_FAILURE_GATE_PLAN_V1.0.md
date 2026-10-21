# D1 R2 原生故障功能门禁与原因可观测性方案 V1.0

2026-10-16。回应R1-R04。[负责人决定§2/5](D:/CodexProjects/VideoKit/docs/D1_R1_COORDINATOR_DECISIONS_V1.0.md)已采纳分栏原则；**本方案的新名称/判据须独立评审及正式派发后才用于新实验**。R2没有注入故障、实现进程/权限变更、创建组件或启动设备。原文§27不变，C13系统0严格FAIL、trace/ordinary UNKNOWN及C14两项NOT_RUN均保持。

依据：[原文§16.2/21/27](D:/CodexProjects/VideoKit/docs/VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)、[系统设计§5/6](D:/CodexProjects/VideoKit/docs/SYSTEM_ARCHITECTURE_V1.0.md)、[C11严格信号要求3–4](D:/CodexProjects/VideoKit/docs/milestones/D1_C11_CODER_REQUIREMENTS_V1.0.md)、[C13报告](D:/CodexProjects/VideoKit/docs/tester/D1_C13_TEST_REPORT_V1.0.md:126)、[R1评审R04](D:/CodexProjects/VideoKit/docs/tester/D1_R1_REVIEW_REPORT_V1.0.md)。已知ordinary isolated直接MediaCodec/GPU不可用不重复同条件探针；companion只保留历史协议证据，不产品化。

## 1. 威胁/故障模型与观察权威

本轮讨论输入触发的单会话故障、可恢复平台API异常、受控worker原生故障、任务资源耗尽及恢复；不承诺抵抗系统失电、强杀整个宿主或全系统崩溃。系统/vendor服务存在、调用公开API、像素有界均不能自动证明宿主JNI致命故障被隔离。被攻陷worker恶意伪造协议/持FD不合作与普通进程故障是不同模型：校验/限额/身份控制能约束数据面，但合作式close/flock不是抵御任意RCE的内核撤权；这类缺证必须披露，不宣称绝对安全。

三个观察者分工：

- **App资源权威**：固定task/epoch/进程代次/Binder/内核PID与UID、Source/帧/FD/codec/Surface/AudioTrack/回调账本、原始系统reason/status及trace状态。App未知原因原样UNKNOWN，不从测试输入/ARMED/raw补值。
- **独立测试观察者**：单独测试进程/受批准的tester只读系统证据，匹配原PID/UID/进程实例/时间/任务和具体阶段，确认目标实际故障、宿主实例未替换、另一任务真正完成。raw可以独立见证native触发，不能写回产品API。
- **输出/源见证者**：授权宿主检查源版本/只读性、独立验证lease和持久query，核部分输出未READY、合法终态唯一。末尾进程空或instrumentation结束不能代替期限内资源证明。

宿主存活须同一进程实例标识（PID＋启动身份/单调心跳与任务域）贯穿故障前后；自动重启新PID不是存活。另一任务必须在目标故障前已实际处理真实源，故障后完成自己的帧/样本或结果，不拿空闲线程/假心跳代替。共享预算期望是目标许可归还、另一任务应有引用仍在，不能一律要求global=0把他槽误释放。

## 2. 逐调用危险边界矩阵

下表“实际”指冻结代码所在位置，不表示C14运行过。所有未来触发仅针对本应用受控任务，须先获整批实验派发；R2不运行任何触发。

| ID/调用与当前来源 | 进程/UID、输入权威与资源owner | 可控触发与独立观察 | 归还证明、当前缺证与具体出口 |
|---|---|---|---|
| J01 Media3 DefaultMediaSourceFactory/Extractor、AssetLoader；[MediaEngine](D:/CodexProjects/VideoKit/docs/coder/d1c14/android/com/videokit/spike/c14/MediaEngine.java) | 旧Debug在宿主普通UID；字节来自授权Provider但容器不可信；session/loader持parser/decoder/source | 错格式/坏头/受限读取/取消可做Java和资源失败对照；观察实际prepare/sniff/loader阶段、宿主实例及第二真实任务 | parser/loader退出、read/close/callback实际归零。不能用CPU worker crash证明宿主Extractor/平台decoder安全；该旧宿主路线的致命故障边界未闭合，需后端/进程决定 |
| J02 NativeCpu.decode/decodePipelineFrame→FFmpeg demux/decode/sws；[NativeCpu](D:/CodexProjects/VideoKit/docs/coder/d1c14/android/com/videokit/spike/c14/NativeCpu.java)、[CPU JNI源](D:/CodexProjects/VideoKit/docs/coder/d1c14/native/cpu.c) | 同APK ordinary isolated UID；broker只授字节，worker持FFmpeg/context/frame，宿主持Provider | 合法真实帧后自进程native fault（历史C13已有），或以后有理由改动的确切阶段故障；独立raw/退出与原任务身份、实际death/第二任务结果相互核对 | child实际死亡只归还其地址空间；宿主read/open/close与在途另证。C12/C13限定证据可引用，不重跑无变化条件；不将故意自crash称已发现FFmpeg漏洞 |
| J03 MediaCodecList/CodecCapabilities查询；[EncoderCapabilities](D:/CodexProjects/VideoKit/docs/coder/d1c14/android/com/videokit/spike/c14/EncoderCapabilities.java) | JNI及Java调用在宿主，系统/vendor可能参与；系统metadata也限界；encoder owner持pending calls | C14记录枚举/能力/格式支持，异常或metadata超限对照；独立观察进入/返回、宿主和他任务 | calls实际返回；返回前超时仍PENDING。小metadata不能防framework内部异常分配/native abort；宿主fatal containment当前无机制证明，**BLOCKED_HOST_JNI_MECHANISM** |
| J04 create/configure/start、dequeue/queue、EOS、stop/release；[PipelineEncoder](D:/CodexProjects/VideoKit/docs/coder/d1c14/android/com/videokit/spike/c14/PipelineEncoder.java) | 宿主普通UID JNI，系统/vendor codec执行；只接受限界裸RGBA/YUV；单encoder owner | 先真实configure/start；原CodecException为Java可恢复事实，configure-first/all注入另列。实际native fault需独立见证并有隔离机制，不能拿抛IOException充当native | actual release/creating=false/owner calls0后下一；未知保持许可与引用。C13两次仅证明configure异常后关闭，C14实机待验；宿主同地址空间致命调用仍BLOCKED |
| J05 getInputImage/Plane buffer/Image.close；同PipelineEncoder | 宿主Image JNI/内存；裸数据由协议校验，Plane布局来自平台；Image/转换缓冲owner唯一 | 真实Image输入路径，旋转/stride/limit异常及取消/在途租约对照；观察实际选中色格式，不因声明Flexible算执行 | Image实际close、codec和转换引用清空、原帧lease归还。缓冲边界检查不是native fatal containment；路径未进入或无可控native见证则对应项NOT_RUN/BLOCKED |
| J06 FragmentedMp4Muxer→FileOutputStream/Os.fsync、AndroidLease.tryLock/unlock | muxer Java与文件/lease JNI在宿主；写目标宿主授权，owner持全部stream/dup/lock | 实际writer后的write/flush/close故障和取消，独立读临时目标与journal/query；普通IO异常与JNI crash分列 | 每份FD/stream/sync/lease实际close，未证不删/不READY；可回收IO失败可有限验证，宿主lease JNI fatal不能靠锁机制自证安全，结构性缺证仍BLOCKED |
| J07 新NativeCpu.verifyOutput、旧AndroidOutputValidator(MediaExtractor/MediaCodec) | 新视频6帧验证在isolated，旧双轨验证宿主；压缩输出不无条件可信，validator持只读lease | 实际编码输出后截断自己的临时目标，观察独立验证真正解码EOF/拒绝；validator native死亡另列，不用“格式可打开”代替 | validator death/read/close及所有验证lease排空；无合法receipt不READY。新路径C14未运行，旧双轨不能冒充已隔离；多轨隔离方案需后续决定 |
| J08 HostFixtures.srt解码、Media3字幕解析/绘制 | 旧路径宿主Java/字符与字体平台接口；字幕不可信，授权内容与编码转换均有限界 | 已授权SRT错编码/大小/取消/切代与实际字幕显示对照；独立观察字体渲染阶段/宿主、真实他任务 | 读取、parser/render任务和相关Surface/缓冲归还；无新的隔离机制/致命故障见证，不能从“字幕正常”关闭native渲染风险 |
| J09 DataSourceBitmapLoader/平台Bitmap、PlatformFaceProbe.FaceDetector | 现有图片加载/FaceDetector对照在宿主；原压缩图像与系统native模型调用；loader/bitmap/detector owner | 限定合法图/坏图/尺寸拒绝和取消；FaceDetector数量只作检测对照 | bitmap/native refs与源真实归还；无全图片产品/模型权利/效果证据。压缩图片native解析若在宿主不可只记录风险就准入，需受控解码路线决定 |
| J10 跟踪/遮罩/GL shader | 自有模板有对照，正式高风险worker/图形owner尚未实现；raw/轨迹/revision授权来自工程 | 未来合法候选真实ROI、LOST/修正、取消与旧revision；native/GL fault须按实际选定进程验证 | 未实现位置不能写成已隔离。模型/GL路径及资源归还机制缺证，保持BLOCKED，先选择合法组件/进程再派有限实验 |
| J11 Surface/Texture、AudioTrack/音频焦点、Flutter显示目标 | 新六帧管线未创建Surface/AudioTrack；旧播放器宿主JNI和系统服务；正式Flutter bridge未实现 | 以后在已准入裸数据路径做真实显示/声音，销毁generation、取消、音频epoch竞争及平台错误；观察截图/声音＋宿主/他任务 | Surface/producer/texture/Image/PCM队列/AudioTrack stop-release实际确认；ByteBuffer接收无效。无合法PCM解码路径先BLOCKED，不能扩FFmpeg音频白名单；native/driver fault不能只凭成功播放判隔离 |

**结构性结论**：J03–J06等宿主致命调用与UI/会话同地址空间，当前没有能拦住宿主native crash的机制；Java catch、四次有限尝试或PENDING账本只能控制可返回错误/回收，不是进程故障屏障。现阶段不得把它们标成完整P0已关闭。

可审替代为：隔离UID继续承担不可信解析，公开codec执行由同APK独立受控执行进程持有，宿主只做有限控制/授权/显示接入。若该执行进程同宿主UID，只增加故障边界，不能称权限隔离；需要负责人明确审当前C04/单APK约束、资料权限、显示对象、恢复/预算和manifest影响。另一选择是证明已准入平台路径的实际调用边界及可观察故障处置，但不能将未知当“系统天然安全”。**R2不采纳或实现任何替代**；未有可满足机制就保持BLOCKED，不循环注入无变化宿主。

## 3. 故障种类与新功能用例候选

| 候选ID/种类 | 前置/触发和真正证明的内容 | 成功/失败出口（均待评审、未运行） |
|---|---|---|
| F01 worker-death containment | 已有真实源/阶段且另一任务实际在途；匹配原代Binder death/OS进程死亡，原因可UNKNOWN | 同宿主实例继续、另一任务完成、原任务无新接纳/错误READY、各资源实际归还才能该限定功能PASS。仅发取消/超时或尚有引用则PENDING，不补精确信号 |
| F02 worker-native-fault containment | F01前置＋独立见证原进程实际native fault（App可靠原始字段或独立测试raw） | 除F01后果证据还须触发真实命中。缺native见证只能说明F01/death，F02为未证；独立raw不改变App cause UNKNOWN，也不表示真实decoder漏洞已复现 |
| F03 Java/API错误与有限回退 | 真实枚举/配置/输入/输出/MUX已到达，再记录真实异常或明确标注的wrapper故障 | 正确阶段/首因、最多4尝试且实际关闭后下一、另一任务/宿主存活及清理；可关闭此可恢复错误机制，不能借它关闭宿主native fault |
| F04 任务配额耗尽/受控分配失败 | 只在获派自身worker预算内触发真实allocator拒绝/ENOMEM，禁止全系统无界压力 | 原任务稳定失败、其他任务继续、原资源实际归还；64MiB allocator配额/192MiB额外VMS不是全进程RSS或真实系统OOM证明 |
| F05 实际native OOM/被内存管理终止 | 需另行批准且可辨具体故障/进程原因、原任务/他槽/宿主与内存边界 | OOM类若未实际发生则NOT_RUN，不用SIGSEGV/配额拒绝冒充；发生宿主受害/误释放他槽为FAIL，无法区分全局压力保持UNKNOWN/BLOCKED |
| F06 全系统压力/OEM策略 | 不是可从单任务quota推导的事件；不在当前计划制造全局压力或更改安全策略 | 独立记录环境影响；不承诺所有App存活。若候选稳定诱发ANR/OOM则仍命中原文发布阻断，不能换名环境豁免 |
| F07 系统强杀宿主/进程重启 | 仅后续获派的自身测试宿主终止与持久恢复，区别“worker原生故障后宿主存活” | 不要求被强杀实例存活；要求旧写引用可核、同export唯一READY/ABORTED/UNKNOWN、源不变、无部分成功。真实失电未测则不宣称crash-durable |
| F08 宿主JNI致命故障屏障 | 必须先有被批准的执行进程/生命周期机制，关联J03–J11真正调用阶段；没有机制不先靠杀宿主作重复演示 | 未有隔离机制时状态BLOCKED_HOST_JNI_MECHANISM；若获派新机制，一次受控实际native fault后同宿主/他任务及全资源条件成立才可限定通过。真实宿主死亡/误释放/假READY即FAIL |

“功能PASS”必须同时满足目标命中、同宿主实例存活（F07另论）、另一真实任务结果、源不变/无部分READY、目标资源实际归还和预算正确。取消响应及时但回收未证可单独记录响应事实，**整项不能PASS**。其他活任务的资源按预期保留，不将global清零当优点。

## 4. 精确原因的独立能力栏与新旧映射

独立观测项建议为O01原始OS记录身份匹配及非零精确信号是否可用、O02 App trace可取得/解析/身份匹配、O03 App最终cause分类是否有足够证据、O04第三方独立故障见证。原始reason/status无论值多少都另存；O01的0/UNKNOWN、O02的ABSENT/不支持和O03 UNKNOWN是能力事实，不是“精确原因成功”。不能借O04把0改为11。

| 历史用例/结果 | 新功能/能力语义映射 | 在当前C14与未来实验中如何保持 |
|---|---|---|
| cpuSelfSigsegvSignalMustBeProven，C13 App系统0严格FAIL、raw11、原代资源归还 | 原代死亡/资源/宿主后果及独立raw为限定历史支持；该单任务方法本身未覆盖“另一真实任务完成”，不足以单独满足F01/F02整项。O01严格原始11断言失败，O02 ABSENT、O03 UNKNOWN分别保留 | 旧方法仍FAIL，不更名改统计。C14仍NOT_RUN_UNCHANGED_PLATFORM_LIMIT，不把拆分直接算新PASS |
| cpuSecondSlotAndHostSurviveFirstSelfCrash，C13原OS11且他槽完成 | F01/F02的限定历史支持，O01该任务系统11；O02仍ABSENT，不推断trace或全部原因能力通过 | 保留原PASS及独立释放事实；C14仍NOT_RUN，不靠换包名再注入一次 |
| C12两方法原系统11 | 仅C12具体任务/设备/代次的历史观察 | 不覆盖C13 self FAIL，不外推平台必给signal；无新采集条件不重跑 |
| 历史ordinary codec cause UNKNOWN/trace缺失 | 其能力观察、实际death/Source/lease事实与原因不可判定分栏 | 历史FAIL/UNKNOWN保持，不将其当已证权限拒绝；不重复ordinary isolated codec/GPU同条件入口 |
| 既有legacy实际编码sample后worker native fault/第二任务 | 只支持其companion实验地址空间/协议/资源边界 | 不是单APK产品证明，也不补App内signal/trace；不扩成产品或新增crash campaign |
| C14 configure-first/all/close ACK保守扣留 | F03可恢复错误/owner操作/释放账本设计，C14实际设备未执行 | 人为IO/Java错误或实际release后扣ACK不是native crash、OOM或真实硬件release失败 |

App语义可以报告负责人允许的WORKER_DIED并保留cause UNKNOWN、原reason/status、trace状态、阶段与资源事实。若WORKER_DIED进入公开enum，它仍需API/binding版本评审；旧码兼容可保守用INTERNAL_ERROR_REDACTED＋reason=WORKER_DIED，不能把UNKNOWN编码成“权限拒绝”或“精确SIGSEGV”。任何正常UI都不接收原生异常对象/敏感路径。

## 5. 实验准入、停止与剩余决定

先由独立评审确认新旧映射、具体J调用故障模型和观测者权限，再由负责人决定是否派新机制的有限实现。C14原73项/两项NOT_RUN保持；其设备等待不因R2被重启。本机provider计划只验证IO/协议，不能给F02/F05/F08造功能通过。

未来若正式派发故障实验：每个有变更且可判定的触发最多一次；正常真实输入/另一任务前置不成立则依赖BLOCKED；保留初错和cleanup，禁止反复同条件求signal/trace。沿当前CPU2/encoder1/帧/输出/日志硬限额，不新crash handler、不提权、不杀无关进程或制造无界全局OOM。JNI卡住/引用未知停止后续分配并保留PENDING；独立observer超时不能写成已死/已释放。

负责人仍需裁定：宿主JNI的可满足执行机制、显示/PCM合法路线与资源owner、原生OOM的可控范围，以及是否在后续实验版本启用上述F/O命名。现阶段原P0未关闭、完整危险链仍有BLOCKED；R2补的是可审计划和判据，D1未通过，不进入M0。
