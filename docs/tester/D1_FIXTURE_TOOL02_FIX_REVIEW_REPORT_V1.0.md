# D1_FIXTURE_TOOL02_FIX 独立整包复审报告 V1.0

日期：2026-10-21。测试人：tester。接收人：负责人01a107c3-2bf9-7fa0-94a0-234258ca6774。

## 1. 结论及限制

**PASS_LIMITED_NONMEDIA_FIX_WITH_GENERATION_NOT_RUN。** FT-B01/P2在同原内存端口的调用/采纳快照范围修复通过；FT-B02/P2在单调body/cleanup完成点与同原线程实际join分离的指定契约范围修复通过。本次未发现新增离线/有限非媒体阻断。原tool01报告仍为源码推导FAIL，不回写成已动态失败或旧PASS。

已实际执行冻结材料入口和双路径29组检查，并独立编写一次固定最小helper，源码/生产JAR优先每路径17组通过，各启动16个原worker均实际join。**这些是内存通道、受控回调、时钟及真实线程返回的有限证据，不是OS FileChannel/编码器/媒体生成结果。** 未调用Main、Job.run、H264Encoder、MP4Muxer，不初始化编码器、不产生媒体、不做Media3资格化、设备/ADB/Gradle/缓存/网络或旧会话操作。

本次不放行真实生成。原48945/17257 UNKNOWN不查询、不轮询/attach或处置，不由这次原JVM返回证明host整体空闲。D1未过、M0未启，P0/J11/C13/发行专利/FFmpeg等历史门不改。

依据 [正式B测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_FIXTURE_TOOL02_FIX_TESTER_REQUIREMENTS_V1.0.md)末尾准确非媒体范围及 [本批完整交付](D:/CodexProjects/VideoKit/docs/coder/D1_FIXTURE_TOOL02_FIX_DELIVERY_V1.0.md)。

## 2. 冻结、来源、许可和构建

|对象|独立核验|
|---|---|
|候选|docs/coder/d1fixture-tool02|
|交付文档SHA-256|ff875c5c0b7c6e589fd6704927b4e413b04236ae466dd51348b66f1026b3cf68|
|seal SHA-256|5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d|
|seal/ZIP|2774记录含ZIP；2773唯一成员，集合及逐项大小/hash一致|
|工具JAR|1954730 B；c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd|
|输入|713 Java/4492852 B：708原source、4driver、1checks|
|class分离|990真实javac class；985生产class进工具JAR，5测试class排除|
|原构建|一次javac、一次jar，原句柄自然exit0/输出handle关闭，无超时/终止/重试|
|尺寸|原构建实际输出9578896 B；冻结候选含ZIP27731759 B，均≤64MiB|
|旧封存|8725项保持；tool01独立FAIL及11项证据保持|

独立Python逐项核708上游Java及ReceiptJson与01不变；新增/修改仅driver/channel/WorkerDeadline和独立checks，无新binary/native/依赖或同名假成熟库。固定JDK21.0.10工具及modules身份、源pin、真实build recipe/argv核对；-proc:none/-implicit:none/空专属classpath/sourcepath/processorpath、713项argfile、512MiB构建heap与并发1保持。本次没有重建编码工具，仅按授权另编译一个tester最小helper。

独立解析全部class的类名、SourceFile、Java11 major55，并与原javac输出/production或test副本/精确source hash关联；生产JAR逐class字节一致，manifest Main-Class仍SixFrameDriver，仅为身份信息。JAR资源与准确package-resources字节一致，无额外测试class或native。FreeBSD版权/免责声明、Guava Preconditions Apache2全文、JAAD Public Domain/JCodec修改FreeBSD及逐文件头保留，未扩大商业/专利清权。

原构建PID34216/29200及起止仅作为冻结回执审查，不查询当前历史PID。材料细项见 [independent-material-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE/independent-material-audit.json)。

## 3. 实际入口、双路径及独立helper

先运行纯Python材料入口，再运行另一个新子目录的固定非媒体入口，均自然exit0：

```text
tools/review_materials02.py --output D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE/materials-001
tools/review_checks.py --output D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE/checks-001
```

实际Python为既有bundled绝对路径，argv及原入口/源码/JAR身份可由回执重放核验。文档入口源码classes和生产JAR优先+test-only目录各29组通过，58是两条路径执行次数，不当作58项不同功能。未运行coder build_one/run_checks/audit旧top-level。

