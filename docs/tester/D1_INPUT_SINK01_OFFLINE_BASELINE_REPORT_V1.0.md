# D1_INPUT_SINK01 阶段A离线基线报告 V1.0

2026-10-20。依据D1_INPUT_SINK01_TESTER_REQUIREMENTS及设备占用时离线推进规则。

**结论：BASELINE_COMPLETE_WITH_ADAPTATION_GAPS。** 已冻结输入桥/租约与输出基础组件的独立边界检查完成；复现2项需新适配承接的差距，另列容量与实际框架集成缺口。不是新候选验收，也不撤销旧RENDER02/E11有限PASS。新候选浮动目录未读取，待完整freeze正式派发阶段B。

本轮0设备/ADB/5037/占用查询，0 Gradle/Android/native构建，未操作共享可变缓存。仅已有JDK在tester新目录编译有限纯Java原组件和独立检查；没有下载依赖、读取真实媒体/模型或改变旧scope/账本/UNKNOWN。D1未通过，M0未启动。

## 1. 来源、样本与真实验证范围

先记录17个准确来源pins，再编译14个原生产纯Java来源；3个Android/事务来源仅静态审证。来源为冻结RENDER02的AsyncReadBridge、LeaseRegistry、HostFixtures、SourceAdmission及E13原归还门，以及冻结E13F的BoundedOutputChannel、PipelineRules、CpuFrameRules、E4Owned、E4Protocol、E4Broker。E4CodecSink、E4Session和E4FencedTask只读源码。每项准确SHA/长度/来源见source-pins-before-tests.json；编译输入及tester检查源码另有tested-source-pins.json。

来源逐项与原RENDER02 seal或E13F seal匹配，结束后17项再次不变。另核E11 seal内E4CodecSink和BoundedOutputChannel，与E13F对应文件逐字节相同，见e11-e13f-sink-provenance.json。没有拿新开发目录或变化中的实现当基线。

样本为固定整数函数 `value(p)=((p*1664525+0x20261020)>>>9)&255`，seed539365408；短读窗口、64KiB稀疏窗口参考SHA、32字节partial-write输入SHA和实际4字节磁盘fixture SHA均列generated-fixture-identities.json。稀疏逻辑偏移覆盖2GiB+123、3GiB+7，不分配大文件；64KiB窗口参考hash明确标为预期，未冒称另存了完整返回buffer hash。

最大单个受控分配2097153 B，小于8MiB样本上限；实际落盘样本4 B，输出远低于16MiB。没有把本批候选预算当产品阈值，也没有真实容器/编码文件或平台峰值结论。

## 2. 已实际执行的独立边界

所有JVM检查进程实际正常返回。原provider异步阶段、调用线程和原bridge executor线程按实际完成/join审证；没有用Future完成或executor TERMINATED单独代替原线程退出。

| 检查 | 实际结果 |
|---|---|
| 已知长度短读/有限range | offset5/request7，返回3+3+1，精确位置5/8/11，字节一致、边界EOF |
| 未知长度/EOF | open返回-1，不虚构长度；3+2后-1 |
| 大offset/单块 | 2GiB+123、3GiB+7保留long；65537请求只准65536，未截成32位 |
| long溢出 | UNKNOWN长度源在Long.MAX_VALUE返回1时INVALID_RANGE，调用者buffer不被私有返回覆盖 |
| 非法宿主read结果 | 0、-2、超过requested count均INVALID_READ_RESULT |
| 错误映射 | 受控AccessDenied只公开SOURCE_PERMISSION_DENIED，不公开原私有名称 |
| 同bridge并发 | 原read未返时第二read为READ_IN_FLIGHT，未新增provider调用 |
| 取消/迟到 | caller因取消醒来，但registry仍未released；迟到写仅改原private buffer，不覆盖调用者；read完成仍不能替代handle close |
| 双consumer归还 | 第一handle close不能释放整源；两个真实async阶段、两handle和原线程全部返回才释放 |
| input close失败/reopen | callback明确失败后保持FAILED/closeFailed及未释放，无自动retry；同bridge重复open/关闭后reopen拒绝 |
| 已观察失败后的显式恢复 | 仅测试原API允许的同handle owner retry；准确第二callback完成及原线程join后才释放，不把hung/UNKNOWN变成可重试 |
| 输出预算 | 老组件2MiB+1在write前拒绝，底层0字节；没有将旧限额自动扩至16MiB |
| 原close异常 | E4Owned保留同原对象/UNKNOWN；第二close在外层拒绝，实际原closer只调用1次 |
| 实际文件reopen/验证拒绝 | 本地生成4B文件真实打开；受控验证回调拒绝后原stream仅关闭1次，firstFailure保留 |
| READY前置 | 缺原帧/close/合法验证状态时remoteOutputClosed/validatedOutput拒绝，不能仅填“6帧/true”求READY |

