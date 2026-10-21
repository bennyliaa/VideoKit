# D1_MEDIA3_CONTAINER01 阶段 A 冻结基线与独立用例报告 V1.0

2026-10-21；tester；仅阶段A。

**结论：BASELINE_REVIEW_COMPLETE_WITH_GAPS。** 已完成INPUT_SINK05冻结来源核验、14个真实接口静态审证、5项原E6拒绝边界实际检查，以及32项可用于阶段B的独立用例。当前已准入muxer的实际JDK构造在 `android.util.SparseArray` 处受平台链接限制；封存extractor/decoder有准确pin，但其本批运行使用准入和合格编码fixture尚不在阶段A证据中。此为基线能力/准备缺口，不是对开发中新候选作FAIL。

**新D1_MEDIA3_CONTAINER01实现没有测试，阶段B没有启动。** 没有读取coder新浮动目录，没有Gradle/共享缓存写入、SDK/ADB/5037/设备/占用/旧handle查询或网络取证。D1仍NOT_PASSED、M0仍NOT_STARTED；真实提取/媒体容器结构重开、隔离内容、READY/COMMIT和播放没有因此通过。

## 1. 来源身份与实际执行范围

按 [测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_MEDIA3_CONTAINER01_TESTER_REQUIREMENTS_V1.0.md) 及协调文档顶部派发，只读取冻结 `docs/coder/d1input-sink05`、其封存库及既有要求文档。没有枚举、读取或执行新容器候选目录。

| 来源 | 独立核验 |
|---|---|
| INPUT_SINK05独立报告 | SHA256 `6cd4621901dddcc9ad7d11ddca4248eaac2a1ae7e45513ca257a35055f1b6973`，保持有限离线PASS |
| 原主报告 | `25503fe0f72310db4b22eeb23875fbdc17f782092ebd4e0bf132baf2fb3f82a7` |
| 原seal | `ec7e5e9a8f38d2d1fe531592117f5db0a6d3481cd3ff89536d985f9dae173d96`；828项逐项hash一致 |
| 原最终输入 | 1,037条源/封存依赖输入逐项hash一致，包括下列AAR/module |
| 生产JAR | `6fbf307a4f0a06f45606ad9a162fcad95330924c2f220b5f68cec1e851916b0b`，运行probe优先加载此JAR |

source pins和所读准确源码副本见 [source-pins.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/source-pins.json)。新的编译、静态提取classes.jar、日志和回执仅写tester阶段A目录；没有重跑无变化的INPUT_SINK05整套50项入口。

已有JDK实际执行：五个无效E6参数组合均返回 `E6_MUX_INCOMPLETE`；真实已准入E6→FragmentedMp4Muxer构造尝试遇到NoClassDefFoundError。probe未提供AVC样本、未添加轨道、未生成媒体fixture；emittedBytes=0、host write0、原host close1、READY0、COMMIT未调用，原Sink/coordinator线程归还，source/output keeper0。见 [probe-runtime.stdout](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/probe-runtime.stdout) 和 [参数/退出回执](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/probe-runtime.json)。

14个类通过JDK javap读取真实封存字节码/公开常量，目标库不实例化；另静态审 muxer字节码。没有定义同名Media3接口或以自写容器解析器代替成熟框架。

## 2. 真实接口与后续接线判据

实际1.9.3 ABI确认：

- HostDataSource真实实现DataSource/DataReader，可接 `DefaultExtractorInput(DataReader, long position, long streamLength)`，而不是绕回SDK路径或网络读取。
- Extractor真实生命周期为sniff/init/read/seek/release；read结果CONTINUE=0、SEEK=1、END_OF_INPUT=-1，SEEK通过PositionHolder的long字节position表达。不能把byte position与seek的timeUs混同。
- ExtractorOutput/TrackOutput提供track、format、seekMap、sampleData、sampleMetadata；独立观察必须汇总实际分段sampleData及metadata的timeUs/flags/size/offset，不只记录“sniff=true”。seek根据该真实SeekMap和随机访问点核验，不能假定目标时间就是返回首帧时间。
- 已封存真实 `Mp4Extractor`、`FragmentedMp4Extractor` 类存在；源码/产物来源应在新包实际ORIGIN和依赖准入后再次证明。阶段A未运行它们。
- 实际FragmentedMp4Muxer支持WritableByteChannel builder、addTrack、writeSampleData、close；BufferInfo只有presentationTimeUs/size/flags。冻结库构造使用 `AnnexBToAvccConverter.DEFAULT`，因此样本NAL表示和codec initialization data必须事先声明，不能拿原容器文件hash相等作remux正确性判据。

