# D1 FIXTURE SIX01 生成阶段B独立证据与文件身份复审报告 V1.0

2026-10-21；tester；准确原生成scope D1GEN01-CANDIDATE-001。

## 结论

**PASS_GENERATION_EVIDENCE_AND_FILE_IDENTITY_ONLY**。准确冻结生成包38项、ZIP37唯一成员、完整原收据/原进程与两流返回/原预算和新文件字节身份独立复核一致，未发现本范围内新增缺陷。样本继续为 **GENERATED_CANDIDATE_NOT_QUALIFIED**。实际容器轨道、六sample map、文件CSD/PTS-DTS/实际时长、解码/Media3/隔离格式资格全部未运行；不能签READY、COMMIT、嵌Android或播放许可。

本报告依据 docs/milestones/D1_FIXTURE_SIX01_GENERATE_TESTER_REQUIREMENTS_V1.0.md 末尾正式B范围；在独立checker准备整包报告0e98643827cdb7cef7841965c34bcdc6a039afe5956006bf1f979e8cf0920e73封存发送后顺序执行，未并发编译/媒体运行。此次只运行独立纯Python有限SHA/ZIP/原JSON证据审，不执行coder脚本或helper/JCodec/Main/encoder/decoder/demuxer/设备。旧48945/17257 UNKNOWN未查询干预。D1未过、M0未启。

## 准确冻结交付与复核链

原coder报告 docs/coder/D1_FIXTURE_SIX01_GENERATE_DELIVERY_V1.0.md，9531B，SHA256 **27a370bbb5b39cc0b9c8e81a9ea3a9ec4806f043f21415914e34ab125122ca03**。原seal docs/coder/d1fixture-six01-evidence/fixture-six01-freeze.json，SHA256 **ffd195f62f0fa0f6266ff2683053dd578b35cac8999acc0b747e0ec1c62c86c4**。38个唯一记录逐项实际大小/hash复核，ZIP37唯一成员与记录集合严格相等、逐项解压hash/CRC一致，未增加parser；没有对媒体结构作Python解析。

ZIP docs/coder/D1-20261021-FIXTURE-SIX01-GENERATE-source.zip，293802B，SHA256 a66180ff69e57a96f0a717c99df9bc673ba2165ea63089b1dcc7038939d28d9b。实际只读原媒体 docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4，**8849B，SHA256 19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c**；实际DOS readonly、无symlink/reparse，前后属性一致，hash与原driver EOF回读/manifest/seal/ZIP相同。这只证这次文件身份，不证文件实际轨道/时长/内容正确。

tool02原seal5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d的2774记录全部现值不变。准确生产JAR1954730B SHA256 c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd、固定JDK release/java/javac/jar/modules与reference一致；冻结driver4源文件和许可证逐字节一致。原tool02独立报告4093db...与36证据、阶段A报告b7a58c...与6证据、checker准备报告0e9864...与13证据均按原manifest核不变，没有改旧plan/旧FAIL或重建。

## 原调用、所有收据与原返回

唯一原argv逐项吻合：固定 D:/Android/Android Studio/jbr/bin/java.exe，-Xmx256m，-XX:-UsePerfData，-jar，准确tool02 JAR，--generate-six，--scope=D1GEN01-CANDIDATE-001，无额外flag/fallback/PATH工具。原控制器owner先于preflight/Popen登记；原preflight记录output根不存在、由driver独占新建，原工具/许可快照hash吻合。仅成功准入路径记录和源码顺序一致，不把它说成已运行目录存在或身份错误的拒绝负例。

同一次Popen原返回记录：历史PID8044，2026-10-21T01:10:24.391727+00:00启动，2026-10-21T01:10:24.686044+00:00自然exit0，控制器elapsed约0.281s；原stdout/stderr捕获句柄均在原进程返回后关闭。逐项环境清除JAVA_TOOL_OPTIONS/JDK_JAVA_OPTIONS/_JAVA_OPTIONS/JDK_JAVAC_OPTIONS/CLASSPATH，固定cwd/temp/JAVA_HOME。run_once.py源码只有一次Popen，shell=False；超观察窗分支持有原进程自然等待，不kill/terminate/重试。原Python控制器工具返回exit0的既存toolChunk2913d7回执亦在后封存记录保全。这里审阅原控制器/原工具返回证据，不以当前PID消失或新进程查询冒原返回；没有再次执行或附着原进程。

完整stdout.raw **12297B**、stderr.raw **0B**，严格UTF8全量小于1MiB；逐行重新解析恰好1个final JSON、0pending、0杂行，与all-original-json-receipts和last-original-driver-receipt完全相等。全部原stdout/stderr另存本B证据，没有tail、丢pending或只核最后exit0。原状态GENERATED_CANDIDATE_NOT_QUALIFIED，firstError=null、deadline/admission/unknown为正常终态；receipt超限/超时/重试/强停/二close/退款均无本次事件，不冒故障分支已执行。

