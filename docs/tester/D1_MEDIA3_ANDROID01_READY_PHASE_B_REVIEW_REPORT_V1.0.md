# D1_MEDIA3_ANDROID01_READY 阶段B独立材料复审报告 V1.0

日期：2026-10-21。测试人：tester。接收人：负责人01a107c3-2bf9-7fa0-94a0-234258ca6774。

## 1. 总体结论

**STATIC_MATERIAL_REVIEW_COMPLETE_WITH_LOCAL_UNKNOWN_AND_FUNCTIONAL_GAPS。** 已完成本次正式要求范围内的整包独立离线材料审查：冻结/ZIP、双APK签名/清单/DEX、双JAR实际Android编译来源、app/test分别依赖闭包、六case/预算/返回门、24项oracle及原片和JCodec提案均有独立静态核验。未发现由本次静态证据可证实的新增产品缺陷。

**不能放行为执行就绪或功能PASS。** 原本地suite会话48945（历史Java39256/父Python35988）及jcmd会话17257未获最终返回，保持UNKNOWN；本次未查当前进程或诊断根因。后续coder 62条绿色只证明它们各自的回执，不替代早期原返回。独立功能重放依正式交测要求全部NOT_RUN，真实Android、合格fixture、mux及成功结构路径继续OPEN/NOT_RUN，JCodec工具UNBUILT仍阻塞构建/生成准入。

本次没有启动62完整入口、ContainerPendingOrderCheck或其他产品检查，没有新attach/轮询/暂停/终止/处置原owner，没有设备/SDK现场/ADB/5037/占用查询、Gradle、编码/解码/播放或JCodec构建/加载。本次仅运行Python字节/文本审计及三个已有静态工具调用（两APK验签、一次javap），原进程均自然exit0返回；不是新增功能测试。D1未过、M0未启，历史FAIL/UNKNOWN/P0/J11及旧批准范围不改。

依据：[正式阶段B测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_MEDIA3_ANDROID01_READY_TESTER_REQUIREMENTS_V1.0.md)末尾限制及负责人本次补充；[主交付](D:/CodexProjects/VideoKit/docs/coder/D1_MEDIA3_ANDROID01_READY_DELIVERY_V1.0.md)。

## 2. 冻结身份及原证据保全

|对象|独立结果|
|---|---|
|候选|docs/coder/d1media3-android01|
|交付文档SHA-256|660f33d468ad9f6b905795345edc8970aef641462efaa02fd39aa05759cc194e|
|seal SHA-256|fca6adcdf9783b91c9af396de3b836efad72c4d59ef820eb1924d8658f0b928a|
|seal/ZIP|740项含ZIP；739个唯一ZIP成员，路径集合和逐项大小/hash一致|
|原冻结/输入|10批旧候选6232项及本批1053项输入核对|
|既有独立证据|02复审1306、01复审1852、05复审1093、容器阶段A75、Android阶段A7项及原报告保持|

本次准确排除当前Android01活动 `evidence/suites-001`，只读已封存29条快照和外置补充；未为凑740身份读取或改写活动目录。早期原目录可能随原父自然继续写入，不能把它包装成已冻结/已返回。旧候选中同名已封存目录与本活动目录区别核对。

见 [static-artifact-dependency-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_EVIDENCE/static-artifact-dependency-audit.json)。

## 3. 双APK、DEX及JAR实际来源

|产物|大小B|SHA-256|
|---|---:|---|
|app-debug.apk|7112721|0477532af0d4f137108780acda9bb01a4fe53434f88a9aebad1f1bfd06666b04|
|test-debug.apk|453174|7ed7e2f6051668f4ed950a48ada3cbd1bfdda4a431cf15054e7066f763794ffe|
|主JAR|119870|a0444cc05bb9d1be24fdf91b86b2e998708be04aba12823f23a5f5e3753cf23d|
|instrumentation JAR|31129|e2f75ff41b23d94d0f7cf015943528c339679efb7794967e920714317e7f687c|

两APK通过同一既有apksig验证器独立v2验签、单证书，SHA-256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。对应静态工具原argv/起止/退出/自然返回单独保存，未编译新验证器或启动产品类。

二进制清单直接解析：app `com.videokit.d1media3.android01`、test同名加`.test`，versionCode1/versionName D1-MEDIA3-ANDROID01-READY，min31/target36；app默认`:media3`。唯一instrumentation为 `com.videokit.d1media3.android01.test.Media3Instrumentation`，targetPackage为上述app，targetProcesses准确为`com.videokit.d1media3.android01:media3`。无sharedUserId、权限、业务组件/native、UI或旧app目标；不安装/升级旧com.videokit.app，不把同UID空数据实验称RCE隔离或生产J11/P0通过。

