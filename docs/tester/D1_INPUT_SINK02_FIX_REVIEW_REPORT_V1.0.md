# INPUT_SINK02_FIX 整包独立离线复审报告 V1.0

2026-10-21；tester；候选 `D1-20261021-INPUT-SINK02`。

**整包结论：FAIL。原 B01/P2、B02/P1 的指定修复及正常/超时尾段回归通过，另发现两项 P2 缺陷：B03 取消异常原 ACK 未消费且泄露宿主私有错误；B04 ABORT/QUERY 超时或原 ABORT 失败历史未保留。** 两项新问题均在准确冻结源码编译类、交付生产 JAR 优先加载两条路径独立复现。请一次性集中修复后重新冻结整包交测，不能只依据原20组、17场景通过裁定本包通过。

本轮按 [正式测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_INPUT_SINK02_FIX_TESTER_REQUIREMENTS_V1.0.md)，完整阅读交付、状态模型和独立入口，复用原十九项矩阵并独立补原任务返回/错误处理。无设备、SDK、ADB、5037、占用、旧 handle 查询；没有 Gradle/Android 构建或共享缓存改写。仅使用已有 JDK，在 tester 新目录编译、运行和验签。D1 `NOT_PASSED`、M0 `NOT_STARTED`，本轮结束后不自动下一批。

## 1. 准确候选与历史保全

| 对象 | 独立身份核验 |
|---|---|
| Delivery | `93a9b8bf2f5970196fb45dbe784dacabc6d4a8cae76bad31a51872c4e6b87bb9` |
| Seal | `48458aaf9903ab799a3c497313ff333bf102a2aee1429a6c24be4b18f283a161`；316条文件逐项字节/hash一致 |
| ZIP | 315个唯一条目与seal对应；`d87593c4f3582e0daf25a0bf38faee8d1a212b2cc40946bf156625855bafe98c` |
| 生产 JAR | 84,773B；`a98ec7f34139dcd08db611280256774af4a4897f20f8c3d2fa39beae87248bc0` |
| APK | 6,300,791B；`25898fe613f845a1ba7dbbd5f5e4d85a7b0875b473099c06ba587eff6df3e08e` |
| 最终输入 | 1,037条源/依赖输入逐项匹配，缓存仅按冻结pin读取 |
| 旧候选 | RENDER01 477、RENDER02 404、capture818、INPUT_SINK01 334，共2,033项原hash及四个原seal保持 |

独立 [frozen-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE/frozen-audit.json) 保存完整结果。旧 INPUT_SINK01 FAIL、114份 tester 证据、五个原场景及报告保留；原 N2 批次、历史 scope账本/UNKNOWN/P0及失败不改写。旧任务停止要求没有扩大套用到本新候选。

## 2. 原 B01/B02 修复裁定

**B01：PASS_LIMITED_OFFLINE。** 未准入时不消费 flush/close 一次进入标记。tester 将真正执行宿主 write、flush、close 的原线程在 ACK 后留在尾段：前序原任务未返，重复 finishWriter 只拒绝，未准入阶段保持 NOT_ADMITTED；join 同一原线程后，flush恰好1次、close恰好1次，首错为空。对已经进入的 timeout/UNKNOWN 没有盲重试。原 B01 的 `flush0/close1/永久pending` 不再复现。

**B02：PASS_LIMITED_OFFLINE_FOR_ORIGINAL_FINDING。** validator 和 COMMIT 显式保留同原 authority。writer与host均已返、独立validator原任务仍活时，READY=0、ownerReturned=false、retained=1；原证明抛错时仍保留资格。join同原validator线程后仅调用一次 READY。显式 COMMIT 原 ACK 已到时 committed=true，但同原 COMMIT 尾段仍活，owner仍未返；join后才能释放，ACK没有抹掉。

同类 REOPEN/READY/ABORT/QUERY 的早ACK与原尾段、原结果缓存及RPC单次进入检查通过；REOPEN不提前读回/验证，READY不提前准入COMMIT，ABORT尾段未返不发QUERY，QUERY早ACK不提前返owner。缓存view并未成为归还证明。原 coordinator callback/executor/thread join仍参与释放。独立补测 reopen读回的close原stage持续未返，5秒等待失败时原registry及source/output keeper均保留；同原close任务完成并join、原bridge/registry/runtime归还后，才允许abort清理，保留 OUTPUT_REOPEN_FAILED，不补 READY。

