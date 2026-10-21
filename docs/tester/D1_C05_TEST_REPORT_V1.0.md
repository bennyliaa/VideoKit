# D1 C05 集中回归测试报告 V1.0

日期：2026-10-05。候选 D1-20261005-C05；需求 D1_C05_TESTER_REQUIREMENTS_V1.0.md 顶部13:01正式交接。自动批次电脑时间13:11:16～13:14:21。

结论：批次已结束，25入口全部执行，23 PASS、2 FAIL、0 BLOCKED/NOT_RUN（方法级）。正常宿主/companion编码前置通过，依赖注入与实际sample恢复均重新运行。普通broker SIGSEGV与独立HANG通过；ordinary探针App内死亡原因分类仍FAIL，AVI10秒取帧回退转换仍FAIL。D1未通过、C05仍NOT_READY，不进入M0。实际source frame PTS、检测质量和手机缺陷不随本批关闭。

## 设备与冻结安装门禁

仅平板HA1Q6WXR / TB138FC、Android12 API31、arm64-v8a。首轮未连接，用户回复“平板已连接”后重新核验。没有操作手机/模拟器、运行Gradle、改产品或冻结件。沿用原平板1536×2560/density320规格；包UID app10221/test10222/worker10220，C04用途明确。

冻结核验5个产物、96个证据文件、106个源码/ZIP条目全部匹配；冻结时间2026-10-05T12:58:18.815344+08:00；source ZIP SHA256 0a7d7544e830ac8be399d6816e9e0431fbb412f420150ef570f7be86781d1d75；freeze-summary SHA256 811ca000436ac10fa16d0d88fb0996122e68a8fe984756a9bdd8336c7ff89d29。

三份debug包独立签名检查同证书SHA256 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；实际已安装C04三包先逐包拉回核验SHA与C04冻结记录一致，保存包路径/dumpsys与APK；cache原字节备份含旧账本/lease/owner/成功输出。随后授权install-r三包全部Success，没有卸载/清数据或覆盖未知数据；unsigned release不安装，companion仅D1实验。

| APK | 字节 | SHA256 |
| --- | ---: | --- |
| app-debug-androidTest.apk | 2308821 | abc7c2cd56ecab256567dfbe6c22f45b9780f5466d9c90c146c2627ae04b790d |
| app-debug.apk | 40623273 | 4639989459c9c9ec5491e71ebe0d52ae35f705c3dbe6f24b5262a1cab9258fd9 |
| worker-debug.apk | 17100536 | 591f8de03b48121e68d4a13d2d3b3a152b4b6a3044fc78e81c915cc86d0ea5b6 |

[冻结核验](D1_C05_EVIDENCE/freeze-check.json)、[旧包身份/恢复路径](D1_C05_EVIDENCE/c04-update-preflight.json)、[安装](D1_C05_EVIDENCE/update.log)。备份c04-installed-*.apk与c04-cache-before-update.tar保留；当前cache备份cache-after-batch.tar及[备份清单](D1_C05_EVIDENCE/backup-manifest.json)可用于后续审查，不自动降级/恢复。

## 素材与边界

按冻结DeviceFixtures路径契约，重新验证C04四份可信私有副本SHA，在全新files/d1_c05_fixtures生成副本并验证长度/SHA。basic.mp4 349102字节、subtitle.avi 736454656、subtitle.srt 93550、large.mkv 3212959911，共3949857219字节；C04目录和电脑源均不修改、不上传。复制前空间记录见space-before.txt，充分满足副本需求。

[副本完整hash](D1_C05_EVIDENCE/fixture-hash-check.json)。结束再验证C05 basic、C05 AVI及旧C04 AVI，hash仍与可信源一致，见[source-after-hashes](D1_C05_EVIDENCE/source-after-hashes.txt)。此路径是App私有cp复用，不能作为Windows传输工具设备通过。

## 25入口结果

