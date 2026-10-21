# D1 Media3 Android02 BUILD_RECOVERY01 独立完整阶段B复审 V1.0

2026-10-21；tester；新冻结728完整恢复包，原372静态审已先完成发送。

## 结论

**OFFLINE_ARTIFACTS_VERIFIED_WITH_5_SOURCE_BLOCKERS_ANDROID_NOT_RUN**。新APK/源-class-JAR-DEX/签名/准确资产/实际strict双闭包及两次原构建返回已独立核实；17项有限公共政策与四份真实APK验签通过。集中交回**5项P2源码/观测阻断**：R01-B01部分case历史导出、R01-B02 SDK/native/actual及phase分层、R01-B03最后受控时间点、R01-B04 rawFD包装异常保管、R01-B05原Media3 muxer异常后未被Job保管/关闭门覆盖。最后一项为独立新增，不只转发coder两项自报。

这不是5次Android实机复现。实际Android/Media3容器解析、mux、nativeFD/平台finish均**NOT_RUN**；当前不能签设备执行就绪、完整容器链PASS、HOST_ISOLATED_FORMAT/READY/COMMIT/播放/RCE/J11/P0或D1通过。M0未启动。全部问题在整包报告集中回交，由负责人统一派下一批，未逐项发修。

## 准确封存与独立材料审

coder完整报告11433B/SHA a0dbc309e9f7df2c1e07dd0cb0e74330f43b033a7940eb137e66f50079901481；seal f58ff8acfea8d05a75af6dc46f80307afac3d5d9d12ed175dc838fc976786937。纯Python新材料入口0c3c114254ab72059301517f917e5b1da5d3ac8c71d0becde3aabdd655bd5649通过；另独立核**728原文件/728唯一ZIP成员**全集、大小/hash/成员CRC解压及结束再hash。外ZIP12879742B/SHA bd9fd8d83c39cc12de616cddcd01cfff01118652f68ac16582484b1aff1c2ced。候选保持不变，无cache/registry旧进程查询、无新Gradle或设备动作。

逐src/android/upstream/instrumentation/app/src全集比旧372，准确**7处声明差异（6Java+1testManifest）**无增删漏项；app Gradle另仅versionName改RECOVERY01，原锁/verification逐字不变。阶段A补充在首构建期间到达，首构建原源/产物保存在build001/before-stage-a；第二构建完整采用最终源pin。旧九份相对Android01差异不能误报成本恢复新增九处。

## 实际双APK与来源链

| 最终产物 | 大小 | SHA256 |
| --- | ---: | --- |
| app-debug.apk | 7124541 | 0998beeaa129ef3858fbe1122b80394383f96ad75196c8e4f22b4b856237f6c8 |
| test-debug.apk | 466368 | f8323a1c0d82d23382baf4f776e56b26174fd5354de5e86d897cb979a467f5de |

真实app class JAR130790B/hash95a6068c5719cc4400d2e10d8dd4262a40d7fe4463166b7889975c4b02f62e6b；test class JAR32695B/hash5742a92cb8910689db7e464a7992093848162e00a47147924c6a79e3de9d6940。独立JVM classfile SourceFile/major55/sourcehash/classhash/JAR entry逐项86类（78生产+8instrumentation），APK实际DEX全类存在；原Extractor/FragmentedMuxer以及run/receipt/预算/原返回等核心方法有真实codeOffset/指令体。此为源pin与产物链交叉证据，不声称JVM字节与DEX逐指令等价，更不等实际方法已运行。

真实二进制AXML包com.videokit.d1media3.android02/.test、versionCode1、RECOVERY01、process:media3、准确built-in runner/targetProcesses已核；零权限/活动服务provider receiver/native，无sharedUID，无JCodec/JAAD/fork/fixture-tool/host checks混入。继承android构建定义集合与Android01准确同，不一概误判平台类。test不混入Media3本体，实际通过app闭包。准确qualified8849/hash19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c、BBB349102及来源/资格manifest/许可资产逐字对应；无替代旧APK。

