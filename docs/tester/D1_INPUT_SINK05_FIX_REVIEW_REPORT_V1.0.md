# INPUT_SINK05_FIX 整包独立离线复审报告 V1.0

2026-10-21；tester；候选 `D1-20261021-INPUT-SINK05`。

**结论：PASS_LIMITED_OFFLINE。原 B06/P2、B07/P2 的指定修复及本批有限关键顺序通过；未发现新的离线阻断缺陷。** 结论来自准确冻结包源码/生产JAR双路径、tester自写八项顺序注入及实际文档入口执行，不仅依据coder的30/7项计数。原B01–B05、C01、A01/A02有限通过保持。

本裁定只覆盖本候选已有端口契约下的有限离线范围。**D1仍NOT_PASSED，M0仍NOT_STARTED；实际Android FD/fsync/codec/muxer、隔离媒体容器及真实宿主COMMIT/发布仍NOT_RUN。** 不自动进入新批次、设备测试或M0。

按 [正式测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_INPUT_SINK05_FIX_TESTER_REQUIREMENTS_V1.0.md)，完整阅读DELIVERY、RESPONSE_ORDER_MODEL和INDEPENDENT_CHECK_PLAN。全程只用已有JDK外置执行；设备/SDK/ADB/5037/占用/旧handle查询、Gradle/Android构建和共享缓存写入均0。

## 1. 准确身份与保全

| 对象 | 独立核验结果 |
|---|---|
| 主报告 | `25503fe0f72310db4b22eeb23875fbdc17f782092ebd4e0bf132baf2fb3f82a7` |
| Seal | `ec7e5e9a8f38d2d1fe531592117f5db0a6d3481cd3ff89536d985f9dae173d96`；828条文件字节/hash逐项一致 |
| ZIP | 827个唯一条目与seal一致；`b387471995c555628baee54e0f56a3affd1782b36da2f6de1fd3425aa08fa5ab` |
| 生产JAR | 91,676B；`6fbf307a4f0a06f45606ad9a162fcad95330924c2f220b5f68cec1e851916b0b` |
| APK | 6,310,283B；`0b5fc8d530c8159c9283d670472255b883d97ad3885e2bae8fd427d25c1148b7` |
| 最终输入 | 1,037条准确源/固定依赖输入一致 |
| 旧候选 | RENDER01 477、RENDER02 404、capture818、INPUT_SINK01 334、02 316、03 629、04 705，共3,683项及七个原seal保持 |

详见 [frozen-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE/frozen-audit.json)。旧tester114/207/258/993份证据、对应原报告与历史FAIL均保留，不因新候选通过回填。历史N2及原scope账本/UNKNOWN/P0未改写。

## 2. B06/P2：迟到READY不可逆采纳通过

tester保留原输入：宿主原markReady方法/实际工作已返，但**同一原响应stage仍pending**。markReady先timeout，再由原ABORT和准确原QUERY确认ABORTED。之后向同一原READY stage交付形状合法却与该终态冲突的迟到token。

实际结果：`readyResponseReceived=true`、`readyResponseSucceeded=true`，但 `readyResponseAccepted=false`、`readyResponseRejection=CONFLICT_WITH_ABORTED`、readyPhase=ACK_REJECTED；readyAck=false、abortedAck=true，不再双成功。原响应传输事实没有被删除，最早OUTPUT_READY_UNKNOWN保持。

默认authority UNKNOWN时owner持续保管、finish稳定OUTPUT_ORIGINAL_PENDING；只有准确兼容、同原任务的实际ABORTED证明开放后才收敛。READY/ABORT/QUERY各1次，不发新RPC“纠正”，不补假ACK、不退款UNKNOWN。终态采纳函数对原READY首次/迟到ACK、等待结果、QUERY、readonly和派生coordinator来源统一生效。

独立证据：[最终源码八项日志](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE/independent-orders-source-1.stdout)、[生产JAR八项日志](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE/independent-orders-production-1.stdout)。旧INPUT_SINK04中B06的真实失败不改写。

## 3. B07/P2：原响应在途与原回调物理返回分层通过

独立正常场景中宿主实际READY，原响应尚未完成；原ABORT正确不能推翻READY，原QUERY准确确认相同token。observeOriginal此时不冒称原响应全部回答；finish稳定OUTPUT_ORIGINAL_PENDING，owner仍持有，state pending=true，不再抛原始IllegalStateException。

完成同一个原READY响应、相同token后，原响应可采纳；还须原observer返回、原executor终止与同一SDK worker实际join，才归还owner。原最早timeout保留，RPC均单次，没有取消原future或换任务求绿。

独立额外物理门测试分别证明：

