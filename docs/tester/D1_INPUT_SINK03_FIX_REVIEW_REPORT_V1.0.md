# INPUT_SINK03_FIX 整包独立离线复审报告 V1.0

2026-10-21；tester；候选 `D1-20261021-INPUT-SINK03`。

**整包结论：FAIL。原 B03/P2、B04/P2 的指定修复有限离线通过；追加负向检查发现 B05/P2：QUERY 终局结果校验遗漏，另有 C01/P3：文档所示独立复核入口拒绝本批输出目录。** B05 在准确冻结源码编译类与交付生产 JAR 优先加载两条路径均复现。请集中修复并重新冻结整包交测，不把已有修复和依赖通过扩大为整包通过。

本轮完整阅读正式测试要求、DELIVERY、EXCEPTION_MODEL 和 INDEPENDENT_CHECK_PLAN，按已有 JDK 外置检查。设备/SDK/ADB/5037/占用/旧handle查询为0，Gradle/Android构建、共享缓存写入为0。D1 `NOT_PASSED`、M0 `NOT_STARTED`，真实平台及业务发布仍 `NOT_RUN`，本轮完成后不自动下一批。

## 1. 候选身份与保全

| 对象 | 独立核验 |
|---|---|
| 主报告 | SHA256 `60c9dd6655384a13f34eaa5da0df1d640f22c0d1fabc4769d8ef4c39093633d4` |
| Seal | `0a9bc068282e3fba8737a1c8c8f426cb2256ddb36feb28c139166ad0921c893a`；629条文件字节/hash逐项一致 |
| ZIP | 628个唯一条目与seal一致；`93fb6654bfd976bcf5c48f68a3153d716b6eb07f0d404d46f5ca154f32bcfd79` |
| 生产JAR | 87,238B；`f053ad930c2f5cdaadc60cfe9157d190212e1f0b2620d0f04631af06382d00ab` |
| APK | 6,396,874B；`aab5754708e29f58ed0c1452db71895bf655eb0e9c363020a985271636bd3a20` |
| 最终输入 | 1,037条准确源/依赖输入全部核对 |
| 历史候选 | RENDER01 477、RENDER02 404、capture818、INPUT_SINK01 334、INPUT_SINK02 316，共2,349项及五个原seal逐项保持 |

见 [frozen-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/frozen-audit.json)。旧 INPUT_SINK01/02 FAIL、tester旧114/207份证据及其原报告均保留，不修改旧失败或UNKNOWN。历史N2停止范围不影响本新离线批。

## 2. 原 B03/B04 与原阶段门裁定

**B03：PASS_LIMITED_OFFLINE_FOR_ORIGINAL_FINDING。** 原stage首次等待及晚observe能消费直接CancellationException，清除该已消费pending，并转为稳定IOException；原私有message/cause不向外传。tester另写六阶段独立检查，嵌入私有message与私有cause，对WRITE/FLUSH/CLOSE/REOPEN/VALIDATE/COMMIT逐一核稳定code、首错、消费一次、反复observe不重RPC。WRITE宿主实际发4B而ACK下界0/callerPos0，UNKNOWN reservation准确4且只记一次。SDK未主动cancel原future，原timeout和UNKNOWN不退款。

原晚取消输入也回归通过：实际原write线程执行4B，caller之后修改不影响原private block，晚取消被消费，同原线程join后可以按真实失败收尾。既有首错保留。调用内直接抛取消、包装ExecutionException、正常/晚成功/晚失败/晚取消在九阶段矩阵分列，普通失败不再反复悬挂原ACK_PENDING。COMMIT无业务ACK时不推断未执行、回滚或成功。

独立证据：[六阶段源码路径](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/independent-cancel-source.stdout)、[生产JAR路径](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/independent-cancel-production.stdout)、[同原晚取消](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/latecancel-production.stdout)。

**B04：PASS_LIMITED_OFFLINE_FOR_ORIGINAL_FINDING。** ABORT/QUERY实际进入后的timeout及时记录 `OUTPUT_TIMEOUT_PENDING`，原ABORT失败后准确QUERY证明ABORTED仍保留 `OUTPUT_ABORT_UNKNOWN`。原晚ACK/终态/资源返回不清首错，原ABORT/QUERY各1次。ABORT早ACK尾段未返、QUERY尚未准入的瞬时pending仍不制造失败。

