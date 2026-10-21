# D1_FIXTURE_TOOL01_BUILD 阶段B独立整包静态复审报告 V1.0

日期：2026-10-21。测试人：tester。接收人：负责人01a107c3-2bf9-7fa0-94a0-234258ca6774。

## 1. 结论

**FAIL_SOURCE_DERIVED_WITH_RUNTIME_NOT_RUN。** 冻结身份、构建来源、许可证资源和一次实际构建材料在本次独立静态范围通过；真实driver源码存在两项P2状态/证据问题：**FT-B01** pending write/seek可能将未采纳的实际物理位置/extent报告成确定旧值；**FT-B02** 限时join已到期后、isAlive检查前的迟到完成可能漏记deadline UNKNOWN，进入generated-candidate成功分类。

两项均为**冻结源码及对应class字节支持的合法时序反例推导，未动态复现**。本次没有运行JVM测试、Main、编码器初始化、wrapper I/O、编码或生成；不能将推导写成实际失败次数或将其余静态项写作运行PASS。建议集中修复并交完整新冻结复审，当前不放行本工具的生成准入。

工具build hash已取得，解决UNBUILT身份缺口，但不解决运行/fixture/真实Media3资格化/产品门。原session48945/17257 UNKNOWN保持，本次未轮询、attach、查询/处置原进程，也没有设备/SDK/ADB/Gradle/共享缓存/网络或媒体操作。D1未过、M0未启。

依据 [正式B测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_FIXTURE_TOOL01_BUILD_TESTER_REQUIREMENTS_V1.0.md)末尾及 [完整交付](D:/CodexProjects/VideoKit/docs/coder/D1_FIXTURE_TOOL01_BUILD_DELIVERY_V1.0.md)。所有动态项按本次明确范围保留NOT_RUN，不以编译、自报算术例或coder静态检查代替。

## 2. 实际纯Python入口及独立核对

