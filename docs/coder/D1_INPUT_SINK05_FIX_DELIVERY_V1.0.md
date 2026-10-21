# INPUT_SINK05 迟到终态与原回调顺序集中修复交付 V1.0

2026-10-21；候选 **D1-20261021-INPUT-SINK05**；任务INPUT_SINK05_FIX。B06/P2、B07/P2及同类终态来源/原响应顺序已集中修复，coder有限离线验证通过，新独立复核 **PENDING**。旧INPUT_SINK01–04整包FAIL、原B01–B05/C01/A01A02有限独立通过及历史UNKNOWN保留；**D1 NOT_PASSED，M0 NOT_STARTED**。

依据 [开发要求](D:/CodexProjects/VideoKit/docs/milestones/D1_INPUT_SINK05_FIX_CODER_REQUIREMENTS_V1.0.md)、[完整复审报告](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK04_FIX_REVIEW_REPORT_V1.0.md)，后者SHA256 `f527fea952e07f8ee568272170c7ad7b44ae956e2e047fb860d0d1d51796f8c5`。两项及相关顺序一次性交接，不以绿色旧矩阵覆盖新顺序，也不冒称整包独立关闭。

## 修复结果

**B06：所有终态来源经过同一个不可逆采纳门。** TemporaryOutput的首次/迟到READY原回调、等待返回、QUERY、readonly原authority及派生coordinator结果，统一进入原owner内同步转换函数。保留READY与ABORTED互斥、已知token不可替换、终态不倒退WRITING；UNKNOWN不抹既有事实。coordinator自身的ACK/QUERY结果同样使用其现有状态中的统一不可逆门，不再由各分支直接覆盖终态。

原响应到达与是否可采纳分列：`readyResponseReceived`、`readyResponseSucceeded`记录原传输终局事实，`readyResponseAccepted`、拒绝原因与既有readyAck/abortedAck记录采纳。形状合法的迟到token若与已确认ABORTED冲突，原响应仍记录成功到达，但拒绝采纳，保留ABORTED、首错和protocol UNKNOWN；不ready+aborted双成功、不新RPC“纠正”、不删除原ACK事实。原token私下保留，不写进日志。

已经出现的冲突不能仅被匹配的迟到ACK或派生缓存结果清除；只有准确、兼容、同原task的原QUERY或readonly仲裁证明可收敛，拒绝历史仍留存。readonly事实可来自已进入的原READY/ABORT/QUERY仲裁，不要求为获取证明新增QUERY；默认UNKNOWN仍保管。COMMIT ACK/readonly结果也保持原READY与不可逆业务结果约束，既有首错/字节UNKNOWN不退款。

**B07：原方法/工作返回、原响应到达、原观察回调返回、原SDK线程返回分别核验。** 所有原READY/ABORT/QUERY response及真实whenComplete返回stage保留在原对象中。coordinator在既有八项上界内保留准确原call/result/observer引用，只有同原observer已返才可剪除；原executor线程引用仍保留，最终必须终止并join。没有新executor、状态平台、释放ledger、验证计数或宿主协议字段。

QUERY准确确认READY而原READY response仍pending时，完整收尾稳定 `OUTPUT_ORIGINAL_PENDING`，不泄内部IllegalStateException，也不提前关停仍需原响应的executor。同原正确ACK返回后，还须实际observer返回、executor退出和每个准确原worker join，才移除owner。计数0只是防护信息，不能证明物理归还；本批实际检查计数0、原observer/worker尾段仍活时保持pending。

等待observer/原线程采用有限界；合法尚未就绪保留同原对象，不cancel、不替换任务、不重RPC。ABORT/QUERY为解决在途READY的原仲裁仍可合法进入；后继COMMIT和完整返回必须通过完整门。生产只改TemporaryOutput与候选SinkCoordinator，其他host/输入/registry/muxer/native/依赖不改。[差异与补丁](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/source-differences.json)。临时诊断字段不是M0 API定版。

## 原复现与有限顺序证据

旧B06/B07检查原样在旧准确源码和旧production JAR优先两路径重新运行，均复现：ABORTED后迟到READY制造双终态，以及原READY响应未完成时的内部unchecked异常；原原始日志、argv和源pins保留。[旧生产复现](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/input04-reproduction/contradictory_aborted-production.stdout)。

| 本批套件 | 源码 / 新production JAR优先 |
|---|---|
| 原两场景安全断言 | 2项，两路径通过。B06保留raw响应并拒绝矛盾采纳，默认UNKNOWN仍持有；B07正常同token原ACK未到稳定pending，准确原回调/线程返回后收敛。 |
| owner有限顺序 | 30项，两路径通过：QUERY先、READY ACK先于QUERY、ABORT ACK延迟、readonly仲裁先、矛盾readonly先于晚ACK、成功/不同token/失败/取消晚返、原observer/原coordinator worker/host物理尾段。 |
| coordinator自身顺序 | 7项，两路径通过：QUERY先确认终态而原调用仍等待，晚同token/冲突token/失败/取消不能倒退；计数0但实际observer仍在同一原worker尾段时不归还，放gate后join该线程。 |
| 既有回归 | 原20/17/23/63/5、88返回值、33状态/授权、原QUERY2、authority3、私有cause取消6均两路径通过；tester新增host返回8源码原样复用并两路径通过。 |
| 文档入口/根 | 真实完整入口源码/JAR两路径执行通过；local_check与完整runner分别实跑正确新根及同7种错误路径拒绝，未写旧根或候选内。重复执行与重叠条件不冒充新增不同场景。 |