输入未知长度seek为CPU_SEEK_UNSUPPORTED，同一bridge只准open一次。该边界符合旧CPU桥角色；新Media3 DataSource必须明确close/open/position映射，不能在尚未归还的原bridge上复活或重置generation。

## 3. 确认差距及最小承接要求

### GAP-A01：每consumer门不能替代每源读在途门

**OBSERVED；阶段B准入重点。** 两个AsyncReadBridge共享同一个Provider、同一LeaseRegistry generation，各自一个handle；两次真实readAt异步阶段同时未返，受控source pending峰值为2。第一关闭仍不能释放，最终原归还正确。

旧桥的READ_IN_FLIGHT是每bridge/consumer的保护；本批新要求是每源1次在途。不能把“各consumer都只有1”登记成“整源只有1”。新薄适配应按原sourceVersion/epoch/实际源身份共享有限准入，排队≤4、取消迟到和退租仍绑定原handle，不另外自造资源平台。阶段B应以同一宿主fixture重放，要求新每源峰值≤1，并分别验证不同源并发与总源≤2。

这不是对旧呈现场景的追溯产品FAIL：旧场景原本就是两个有限consumer，本阶段增加的是新的全源契约要求。尚未读取新实现，不能说coder新候选已存在该缺陷。

### GAP-A02：保守输出扣减不是实际写入量或事务完成

**OBSERVED。** 原BoundedOutputChannel把32B ByteBuffer提前取出并预算扣32，底层受控OutputStream只写7B即抛错。实际观察：底层已知prefix7、channel.bytes=32、buffer.position=32、channel仍open。

该计数保守占用预算，对硬上限有用；不能叫“实际已写32B”。真实OutputStream异常往往没有partial进度回执，除了已证prefix外应为UNKNOWN，保留该次预算，不能用文件大小/attempted count冒精确总量，也不能自动回退buffer重发而重复已写部分。基础通道没有事务失败sticky门；外层E4Owned/现有E4CodecSink保管规则才承担失败停止。

新OutputSink薄适配必须分列attempt/reservation、已知完成及UNKNOWN，保存首错误/实际owner，失败后不准READY/COMMIT或不明重试。close/flush/reopen/验证必须逐原调用完成；不得把旧bytes()直接作为新宿主已提交或持久化字节数。本用例可在阶段B直接复用受控partial流，不能冒充平台FD真实partial故障已测。

### 其他需要阶段B核准的差异

- 基线Runtime队列是16，LeaseRegistry还有其原consumer/generation上限；它们不直接证明本批queue≤4及全局同时源≤2。应由新候选准确有限准入补齐，不修改旧预算或把旧高上限称新契约通过。
- 冻结桥不是现成Media3 DataSource接口实现；未知长度、DataSpec.position/length、open/close复用、sourceVersion/epoch、错误及capability映射仍须实际接口验证。
- 基线BoundedOutputChannel不是完整授权OutputSink事务；顺序写能力、临时对象/FD授予、seek能力协商、close/reopen和宿主提交不能从WritableByteChannel类型自动推导。

以上集中交负责人用于新候选审查，不逐项打断coder，也不要求重写成熟输入/codec/容器。

