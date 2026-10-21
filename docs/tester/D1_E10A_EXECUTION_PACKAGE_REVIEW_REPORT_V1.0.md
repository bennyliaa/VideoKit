# D1 E10A 实现与精确执行包独立复审报告 V1.0

2026-10-18；tester；依据 `docs/milestones/D1_E10A_TESTER_REQUIREMENTS_V1.0.md`。审查四执行文档/HANDOFF、候选实际生产源、APK/JAR与构建来源、12组已有定向记录、机器计划与未生效模板。未运行候选工具或测试。

**结论：完整性 PASS；E10-PREEXEC-BOUND-CLEANUP / P1及E10-POSTARCHIVE-STOP / P2均 CLOSED_STATIC_LOCAL。SUPPORTED_FOR_EXACT_ACTOR1_EXECUTION_PREPARATION，支持负责人另行确定并派发准确单actor1迁移批次；本报告不是实际写执行许可。无新增阻断实现缺陷，保留一处非阻断文案说明。**

支持范围是源码审查和有限本机证据，不是Android写迁移/取消/故障PASS。本轮设备/ADB/构建/候选测试重跑/媒体/实际UUID生成/scope签发/写迁移均0，无实际token/H_actor/catalog/activation。D1 NOT_PASSED、M0 NOT_STARTED、长期准入OPEN；其他P0/许可及历史FAIL保持。

## 1. 冻结完整性与来源

独立审计：[independent-review-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_E10A_EVIDENCE/independent-review-audit.json)。仅自编只读元数据/AST审计，没有运行候选校验器、打包器或生产代码。

| 核验对象 | 独立结果 |
| --- | --- |
| 外seal | SHA256 `0a2d1c3a6c02f6194427ca93688a804f7df8d7966ffedb1ee0324cbccaf7d090`；463项immutable全匹配 |
| 清单/ZIP | manifest461项全匹配；ZIP462文件逐项与磁盘相同（含清单）；463 immutable另计ZIP |
| ZIP | 24396414B；SHA256 `53986b28eb4ce2f01f730b8774ba8bd049c97be1b7ad1d13cfa22a61ea057a37` |
| 外部来源/历史 | 32项external输入匹配；原E9B402项和E1067项/各原seal不变；旧只读manifest127项全匹配 |
| version14 app | 10659394B；SHA256 `611672a9f2a7eab3f08a495832d513e79ee446cb1a9f99001fe323e944f2af54` |
| androidTest | 2749733B；SHA256 `2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b`，与E9B相同 |
| 生产host JAR | 261552B；SHA256 `8f5cbce3461d61fecf4c9bc1c026e66ddc4ed3ee1f9ab705ecdebaa594f800a0` |
| 编译来源 | 159生产class逐项匹配源码摘要、targeted-002和console-003编译class及最终JAR；无测试类，156个类与E9B相同 |
| 最终Android输入 | 163项全匹配；SHA256 `77bae40d39c2a390e149335302681ab71e362deac933145e8888098febdd45d9` |
| 继承 | 130项严格逻辑/原生继承输入、73项Android入口继承输入匹配；7个so摘要/ELF LOAD 16KiB对齐匹配；35坐标/7库差集为空 |
| 定向证据 | 26份原stdout/stderr/夹具收尾pin、126份trace和2份最终输入pin匹配；12组result与映射断言/结束状态一致 |