证据：[tester独立12场景源码路径](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE/tester-independent-source.stdout)、[交付JAR路径](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE/tester-independent-production.stdout)、[原读回registry归还](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE/readbackreturncheck-production.stdout)。这些有限通过不覆盖下述新失败分支。

## 3. 新缺陷 B03 / P2：已取消的原 future 未作为终局失败消费，未经脱敏异常反复外泄

位置：[TemporaryOutput.java:44](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/src/com/videokit/d1input/TemporaryOutput.java:44)、[TemporaryOutput.java:53](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/src/com/videokit/d1input/TemporaryOutput.java:53)。原 future 的 `get()` 可能直接抛 `CancellationException`，但首次等待及 observeNow 只处理 ExecutionException、超时、线程中断；因而没有走原结果消费/Failures映射/首错或UNKNOWN登记。abort也在observeNow处再次抛同一未消费异常。

独立受控宿主已真正进入原方法，并返回以 `CancellationException("private-host-cancellation-detail")` 完成的原stage。没有由SDK或tester调用cancel去取消被测原stage。WRITE/FLUSH/CLOSE/REOPEN/VALIDATE/COMMIT六个阶段分别在隔离JVM核验，均得到：首次调用、observeOriginal、abort三次直接抛带原私有信息的CancellationException，pending一直true，keeper=1，即使同原authority已报告任务实际返回。

WRITE准确输出：`callerPos=0 actualWriteCalls=1 writeAttemptedOrReserved=4 writeAmountUnknown=false unknownWriteReservation=0 pending=true error=null`。原调用已经进入而没有有效字节ACK，SDK却既未登记首错，也没有保留写量UNKNOWN。测试宿主实际字节事实与SDK已确认下界仍须分开，不能从失败ACK推导实际0B。

另补同原晚取消场景：write原线程实际发出4B后取消ACK；先前SDK已超时并保留4B reservation，修改caller字节不会改原private block。完成同一原线程并join后，observe/abort仍反复抛私有CancellationException，pending=true、keeper=1。原timeout/UNKNOWN没有被清零，但同一终局原结果始终无法结算。

影响：宿主合法的原stage取消失败既能越过稳定脱敏错误接口，也使原结果永久挂在ACK_PENDING，阻塞后续正确清理和容量。COMMIT未收到业务ACK时仍可能必须保持业务UNKNOWN/owner，不能因此强行释放；此缺陷不是要求把取消当作已提交或安全回滚，而是要求准确消费原终局失败、保存ACK未知与原任务归还的独立事实。

修复要求：覆盖首次等待和晚结果观察的CancellationException，映射稳定无私有cause/message的code，一次性登记原失败；WRITE补正确UNKNOWN且不重复加账。其余阶段按准确失败/调用UNKNOWN语义保留，不伪造成功ACK、不重发COMMIT或已执行flush/close；在允许清理的分支同原资源真实归还后正常结算。增加六阶段及timeout后同原晚取消回归。

证据：[WRITE生产JAR复现](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE/cancelled-write-production.stdout)、[COMMIT生产JAR复现](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE/cancelled-commit-production.stdout)、[同原晚取消](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE/latecancelledackcheck-production.stdout)。其余五阶段、源码双路径及完整argv/退出回执同目录保留。

## 4. 新缺陷 B04 / P2：ABORT/QUERY超时或原ABORT失败，经终态确认后首错仍为空

位置：[TemporaryOutput.java:125](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/src/com/videokit/d1input/TemporaryOutput.java:125)。abortBeforeReady抛IOException后，前序原任务未返就直接return false；若随后reconcile成功则直接继续终态处理。只有reconcile本身再失败才调用fail。原 ABORT/QUERY 已经发生的失败或timeout没有保留到firstFailure。

根据本候选 [状态模型](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK02_STATE_MODEL_V1.0.md)，首次业务失败/超时须保留，晚ACK与资源归还不抹掉历史。独立在两条加载路径执行三种情形：

