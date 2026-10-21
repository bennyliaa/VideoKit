# D1 E9A 整包独立静态复审报告 V1.0

2026-10-18；tester；依据 `docs/milestones/D1_E9A_TESTER_REQUIREMENTS_V1.0.md`。候选 `docs/coder/d1e9a`，version12 / D1-E9A-PREPARE。复用 E9 已完成的共享架构审查，对实际变更、完整新冻结与定向证据独立复审。

**结论：冻结完整性 PASS；实现复审 NEEDS_FIX / NOT_SUPPORTED_FOR_DEVICE_BATCH。E9-F01/F03/F04 CLOSED_STATIC_LOCAL；E9-F02因登记存储原资源与未来activation前置出口仍有缺口，保持OPEN。集中保留1项P1残留（E9A-F02，对应原E9-F02）及1项新增P2（E9A-F01，本机连接数硬界）。暂不建议派设备批次，先集中修复并补有限本机证据。**

本结论是静态与已归档本机证据范围的复审，不是 Android 实测 PASS、scope 批准或执行指令。本轮 tester 设备/ADB/安装/广播、构建、候选测试重跑、媒体、迁移及 ABORT 全部0。没有生成实际授权配置、token、H_actor/catalog 或 activation。D1 NOT_PASSED、M0 NOT_STARTED、E6B-OBS-F01长期准入OPEN，其他P0和历史FAIL保持。

## 1. 独立完整性核验

审计：[independent-metadata-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_E9A_EVIDENCE/independent-metadata-audit.json)。审计仅读取/hash/解析源码、JSON、日志、ZIP/JAR/ELF，不执行候选，也不运行候选自检脚本。

| 核验对象 | 结果 |
| --- | --- |
| E9A seal | `edfb13109b1cc5103ed348f3ce757165597fe16fe8320a1426afd4cd9651fdfb`；733项 immutable 全匹配 |
| 源清单与ZIP | manifest731项全匹配；ZIP732文件逐项与原文件比较，无差异；732包含源清单，733 immutable另计ZIP，口径一致 |
| ZIP | 24710914B；SHA256 `378b2ceec7ac5d47e0f63710efde0d590a33adea6316219e554f193de7b37acb` |
| version12 app | 10643010B；SHA256 `1edb820faea79cf87d261555adbd397f32c6796447ace127bd39cb756e10c841` |
| androidTest | 2749733B；SHA256 `2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b` |
| 构建输入 | `06fc16bd7e27f766d30fc2b57810c0952df56aaf59011c4d93b0f3b0aee87d0b`；163项全匹配 |
| 最终生产host JAR | 255014B；SHA256 `709fa796ed59ce6394b25f75bc69391099f7a4d398cafbd79cef91ef257d17e4`；155个生产class，逐项匹配来源源码摘要、008编译class及JAR字节，无测试类 |
| 007→008来源 | 148个生命周期/共享class与final-pc-007逐字节相同；其余为HostManager/HostDeployment及其嵌套类的最后纯PC帧验证变更；不冒称007执行了最终新增断言 |
| 定向输入 | 007/008各76项；007三份历史工具源码精确匹配保留的before-final-frame-validation副本，008全匹配，无未解释摘要差异 |
| 公共Android入口 | 206项输入全匹配；6个公共入口及1个Runtime失效序列，SDK桩范围 |
| 历史冻结 | E9的1045项、E7A的200项、E8A的42项及各原seal全匹配，未修改历史结论或原产物 |
| 继承 | 130项严格逻辑/原生继承输入匹配；35个依赖坐标和7个native差集为空，SBOM全部组件与E9一致；APK内7个so摘要与ELF LOAD 16KiB alignment均通过元数据核验 |