固定apksig9.3.3先对verification元数据SHA准入，tester自己一次有界控制器编译已读固定公共政策/验签helper，再一次JVM执行；**17政策项/4个实际APK（最终2+首构建保全2）签名v2=true/同单证书5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f通过**。class path最终生产JAR在前，来源打印准确；未运行ExperimentJob、Android方法、媒体parser或旧host大套件。javac PID36740 UTC03:53:59.597177–03:54:00.465068，JVM PID6736 UTC03:54:00.465068–03:54:00.816889，原exit0/两流关闭；总1.25秒、两进程各heap256MiB、全窗口<30秒。stdout0/1511B、stderr均0。可选新增tester纯Java helper未使用，没有为审计脚本修正重跑JVM。

## 两次构建、实际strict消费及原返回

仅读准确冻结原receipt/controller/全stdout-stderr/daemon快照，不新查询进程。001 client28184/daemon22948 UIDcf8fac88-ff0c-4260-a786-800c078335f6 UTC03:31:18.427016–03:32:59.039903；002 client36588/daemon39576 UID15d77138-57c5-43dc-845f-6203324b6da2 UTC03:35:33.027334–03:36:10.047127。各client原exit0/两流关闭、daemon准确新创建时间/镜像及同已持有Win32 handle waitResult0/exit0，UID/PID与各自当次日志及client stdout对应，真实BUILD SUCCESSFUL及shutdown末句相符。保留single-use daemon事实，不把--no-daemon请求误报为没有JVM。两次各<600秒/每流<16MiB，无第三构建/kill/stop。

每次实际consumption原事件独立提取**300唯一artifact=123binary+37module+140POM**，每项实际镜像/metadata副本SHA吻合verification并与原Android01实际300身份完全相同；不是只请求strict或读取SBOM。app/test四个实际configuration分别compile12/runtime17/testcompile12/testruntime0，逐独立事件集合吻合锁，不从app17推测试闭包；各两条实际javac classpath事件。metadata verify true、锁与元数据原字节，Media31.9.3及原17坐标不变。

新SBOM17坐标/适用binaryhash/许可项与闭包核实；annotation聚合坐标和kotlin-bom仅metadata消费，空binaryhash不冒二进制。继承source-admission及官方metadata来源封存，BBB与合成资产来源保持；不将静态依赖准入扩大成专利/商业/FFmpeg/模型/发布清权。原Android02 372/Android01 740/Container02 676/fork2738与QUAL03/A证据各原manifest及全部列项再次核保持，不改报告和旧失败。新4个构建进程返回不解决旧daemon35512或48945/17257的UNKNOWN，也不证明host全局空闲。

## 全scope源码、旧问题迁移与未运行边界

唯一外准入scopeAll，内部preopenAdmission/rejectFixture/cancelLateRead/writerPending/inspectKnown/inspectShort3/inspectUnknown/inspectSeek1s/bbbObserve/muxQualified十项，同一Job/同一原worker/同一60秒；newJob计量不再每case重置。原assetOwners/providers/factories保留跨case，inputReserved/outputAttemptReserved累计；controlled读1/写4预扣属于保守controlled口，不冒真实native传输。每case成功资源返回后才进入后继；异常和UNKNOWN停止，不为补历史重试。

| 旧372静态项 | 新728裁定 |
| --- | --- |
| A02-S01 raw flags全1冲突 | **源码政策已修，17有限host政策通过**；actual raw flags保留，仅KEY+末index5的LAST可准入，mux只传已准入key语义；真实extractor/fMP4 flags仍NOT_RUN。旧q.flags列表仍存在但不再作raw全等。 |
| A02-S02 早body marker | **仍适用，R01-B03**；清理后还有同步returned回调。 |
| A02-S03 原FD包装保管 | **仍适用，R01-B04**；Os.open表达式/外owner赋值窗口未变。 |
| A02-S04 同scope全case预算 | **部分修复**：同Job native/copy/EOF与output attempt累计已修，六操作/双APK文本上界计划已补；SDK requested/phase分层归R01-B02，准确外设备/捕获/全wall/cleanup仍待派发前绑定。不能搬称全项未修或已全闭。 |