| 方法 | 结果 | 覆盖及限制 | 证据 |
| --- | --- | --- | --- |
| realEncoderOutput | PASS | 宿主 H264/AAC、256×144、3秒、非零双轨/严格PTS/视频decode/READY 门禁通过。 | [日志](D1_C05_EVIDENCE/realEncoderOutput.log) |
| isolatedActualEncodeAndReadyRecovery | PASS | companion异UID/PID、broker字节、有效真实视频sample、decode验证、死亡/源排空、READY同task恢复。 | [日志](D1_C05_EVIDENCE/isolatedActualEncodeAndReadyRecovery.log) |
| outputValidationCounterexamples | PASS | 12个规则反例与拒绝未缩放剪辑原片；不是 decoder fuzz。 | [日志](D1_C05_EVIDENCE/outputValidationCounterexamples.log) |
| exportReadyResponseLoss | PASS | 编码完成；响应丢失后同task查询 READY/token，重开一致。 | [日志](D1_C05_EVIDENCE/exportReadyResponseLoss.log) |
| exportWriteFault | PASS | stage=write、hits=1、code7001、正确注入cause、abort 无 READY。 | [日志](D1_C05_EVIDENCE/exportWriteFault.log) |
| exportFlushFault | PASS | stage=flush、hits=1、code7001；已有字节、正确注入cause、abort 无 READY。 | [日志](D1_C05_EVIDENCE/exportFlushFault.log) |
| exportValidationFault | PASS | 编码/fsync/字节完成后 stage=validate、hits=1、OUTPUT_VALIDATION_FAILED。 | [日志](D1_C05_EVIDENCE/exportValidationFault.log) |
| realPipelineImmediateCancel | PASS | 实际 Transformer 立即取消及输入排空；不是sample后取消。 | [日志](D1_C05_EVIDENCE/realPipelineImmediateCancel.log) |
| writingJournalRecovery | PASS | WRITING账本恢复/abort；不是宿主实际死亡。 | [日志](D1_C05_EVIDENCE/writingJournalRecovery.log) |
| isolatedWorkerDeathAndTimeout | PASS | 本轮只含NORMAL/PRESSURE/EXIT，进入/ACK、故障、死亡和源排空均通过；EXIT OS历史记录不可用，仅相应诊断未知。 | [日志](D1_C05_EVIDENCE/isolatedWorkerDeathAndTimeout.log) |
| isolatedBrokerSigsegvIndependently | PASS | 独立NORMAL后SIGSEGV；ARMED、hits=1、Binder death、PID/UID/时间匹配signal11、源账本零计数。 | [日志](D1_C05_EVIDENCE/isolatedBrokerSigsegvIndependently.log) |
| isolatedBrokerHangIndependently | PASS | 独立NORMAL后HANG；WAIT_BEGIN、hits=1、精确WORKER_TIMEOUT、有界等待、死亡和源排空。 | [日志](D1_C05_EVIDENCE/isolatedBrokerHangIndependently.log) |
| ordinaryIsolatedCodecOutcomeDoesNotReady | FAIL | App内cause UNKNOWN而FAIL；外部对应PID/UID原始tombstone可解释native SIGABRT；最终death/source_released/lease_clear均true。 | [日志](D1_C05_EVIDENCE/ordinaryIsolatedCodecOutcomeDoesNotReady.log) |
| nativeLeaseSurvivesDuplicateDescriptorClose | PASS | 锁竞争、重复FD关闭及abort原生语义。 | [日志](D1_C05_EVIDENCE/nativeLeaseSurvivesDuplicateDescriptorClose.log) |
| cancelAfterActualVideoSample | PASS | 实际H264 sample后取消、死亡、租约/source释放、partial删除且无READY。 | [日志](D1_C05_EVIDENCE/cancelAfterActualVideoSample.log) |
| workerExitDuringActualEncoding | PASS | 实际H264 sample后自身EXIT、死亡与abort/source门禁。 | [日志](D1_C05_EVIDENCE/workerExitDuringActualEncoding.log) |
| workerSigsegvDuringActualEncoding | PASS | companion实际H264 sample后自身SIGSEGV、死亡与abort/source门禁。 | [日志](D1_C05_EVIDENCE/workerSigsegvDuringActualEncoding.log) |
| secondCodecTaskSurvivesFirstNativeCrash | PASS | 两任务真实sample，不同PID同UID；首任务崩溃后第二任务存活、完成验证/READY。 | [日志](D1_C05_EVIDENCE/secondCodecTaskSurvivesFirstNativeCrash.log) |
| actualHostDeathDuringEncodingAndCrossOwnerAbort | PASS | sample后helper宿主自杀；新owner租约恢复并同task abort，无READY。 | [日志](D1_C05_EVIDENCE/actualHostDeathDuringEncodingAndCrossOwnerAbort.log) |
| actualHostDeathAfterReadyAndSameTaskQuery | PASS | durable READY后helper死亡；新owner原task/token一致且abort保留成功输出。 | [日志](D1_C05_EVIDENCE/actualHostDeathAfterReadyAndSameTaskQuery.log) |
| playbackMp4 | PASS | 结构/5次Seek/短播放/源排空通过；静音自动用例。 | [日志](D1_C05_EVIDENCE/playbackMp4.log) |
| playbackAviWithoutSrt | PASS | 无SRT对照结构/Seek/短播放/释放通过。 | [日志](D1_C05_EVIDENCE/playbackAviWithoutSrt.log) |
| playbackAviSrt | PASS | 有SRT轨选择/开关/Seek/播放/释放通过；字形效果另核查。 | [日志](D1_C05_EVIDENCE/playbackAviSrt.log) |
| playbackMkvAss | PASS | ASS轨选择/开关/Seek/播放/释放通过；自动静音不判声音。 | [日志](D1_C05_EVIDENCE/playbackMkvAss.log) |
| offlinePlatformFaceFeasibility | FAIL | MP4控制非空；AVI10秒直接空，9～12秒转换因10秒无sample watchdog失败；未到转换MP4的1秒取帧或检测。 | [日志](D1_C05_EVIDENCE/offlinePlatformFaceFeasibility.log) |