DEX实际定义app4937类、test312类；两者280个`android/`构建生成定义集合与冻结02完全一致，准确排除Uri/ErrnoException/OsConstants主机替身、checks及JCodec，未虚称DEX没有任何android定义。test没有自带Media3实现，被测库由target app提供。

进一步独立解析DEX encoded method/codeOffset，核runner onCreate/onStart/finish/onException、ExperimentJob run/canFinish/resourcesReturned/runQualified/receipt、输入复制/资格门、原E13FinishOwner、真实Mp4/FragmentedMp4Extractor和FragmentedMp4Muxer均有实际代码，而非仅匹配名称字符串。两个JAR每个class的路径集合和字节分别与最终Android javac classes一致；一次既有javap静态反汇编再核关键调用链，不初始化产品/编码器类。

证据：[app验签](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_EVIDENCE/signature-app.stdout)、[test验签](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_EVIDENCE/signature-test.stdout)、[DEX方法代码偏移](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_EVIDENCE/dex-implemented-methods.json)、[JAR静态反汇编](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_EVIDENCE/javap-static.stdout)。以上不证明Android实际执行。

## 4. app/test strict与继承许可

固定Media31.9.3及既有来源许可准入继承02限定结论，未升级为发行或商业清权。settings锁和verification-metadata与02逐字节一致，LockMode.STRICT及metadata开启；app锁的原scope保留，仅12个已有compile坐标增加准确AndroidTestCompile scope，其余新增空配置按空锁记录。

从本批原始build-main-004解析/编译事件重新关联，而非抄app17坐标当test闭包：

|实际配置|外部坐标|本次独立核对|
|---|---:|---|
|debugCompileClasspath|12|原解析事件逐项一致|
|debugRuntimeClasspath|17|继承实际运行闭包|
|debugAndroidTestCompileClasspath|12|与app compile精确坐标一致，另有target project组件|
|debugAndroidTestRuntimeClasspath|0|target app提供被测代码，无新AndroidX runner/JUnit/JCodec外部运行依赖|
|两个实际javac classpath|16/17文件记录|与原编译事件逐项一致，存在hash的实际文件逐项核对；null/hash为空的空Kotlin输出项不虚报已存在或验hash|

实际核验对象仍300项，身份集合与02相同：123 binary、37 module、140 POM；逐项关联Dependency verification事件及原字节/hash。原strict离线004回执和日志63任务全部执行成功已审阅，本次没有重跑Gradle或把缓存枚举当消费。无新runtime/test坐标、版本、pin或二进制下载；JCodec source提案不在任何app/test依赖或classpath。

来源/license文本和实际deps与02核对保持；本次无联网重新取证、不声称验证不存在的上游签名或扩大发布许可。

## 5. 六case、预算和原finish门

实际机制是一个系统自带Instrumentation runner按enum分派六个case，**不是六个JUnit测试方法**。参数键严格为case/fixtureSha256/runId三个字符串；禁止附加class、路径、URI、codec或运行时fixture注册。fixtureSha256固定批准原片，runId格式D1MA01-[A-Z0-9_-]{1,32}；精确每例runId/完整am数组与冻结plan逐项一致。

|case|静态行为与当前真实状态|
|---|---|
|inspectKnown|MP4、cap=true、seek=-1、capture=false、已知349102B；真实观察NOT_RUN|
|inspectShort3|同片，原host每次最多返回3B；需与known归一化轨道/CSD/逐样本指纹比较，NOT_RUN|
|inspectUnknown|同片，length=-1；有限原EOF、无猜长度；NOT_RUN|
|inspectSeek1s|只用实际SeekMap首point及1000000us请求，记录真实position/time/new epoch/replay；NOT_RUN|
|preopenAdmission|false capability/null container/-2/2000001在真实解析/adapter和source open前拒绝；本次只静态审，未执行|
|muxQualified|QUALIFIED=null，先返回FIXTURE_BLOCKED，在私有目录、文件、输出或mux创建前停止；实际正路径NOT_RUN|

原片从test asset经原受控流复制到新包新鲜私有cache根；同流定长/hash/实际EOF校验，flush/sync、同原close返回后设只读再解析。新root存在即拒绝，不覆盖原媒体；运行时不允许指定替代路径或注册fixture。test APK唯一sample资产与批准原片逐字节hash一致，app不含该资产。