另独立实现 [IndependentFix02Check.java](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE/IndependentFix02Check.java)，只引用现有channel/WorkerDeadline/真实接口及最小自有内存端口，未使用反射改生产状态。固定一次javac，仅编译该helper到独立目录，heap256MiB/-proc:none/-implicit:none、空source/processor path；不编译生产或编码工具。原helper编译及随后两条原JVM均自然exit0、原stdout/stderr handle关闭，没有超时/强杀/interrupt/重试。

独立源码路径使用helper目录+冻结classes；生产路径仅新工具JAR优先+helper目录，无raw production fallback。CodeSource同时核channel与deadline来源；四条运行JVM的class-load记录均仅使用JCodec真实SeekableByteChannel接口，不加载SixFrameDriver/Job或codec/muxer类。类元数据/JAR读取不是编码器初始化或OS媒体FileChannel测试。

每路径17个独立组、16个实际启动worker，全部原门finally放行并join。每组5秒/独立编译加两次运行总60秒门保持，本次独立编译+运行约1.5秒，未触发观察超窗。原回执保留时间、PID、argv/cwd、input/helper/JAR hash及原返回；这些PID不当未来身份。

证据：[文档检查汇总](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE/checks-001/summary.json)、[独立helper汇总](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE/own-helper-summary.json)、[独立生产路径原输出](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE/own-production/stdout)。

## 4. FT-B01独立修复验证

新通道将native进入、返回已观察、结果采纳分开，同锁保持inFlight/pendingAdoption/lastAck；任一未解决时actualPhysicalPosition/Extent为UNKNOWN，事件列表不暴露活对象。原afterNativeReturn生产默认no-op，测试使用同原worker的真实callback门闩，未通过预设内部布尔量或替代任务制造结果。

独立六操作WRITE/SEEK/FORCE/POSITION/SIZE/CLOSE每次依次保留两扇真实门：

|观察点|实际独立断言|
|---|---|
|内存端口内部物理改变、原调用尚未返|nativeInFlight=1、resultAdoptionPending=1，实际物理两字段UNKNOWN；lastAcknowledged旧值保留|
|同原端口调用已返、同原callback/采纳尾段尚未返|nativeInFlight=0、pending=1，两actual字段仍UNKNOWN；lastAck未提前更新，不输出活事件列表|
|同原callback放行、同worker cleanup并实际join|inFlight/pending均0，最终结果采纳；原close一次，物理值scope为LAST_CONFIRMED_BEFORE_ORIGINAL_CLOSE|

WRITE使用6B：实际内存position已到6而原caller ByteBuffer.position仍0，直到采纳才推进，直接覆盖旧FT-B01的物理/采纳窗口。SEEK先正常写4B，再实际定位到1，两个窗口仍保留lastAck4而actual=UNKNOWN。FORCE/POSITION/SIZE/CLOSE同样分别停原端口与原callback，没有把“返回已观察”当采纳完成。第一份旧scalar snapshot不因后续事实改变，事件map修改也不会改原记录。

最终普通close后的数值明确只是关闭前最后确认事实；受控native或adoption错误继续sticky UNKNOWN，未新开查询handle或清未知。该结果有限关闭tool02指定NativePort/采纳/快照问题，未声称真实FileChannel/磁盘/force已测。

## 5. FT-B02独立修复验证

WorkerDeadline用单调起点和同原worker在cleanup之后的最后受控body完成点作时间判定，等号算迟返、负半区间/倒退保守UNKNOWN；实际Thread.join独立必需。body marker**不是OS线程退出时间**，其合法及时性与原线程后来实际返回两者必须同时满足，不用observer晚采样伪造迟到或提前返回。

|独立输入|实际结果|
|---|---|
|timedjoin已返回、worker仍等门，clock101完成，103才观察，期限100|deadline UNKNOWN，不会在isAlive采样前迟返时升级|
|clock80完成、300才观察，期限100|原完成及时；同原真实join后允许timely，晚观察不误当原完成迟到|
|clock100完成，期限100|等号为迟返，UNKNOWN sticky|
|nanoTime从Long.MAX附近跨至Long.MIN附近|有效模回绕差值按契约判定及时，不拿带符号原值直接比较；独立数值与coder样例不同|
|完成点倒退或observer倒退|invalidMonotonicRange/UNKNOWN，不升级|
|body marker70已记但同原线程尾段仍在，observer500|未实际join时timelyAndJoined=false；正常放门并join原线程后才可及时完成，遵循body完成点契约|
|实际System.nanoTime 15ms观察窗，原线程门未放|真期限到期只产生UNKNOWN，原线程仍由finally正常放门/join；迟返不升级|

