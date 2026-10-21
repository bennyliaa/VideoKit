# D1_MEDIA3_ANDROID01_READY 阶段A准备报告 V1.0

日期：2026-10-21。测试人：tester。接收人：负责人01a107c3-2bf9-7fa0-94a0-234258ca6774。

## 1. 结论

**PHASE_A_ORACLES_PREPARED_WITH_FIXTURE_AND_EXECUTION_GAPS。** 已完成冻结02及既有已审Android基线静态核对，形成24项独立检查判据、结果证据合同和完整素材生成方案审查清单。当前没有资格化的单AVC256×144六样本编码fixture，mux正例保持FIXTURE_BLOCKED；批准原片的真实Android普通MP4提取观察可按新冻结及后续准确批次准备，未因JDK缺平台类停止准备工作。

本报告是阶段A准备结果，**不是新实现验收、Android执行或素材生成许可**。本阶段未读 `docs/coder/d1media3-android01` 新浮动源码，未运行JVM旧套件/Gradle/SDK/ADB/设备占用查询，无编码、转码、解码、播放、音量或ordinary isolated codec/GPU探针。仅检查既有冻结文件、材料清单和批准原片大小/hash；不读取其他媒体payload。D1未过、M0未启，历史FAIL/UNKNOWN/P0/J11门保持。

## 2. 依据和准确基线

依据 [正式阶段A测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_MEDIA3_ANDROID01_READY_TESTER_REQUIREMENTS_V1.0.md) 和负责人派发，仅使用以下已审基线：

|基线|本次核对与可继承范围|
|---|---|
|MEDIA3_CONTAINER02|seal `0bff92319ac4ec9130574db358f644c35d99f145a75fdaf2b3f7b4521f4ae06d`，676项逐项大小/hash保持；真实Media31.9.3接口、原输入/Sink、预算和准入修复来源|
|02独立报告|`e857e11a919475562587ff300223472076e8c190388f838e61a8417fecd46649`保持；MC-B01只在实际检查开始前准入/原归还范围关闭，不继承容器功能PASS|
|RENDER02已审实验基线|seal `a226b5fe0703d31c486ec2deaad1c2f2241169f4c8257701331cd5d9c1a83581`，404项逐项大小/hash保持；参考instrumentation精确方法/参数校验、原owner保管和空测试包身份审查经验|
|既有Android/采集报告|审阅RENDER02离线、CAPTURE_ADAPT及DEVICE_V2报告；旧25串行采集角色及原资源闭合只作机制参考，旧scope/预算/activation不能复用|
|C13历史报告|原普通隔离AVC configure失败、管线未进入后续阶段及旧FAIL保持；不以换测试包/UID重标旧结果，也不重跑已知不可用探针|

本阶段没有把RENDER02的Activity、音频、CPU/native或ordinary isolated service移作新容器测试必需项。其源码存在这些端点，不代表本新批获准使用。历史DEVICE_V2占用结果仅是历史，未用它判断当前设备空闲或忙，也未轮询设备。

来源及准确文件hash见 [baseline-identity.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_A_EVIDENCE/baseline-identity.json)。本次没有重复02已完成的28/8或60条检查；新实现待完整冻结后才审。

## 3. 批准原片及资格化fixture判据

批准原片为 `test_media/imgs_and_videos/videos/sample.mp4`，349102 B，SHA-256 `720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9`，本次只读核对一致。原项目manifest声明320×180、H.264/AAC、8秒、isom；权利记录为 Big Buck Bunny (2008)、Blender Foundation、CC BY 3.0，且明确是00:30–00:38节选及重编码派生物，不能写成原始未修改下载。来源、署名与修改记录沿用原manifest，不因复制到私有目录省略。

有限核manifest中8个既有视频条目的**声明**，均320×180、含音频、约8秒，未发现可资格化的单AVC256×144六样本记录。仅sample.mp4是本新Android提取观察的批准输入；没有打开其他7个媒体payload，没有把MKV/MOV/M4V等自动加入本批，也未搜索无关目录或假定机器其他文件不存在。

原片只能准备普通MP4实际读取/提取观察，不能进入capture/remux六样本门。原manifest的历史decode_validation=PASS不是本批解码证据；本次没有观测真实轨道ID、样本数、PTS、CSD或NAL。不能预填这些数值求一致。

未来写入正例必须同时具备：单 `video/avc`、256×144、rotation0、无音频/加密/DRM；恰6个真实access unit；非空初始化数据总量≤65536 B；每样本1..262144 B；首样本keyframe；声明PTS为0/200000/400000/600000/800000/1000000 us及时基、NAL表示、逐样本大小/hash/flags；来源/权利、工具版本/参数和原输出整体大小/hash可核。任一资格缺失须在实际muxer创建/写入前明确FIXTURE_BLOCKED，actual writes=0，不能把跳过写成成功。

见 [fixture-qualification.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_A_EVIDENCE/fixture-qualification.json)。本阶段未创建新媒体，也未改写原片。