原同worker单调body完成点elapsed **152633600ns**，observer152939400ns，低于60000000000ns；start与completed的差重新计算一致。body marker明确是cleanup后最后受控语句，非OS线程退出点；同原Thread实际join、两个资源原close和原Popen自然退出分别有记录。worker deadline/timely、owner.return、EOF/hash、firstError同时成立，结论没有只靠exit0。

## 原资源与逐事件账本

writer/reader均owner-before-open、CLOSE_RETURNED、closeAttempted和sameOriginalCloseReturned=true。writer真实mux.finish、force(true)、size8849、原close返回后才setReadOnly、同一固定新路径只读reader open；reader真实read2次/8849B/EOF1次/原close返回，无reader force。原owner峰1/live0仅辅助，不能代原close/线程/进程返回；force结果也不冒业务COMMIT或普遍持久化保证。

从原nativeOperationEvents重新累计19个常规事件，再加单独terminalClose20：**9 WRITE，7 POSITION，1 SEEK，1 FORCE，1 SIZE，1 CLOSE**。20entered/returns/adoptions相等，最终nativeInFlight0/adoptionPending0/throws0、activeOperation NONE、peak1/queue0，failedOrUncertain/physicalUnknownSticky均false，所有outcome RESULT_ADOPTED。

9次WRITE requested=returned=**8857B**，原累计attempted/acknowledged均8857，初始meter-only0、退款0。每个真实buffer位移与有效returned一致，最大request1340B≤65536；其中最后头部回写8B计入attempt，**实际文件8849B不能替代8857B累计写账**。所有write完整返回，本次未实际跑partial/throw，不能据此扩大FT-B01/B02有限非媒体覆盖。

重新推导最后位置**56**、extent**8849**，与receipt/原SIZE/真实文件大小一致；SEEK回header48后WRITE8，所以position不是EOF，也不能强求position=size。close后的physical scope准确LAST_CONFIRMED_BEFORE_ORIGINAL_CLOSE，没有通过关闭后新FD偷换原position事实。

原inputReserved **340626B** ≤8MiB：内存原创像素331776B + 原只读文件返回8849B + EOF探测预留1B。observed **340625B**=331776+8849；内存像素不能称OS媒体读取，EOF预留也不能计作返回字节。output8857≤16MiB，19常规事件+单close≤512+1，sourceOwnersMax2、原worker1/heap256MiB/per-source1/queue0契约与原源码、argv、收据一致。

## 内部六AU、CSD与时间线的证据上限

六条原rawEncoderAnnexB index0..5，各1360B、总8160B，key/IDR均true，NAL类型7/8/5，NAL字节+各4字节AnnexB前缀总和与1360一致；原hash字段格式、index/Packet输入与manifest逐条一致。**未保留raw AU字节，不能独立重算AU/NAL hash；本B只确认原内部观察记录及其自一致性，不称实际文件AVCC sample hash。** 生成器成熟mux去SPS/PPS与表示转换后，文件sample不能与raw AnnexB简单相等。

三个原mux-track CSD表示为SPS payload7B/PPS payload3B/库转换AnnexB20B，逐个重新解hex并算size/SHA全部吻合，合计30B，rawPS观测累计120B≤64KiB；NAL长度字段4保留来源。此为原收据CSD hex/hash自一致性，不是文件实际avcC重开提取或SPS语法/解码验证。本B没有调用JCodec或自写AVC解析器。

原Packet ptsUnits0..5、timescale5、duration1、ptsUs0..1000000步200000、内部trackDurationUnits6/end1200000相互一致；这些仍是API输入/内部mux观察，**实际文件durationUs、轨道单AVC/零音频/无加密/rotation0、实际sample PTS-DTS均null/NOT_RUN**。未来Media3 E6空EOS1200000us/fragment3000ms属于另批，当前e6EmptyEosWritten=false，无第七payload不能冒未来Remux流程已验。

## GS01–GS24独立逐项结果

下表每项只在证据级别结算；没有把24项统一冒充运行通过，也没有改阶段A原PREPARED_NOT_RUN。失败/超时负例和格式runtime另列NOT_RUN。

