# INPUT_SINK04_FIX 整包独立离线复审报告 V1.0

2026-10-21；tester；候选 `D1-20261021-INPUT-SINK04`。

**整包结论：FAIL。原 B05/P2、C01/P3 的指定修复有限离线通过，另发现 B06/P2：迟到 READY 响应可与已确认 ABORTED 同时成为成功事实；B07/P2：原 READY 响应仍未完成时，收尾抛出未映射的内部异常。** 新问题在准确冻结源码编译和实际生产JAR优先加载两路径均独立复现。请集中修复、完整重冻后交测，不以88/33矩阵或入口执行成功替代整包裁定。

依据 [正式测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_INPUT_SINK04_FIX_TESTER_REQUIREMENTS_V1.0.md)，完整阅读DELIVERY、RETURN_BOUNDARIES、INDEPENDENT_CHECK_PLAN。本轮只用已有JDK外置离线测试，SDK/ADB/5037/设备/占用/旧handle查询、Gradle/Android构建和共享缓存写入全部0。D1 `NOT_PASSED`、M0 `NOT_STARTED`，不自动下一批。

## 1. 身份与历史保全

| 对象 | 独立核验 |
|---|---|
| 主报告 | `0d062ee1ebf693b92a4206a5412a18aef491016e6f1cce820a91417f28c77e55` |
| Seal | `7a71b68959de3480a8f3d3a1d326fe6994cc843377398845f033956ba1e21650`；705条逐项字节/hash一致 |
| ZIP | 704个唯一条目与seal一致；`8fe78bf542f1bbb2671aa35778fc555157c1c7a8e733bf70512a0660f142c231` |
| 生产JAR | 88,583B；`f241f2f256f261f696f1713b164d17f6ffe68a692e2cf3702acf9eb881ce2e95` |
| APK | 6,305,359B；`24c6fdbed294771268a103200b19e5a3a8a099002d16dc392fe8d86f8c2d305b` |
| 最终输入 | 1,037条源/固定依赖输入一致 |
| 旧冻结 | RENDER01 477、RENDER02 404、capture818、INPUT_SINK01 334、INPUT_SINK02 316、INPUT_SINK03 629，共2,978项及六个原seal保持 |

独立审证见 [frozen-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/frozen-audit.json)。旧114/207/258份tester证据和旧报告保持；旧整包FAIL、历史N2、P0/UNKNOWN及有限PASS均不改写。

## 2. 原 B05、C01 指定修复裁定

**B05：PASS_LIMITED_OFFLINE_FOR_ORIGINAL_FINDING。** tester自写原QUERY null、空READY token、错类型三个输入。原ABORT实际已令宿主ABORTED，但QUERY坏响应本身不证明该副作用；三个输入都稳定登记 `OUTPUT_INVALID_HOST_RESULT`，不产生NPE、不把空token标READY。默认readonly authority UNKNOWN时，owner持续保管、ABORT/QUERY均1次、无新RPC补绿；仅开启宿主该原任务已保留的真实ABORTED记录后才收敛，首错不清。

另独立抽查WRITE返回Long、FLUSH返回String、validator错task、READY空白token、COMMIT返回String。类型/字段错误稳定消费，泛型桥不再把错误结果留在pending。WRITE原宿主实际发4B，SDK ACK下界0/callerPos0/UNKNOWN4，不按坏ACK退款或猜实际0B。坏READY ACK不等于宿主没有READY：该独立宿主实际已READY，随后准确原QUERY可证明相同有效token并正常收尾，协议首错保持。坏COMMIT ACK不等于没有发布：默认业务UNKNOWN持有，准确相同原task/token的原事实确认实际COMMITTED后才收尾，COMMIT只进入1次，不伪造回滚。

上述八项在源码/交付JAR双路径实际运行，见 [IndependentHostResults.java](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/IndependentHostResults.java)、[生产日志](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/host-samples-production.stdout)。这关闭原B05的指定输入，不覆盖新增迟到READY跨终态顺序。