| 注入 | 实际观察 |
|---|---|
| ABORT已进入，同原stage超出80ms等待；后同原晚ACK、尾段退出 | 初次abort=false/error=null；最终ownerReturned=true/error=null |
| QUERY已进入，同原stage超出80ms等待；后同原晚ACK、尾段退出 | 初次abort=false/error=null；最终ownerReturned=true/error=null |
| 原ABORT先完成实际状态变更为ABORTED，再返回失败IOException；QUERY准确确认ABORTED | abort可直接返回true，ownerReturned=true，但error=null |

三种情形均只执行一次原ABORT和一次原QUERY，业务ABORTED及原任务归还的事实正确；缺陷是已发生的错误被成功reconcile/晚返回路径吞掉，后续报告看不出原RPC失败或超时，违背同批首错sticky模型。第三项不应因为RPC失败就抹掉QUERY确认的ABORTED，也不应据此重复RPC；需同时保留失败历史与真实终态。

修复要求：区分“原RPC根本未准入的瞬时pending”和“原RPC已实际进入后的超时/失败”。仅后者准确登记首次稳定错误，再按同原stage缓存、原authority及coordinator归还完成收尾。首错不能因reconcile成功而为空，也不能以补错误为由推翻已证终态或退款UNKNOWN。

证据：[ABORT超时](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE/history-abort-production.stdout)、[QUERY超时](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE/history-query-production.stdout)、[ABORT原失败后确认终态](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE/history-abort_error-production.stdout)。源码编译路径的同名日志完整保留。

## 5. 测试执行与十九项矩阵

冻结入口在tester新目录实际编译并跑原20语义组；另以交付生产JAR置于classpath首位再跑20组。两次均通过。冻结 ReturnBoundaryCheck 的17场景也在源码/交付JAR双路径实际运行并通过，作为补充回归，不代替tester独立断言。

tester新增23个不同场景在两条路径执行：原五场景的安全断言，加7个阶段/错误/私有块场景，共12项；读回原registry/close返回1项；取消ACK六阶段和晚取消共7项；ABORT/QUERY失败历史3项。前13项通过，后10项分别复现B03/B04。两路径合计46次场景执行，重复加载路径不冒充新增场景。复现程序exit0表示成功捕获预期缺陷，不代表产品该场景通过。

| 清单 | 新候选独立裁定 |
|---|---|
| I01 | PASS_LIMITED：真实DataSpec/TransferListener、3+3+1短读、准确offset/range、EOF及重复open/close |
| I02 | PASS_LIMITED：未知长度-1，3+2后EOF |
| I03 | PASS_LIMITED：3GiB+7逻辑偏移、≤64KiB读块，无巨大文件 |
| I04 | PASS_LIMITED：long溢出先拒绝，caller不改、host未调用 |
| I05 | PASS_LIMITED：0/-2/超过count非法结果拒绝 |
| I06 | PASS_LIMITED_INPUT：输入权限/私有错误脱敏保持；输出取消异常的独立脱敏失败另列B03 |
| I07 | PASS_LIMITED：同DataSource读重入拒绝 |
| I08 | PASS_LIMITED：cancel/迟到private buffer，caller目标不覆盖，原read/close等待 |
| I09 | PASS_LIMITED：双consumer首关闭不足以释放，原线程/registry返回后归还 |
| I10/A01 | PASS_LIMITED：单provider峰值1、queue0≤4、global2；跨factory同provider拒绝 |
| I11 | PASS_LIMITED：旧epoch原归还后新range，独立offset7数据准确 |
| I12 | PASS_LIMITED：观察到原FAILED close后显式原API恢复，未盲重试PENDING/UNKNOWN |
| S01/A02 | PARTIAL_FAIL_B03：physical10/ACK3/callerPos3、private block、首错与UNKNOWN不重复计账通过；即时取消WRITE漏UNKNOWN/首错失败 |
| S02 | PASS_LIMITED：16MiB资格边界，超限前无新host write，复用64KiB块计数 |
| S03 | PARTIAL_FAIL_B03_B04：B01修复、普通close失败/lateACK/原尾段通过；取消ACK未消费、cleanup首错遗漏失败 |
| S04 | PARTIAL_FAIL_B03：真实生成4B写/force/close/reopen和验证拒绝、原读回registry待归还通过；REOPEN/VALIDATE取消ACK失败 |
| S05 | NOT_RUN_PLATFORM：实际Android FD/fsync、muxer/容器重开故障未执行；能力与受控随机offset接线仅有限通过 |
| S06 | PARTIAL_FAIL_B03_B04：B02修复及正常READY/显式COMMIT分层、ACK保留与原返回通过；COMMIT取消ACK/cleanup失败历史仍失败 |
| F01 | PASS_LIMITED：实际Media3接口、固定依赖及产物身份通过；Android平台运行/真实业务仍未测 |

