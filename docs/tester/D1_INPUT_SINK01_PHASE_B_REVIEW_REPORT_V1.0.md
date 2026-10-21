# D1_INPUT_SINK01 阶段 B 整包离线复审报告 V1.0

2026-10-21；tester；候选 `D1-20261021-INPUT-SINK01`。按负责人正式交测、阶段 B 测试要求及阶段 A 十九项清单，复审完整冻结包，并使用已有 JDK 在 tester 独立目录执行检查。

**整包结论：FAIL，集中提交两项缺陷（P1 一项、P2 一项）。** 真实 Media3 接口、A01/A02 的目标修复、固定依赖身份和多数有限边界回归通过；新增异步宿主原任务尾段检查复现输出资源提前归还及 flush 准入状态错误。两项问题同时存在于冻结源码编译结果和交付生产 JAR，不是只在测试替身中修改产品逻辑得到的结果。请集中修复、重新冻结整包后复审。

本报告不裁定实际 Android 媒体处理通过。D1 `NOT_PASSED`、M0 `NOT_STARTED`；真实 FD/fsync、MediaCodec/muxer、容器隔离验证、宿主业务 COMMIT 均仍 `NOT_RUN`。本轮 SDK/ADB/5037/设备/占用/旧 handle 查询及 Gradle/Android 构建全部为 0，没有启动后续批次。

## 1. 身份与保全

| 对象 | 独立核验结果 |
|---|---|
| 交付说明 | SHA256 `9fc09bf6ce1293433706e748d0286dcb60264127676f18edb751b5df78b6dd38` |
| 冻结 seal | SHA256 `128113fd40b958b56823cb76b230833b5cc9a42aff0f0bcfab7a5db90038a238`；334 条文件的字节数/hash 全部一致 |
| ZIP | 333 个唯一条目与 seal 逐字节核对；SHA256 `ed9332f19ca79824324b82bc06634ed4a2b66dc0524d24be3d8180ddceb430c1` |
| APK | 6,372,274B；SHA256 `a480294485c93e5d354cf47bc4466c2c7695bb53ce4983bcf1da5e7c274d656d` |
| 生产 class JAR | 79,895B；SHA256 `b297ec02714042d9982ffd399f248c12bf68d40a4fb34cc08cb1eda09d871b12` |
| 最终源/依赖输入 | 1,037 条实际文件身份逐项匹配，包含固定缓存 artifact；未修改共享缓存 |
| 原冻结包 | RENDER01 477、RENDER02 404、capture-adapt 818，合计 1,699 项全部保持原 hash |

完整审证见 [frozen-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/frozen-audit.json)。旧 N2 ABORT、旧 scope 的消费/UNKNOWN、ENV_WAIT 与历史设备报告不回填、不清零、不改写。

## 2. 两项集中缺陷

### B02 / P1：宿主验证或 COMMIT 原任务尚未退出，输出已被宣称归还

位置：[TemporaryOutput.java:83](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/src/com/videokit/d1input/TemporaryOutput.java:83)、[TemporaryOutput.java:91](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/src/com/videokit/d1input/TemporaryOutput.java:91)。`writerReturned()` 只核原 writer/descriptor 的归还；`markReady()` 和 `finishOriginalCallbacks()` 没有同时核 `host.originalOperationsReturned()`。`call()` 在 future 完成时已经清掉 `pending`。SinkCoordinator 的自身线程 join 不能替代宿主原异步任务的退出证明。

独立受控宿主明确区分 writer 已退出与后续原任务仍存活，使用同一个原线程和有界 latch 保留尾段，未伪造产品成功状态：

1. 4B 写入、flush/原 writer close、reopen/hash 正常完成。validator 返回字段准确的受控回执，其原宿主尾段线程仍存活，此时 `originalOperationsReturned=false`、`writerOriginalsReturned=true`。
2. `verifyAndValidate()` 返回后调用 `markReady()` 和 `finishOriginalCallbacks()`，实际得到 `READY=1 ownerReturned=true hostOriginalReturned=false retained=0`。
3. 另一路完成正常受控 READY，显式宿主 COMMIT 的 future 已 ACK、原 COMMIT 线程尾段仍存活，再调用 `finishOriginalCallbacks()`，实际得到 `committed=true ownerReturned=true hostOriginalReturned=false`。