对deadline边界额外读源码核证：`cleanupFailure`检查本次等待异常链的 `OUTPUT_STATE_UNKNOWN` 及对应原动作已进入标记，不只依赖view当前done；即使晚ACK在catch处理前完成，已观察timeout仍登记。动态覆盖真实timeout→同原晚ACK/原尾段→终态返回；精确到catch前几条指令的调度竞态未作确定性注入，源码因果分支和动态晚ACK分别作为证据，不冒称可精确控制该调度时刻。

证据：[ABORT timeout](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/history-abort-production.stdout)、[QUERY timeout](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/history-query-production.stdout)、[ABORT先发生副作用再失败](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/history-abort_error-production.stdout)。

原B01/B02指定场景继续通过：未准入不消费flush/close标记，同原WRITE/FLUSH/CLOSE尾段join后flush1/close1；validator/COMMIT独立原authority、READY/REOPEN/ABORT/QUERY尾段、原读回registry/worker和coordinator线程归还门保留。COMMIT原ACK早到时业务ACK与资源返回分列；未返不移除keeper，不退款UNKNOWN。此结论不覆盖本报告新增的非法QUERY结果分支。

## 3. 新增 B05 / P2：非法 QUERY 终局结果没有验证，null抛原始异常，空READY token被接受

位置：[TemporaryOutput.queryHost](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/src/com/videokit/d1input/TemporaryOutput.java:120)、[SinkCoordinator.abortBeforeReady](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/upstream/com/videokit/spike/c14/SinkCoordinator.java:64)。新包已验证REOPEN/VALIDATE终局值的类型/内容，但QUERY view在error为空时直接转发结果；READY只检查token非null，没有检查非空。旧coordinator随后直接解引用结果，并同样只检查token非null。

tester只在宿主端口注入非法返回，不修改产品状态或伪造SDK成功。宿主原ABORT实际将状态变成ABORTED，QUERY原调用恰好1次、全部原任务已返；随后模拟坏的QUERY响应，默认terminal authority保持UNKNOWN：

| 注入 | 准确观察 |
|---|---|
| QUERY返回成功stage、结果null | abort直接抛 `NullPointerException: Cannot read field "state" because "result" is null`；queryPhase=ACKED、firstFailure=null、owner未返，未转稳定失败 |
| QUERY返回 `Status(READY, "")` | 没有异常，readyAck=true、readyToken为空、firstFailure=null；`finishOriginalCallbacks()`可使ownerReturned=true |

该阶段输入不合法，应在更新READY/ABORTED事实或交给coordinator前拒绝。`markReady()`已要求token非空，`observeTerminalAuthority()`也要求非空，而QUERY路径使用更宽松条件，导致同一候选的终态接受规则不一致。第二场景不证明真实READY或业务COMMIT发生；它准确证明SDK把非法响应接受成READY、并据此通过释放条件。原宿主实际终态为ABORTED，不能将此坏响应称为准确业务证明。

预期：null、缺失/空READY token等非法结果作为该原QUERY的稳定失败消费并保留首错，不能发布READY、不能新RPC补绿；没有有效终态证明时按UNKNOWN保管。后续可依据准确原task的既有authority证明收敛，不改已发生的RPC事实。实际null分支越过稳定IOException边界，空token分支制造无有效token的READY。

修复建议：集中校验原QUERY成功结果，统一原QUERY、readonly terminal authority和coordinator的终态/token条件，先记准确失败再完成缓存view；同时防御旧coordinator的null解引用。不要仅在外层捕获NPE后继续接受空token，也不要把无效结果猜成ABORTED。保留原RPC一次、原任务归还和UNKNOWN边界。

双路径证据：[null生产JAR](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/invalid-query-null-production.stdout)、[空READY token生产JAR](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/invalid-query-empty_ready-production.stdout)，以及同目录source日志。null分支采证后仅用宿主真实原ABORTED记录开启只读authority完成清理；没有反射改SDK状态。空token场景保留实际错误状态，所有原资源已实际返回。

## 4. 新增 C01 / P3：独立复核入口仍限定 INPUT_SINK02 目录