每例60000ms，receipt UTF8上限262144 B，超额返回明确失败/observationComplete=false，不截断成功。输入attempt/reserved≤8MiB，包含复制、hash/sniff/parse/seek/读回及EOF witness；actual returned另列、保守预留不退款。块≤65536，输出attempt16MiB，全局源2/每源inflight1/queue0；原02有限门仍在，实际库内部内存未由这些外部计数证明。

新range/seek/replay/原EOF及release/close字段补足阶段A证据需求；普通轨道观察不预填golden。两个writer输入/读回源、UID/PID等均需实际receipt，不能凭源码推峰值或1.2秒duration。项目自有线程理论上界11、最多16seek/18range、2轨/512样本/轨、1024 replay及单样本262144是静态范围，非实测整进程峰值。

原E13FinishOwner与02/upstream一致，唯一platform finish路径等待同一case worker实际join及原source/observer/FD/registry/keeper归还。60000ms后仅停止准入、保留UNKNOWN/强引用，不interrupt/kill/二close/重启或退款。receipt形成时runnerFinalizerOwnerAtReceipt仍可能为1；自身不能证明platform finish或外层采集已返，须后续原外层自然返回证据。真实门时序未独立运行，不能登记PASS_RETURN。

后续计划仍为未授权提案：14操作、六case各一次、总text4MiB/每例含framing512KiB、binary output0、control1MiB/proof1MiB；两APK合计7565895 B，input含framing8614471 B，outer总14905927 B、600000ms，算术一致。scope/device/build/capture/fresh gate均null，当前不可执行。不能把旧25/32操作计划、once或余额当新授权，也不能把该预算提案代复用采集工具的实际操作支持；准确新采集绑定仍待后续另审。

## 6. 原片权利、fixture及JCodec静态方案

批准原片349102 B/hash `720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9` 原文件、test asset和APK成员一致，权利材料继承BBB/Blender/CC BY3.0署名及00:30–00:38节选重编码修改记录，未冒原始未修改下载。其他7个媒体payload未读。320×180、含AAC、8秒不符单AVC256×144/rotation0/六样本写入门；当前registry=null、mux正例FIXTURE_BLOCKED，不用4B或伪NAL代替。

JCodec0.2.5仅source/POM/许可提案：1246282 B源码archive，SHA-256 `9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db`，807 ZIP条目，无class/native/可执行JAR等成员；官方SHA1保全值与原字节一致，同源校验不冒独立发布者签名。11份API摘录逐字节匹配archive原成员，POM精确坐标/FreeBSD及唯一test-scope JUnit4.12声明已核。当前官方仓库两条款LICENSE文本原样保全，明确不冒不存在的0.2.5标签许可或专利/商业发行清权。

具体API提案静态一致：H264Encoder.createH264Encoder选DumbRateControl，初QP20但允许其真实调整，不标constant-QP；setKeyInterval1/motionSearch0、YUV420J六帧原创整数色块；每帧55296 B、六帧331776 B，5fps、PTS0..1000000。编码器原AnnexB由CodecMP4MuxerTrack一次提取SPS/PPS及AVCC转换，不重复转换；Packet timescale5/duration1形成1200000us结束规则。精确已有JDK21.0.10编译器hash/API提案hash、新CREATE_NEW路径、块/attempt/heap/期限/原退出及UNKNOWN保管等材料具备。

**尚无可执行工具：build hash=UNBUILT，driver/source list/编译class及JAR精确身份未产生，本次未编译、加载或编码。** 当前可接受的只是完整静态方案供后续决策，不能签“工具ready”或生成许可。后续单独工具构建批次必须冻结实际driver和源码列表、精确编译参数及确定的build产物hash；driver还须具体落实原channel完整/partial write与header rewrite attempt预留、真实close/force/worker归还，不能仅凭提案文本。再另行生成、冻结实际文件/CSD/NAL/六样本/时基manifest，独立真实Media3资格化，才能嵌入另一个新候选。源hash不是build hash，提案PTS/EOS不是实际duration证据。

见 [generation-source-static-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_EVIDENCE/generation-source-static-audit.json)。

## 7. 本地UNKNOWN、父派发风险及收尾意见

当前按既有记录保留：