按要求在全新独立子目录执行一次：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B D:/CodexProjects/VideoKit/docs/coder/d1fixture-tool01/tools/review_materials.py --output D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/independent-001
```

原工具session22955自然exit0返回，输出 [receipt.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/independent-001/receipt.json)。这是实际材料入口执行，不含Java编译/加载或任何产品测试。另独立Python逐项核ZIP/source/classfile/原构建回执，并自行解析class constant pool、SourceFile和方法Code hash，没有运行javap或新JVM。

|核验对象|独立结果|
|---|---|
|主报告SHA-256|85553ab27c1a6bfe9880f1f1123a983c5352a9cd952553f9314702ccee702251|
|seal SHA-256|f12b646ce6afd66091f59f509c6d46fc62e343e16671d749225242fa9d6a2670|
|seal/ZIP|1753记录含ZIP；1752唯一成员，集合及逐项字节/hash相符|
|工具JAR|1948772 B；af24b4aa66bed72957803f2ff44a8a45cd7c143d72441e3f640cb55490af9959|
|源码|711文件/4465907 B；708原source逐字节匹配固定source archive，新增3driver|
|实际class|982；JAR集合及每个class字节匹配本次真实javac输出，Java11 major55，类名/SourceFile与准确原输入关联|
|旧封存|6972文件hash保持；Android01独立B20项、阶段A7项及原报告保持|

JAR只有982个class、准确manifest及许可resources，无extra/native；Main-Class为com.videokit.fixturetool.SixFrameDriver，Created-By21.0.10 JetBrains。class方法Code的独立hash与源归属见 [independent-class-origin.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/independent-class-origin.json)，不能把class存在或类型检查当运行证据。

## 3. 一次构建、全口径尺寸及许可

独立核固定已有JDK21.0.10 java/javac/jar/release/lib/modules字节/hash、真实argv/cwd及source argfile711项；javac显式-J-Xmx512m、--release11、UTF-8、-proc:none、-implicit:none，classpath/sourcepath/processorpath均为新专属空目录。无Maven/Gradle/测试JUnit/processor/插件/下载、PATH或环境classpath补入；原环境注入选项移除和预构建输入pin已保全。

原构建两进程各一次、串行，自然exit0、同原输出handle关闭且未触发超时或终止：javac历史PID3284，UTC00:08:09.652283–00:08:16.778591；jar历史PID29872，UTC00:08:17.155389–00:08:33.566592。父控制器73877的原返回记录已审；本次不查询这些历史PID或重建。原javac上游dep-ann/废弃/unchecked提示保留，没有为消警修改原source。早期bundled路径展开假设修正发生在编译前，未计成第二次compiler。

source/driver输入4465907 B≤16MiB；自然返回时全部实际构建输出5947592 B；封存记录所列候选文件加ZIP共20442547 B≤64MiB。逐项原输出文件hash/大小核对，不只看1.95MB JAR、不去重、不把已安装JDK复制量混入已定义的source输入口径。该结果是本批实际大小核对，非OS磁盘硬配额、恶意源码沙箱或未来构建上界证明。

许可证资源与package-resources及JAR成员逐字节相同：FreeBSD版权/免责声明、SOURCE_NOTICES逐原文件头、Guava Preconditions Apache2.0及全文、73个bundled JAAD的Public Domain/JCodec FreeBSD修改说明、自有driver内部开发声明均保留。POM摘要未冒全树唯一许可；JAR内其他codec/CLI仅被编译，未获调用准入。未升级专利/商业发行/旧FFmpeg清权。

独立结果：[independent-material-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/independent-material-audit.json)。

## 4. FT-B01 / P2：pending receipt把未确定物理位置写成确定值

位置：[AttemptBudgetChannel.java:60](D:/CodexProjects/VideoKit/docs/coder/d1fixture-tool01/driver/com/videokit/fixturetool/AttemptBudgetChannel.java:60)、[receipt:128](D:/CodexProjects/VideoKit/docs/coder/d1fixture-tool01/driver/com/videokit/fixturetool/AttemptBudgetChannel.java:128)。同类seek窗口位于104–109行。

write在native前设置inFlight=1并预留attempt；native返回后，logicalPosition/extent/acknowledged才在后续synchronized块采纳。receipt虽然持通道锁，却仅依据physicalPositionUnknown输出actualPhysicalPosition/actualPhysicalExtent；该flag只在异常/不匹配后置true，正常在途或“原调用已返但尚未采纳”没有被排除。

静态可达反例（没有实际I/O运行）：

1. 请求10B已进入，同通道attempt=10、inFlight=1、logicalPosition/extent=0、physicalPositionUnknown=false。
2. 同原FileChannel.write已成功返回10B，真实position和extent已为10；worker在采纳67行状态前被调度挂起。
3. 主线程观察期限后确认worker仍活着，设置deadline UNKNOWN并构造pending receipt；此刻通道锁可取得，worker未持该锁。
4. receipt给出nativeInFlight=1，却将actualPhysicalPosition/actualPhysicalExtent写成确定0。正确的0只能称最后已采纳值；此合法时序下实际原file已到10。

setPosition同理：positionCalls已加一、原seek成功返回，但logicalPosition/positionReturns尚未更新时，pending receipt仍将旧位置称actual。只略去活ArrayList事件避免遍历竞态，没有解决标量事实与原调用采纳间的时序。

影响为pending/UNKNOWN证据真实性错误；**未据此声称文件损坏、提前close或错误签发合格fixture**。建议actual字段在write/seek未返或未完成采纳时明确UNKNOWN/未确认；lastAcknowledged*可保留旧值，异常UNKNOWN继续sticky。不得为补值新开handle、强停、二close或用file size倒推原返回。

## 5. FT-B02 / P2：timed join与isAlive之间可能遗漏已到期状态

位置：[SixFrameDriver.java:240](D:/CodexProjects/VideoKit/docs/coder/d1fixture-tool01/driver/com/videokit/fixturetool/SixFrameDriver.java:240) 附近的worker.start/join(DEADLINE_MS)、后续isAlive分支及joined/receipt。精确token行号随 [source-derived-findings.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/source-derived-findings.json) 保存。

只有isAlive检查当下为true才调用job.deadline；源码没有单调deadline或同原worker完成时间，用来区分限时等待到期前后。其“不升级迟到成功”只覆盖已经置deadlineUnknown的分支。

静态可达反例（相对限时等待起点，不是实测时间）：

|时刻|原线程/主线程事件|
|---|---|
|60000ms|join(60000)的等待窗到期返回，worker仍活着；主线程在后续isAlive前被调度挂起|
|60001ms|同原worker正常完成且原handle已关闭，bodyReturned=true|
|60002ms|主线程恢复，isAlive=false，跳过整个deadline分支；置joined=true|
|最终receipt|若无其他错误，则GENERATED_CANDIDATE_NOT_QUALIFIED、deadlineUnknownSticky=false，并可能清除ORIGINAL引用|

这会将超过60秒窗的完成当成非超时成功分类，破坏期限UNKNOWN及不得迟到升级的判据。**仍不是合格fixture或产品成功**，也没有实际运行编码来复现。

建议用单调起点/deadline与同原worker完成时间，或明确原子完成/到期决策，保留真正到期后的UNKNOWN；继续同worker实际join/原强保管，不引入interrupt/kill、重试或提前native归还。修复应同时覆盖“已观察到期限后迟返”和“timed join到期后、isAlive读取前返回”，不能只保留原前者分支。

## 6. 其余源码判据及明确边界

AttemptBudgetChannel的静态正向实现包括：同原worker/holder准入、每次native前按requested≤65536预留、positive partial前移原buffer再请求剩余、header rewrites同通道累计、512事件满前拒绝、非空0/负值/>requested或buffer位置异常拒绝、不spin、异常首错/UNKNOWN、不退款；position以减法界防溢出，read/truncate拒绝。六组算术例与这些正常/异常分支静态对应，但本次未运行一次wrapper I/O，不能写成六例动态PASS。

CREATE_NEW固定新root/new-output与逐父canonical/reparse检查、原holder在open及mux构造前登记已审；无任意path/URL/原媒体输入。其防误用范围依赖可信私有workspace，不冒恶意并发文件系统或RCE防护。原finish/force/单close、writer关闭后只读reader全EOF/hash和外部同worker join、未知目录始终不删、原encoder/mux/channel引用保管均有代码；除两问题外没有由本次静态证据确定的新增放行问题，实际native行为仍NOT_RUN。

真实driver参数与原提案一致：原创YUV420J、256×144、单帧55296 B/六帧331776 B，六次真实encoder调用方案，keyInterval1/motion0/DumbRateControl起始QP20非constant-QP；每raw AU非空≤262144 B/总≤1572864 B、实际keyflag/IDR观测、CSD64KiB门。编码器raw AnnexB在addFrame前记hash，CodecMP4MuxerTrack内部去PS/AVCC转换一次；track内部AvcC/SPS/PPS与库转换AnnexB各自标明表示，未冒容器重新提取的AU hash。

六Packet pts0..5/timescale5/duration1、声明end1200000us，JCodec finish不加第七帧；未来Media3 E6空EOS flags4/fragment3000ms仍独立。源MP4Muxer当前Date未改，确定像素/PTS不冒整文件重复hash。生成后的真实container AU、CSD、size/hash、PTS/duration、Media3资格化均未取得，raw-AU/内部CSD证据不等容器正例。

ReceiptJson有1MiB上限及pending省略活samples/csd/events的设计；最终joined后才遍历完整列表可静态核对，**该列表策略不消除FT-B01的标量事实窗口**。实际序列化/超额/原输出工具归还未动态测，不能以源码看似安全登记运行PASS。

## 7. FT01–FT28映射与未来最低受控运行条件

完整映射见 [independent-ft01-ft28-results.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/independent-ft01-ft28-results.json)。材料/字节/build来源/许可/无运行项为PASS_STATIC_MATERIAL_SCOPE_ONLY；其余为静态实现已审、动态NOT_RUN；FT10/13/16/22关联FT-B01，FT23关联两项问题。没有把“28准备项”或6个声明式例改成28/6次真实测试。

未来最低受控wrapper运行条件已完整写入 [future-controlled-test-conditions.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/future-controlled-test-conditions.json)，当前不授权执行：

1. 集中修复后完整新候选冻结，重新绑定driver/source/class/tool hash、源归属和两项状态修复；原48945/17257 UNKNOWN独立保留，不能由此假定host idle或获处置授权。
2. 负责人另签有限非媒体wrapper/时钟/receipt范围、精确runner和产物、进程/heap/字节/期限及原返回保管。当前adapter绑定具体Job.FileOwner/FileChannel，若需受控partial/0/异常/时间门，必须先冻结最小明确测试端口/调度机制，不临场反射改状态或造通用框架。
3. 覆盖full/partial10→3+7/header8，0/非法返回/空write，16MiB+1/overflow/512事件前拒绝，partial后异常UNKNOWN无重发/二close/退款；原write/seek已返回但采纳尾段未返时snapshot，以及timedjoin到期后isAlive前迟返。
4. 分开原owner登记、CREATE_NEW/已有/reparse拒绝、finish/force/单close/外部join、pending和final receipt有界输出及真实归还。只操作新受控非媒体资源，不运行SixFrameDriver.main/Job.run、H264Encoder初始化/encode或产生媒体。
5. 有限wrapper证据不等真实生成；准确工具运行/生成scope、实际新媒体manifest、真实Media3资格化及Android mux新包仍按后续各自审定，不用本报告或build hash跳过。

本次没有执行这些建议或编译新测试harness。

## 8. 集中交接

本批两项源码推导P2阻断当前生成准入，交负责人统一回交集中修复并另派完整包复审；保全现有准确build产物和失败报告，不在原候选上改代码或重复构建。动态确认仍须另行准确范围，不能为了证明问题运行编码器或复现旧挂起。

材料入口和独立Python审计均已完成自然返回，无本次新增在途工具；原1753记录、旧6972及原阶段A/Android01B证据保持。报告及证据发送前冻结、发送回执另存；不自动进入修复联调、JVM/工具运行、生成、设备或原owner处置。所有旧FAIL/UNKNOWN及许可/P0门保持，D1未过、M0未启。
