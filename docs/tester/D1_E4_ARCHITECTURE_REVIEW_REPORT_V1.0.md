# D1 E4 进程边界独立架构与代码审查报告 V1.0

日期：2026-10-17。角色：VideoKit tester。依据：E4正式开发/测试需求及负责人冻结交接。已全文审读四份交付文档、实际代码、manifest、APK/源码归档、本机证据及8项设备计划。

**结论：REQUEST_CHANGES，当前不建议正式派发整批设备测试。发现2项P1、1项P2，集中修复后重新冻结交审。** 包完整性PASS、本机编译及89条JVM规则证据有效，但不能替代Android codec/Binder/native故障行为验证。本轮未Gradle、ADB、连接设备、读取媒体或运行fault，没有修改候选/C14。

## 1. 冻结与有限证据

| 项目 | 独立核验 |
|---|---|
| 候选 | D1-20261017-E4 |
| freeze SHA256 | `0940855c58ada5c2ce3b23e8bd4c63803016afeb4b563127f589a043847e0227` |
| 源码ZIP SHA256 | `f35e113e563b2c9f15db530f5d780fd2f57ab73e545367e8a5baa58278cd754e` |
| 集合 | 112源/116不可变条目、ZIP精确成员/逐hash一致 |
| app APK | 10529808 B；`7368e7d9cdef6ad810014dc71f04cf22f6aefbc60c51019588f09df363bdeca9` |
| instrumentation APK | 2711421 B；`427383e302708e1a0f6003d209fabed94ac969450f9fe3bbcc3f6e680ce1b171` |
| 两APK签名证书 | `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，原签名报告一致 |
| 本机证据 | 1 MAIN＋4必要REPAIR保留，最终repair-004源码绑定；89条纯JVM，未重跑 |
| 原依赖 | C14原23 Java闭包＋7 native库字节/来源绑定；APK实际7库一致 |

已审只读verify_e4一次PASS；实体读取73,348,886 B/172次，逻辑归档读取29,438,436 B，不递归展开历史容器，不启动进程。tester自有hash/ZIP/APK成员核验亦通过，见 [独立封存审计](D:/CodexProjects/VideoKit/docs/tester/D1_E4_EVIDENCE/independent-package-audit.json)。完整性PASS不撤销下述代码缺陷。

## 2. 集中缺陷

### E4-F01 / P1：失败收尾删除原输出，累计输出预算实际按剩余存量退款

位置：[E4Session.java:165](D:/CodexProjects/VideoKit/docs/coder/d1e4/android/com/videokit/spike/e4/E4Session.java:165)、[FencedTask.java:95](D:/CodexProjects/VideoKit/docs/coder/d1e4/upstream-c14/src/com/videokit/spike/c14/FencedTask.java:95)、[Sink.open:261](D:/CodexProjects/VideoKit/docs/coder/d1e4/android/com/videokit/spike/e4/E4Session.java:261)。

非READY分支在原worker lease已清、远端已知关闭或死亡等条件满足后调用task.abort；复制的abort实际执行Files.deleteIfExists(output)。因此失败/取消的空或部分编码产物会被自动删除，无法按本批设备合同保留全部失败输出。这里不是说它会删除仍未知的活跃writer；问题在于已安全结束的失败产物也没有归档保留。

同时Sink.open只累加当前目录Files.size并预留2MiB，没有跨方法/原进程的单调累计写入或已消费输出信用。失败文件被abort删除后，该部分字节不再进入下一次准入，不能证明文档声明的“累计4MiB、不删除失败输出凑额度”。即使某次8项运行的实际输出很小，当前算法也只证明存量界，不能宣称累计界。

修复：E4独立适配中将撤销写权限/持久ABORT与保留原产物分开；失败输出应保留原身份、实际长度/hash或UNKNOWN及预算消费。明确并实现本批跨方法/必要跨host批次的累计额度；不能靠删文件或新实例退款。保留原C14冻结字节，用E4衍生适配及hash关系处理。补有限离线“写部分→失败→保留→后续准入仍消费原额度”的检查；不以真实设备fault补证代替代码修复。

### E4-F02 / P1：外层两阶段Sink不能保留构造失败时未返回的lease原owner

位置：[E4Session.java:269](D:/CodexProjects/VideoKit/docs/coder/d1e4/android/com/videokit/spike/e4/E4Session.java:269)、[FencedTask构造:41](D:/CodexProjects/VideoKit/docs/coder/d1e4/upstream-c14/src/com/videokit/spike/c14/FencedTask.java:41)、[构造失败清理:44](D:/CodexProjects/VideoKit/docs/coder/d1e4/upstream-c14/src/com/videokit/spike/c14/FencedTask.java:44)、[AndroidLease.java:15](D:/CodexProjects/VideoKit/docs/coder/d1e4/upstream-c14/android/com/videokit/spike/c14/AndroidLease.java:15)。

外层先登记Sink及opening=true，但task赋值发生在new FencedTask完全返回之后。内层先分配ownerGuard，再持久化/目录sync；若该步抛IOException且随后ownerGuard的close亦未证返回，构造直接抛出，Sink.task仍null，外层强引用只持有空Sink，不能再到达未返回构造对象中的ownerGuard/PFD。更早AndroidLease.exclusive在open后acquire失败、fd.close也异常时，同样在返回guard前失去外部可追踪的原owner。

外层opening/PENDING和encoder许可仍保留，这是保守状态；但不能据此声称实际原FD/guard也已由host强保留。该双失败路径没有可复核的实际关闭证明，也没有把未证owner交给外部账本，可能依赖不可达对象/GC收尾，违反本批UNKNOWN原对象强保留合同。不是把所有构造失败都判泄漏：正常异常且close实际成功的路径不属于此缺陷。

修复：原FD分配及guard取得前就建立外部可达holder，在构造/持久化前交接实际owner，或拆开allocate/register/initialize；所有未证close的原PFD/guard/异常保留在该holder，禁止重试或退款。不能只保留opening标志。以有限自有假close/directory-sync故障验证初始化失败＋close失败时原owner仍可达，不触发Android/native故障。E4局部衍生处理，不修改C14原冻结。

### E4-F03 / P2：取消设备用例在独立control调用真正返回前固定断言全部释放

位置：[E4Session.java:206](D:/CodexProjects/VideoKit/docs/coder/d1e4/android/com/videokit/spike/e4/E4Session.java:206)、[结果发布:171](D:/CodexProjects/VideoKit/docs/coder/d1e4/android/com/videokit/spike/e4/E4Session.java:171)、[取消用例:127](D:/CodexProjects/VideoKit/docs/coder/d1e4/app/src/androidTest/java/com/videokit/spike/e4/E4DeviceTests.java:127)。

s.cancel另派CONTROL同步CANCEL并计controlInFlight；host owner可同时完成自身CANCEL/QUERY/Source/Sink清理，ownerFinished后立即result.complete(report)。若独立control已返回或远端已排空、但该CONTROL线程尚未调度到finally扣数，report会合法为PENDING。CONTROL finally仅扣数，不重新发布结果或tryRelease；设备用例只取一次await的不可变快照，立即released(result)并断言许可0，没有再query等待原control返回。

因此存在“资源最终正确排空，但用例读到原PENDING就失败/许可暂未归还”的调度窗口。保留in-flight本身正确，不应通过提前扣数修复。用例需在同原身份、原总时限内通过query观察真正返回后的状态，或由唯一完成路径在所有已接纳control返回后发布终态；缺证仍PENDING。补有界CONTROL返回前/后屏障检查，不能靠同设备重跑求稳定。

以上均为静态可达路径分析，未运行故障或声称设备已重现。修复应集中交下一冻结包；本轮不编辑候选。

## 3. 已成立的架构与代码边界

实际manifest及冻结APK清单为同一com.videokit.app中的两个exported=false service：CpuIsolatedService是ordinary isolated，E4CodecService在:e4_codec且非isolated、与host同UID；instrumentation APK是测试工具，不是媒体companion。仅ACCESS_NETWORK_STATE，无INTERNET/companion查询权限。该normal权限仍是网络相关能力，不能说无任何网络权限。

压缩输入及输出EOF验证走原CPU isolated闭包；系统codec枚举/四提案、编码、Image/Plane及fMP4在受控service owner线程。sameUID只提供待设备验证的地址空间/崩溃边界，无权限/RCE隔离；同UID私有目录和一般能力不能由有限Binder协议撤销。host仍调用AndroidLease的flock/unlock JNI和文件/sync/Binder/运行时native，J06残余已承认，不能称host零JNI。

Binder入口核实际UID、完整task/epoch/generation/instance及原host PID一致性，帧Parcel196608B/callback16384B、ingress1；只BEGIN收Sink/lease FD，不传路径/URI/凭据。原帧六个、queue2/consumer1、encoder1、CPU2、256×144/147456B，有序PTS和alpha/布局边界明确；帧不经Flutter/Dart。

本轮未发现同步callback内反向Binder等待：host callback只保存有限metadata并ACK，不等待owner/codec；broker资源close action在锁外执行。service在原callback实际返回前保持in-flight，host后续QUERY0且无callbackUnknown才认可关闭；最终callback自身携inFlight=1不能当结束。同步调用若不返回，名义轮询窗口不是硬中断或归还证明。这是静态未发现锁环，不是Android实测无死锁。

BEGIN提前落transferAttempted，未adopt需显式rejectedGrantCloseProven；无回复或workerLeaseClear不能代替原FD归还。未知拒绝bundle/FD强留并锁住admission，已接管资源按原owner收尾。普通取消只撤销新工作，原consumer/resource/operation及未知许可保持；死亡不把原UNKNOWN资源全局归零。上述机制方向成立，但F02的内层构造owner还未被完整覆盖。

正常路径源码具六真实snapshot/原PTS、六编码输入/样本、原codec/Image/Sink/lease关闭、isolated完整EOF/PTS≤1ms/画面验证及最后host owner关闭的分层门槛；原流量forwarded不等真实encoded。运行期不重选codec、四提案12s/总60s，最终READY不等业务COMMIT。当前全部Android正常与故障结果NOT_RUN，不能从源码或JVM89条推断可用或归还。

## 4. 八项设备计划的可调度条件

| 分组 | 编译用例 | 审查意见 |
|---|---|---|
| 正常2项 | normalMp4SixRealFrames、normalAviSixRealFrames | 必须先各一次、同设备真实源/六帧/隔离验证/实际owner归还；当前未派发 |
| 独立反例2项 | capabilityDenialDoesNotOpenSource、binderRefusesBeforeBeginAndOversizeParcel | 区分实际Binder拒绝与伪UID消息；能力拒绝虽Source0仍可能授出空Sink FD，不应写FD0 |
| 取消1项 | cancelRejectsWrongEpochOversizeAndLateFrame | 依赖外部已核正常receipt；需先修F03的原control归还观察 |
| quarantine3项 | selfKillOtherCpuContinuesAndOldGenerationRejected、nativeSegvOtherCpuContinuesAndOldGenerationRejected、closeUnprovenRetainsPermitAndNeverReady | 三项分别独立最后方法；不能在同一未知许可域连续执行 |

故障前源码确实要求原codec ACTIVE、另一真实isolated任务已接纳readAt并受控等待，fault后原Binder death、主Handler响应、另一任务实际RGBA及源归还；不是空闲心跳。另任务首个底层文件read在gate放行后才执行，不能把故障前等待写成已读完字节。两阶段arm/commit及迟发前原Session核验、自身native hook过程名/Debug限制存在；它们尚未设备执行。

新代探针仅metadata HELLO及旧身份QUERY拒绝，不BEGIN、不授新Sink/encoder，旧UNKNOWN许可保留；不能称恢复编码成功。系统reason/status按原值保留，status0仍UNKNOWN_FAIL；本批不是重跑C14 CPU旧信号条件，不能修改旧严格FAIL。

三项quarantine不是可紧接着执行的6→7→8序列。每项后的原host/worker/绑定/许可需归档，是否允许结束原进程并建下一独立批次由负责人另裁定，不能借instrumentation启动新host自动洗掉未知许可。修复后的计划还须把F01的累计输出预算落实到跨方法/必要跨host范围；现4MiB“累计”尚无代码证明。

单输出含头≤2MiB、总4MiB/128文件记录、每方法日志≤4MiB/整批≤32MiB；这些为计划界，非实际峰。预置源只读占用约736.8MB，不当新输出。若8项均各执行一次且前后全hash，6个MP4方法＋1个AVI方法的fixture核验计划读取1,477,098,536 B，另加CPU实际请求，须正式批次单列，当前未访问这些文件。源码内e4Case/e4Batch/normalReceipt格式只是误调度护栏，不能代替外部授权及同设备真实前置receipt核验。

## 5. 依赖、宿主和剩余门禁

Media3固定1.9.3；FFmpeg8.0.3受限白名单/网络禁用配置及7原native库未扩。SBOM为35锁定坐标、新增GA family0、14个GA所选版本集合与C14有差异，不宣称整个图不变。原签名/NOTICE/来源hash有效不等新增SCA、漏洞清零、生产发行许可、再链接/商店/专利/闭源宿主兼容通过。

E4独立最小app不依赖Browser/SMB/Room业务类型，帧不走Dart；但SDK正式AAR服务命名冲突、manifest合并、多实例/多宿主池、公共API与Flutter生命周期尚未实现或验证，不能将内部实验类名冻结成产品契约。iOS/macOS/Windows仍只设计，不因缺环境否决当前Android静态准备，也不计支持完成。

J03–J05及部分J06获得新可测owner进程，不等风险关闭。J01旧host Source/Media3、J07旧host MediaExtractor未编入最小APK不等产品链已解决；J08字幕/字体、J09图片/FaceDetector、J10跟踪/遮罩/GL、J11 Surface/Texture/AudioTrack/焦点均不被本codec service覆盖。未跑Image分支不能由ByteBuffer路径替代，软件codec不能称硬件保证，逻辑数组/queue限额不能代替ART/Binder/系统codec/驱动/RSS实测。

## 6. 集中修复后再交审

请负责人统一安排F01/F02/F03修复及有界离线证据，保留当前候选/失败日志和C14原冻结，不测浮动源码。重新冻结完整源码/APK/签名/依赖差异/四文档和调整后的8项计划后，tester复审再决定可派范围；本轮不直接交设备验证这些代码缺口。

届时仍需正式指定设备与独立批次，先只读核安装身份、App/service enabled及手机既有阻断、API/ABI/空间/签名/fixture当前hash，再授权安装动作与准确方法；不从旧连接猜可用、不轮询ADB、不换包名/卸载清数据/强启绕过。先正常前置，失败即BLOCKED依赖项；未知状态保原owner/许可和原系统值，不补跑求signal。

**本轮设备/Gradle/ADB/fault执行0，无在途任务；REQUEST_CHANGES。** C14冻结、73项待设备及两项NOT_RUN_UNCHANGED_PLATFORM_LIMIT、旧signal0严格FAIL/外部raw11/另方法signal11分别保留。全部原P0、JNI残留、剩余J01–J11继续开放，**D1 NOT_PASSED、M0 NOT_STARTED**。完整报告主动交负责人，不自行执行下一批。