## 4. 平台与事务层的静态结论/未测

冻结E4CodecSink实际薄接Media3 FragmentedMp4Muxer，只接被授予FD，不自行开路径；检查空的可写regular file、lease区别及append限制；finish先muxer finalize再fsync，close异常sticky保留原对象，activeCalls未返不称released。其内层通道也预扣write attempt，不能扩大bytes语义。

冻结E4Session实际先等远端sink/encoder/frames/lease与native调用归还，再同原输出digest/大小和独立CPU reopen验证；检查完整EOF、source关闭、真实worker death/slot release、UID/PID/内容hash及timeline等，之后才E4FencedTask.ready、关闭owner。这里是源代码审证，未本机执行AndroidFD/codec/CPU容器路径。

E4Broker/E4FencedTask的READY是已验证临时输出可交付的有限状态，不是宿主业务COMMIT。基线enum/API没有完成业务发布的COMMIT；未伪造true或平台替身完成容器来通过READY。新候选应继续分层：资源真实归还、reopen校验、临时输出READY、宿主业务接受/COMMIT各自证据，校验或reopen失败不发布成功token。

| 尚未实际执行 | 本阶段判定 |
|---|---|
| 新Media3 DataSource真实接口/新依赖身份 | NOT_RUN_PHASE_B，未读取新浮动目录或缓存 |
| Android FD/Media3 muxer finalize、fsync/真实容器重新打开失败 | NOT_RUN_PLATFORM；仅静态来源审证 |
| 实际编解码后输出内容/timeline/可播放性 | NOT_RUN，4B样本不是媒体，受控validator拒绝不是容器校验 |
| 真实平台partial write/永久close未知/worker卡死 | NOT_RUN；受控无外部资源stream故障不扩大为平台永久UNKNOWN通过 |
| 完整NAS/网络/凭据/持续播放/宿主业务COMMIT | NOT_RUN_NOT_IMPLEMENTED_BY_BASELINE |

本轮E4Owned UNKNOWN案例用有界受控stream和确定缺失文件模拟失败状态，没有未归还的真实外部FD或SDK owner；不据此清理任何旧UNKNOWN。实际生成文件的原stream已关闭，输入read/close回调和executor均实际返回。

## 5. 阶段B可复用回归清单

reusable-regression-cases.json包含19项：I01–I12输入/range/EOF/身份与取消归还，S01–S06输出partial/预算/close/reopen/READY-COMMIT，F01真实框架接口与依赖。每项标阶段A已测范围、差距或NOT_RUN及阶段B目标，不把19项都登记PASS。

BaselineCheck.java及CloseBoundaryCheck.java为独立宿主fixture和原组件断言，可将同一受控Provider/partial流/late回调用于新冻结适配；实际Media3接口接线断言仍须在阶段B补齐，不能用同名假接口替代。最大样本8MiB、块64KiB、每源1/queue4、总源2、输出16MiB按新批需求核，不反向冻结为公共产品阈值。

阶段B收到完整freeze后再核实际DataSource/Sink实现、准确Media3 1.9.3依赖/传递闭包/metadata及许可、产物身份、源码到构建/自测证据，集中运行这些回归和差异检查。若必要artifact来源不足，对应真实集成BLOCKED，但继续不受影响的有限验证；不升级版本或关闭metadata校验求绿。

## 6. 证据与移交

全部新代码/类/数据/报告在 `D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK01_PHASE_A_EVIDENCE`，与coder开发/构建目录分开。主要文件：source-pins-before-tests.json、tested-source-pins.json、e11-e13f-sink-provenance.json、generated-fixture-identities.json、两检查源码、run.stdout/原进程回执、close-boundary回执、baseline-result.json、reusable-regression-cases.json。

本报告主动集中交负责人，不逐缺陷打断coder。旧冻结候选/已停止设备scope、实际消费/UNKNOWN均保持原样；本轮不等待或重新核查设备，阶段B仍等完整冻结及正式交测。原有限实机PASS、历史FAIL和其他NOT_RUN分别保留，不自动D1退出/M0。