生成seed539365408，最大测试块65,537B；实际新落盘输出每份4B，SHA256 `e6e8cb429864b8e8d7fe95e53360dbd00756316813fb1e4a03a778d4632dbde6`。新增故障字节块≤32B，不读取真实媒体/旧宿主输出。UI/errno为明确JVM平台端口；Android真实Looper、授予流/原E4Owned、FD fsync和成熟Media3/E6 muxer仅静态/真实ABI构建证据，不冒充平台故障或容器效果已测。

## 6. 依赖、编译和产物核验

新包与INPUT_SINK01的真实deps JAR逐字节一致；15runtime坐标、两份锁和verification XML逐字节一致，新增坐标/版本/pin为0。datasource/database/exif的原有限离线身份/Apache许可准入保持，不扩展为release或其他发行放行。

独立核005旧包与本次001构建材料分列：本次实际819行事件内的296条验证ID、artifact/坐标与清单一致，121binary/35module/140POM全部匹配原pin及当前固定缓存字节，175份metadata副本匹配。verify-metadata=true、verification strict、LockMode.STRICT保持；本轮未运行Gradle。原build-main-001 exit0/BUILD SUCCESSFUL作为开发构建原始证据保留，tester不重复构建求绿。

APK二进制manifest独立解析：com.videokit.d1input/versionCode2/min31/target36，无权限、四类组件或native库。DEX4,393类包含真实适配，未包含InputSinkCheck/ReturnBoundaryCheck及准确JVM URI/errno替身；生产JAR52项，不含检查helper或Android平台替身。独立JDK+已固定官方apksig库验v2及证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，没有调用SDK工具。正常回归、两个新缺陷和读回归还检查的production回执均记录JAR优先classpath与实际ORIGIN，避免源码类遮住交付产物。

HostInputFactory/HostDataSource、原桥/registry、成熟muxer绑定与原源版本不变；产品修复集中TemporaryOutput/HostOutput、AndroidGrantedStream、SinkCoordinator副本。Validator/Commit及Android authority的原证明接口变化明确，仍是候选契约，不是M0最终API。原五场景逻辑独立迁移到新端口，未修改旧tester源或旧复现断言。

## 7. 清理、保留边界与集中返修

正常/尾段/读回测试均join同一实际执行宿主动作的原线程，source/output keeper归零。B03故障场景在独立JVM保留了被测逻辑keeper=1的真实失败现场，没有反射修改产品状态或删除keeper来伪造归还；全部实际宿主原线程已经退出，随后测试JVM实际exit返回，其余仅该隔离进程内内存回收。COMMIT失败UNKNOWN不被改成已成功/已回滚。所有JDK子进程与输出管道已返回，无在途工具或设备资源。

完整证据目录：[D1_INPUT_SINK02_REVIEW_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE)。主要语义检查保存准确argv、exit、时间、生产JAR SHA，验签另存argv/退出回执；源码pins、双路径原日志、case矩阵、身份审证及最终证据manifest独立保存。没有新建执行许可、自动观察设备或启动下一批。

请负责人集中派发B03/B04一次修复，保留本批已证B01/B02原归还门、A01/A02正常分支及严格依赖，补完整终局失败/取消/cleanup首错矩阵；重新冻结源码、产物及整包证据后交独立复审。原INPUT_SINK01历史FAIL保留，本候选有限通过项不覆盖新失败。

实际Android FD/fsync/codec/muxer、隔离格式/内容/timeline验证、真实宿主业务COMMIT/发布全部NOT_RUN。历史有限真机PASS不清空，原C13 FAIL、P0/J11危险链、UNKNOWN、FFmpeg/release/model/media等未结项保持原裁定。本报告不自动M0，不因历史N2停止要求搁置本新离线批。