预期：保持原 owner/资格占用，原宿主操作真实退出前不得报告完整归还；验证原任务未退出时不得越过既定原任务门发布 READY。COMMIT 的原 ACK、业务状态与原任务物理归还也应各自保留。实际：原输出 keeper 已移除，下一输出可复用名额，而旧宿主任务仍在运行，破坏本批原资源未知时保留容量的要求。此处只证明受控端口接线错误，不声称实际业务已发布或真实隔离格式验证执行。

修复要求：统一原操作准入和终局归还判定，覆盖 writer 之外的 reopen/validate/READY/显式 COMMIT 等原宿主操作；原 future、原线程与 coordinator 线程均需按职责保留并实际归还。不能仅补一个早完成计数或新建替代线程证明成功。若现有端口不足以证明 validator/commit 的原返回，需补清准确契约及可信原返回证据，无法证明时保持 pending。

### B01 / P2：flush 尚未准入，attempted 标记已消费，原尾段归还后仍无法完成输出

位置：[TemporaryOutput.java:67](D:/CodexProjects/VideoKit/docs/coder/d1input-sink01/src/com/videokit/d1input/TemporaryOutput.java:67)。`finishWriter()` 在调用 `call("FLUSH", ...)` 的准入检查之前先设置 `flushAttempted=true`；该检查发现原宿主任务未返时只抛 `OUTPUT_ORIGINAL_PENDING`，没有调用原 flush。

复现：原宿主 write 实际写入并 ACK 4B，但同一个 write 原线程仍在尾段等待；关闭 producer 后调用 `finishWriter()`，得到预期的 pending，flush/close 均未调用。释放并 join 同一原 write 线程后再次调用 `finishWriter()`，实际 `flushCalls=0 closeCalls=1 retry=OUTPUT_ORIGINAL_PENDING`，状态 `flush=false closeSucceeded=true error=null`。之后该对象永久跳过 flush，无法走正常验证/READY。

预期：未准入不算已执行；待原任务返回后，能恰好执行一次 flush，再执行一次 close，进入验证。实际把短暂背压变成正常输出无法完成。相邻 `closeAttempted` 也在调用前设置，修复应一起核对准入与执行边界；本次动态证据直接复现的是 flush 分支。不得对已经真正执行、超时或 UNKNOWN 的原 flush/close 盲重试；仅对从未准入的操作恢复正确资格。

两项最终复现原始输出见 [源码编译检查](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/independent-boundaries-2.stdout) 和 [交付 JAR 优先加载检查](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/independent-boundaries-3.stdout)。后者 classpath 将交付 JAR 放在 tester classes 前，确认缺陷存在于实际交付产物；测试辅助类从 tester 目录加载，真实 Media3 类来自固定依赖。所有受控尾段在 finally 中释放并 join，结尾 source/output keeper 为 0；没有遗留本机 pending 线程。

## 3. 阶段 A 十九项与新增独立回归

在 tester `independent-001` 新目录实际运行冻结入口 `local_check.py --review-output`，重新编译准确冻结源，20 组检查 exit0。该次不是直接引用 coder 的 local-007 结果。另写 tester 自有边界类，最终五个场景在源码编译类与生产 JAR 上均实际运行；新增场景用于补原自测遗漏，未修改产品源。