| 项目 | 本B结果 | 证据及限制 |
| --- | --- | --- |
| GS01 authority | PASS_EVIDENCE_ONLY | 准确scope/argv/JAR/JDK/原许可快照一致；旧plan不改 |
| GS02 preflight refusal | PASS_NORMAL_PATH_RECORD_NEGATIVE_BRANCH_NOT_RUN | 正常准入原记录吻合；已有目录/身份错误拒绝分支未运行 |
| GS03 source rights | PASS_EVIDENCE_ONLY | 原创像素公式与固定driver/许可证链一致；非专利/发行许可 |
| GS04 original controller | PASS_EVIDENCE_ONLY | 同原Popen及两流/环境清理返回记录与控制器源码吻合，未用PID查询替代 |
| GS05 all raw receipts | PASS_EVIDENCE_ONLY | 原12297B stdout+0 stderr完整审阅，一final零pending零杂行 |
| GS06 body timing | PASS_EVIDENCE_ONLY | 原body152633600ns与实际join/原进程返回分层；超时负例未运行 |
| GS07 successful candidate status | PASS_EVIDENCE_ONLY | 候选状态、firstError/null、timely、EOF/close/join及外部身份全吻合 |
| GS08 pending/failure handling | PASS_NORMAL_PATH_RECORD_NEGATIVE_BRANCH_NOT_RUN | 没有本次pending/超界/异常；负例未运行，不能凭正常返回冒覆盖 |
| GS09 path and ownership | PASS_EVIDENCE_ONLY | 固定新路径、driver独占create与原owner-before-open记录/源码吻合 |
| GS10 writer lifecycle | PASS_EVIDENCE_ONLY | writer实际finish/force/close返回记录齐；不代业务COMMIT或掉电持久化 |
| GS11 reader lifecycle | PASS_EVIDENCE_ONLY | 原只读reader2calls/8849bytes/EOF1/close返回；live0仅辅助 |
| GS12 attempt ledger | PASS_EVIDENCE_ONLY | 9WRITE requested/returned8857含8rewrite；初始预留0退款0；partial分支未运行 |
| GS13 snapshot state | PASS_EVIDENCE_ONLY | 20entered/returned/adopted，inFlight0、uncertain false、close后LAST_CONFIRMED |
| GS14 position extent size | PASS_EVIDENCE_ONLY | position56与extent/真实size8849分层，attempt8857不得以size代替 |
| GS15 budgets | PASS_EVIDENCE_ONLY | inputReserved340626/observed340625含像素331776/文件8849/EOF预留1；外读另账 |
| GS16 raw six AU | PASS_INTERNAL_OBSERVATION_RECORD_RAW_HASH_NOT_RECOMPUTED | 六AU各1360总8160/IDR/key/NAL仅原内部观察；缺raw bytes不能重算hash |
| GS17 CSD NAL | PASS_RECEIPT_CSD_SELF_CONSISTENCY_ONLY | CSD三表示7/3/20B hex/hash自一致通过，非文件提取；raw PS120B |
| GS18 timebase | PASS_INTERNAL_TIMEBASE_RECORD_FILE_TIMELINE_NOT_RUN | Packet单位0..5/scale5/duration1、内部duration6吻合；真实文件时长未查 |
| GS19 whole file identity | PASS_EVIDENCE_ONLY | 实际媒体8849B/准确SHA/只读属性与原EOF/hash一致，仅身份 |
| GS20 actual evidence limitations | PASS_LIMITATION_DISCLOSURE_CONTAINER_NOT_RUN | 真实轨道/sample/PTS-DTS/duration/CSD独立提取全部null/NOT_RUN |
| GS21 date nondeterminism | PASS_EVIDENCE_ONLY | 原成熟库Date保留，仅冻结本次hash，不保证重生成hash |
| GS22 immutable chain | PASS_EVIDENCE_ONLY | seal38/ZIP37、tool2774、原报告/阶段A/准备证据均原样；新增B另封存 |
| GS23 old UNKNOWN | PASS_EVIDENCE_ONLY | 旧48945/17257 UNKNOWN未查询或干预；不证明host全空闲 |
| GS24 next qualification gate | PASS_EVIDENCE_ONLY | 本B只Python证据/身份；helper编译已另封存，实际运行/Android另准确批 |

## 来源、外部读量与集中交接

内容来自固定项目driver的原创YUV420J公式，六帧256×144，Y unsigned16+16*((x/16+y/16+i)%14)再转signed减128，U/V signed0；固定source/既有权属声明与版权许可一致，无原BBB/其他媒体、音频、字体、商标或decoder输入。保留FreeBSD、JAAD Public Domain与FreeBSD变更、Guava Apache2；本测试不授专利/商业发行或FFmpeg许可。成熟库Date未改，仅冻结本次实际文件，不许诺重生成同hash，也未为目标hash重复生成。

本B媒体逻辑应用读单列：原媒体seal逐项hash8849B + 终审保全hash8849B=**17698B**；ZIP媒体成员hash/自动CRC同一读取**8849B**，没有另做testzip重复读取。上述不混入原driver340626预算，控制元数据/JDK/tool身份读也另类。coder原seal外读原媒体35396B/归档媒体17698B、其postfreeze另读原媒体8849B/归档17698B均保留历史口径，不据此推算其他窗口或物理磁盘IO总量；负责人外读不混成本B账本。没有因是同文件把多次真实读去重。

本范围无新增缺陷；**实际容器资格仍是明确未执行门**，不是用生成证据补绿。下一准确单次容器检查须负责人结合本B与已冻结helper源码/class/JAR/JDK/schema重新绑定准确输入和scope后派发；本B没有自动启动helper、decoder/Media3、设备、READY/COMMIT或后续测试。报告及本B证据冻结后立即发负责人，原报告与coder冻结文件不修改。
