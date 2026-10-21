# D1_MEDIA3_CONTAINER01 阶段B独立整包复审报告 V1.0

日期：2026-10-21。测试人：tester。接收人：项目负责人（01a107c3-2bf9-7fa0-94a0-234258ca6774）。

## 1. 结论

**FAIL_NEW_P2_WITH_FUNCTIONAL_SCOPE_OPEN。** 本次对正式冻结的有限读取/薄接线交付进行整包离线审查，新增一项独立双路径复现的 P2 状态问题 **MC-B01**：只读重开原任务尚未物理返回的暂待状态，被新结构检查永久记为首错并消耗检查资格；同一原任务返回后无法继续。

新使用依赖的固定身份、许可和 strict 本地证据审查通过；真实 DefaultExtractorInput 的读取边界、预算、取消及既有 INPUT_SINK05 回归获得有限证据。**真实 MP4/fMP4 解析、六样本 AVC fixture、实际 mux/remux→Sink→结构重开目标仍为 OPEN/NOT_RUN**。平台链接限制和 fixture 不符属于已披露缺口，未据此额外判产品 FAIL。文档入口的 56 项退出0不代表56项容器功能通过，其中平台 probe 明确记录 NOT_RUN。

本批零 SDK/ADB/设备占用检查、零 Gradle/网络/共享缓存修改；无新编码器、fixture或平台替身。D1未通过、M0未启动；旧 FAIL/UNKNOWN/P0 门不变。完整集中反馈后停止本批，不自动进入设备、修复验证或下一轮测试。

## 2. 范围和冻结身份

依据 [正式测试要求](D:/CodexProjects/VideoKit/docs/milestones/D1_MEDIA3_CONTAINER01_TESTER_REQUIREMENTS_V1.0.md) 阶段B补充及负责人交测，审查候选 `docs/coder/d1media3-container01`；新源码重点为 HostMp4Inspection、MatureContainerRemux 和 TemporaryOutput 结构检查入口。

|对象|独立核验值|
|---|---|
|交付文档 SHA-256|18137c21ad6806b13d1a8d0a8b818b5be1b0db20ba7b07067900cda6018dfca7|
|freeze SHA-256|6d08e618dd1b98852830468a69b5048f65b55f4bc0a9117360c7bd414423c4ed|
|seal/ZIP|1045项（含ZIP）；1044个唯一ZIP成员，路径集合及逐项字节/hash一致|
|生产 JAR|108476 B；57f07b9f841487a5e76750ed0380656f72862e60caeef78a4ae9cb40d42e527e|
|APK|7208106 B；0979fc8fc8428f5ee8ada6fb4859450aa8a39f5acd67bba0d7872310bb7ea3aa|
|APK身份|com.videokit.d1input；versionCode 6；min31/target36；编译探针|
|签名|独立 apksig v2 验证通过；证书SHA-256 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f|
|原冻结/输入|8份旧seal的4511项保全；1043项源码/依赖输入核对|

APK的4927个DEX类、JAR的64个条目已检查：测试检查类未进入产物，沿用主机测试替身未混入APK，无新增组件、权限或native库。未安装、启动或把签名/编译通过当作平台效果。

[身份及依赖审计](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/admission-and-artifact-audit.json)、[签名输出](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/signature-1.stdout)、[收尾保全核对](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/post-review-preservation.json)。

## 3. 新使用来源、许可和 strict 实际消费

