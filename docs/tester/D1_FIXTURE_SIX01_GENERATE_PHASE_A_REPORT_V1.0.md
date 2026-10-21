# D1_FIXTURE_SIX01_GENERATE 阶段A准备报告 V1.0

日期：2026-10-21。测试人：tester。接收人：负责人01a107c3-2bf9-7fa0-94a0-234258ca6774。

## 1. 结论与当前边界

**PHASE_A_GENERATION_RECEIPT_ORACLES_PREPARED。** 已对冻结tool02和本批准确要求完成核对，准备24项生成收据/工具→文件→raw AU/CSD/时基/权属链检查判据、结果证据合同及分层裁定规则。全部GS01–GS24为PREPARED_NOT_RUN。

新要求已另行批准**coder一次固定生成**；本窗口tester仅阶段A准备，未运行工具、重生成、编译、打开新结果或查询新输出是否存在。对coder当前实际生成进度/结果不作推断。原报告、工具包保持冻结；旧48945/17257 UNKNOWN不轮询/attach/处置，不由独立生成推出host空闲或原强制收尾批准。

本阶段不使用新解析器、demuxer、Media3、编码器或设备；D1未过、M0未启。完整产物冻结后由负责人另派B，B只审生成证据和文件身份，真实成熟框架重开/Media3资格另批。

依据 [本批测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_FIXTURE_SIX01_GENERATE_TESTER_REQUIREMENTS_V1.0.md)。

## 2. 准确授权和工具来源

|对象|阶段A核对|
|---|---|
|唯一scope|D1GEN01-CANDIDATE-001|
|工具JAR|1954730 B；c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd|
|tool02 seal|5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d|
|原独立报告|4093db865bf0ed1419245c94a3102578835ce57ecd750da6010645a314176fb4|
|原独立证据manifest|4cf38051ed21b927da639418ef9ef58629219fbe042645f46b0ccf946c900109；36项保持|
|已有运行环境|固定JDK identity中java.exe/release/modules大小/hash与当前原文件一致；不启动Java查询版本|

准确未来执行argv为：

```text
D:/Android/Android Studio/jbr/bin/java.exe
-Xmx256m
-XX:-UsePerfData
-jar
D:/CodexProjects/VideoKit/docs/coder/d1fixture-tool02/artifacts/videokit-fixture-tool02.jar
--generate-six
--scope=D1GEN01-CANDIDATE-001
```

这是本批coder获准的一次准确调用说明，**本阶段没有执行该命令**。与冻结generation-plan02的参数规范化核对相同；实际许可来自本批新要求，不来自scope字符串。原plan里的generationAuthorized=false记录当时状态，不能改写旧文件，也不能误用旧字段否定本次明确新许可或批准其他调用。原FT-B01/B02仅指定非媒体契约有限关闭，不扩大为真实生成已通过。

只允许固定新文件 `D:/CodexProjects/VideoKit/docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4`；ROOT/new-output由driver独占创建，控制器不能预建，已有目录/身份不符则调用0并报阻塞，不删改或换scope重试。外置控制证据目录与driver路径分开。本阶段未查询或读取这些浮动路径。

来源、准确参数和权限角色见 [authority-and-baseline.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_SIX01_GENERATE_PHASE_A_EVIDENCE/authority-and-baseline.json)。

## 3. 收据完整性与原返回判据

未来B必须首先保全原控制器的准确argv/cwd/env及清除注入项、同一次原Popen/流handle登记、起止和自然返回事实。进程自然exit0不能独立证明生成成功，原工具日志或JAR身份也不等媒体有效。

stdout/stderr原字节及**所有pending/final JSON**须保存，其他非JSON输出也分类记录，不能只取最后一行或tail丢掉pending/异常。receipt UTF8总量≤1MiB须累计，不把每行各≤1MiB冒全量合格；超额停止后续审定，仍持有原进程/管道，不强关、截断成成功或重生成。控制器记录/复核I/O另列，不冒原输入8MiB已覆盖所有后续读取。

候选成功至少同时满足：最终GENERATED_CANDIDATE_NOT_QUALIFIED、firstError=null、没有此前pending/期限UNKNOWN被抹掉，deadlineUnknownSticky=false、同原完成点timely且同原实际join、body cleanup和原资源返回、mux.finish返回、writer原force/close、只读reader原EOF/hash/close、原进程及外层流自然归还。输出形状、语义或原返回不足则保留准确失败/UNKNOWN，不用exit0补PASS。

单调body完成点是同原worker在cleanup后的最后受控语句，不是OS线程退出时间戳。完成及时、observer晚采样可按已审契约判及时；等号算迟返，真正迟返/已观察期限/无效半区间/倒退/显式UNKNOWN保持sticky。marker不能代外部同Thread.join，join又不能代原FD/force/close。旧有限非媒体测试结果不回填成这些平台事实。

## 4. 计量、位置和生命周期核对