位置：[local_check.py:5](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/tools/local_check.py:5)。独立计划要求输出到 `D1_INPUT_SINK03_REVIEW_EVIDENCE`，但冻结脚本仍断言路径必须以 `D1_INPUT_SINK02_REVIEW_EVIDENCE` 开头。按文档指定本批新目录执行，立即 `AssertionError: INDEPENDENT_TESTER_ROOT_ONLY`，未创建目标目录。

证据：[原stderr](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/documented-entry.stderr)、[准确参数及退出回执](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/documented-entry.json)。本轮在tester新目录编写独立JDK编译入口，使用相同冻结源/真实deps继续完成全部审查，未改冻结脚本、未把新产物混入旧207份证据。请新候选改为准确本批目录并同步文档；本项本身属于可绕过的复核工具问题，不是平台业务效果失败。

## 5. 新 readonly authority 的独立边界

tester新增三项独立检查，不仅采用coder的临时boolean结果：

- 原COMMIT失败ACK后，准确原task/token的readonly accessor默认UNKNOWN。反复observe/finish不重复COMMIT，不提前返owner。
- 宿主相同原COMMIT的实际副作用分别为发生/未发生，原宿主查询线程从该真实记录读取，查询ACK已到而同原查询尾段仍活时，SDK不接受终态；join同一查询线程后才接受CONFIRMED_COMMITTED或CONFIRMED_NOT_APPLIED。
- QUERY ACK失败且原查询尾段未返时继续保管；join后默认UNKNOWN仍不释放/重RPC，只有同原task准确已保留的ABORTED事实可收敛。ABORT1/QUERY1，首错不改。

分别核原task/token参数、RPC数、readonly accessor调用与原查询线程身份。业务确认COMMITTED可与原 `commitAcknowledged=false`并存；NOT_APPLIED不会被登记为SDK回滚/ABORTED，也不抹掉已证READY或首错。未用取消、线程已返或无ACK推导业务终态。证据：[独立authority源码路径](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/independent-authority-source.stdout)、[生产JAR路径](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE/independent-authority-production.stdout)。

该有限通过仍依赖真实宿主诚实实现同原task/token、非阻塞、无新RPC的端口契约。SDK当前通过参数绑定和原物理返回门接受端口事实，没有独立验证宿主自身持久化账本/真实跨进程业务；真实authority集成与发布效果NOT_RUN，不因本轮受控端口通过而获得产品放行。

## 6. 实际执行及十九项矩阵

源码与生产JAR优先两路径均实际执行：原20语义组、原17尾段、原tester23场景的安全回归、九阶段63项异常矩阵、输入5项。重叠场景不相加冒称新增独立用例。完整阅读并检查了矩阵的ACK/EXEC/CANCEL/LATE_ACK/LATE_EXEC/LATE_CANCEL/THROW_CANCEL断言及不适用项，不只引用coder计数。

额外tester自写六阶段私有cause取消检查、三项原authority检查、两个非法QUERY检查均双路径运行；另执行文档入口失败的本机检查。全部production回执以交付JAR为classpath首项并核实际ORIGIN；源码类没有遮住生产类。原12项和读回检查与旧tester源码身份保持，旧失败复现源码/日志没有改写。

| 清单 | 独立裁定及范围 |
|---|---|
| I01 | PASS_LIMITED：真实DataSpec/TransferListener、3+3+1短读、准确range/offset、EOF和重复open/close |
| I02 | PASS_LIMITED：未知长度-1，3+2后EOF |
| I03 | PASS_LIMITED：3GiB+7逻辑offset、64KiB读块，无巨大文件 |
| I04 | PASS_LIMITED：long溢出先拒绝，caller不改、host不调用 |
| I05 | PASS_LIMITED：0/-2/超count结果拒绝；QUERY非法值为另一阶段问题B05 |
| I06 | PASS_LIMITED：输入权限及取消映射，新增输出Cancellation私有message/cause已脱敏 |
| I07 | PASS_LIMITED：同DataSource读重入拒绝 |
| I08 | PASS_LIMITED：cancel与迟到private buffer、caller不覆盖、同原结果等待 |
| I09 | PASS_LIMITED：双consumer首关闭不足释放，原handle/stage/线程归还 |
| I10/A01 | PASS_LIMITED：共享源峰值1/queue0、global2、跨factory同provider拒绝 |
| I11 | PASS_LIMITED：旧epoch原归还后开新range，offset7数据正确 |
| I12 | PASS_LIMITED：原FAILED close仅走显式原API恢复，不盲重试PENDING/UNKNOWN |
| S01/A02 | PASS_LIMITED：physical10/ACK3/caller3、private block、即时/晚取消UNKNOWN一次登记，不回退重发或退款 |
| S02 | PASS_LIMITED：16MiB候选资格边界，超限前无新host write |
| S03 | PARTIAL_FAIL_B05：原close/flush/UNKNOWN/尾段及B01/B03/B04修复通过；cleanup的非法QUERY结果校验失败 |
| S04 | PASS_LIMITED：真实4B宿主文件写/force/close/reopen、摘要/验证拒绝及读回原registry返回门 |
| S05 | NOT_RUN_PLATFORM：真实Android FD/fsync、codec/muxer及容器重开故障未执行 |
| S06 | PARTIAL_FAIL_B05：正常READY/COMMIT分层、原B02、ACK/业务结果/真实返回分列通过；QUERY空token错误接受READY失败 |
| F01 | PASS_LIMITED：真实Media3接口、依赖/产物身份通过；C01独立工具入口错误另列 |

