# D1_INPUT_SINK01 集中离线交付

2026-10-21；候选 `D1-20261021-INPUT-SINK01`，承接原D1第3/4项。本批完成实际Media3输入薄适配与临时宿主输出能力/事务接线、有限本机回归和实际平台接口编译，等待独立阶段B复审。**D1未通过、M0未启动；真机、Android FD/muxer/容器验证、实际业务COMMIT未执行。**

依据 [开发要求](D:/CodexProjects/VideoKit/docs/milestones/D1_INPUT_SINK01_CODER_REQUIREMENTS_V1.0.md)、[测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_INPUT_SINK01_TESTER_REQUIREMENTS_V1.0.md) 和 [设备等待离线推进规则](D:/CodexProjects/VideoKit/docs/OFFLINE_PROGRESS_DURING_DEVICE_WAIT_V1.0.md)。阶段A报告SHA256 `db797e0a7714982b85dc474eabc70273c9ea49fc97c88fdf98a54ea0874379a1` 的A01/A02和19项独立清单已纳入本批，未把基线结论冒作新候选通过。

## 实现结果

| 范围 | 完成与证据边界 |
|---|---|
| 实际DataSource/Factory | 实现真实Media3 1.9.3接口；使用实际DataSpec、TransferListener、DataSourceException，不定义同名Media3假接口。宿主readAt仍经原AsyncReadBridge/LeaseRegistry/E13原归还门 |
| source range/epoch | position/length、未知长度/EOF、短读、长偏移和溢出前拒绝、重复open/close、close→新代range、取消迟到私有buffer、错误脱敏及listener生命周期已本机验证。显式length的open返回request length，EOF按原源返回，符合[固定1.9.3接口契约](https://github.com/androidx/media/blob/1.9.3/libraries/datasource/src/main/java/androidx/media3/datasource/DataSource.java) |
| A01共享源准入 | 一个实际Provider capability只能有一个活动factory；同factory/sourceVersion/epoch的两个consumer共享readAt原结果门，**每源在途1、等待队列0**，全局最多2个宿主源。未把原Runtime队列16或per-consumer门称为新限额 |
| 宿主OutputSink | 写前协商顺序/随机/flush/close/reopen；不支持能力拒绝，不缓存整文件或用SDK路径写绕宿主。WritableByteChannel与host writeAt薄接、partial成功返回、原写/flush/close及重新打开/摘要可执行 |
| A02真实量/UNKNOWN | controlled stream实际写7后抛错：SDK只报告已确认下界0、attempt/reservation32及UNKNOWN；不把32说成实际，不rewind或重发。首错sticky，拒绝READY/COMMIT，abort不回填成功、不退款UNKNOWN |
| 事务分层 | producer view关闭→原flush/close返回及原host任务实际归还→只读reopen/字节摘要→独立格式验证port回执→原SinkCoordinator READY→显式host COMMIT分别处理。close、hash或READY不自动业务提交 |
| 实际平台接口 | Android主Looper工作线程门、授予流/E4Owned/原FD fsync、稳定errno映射和原Media3 FragmentedMp4Muxer/E6六样本EOS路径均实际编译。真实Android/codec/容器执行仍NOT_RUN |

源码入口：[HostInputFactory](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/src/com/videokit/d1input/HostInputFactory.java)、[HostDataSource](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/src/com/videokit/d1input/HostDataSource.java)、[HostOutput](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/src/com/videokit/d1input/HostOutput.java)、[TemporaryOutput](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/src/com/videokit/d1input/TemporaryOutput.java)、[成熟muxer绑定](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/src/com/videokit/d1input/MatureMuxerBinding.java)、[Android授予流](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/android/com/videokit/d1input/AndroidGrantedStream.java)。

## 原资源与能力边界

input factory仅作有限capability准入，不维护第二份source release账。原handle、原异步operation、failed close、registry及原线程退出仍由E13/AsyncReadBridge判定。**`sourceSnapshot()`是原registry原始计数，`Snapshot.released()`单独不证明原executor线程退出；完整返回以`originalsReturned()/awaitOriginalReturns()`为准。** close/cancel不等待平台；同步open/read/close及await禁止UI等待，Android绑定检查实际main Looper。

队列0是本候选明确策略：第二个共享源readAt在原返回前拒绝，不将其排到原runtime队列16后声称queue4。全局2源容量在原资源未知时保留。一个factory最多2个DataSource对象、每代最多2个consumer；单对象重复open在旧代原归还后新建epoch。相同Provider对象不能另建factory绕门；跨IPC capability的最终规范身份仍待M0决定。

原close明确FAILED后只提供显式owner调用原bridge已有retryFailedClose；PENDING/超时/UNKNOWN不自动retry，不换handle。数据源旧回调只触及原private buffer；新代不得接纳旧结果。TransferListener end是前端传输事件，不是SourceReleased或物理线程归还证明。

output保持同一原grant、stage和private block，单次host I/O≤64KiB、同一原操作未返不发后续写/flush/close。timeout只停止新准入，保留原结果；完成future后还须host证明同原writer/tasks真实归还。无证明则保持PENDING。原SinkCoordinator新增原callback线程记录/join；无通用IO执行器、codec、容器、网络/NAS或新资源平台。

Android授予流只接宿主已经登记的E4Owned与同一FD别名，SDK不自行开输出路径、不添加第二FD closer；宿主仍负责授予/原fence/重新打开权限。实际grant错误映射ENOSPC/EDQUOT、EACCES/EPERM、EPIPE/EBADF/ENODEV为稳定脱敏code。JVM仅执行明确errno平台端口，不冒称实际平台故障已测。

顺序写正常ACK逐块累积摘要，reopen需完整EOF、字节数与原已确认摘要一致；随机写按宿主能力传递offset，reopen完整摘要交独立validator判内容/结构。不能用同长度或hash-only回执获得READY。`HOST_ISOLATED_FORMAT_V1`是临时受信宿主验证port的回执类别，**本机受控validator通过只证明接线/字段绑定，不证明实际隔离CPU容器验证或媒体有效。** 原实际C14验证者的death/slot/source/内容/timeline前置未被本批替换。

## 依赖、许可和构建

沿用Media3 **1.9.3**；本探针15个锁定坐标，相对旧RENDER02使用范围新增 datasource1.9.3、database1.9.3、exifinterface1.3.6 三项。它们的AAR/module均来自原缓存及既有verification pin；没有新二进制下载或版本升级。另获取这三项的固定官方POM/module，module与既有pin逐字节一致，内含AAR SHA256与原二进制一致；POM均声明Apache-2.0，许可证原文及来源回执保存。见 [官方材料](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/evidence/official-added-dependencies/receipt.json)、[许可差异](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/evidence/dependency-license-difference.json)、[SBOM](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/input-sink01-sbom.cdx.json)。本批新使用是否独立准入仍PENDING_REVIEW，不自签批准。

datasource AAR SHA256 `ccaf5530a31e64dffe2a803feeeb654e7e81fc4a2597f6d929ce7a9aba7ff13e`。测试使用由真实AAR提取的classes.jar及原pin的Guava等依赖；所有classpath hash留存。仅Android URI/errno和工作线程策略为明确平台测试port，未仿Media3类。源集与APK审计排除checks/platform-fixtures，探针无组件、无权限、无native库，不安装。

严格`verify-metadata=true`、verification strict及`LockMode.STRICT`；最终构建不更新锁。verification XML与旧RENDER02一致，未关闭检查或加入观察hash求绿。最终005实际Gradle验证事件296项：121 binary、35 module、140 POM；完整消费描述副本、坐标/hash和原事件在 [消费清单](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/evidence/actual-consumption/summary.json)。静态全缓存不冒充实际消费闭包。

同批构建记录全部保留：001新缓存实际平台接口全量编译成功；002补平台errno分类后增量编译成功；003严格锁不写锁重放成功；004移除依赖合并带入的未使用ACCESS_NETWORK_STATE权限；005将muxer绑定收束到原E6六样本/PTS/单样本上限与EOS helper后最终严格编译成功。旧native/外部host工具未改或重建。最终产物与本机007源码一致；不是设备运行结果。

## 自测与保留失败

最终 [local-007](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/evidence/local-007/checks.stdout) 共20组有限语义检查通过，所有原JDK检查进程返回。A01实测共享源峰值1、第二consumer未再调用原provider；不同源可并行但第三源拒绝。A02实测controlled prefix7/attempt32及UNKNOWN，首错后无新写/READY/COMMIT。原read/close晚返、原host线程future完成后的tail、同原write late/cancel、双consumer首关闭、原callback executor实际join均覆盖。

还覆盖3+3+1短读、未知EOF、3GiB+7稀疏偏移、64KiB截块、long溢出、非法host count、私有错误脱敏、重复open/close、显式已失败原close恢复、能力拒绝、成功partial、16MiB输出资格边界、flush/close/reopen/摘要/validator失败、随机offset和READY/显式受控COMMIT分层。预算测试复用64KiB受控块计数，不创建16MiB样本；唯一实际生成落盘输出为4B，宿主真实FileChannel写/force/close后通过原桥reopen，验证拒绝后abort，未当媒体。

[阶段A十九项映射](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/independent-regression-map.json) 明列S05实际平台NOT_RUN；不是把19项都登记平台PASS。样本seed539365408，实际样本hash及逻辑偏移见 [样本身份](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/evidence/generated-fixture-identities.json)。无真实媒体、模型、巨大文件或旧宿主输出读取。

local001因测试lambda未final而编译失败；002实际DataSpec启动发现缺少运行classpath的真实Guava；003补原pin的真实传递jar后通过，004加实际4B host file，005补late-write及random，006补errno，007最终源码20组通过。旧失败stdout/stderr和原退出回执保留。交付整理首次因负责人中途追加A01/A02到活的需求文档触发来源断言，保留初始快照与新补充两个版本及 [演进记录](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/evidence/requirement-evolution.json)，没有改旧冻结源或再次重编译求绿。

## 产物身份及移交

| 产物 | 字节 | SHA256 |
|---|---:|---|
| [编译探针APK](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/artifacts/input-sink01-compile-probe-debug.apk) | 6372274 | `a480294485c93e5d354cf47bc4466c2c7695bb53ce4983bcf1da5e7c274d656d` |
| [生产适配class JAR](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/artifacts/input-sink01-classes.jar) | 79895 | `b297ec02714042d9982ffd399f248c12bf68d40a4fb34cc08cb1eda09d871b12` |

APK仅用于实际接口编译证明：`com.videokit.d1input` version1/min31/target36，无Activity/Service/Provider、无权限、无native，未安装。原缓存官方apksig经JDK验证v2签名，公钥证书SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，未调用SDK签名工具；[产物审计](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/evidence/artifact-audit.json)。

原RENDER01 477、RENDER02 404、capture-adapt818，共1699冻结文件/旧ZIP/源码/APK逐项未变；所有旧scope消费/UNKNOWN及设备ENV_WAIT保持原账。本批0 SDK现场/ADB/5037/设备/占用/旧handle查询，无设备release/激活层。三项旧有限PASS不回溯改写；完整D1/P0、实际播放/编辑/隔离、许可与实际业务提交缺口保持。

[接口可冻结与未决决定](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK01_INTERFACE_DECISIONS_V1.0.md)、[独立测试入口](D:/CodexProjects/VideoKit/docs/coder/D1_INPUT_SINK01_INDEPENDENT_CHECK_PLAN_V1.0.md)、[完成矩阵](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/completion-matrix.json)、[ZIP](D:/CodexProjects/VideoKit/docs/coder/D1-20261021-INPUT-SINK01-source.zip)、[seal](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/evidence/input-sink01-freeze.json)。源码/真实测试依赖/许可/构建证据/消费闭包/候选产物一次冻结，独立审查证据外置。平台NOT_RUN与新依赖使用准入由阶段B集中审定；不为设备等待停离线开发，也不自动进入M0。
