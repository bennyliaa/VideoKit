# D1 E13F 生命周期整包独立离线复审报告 V1.0

2026-10-18；tester。依据正式E13F tester需求及E13E三项P1报告。**结论：PASS_LIMITED_OFFLINE_REVIEW。E13E-F01/F02/F03在本次生产静态接线及有限本机证据范围关闭，未发现新的阻断缺陷。** 该结论不代表真实Android验证通过、原v17归还、处置获批或新版本设备准入。D1 NOT_PASSED / M0 NOT_STARTED，实际旧任务挂起点仍NOT_UNIQUELY_DETERMINED。

本轮没有设备/ADB、原PID/handle/session查询、STATUS连接、处置、部署/安装或方法重测；没有运行候选全套/打包verify、编译候选、重跑55秒长子进程。只编译tester自身短探针，调用未改最终JAR两次，并使用官方工具独立读取APK签名/清单。旧主case、宿主及reader继续原安排保管，不循环轮询。

## 1. 整包、来源与构建

| 对象 | 独立核验 |
| --- | --- |
| 外seal | `docs/coder/d1e13f/evidence/e13f-freeze.json`，SHA256 `7b72f1bade91286b7d99fbba5459777261e905f4317e0daa969042148b5bf38f` |
| ZIP | `docs/coder/D1-20261018-E13F-source.zip`，25331078B，SHA256 `0217b77bca8a7b6dd6ad78fe1cac27a1b153057775965437c616cdc172e5aceb` |
| 封包集合 | 1179条唯一不可变记录、1178个准确ZIP成员；字节/SHA/成员集合/CRC通过 |
| 独立审计 | tester自有审计10502项检查通过，读取3580份唯一冻结文件；不运行候选自检替代独立审查 |
| 旧冻结 | 九组旧manifest的375/65/46/367/270/118/141/9/1001行逐条保持；不把重复行加总冒唯一文件数 |
| 生产来源 | 138条来源映射、142项最终APK构建输入、183个host JAR成员及逐成员source pin核实；183份实际host-007已测class与最终JAR逐字节一致 |
| 测试替身来源 | 20份实际fixture class原字节及public-008六组shadow源码/生产来源核实；测试类与shadow未装入最终生产JAR/APK |

四主文档完整纳入包：LIFECYCLE_DELIVERY、IMPLEMENTATION_CONTRACT、SELF_CHECK_REPORT、ORIGINAL_TASK_DISPOSITION_PLAN。手工汇总与源码/实际命令回执交叉核对，不把coder的状态PASS字段单独当证据。

本批APK仅一次必要集中离线Gradle main-001，exit0，11:09:46–11:10:50 UTC，最终输入SHA `d2c33eec8bc88c3b6bd376dd97137c272211c4604b85d2eee9c51ec70b1e7b95`。最后starter/reader屏障改动位于host tools，未变APK构建来源，因此没有要求成功后重建APK。host-006编译误纳依赖shadow的检查harness失败，其日志保留、没有该轮运行证据；host-007分离编译后作为最终生产classes来源。public-002/003等开发失败、host-001执行时旧harness及后续finally释放修正记录保留，不倒填历史PASS。

| 最终制品 | 字节 / SHA256 |
| --- | --- |
| e13f-host-tools.jar | 323116 / `97eadcd0cf7beaf1fd0bb7986e012ced69f6e09866f4af7e060338a2d0afabc4` |
| app-debug.apk | 10708622 / `938d70fbc70fd9bfdbef4ac37d2d83a66d7260e88e8c3c62bb2d022ea427908e` |
| app-debug-androidTest.apk | 2774237 / `4227751bf659fca9efc8a8d2d32d5ce754bcbef9033e15a0c92ab7537dca9dd7` |
| fixture-debug.apk | 80041 / `a8c86650ae756f682fb2cbaaa896424974893282026525266e7b1912a8dd1867` |

官方apksigner对三APK独立verify均exit0，v2签名有效。app/test证书SHA256均为 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；fixture为独立 `45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9`。aapt2独立解析app version19/D1-E13F-ACTIVATION、fixture version3；test版本字段为空，按准确byte pair核。DEX生产线索/检查类缺席核验是静态存在性证据，不冒逐指令动态执行证明。

35 Maven坐标/锁与已审基线保持；七native逐字节与基线及最终APK成员相同；fixture零第三方runtime。无native重建/下载，私钥不分发、不读取或补造。SBOM/静态对齐记录不代表真实16KiB设备兼容；许可NOT_GRANTED保持。

## 2. 三项P1的关闭判定

### E13E-F01：同原claim超时后的续办——CLOSED_LIMITED