|原对象|准确已知与缺失|
|---|---|
|suite session48945|历史父Python35988/Java39256，ContainerPendingOrderCheck；29条已自然返回快照，其后该例无最终receipt，原线程/pipe/callback/keeper归还UNKNOWN|
|jcmd session17257|命令目标参数39256 Thread.print -l，原输出未获最终栈/退出；jcmd自身PID/创建身份未知，不能把目标PID当诊断进程PID|
|当前系统状态|本次未查询；负责人一次CIM不可访问不产生状态证据；历史PID/创建时间不升级为当前身份绑定或防PID复用证明|
|后62回执|已核冻结汇总均exit0，只作coder该批自检；不替代上述早期原任务或tester独立重放|

补充方案 [ORIGINAL_SESSION_CLOSEOUT_PLAN](D:/CodexProjects/VideoKit/docs/coder/D1_MEDIA3_ANDROID01_READY_ORIGINAL_SESSION_CLOSEOUT_PLAN_V1.0.md) SHA-256 `e6055b772048a0f192efe594258a690d0d2575ca8732522999ce11c29be5a129` 及外置manifest逐项核对。coder在06:41对两个原session各收取一次，原结果均无exit_code、空output、仍给session id；这不证明历史PID当前存活或已经结束。本次tester未再收取、attach或干预；当前方案A保持UNKNOWN，不继续主动轮询。

独立读父run_suites.py确认：seal只在脚本启动时检查，已载入的for循环没有逐项stop/frozen屏障。原子若自然返回0，父可能继续最后AndroidReadyCheck；磁盘现有seal/停文件/改脚本或关闭显示窗不是原父派发屏障。因此A可保全现状，却**不能承诺停止后继派发、原资源回收或host空闲**，必须作为执行前阻塞保留。

建议负责人继续将本地收尾与材料审查分开集中决策。若未来要求阻止任何新派发，须先有经审定的准确原父派发屏障；若仅考虑强制诊断收尾，准确父句柄/创建时间/image/完整argv/亲子关系及jcmd自身身份等缺失必须先补足，不能裸PID或按名称批量处置。父先退出只阻止确认退出后的新派发，仍有决策到退出窄窗口，须明确预算和前后子列表/新资源处理；不先单独放行/终止Java或jcmd来赌父不会继续。当前无任何B/C处置授权或动作。

任何将来强制收尾都会改变管道/进程执行，可能丢失未落盘stdout/stderr/线程栈、原finally/close/observer及自然返回证据；只能记录独立诊断干预结果和原测试UNKNOWN，不能补ACK、改exit0/PASS、退款、回写29快照或用以后绿色抵消。未知归还不自动删目录或卸载。以上建议不执行新工具/建新框架，当前不提供或运行终止脚本。

见 [execution-and-unknown-review.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_EVIDENCE/execution-and-unknown-review.json)、[补充方案独立审阅](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_EVIDENCE/closeout-supplement-review.json)。

## 8. 24项映射、未执行及最终交接

全部MA01–MA24逐项独立状态见 [independent-ma01-ma24-results.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_EVIDENCE/independent-ma01-ma24-results.json)。PASS_STATIC_MATERIAL_ONLY仅指本次材料/字节/调用链；MA21沿用02有限修复并只审新差异，未在新包重测。MA16–MA20真实正例FIXTURE_BLOCKED，其他真实路径均NOT_RUN。不能以24映射、源码/JAR包含实现、coder62条exit0或probe记录环境缺类代实际提取、seek、fsync、原finish时序、mux/EOS/播放PASS。

待负责人另行决定的准确门为：本地原会话/父派发UNKNOWN处置与执行就绪、独立新候选实际重放范围、JCodec独立工具构建准入和build hash、后续生成/资格化及新candidate、准确新设备批次和fresh门。它们不阻碍本次已完成的静态审，但任一不能由本材料结论自动越过。

审计过程一项tester修正：首次静态脚本将“当前活动suites-001排除”写成所有同名路径排除，遇旧不可变候选同名目录而退出1；收窄至准确Android01活动目录后完成。初始脚本和纠正记录保留，未修改产品、旧证据或重放任何测试；该首次退出发生在静态JVM工具之前，不作产品FAIL。最终三个静态工具均自然返回，无本次新增未归还tool session。

本阶段完整材料审查已完成。报告及证据发送前冻结，回执外存；集中交负责人统一处理，不逐问题联调、不启动62入口/挂起复现/attach/设备/生成或原owner处置。原740 seal、旧6232项、全部旧报告/FAIL/UNKNOWN保持；真实容器目标继续OPEN，D1未过、M0未启。