最终 **local-005**、源码 **suites-004**、production **suites-005**。完整原JVM回执、原stage身份、采纳/拒绝原因、firstFailure、原keeper与线程、RPC次数均保存。有限gate在最终有效检查全部释放，同原response/实际observer/SDK worker及适用host delivery线程真实返回/join，最终source/output keeper0。合法迟到可收敛；矛盾来源无准确兼容证明时稳定失败保管。

这里没有数学全状态/完整宿主协议证明。外部完成方可能是持续存活的调用线程；其observer已返与该调用线程仍活不是同一事实。SDK拥有的原executor线程必须实际退出/join，仍拥有host任务尾段的线程由原authority保持未返；不能据线程数或计数0放行。[顺序矩阵与原观察](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/response-order-matrix.json)、[响应事实/采纳/物理模型](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/response-fact-adoption-model.json)、[生产完整顺序日志](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/suites-005/orders.stdout)、[零计数真实尾段](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/suites-005/coordinator-orders.stdout)。

初版新增顺序测试在释放coordinator gate后立即假定worker已返回；正确的稳定pending到达其错误的测试cleanup，初版exit1、stderr及准确测试源码留存。仅修正测试为有限等待同一原response/worker并实际join，没有为此放宽生产门。该初版失败进程退出不计为owner归还证明；最终有效两路径均实际清理。[原型检查历史](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/prototype-check-history.json)。

A01共享源/跨factory/epoch和预算保持；A02 physical10/ACK3/callerPos3、late actual4/ACK下界0/UNKNOWN4及private block/首错不清、不重发/退款。19项逐行保留旧独立裁定并列本批coder结果；S03/S06有限修复待独立复核，S05真实平台仍NOT_RUN。[19项映射](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/independent-regression-map.json)、[批次验证索引](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/batch-validation.json)。

## 文档工具与构建

完整文档命令直接调用 `tools/review_all.py --output <本批正确新根内的新子目录>`，冻结时先核全部seal文件，再真正调用同一local_check外置编译及两路径。新根为D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE；旧04/03根、候选内、伪前缀、遍历/相对、根本身或复用目录拒绝。实际positive执行50条顶层入口/套件回执全exit0，编译/源码20组另有子回执；不是50个新增场景。[入口根回归](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/tool-root-regression.json)、[完整命令实测](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/review-runner-gate/summary.json)。冻结前自检明确为CODER_SELF_CHECK；冻结后只读入口外置回执随负责人交接另提供，包内不再写入。

一次必要严格离线实际Android/Media3 ABI构建 **build-main-001成功**，33tasks全部executed。15runtime坐标、两锁、verification XML、真实JVM deps与旧包逐字节一致；strict verification、verify-metadata=true、LockMode.STRICT。实际296项=121binary/35module/140POM、175metadata副本绑定原pin，无新版本/pin/binary下载。原三依赖有限离线来源/Apache准入不扩大为release/平台/新修复独立通过。[构建](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/build-main-001/receipt.json)、[实际消费](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/actual-consumption/summary.json)。deprecated提示原stderr保留。

旧INPUT_SINK04的705项及此前2978项，共 **3683旧冻结文件**、七个原seal/各原ZIP逐项保持；原FAIL、UNKNOWN、tester失败记录不删除或改写。[历史保全](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/frozen-baseline-preservation.json)。

## 产物与未结范围

| 文件 | 字节 | SHA256 |
|---|---:|---|
| [production JAR](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/artifacts/input-sink05-classes.jar) | 91676 | `6fbf307a4f0a06f45606ad9a162fcad95330924c2f220b5f68cec1e851916b0b` |
| [compile probe APK](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/artifacts/input-sink05-compile-probe-debug.apk) | 6310283 | `0b5fc8d530c8159c9283d670472255b883d97ad3885e2bae8fd427d25c1148b7` |

APK com.videokit.d1input/versionCode5/versionName D1-INPUT-SINK05/min31/target36，无权限、组件/native/test helpers，未安装。固定本地apksig/JDK v2验签通过，证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。[产物审计](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/artifact-audit.json)。

[完整ZIP](D:/CodexProjects/VideoKit/docs/coder/D1-20261021-INPUT-SINK05-source.zip) 与 [seal](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/input-sink05-freeze.json)记录所有交付文件/归档身份；seal自身hash随交接另给避免循环。排除镜像/Gradle缓存/JDK/SDK/build/classes，包含真实deps、实际metadata、源码、原失败和最终通过证据。

原opaque host能力、CompletionStage/observer契约与宿主诚实原task/token/readonly证明仍是依赖，不证明恶意不合约实现、宿主持久化账本/跨进程发布、token密码学或同物理FD；未增加不存在的返回身份/nonce/协议。真实Android FD/fsync/codec/muxer、媒体容器/内容/timeline、真实COMMIT/发布均NOT_RUN。

SDK/ADB/5037/设备/占用/旧handle查询0，无native/外部host构建，未生成或启用执行许可。历史P0/J11危险链、C13 FAIL、UNKNOWN及FFmpeg/release/model/media许可未结项不减。完整冻结后请tester集中复审，不原地单项修改，不自动下一批/M0。[顺序模型](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK05_RESPONSE_ORDER_MODEL_V1.0.md)、[独立可执行入口](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK05_INDEPENDENT_CHECK_PLAN_V1.0.md)。