`E13HostCase.java:26–27`、`E13HostActivationSession.java:19–20`、`E9HostActivationSession.java:21–22`均在原child前把唯一原claim follow到同一supervisor；同步finally中的手工`originalReturned(boolean)`路径移除。`E13PendingGuard.java:6–8,28–29`由静态OWNERS强持guard、guard强持samePC及责任线程，责任线程join同原custodian，不依赖main是否返回或一次通知是否已发生。

`E9PcSupervisor.java:122–123`终止判定包含原custodian线程非alive、listener已返及LIVE已退；先实际join后才生成准确claim结算。marker绑定原claim SHA、PC UUID/PID及pcThreadJoined；CREATE_NEW临时文件经原FileChannel写全/force/同handle读回/长度核对/原close真实返回后才atomic move。错误进入同责任对象的保管等待，不重试、不二close；部分claim或缺marker继续封锁。

public-008的CASE/DEPLOY/LEGACY各NORMAL和FAIL_MARKER共六组真实公开入口组合证据逐条核实：本机100ms受控超时→isolation/main调用栈返回→同原本机child自然返→归档尾通知扣住时归还/pcClosed/claim均不提前→释放后原线程归还/原custodian join→同claim唯一marker→下一scope经同公开入口准入；失败marker分支仍保同guard/PC/责任线程，下一scope在新PC创建前拒绝。无手工true。join-orders-009另覆盖follow早于close、晚于真实终止、与close并发三时序，重复follow拒绝。

marker证明同原PC终止及原marker文件归还，**不证明发布该marker的责任线程在发布前已自行退出**。生产成功发布后仅更新内存状态并返回，不再新增IO；下一scope资格不得解释成所有记录线程的全局退出。失败时生产责任线程在`E13GuardLocation.java:8`为non-daemon并持续保管，不能以测试JVM结束补它归还。

### E13E-F02：锁内日志阻塞完成请求——CLOSED_LIMITED

`E13FinishOwner.java:16–17`锁内仅发布首结果/失败、唯一worker及唤醒，锁外启动worker与记录。`E13Stages.java:11–20`单一daemon诊断线程消费有界队列，平台sink在owner/Stages monitor外；stage调用只做固定ring/非阻塞offer。48事件/500 ASCII字符/24576B（含更充分footer预留）及最多48队列引用；日志错误计数且不重试，单一sink未返不再增长调用线程。

原host-007 BLOCKED/THROWS两组的request/fail实际接线、未返/异常与原结果保留证据成立。tester另外对**未改最终JAR**短探针验证：原sink被有限扣住时request及fail均返回，唯一完成worker仍处理首payload和原失败，sink不持相关owner monitor；随后释放有限latch，排队请求/失败记录仍各一次。

诊断线程不拥有完成请求，也不是PC保管者；它可能仍有平台日志未返，不能把日志队列或丢日志状态当成资源ACK。真实Android进程终态及monitor仍留T07，不由JVM daemon属性推断。不可变首结果、失败/超时只降低资格、永久UNKNOWN不finish的既有门保持。

### E13E-F03：writer体结束冒原线程归还——CLOSED_LIMITED

`E13OperationArchive.java:25–30`将writerBodyReturned与writerThreadReturned分开；尾通知尚在执行时原线程仍alive。resourcesReturned拒绝writer自身调用，也拒绝原线程仍活；外部观察非alive后join同Thread，再逐份核原文件returned后才退OWNERS。通知异常记archiveFailed，物理归还与成功资格分离。

`E9PcSupervisor.java:94–95`也为原starter/reader增加外部线程终止/join屏障，不再仅依赖线程内部的尾部布尔值。原await、supervisor原始资源门及claim的custodian join串联这些条件。archive-facts仍是writer内快照，不能自证writer线程或自身文件close；最终外部事实另证。

public-008六组明确扣住实际原writer尾通知，检验resourcesReturned=false、无pcClosed、无claim marker；释放后才进入归还链。tester最终JAR短探针独立确认：**原writer alive时resourcesReturned=false；释放并join同writer后才为true**。归档器started/exit字段为明确的本机输入替身，不是Android/真实child证明；探针仅验证旧F03窗口，不冒整条设备归还。

本轮没有新的集中阻断项；上述关闭限于冻结源码、真实生产class及有限本机交错。真实平台未返或永久UNKNOWN仍应持续保管，修复不承诺把所有同步IO强制结束。

## 3. 实证与替身限制

