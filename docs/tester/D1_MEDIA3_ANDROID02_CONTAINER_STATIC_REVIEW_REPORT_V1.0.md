# D1 Media3 Android02 Container 构建阻塞包独立纯静态整包复审 V1.0

2026-10-21；tester；原372项冻结阻塞包，不是recovery产物B。

## 结论

**BUILD_BLOCKED_STATIC_ONLY**。原372文件/外置ZIP372唯一成员、九份生产/Android源码差异、准确资产/来源、依赖/锁、方法/预算/原失败与既有有限非媒体收据已完成纯Python独立审。**无新APK/JAR/签名/DEX/Android编译及实际运行结果**，不能执行就绪或功能PASS；未用旧Android01产物替验。

集中回交4项P2：**A02-S01 固定Media3末样本flags与全1raw manifest必然冲突；A02-S02 body完成时间早于最后受控信号；A02-S03 Os.open→流包装间的原FD保管异常窗口；A02-S04 同scope全case计量/全操作预算未闭合。** 全部明确为静态代码/合同证据，实际Android复现0；不把未运行的SDK API/FD/真实duration/DTS补绿。

原Gradle client已exit1，daemon35512/UID445eecb5-f5d5-4eba-95e5-4adeb0112c78最终物理返回仍 **UNKNOWN**，仅读冻结当次快照，不查当前PID/端口/缓存registry，不attach/kill/--stop/删锁。原48945/17257也不碰。未读/遍历coder新recovery源码或其输出、未Gradle/JVM/ADB/设备/Media3 parser/编码解码生成，D1未过M0未启。

依据 D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_TESTER_REQUIREMENTS_V1.0.md末尾正式静态派发，在已完成A报告82a2f7942023d16a7cf98a4e5c24be052e2d8ebf946b401ab63742bd2724a02c后顺序进行。恢复构建/提权/集中源码修复权限属于coder新批，本tester没有借该授权执行恢复或诊断网络。

## 准确封存、不存在的产物与原构建事实

原coder报告 **bcfd21251963145c8241bc7a93602a61527f97df7ba87f121973b2cd9bdd3d72**；seal **36d3d06ca38da726aa5ee1d97c54a7cffd025be1af686d0f991cdd4fb9e796b2**。先运行已读纯Python材料入口到materials-001，再独立逐项大小/hash及ZIP去重/集合/hash核**372文件=372唯一ZIP成员**；ZIP5604553B/SHA2569e613481e0aca6a91a31010a897b41c8e7ce9ee127c7857e65fc1737c2f45bda。结束再核372项不变，无写原候选。

artifacts空，app目录无新APK，artifact-status明确UNBUILT_GRADLE_DAEMON_CONNECT_FAILED_BEFORE_COMPILE；无实际Android编译事件、consumption.jsonl、签名/DEX或可安装app/test。源中包com.videokit.d1media3.android02/.test与预期证书/runner只属配置目标，不冒已签二进制身份。旧Android01 APK不能作为本批产物。

原一次构建仅请求:app:assembleDebug和:app:assembleDebugAndroidTest，client UTC03:19:16.6260945–03:19:19.9766371自然exit1。offline/strictLock/verification flags均是**请求值**；在daemon transport阶段失败、项目任务/解析classpath/Android javac未到，不能签strict实际消费成功。daemon当次日志有127.0.0.1监听/greeting写完/awaitExpiration，同client失败并存，**不能唯一断定防火墙、沙箱或端口根因，更不证daemon已退出或当前仍活着**。

材料入口核旧Android01 740/Container02 676/审计fork2738及qualification03证据不变；本tester另核本372、原source/dependency与已保存构建/nonmedia原收据，不新启动它们。材料入口只读既有快照，未读取活动old suite或新recovery。

## 九处源码差异与继承链

独立对src/android/upstream/instrumentation四family做旧Android01路径重映射后全集比较，差异集合严格就是声明九份（新增两份、其余变更），无额外移除/未声明生产Java；所有新hash实际吻合。VerifiedFixtureCopy read_text与原相同，原始字节差异为换行，**九条hash变化不等九个逻辑功能重写**。新独立包名变化与具体逻辑分别审，不把renamed目录当新后端。

