# D1_FIXTURE_TOOL01_BUILD 阶段A准备报告 V1.0

日期：2026-10-21。测试人：tester。接收人：负责人01a107c3-2bf9-7fa0-94a0-234258ca6774。

## 1. 结论和范围

**PHASE_A_DRIVER_ORACLES_PREPARED。** 已基于冻结Android01的JCodec0.2.5官方source/API/生成提案及独立B材料，完成28项driver检查判据、6组累计attempt数据例及未来构建/原owner证据合同。本报告不审新driver、不登记新工具PASS，不产生编码fixture。

本批一次固定离线javac/jar构建授权属于coder开发批，用于取得准确工具hash；tester阶段A仅静态准备，**编译/打包/工具Main/编码器初始化及生成均0次**。未读取 `docs/coder/d1fixture-tool01` 浮动新源，未重放62入口/挂起场景、attach/诊断/设备/ADB/Gradle或共享缓存；没有触及原活动suite目录、旧账或owner。用户“继续推进”不解释为原强制收尾批准，session48945/17257仍UNKNOWN。D1未过、M0未启。

依据 [本批测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_FIXTURE_TOOL01_BUILD_TESTER_REQUIREMENTS_V1.0.md) 和负责人正式阶段A派发。所有FT01–FT28状态均 **PREPARED_NOT_RUN**；仅既有冻结身份/静态内容检查具有本阶段证据。

## 2. 固定来源及静态输入闭包

|对象|核对|
|---|---|
|Android01 seal|fca6adcdf9783b91c9af396de3b836efad72c4d59ef820eb1924d8658f0b928a|
|既有独立B报告|845cd5920251c44beed2497d66d6843e5e6531e209d503cc93eb598f45fe2829|
|B证据manifest|61b93d6d827cb29d868a548a2740fcfa88d9d0aeac083c4664582b72fa11d951；20项逐字节保持|
|JCodec0.2.5 source archive|1246282 B；9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db|
|原API提案|GENERATION_API_SEQUENCE_PROPOSAL.txt及generation-proposal.json固定hash核对|

仅以Python读取ZIP/源码文本：807条目中 **708个Java源码、合计4435752 B**，其中635个org/jcodec、73个net/sourceforge/jaad。后一组在同一固定source archive内，不能因包名前缀不同误报为缺少未获准外部依赖，也不能静默省掉它们后声称“编译全main树”。静态import扫描中，除java/javax/org.jcodec以外的引用均落入该bundled JAAD命名空间；这是文本闭包筛查，**不等于Java类型检查或编译成功**，反射/资源/实际源码列表仍须新包准确核定。当前没有下载或补依赖。

708源码的4.44MB在16MiB build-input界内，但还须纳入真实driver、其余规定输入和准确统计口径；全部构建输出≤64MiB不得只统计最终JAR、忽略classes/副本/回执或将未知量写成0。源清单、编译器、参数及输出实际hash须随新冻结交付，不能从原提案source hash推算build hash。

许可检查需保留具体源归属：POM/当前仓库FreeBSD版权免责声明、`Preconditions.java` 的Guava Authors/Apache2.0头，以及bundled JAAD源码明确的Public Domain与JCodec修改FreeBSD说明。不能把POM“FreeBSD”简化为所有源码仅一个许可，也不把包含JAAD代码等同本driver实际解码AAC。这里是构建范围和通知清单准备，不是新增运行依赖批准、法律清权或新候选缺陷；专利/商业发行/旧FFmpeg门保持。

证据：[source-inventory-and-api-evidence.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL01_BUILD_PHASE_A_EVIDENCE/source-inventory-and-api-evidence.json)、[baseline-identity.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL01_BUILD_PHASE_A_EVIDENCE/baseline-identity.json)。未重跑旧基线套件。

## 3. 短写、header回写及累计attempt oracle

冻结真实源码提供三个直接判据：MP4Muxer构造器写ftyp/wide/mdat时仅一次output.write；MP4MuxerTrack.outChunk对每个样本块仅一次out.write；NIOUtils.writeLong只对8B缓冲执行一次channel.write。finish的storeHeader先写movie header，再setPosition(mdatOffset)回写长度。因此薄通道包装必须完整处理短写，不能只返回首个partial就让库丢掉剩余字节，更不能自写容器补救。