原签名证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`：已归档签名审计与最终APK匹配，本轮未重跑签名工具。共享Registry已进入Android输入，因此一次main-001必要离线构建合理；原日志BUILD SUCCESSFUL in 1m、68任务，无repair/native重编/下载。AndroidIdentity版本门准确更新14；Run/Instrumentation/IO/ABI1与原继承范围保持。

targeted-001在测试资源callback未处理checked Exception处编译失败，无用例执行，前像与失败日志保留；002通过11组，003只加console用例和原child合并stdout记录。001/002输入中的旧测试源码分别精确对应两份before副本，003全部匹配，无未解释差异。不能把首次测试编译失败描述成APK构建失败，也不能用后续成功覆盖历史。

## 2. P1：BOUND未EXEC取消收尾 — CLOSED_STATIC_LOCAL

[E9Registry.captureIdentityForFinish](D:/CodexProjects/VideoKit/docs/coder/d1e10a/src/com/videokit/spike/e4/E9Registry.java:129)不再一律拒绝存在reserve；存在BOUND时进入严格原证据校验，[validateBoundIdentityCancellation](D:/CodexProjects/VideoKit/docs/coder/d1e10a/src/com/videokit/spike/e4/E9Registry.java:141)核：

- 当前回执是实际IDENTITY/PENDING/EXTERNAL_STOP、executeDone=false、无device/未返资源；原qualified identity的时间、owned相同且新stateSeq更大。完整actor canonical字节包含原出生身份，不能换actor/boot/start。
- 原launch、plan/authorization、精确reserve、同registry/migration及最后BOUND head/evidence全部绑定；磁盘events与原内存连续链、prepare-deployment原字节一致。
- 命令同handle/连续seq，存在唯一STOP；任何EXEC或ACK意图均拒绝。不能只用executeDone=false或缓存旧IDENTITY排除已预留/在途执行。

原Run未改：有已预留execute而未实际归还时actualSafe=false，不会产生可归档新return；STOP形成永久sticky PENDING，bindAndReserve不再允许。主机/registry额外禁止STOP后EXEC与第二STOP。取消条件因此不是由调用者一个true自报。

成功分支复用已存identify/reserve原字节，不再CREATE_NEW冲突或覆盖原qualified identity；只新建当前真实停止return并追加BOUND_IDENTITY_CANCELLED_NO_COMMIT。该原return可唯一ACK、独立normalfinish、归还Remote/PC责任。sealFinal/requireRecovery仍要求COMMIT原返回，身份取消不授final或actor2资格，也不新增device三文件。

实际生产对象的BOUND_CANCEL/NOT_STOPPED/WRONG_ACTOR/WRONG_RESERVE/WRONG_HEAD/WRONG_PLAN定向记录支持拒绝条件、原字节保留、零device写、错误ACK不消耗、唯一finish。负例中的篡改/恢复仅在SYNTHETIC夹具中用于完成有限测试，不构成真实registry修复方法。EXEC_INTENT_ISOLATION已登记EXEC意图但故意不投wire，再直接调用原Run.stop，证明真实取消proof也不能抹除原EXEC意图；这不是host能合法发送那个错位STOP的证明。

## 3. P2：终局/已归档STOP与错ACK — CLOSED_STATIC_LOCAL

[HostManager.prepareControl](D:/CodexProjects/VideoKit/docs/coder/d1e10a/tools/E9HostManager.java:64)为实际CLI共用公开入口。它在持久化intent前检查已归档returned、finishClaimed、已STOP，以及safe且executeReserved的已知COMMIT终局；不适用的STOP不会进入wire。原R0不因该拒绝生成R1。

ACK先核已归档原字节与当前原proof完全相同，再调用commandIntent；[control:76](D:/CodexProjects/VideoKit/docs/coder/d1e10a/tools/E9HostManager.java:76)在prepare成功后才推进nextSeq。Registry在append前再拒归档后STOP、重复STOP/STOP后EXEC和重复已发EXEC/ACK。重复ARCHIVE也在CREATE_NEW之前拒绝，不用故意制造文件冲突毒化Store。已经发出且未知的EXEC/ACK仍不可重发，前置拒绝不代表可恢复已消费意图。

TERMINAL_PREARCHIVE_STOP/POSTARCHIVE_STOP/FAILED_RETURN核原proof、归档、commands、seq及wire计数均不变，之后唯一精确ACK/normalfinish仍可完成；FAILED COMMIT/device ABSENT可以实际收尾而不能final。未知COMMIT原close则仍没有可用return，不被新身份取消口收走。

源码中原operation失败仍置manager.failed；只允许原scope的CLEANUP白名单，禁止RESERVE/EXEC/SEAL，不把成功清理变成发布资格恢复。阶段化失败表已与新入口一致，不再要求每个失败切点机械发送STOP。

## 4. 12组本机证据的准确边界

383边界断言+222共享合成夹具断言=605。最终12组来自002的11组和003新增1组，不重复跑旧19/32/24/native。10组真实本机正常结束且有E9_PC_CLOSED；2组保留原责任、无E9_PC_CLOSED、originalCloseAck=false/productionExitAllowed=false。

| 已证范围 | 限制/NOT_RUN |
| --- | --- |
| 实际生产Registry/Run及HostManager.prepareControl，原字节/意图/seq/wire前置拒绝 | metadata/身份/控制/系统finish均为SYNTHETIC替身，不是Android写/取消实测 |
| 原ProcessBuilder子进程、5秒响应decoder、真实console异常和共用entry/custodian结束边界 | 子进程只输出模拟广播响应，不是adb.exe或DUMP权限实测 |
| CONSOLE拒绝后，经Processes.controlResponse(cleanupOnly=true)和原Run/Registry/Remote完成精确ACK/normalfinish | 没有运行获批DEVICE CLI，没有通过真实manager.custodialCleanup的CLEANUP IPC回调执行这一错误出口 |
| 原operation.failed/CLEANUP白名单和SEAL禁止的源码接线核对 | private manager.operation的failed标记与真实IPC整体路径未由新增用例运行，不扩大console回调的证明范围 |
| EXEC_INTENT_ISOLATION、UNKNOWN_COMMIT_CLOSE拒绝伪归还且原custodian继续持有 | 两组controller只在真实child已返后结束专用合成JVM；这是有限测试清理，不是生产close或Android安全结束 |

CONSOLE用例实际使用共享console/prepareControl及原Processes清理标记，证明这些组件组合可按原回执结束；未实例化真实Device配置或绕过环境门。其Driver的cleanup callback不是完整生产manager的私有IPC处理器，报告据此限制运行结论。源码接线与同一个公开前置门已独立阅读，未发现新增执行阻断。

002保留child argv、canonical frame和测试JVM原stdout/stderr，没有逐次保存child raw stdout；003额外原样保存合并输出。两组隔离的测试退出结果由controller归一化为断言PASS，不能视为原监督者自然exit0。原UNKNOWN仍无Java ACK、无第二close；这不证明所有故障都可正常退出。

原Android raw/dup/guard/目录force、实际COMMIT或取消、真实网络断连/超时、普通发送者DUMP负例、实际CLEANUP IPC及全部调度排列仍NOT_RUN。原E9B只读真机PASS只证明当时version13身份/控制正常路径，本包没有据它宣称version14实机通过。

## 5. 执行包、部署与授权绑定

机器plan、preparePlan、scope.artifactPins及12个条件命令一致：实际部署来源为**E9B version13精确pair**，目标为**E10A version14精确pair**；manager-config.originalVersion=13/originalRole=PREPARE/ABI1，candidate plan.version=14。00-DEPLOY_PREPARE安排原门两条install-r各一次保数据、安装后核pair；现场来源若已变化或已有在途任务必须停，不能重复安装或绕门。此刻没有现场预检或安装动作。

descriptor仍725B，commit仍244B；单actor1仅actors/0001.intent≤2048B、n2-v2.acceptance725B、n2-v2.commit244B，内容≤3017B/分配上界6400B、最多3新目录，FS目录项/块/journal成本另计。原三R三S/107218/0reserved、13metadata、0B/S0、guard/fence及合法settled后缀保持；无原R/S追加、媒体payload、ABORT、预算重置。

scope是DRAFT_NOT_EFFECTIVE，四新UUID/issuedAt/正式派发/acceptedE10AReviewSha256均null，newIdentity/currentDeviceFacts也为null。未来scope真实字节→plan.authorization，新接受的本次修复审查SHA→sourceReview/review，plan→config→index单向。12模板有templateOnly外壳，不能直接送CLI或无条件串行喂完；新STOP只在BOUND未EXEC的严格取消分支使用。

正常链仍是新REGISTERED_MIGRATION身份→BOUND→唯一EXEC→原COMMIT真返→精确归档ACK→独立normalfinish→当前三文件/旧账审证→SEAL_FINAL；取消链是STOP→原IDENTITY取消归档→唯一ACK/normalfinish，**不SEAL**。正式scope需由负责人采纳新终局策略、三文件与一次actor1/受管部署并另行派发；本轮不生成这些身份或文件，也不复用已结束只读scope/旧E3许可。scope SHA是实际授权内容绑定，不是随机token或资源返回证据。

只读校验器的AST/源码无网络、subprocess、文件写或UUID生成；已有准备与拒绝性校验只证明静态绑定。它不认证采集者真实性、当前设备值或owner实际返回，九个true及原receipt pin仍须独立审证。完整bound正向现场fixture未运行，status仍PENDING_INDEPENDENT_REVIEW_NOT_AUTHORIZED，与未派发状态一致。

Android≤8/STATUS≤3、EXEC/ACK各1；常规链4或5控制、取消3控制；本机STATUS/OP/CLEANUP合计≤16共用原128accept、Process≤96、独立metadata客户端≤20、原日志1MiB/登记20文件155648B、48owner、5秒响应含decoder及两phase各10秒均不放宽。额度耗尽后端口不可用但原custodian仍持有，不换port或新manager扩额。

## 6. 非阻断文案说明与后续精确准入

ACTIVATION_INPUT_DAG第2步仍写“E9B固定APK SHA”，是旧名称残留；机器计划、模板、runbook、制品表与后文已准确使用E10A14。后续输入应采用本报告第1/5节**version14目标pair**，E9B13只作部署来源；不能按这句旧文案改回旧candidate。建议下一文档版本更正，无需为名称重编APK，也不修改当前冻结。其余DAG为真实scope→plan/config→原actor/COMMIT/normalfinish→真实catalog/head/checkpoint/seal→独立接受→另派activation导出/构建→实际APK入release→部署/每新host当前观察，没有哈希环或提前创建H_actor。后续activation版本须>14。

当前实现和包准备程度支持负责人另派准确actor1批次，执行前仍须：真实scope及新一次身份落盘、当前13来源pair/原UID/无在途/13metadata/完整ledger/无pending/新M缺席/日志容量等原receipt重核，受管更新14，再按条件原生产链执行。预检失败或未知即停，不以本静态报告补当前事实。任何COMMIT/正常finish/final门缺证都保留隔离，不覆盖、kill、重放或直接生成catalog。

本轮不自动派发或启动迁移。真实终局独立审查通过后activation仍单独安排；PREPARE/catalog ABSENT不授产品grant。D1未过、M0未启、E6B-OBS-F01长期准入OPEN，Framework/独立Kit/Flutter、严格六帧/full EOF/1000us和全部许可/P0不变。报告冻结后主动发送负责人并保存回执，设备继续停止。