| 文件 | 本静态性质 | 新SHA256 |
| --- | --- | --- |
| src/com/videokit/d1android/ExperimentContract.java | 源码变化（含独立包名） | b50b9d94dac422b131341d8c7a5029b1fcb154872de628d8e97e9b8513721033 |
| src/com/videokit/d1android/QualifiedObservation.java | 新生产辅助 | 1b46bdac1754ea4fd1899be2edd2730e793579e0e54ffce48c0659cd58ac7d0b |
| src/com/videokit/d1android/VerifiedFixtureCopy.java | 文本相同，仅字节/换行差异 | d823c959325c204b17d7a7f3186b4fa27cecb3a7b1723990a97db782d818eb1a |
| src/com/videokit/d1input/BoundaryScenarios.java | 新生产辅助 | 2cc529f9fd3a8c677783d8b75e84cd3f7466c038ac05a0a0eddc9aa5b1cc70d1 |
| src/com/videokit/d1input/MatureContainerRemux.java | 源码变化（含独立包名） | 89651f21b4c2d38ebb0f0b1843ebf3e4328f61e214b8c55248cb4a3b5b3ac24e |
| src/com/videokit/d1input/TemporaryOutput.java | 源码变化（含独立包名） | 2ee629505b5bd6f640901ffab04a312b087196e670e4d66df79c6520c04a2aaa |
| instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java | 源码变化（含独立包名） | 22976833793ab96e53f3d25baa3f5b940d3b40916d20a629ba3d3cc0a6459da0 |
| instrumentation/com/videokit/d1media3/android02/test/Media3Instrumentation.java | 源码变化（含独立包名） | d3c0423fa2edf05f3d24107ac6e5cad151be3858c61fe5b8cc20bb9c15c45216 |
| instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java | 源码变化（含独立包名） | 886acc1ff6bb2afd5dbd45ce8c8cf0ad5cf49473b33034dd5351e78b429b0d39 |

源已接准确qualified fixture/固定角色，copy O_CREAT|O_EXCL|O_NOFOLLOW、原flush/sync/close/readonly、实际capture与mature mux/fMP4链调用及原返回gate；TemporaryOutput从按written余量改为按writeAttemptedBytes余量约束，不退款，原MC-B01 pre-admission顺序保持。新BoundaryScenarios明确仅controlled非媒体HOST future/thread口，不冒nativeFD fault注入。下面问题必须在允许的新恢复批集中处理，不能只让编译通过就签功能。

## 集中静态问题

### A02-S01 / P2 — 固定raw flags=1与真实Mp4Extractor末样本标记冲突

触发：任一qualified正路真实Mp4Extractor产出六个样本并进入QualifiedObservation.require。

证据：固定C.BUFFER_FLAG_LAST_SAMPLE=536870912；TrackSampleTable ctor pc116..128对flags[last] OR此位；Mp4Extractor.readSample pc844/849/850取原flags到local16，pc917/923原样送TrackOutput.sampleMetadata。HostMp4Inspection透传flags；q.flags六项全1，require按raw int全等，末样本必不能等1。NOT_DEPENDED_ON等附加位也应依固定库预声明，不凭keybool填原flags。

影响与边界：正常inspectKnown/short/unknown/seek与muxQualified会在该比较门被拒；无设备复现，结论为确定源码/库合同冲突。

集中修复建议：保留raw真实flags，按固定Media3语义明确KEY/ENCRYPTED/EOS与FIRST/LAST等框架信息的对照；仅向mux传其支持的flag域，仍拒未知/加密/EOS，不可删除关键门或现场任意mask求绿。

准确source/hash/行号：docs/coder/d1media3-android02/src/com/videokit/d1android/ExperimentContract.java:31；docs/coder/d1media3-android02/src/com/videokit/d1android/QualifiedObservation.java:16；docs/coder/d1media3-android02/src/com/videokit/d1input/HostMp4Inspection.java:117。

### A02-S02 / P2 — 单调完成时间仍早于最后受控返回事件

触发：cleanup后完成时间小于60秒，但其后E13ReturnEvents.returned同步回调或线程调度跨过观察界，等待者随后才检查isAlive。

证据：completedNano和workerBodyReturned在E13ReturnEvents.returned之前写；returned同步遍历listener。onStart只在检查时isAlive或该较早timestamp>=界时判UNKNOWN。worker可在事件尾段后终止而timestamp仍及时，违反最后受控语句定义。

影响与边界：可出现尾段迟返未计入body契约的正常分支；这是源码时序反例，未运行时间注入/线程测试。

集中修复建议：将同原完成标记放到cleanup及所有可延迟的受控返回信号之后，保留实际join/等界迟/先前UNKNOWN sticky；不以事后isAlive或早marker补绿。

准确source/hash/行号：docs/coder/d1media3-android02/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:38；docs/coder/d1media3-android02/instrumentation/com/videokit/d1media3/android02/test/Media3Instrumentation.java:45；docs/coder/d1media3-android02/upstream/com/videokit/spike/e4/E13ReturnEvents.java:11。

### A02-S03 / P2 — Os.open返回的raw FD未在包装前进入原owner

触发：Os.open已经返回FD，但new FileOutputStream(fd)包装构造随后异常。