| 清单 | 阶段 B 结果与准确范围 |
|---|---|
| I01 | PASS：真实 DataSpec/TransferListener，offset5/length7 的 3+3+1 短读、EOF、transfer bytes/lifecycle，重复 open/close |
| I02 | PASS：未知长度保持 -1，3+2 后 EOF |
| I03 | PASS：3GiB+7 逻辑偏移、64KiB 单块；未创建巨大文件 |
| I04 | PASS：long 溢出在调用 provider/写 caller buffer 前拒绝 |
| I05 | PASS：host 返回 0/-2/超过 count 均拒绝 |
| I06 | PASS：权限/路径错误脱敏，稳定 code，无私有 cause |
| I07 | PASS：同 DataSource 同步读重入拒绝 |
| I08 | PASS：取消唤醒、迟到结果只落原 private buffer，caller 目标不被覆盖，读/close 原结果保持 |
| I09 | PASS：首 consumer 关闭不释放源；两个 consumer、原读/close 与原线程完成后归还 |
| I10 / A01 | PASS：共享 provider 两 consumer 峰值 1、第二个 host read 未准入；queue0 满足 ≤4；不同源并行且总源≤2；独立补测同 Provider 跨 factory 拒绝 |
| I11 | PASS：close 后旧代实际归还，再开新 range/epoch；独立补测新 offset7 的内容准确，不能复用旧结果 |
| I12 | PASS：已观察到 FAILED 的原 close 无自动重试，显式走同原 bridge 的失败恢复；PENDING/UNKNOWN 不按失败重试 |
| S01 / A02 | PASS：实际 prefix7 后抛错，ACK 下界0、caller position0、UNKNOWN；另补首 ACK3、下一次实际写7后失败，physical10/ACK下界3/caller position3，首错后无重发，abort 保留 UNKNOWN |
| S02 | PASS：输出16MiB资格上限，超限前不发新 host write；复用64KiB块计数，无16MiB样本落盘 |
| S03 | 部分 FAIL：原 close 异常、late write/close、future 后原线程尾段及 same-close-once 基线通过；新增 finishWriter 未准入 attempt 错误见 B01 |
| S04 | PASS_LIMITED：真实生成4B宿主 FileChannel write/force/close，经原桥只读 reopen，失败验证不得 READY；摘要损坏/validator拒绝也不升级成功；不等于媒体容器已验证 |
| S05 | NOT_RUN_PLATFORM：真实 Android FD/fsync、muxer close、真实容器重开故障未执行。顺序/随机能力拒绝和受控随机 offset 接线通过，不替代此项 |
| S06 | FAIL：正常受控 close→hash→validator→READY→显式 COMMIT 分层通过，未发生自动业务提交；新增后续原宿主任务尾段过早归还见 B02 |
| F01 | PASS_LIMITED：真实 Media3 1.9.3 DataSource/Factory/DataSpec 等类型及固定依赖身份通过；真实 Android 主 Looper/FD 运行仍 NOT_RUN |

本机 UI 线程拒绝测试使用明确的 worker-rule 平台端口；另静态核 AndroidInput 实际 `Looper.myLooper()==Looper.getMainLooper()` 绑定，在主 Looper 前拒绝同步读写/等待。errno 用明确 Android system 测试端口执行 ENOSPC/EDQUOT、EACCES/EPERM、EPIPE/EBADF/ENODEV 的稳定脱敏映射，没有把端口注入称为平台实际故障。

样本 pattern seed `539365408`；最大候选测试块65,537B，新增实际字节块≤32B。原4B落盘样本 SHA256 `e6e8cb429864b8e8d7fe95e53360dbd00756316813fb1e4a03a778d4632dbde6`。输出预算检查复用块计数；输入大偏移由受控 provider 提供。受控 validator 的类别字符串/字段绑定只用于验证接线，真实 CPU/slot/death/内容/timeline 证据均未产生。

## 4. 实际框架、依赖准入与产物审证

**三项新增使用准入：PASS_IDENTITY_LICENSE_FOR_THIS_OFFLINE_CANDIDATE。** `media3-datasource:1.9.3`、`media3-database:1.9.3`、`exifinterface:1.3.6` 的已缓存 AAR 和固定 module hash 同既有 verification pin 匹配；本轮独立重算原 AAR、module 中声明的 AAR hash 及由真实 AAR 提取的 classes.jar 身份。datasource AAR SHA256 为 `ccaf5530a31e64dffe2a803feeeb654e7e81fc4a2597f6d929ce7a9aba7ff13e`。真实 datasource 类型进入独立 JVM 回归；没有自造同名 Media3 接口。