- 真实whenComplete已经执行SDK动作、response和代理view已done，但**同一个observer函数仍在实际尾段**，其真实返回stage未完成。finish稳定pending、keeper1，不能用业务ACK或host工作已返替代observer返回。
- 放开同一observer尾段后，外部交付客户端线程仍在测试事件循环中活着，SDK可以正确归还；observer已返不要求无关的长寿命客户端线程退出。最后另行停止并join该同一客户端，未遗留线程。
- standalone原coordinator的outstanding=0，但原whenComplete注册方法仍在**该SDK自己创建的同一worker**中留有实际尾段；originalResponsesCompleted=false、originalCallbacksReturned=false，有限await稳定pending。放gate后实际join该原worker，再检查资格才通过。

记录的原SDK worker名为videokit-d1-sink，日志保存实际thread ID、alive、pendingCount0和真实完成状态。未用新线程、新计数器或代理future冒充原线程归还证明。源码和生产JAR均通过，原B07仅限本批有限离线场景关闭。

## 4. tester自写八项关键顺序

源码：[IndependentResponseOrderCheck.java](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE/IndependentResponseOrderCheck.java)。测试端口使用标准CompletableFuture及真实whenComplete依赖stage；有限gate阻塞的是实际执行该动作/方法的原线程，不是SDK状态反射或伪造返回布尔值。

| 独立场景 | 实际检查与结果 |
|---|---|
| B06 QUERY先确认ABORTED，原READY ACK后到 | raw成功收到但拒绝采纳，保留ABORTED、首错、冲突UNKNOWN；准确原authority后才释放 |
| B07 QUERY先确认READY，同token原ACK后到 | response pending时稳定pending；同ACK、observer、原worker归还后收敛 |
| READY ACK先于原QUERY response | READY先采纳，后到矛盾ABORTED QUERY被拒，不覆盖READY；准确兼容原authority后收敛，无重RPC |
| 坏readonly先于同token晚ACK | 已知READY后，矛盾ABORTED authority产生冲突；匹配ACK可以被采纳但不能清该冲突；UNKNOWN不清账，准确原READY authority才清未决 |
| 实际SDK observer尾段 | response/业务ACK已完成但同observer返回stage未返，keeper保留；放gate后才可归还，外部长寿命客户端不被误作SDK-owned线程 |
| 零计数但原SDK worker尾段仍活 | outstanding0不证明返回；有限await pending，释放gate并join同worker后才通过 |
| ABORT ACK在途，原READY晚失败 | 原ABORT实际已发生但ACK仍pending时不发QUERY；失败响应如实收到/拒绝，不能推导回滚；原ABORT ACK后首次原QUERY准确确认ABORTED |
| ABORT ACK在途，原READY晚取消 | 同上，取消与实际副作用分开；准确终态后归还，最早首错、单次RPC保持 |

最终八项均源码/JAR双路径exit0，keeper最终归0。早期六项通过日志保留；补入两项失败/取消顺序后只重编译并重复自身有限检查，没有重跑Gradle或整个旧批次。不同加载路径、重复和套件重叠不冒作新增不同场景。

## 5. 实际文档入口与既有套件

直接执行冻结 `review_all.py --output` 到tester新 [independent-001](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE/independent-001)，未复用coder-frozen-entry-001，也未复制工具/改断言。入口先核完整seal，真实调用local_check外置编译及源码20组，再执行两路径套件，50条顶层原进程回执均exit0；编译/源码20组另有子回执。见 [summary.json](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE/independent-001/summary.json)。

实际两路径运行原20/17/23/63/5、本批返回值88/转换33、原QUERY2、authority3、私有cause取消6、独立host返回8，以及原响应2/owner顺序30/coordinator顺序7。检查了关键断言和原stage/observer/worker身份；这些是可复用回归，与tester自写八项分列，不仅引用coder的绿色计数。未声称数学全状态或穷尽所有调度。

C01输出门继续通过：review_all、local_check各实际拒绝旧04根、候选内、伪前缀、越界、相对路径、根本身和已有independent-001，新错误目标未创建。两个工具相同七类条件有重叠。见 [independent-output-gates.json](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE/independent-output-gates.json)。

所有production回执将准确交付JAR置于classpath首位，核实际ORIGIN，源码类未遮住产物。既有readback原registry、同close任务、validator/commit原authority与取消/晚返继续通过；原firstFailure/字节UNKNOWN不清，不因拒绝坏响应就认定host没副作用。

## 6. 十九项独立矩阵