证据：createNew将Os.open直接嵌入new FileOutputStream表达式；E4Owned.resource仅action.run整体返回后赋值。该异常窗口无raw FD字段/登记槽/专门closer，保留的外层owner只有nullresource，无法retain该已打开原FD。

影响与边界：异常路径的原nativeFD保管/归还证据缺口；未注入OOM/权限/原生错误，也不据此断言正常Android一定泄漏。FileOutputStream(fd)正常关闭的Android所有权另待准确平台API证据，JDK模拟不代。

集中修复建议：原nativeFD在Os.open成功后先挂到已登记owner，再包装；明确单一真实关闭者/失败归还与UNKNOWN保管，防二close。恢复包需给Android真实所有权依据和实际close证据，不做资源攻击。

准确source/hash/行号：docs/coder/d1media3-android02/instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java:7；docs/coder/d1media3-android02/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:45；docs/coder/d1media3-android02/instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java:39；docs/coder/d1media3-android02/upstream/com/videokit/spike/e4/E4Owned.java:18。

### A02-S04 / P2 — 单scope十方法预算与Job局部计量及全操作计划未闭合

触发：将execution-plan的一个futureScopeId/sameScopeBudget用于最多10方法。

证据：plan标sameScopeBudget输入8MiB/输出16MiB，但inputReserved在每new ExperimentJob起0，nativeattempted每OutputCapability起0；三参数无scope剩余额度，计划没有跨方法预扣账。仅methodsMaximum/每方法capture限额，不是含安装/证据/清理的精确operation列表及wholewall。

影响与边界：当前无APK/设备，不是已发生超限；不能据该提案批准整个设备窗口。Job内全phase累计是已有正确部分，不能扩大为十case共享已实现。

集中修复建议：冻结前统一scope ledger/剩余额度准入，或由负责人明确各独立case scope与外层总额，禁止静默乘N。补全安装/执行/采集/证明/清理逐操作和总wall/进出站预算，保留无APK时UNBOUND。

准确source/hash/行号：docs/coder/d1media3-android02/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:14；docs/coder/d1media3-android02/instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java:18；docs/coder/d1media3-android02/instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java:38；docs/coder/d1media3-android02/instrumentation/com/videokit/d1media3/android02/test/Media3Instrumentation.java:33。

### A02-S01的固定库原始字节证据

此项不是猜测可能的flags差异，也没有运行Media3。用纯Python classfile/constant-pool/Code静态读取**本冻结deps原class bytes**：C.BUFFER_FLAG_LAST_SAMPLE=536870912(0x20000000)；TrackSampleTable构造pc116..128对flags[flags.length-1]执行iaload/ldc该常量/ior/iastore；Mp4Extractor.readSample pc844取flags、pc849iaload、pc850存local16，普通轨道pc917取local16、pc923调用TrackOutput.sampleMetadata，没有清除LAST位（中间只可能另OR NOT_DEPENDED_ON）。HostMp4Inspection直接new Sample(time,flags,...)透传，q.flags却六个1。

所以在目标六样本正常路径，末项至少保留LAST位，**不能与1做raw全等**，会触发QUALIFIED_SAMPLE_MISMATCH而到不了目标mux正路。实际平台是否还返回其他附加位没有运行，不伪填536870913为真实设备结果。静态字节/各原class SHA、method Code hash与完整指令保存在media3-extractor-flags-static-bytecode.json，来源是准确Media31.9.3 JAR，不是手写MP4/AVC parser、javap或反射加载。

### A02-S02的时间反例边界

例如cleanup结束59.9s就写completedNano；其后受控returned()同步listener/调度尾段跨界到60.1s，等待者恢复后原worker已结束，isAlive=false但completed-start仍59.9s，代码可走及时正常分支。实际OS线程退出可晚于最后受控body点这一点本身允许，**问题是当前marker后仍有明确受控回调**。这里是源时序反例，没有注入耗时或碰原挂起进程，不当作实机复现。

### A02-S03的正常关闭API与异常保管分列

可证的是新Os.open已成功而包装构造未整体返回时，E4Owned尚未取得该rawFileDescriptor；不能用外层owner已登记且UNKNOWN就假称原FD强引用也已保留。正常Android FileOutputStream(FileDescriptor)是否负责关闭这份Os.open来源FD，本静态包没有准确平台实现/原返回证据，**仍API_UNPROVEN，不依据JDK模拟断言正常必泄漏，也不做OOM/权限/坏资源注入**。修复应明确真实原descriptor owner与单一closer，而不是先加两个close绕门。

### A02-S04的正确部分与未闭合部分