实际CSD由真实Format.initData逐buffer记录长度/hash、AnnexB4 concat20比固定规范化hash，不照抄host SPS7/PPS3/20成三数组；sample比较真实normalizedAnnexB1340/hash/PTS0..1e6，旧rawAU1360不混。真实raw flags在receipt保留，未知bit拒，不现场mask求绿；实际库可能字段/附加位返回仍未运行。独立DTS API明确NO_INDEPENDENT_DTS_API，不用PTS代DTS。真实input/fMP4 duration须SeekMap或TrackOutput1200000，否则UNPROVEN/拒；空EOS4/1200000只是原E6意图，非第七payload或实际duration证明。原fragment3000/copying不变。

MatureExtractor/capture→原MatureMuxerBinding/FragmentedMuxer→原Sink→同writer/task/只读grant→实际fMP4 parser的源码与DEX链存在，但实际执行0。MC-B01同grant一次REOPEN、未返回pending不sticky/不耗检查保留原已修源码，不重复原旧20父组/含8子项。controlled BoundaryScenarios不冒nativeFD错误注入，也不等全取消阶段覆盖。finalizer owner-at-receipt1、super.finish外部原返回/两流完成分列，source0/Future.done/SDKclose不替原返回。

## 集中问题（一次交回）

### R01-B01 / P2 — 部分失败或pending时此前case历史未导出

原映射：REC-OBS01；证据类型：DETERMINISTIC_SOURCE_REPORTING_GAP；Android动态复现0。

触发：scopeAll已完成前k项，后一case抛异常/原返回pending，或whole deadline在子case执行时到达。

证据：run循环每次method=next；仅十项全部成功后method=requestedMethod；receipt只在current method==scopeAll加入caseReceipts/completedCaseCount。因此失败/pending时已存的历史仍在原Job，外部receipt却没有。不是此前未执行，也不是原Job完全丢失。

影响：无法按实际部分执行结算全scope；不能交设备求测后才补历史。

集中修复：按requestedMethod输出有界已有历史/完成数/当前case与同scope累计账；失败当前case另标partial；保持原Job/firstError/UNKNOWN，不重放完成case，不突破262144B。

准确冻结来源：docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:28（SHA 15193c2011f1de962147c8e191f558cac421dc81051094ebc7936fbe418f461b）；docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:32（SHA 15193c2011f1de962147c8e191f558cac421dc81051094ebc7936fbe418f461b）；docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:124（SHA 15193c2011f1de962147c8e191f558cac421dc81051094ebc7936fbe418f461b）；docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/Media3Instrumentation.java:46（SHA 29272a92b233e314f6c3d9e167091836a5d11fb61b288949409e355742e689b8）。

### R01-B02 / P2 — 原生attempt全scope累计已修，SDK requested及完整phase分层仍缺失

原映射：REC-OBS02 + A02-S04 remaining layer gap；证据类型：SOURCE_OBSERVABILITY_CONTRACT_GAP；Android动态复现0。

触发：inspectShort3时桥接SDK count可大于3，native实际read n=min(count,chunk,size-at)=3；或copy/hash/sniff/seek/reopen任一phase。

证据：reserveInput(n)在native读取前累计，inputActual只加正返回；sdk count无独立累计/预扣且phase无分层记录；receipt无SDK requested与native attempted/returned完整分层，readCalls不能推算。8MiB当前是native attempt+copy/control/EOF reserve，不是SDK requested总量。

影响：M2A10/35/37的全口径观测与预算合同未闭合；绝不声称本批已实际超限。

集中修复：同原路径在调用前记录/准入SDK requested、native attempted、returned/EOF及phase累计，无退款无新factory额度；明确copy/control非native传输计数；原native FD/asset/writer分层峰值也需在设备合同前补齐，不能从sourcePeak冒FD峰值。

准确冻结来源：docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java:25（SHA 7bc0749e44cfbc207b51aa9296b8a7f79fa2df7f4dc2453c79e579792c84eb23）；docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java:26（SHA 7bc0749e44cfbc207b51aa9296b8a7f79fa2df7f4dc2453c79e579792c84eb23）；docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:19（SHA 15193c2011f1de962147c8e191f558cac421dc81051094ebc7936fbe418f461b）；docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:119（SHA 15193c2011f1de962147c8e191f558cac421dc81051094ebc7936fbe418f461b）；docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:122（SHA 15193c2011f1de962147c8e191f558cac421dc81051094ebc7936fbe418f461b）。