对应原始接口输出：[Extractor](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/abi-02.stdout)、[DefaultExtractorInput](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/abi-04.stdout)、[TrackOutput](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/abi-06.stdout)、[Muxer](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/abi-11.stdout)。

新链路应证明：实际host readAt→原DataSource→真实Extractor→有界轨道/样本观察；随后真实成熟muxer→原临时Sink→原writer/任务返回→授予的只读Provider→真实Extractor重开。提取器release不等于DataSource/registry线程归还，muxer close也不等于宿主FD/fsync或业务COMMIT。

## 3. 四项基线缺口与进入阶段B的条件

### A-G01：现有最小JDK环境不能直接构造真实muxer

实际结果为 `NoClassDefFoundError: android/util/SparseArray`，original muxer未构造，无输出字节。已有05仅包含明确JVM URI/errno/WorkerRule端口，没有该平台类。该结果只证明这一次真实调用首先受此链接限制，不能声称补一个类就保证完整链路可运行。

新包应明确实际运行环境、所需平台条件和所有测试端口；若只能在明确主机端口环境运行真实库算法/结构，证据也只能命名为该主机结构检查。不能用同名假Media3类或虚构平台效果求绿；无法执行的真实Android路径继续NOT_RUN。本阶段不修改平台端口、添加替身或启动设备。

### A-G02：extractor/decoder封存身份可核，本批新增运行准入仍需材料

| 固定库 | AAR SHA256 | 当前阶段A处置 |
|---|---|---|
| media3-extractor1.9.3 | `fb1d260cea679efd3568b4b4b02c9aa1dd84cef847cd50f93f50ca02e59cb20b` | 仅静态ABI；不在05的15runtime坐标内 |
| media3-decoder1.9.3 | `2337461b4ed4ec3cd32330cd530d9b471d5d45b76410f6e0d66f1331c9a0bc08` | 仅静态审证；新增运行准入待证 |

两者AAR/module均与原verification pin及1,037输入清单一致，module声明的AAR hash也一致；静态提取classes.jar另存准确hash。冻结镜像相应目录没有POM，AAR未带可直接采用的LICENSE/NOTICE条目；当前阶段材料不能据此独立补成新运行范围的来源/许可准入。这里不否定已有项目历史许可，只说明本阶段没有该新增使用闭包的完整证明。

阶段B前需新包保全固定官方POM/module、适用许可/传递依赖差异、strict锁/metadata实际消费及独立准入。无需升级、不新增pin求绿；未经相应来源准入不执行新增artifact。本轮未联网、未运行extractor/decoder代码。详见 [sealed-library-identities.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/sealed-library-identities.json)。

### A-G03：阶段A没有合格编码fixture，不能用4B或伪NAL冒充

冻结05的生成4B文件不是媒体；阶段A允许材料中未提供可资格化的六样本AVCfixture。本轮未打开项目其他路径的只读sample.mp4，也未生成、下载或读取新的媒体字节；没有编造fixture hash。

验收manifest至少记录权属/许可、来源或已准入生成工具及版本/参数/许可、原文件hash/大小、轨道/AVC参数、SPS/PPS等初始化数据、每样本大小/已声明NAL表示下的hash/keyframe/PTS、时基及duration规则。候选只支持单AVC256×144、rotation0、无加密，原输入≤8MiB；不能为适配不符sample而扩范围。

建议正例可用项目自有合成内容、由已经准入工具合法编码，六个样本PTS为0/200000/400000/600000/800000/1000000us；这是**未生成的用例参数建议**，不是实际有效压缩数据或新编码器授权。只读已有sample如不符或权属未证，应明确fixture阻塞，不能伪造NAL或自动运行新FFmpeg/编码工具。见 [fixture-acceptance.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/fixture-acceptance.json)。

### A-G04：结构、EOS、EOF/hash的oracle须分开

冻结MatureMuxerBinding限制最多6个样本、PTS0..2000000且严格递增、单样本≤262144；**E6.finish要求恰好6个payload样本**，5或7不能完成。原fragment duration为3000ms；最后写0B、flags4的EOS，其PTS=last+200000，不是第七个媒体帧。