[完整结果/命令/依赖/时间](D1_C05_EVIDENCE/tablet-batch-results.json)、[控制台](D1_C05_EVIDENCE/tablet-batch-console.log)。逐方法单独instrumentation，外部上限180～360秒，本轮无外部超时。日志按当前方法设备开始时间、App/companion UID采集；相关isolated PID从当前协议日志确定，再保存对应crash记录。完整tombstone仅保留匹配本次PID及com.videokit进程块，排除无关及旧崩溃。电脑/设备时钟有偏差，不用跨时钟差评价性能。

## 三项修复复验与实际释放

### 普通broker SIGSEGV与HANG

SIGSEGV独立方法先NORMAL，再mode2，ARMED同步ACK及hits=1断言；PID5388/isolated UID99009，OS退出matched=true、reason5、signal11，phase=SIGSEGV_ARMED，death=true、source_released=true、operations/consumers/failed_closes全0。对应原始tombstone保留。没有以cleanup SIGKILL或单纯ENTERED当指定故障成功。

HANG独立方法先NORMAL，再mode4，PID5507/UID99011、HANG_WAIT_BEGIN、精确WORKER_TIMEOUT、等待预算断言通过，最终死亡/源排空和零计数。OS记录reason13/signal0，仅记录实际退出，不称HANG是SIGSEGV。即使SIGSEGV失败也不会遮蔽HANG；本轮两项均PASS。

旧整组方法本轮只有NORMAL/PRESSURE/EXIT并PASS。EXIT_ARMED后actual死亡/source排空通过，最终PID5215/UID99007；其OS历史查询记录不可用（EXIT_RECORD_UNAVAILABLE），因此不声称有EXIT OS reason证明。普通broker实验没有真实媒体输出Writer FD，其源账本与companion输出lease门禁分开。

[SIGSEGV协议](D1_C05_EVIDENCE/isolatedBrokerSigsegvIndependently-uid10221.log)、[SIGSEGV崩溃](D1_C05_EVIDENCE/isolatedBrokerSigsegvIndependently-tombstone-pid5388.log)、[HANG协议](D1_C05_EVIDENCE/isolatedBrokerHangIndependently-uid10221.log)。TABLET-C04-01在本候选/本平板限定复验通过，不外推手机或所有native路径。

### ordinary codec死亡与原因

task029c994a-3360-417e-991f-475f61e31cc1，PID5588/isolated UID99012；同步阶段PROBE_LEASE_ACQUIRED、PROBE_CODEC_CREATE_BEGIN，随后WORKER_DIED。App ExitEvidence匹配reason5/signal6，但cause=UNKNOWN、trace_sha空，native_abort_with_cause=false，permission_denial_proven=false，自动方法在“需Java cause或匹配native SIGABRT原因”断言失败，保持FAIL，不人工改判PASS。

tester额外保存的本次同PID/UID原始tombstone给出SIGABRT，具体Abort message：`Check failed: serviceManager Hardware service manager is not running.` 栈含libcodec2_client.so的Codec2Client::GetServiceNames/ListComponents以及Codec2InfoBuilder。由该证据可记录“codec创建阶段枚举codec2服务时native abort事实”；不能据此宣布全局服务确实停机、权限拒绝根因或产品隔离验收。