沿原准确预算：heap256MiB、worker1、两个原owner/每源inflight1/queue0，input累计8MiB、output attempt16MiB、原块65536 B，每AU262144 B/六AU1572864 B、CSD65536 B、512常规操作事件+一个终态close记录。

原生产initialMeterOnlyReservation应为0。未来B从原事件独立求和WRITE requested/reserved及有效返回，与attempt/ack下界/无退款对应；metadata position/size/force等request0不冒载荷，partial剩余请求与header回写分别收费。成功终态须无native/adoption在途、无异常/物理UNKNOWN；所有已进入返回/采纳事实相符。不要求原nativeCalls等于“写调用数”，因为它包括metadata及close。

**最终logicalPosition可能停在被回写的header，而不是EOF。** 独立文件大小应与实际file-size/extent事实比较，不强求position==size，不以最终文件长度代累计attempt。adopted close后的物理字段scope只是LAST_CONFIRMED_BEFORE_ORIGINAL_CLOSE，不是关闭后新测量FD。pending时实际物理值UNKNOWN与lastAcknowledged必须分栏。

writer在mux构造/header写之前已登记，原finish/force/单close分别核；reader只能在原writer已关闭后只读打开同一输出，原完整EOF/hash及其close独立。nativeOwnersLive=0或receipt内计数0不能单独证明原返回，峰值按实际≤2检查，不预填必须为某个数。

输入账还须区分原创raw像素331776 B与实际文件读取/EOF探测，不能将程序内像素量写成原媒体OS读取。任何追加Python hash/保存/复制都属于后续审计量，不倒算进原generator账，不退款或冲销旧未知。

## 5. 工具→raw AU/CSD/时基→文件的证据层次

原内容是项目原创YUV420J、256×144六帧，固定整数色块，U/V signed0；无BBB/其他媒体/音频/字体/标志/解码输入。source/build/compiler身份、FreeBSD/JAAD/Guava归属及自有driver来源沿已审材料保留，不增加商业/专利/旧FFmpeg清权。

未来收据须有六个实际raw encoder AnnexB AU：index0..5、真实非空size/总量、isKeyframe/实际IDR、raw hash和NAL观察；CSD区分原SPS/PPS payload与库转换AnnexB的hex/size/hash/数量/表示，聚合不超64KiB。CodecMP4MuxerTrack内部转换AVCC一次，不能双转或强等不同表示hash。

这些仍是准确工具的内部观察。只记录raw-AU hash而没有原AU字节时，B不能独立重新计算该hash；也不能不经demux就将raw-AU hash当文件容器AU hash。CSD内部对象来自mux track，不是从封存文件独立重开取得。JSON内hex与自报hash可核相互一致，但不升级其来源层次。

Packet pts0..5/timescale5/duration1给出声明PTS0..1000000us、结束1200000us；原工具trackDurationUnits=6只是内部观察，不是独立文件duration。JCodec六Packet+finish不能混同后续Media3 E6空EOS flags4/fragment3000ms；不得加第七媒体帧补时长。原MovieHeader Date保持，确定像素/PTS不承诺每次全片hash相同，不能重生成求目标hash。

完整结果冻结后，B可在准确文件范围以已有Python做有限大小/hash核对，比较原receipt、controller、manifest、seal；保全真实一次产物身份。**整文件hash一致仅证明这些字节一致，不证明单轨无音频加密/rotation0、AVC语法、帧数、容器AU/CSD/PTS/duration或解码正确。** 独立成熟框架重开/Media3资格尚需准确新批次，不新增自写parser/demuxer求绿。

## 6. 24项准备与后续交接

[independent-gs01-gs24-oracles.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_SIX01_GENERATE_PHASE_A_EVIDENCE/independent-gs01-gs24-oracles.json) 共24项，全部PREPARED_NOT_RUN，覆盖权限/准确命令/拒绝前提、权属及原控制器、所有收据/期限/状态、路径/原writer-reader、attempt/snapshot/position/预算、raw AU/CSD/NAL/时基、有限文件身份、Date差异、不可变链及旧UNKNOWN/后续资格门。

[receipt-and-identity-contract.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_SIX01_GENERATE_PHASE_A_EVIDENCE/receipt-and-identity-contract.json) 给出未来应核字段和计量口径。字段中的期望成功值是oracle，**不是实际生成收据**；未来文件bytes/hash/独立容器samples及duration均留空、未读取。[result-classification.json](D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_SIX01_GENERATE_PHASE_A_EVIDENCE/result-classification.json) 分开本tester准备、coder一次生成、正式B证据审查、后续真实资格化四层，不把本窗口未执行误称coder未执行。

本阶段准备完成，报告及证据发送前冻结，回执外存。等待负责人核完整新产物后另派B，不读浮动结果、不同时运行工具或重生成。失败/UNKNOWN也完整停批报告，不改工具、不删除未知目录、不换scope、不强停/二close/退款。旧48945/17257及历史FAIL/P0保持；B不自动加载新demuxer/Media3/编码器或设备，不签HOST_ISOLATED_FORMAT_V1/READY/COMMIT/播放，D1未过、M0未启。