**C01：PASS。** 实际直接执行文档的冻结 `review_all.py --output`，使用tester自己的新目录 [independent-001](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/independent-001)，没有复用coder-frozen-entry-001，也没有复制/修改工具绕过。工具先核seal，真实调用同一local_check入口，源码编译/20组及后续源码/JAR两路径全套均成功；完整42条原进程回执在 [summary.json](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/independent-001/summary.json)。

对review_all和local_check分别实际执行七种错误目标：旧03根、候选内部、伪前缀、越界、相对路径、根目录本身、已有independent-001。均拒绝，未创建新目标；复用目录在mkdir前拒绝，不启动编译。两工具相同规则有意重叠，不当14个不同产品场景。见 [independent-output-gates.json](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/independent-output-gates.json)。

## 3. 新 B06 / P2：迟到READY响应绕过已确认ABORTED的不可逆门

位置：[TemporaryOutput.java:129](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/src/com/videokit/d1input/TemporaryOutput.java:129)。query/readonly authority已使用validTerminal检查READY与ABORTED互斥；READY原stage的完成回调只检查类型、token形状及既有token绑定，没有检查此前已经确认的ABORTED。随后直接设置ready=true并清terminalProtocolUnknown。

独立场景明确区分原方法/物理任务与原响应ACK：原markReady方法已返回其同一个待完成响应stage，宿主没有仍运行的原工作任务，SDK仍保留该原响应；方法调用返回不被当作ACK。随后：

1. markReady等待80ms后返回OUTPUT_READY_UNKNOWN。原宿主此次没有实际READY，原响应仍未完成。
2. 原ABORT及原QUERY各1次，真实宿主和准确QUERY均确认ABORTED，SDK已有abortedAck=true、readyAck=false。
3. 向**同一原READY响应stage**注入一个形状合法、但与已确认终态相矛盾的迟到token。此为坏响应负向测试，没有在宿主造第二个READY副作用或修改SDK状态。
4. SDK实际将readyPhase置ACKED、readyAck=true，保留abortedAck=true，同时terminalProtocolUnknown=false；finishOriginalCallbacks可ownerReturned=true。真实宿主仍ABORTED。

原始观察：`actualHost=ABORTED READY_RPC=1 ABORT_RPC=1 QUERY_RPC=1 readyAck=true abortedAck=true ownerReturned=true`。firstFailure仍为最早OUTPUT_READY_UNKNOWN；缺陷不是要求覆盖该首错，而是迟到坏响应被当成第二个成功终态，未走现有不可逆校验/协议未知路径。

预期：所有终态来源，包括迟到READY原ACK，都遵守同一状态转换门。拒绝与ABORTED冲突的READY、保留原确认终态和首错，按现有原authority/未决规则处理，不凭坏响应清UNKNOWN或重RPC。准确原业务事实和实际原任务归还仍须分别满足。无需增加新协议字段、nonce或额外资源框架。

证据：[最终源码复现](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/late-ready-contradictory_aborted-source-1.stdout)、[生产JAR复现](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/late-ready-contradictory_aborted-production.stdout)。这不声称宿主实际READY/COMMIT，更不证明设备发生发布；仅证明SDK接受了矛盾原响应并报告双终态。

## 4. 新 B07 / P2：原READY响应仍在途时，完整收尾抛原始内部异常

位置：[TemporaryOutput.java:180](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/src/com/videokit/d1input/TemporaryOutput.java:180)、[TemporaryOutput.java:183](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/src/com/videokit/d1input/TemporaryOutput.java:183)，及原SinkCoordinator.awaitOriginalCallbacks的outstanding检查。

另一个独立场景使用**完全正常且一致的宿主终态**，不依赖B06坏响应：原markReady实际已令宿主READY，但原ACK交付仍在保留的stage中；原宿主方法/物理工作已返，不等于响应ACK已到。markReady timeout后，原ABORT正确不能推翻READY，原QUERY准确确认 `READY/controlled_ready_token`。此时原READY stage仍未完成，keeper应继续保管。