在运行新增库检查前，独立核对 media3-extractor/decoder **1.9.3** 的官方固定坐标/URL来源记录、保全POM/module、Apache许可文本、AAR及提取classes.jar身份。AAR/module旧精确pin未变，module所列AAR hash/大小与实际一致，classes.jar逐字节匹配AAR成员。许可文本11358 B，SHA-256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`。仅对当前有限离线新使用判准入通过，不证明Android平台运行。

新增精确POM pin分别为 extractor `5a94ba0b9b0ac2786d9429f8651b930a0c7399312a8b981a3e3fbdc9bc4c9de3`、decoder `34b8d1530c8cc0ca7943571ae9b64304174e31ccd9e24991a5e882c00200a1ba`；原pins保持。verify-metadata=true、strict及LockMode.STRICT保留，settings锁不变，应用运行闭包由15增至17坐标。

独立关联冻结构建的636条消费事件及300项实际消费：**123 binary、37 module、140 POM**。相对05新增的实际消费仅两库各AAR/module，共4项；新增POM pin是本次来源材料，不能表述为新增POM实际消费。原消费身份保持。本次核验的是保全材料和来源记录，未重新联网下载，也未声称独立验证网络传输或缺失的原HTTP响应头。未关闭metadata、改版本或引入同名Media3实现。

## 4. 实际执行及有限通过

在新绝对路径 `D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/independent-001` 执行冻结文档命令：

```text
python -X utf8 -B docs/coder/d1media3-container01/tools/review_all.py --output D:\CodexProjects\VideoKit\docs\tester\D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE\independent-001
```

实际使用已有Python/JDK绝对路径，源码编译输出和生产JAR优先两路径均运行，日志记录原argv、起止时间、原进程返回、JAR hash及ORIGIN。共56项退出0；既有原响应/observer/worker、首错、终态、取消、partial UNKNOWN、输入错误、额度与保管回归执行完成。各子检查计数有继承和重叠，不叠加成独立容器功能通过数。

另编写独立 [IndependentContainerBoundaryCheck.java](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/IndependentContainerBoundaryCheck.java)，只编译测试辅助类，不修改冻结产品。源码与JAR优先路径最终各 **7项边界通过、1项问题复现**，所有实际线程返回，source/output keeper最终均0。

|独立检查|实际结果与限制|
|---|---|
|真实DefaultExtractorInput peek/reset/短读|3+3+1底层读取，位置0/3/6，物理预算7；peek重置不重复计费；未执行真实容器sniff|
|跨重开累计8MiB|同Reader先4MiB，close/reopen再4MiB，共128次64KiB原read；下一读在provider前拒绝；重开后逻辑位置4MiB与累计物理8MiB分开|
|绝对终点/未知长度|source73、open位置5返回remaining68，input.length=73，读取后position8；未知长度保持-1、从2读至5后EOF|
|取消及迟到原任务|真实DefaultInput调用者可返回；同一原read和close未返回时仍保管；迟到私有字节未交调用者；原尾段放行后实际归还|
|检查准入|false capability、null container、seek=-2/2000001在provider open/适配器配额分配前拒绝，未耗掉后续两适配器资格|
|真实超时对照|REOPEN超时保持OUTPUT_TIMEOUT_PENDING，观察同一原迟到结果和尾段后仍不盲目重发；无第二RPC，abort清理|
|remux缺输入证据|null Evidence以MP4_REMUX_INPUT_UNPROVEN在写入及muxer构造前拒绝；清理完成|

新增ExtractorInputCheck每路径7组真实输入组件检查通过，包括已知/未知EOF、取消、预开上限与失败不READY。原参考视频每路径known/unknown各一次完整EOF/hash，合计4次只读原文件扫描；**未解析轨道、提取样本或验证播放**。

review_all和local_check各7项输出路径反例，共14项：旧05根、新候选内部、伪前缀、`..`越界、相对路径、根本身、已存在子目录均非0拒绝，未创建新目标。见 [output-gates.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/output-gates.json)。

执行索引：[文档入口汇总](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/independent-001/summary.json)、[源码最终独立输出](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/independent-boundaries-source-1.stdout)、[生产JAR最终独立输出](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/independent-boundaries-production-1.stdout)。

## 5. 新增问题 MC-B01 / P2

**暂待原REOPEN物理归还被结构检查永久采纳为失败，尚未进行的检查无法继续。**

位置：[TemporaryOutput.java:129](D:/CodexProjects/VideoKit/docs/coder/d1media3-container01/src/com/videokit/d1input/TemporaryOutput.java:129)，涉及131–144行。入口先将hostInspectionAttempted置true，再发一次原REOPEN并requirePrevious；若原REOPEN已给ACK但原线程尾段仍活着，requirePrevious抛OUTPUT_ORIGINAL_PENDING，外层catch因attempted=true将其记入firstFailure。之后即使同一个原REOPEN任务真正返回，131行仍因attempted/firstFailure拒绝。

复现步骤（两路径一致）：

1. 完成有界原写入、flush、close和writer实际归还；没有取消、abort或先前业务失败。
2. 原Host执行一次reopenReadOnly，返回同一授权Provider的ACK，同时用门闩保留**该原任务线程**尾段，originalOperationsReturned=false。
3. 第一次inspectHostMp4Structure返回OUTPUT_ORIGINAL_PENDING。此时并无超时或失败；结构提取器/读工厂尚未构造，未发生结构解析。
4. 仅观察原回调归还，放行并join**同一原线程**，确认allOriginalHostTasksReturned=true，reopenRPC=1，不另起替代任务。
5. 再进入检查得到OUTPUT_NOT_VALIDATABLE，首错仍OUTPUT_ORIGINAL_PENDING，实际结构检查永久无法进入。随后执行abort清理，所有原线程/keeper归还。

最终原始日志包含 `cancelOrAbortBeforeRetry=false`、`hostOriginalReturned=true`、`reopenRPC=1`、`error=OUTPUT_ORIGINAL_PENDING`；两路径均readyEntered=false、commitAcknowledged=false。本问题是可用性/阶段状态错误，未观察到提前READY/COMMIT或资源错误释放。

首轮辅助检查曾在再次观察前调用abort，存在取消干扰，原日志原样保留；**本结论仅依据后缀-1的最终源码/JAR两次运行**，该两次在重入前从未cancel/abort。另设真实超时对照，确保建议不会清除真实超时、取消或UNKNOWN。

预期：沿用05原任务保管模型，原任务正常ACK而暂未物理返回应保持稳定待归还；返回后复用同一个已采纳REOPEN结果，允许尚未实际执行的结构检查第一次开始，不增加REOPEN RPC。实际：瞬时等待被当成首错，并消耗整个检查资格。

建议集中修复准入标记与暂待归还分类，保持真实失败/超时/取消及UNKNOWN不可盲目恢复。修复验收需含：原尾段持续时稳定pending、同原任务返回后使用原Provider、不重复REOPEN、不清真实首错、不提前释放，以及源码/生产JAR双路径。由于真实提取器当前平台限制，**本次不声称修复后容器正例即可通过**。

## 6. 真实容器目标的准确缺口

真实构造 probe 记录：Mp4Extractor缺 `android/content/pm/PackageManager$NameNotFoundException`，FragmentedMp4Extractor缺 `android/os/Parcelable`，FragmentedMp4Muxer缺 `android/util/SparseArray`。这些probe退出0只表示阻塞已记录；并未执行合法MP4/fMP4解析、轨道/sampleData/sampleMetadata、实际SeekMap、实际muxer写样本或remux比较。见 [生产路径平台输出](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/independent-001/platform-availability-production.stdout)。未为越过缺类添加新替身。

原视频 `test_media/imgs_and_videos/videos/sample.mp4` 权利记录为 Blender Big Buck Bunny 2008 / CC BY 3.0。大小349102 B，SHA-256 `720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9`。范围材料声明320x180、含AAC、8秒，不符单AVC256x144/rotation0/恰6个真实access unit要求，writeAdmission=DENIED_FIXTURE_MISMATCH；本次前后大小/hash一致，未改写或转码。原视频全EOF/hash通过不能补齐fixture资格、编码初始化数据、NAL表示/keyframe/PTS/时基证据。

阶段A的E6五项负例及接口证据保持，不重新写成六样本编码正例。E6静态约束仍恰6 payload、空EOS flags4在lastPTS+200000，非第7个媒体帧；payload≤2000000不等容器总时长≤2秒。真实timescale/舍入、duration、NAL AnnexB/AVCC转换和CSD比较、畸形atom内部内存限制、真实seek图及重开格式正反例均未执行。

后续由负责人统一安排准确运行环境及已准入合法六样本fixture。fixture须先提供来源/权利、工具和版本参数（如使用）、不可变hash/大小、CSD、逐样本表示/hash/keyframe/PTS/时基和EOS时长判据；平台执行条件须精确说明。届时才能测真实提取→成熟muxer→原Sink→只读结构检查。Android FD/fsync、解码、隔离内容验证/死亡/时序、业务提交和播放仍需各自证据。host结构类型不能签发HOST_ISOLATED_FORMAT_V1、validated、READY或COMMIT；当前静态与失败边界未发现此类越权放行，但成功结构路径未执行。

## 7. MC01–MC32逐项结果与证据保全

完整逐项输入、预期、阶段B状态及限制见 [independent-case-results.json](D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/independent-case-results.json)，覆盖全部32项。有限组件或旧基线通过均有后缀限制，不代替对应容器整链用例；MC26/MC30关联新增MC-B01。MC05/06/12/17/18/22/27/28/32真实路径NOT_RUN；MC03/20/21保持OPEN，其余亦按实际有限范围记录，不能据数量关闭功能簇。

最终再次核1045项候选未变、阶段A75项旧证据及原报告 `edb4cd48b9bd1c04f0d1f9ddff5f80a6a16257e0055a7aa4c3eb000a303870d7` 未变、05复审1093项及报告 `6cd4621901dddcc9ad7d11ddca4248eaac2a1ae7e45513ca257a35055f1b6973` 未变。参考原片前后同hash。已有coder预冻结/工具自检子目录保留原身份，不算tester独立正例；本次独立运行位于independent-001及独立边界/审计文件。

本报告与完整证据清单在发送前冻结；发送状态另存回执，不回写已发送报告。负责人应集中回交MC-B01修复，并保留真实容器目标OPEN；测试端等待正式新冻结交测，不逐问题联调、不自动续测。