逐项核固定官方 Google Maven POM/module 的保全文件、HTTP 200/最终 URL/字节数/hash 回执；三份 POM 均声明 Apache-2.0。保存的 Apache 原文11,358B、SHA256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` 与来源回执一致。此结论限提供的固定来源证据与本候选新增使用，不扩大为完整产品发行、其他库或 FFmpeg 许可放行；本轮未联网重新取证。

15 个锁定坐标的候选使用范围清楚，与旧包相比只新增上述三项；未升级既有产品版本。`verify-metadata=true`、verification strict、`LockMode.STRICT` 保持；verification XML 同原 RENDER02 逐字节相同。独立核实际005构建632行事件中的消费 ID、artifact/坐标与296条消费清单绑定，121 binary/35 module/140 POM 均匹配 pin；175份 metadata 副本全部 hash 一致。原005 receipt 为 exit0、严格锁不写新锁，原日志 BUILD SUCCESSFUL。没有把全缓存1,037条输入当实际296项消费，也没有为复审重跑 Gradle。

APK 二进制 manifest 独立解析：`com.videokit.d1input`、version1、min31/target36，无权限、无 Activity/Service/Provider/Receiver，无 native .so。DEX 4,388个类定义中实际适配/Media3 类存在，`InputSinkCheck` 和 JVM URI/errno 平台替身不在交付中。原 upstream HostFixtures 宿主适配辅助类仍包含在 compile probe，并非新测试入口；平台 API 合成类不据此认作 JVM fixture。生产 JAR 50项，不含 Android 测试替身或 InputSinkCheck。

通过已有缓存官方 apksig 库与 tester 新编写的 JDK 验证器，实际独立验证 v2 签名及单签名证书 SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。没有调用 SDK 工具。真实 AndroidGrantedStream 绑定同原 E4Owned 与 FD，flush/fsync、原 closer 和实际 errno 来源仅编译/静态核证；FragmentedMp4Muxer 仍接原 E6 六样本 EOS/helper、AVC256×144/≤2秒/单样本≤262144B，未造新容器。

## 5. 验证限制、过程记录与集中返修

tester 新增检查初次编译因遗漏 E13SourceGroup import 失败，原 stderr 保留；补 import 后通过。静态审证初次对所有 upstream HostFixtures 或所有 `android/` DEX 定义作了过宽排除，后核实际来源，收窄为 checks 与准确 JVM fixture 定义；这是 tester 审证规则修正，不是候选产品修改或新增产品缺陷。后续重复仅因加强原 write 线程复现、补 ACK3+故障7、以及交付 JAR 优先加载的产物一致性检查；没有在成功后无理由重复整批构建。

原桥/registry未替换；E13SourceGroup 副本只增加 range 委托，SinkCoordinator 副本增加自身原 callback 线程的 join。该 join 的有限正确性保留，不能覆盖 B02 的宿主任务缺口。原 P0、J11权限/RCE链、C13历史 FAIL、其他平台 NOT_RUN/UNKNOWN、外部分发许可和模型权利等门全部保持原裁定；历史三项有限真机 PASS 不被清空。既定 Flutter Theme/18PPT UI、SkinKit 延期不因本候选改变。

请负责人一次性交开发修复 B01/B02，要求同时保留本报告已通过的 A01/A02/真实依赖/未知量不退款边界，补两项原场景回归，再重新冻结源码、JAR/APK、消费证据和整包 seal 后交 tester 复审。本轮只集中交报告，不逐项向 coder 打断，不自动设备测试或进入下一批。

历史 N2 指令曾被 tester 在 compaction 后误套为新暂停，现已核实更正；独立 [协调记录](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/coordination-correction-20261021.json) 保留准确来源/范围。原10月17日批准、N2报告和既有账本均未改；阶段 B 已按负责人明确安排恢复并完成。

全部证据位于 [D1_INPUT_SINK01_REVIEW_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE)。报告冻结 hash 后主动发送负责人，另存发送回执；不修改已发送报告。