### R01-B03 / P2 — wholebody完成标记仍早于最后受控返回信号

原映射：A02-S02 STILL_APPLIES；证据类型：SOURCE_ORDER_COUNTEREXAMPLE_NOT_RUNTIME_REPRO；Android动态复现0。

触发：cleanup后marker及时，但之后同步E13ReturnEvents.returned回调/调度尾段跨60秒，等待者晚恢复时worker已结束。

证据：completedNano/workerBodyReturned均在returned()之前；returned同步遍历listener.changed。onStart只看isAlive/早marker差值。59.9s写marker，60.1s回调后worker结束，可被早时间认作及时。

影响：源码不满足M2A42 last-controlled-point，实际join不能替较早body点；不伪称已实机触发。

集中修复：把最后受控body标记置于全部cleanup/可延迟信号之后，保同worker join、等界迟及UNKNOWN sticky；若信号需提前，明确最终不可提前补绿的原完成点。

准确冻结来源：docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:34（SHA 15193c2011f1de962147c8e191f558cac421dc81051094ebc7936fbe418f461b）；docs/coder/d1media3-android02-recovery01/upstream/com/videokit/spike/e4/E13ReturnEvents.java:12（SHA 44576bbb0c0fdd555ad3044e5645b5de3ae250c0172399098388964adcf53118）；docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/Media3Instrumentation.java:46（SHA 29272a92b233e314f6c3d9e167091836a5d11fb61b288949409e355742e689b8）。

### R01-B04 / P2 — Os.open成功至流包装返回间raw FD仍未进入原owner

原映射：A02-S03 STILL_APPLIES；证据类型：SOURCE_EXCEPTION_RETENTION_GAP；Android动态复现0。

触发：Os.open成功返回原FD，随后new FileOutputStream(fd)构造异常。

证据：createNew仍内嵌Os.open；外E4Owned仅在action.run整体返回后写resource，故此窗口原FD无登记字段/closer。包中正常Android wrapper关闭所有权依据仍API_UNPROVEN，不能用JDK helper替平台。

影响：已注册外holder并不证明原FD被强保管；异常路径原FD归还证据缺口。未OOM/坏资源/权限注入，不断言正常Android一定泄漏。

集中修复：先登记原native descriptor owner并在open返回后立即采用，包装/关闭单一权责，异常UNKNOWN强保管；提供准确Android关闭依据，防二close；不重放/强制清空。

准确冻结来源：docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java:8（SHA 7bc0749e44cfbc207b51aa9296b8a7f79fa2df7f4dc2453c79e579792c84eb23）；docs/coder/d1media3-android02-recovery01/upstream/com/videokit/spike/e4/E4Owned.java:19（SHA aee54f13e6eb548006a0fe355d59c22521a407df632210d104e739ccecd83626）；docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:58（SHA 15193c2011f1de962147c8e191f558cac421dc81051094ebc7936fbe418f461b）；docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java:40（SHA 7bc0749e44cfbc207b51aa9296b8a7f79fa2df7f4dc2453c79e579792c84eb23）。

### R01-B05 / P2 — 原Media3 muxer在addTrack/write/EOS异常后无Job级保管及关闭门

原映射：NEW_INDEPENDENT_FINDING_INHERITED_SOURCE；证据类型：SOURCE_EXCEPTION_OWNERSHIP_GAP_NOT_ANDROID_REPRO；Android动态复现0。

触发：MatureMuxerBinding构造及E6Muxer.create成功，后续addTrack、sample或E6 EOS/close抛异常。

证据：binding仅writeAndInspect栈局部；private original只在binding内，未登记到Job原owner。正路finishWriter才走E6Muxer.finish/close；异常没有finally或保管转移。Job cleanup只abort TemporaryOutput/关hostFD，resourcesReturned无binding/muxer状态。即使sink/native均返回，仍不能据此证原Media3 muxer已close/归还。