| 证据 | 实际证明 | 不能外推的结论 |
| --- | --- | --- |
| host-007两组 | 实际request/fail、完成worker、sink锁关系和未返/异常隔离 | 非真实Android Log/Looper/monitor平台finish |
| public-008六组 | 实际公开入口、原claim/PC/archive、短超时晚返/marker失败与跨scope准入组合 | 固定guard根/处置pin、HostRuntime本机child命令/预算/归档根为显式shadow，合成JUnit/token不是Android owner ACK或产品PASS |
| join-orders-009三时序 | 同原零child supervisor，follow前/后/并发与唯一marker | 不是设备方法、部署成功或真实SDK链 |
| tester两短探针 | 最终生产JAR的F02与F03旧窗口修复 | 未重跑全部公开组合或真实平台，生产class未重编 |
| 最终class绑定 | host-007的183个生产成员与JAR一一字节等价，公开测试shadow与harness原字节可追溯 | 类字节等价不扩大测试场景覆盖；不把同名来源当全部动态行为证明 |

特别核实：public-008 **NORMAL及FAIL_MARKER两类**的本地E13GuardLocation工厂均设置测试责任线程为daemon；join-orders-009的测试工厂也如此。失败分支在断言时确实仍有原责任线程/guard，不因测试JVM自然exit0而视为归还。NORMAL分支的marker/PC终止可由真实生产逻辑与原回执证明，但exit0本身不能证明所有测试责任线程已退出。生产工厂non-daemon性质为准确源码与最终class来源证据，不称已通过无限保管线程的生产退出试验。本报告按实际shadow范围解释，未仅凭简写的“失败子测试daemon”缩小替身边界。

部署组只把首SDK调用替为本机JVM，后续metadata格式故意不完整；证明实际部署入口准入/超时/归还组合，不是完整成功安装或35条SDK流程成功。第一次超时异常仍保留，下一scope获准不把原方法改PASS，不自动执行设备后五法。

本批未机械重跑E13E Android适配套件/source/native/signal或长55秒；其未改来源与历史证据保持，不能将历史JVM结果写成新19/3的真机结果。真实API31主Looper/Binder/不同UID/kernel拒绝、系统false/SE原一次unbind及真实monitor.finish仍全部NOT_RUN。

## 4. 原任务处置方案及当前权限边界

处置文档准确限定新接线只属于新bytecode：旧v17主case最后切片为exec42537/PS39560/Java38056/ADB49540及Android14763/14765/14779，本轮未查询当前状态。旧`retainAuthority(owner,null,owner)`无受审恢复入口，新19/fixture3不能补旧marker、接管旧handle或解除旧原authority。原实际挂起点不因F01–F03关闭而被定位。

自然分支继续要求同原owner、同runner准确scope终态、原ADB/pipe/decoder/custodian真实归还；超时资格不恢复PASS。外部分支要求负责人另定准确fresh启动身份、对象作用范围、证据先行、单次动作/响应/字节预算和原保管转交。共享ADB server/adbd/system_server及其他项目/serial排除；Android/ADB/Java/PowerShell作用分别审定。外部死亡只记录TERMINATED_WITHOUT_RETURN/originalJavaReturn=false及原归还未证，不能造旧Java ACK、正常pcClosed或平台finish。

失败ps诊断维持独立LOST_DIAGNOSTIC_OWNER_UNKNOWN，58908B及缺stderr/exit/close事实保留，不拿主case将来归还抵消、不退款未知预留。若需行政隔离，另审独立记录；不能找新PID/Process冒原对象。该处置方案具备继续审议的具体边界，**当前未选择或执行A/B，无处置许可**。

源码DISPOSITION_SHA=ABSENT，actualScope/release/once/sourceReview均null。固定新batch D1-E13F-LIFECYCLE-20261018 / e13f-lifecycle-deployment.once不构成派单。51成功/53含占用复查、2MiB文本及archive磁盘预算仍只是全六法草案，旧41/55等余额不继承；不是T07单方法需求。

后续必须先审定旧主任务和独立诊断处置，重新核fresh完整M1、精确已装v17/fixture1→候选19/3 metadata及全局无在途，再由负责人另派准确单一T07 scope/release/once/预算。不能因本离线PASS自动更新源码处置pin、部署或续六方法。持续平板测试授权已存在，当前停止源于原任务未决而非重复申请设备使用授权。

## 5. 审证与停止

独立证据位于 `D:/CodexProjects/VideoKit/docs/tester/D1_E13F_REVIEW_EVIDENCE`：自有审计/输入快照、两个最终JAR探针源与原stdout/stderr/退出回执、官方APK静态工具回执、最终不变复核、关闭映射及manifest。两个短探针均自然exit0，归档探针在finally释放并join同原writer；未留下持续运行的探针进程，不冒诊断daemon的原平台终态。

3580份审查输入出报告前再次核SHA不变。报告集中发送负责人，通知回执单独保存，不回写已发送报告。D1未过、M0未启，P0/历史FAIL/UNKNOWN、renderer/audio/Kit和许可门保持。