## 4. 可复用的实际接口和oracle

已从冻结02源码核实际链：授权原Provider/readAt→真实HostDataSource→真实DefaultExtractorInput→Mp4Extractor或FragmentedMp4Extractor→TrackOutput格式及样本观察；写入链仍为原MatureMuxerBinding/E6→TemporaryOutput→原writer归还→原只读Provider→真实结构检查。AndroidInput以真实Looper拒绝主线程I/O，SDK无路径/网络源fallback；新候选必须保留此边界。

**以下是冻结库API参数判据，不是已存在的新Android方法或设备命令。** 新候选实际测试类、方法、runner、scope参数、精确包/进程、期限及输出上限当前均未绑定；阶段B必须从新冻结产物核定，设备执行再由负责人另派。

|角色|拟定实际库参数|独立结果判据|
|---|---|---|
|普通MP4观察|container=MP4，capability=true，seekUs=-1，capture=false|实际库进入解析、endTracks、轨道/样本/PTS及parser EOF单列；原片完整349102 B/hash/底层EOF独立记录；不写muxer|
|短读/未知长度观察|同一精确良性字节，host chunk=3或length=null/-1，其余参数同上|相同表示下的格式/CSD、样本数、逐样本size/PTS/flags/hash与同片正常读取观察一致；unknown不猜长度，短读不当EOF|
|sniff/peek/reset|同片、真实ExtractorInput peek与reset后实际解析|逻辑位置和peek位置分开；无重复/丢失字节；sniff成功不等完整结构有效|
|真实seek观察|container=MP4、seekUs=1000000、capture=false，仅实际SeekMap及duration支持时准入|记录真实map第一点/byte position/timeUs、RESULT_SEEK与新epoch；已知end=position+remaining，unknown=-1；不猜随机位置，也不把首帧必须恰好1秒作为断言|
|六样本capture|仅资格化fixture、真实容器种类、seekUs=-1、capture=true|捕获真实编码样本及CSD；原片不符必须在mux创建/写入前拒绝；不伪NAL或4B样本|
|mux→fMP4重开|资格通过后调用原writeAndInspect链|真实mux写恰6 payload，原返回后用真实FragmentedMp4Extractor重开；格式、CSD、sample count/size/PTS/hash按预声明表示比较|

原片声明支持预期观察为AVC视频和AAC音频、视频320×180，但准确轨道ID、每轨样本数、时间线/CSD/NAL和实际duration未知。首次真实观察须留原始有界证据，不能使用同一解析器的自报结果伪造外部golden manifest。正常/短读/未知长度之间一致只证明该受限链路稳定；即使结构通过也不等解码或内容验证。若实际合法原片遇当前端口限制或断言失败，保留准确失败/不支持阶段，不静默放宽MIME/时间/计数门。

seekReplaySamples>0或extractorSeeks计数不能替代实际map点、原偏移及sample观察。冻结02 Evidence并未完整暴露逐次seek轨迹；新Android测试证据须补足准确已发生信息，若新包未提供则阶段B记录证据缺口，不能只看绿色测试名。阶段A不修改产品接口。

## 5. EOS、时间及字节比较

冻结E6 fragment duration=3000ms，finish恰6 payload，随后0 B flags4 EOS在lastPTS+200000，然后调用原muxer close；EOS不是第7帧。上述正例最后PTS=1000000、EOS=1200000 us；真实容器最终duration应按新冻结的实际时基及舍入规则验证，不用PTS上限2000000代替duration断言。

冻结MatureContainerRemux采用相同库提取后的Annex-B样本、精确CSD数组及整数微秒PTS做保守比较。新候选若引入AVCC/Annex-B表示转换或不同时间基，必须在执行前给出明确转换及允许舍入的数值规则；不能事后加容差解释差异。逐样本压缩字节一致与源/输出容器整体hash一致是不同断言；重封装后的整个文件hash通常无需等于输入，但输出自身全EOF/hash仍必须可核。以上均不证明像素解码、同步或播放效果。

原流的全EOF/字节/hash与Extractor.RESULT_END_OF_INPUT必须分栏。合法精确hash原片是本批唯一观察输入，不制作损坏atom、恶意尾部、巨量声明、OOM、崩溃、卡死或hang注入；此类原功能用例继续NOT_RUN。本阶段不以准备oracle授权新负载。

## 6. 预算、原归还和停止证据

沿用输入8MiB累计、输出16MiB、原I/O块65536 B、全局源2/每源在途1/queue0。输入累计应包含同次hash、sniff/peek实际底层读取、解析和所有seek/重读，不在重开时清零；多观察方法/输入与输出结构读的实际数分别列明，由准确新scope限定，不拿单个Reader计数冒整个批次消费。输出预算包含容器开销，16MiB写预算不解除结构读取8MiB的既有限制。

冻结02另有max2轨、每轨512样本、单样本262144、4096 extractor steps、16 position changes、1024 replay samples等有限门。六样本总payload至多1572864 B、CSD≤65536 B仍不能推断实际容器总大小或内部峰值；Media3内部原生/平台内存不由外部字节门证明。只用良性精确hash样本，不以“同UID空沙箱”假装恶意输入隔离。