文档29组还实际覆盖20ms真实窗、已观察UNKNOWN后迟返、wrap等号及错误完成/范围门；本次独立helper没有复制这些计数冒额外覆盖。新Main静态核确实使用waitState.awaitBodyWindow/observeUnknown/joinSameOriginal及最终timelyAndJoined门；Main/Job本身未运行，真实60秒编码作业未执行。

据此有限关闭FT-B02“单调body完成点+同原真实join”范围。没有把测试钟当实际编码时间，没有断言OS线程在body marker时已退出，旧source推导FAIL保留。

## 6. 计量、异常、容量及真实原返回

独立输入使用不同于coder的数值：7B请求先返2再返5，attempt=12/knownReturned=7；seek0回写3后attempt=15/returned=10/extent=7/position=3。partial后第二请求额外物理写1再抛错，attempt=12、knownReturned下界2、内存实际position3，receipt仍UNKNOWN，不重发/退款；首错还阻止新force，cleanup不被它阻断。

另用prior meter reservation=16MiB−4，实际只写4B到精确界，随后1B在native前拒绝；明示该大数是计量接缝，非实际16MiB载荷。512次metadata position事件后，额外size在native前拒绝，但一个独立terminal close仍可执行，最终nativeCalls513/常规事件512/close一次。错误worker/read/truncate、空write、detach事件、内存close-throw不得二close均有实际原断言；文档入口还回归非空0/负/>request及负/overflow范围。

|本次范围|实际已知量|
|---|---:|
|文档29组两路径byte[]载荷|36928 B|
|独立17组两路径byte[]载荷|3392 B|
|合计byte[]载荷|40320 B≤65536|
|合计native requested内存载荷|1366 B≤65536|
|合计受控返回/已知物理写入（含注入额外1）|1238 B；非磁盘持久化量|
|独立原worker|每路径16启动/16实际join|
|本次受控JVM / helper编译|4个JVM自然返回 / 1次helper编译自然返回|

原JDK/JAR/class-load/receipt日志属构建/控制元数据，未混称非媒体native载荷。heap每原测试JVM256MiB、单进程串行、门闩2秒有界、finally放门及原join保持；本次未产生测试新在途工具。所有raw日志原样保存，无故意永久挂起、kill/interrupt或盲重放。

每个文档/独立JVM各有一个刻意close-throw内存对象，合计4个：引用保留至各JVM退出，原对象未报closeReturned、无第二native close。它们无OS FD/异步工作，**不是平台close已经证明或旧UNKNOWN消失**。所有本次已启动worker与原JVM确已归还，和预期内存UNKNOWN分栏，不伪报“所有close成功”。

## 7. FT01–FT28及未执行范围

完整逐项结果见 [independent-ft01-ft28-results.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE/independent-ft01-ft28-results.json)：FT09–16、FT22/23仅在受控内存/计时/线程范围通过；build/source/license/JAR等为静态材料通过。文档29组与自有17组互有重叠，不合并成92项独立功能或编码用例。

以下仍NOT_RUN：真实CREATE_NEW/reparse与FileChannel、OS部分写/异常/FD/force/fsync、真实生成worker60秒/实际codec/muxer、原创六帧/AU/CSD/NAL/MP4生成、真实容器PTS/EOS/duration、只读媒体全EOF/hash、Media3资格化、新Android mux链及播放。保留源实现不变及字段golden=null等静态证据，不能代运行。

同样不能由本次有限自测推断通用RCE隔离、恶意/不受信文件系统防护、整机线程/内存峰值或旧会话原返回。未来真实生成须另行准确工具hash/scope/预算/原owner及执行门，生成后冻结真实媒体manifest，再独立资格化；本报告不授权任何一步。

## 8. 保全及集中移交

最终核2774项新候选未变，旧8725封存及tool01原独立FAIL/11项证据保持。材料入口、受控入口和独立helper源码/原argv/原stdout-stderr/类来源与class-load记录完整保存。收尾核对见 [post-review-preservation.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE/post-review-preservation.json)。

负责人可按本报告限定的非媒体范围关闭FT-B01/FT-B02；原生成/fixture/平台与P0门继续保留。完整报告及证据发送前冻结、回执另存。本批已完成，等待负责人统一安排后续，不自动继续测试、重建/运行工具、生成媒体、设备或原48945/17257收尾；D1未过、M0未启。