实际执行五个E6前置拒绝：track=-1、count5、count7、last=-1、last=2000001均通过。未用null muxer调用合法完成分支，也未构造有效媒体。若last=2000000，EOS时间为2200000：入参PTS≤2秒与最终容器结束时间不是同一断言。若新批宣称总duration≤2秒，必须用合格fixture及真实重提取/时基规则另证，不能静默把范围扩为2.2秒。建议上述正例EOS为1200000us。

Extractor的END_OF_INPUT不自动证明底层全字节EOF/hash；sniff成功更不证明完整容器。需独立记录整个有界原流的实际EOF、总字节/hash，以及成熟Extractor观察到的轨道/样本/PTS。合法尾随box与坏尾数据按预先声明策略处理，不能只见parser停止就称全源已验证。

seek重开还需明确绝对byte position与允许流终点：DataSource.open返回的已知剩余长度不能不加区分地当作从0起的绝对streamLength；unknown保持unknown，受限range、原epoch/sourceVersion和long溢出前拒绝保持。NAL前缀/时基转换有合法变化，只有预先声明相同表示/重标规则后才比较样本hash/PTS，不能任意容忍差异或把结构成功称为解码内容成功。

## 4. 三十二项独立用例准备

完整可复用清单：[independent-cases.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/independent-cases.json)，共32项，状态是阶段B正式冻结及准入后的待执行，不登记新实现PASS。

| 用例 | 主要覆盖 |
|---|---|
| MC01–MC04 | 真依赖来源/许可/消费、fixture资格、参数/权属、能力拒绝先于open/write |
| MC05–MC10 | 真普通/fragmented MP4提取、短读、未知长度、peek/sniff、实际SeekMap/RESULT_SEEK |
| MC11–MC16 | long/范围溢出、损坏/截断、非法host count/权限脱敏、取消迟返、原close、底层全EOF/hash |
| MC17–MC22 | 原track门、样本大小/ByteBuffer、恰6样本/EOS、PTS/时基、NAL表示、真实muxer→Sink |
| MC23–MC26 | partial UNKNOWN、8MiB/16MiB/64KiB/两源预算、flush/close失败、writer真实返后只读reopen |
| MC27–MC30 | 真结构重开与错轨道/样本/摘要、原source/registry、response/observer/SDK worker返回门 |
| MC31–MC32 | 主机结构结果不能签发HOST_ISOLATED_FORMAT_V1/READY/COMMIT/播放，平台隔离真实路径单列 |

phaseB的结构正例应至少核单AVC256×144/rotation/config、六个媒体样本、已声明时基下的PTS与EOS duration，读回前原writer确已返回，读后原source/observer/线程确已返回。partial故障保持physical10/ACK下界3/caller3/UNKNOWN，首错不清、不回退重发退款；坏响应不是“宿主没有副作用”的证明。

既有05每源在途1/排队0、总源2和output16MiB仍有效。原输入提取和输出读回占用两源时不能额外创建第三源，seek不能通过不断新factory绕过旧epoch原归还。真实Extractor.release、producer channel close、host writer close、原registry/worker返回及业务终态分别留证。

## 5. 不可越过的结果分层与下一交接

阶段A的PASS项只有冻结身份/静态接口和五个E6拒绝边界；真实muxer构造记HOST_PLATFORM_LINKAGE_BLOCKED，真实提取、编码fixture、muxer输出结构重开为NOT_RUN。没有修改/重测全部INPUT_SINK05实现，没有对新候选作验收。

未来主机结构检查即使成功，也应独立命名为host structure result。不得把它包装成 `HOST_ISOLATED_FORMAT_V1`，不得据此调用产品READY/COMMIT或发布播放PASS；原隔离CPU/slot/death/source/内容/timeline前置保持。阶段A probe READY0/COMMIT未调用，host内存sink关闭1次、原coordinator实际归还，所有JDK子进程及管道返回，无设备资源。

完整证据：[D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE)。既有D1/P0/J11、历史FAIL/UNKNOWN、有限真机PASS及FFmpeg/release/model/media许可等边界保持，不因本准备工作增减。

请负责人审阅本阶段A整批报告和32项清单；coder完成真实功能簇及来源/fixture/环境材料并冻结后，再由负责人另派阶段B。当前不进入B、不逐问题打断coder，不自动设备测试/M0。报告主动发送负责人，通知失败保留并停在准确失败事实，不绕过发送渠道。