调用finishOriginalCallbacks，实际直接抛 `IllegalStateException: ORIGINAL_SINK_CALLBACK_PENDING`，不是本API惯用的稳定OUTPUT_ORIGINAL_PENDING IOException。SDK状态甚至显示pending=false，但原coordinator仍有未完成原响应。joinCoordinatorOriginals先关闭/join executor，再因outstanding非零抛内部异常；TemporaryOutput只处理InterruptedException，没有将这种尚未就绪状态作为正常的归还门。

原错误并未提前释放owner，正确保留原响应是可取的；问题是合法未完成状态泄露成未检查内部异常，调用方不能按既定稳定IO/pending路径收尾。之后仅完成同一原READY stage、token与QUERY一致，再次finish可正确归还，READY/ABORT/QUERY各1次，无重发。这证明缺陷独立于矛盾/非法值注入。

修复要求：完整归还前同时检查原结果仍在途的状态和原coordinator callback资格；未就绪时保留同原对象、稳定返回pending，不能盲取消、伪造原返回、退款或另发RPC。原ACK最终完成后仍须实际join原线程，不能只用outstanding==0作正向归还证明；也不应把正常未完成当作不可恢复内部错误。

证据：[最终源码正常响应顺序](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/late-ready-normal_query_ready-source-1.stdout)、[生产JAR正常响应顺序](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE/late-ready-normal_query_ready-production.stdout)。B06场景在ABORTED收尾时也触发同一内部异常，故两项修复应集中处理但分别验证。

## 5. 完整回归与十九项矩阵

按真实文档入口在tester独立目录执行：原20组、17尾段、tester23安全回归、九阶段63异常、输入5项、本批88返回值及33状态/授权、原QUERY两项安全回归、authority3及私有cause取消6，两路径全部通过。完整阅读关键断言和不适用项；这些有重叠，不相加冒称不同独立场景。绿色运行结果不能覆盖tester新发现的跨来源/迟到响应顺序。

原B01–B04指定修复、A01/A02及严格依赖边界保持：未准入不消费一次进入标记，原尾返后flush1close1；同原validator/commit/query任务尾段未返不放行；原readback registry/worker/close阶段保管；最早失败/timeout sticky；partial与即时/晚取消UNKNOWN一次登记，caller与private block不混同。readonly authority默认UNKNOWN不触发新RPC/释放；相同原task/token准确事实与物理返回分别接纳。没有新增或假装已验证Status/CommitOutcome中不存在的返回身份字段。

| 清单 | 本候选独立裁定 |
|---|---|
| I01 | PASS_LIMITED：真实DataSpec/TransferListener、3+3+1短读、准确range/offset、重复open/close |
| I02 | PASS_LIMITED：未知长度-1，3+2后EOF |
| I03 | PASS_LIMITED：3GiB+7逻辑offset、≤64KiB读块，无巨大文件 |
| I04 | PASS_LIMITED：long溢出先拒绝，caller不改/host不调用 |
| I05 | PASS_LIMITED：非法read count拒绝；另有WRITE/QUERY错类型独立检查 |
| I06 | PASS_LIMITED：输入及输出私有message/cause稳定脱敏 |
| I07 | PASS_LIMITED：同DataSource读重入拒绝 |
| I08 | PASS_LIMITED：cancel/迟到private block、caller不覆盖、原read/close返回 |
| I09 | PASS_LIMITED：双consumer首关闭不足释放，原任务/registry/线程返回 |
| I10/A01 | PASS_LIMITED：共享源峰值1/queue0、global2、跨factory同provider拒绝 |
| I11 | PASS_LIMITED：旧epoch原归还后新range、offset7数据准确 |
| I12 | PASS_LIMITED：原FAILED close显式原API恢复，无PENDING/UNKNOWN盲重试 |
| S01/A02 | PASS_LIMITED：physical10/ACK3/caller3；坏WRITE可actual4/ACK0/UNKNOWN4，不重发/回退/退款 |
| S02 | PASS_LIMITED：16MiB候选资格，超限前无新host write |
| S03 | PARTIAL_FAIL_B07：原flush/close错误、B01/B03/B04及尾段通过；原READY响应仍在途的完整收尾异常失败 |
| S04 | PASS_LIMITED：真实生成4B文件写/force/close/reopen、摘要/receipt拒绝、原读回registry返回 |
| S05 | NOT_RUN_PLATFORM：真实Android FD/fsync/codec/muxer/容器故障未执行 |
| S06 | PARTIAL_FAIL_B06_B07：正常READY/COMMIT、原B02/ACK业务事实分层通过；迟到READY不可逆及在途收尾失败 |
| F01 | PASS_LIMITED：真实Media3接口、依赖/产物及正确复核工具路径通过 |