源码Job内copy/native provider/parse/seek/reopen共用inputReserved，TemporaryOutput/native attempted在调用前累加，是正确的局部全phase设计。问题是plan的一个futureScopeId/sameScopeBudget与最多10个newJob局部计数不能自动视作一个全case总账；缺少统一剩余额度准入和含全部安装/证据/最终清理的operation/wall计划。当前APK/设备未绑定本来就应UNBOUND，不把它本身算成伪造或实际超限；但后续不能借该提案直接开完整设备窗口。

## 来源、资产与有限非媒体结果：保持准确层级

固定deps每个JAR与原Android01字节/hash相同，三个锁/verification-metadata逐字相同，无新JCodec/fork依赖类；reference里包含主机qualification源文件名不等进入sourceSet。准确test asset qualified-six-avc.mp4 **8849B/SHA19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c**与主机资格一致，BBB仅bbbObserve，不能借参数转换送mux。源AndroidManifest/no-permission与Gradle sourceSet只能静态核配置，**尚无APK/DEX以证实际打包**。

本静态材料核涉及冻结asset的有限hash、ZIP CRC/member hash及入口继承baseline身份读，**不是媒体载荷零读取**。它们都不是Media3/容器parser执行，也不倒灌原D1QUAL03或未来设备8MiB。独立372hash/ZIP成员hash/终审372hash按角色另记external-asset-identity-ledger，材料入口的多次有限资产保全读亦说明，未把两套读取总量混成一个原native ledger或物理磁盘IO。

原nonmedia一次JDK javac与metadata JVM原自然exit0/两流关闭，metadata PID32356/UTC03:20:26.195199–03:20:27.907042。source/class178项与pins和major55相符，但**未编译instrumentation Android三文件**；其20父组含8个继承MC-B01子项，不能再计为28个独立顶层通过。原controlled late-read/writer ACK-tail/准入端口等有限结果可保留，actualnative FD/fsync、Media3实际Mp4/fMP4、正路duration/flags和Android API编译不由此证明。tester新host/JVM/非媒体套件重放0。

新CSD政策只对真实Format初始化buffer检查AnnexB4 prefix并按顺序拼接规范化hash，拒绝空或超64KiB；不是构造新NAL或借wholeinputhash冒samplehash。它的真实1.9.3数组边界、capture/reopen样本hash与duration仍未运行，不能因源看似可达给PASS。实际独立DTS能力源码已诚实标NO_INDEPENDENT_DTS_API_HOST_NO_CTTS_FIXTURE_ONLY，不把host Dts=Pts冒Android独立DTS。output duration要求SeekMap/TrackOutput真实1200000，TIME_UNSET时仍需NOT_PROVEN，不能只用空EOS意图补。

## 全方法、原返回与未证清单

plan十意图方法inspectKnown/Short3/Unknown/Seek1s/muxQualified/preopenAdmission/rejectFixture/cancelLateRead/writerPending/bbbObserve与固定三字符串参数、fresh runId、qualified/BBB角色静态连线存在；实际entry Android编译、runner方法DEX/签名/cert/APK与安装SHA、nativeUID/PID/FD、capturetool、freshidle/source epoch/SDK版本和真实finish均 **NOT_RUN/UNBUILT**。无隐藏新scope或用旧APK执行授权。

资源门仍需：actualrawEOF和parserEOF、Extractor.release/DataSource.close、原Provider read/close、writer flush/sync/FDclose、host任务/observer/native原调用归还、worker单调最后点和实际join、E13 finalizer/平台finish原返回分别收据。原receipt runnerFinalizerOwnerAtReceipt=1、runnerFinishReturn=EXTERNAL_ORIGINAL_CAPTURE_REQUIRED不能补成全runner已归还。count0/Future.done/SDKchannel.close只是各自事实。所有实际平台原返回目前仍未执行，不允许删目录/强停/卸载UNKNOWN求空闲。

完整M2A01–48静态覆盖JSON已交，A原PREPARED_NOT_RUN不回写；本文不是48个Android功能PASS。源码层四问题与DTS/duration/原FD/API capability和未知构建物理返回分列，没有把source-policy不符归因媒体坏文件或重生成需求。

## 集中交接与停止

完整4项及本报告/372独立核/九source diff/字节码/预算/原失败层级/未覆盖矩阵冻结后主动交负责人，由其已授权的独立BUILD_RECOVERY01新批集中处理。tester不读该恢复浮动内容、不执行构建/特权工具/网络端口诊断；不存在本tester自动审查拒绝或需人类再授权的动作。若未来新完整包确有APK，负责人再准确另派产物/实际消费及必要测试B，**不是复用当前阻塞包范围重放**。

原candidate/media/encoder/fork/旧helper/源码/seal保持；旧daemon35512及48945/17257 UNKNOWN只保留历史状态不触碰，未以新静态核通过声称host空闲。停止后继，无设备/Media3/生成/播放，D1未过M0未启。