原签名证书 SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`：两份已归档签名报告与APK audit一致，本轮未重复调用签名工具。Android身份实现核version12和原UID，而非沿用version11校验。

一次集中离线主构建main-001，原日志 `BUILD SUCCESSFUL in 1m 11s`、68任务执行，无APK修复构建。最后008为纯PC工具/语义帧校验变更，最终JAR直接取已定向编译和验证的class打包，不重复Android或native编译。三份实际JAR默认入口原记录均exit0/INSPECT_ONLY；本轮未再运行。

## 2. 原四项缺陷逐项复审

### E9-F01 / 原P1：非等待启动与独立完整状态 — CLOSED_STATIC_LOCAL

`E9HostManager.nonWaitingLaunch()` 实际构造 `am instrument -r`，无-w；launch client仅用5秒原任务结算PC请求，不将启动命令退出当作Android actor返回。启动前先登记外部launch与Remote责任，后者独立于client/pipe的生命周期。

`POLL`实际发送一次STATUS，不再返回缓存首帧。独立DUMP保护ordered broadcast返回完整transport；STATUS state=-1由原Run同锁取state，并核handle/seq。`observeStatus()`对丢失序号保守计入请求与STATUS额度；写/ACK仍要求精确state。`broadcastFrame/checkTransport`在同一个原5秒响应任务内检查result=1、唯一完整canonical帧、模式、UID、request/actor/PID/handle/seq与回退/重放；错误回复不能先被采用后再校验。

Android `publish()`只记snapshot，不再依赖sendStatus或等待watcher stdout。READ_ONLY_IDENTITY实际身份结束后封闭写入口，但允许有限STATUS和精确收尾ACK；`captureIdentityForFinish()`允许原identity回执在无reserve/无device写时归档，normalFinish可归还PC Remote责任。identity-only不满足final COMMIT资格，也不能续actor2。缺有效原身份或回执仍UNKNOWN，不补造boot/start或close。

TRANSPORT/STATUS_GAP/IDENTITY_CLEANUP/REMOTE及最终源码支持上述实现；真实Android冷启动、receiver可达性、DUMP权限与广播返回格式仍NOT_RUN，正是下一只读批次要验证的内容。

### E9-F02 / 原P1：PC Process/pipe出口已修，登记存储原资源仍有残留 — OPEN

`E9PcSupervisor`在ProcessBuilder.start前保存Operation、starter和静态LIVE强根；starter/reader/custodian都为非daemon。原stdin/stdout/stderr分别由E4Owned持有，实际Process、wait、原解码及pipe close未返时不会满足resourcesReturned。read先EOF、输出失败、child仍活、close在途或UNKNOWN不会被reader结束替代。

`HostManager.console()`正常EOF、截断、16KiB超界及异常出口统一进入closeIngressAndSupervise；其构造阶段异常也进入原监督。Deployment.Processes共用监督者；activation的实际部署调用本身有finally closeSession，但前置登记存储读取/发布尚在监督者建立之前，不能宣称整个入口已覆盖。监督者会检查Process/pipe、Remote、已接受连接及registry.returned()；后者遗漏了目录遍历原holder，见第4节P1。pcIsolationAck只允许main交给同JVM中已运行的原custodian，JVM仍由非daemon线程保持。原registry/manager/remote对象不转移给新进程。

本机端点用原handle/PC PID/port/operation UUID/child PID识别原对象。CLEANUP须原配置pin、原ingress已关闭且只调用原manager允许的收尾动作；新LAUNCH/RESERVE/EXECUTE/DEPLOY/SEAL_FINAL均拒绝。生产执行不含测试controller的kill路径。监听/accept/close未知时停止后继并保留原标识，不把unknown网络状态当资源已返；永久内核失败未运行，不能承诺未知时端点总可访问。

真实本机manager JVM+child/pipe的定向记录支持已修路径，尤其原reader结束和child仍活时的原漏洞；不是仅用模拟列表或仅join已死reader。但这些用例没有覆盖Store.checkTotal原walk关闭未知及activation前置出口，故E9-F02整体不能关闭。第4节集中列出两处残留及连接上界问题，不否定上述已成立的Process/pipe证据。

### E9-F03 / 原P2：控制5秒绝对资格与不重发 — CLOSED_STATIC_LOCAL

`Processes.controlResponse/runControl → supervisor.runDecoded`采用CONTROL_NS=5e9，从原Operation登记时起计，覆盖实际启动、Process等待、pipe/reader及语法/身份/模式/seq解码。不再55秒wait后追加1秒join。到界返回PENDING、停依赖，原starter仍保留未返decoder；随后物理全返也不回SUCCEEDED。

GENERAL_NS=55秒仅保留在安装/独立证据等一般任务。已发控制先落外部intent，EXECUTE/ACK跨seq重复也拒绝。STATUS缺失不返还额度；总8/STATUS3和Android两phase各10秒不变。DECODE_DEADLINE实际5.5秒Hook和真实本机CONTROL5/LATE_VERDICT支持边界。父进程观测5～6.5秒包含调度/交接，不是放宽5秒资格。实际ADB/Android控制链路仍NOT_RUN。

### E9-F04 / 原P2：提前拒绝与并发旧grant — CLOSED_STATIC_LOCAL

`observe()`在进入类串行锁之前beginCurrentObservation清grant并领新epoch；used/ACTIVE/历史未知等早退也不能沿用旧准入。发布与require同步；只允许最新epoch和实际原返回发布grant。后来的调用已进入时，旧在途观察即使物理归还，也返回SUPERSEDED_NO_GRANT，不晚发grant。Runtime在检查catalog/context之前先撤销旧grant。

GRANT已补“成功→重复BLOCKED→requireCurrent拒绝”的原缺失后置断言；CONCURRENT_GRANT实际用本地原guard关闭latch和线程交错检查旧epoch不能晚发布。最终新Gradle类的SDK桩Runtime失效序列也通过。没有取消别的原任务；旧的物理返回事实可以保持，新的grant被撤销。真实Android观察仍未执行。

## 3. 19组／279断言的范围及UNKNOWN清理核验

最终映射19组，19次映射调用；007集中19组加008针对TRANSPORT/DECODE_DEADLINE的2次，合计21次最终验证调用。映射断言279=边界205+共享夹具74；12组使用真实本机ProcessBuilder/child，其他7组为生产管理/元数据对象。38份最终映射stdout/stderr摘要与各组断言数均独立匹配。没有累加旧32组的PASS或重复宣称跑过native套件。

| 定向组 | 已证有限范围 | 未证边界 |
| --- | --- | --- |
| TRANSPORT / STATUS_GAP | 最终生产命令与帧校验、独立STATUS、缺失seq扣额、只读封写、STATUS3门 | Android投递/冷启动/权限/实际shell返回格式 |
| IDENTITY_CLEANUP / NO_REPLAY / REMOTE | 无reserve身份收尾、原finish后Remote才返；已发EXECUTE/ACK不重发 | actor与系统finish来源为合成元数据，不是Android死亡事实 |
| GRANT / CONCURRENT_GRANT | 实际共享观察及有限并发交错，重复/被超越不再grant | UID/inode/dirsync为平台替身；未穷举所有调度 |
| CUSTODY_PIN | 同原custodian状态可查，错pin拒绝、正确pin调用原对象 | 回调只执行本地INSPECT，真实设备收尾未运行 |
| EARLY_EOF / READER_ERROR / OUTPUT_BOUND | 原reader结束或失败时真实child仍活，main隔离交接后JVM继续存活 | IO异常为Hook，不是Win32内核注错或ADB失联 |
| CONSOLE_EOF / TRUNCATED / OVERFLOW | 主console三种退出经过原结束边界，真实child/pipe与状态authority保留 | 全部输入/内存/线程创建失败未穷举 |
| CONTROL5 / DECODE_DEADLINE / LATE_VERDICT | 5秒时限含原decoder、原client未返可识别，真正晚返仍PENDING | Android实际端到端时延、全部启动失败排列 |
| CLOSE_LATCH / CLOSE_UNKNOWN | child真退出后原stdout仍CLOSING/UNKNOWN，不能发安全退出；有限latch真返后才能CLOSED | 永久内核close/监听异常未运行；UNKNOWN测试清理不是原归还 |

特别核对最终007 CLOSE_UNKNOWN：原child PID17320已经退出；stdout=UNKNOWN、allReturned=false、verdict=PENDING，stdin/stderr=CLOSED；原manager仍存活、可查询。`unknown-hold-before-fixture-teardown.json`保存了该状态；fixture-teardown明确originalCloseAck=false、productionExitAllowed=false。后续测试controller只终止这个合成manager以结束有限观察，生产holder没有变成CLOSED，stderr没有E9_PC_CLOSED。生产JAR未包含这段测试类/清理代码。**此用例PASS证明“未知时拒绝安全退出”，不证明“UNKNOWN已关闭成功”。** CLOSE_LATCH在原close真实释放后自然记录E9_PC_CLOSED，与UNKNOWN口径不同。

首次main-001本机Socket.connect被沙箱阻止，原custodian继续保持，诊断查询超时与精确夹具无ACK清理均保留，不能计PASS。004/005的失败由测试将conhost.exe误计业务child引起，原失败、修正和006/007复验保留；未据此改松生产原返回门。本轮tester没有再连接这些历史本机端点或重启任何夹具。

六个最终Android公共入口使用SDK桩，Runtime失效序列使用合成共享元数据；Binder、真实raw/dup、目录barrier、boot/start、normal finished inst与新host实际观察仍NOT_RUN。合法R/S后缀、真实原锁/FD与32组历史证据的适用范围继承E9报告，不把未重跑写成新增通过。

## 4. 集中残留与新增问题

### E9A-F02 / P1，原E9-F02残留：registry返回判断遗漏原walk，activation前置IO未进入监督

位置：[E9Registry.java:52](D:/CodexProjects/VideoKit/docs/coder/d1e9a/src/com/videokit/spike/e4/E9Registry.java:52)的checkTotal及其局部walk、[Store.returned](D:/CodexProjects/VideoKit/docs/coder/d1e9a/src/com/videokit/spike/e4/E9Registry.java:33)、[E9HostActivationSession.java:19](D:/CodexProjects/VideoKit/docs/coder/d1e9a/tools/E9HostActivationSession.java:19)。静态见证如下，未新增故障运行：

1. Store.checkTotal用局部E4Owned<Stream<Path>>持有Files.walk，只在局部finally close；没有把walk登记到outstanding或任何原Store长期owner集合。若walk分配/close返回不明，holder保持UNKNOWN/未返；close异常只将healthy=false。Store.returned()却仅遍历outstanding中的IO holder，不检查walk；healthy=false也不是原walk返回证明。
2. HostManager受管初始化/部署会调用registry.initialize/create/checkTotal。假设原普通文件IO都已实际关闭、尚无Remote/Process，而walk.close抛异常：构造finally将authorityCallActive置false，main结束边界询问registry.returned()可得到true，监督者可产pcClosed并移除LIVE；局部未知walk随栈退出失去原管理者。该路径同已覆盖的“stdout UNKNOWN会保留”不同，不能用后者代证。
3. activation的openKnownHead与recordActivationRelease在第24行new Processes/supervisor之前执行。若该阶段的registry FileChannel open/close UNKNOWN，异常可直接结束main，没有原custodian和持续强根；finally closeSession只覆盖后面的deploy。`--approved-export`同样先open registry，而无监督生命周期。虽然activation目前未派发，这段实际工具代码也不能声称全入口异常出口已闭合。

影响：已有定向验证支持Process/pipe保留，但原登记存储资源仍可能被遗漏并发生不成立的“全部已返”结论。初始registry路径与未来发布路径均涉及此规则。没有记录到真实资源泄漏或实际错误pcClosed；这里是可定位的静态异常路径。

修复要求：原Store的目录walk等全部原资源须在实际IO前登记并持续强持有，returned()须覆盖它们；不能仅以healthy=false阻断下一步而遗漏原返回。区分业务失败但资源真实已返与UNKNOWN，不用把所有失败永久冒充在途。activation的registry open/export/release前置阶段也应从原监督生命周期开始，登记对象构造完成前后的异常都进入同一结束门。补有限本机故障切点：walk CLOSE_AFTER UNKNOWN不得pcClosed；原资源真返才允许关闭；activation前置registry异常也保持原holder/监督。沿用合成夹具收尾口径，无设备、无真实release或token；不需native重编，是否需要一次集中APK构建取决于是否修改了封存的共享Android输入。

### E9A-F01 / P2：128是处理拒绝门，尚不是本机连接次数硬界

位置：[E9PcSupervisor.java:119](D:/CodexProjects/VideoKit/docs/coder/d1e9a/tools/E9PcSupervisor.java:119)、[第125行](D:/CodexProjects/VideoKit/docs/coder/d1e9a/tools/E9PcSupervisor.java:125)、[第141行](D:/CodexProjects/VideoKit/docs/coder/d1e9a/tools/E9PcSupervisor.java:141)。

静态见证：先accept并登记Socket，之后才`++accepted>128`抛错；超界连接如close实际成功，supervise的catch发现没有未返client，不置statusTransportUncertain，下一轮仍调用acceptAndServe。故129、130……连接均可继续建立后拒绝，未实现文档“最多128个本机状态连接”的硬界。超界不会执行STATUS/OP/CLEANUP回调，不会新增Android权限或把UNKNOWN标成CLOSED；也不会累积已关闭holder冒充仍占用。这是连接成本/耗尽处分与承诺不一致，不是新的产品激活绕过。

边界128/129的实际连接用例NOT_RUN；19组不覆盖。建议后续集中修订为accept前的明确接入门与耗尽后的原custody状态/报告，同时保留现有原对象，不能靠kill或重复监听规避。若设计本意只限“最多处理128请求”，应明确修订连接成本承诺及有限异常拒绝成本，不能继续声称硬连接总数128已实现。

单独看该P2，低请求量只读批次可以用明确的本机查询预算避开耗尽路径；但当前还有上面的P1，故本报告不授予设备准入。建议将两项一起集中修复和定向核验，不以另换scope/监听端口绕过上限。本轮不另起子进程或追加候选测试。

## 5. 下一准确准入：先集中工具修复，再决定设备只读批次

当前建议负责人先派第4节两项集中工具修复，保留已通过的生命周期/控制/观察证据，仅补受影响切点并重冻源码和host JAR，避免机械重跑19组、32组或native。若Android源未变，沿用已核双APK和构建输入，不为纯PC修改重编APK。tester关闭P1并复核限额后，才考虑下面的**一台HA1Q6WXR、一个显式READ_ONLY_IDENTITY actor的有限身份/控制验证候选范围**：

1. 按最终version12双APK与JAR精确摘要核当前设备、user0、实际原安装pair/原UID/原签名和无相关在途进程；是否需要安装由该批准确需求决定，不能把本轮没有查过的设备状态当新证据。使用实际受审managerTrust/config pin及有限外部registry范围，不把任意64hex当批准。
2. LAUNCH必须显式mode=READ_ONLY_IDENTITY，不利用兼容默认REGISTERED_MIGRATION。仅核非等待启动client实际归还与Android actor独立存活、有限DUMP状态通道、真实boot/start/原FD返回和5秒控制链路。Android请求总≤8、STATUS≤3，本机端点总连接≤16；禁循环轮询、重发EXECUTE/ACK或自动扩额。此批**不发RESERVE/EXECUTE_COMMIT/SEAL_FINAL**。
3. 原身份/回执符合实际资格时，只归档同一return bytes、唯一精确ACK_FINISH并独立核normal finish/原PID缺席，最后核PC原责任与pipe归还。client退出、磁盘文件或finishClaimed均不能代替。失败、receiver缺失、身份不可验证或任何UNKNOWN立即停止依赖，保留原custodian和可识别handle；只能按原scope有限收尾，不能自动kill、换scope/handle、actor2/3或以管理员终止JVM充close。
4. readonly scope完成不产生COMMIT/final authority，也不自动复用为写迁移scope。设备批次独立出报告，实际证据齐全后负责人再决定写迁移方案和scope；真实final facts/canonical catalog独立接受后才讨论activation发布。同一实现与精确catalog/head约束继续有效。

以上仅供后续需求编制，P1未关闭前不得以它开始设备测试；不是本轮发出的设备指令。本轮不自动连接或开始测试，不请求重复平板设备使用授权，也不生成迁移许可。

原N2一次ABORTED_SETTLED/0B、原budget `730a73e1-50e1-4198-a515-047104f00e31`、107218消费/三R三S/reserved0、原0B输出/前像/pending归档、fence `662e9ecd-bede-42e6-bb58-ce81d668ff44`、oldCloseACK=false及旧根因UNKNOWN保留。它们是历史已接受事实，本轮未重读设备。1011B已接受前缀后允许合法完整R/S追加，不能冻结整个账本为永久1011B。

设备4文件8448B/3目录、PC20种元数据155648B且≤192KiB+原日志1MiB、catalog16KiB≤24KiB、2actor/各8控制STATUS3、Android两phase各10秒、48新增Android holder，以及原预算4MiB/单项2MiB/128任务均不扩大。新增PC96操作记录与128处理门不改变Android额度；连接硬界缺陷按第4节保留。严格六帧/完整EOF/1000us、独立Kit/Flutter、许可状态与其他全部P0保持。

报告冻结后主动发送负责人，通知回执另存于本报告证据目录；旧E9报告保持原结论和时间，不回改历史审查。