seed539365408；最大测试块65,537B，实际新落盘文件4B，SHA256 `e6e8cb429864b8e8d7fe95e53360dbd00756316813fb1e4a03a778d4632dbde6`。16MiB预算用复用64KiB块计数，大offset由受控provider提供；未读取真实媒体/旧输出。JVM平台端口、受控validator/authority及COMMIT不代替真实FD、隔离容器或业务发布。

## 6. 依赖、产物和原构建

15runtime坐标、两锁、verification XML、实际deps均与INPUT_SINK03逐字节一致，无新版本/pin/下载。独立核本次最终build-main-001的819事件内296实际消费验证ID、artifact/坐标、原pin与缓存字节，121binary/35module/140POM，175份metadata副本一致；strict verification、verify-metadata=true、LockMode.STRICT保持。原receipt exit0、BUILD SUCCESSFUL，tester没有重复Gradle/Android构建。

APK二进制manifest独立解析为com.videokit.d1input/versionCode4/min31/target36，无权限、四类组件/native .so；DEX4,394类，JAR53项。真实适配存在，检查helper/JVM URI/errno替身排除。独立已有JDK+固定官方apksig库验证v2与单证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，未调用SDK工具。生产JAR优先的最终场景保存实际ORIGIN与完整classpath，未被源码类遮住。

产品差异集中TemporaryOutput/Failures/候选SinkCoordinator；HostOutput/AndroidGrantedStream、输入/bridge/registry/成熟muxer不变。原三依赖来源/Apache有限离线准入保持，不扩大为release、真实平台或宿主内部账本证明。token仍为既定不透明String，未发明密码学格式、过期/编码或任意新阈值；现有字段不能证明同一物理FD、真实授权持久化或随机输出最终期望摘要。

## 7. 测试过程、清理与集中返修

文档整套入口直接跑通，新额外测试只写tester目录。独立双路径原响应由同一个保留的future完成，没有替换stage、反射改SDK状态或额外RPC。原宿主调用/实际工作任务已经返回时，原ACK仍可能在途；本轮专门覆盖该事实与“ACK早到、原线程仍活”的既有测试相反的顺序。

补B07正常场景的初版tester检查误以为abort必定同步进入完整收尾，断言失败；其清理还错误提供了不同的READY token，引入额外protocol unknown，原失败stderr/exit1保留。修正检查为显式调用finishOriginalCallbacks，并在清理完成同一个正确token后，最终源码/生产JAR均复现B07且正常归还。该初版失败JVM中残留的是被测内存keeper，实际宿主工作/源资源已返回；不把其进程退出算归还证明，不将tester清理错误列为产品新缺陷。最终有效检查全部同原callback/线程实际join、source/output keeper0。

完整证据：[D1_INPUT_SINK04_REVIEW_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE)。准确argv、退出/时间、source pins、ORIGIN、原stage/终态观察、正反工具路径、产物审证及最终证据manifest均保留；原失败日志不覆盖。所有实际JDK进程/管道已返回，没有在途设备或工具资源。

请负责人集中派发B06/B07，补全原响应在途与物理已返、已确认终态与迟到响应交叉顺序；所有终态来源使用统一不可逆门，完成归还保持稳定pending且不重RPC/伪取消。保留本批已通过的B05/C01、B01–B04、A01/A02和严格依赖，完整重冻再交tester。此次报告后不自动下一批/M0。

真实Android FD/fsync/codec/muxer、隔离媒体格式/内容/timeline、宿主真实COMMIT/发布全部NOT_RUN。历史有限真机PASS、C13 FAIL、P0/J11危险链、UNKNOWN、FFmpeg/release/model/media等未结项维持原裁定，不因本候选正常分支通过而清账。