定义：A是每次进入**原native write之前**预留的requested数量累计；R是经有效原返回证明的写入数量累计，不是durability或磁盘物理落盘量；position、extent/file size及A/R各自独立。每次native requested≤65536，检查剩余16MiB及溢出先于native进入。正partial后的继续使用同一channel/同一缓冲剩余段，仍是新的native attempt，不能按最终样本大小一次计完或退还先前预留。

|数据例|准备的预期，尚未执行I/O|
|---|---|
|写10，原返回3，再写剩余7返回7|A=17、R=10、extent=10、position=10；短写继续不等于重试失败任务|
|上述完成后seek0，header写8返回8|A=25、R=18、extent仍10、position=8；覆盖旧位置不抵扣attempt，最终position也不是file size|
|写10返3，再请求7时异常且amount未知|A=17、R已知下界3、额外物理写入/实际position UNKNOWN；首错sticky，不重发/回退/退款，原owner保持|
|先前A=16MiB−8，原请求8完成，再请求1|8的有效原请求可准入，A=16MiB；后1在native调用前拒绝，A不虚增为已进入|
|非空请求10，原返回0|A保留10、R=0；不能无限循环或报整个写入成功，应有明确失败/停止策略|
|调用者零长度write|无native调用、不加attempt、返回0；不能为此分配额外源或触发真实写入|

负数或大于requested的结果、position+count溢出、负seek等应在各自确定边界拒绝；真实写异常后的UNKNOWN不能用后读file size消除。适配器若要保证整段写完，返回总数必须与原有效返回和ByteBuffer推进一致；原缓冲的position/limit及duplicate/slice不能跳过预算。禁止将部分native返回的R误记为A、将最终文件大小当累计写量，或对header rewrites遗漏计费。

对setPosition/size/truncate/read的实现审查须符合JCodec的真实SeekableByteChannel合同：position变化不计写但也不退款；最终finish可能让position停在header中；无需要的read/truncate可明确拒绝，不能另开任意文件/缓存/网络补语义。分块、partial与header路径只能包装同一个原channel，不增加第二个closer。

见 [attempt-accounting-examples.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL01_BUILD_PHASE_A_EVIDENCE/attempt-accounting-examples.json)。这些是声明式oracle数据，未编写或运行新driver/受控native写测试；不登记6项执行PASS。

## 4. CREATE_NEW、原owner及退出

新工具必须在固定、全新、获准私有路径用CREATE_NEW原子创建文件；已有文件/越根/重解析父路径拒绝，不能退化为FileOutputStream覆盖或接受任意路径参数。原路径/内容输入仅原创程序内YUV，不读取BBB、其他媒体或网络。父目录身份与输出新建事实须实际记录；不以规范化字符串单独证明无reparse。

原channel holder要在分配之前登记，**必须早于MP4Muxer构造器**，因为构造即写header，不是等第一帧才开始输出计量/owner保管。实际分配失败且返回不明时保留UNKNOWN及原引用；不通过新holder、重开或二close“修复账目”。

正常路径分别留证：实际mux.finish返回、可选同原force返回、同原close恰一次、外部同原worker join。mux.finish不等channel close；FileChannel.force不等业务COMMIT；receipt或进程退出也不能补原finally/回调证据。首错先于cleanup错误记录，后错不得覆盖；失败/期限/UNKNOWN无新准入、无退款或替代encoder。

60秒是观察/停止准入界，不能强杀/interrupt或将等待到期当归还。编译原进程的60秒与未来编码worker的60秒分别记录，不能混用生命周期。原资源/worker未正归还时不得删新目录、二close或自动清理UNKNOWN；也不触及任何旧候选、once、余额或原session。

外层只能在准确原工具/worker自然返回后形成返回收据，日志文件存在/JAR产生/isDone/计数0不充分。当前这些新实现和运行顺序均未审未测，只作为新完整冻结B必须核的门。

## 5. 六帧、NAL、CSD和时间基

沿提案固定：H264Encoder.createH264Encoder、keyInterval1、motionSearchRange0，实际DumbRateControl起始QP20且允许其既有调整，不标constantQP。原创YUV420J、256×144，Y整数色块公式及U/V signed0保持；单帧55296 B、六帧331776 B分别计为生成原始像素量，不冒OS文件输入读取或压缩码流大小。只生成六次实际编码输出，非空、每AU≤262144 B、总payload≤1572864 B、实际keyframe标记检查，不伪造NAL或“六帧已有效”。内部编码内存不由这些外部字节上限证明。