seed539365408；最大有限测试块65,537B。实际生成文件为4B，每份SHA256 `e6e8cb429864b8e8d7fe95e53360dbd00756316813fb1e4a03a778d4632dbde6`；大offset受控提供，不创建巨大文件。16MiB预算用复用64KiB块计数。受控validator、readonly authority和COMMIT不是实际媒体/业务发布，JVM URI/errno/WorkerRule端口不是Android实际故障。

## 7. 依赖、最终构建和产物

15runtime坐标、两锁、verification XML、真实deps与INPUT_SINK02逐字节不变，无新增版本/pin/下载。1,037条最终输入匹配。本次最终build-main-002的632行事件中296实际验证项逐项绑定ID、artifact/坐标、原pin及缓存字节，121binary/35module/140POM，175份metadata副本一致；strict verification、verify-metadata=true、LockMode.STRICT保持。原三依赖有限离线来源/Apache准入不扩大为release许可。

build-main-002原receipt exit0，最终日志BUILD SUCCESSFUL；build001的superseded.json保留旧APK hash与deadline修正说明，未用其充当最终源码构建。本轮仅审原证据和已有JDK执行，未重跑Android构建。产品改动仅TemporaryOutput/HostOutput/AndroidGrantedStream，原SinkCoordinator、输入、bridge/registry、成熟muxer未改；B05是追加发现的同类既有结果校验缺口。

APK二进制manifest：com.videokit.d1input/versionCode3/min31/target36，无权限、四类组件/native .so；DEX4,394类，生产JAR53项。真实适配存在，检查helper/JVM URI/errno替身不在产物源集与准确审证范围内。独立已有JDK+固定官方apksig库验证v2和单证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，没有调用SDK工具。平台Android authority新增只读委托仅ABI/静态核证，运行仍NOT_RUN。

## 8. 原资源清理与集中返修

每个原受控动作及其查询尾段均由真正执行该动作的同一原线程完成并join，原registry/coordinator线程按既有门归还。默认UNKNOWN期间keeper保持；得到准确原task业务事实且全部原任务返回后才清理。所有测试最终source/output keeper归0，实际JDK子进程/管道已退出，没有反射删除keeper、退出JVM掩盖未返资源或设备在途操作。

完整证据：[D1_INPUT_SINK03_REVIEW_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE)。保留准确source pins、argv/退出回执、两路径完整stdout/stderr、case矩阵、身份/签名审证和最终证据manifest。C01只用外置编译绕过，不修冻结源码。

请负责人集中修复B05并同时修正C01，覆盖null/空token/其他非法终态及缓存结果不重复RPC、readonly authority默认UNKNOWN、首错sticky和原返回门；保留已证B01–B04、A01/A02及严格依赖边界。完整重新冻结后再交tester，不逐项打断coder，不自动下一批/M0。

实际Android FD/fsync/codec/muxer、隔离媒体格式/内容/timeline、真实宿主业务COMMIT/发布全部NOT_RUN。历史有限真机PASS、C13 FAIL、P0/J11危险链、UNKNOWN、FFmpeg/release/model/media等未结项保留原裁定；本报告仅裁定本候选的有限离线范围。