| 清单 | 裁定及范围 |
|---|---|
| I01 | PASS_LIMITED：真实DataSpec/TransferListener、3+3+1短读、准确range/offset、重复open/close |
| I02 | PASS_LIMITED：未知长度-1，3+2后EOF |
| I03 | PASS_LIMITED：3GiB+7逻辑偏移、≤64KiB读块，无巨大文件 |
| I04 | PASS_LIMITED：long溢出先拒绝，caller不改/host不调用 |
| I05 | PASS_LIMITED：非法read count/host返回拒绝 |
| I06 | PASS_LIMITED：输入/输出私有message/cause稳定脱敏 |
| I07 | PASS_LIMITED：同DataSource读重入拒绝 |
| I08 | PASS_LIMITED：cancel/迟到private block、caller不覆盖、原read/close等待 |
| I09 | PASS_LIMITED：双consumer首关闭不足释放，原handle/stage/registry/线程返回 |
| I10/A01 | PASS_LIMITED：同provider峰值1/queue0、global2、跨factory同provider拒绝 |
| I11 | PASS_LIMITED：旧epoch原归还后新range，offset7内容正确 |
| I12 | PASS_LIMITED：原FAILED close显式原API恢复，不盲重试PENDING/UNKNOWN |
| S01/A02 | PASS_LIMITED：physical10/ACK3/caller3、late actual4/ACK0/UNKNOWN4、private block/首错/未知量一次登记，不重发回退退款 |
| S02 | PASS_LIMITED：16MiB候选资格，超限前无新host write |
| S03 | PASS_LIMITED：原flush/close错误、ACK/observer/线程分别归还；原B01/B03/B04/B07指定修复保持 |
| S04 | PASS_LIMITED：真实生成4B文件写/force/close/reopen、摘要/receipt拒绝、原读回registry返回 |
| S05 | NOT_RUN_PLATFORM：实际Android FD/fsync/codec/muxer/容器故障未执行 |
| S06 | PASS_LIMITED：READY/COMMIT/终态采纳、raw响应和真实归还分列；原B02/B05/B06/B07有限关闭 |
| F01 | PASS_LIMITED：真实Media3接口、固定依赖/产物及正确工具输出门 |

seed539365408；最大测试块65,537B，实际生成文件4B，SHA256 `e6e8cb429864b8e8d7fe95e53360dbd00756316813fb1e4a03a778d4632dbde6`。16MiB候选预算使用复用64KiB块计数，大offset由受控provider提供。未读取真实媒体/旧宿主输出；受控4B文件不是媒体容器。

## 7. 依赖、构建与二进制

15runtime坐标、两锁、verification XML、真实JVM deps与INPUT_SINK04逐字节一致。独立核1,037条最终源/依赖输入，以及当前build-main-001的819行事件中296项实际消费ID、artifact/坐标、原pin及缓存字节；121binary/35module/140POM、175份metadata副本准确一致。strict verification、verify-metadata=true、LockMode.STRICT保持，无新版本/pin/下载，原三依赖有限离线来源/Apache准入不扩大发行范围。

原最终构建receipt exit0、日志BUILD SUCCESSFUL；tester未重跑Android构建。生产差异仅TemporaryOutput与候选SinkCoordinator，原HostOutput/AndroidGrantedStream、Failures、输入适配/bridge/registry/muxer不变。原stage、observer和线程仍由原owner/registry/coordinator保管，没有新executor、资源ledger或宿主协议字段。

APK二进制manifest独立解析：com.videokit.d1input/versionCode5/min31/target36，无权限、四类组件或native .so；DEX4,396类、生产JAR54项。真实适配存在，检查helper及JVM URI/errno替身排除。独立已有JDK+固定官方apksig库验证v2与单证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，未调用SDK工具。Android实际Looper/FD绑定保留真实ABI证据，运行仍NOT_RUN。

## 8. 清理、未测边界与交付

最终独立检查及文档套件的有限gate全部释放，实际observer返回、准确原SDK worker退出/join，适用host/client原线程最终join；source/output keeper0，所有JDK子进程与输出管道已返回。本轮没有新失败检查需要靠JVM退出补逻辑归还，也没有反射删除keeper或制造authority结果求绿。coder早期prototype exit1及旧批tester失败仍按历史保留，不回填通过。

完整证据：[D1_INPUT_SINK05_REVIEW_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE)，包含原source pins、真实参数/退出时间回执、两路径完整日志、实际stage/observer/thread/RPC观察、输出门、身份/签名、十九项矩阵及最终证据manifest。报告hash冻结后一次性主动发送负责人，另存通知回执。

未证明的范围继续明确保留：全部可能并发调度、恶意/不合约CompletionStage、真实宿主原task/token权威内部账本及跨进程发布；Status/CommitOutcome/Provider缺少的返回身份/物理FD字段；token密码学/到期协议；随机输出最终期望摘要。未发明新字段或协议，也未将受控端口当真实业务证明。

实际Android FD/fsync/codec/muxer、隔离格式/内容/timeline和宿主真实COMMIT/发布均NOT_RUN。历史有限真机PASS、C13 FAIL、P0/J11危险链、UNKNOWN、FFmpeg/release/model/media许可等未结项保持原裁定。请负责人审核本有限离线通过结果后统一决定下一批，本轮不自动继续或启M0。