原encoder AnnexB原始size/hash必须在mux修改前采集。CodecMP4MuxerTrack按原实现去PS并转换到MOV/AVCC，driver不要再做第二次转换。SPS/PPS/CSD须取实际bytes、hash、数量及表示，总计≤65536 B；不得手填固定golden或只记录压缩后的某个数组而漏原初始化数据。未来Media3提取出的AnnexB可能与encoder原AnnexB因PS变化不同，比较策略先声明，两表示的hash不可直接强等或任意放过。

Packet pts整数0..5、timescale5、duration1产生us PTS0/200000/400000/600000/800000/1000000，结束6/5=1200000us，无需容差舍入。**本JCodec driver应六个媒体Packet后mux.finish，不额外构造第七帧或把Media3空EOS写进JCodec媒体轨。** 后续Media3 E6重封装才沿原约定写0B/flags4 EOS在1200000us、fragment3000ms；两阶段不能混淆。

另有固定源码细节：MP4Muxer.movieHeader使用当前Date。原创像素/PTS确定，不自动证明重复生成整个MP4的字节hash一致；若未来声称文件可逐字节复现，必须另给明确时间戳规则，不能暗改上游。一次实际生成完成后的准确文件hash可以冻结，当前不得预造。源码归属、固定API/时基推导、编码语法实际有效和真实解析duration为不同证据。

本批无.mp4/CSD/实际sample hash，无运行时codec/MediaCodec/FFmpeg/解码或Media3资格化；原fixture阻塞没有因此关闭。

## 6. 一次构建及产物审查判据

新包应冻结真实main/driver源码列表及所有输入pin，准确已有JDK21.0.10 java/javac/jar/release身份、固定argv/工作目录及独立classes，显式无annotation processor（例如-proc:none及无processor path）、无插件/Maven/Gradle/JUnit测试依赖/动态下载或PATH fallback。不能隐式从当前目录/环境classpath带入额外编译实现，也不能用同名假类补缺失类型。静态文本闭包没有代替这项实际编译核验。

coder本批一次固定build、并发1、-J-Xmx512m、输入≤16MiB/所有构建输出≤64MiB；javac与jar各自的原调用、起止/实际返回/输出必须记录，不能只看最终总脚本退出或JAR存在。任何失败保留准确失败源码/receipt集中报告，不按失败反复修建求绿；超过观察窗保管同原编译器，不强杀或盲重试。

新工具JAR逐class与实际编译输出及源列表对应，manifest主类和额外资源明确，许可/SBOM及新driver归属保全；工具不进入App/APK或产品依赖。构建/打包不得附带java -jar、Main、编码类初始化、self-test或生成调用；`jar`写manifest主类只是打包信息，不是运行授权。精确build hash取得后才能交独立B审；当前tester不重复构建或运行类验证。

未来生成命令和工具hash/driver来源、资源预算及无运行门应一次完整列出，但权限仍须后续准确新批次。源码hash、编译产物hash、媒体hash、资格化manifest和产品结果不能相互替代。

## 7. 用例与交接

[independent-driver-oracles.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL01_BUILD_PHASE_A_EVIDENCE/independent-driver-oracles.json) 共FT01–FT28，全部PREPARED_NOT_RUN，覆盖来源/闭包/一次构建/许可/无运行、CREATE_NEW/owner、full-write/attempt/partial/header/异常/0/边界、合成参数/AU/CSD/NAL/时基、原退出/UNKNOWN/清理、hash层次/时间戳以及旧会话和后续门。[future-evidence-contract.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_TOOL01_BUILD_PHASE_A_EVIDENCE/future-evidence-contract.json) 分开构建证据和未来运行证据；新driver/tool/media/CSD hash均留空，非伪造缺省成功值。

本阶段补充三项审查重点：**上游单次write要求driver完整处理短写；完整源树的bundled/逐文件许可归属；当前Date使像素确定不等于整文件hash复现。** 它们是基线准备发现，不是对未读取新driver的缺陷判定，也不回写旧报告。新工具完整冻结由负责人另派B，届时准确判实现/构建/NOT_RUN和集中问题。

原Android01本地UNKNOWN独立保留；本阶段没有查询或处置48945/17257/历史父子PID，不以用户继续推进批准强制收尾或证明host空闲。工具开发可在准确隔离范围继续，原证据不变；强制收尾、工具运行、生成和设备均不得自动进入。

完整阶段A准备已完成，报告/证据发送前冻结，发送回执另存。等待负责人核完整新工具交B；不逐问题打断coder，不读浮动源，不自动编译/运行工具/编码或复用旧scope。D1未过、M0未启。