影响：失败路径原muxer引用/原close返回缺口；可能在外资源已返回时允许finisher通过，不代表该muxer事实已证。源码继承不等此合同已验收。

集中修复：原muxer/binding在创建前有Job级keeper、成功后采用；错误保管同原对象，按真实API明确一次关闭/close未知状态门，不重建muxer、不二close、不把sink abort当原mux close。

准确冻结来源：docs/coder/d1media3-android02-recovery01/src/com/videokit/d1input/MatureContainerRemux.java:13（SHA 3bf25db0f20eb8fadcb26d382632b67871088052eb84233be1f84aaf2f452028）；docs/coder/d1media3-android02-recovery01/src/com/videokit/d1input/MatureMuxerBinding.java:7（SHA c82377ae13e0b6fd136b799a468ad260ac3cf1b4111dda50dd7dd5ede4c885ee）；docs/coder/d1media3-android02-recovery01/src/com/videokit/d1input/MatureMuxerBinding.java:11（SHA c82377ae13e0b6fd136b799a468ad260ac3cf1b4111dda50dd7dd5ede4c885ee）；docs/coder/d1media3-android02-recovery01/upstream/com/videokit/spike/c14/E6Muxer.java:18（SHA bea5c0c3625b3c7d433ca22e8106fd6280630d622ca81f1f241f5a6eb2fbe3d2）；docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:94（SHA 15193c2011f1de962147c8e191f558cac421dc81051094ebc7936fbe418f461b）；docs/coder/d1media3-android02-recovery01/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:104（SHA 15193c2011f1de962147c8e191f558cac421dc81051094ebc7936fbe418f461b）。

## 全48项与后续准确范围

independent-m2a01-m2a48-results.json对M2A01–48逐条原oracle给离线证据/源码缺陷/平台NOT_RUN边界；未改A的48个PREPARED_NOT_RUN，未把17公共政策项冒48个Android PASS。实际FD/格式/PTS/DTS/duration/flush-sync/原mux/finish、真实sourceepoch/FD峰值/取消各阶段均未运行。

计划准确双APK合计7590909B，六逻辑调用（fingerprint1、本APP/TEST存在性各1、准确各install1、不-r，scopeAll instrumentation1）；命令每op4096总24576，上行逻辑payload7615485B；preflight786432/install131072/instrumentation pending+final1048576/controllerproof1048576，总下行文本3014656B；每receipt262144B。独立算术核这些上界准确，ADB协议framing明确未观测，不造精确wire字节。scope/serial/freshIdle/captureTool尚null，完整外wholewall/cleanup处置与捕获工具/协议预算需在缺陷处理后的准确新设备合同绑定，不能以当前六逻辑计划自动执行。

用户持续平板使用授权保持，无需再重复向用户索取通用平板授权；当前范围仅离线B，未发起设备/ADB/5037/占用/安装/生成播放或网络/旧进程动作。当前五项问题先由负责人统一组织新集中修复，再整包独立复审及另派准确设备范围；本tester不自行改候选、开第三构建或转设备。

## 过程与冻结

一次独立Python材料核和独立自写审计完整完成；初审tester对Gradle versionName行缩进的错误断言（实际同一行含多个version字段），改为整文件旧version→新version精确等值；最终器首次误假设所有SBOM坐标都有binaryhash，明确annotation聚合与kotlin-bom仅metadata消费后按层核实。两次均为tester静态断言修正，不属于产品错误，未改候选或重放JVM。读取过有限文件/ZIP/AXML/DEX/class/签名及包含媒体的opaque字节，不能声称媒体载荷读取0；没有MP4/AVC/Media3解析，也不倒灌旧QUAL03或未来设备8MiB账。本机apksig内部读量未单独观测，不伪填0或精确总量。

本报告/完整问题/48矩阵/独立源与binary审/两build消费/原返回/17政策与签名原流及owner/旧seal保全一并冻结于D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_REVIEW_EVIDENCE，manifest在全部写完后生成；发送收据另存证据目录外。冻结后不改报告及已发送证据，停止后继等负责人整包处理。没有自动审批拒绝或待用户重复授权动作。