finally日志death=true、source_released=true、lease_clear=true；冻结断言同时检查无token。此条分类FAIL的最终释放已得到实际证据，不将其笼统标成未排空；没有运行重试或扩大当前allowlist来掩盖失败。App内历史trace缺失的原因仍待查。

[当前协议/最终状态](D1_C05_EVIDENCE/ordinaryIsolatedCodecOutcomeDoesNotReady-uid10221.log)、[对应原始tombstone](D1_C05_EVIDENCE/ordinaryIsolatedCodecOutcomeDoesNotReady-tombstone-pid5588.log)。TABLET-C05-01：高，诊断分类未闭合；建议后续整包修复原生死因证据获取和具体分类，不把SIGABRT直接当权限证据。

### AVI原10秒请求与映射回退

MP4 2秒scaled非空，metadata320×180/8021ms，generation1 released=true。AVI原10秒scaled与同10秒unscaled均null，width/height null、duration5431488；稳定FRAME_AT_REQUESTED_TIME_UNAVAILABLE触发回退，generation2 released=true。

实际回退记录source_requested_us=10000000、clip_start_ms=9000、clip_end_ms=12000、requested_clip_us=1000000、actual_source_frame_pts=UNKNOWN。转换约10秒后ExportException Muxer error，其内层IllegalStateException为`Abort: no output sample written in the last 10000 milliseconds`。没有到完整片段T01验证/READY，也没有到转换MP4的1秒OPTION_CLOSEST或人脸检测，故方法FAIL；不是MP4控制非空即通过。

日志有Extractor/read/offset及取消后的SOURCE_READ_FAILED CANCELLED；该取消日志不单独当转码根因。回退finally source_released=true、transformer_cancel_returned=true。cache保留d1_c05_frame_35a9f416-15d7-468e-a724-6bc4e7064d5e.mp4.task（46字节），目录未见同名MP4；没有宣称得到有效帧/成功输出，未清理恢复材料。缓存预算尚只占一项，不重跑增加文件。

[取帧/转换完整cause](D1_C05_EVIDENCE/offlinePlatformFaceFeasibility.log)、[分阶段/释放](D1_C05_EVIDENCE/offlinePlatformFaceFeasibility-uid10221.log)。TABLET-C05-02：高，回退转换不可用；下一批需查AVI加载/剪辑/解码/输出无sample的具体阶段，保持原10秒语义、完整验证和资源门禁。精确source frame PTS和检测质量仍NOT_RUN。

## 既有门禁、效果及结束保留

T01正常H264/AAC256×144、3秒±150ms、独立双轨有效样本/严格PTS/完整视频decode，以及12规则反例重新通过；规则反例不是恶意容器decoder fuzz。T02 write/flush准确阶段、hits=1和指定cause、flush非零字节，validate编码/fsync后非零字节和OUTPUT_VALIDATION_FAILED，均重新通过。READY响应丢失、同task/token恢复与abort保留成功输出通过。

companion真实编码、实际sample后cancel/EXIT/SIGSEGV、不同PID同UID第二槽存活、实际helper宿主死亡和跨ownerabort/READY、dup-close原生锁语义全部重新通过。仅是这些冻结方法覆盖，不代表单App产品分发、全P0隔离、native OOM或性能矩阵通过。

MP4/AVI无SRT/AVI SRT/MKV ASS的自动播放、5次Seek、字幕轨开关与实际源排空通过；自动静音，不判声音或完整字形/同步。C05人工声音/ASS全样式/对白同步/旋转/前后台/RTL均NOT_RUN，未将旧C04用户有声反馈迁移为C05结果。手机AVI挂起/无声及Windows传输仍待单独修复候选同机补测；本轮不操作手机。

批次完成后已停止本次App及companion，没有清数据/卸载/更换候选。C04/C05私有fixture、所有账本/lease/owner、成功输出和当前失败frame账本保留，cache完整备份可审查。停止App不能替代未知资源释放；本轮上述两FAIL最终实际释放已有日志，其他PASS仅按其断言范围。

剩余模型权利、标注质量、NAS不协作、权限/满盘、native OOM/12路并发、完整产品隔离与供应链风险沿用未决清单。集中交付两项失败，不据23个限定PASS进入M0；下一候选及手机补测由负责人另行整体交接。