必须分别记录：同原读Provider/handle及sourceVersion/epoch，DataSource/registry/原worker、真实observer和caller线程返回，Extractor.release，实际writer flush/fsync（若声称）/close及回调返回，输出只读重开，以及最终owner keeper。方法返回、ACK、计数0、超时、进程消失或instrumentation结束均不单独证明这些原对象归还。

超时/失败停止后继准入，首错及UNKNOWN保留，仍在途原owner强保管；不强停/kill、二close、替代任务补ACK、退款或自动重试。不使用旧N2/RENDER停止scope或旧余额。后续设备批次必须新鲜核准确设备/空闲、精确operation及文本/二进制/出站输入/控制/proof/外层开销和原工具自然返回；本阶段这些预算字段保持未绑定，不复制旧32操作/4MiB/16MiB为新许可。

完整结果字段分组见 [evidence-contract.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_A_EVIDENCE/evidence-contract.json)。新包须冻结单方法期限和receipt上限；观察窗结束只能停止准入，不能宣布归还。

## 7. 生成方案审查清单

当前没有具体已审生成方案，准确工具/版本/组件/hash、输入/新输出、命令或API序列均为未绑定，**不运行MediaCodec、FFmpeg或新编码/转码工具**。阶段A交付的是可一次性审阅coder完整方案的清单，不能填写虚构版本或“自动选择可用编码器”。

完整方案至少同时提交：

1. 精确工具名称/版本/构建hash及官方来源/适用许可/传递和native差异；如未来提议Android编码器，记录准确codec组件、系统build/API及版本依据、完整API调用顺序和参数，不以动态fallback代替精确对象。
2. 内容权利：项目自有合成内容的作者/来源证明，或准确原片hash与CC BY署名、修改说明。既有生成RGBA图案可以作为来源审查参考，但它不是有效压缩六样本fixture或编码执行许可。
3. 完整确定的参数：AVC256×144、无音频/加密、rotation0、六帧5fps及上述PTS、首keyframe、禁止未资格化的B帧重排；固定CSD/NAL表示/时基/EOS规则、逐样本hash及最终整体hash/大小。实际数只能生成后填证，当前不预造hash。
4. 输出到全新私有文件，原片永不覆盖；固定路径与输入范围，无网络/PATH/工具替代fallback。总字节/内存/在途源/线程预算、精确deadline和退出清理及UNKNOWN强保管一并给出。
5. 负责人先审完整准确方案及边界，再另行安排生成；生成完成后冻结大小/hash/CSD/样本manifest，独立资格审查后才能运行mux正例。生成退出不等原编码/FD/观察线程已返，不允许强停或补第二次close。

当前C13 ordinary isolated AVC失败不能通过换UID叙述为已解决。本新包按要求使用独立空数据、无权限良性测试环境，不代表生产P0/J11/RCE隔离；若既定边界不满足则准确阻塞，不启动已知不可用ordinary isolated codec/GPU探针。

逐项机读清单：[generation-plan-review-checklist.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_A_EVIDENCE/generation-plan-review-checklist.json)。清单不是另一套release框架或执行批准。

## 8. 阶段B准备清单与交接

[independent-oracles.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_A_EVIDENCE/independent-oracles.json) 共24项，全部状态PREPARED_NOT_RUN；覆盖app/test身份和strict、真实绑定、方法参数、批准原片、普通提取/短读/未知/peek/seek、底层EOF、预算/归还、fixture门/方案、未来真实六样本mux/fMP4重开/EOS、继承MC-B01、同UID/旧数据边界及新执行scope。未伪造任何新测试类#方法。

新候选完整冻结后，阶段B仅独立离线核：app/test两APK及签名/准确包/进程/runner/目标方法与DEX实现；无sharedUserId/不当exported或权限；与com.videokit.app/旧实验包/其他项目身份分离；真实Media3和继承02差异；app/test分别strict锁/metadata/来源许可及实际消费闭包，不能把02的17个app坐标直接当AndroidTest完整闭包；fixture只读资格门、实际写入0的准确阻塞和完整生成方案；预算/期限/退出证据以及所有NOT_RUN。仅保全既有机制，不新造采集框架。

Android真实观察、主机有限自测/静态审查、未来NOT_RUN必须三栏。结构结果不得签HOST_ISOLATED_FORMAT_V1、validated、READY或COMMIT；不启动Activity/Surface/AudioTrack/播放/解码路径。新包不安装更新旧com.videokit.app、不使用其他项目数据，独立同UID测试进程不冒RCE安全隔离或P0通过。

本阶段准备已完成。负责人核新完整冻结后另派B；B本身仍不设备。任何真实Android方法、fixture生成及后续设备新批次均按准确另行派发执行，tester不自动进入下一阶段。本报告及证据发送前冻结，发送回执另存，历史报告/FAIL/UNKNOWN保持。
