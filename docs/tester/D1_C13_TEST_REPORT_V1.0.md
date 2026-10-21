# D1 C13 集中测试报告 V1.0

报告时间：2026-10-16T12:14:28+08:00。候选D1-20261016-C13，git_commit=null。依据C13正式测试需求、交付、DEVICE_APPENDIX、PIPELINE_BOUNDARY、REMAINING_GATE、LICENSE、TRACKING及冻结device_plan；对照原始需求§29、系统/API/编辑/许可/测试设计、项目已决事项与D1架构门禁评审。

## 结论

**本批结束，D1未通过，不进入M0。** 手机69项环境阻断。平板69项计划，实际运行55项：52 PASS、3 FAIL；其余14项管线前置BLOCKED。两六帧管线正例均在公开AVC编码器configure阶段失败，尚未进入源帧生产、编码样本及隔离EOF验证；不能将局部CPU正常帧或本机814项断言当作接续成功。另有一项CPU SIGSEGV因App原始signal0严格FAIL，raw11独立保留。

| 设备 | CPU37 | host7 | legacy8 | pipeline17 | 总计 |
| --- | --- | --- | --- | --- | --- |
| OPPO PDYM20 / U4999DLBNRR89DOR | 37环境阻断 | 7环境阻断 | 8环境阻断 | 17环境阻断 | 69 ENVIRONMENT_BLOCKED，0次C13方法 |
| Lenovo TB138FC / HA1Q6WXR | 36 PASS / 1 FAIL | 7 PASS | 8 PASS | 1 PASS / 2 FAIL / 14 BLOCKED | 52 PASS / 3 FAIL / 14 BLOCKED |

当前无在途设备方法、无VideoKit残留进程/服务。此结束事实与方法期限内资源门禁分栏，未用末尾ps空补PASS。手机仍enabled=2、lastDisabledCaller=com.oplus.athena；没有重复寻找“启用”按钮、强启、卸载清数据、变包或安装C13绕过。两设备实际API31、ARM64、4096字节页。

## 冻结、实际安装与供应链

冻结时间2026-10-16T12:01:18.499595+08:00；独立归档核验325源文件、130证据、5产物PASS，逐entry/hash核对并独占复制。另独立verify_c13 --working-tree PASS，核对冻结对应当前源文件。详见 [freeze-check](D1_C13_EVIDENCE/freeze-check.json)、[working-tree-check](D1_C13_EVIDENCE/working-tree-check.json)、[admission-check](D1_C13_EVIDENCE/admission-check.json)。

| 对象 | SHA256 |
| --- | --- |
| freeze-summary | 44bdfafefd0a56f2d529928d88ee9499bbd6dc48749e33091efe9a6f50a6c67a |
| source ZIP | 0d2288890549a34e01e80a4e31b4b8e0f1a672f5994c27f8b5ac8282e26e0f7a |
| app-debug-androidTest.apk | 3ef601b1d94041af82f122eb904ff129f3b8e05ba5d7220e3097f99805782cad |
| app-debug.apk | 8988bfc40cbed3f907a33bccef1c0eaa453daf37ea01d3868ee421d6a9bd6b51 |
| app-release-unsigned.apk | 71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e |
| worker-debug.apk | 3dde3ed9ab312a791886c889b50abbc13c08ced1eaf313323e5f3a13e784c217 |

三Debug包实际签名核验PASS，证书SHA256 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。更新前保存旧包身份/APK与可读cache；平板main/test保留数据同签名更新后回读实际APK，hash等于冻结，CPU不用companion。host结束后才另备份并更新legacy worker，最终实际worker APK hash再次核对。手机有限预检/备份后阻断，未更新。Release只对照未安装。

独立检查16个native条目实际hash、ZIP_STORED/16KiB偏移及ELF LOAD；五个FFmpeg/allocator库与既有基线相同。C13 CPU JNI新增mode10/11实际变化，不能说仅包名变化；normal CPU已运行，新管线mode10/11因编码配置前置未进入。静态16KiB不证明16KiB页设备运行。未运行Gradle、改产品/冻结件、重建上游或删旧证据。782 JVM＋32脚本＝814本机断言只作交付证据，不计设备PASS。

## 执行控制与逐项结果

明确serial手机→平板，逐方法独占attempt。先正常MP4/AVI及C12完整52项，再pipeline两正例。三次FAIL均停止外层调度，核完整instrumentation终态、真实资源账本与当前进程/服务，保存review.json后才继续独立项；未重跑失败方法、未修包补跑或求理想signal/trace。MP4/AVI管线正例独立各执行一次；两者失败后14反例BLOCKED，无attempt，只有不依赖编码的OwnerRecovery继续一次并PASS。真实断言失败未改成环境/能力阻断，能力缺失亦未当PASS。

手机EB=ENVIRONMENT_BLOCKED，统一证据phone/environment.json、preflight.json及package-at-end.txt。平板实际原始证据在 `D1_C13_EVIDENCE/tablet/attempts/方法名/`，含command/result/post，FAIL另有review。总表results.json；[runtime-review](D1_C13_EVIDENCE/runtime-review.json)独立审身份/媒体端点/slot， [pipeline-review](D1_C13_EVIDENCE/pipeline-review.json)保留真实进入阶段及未完成映射， [execution-audit](D1_C13_EVIDENCE/execution-audit.json)核对55次终态。没有以pipeline-positive缺少六帧的审查失败反向覆盖原始FAIL。

| 序号 | 组 | 方法 | 手机 | 平板 |
| --- | --- | --- | --- | --- |
| 01 | cpu | cpuEnvironmentPreflight | EB | PASS |
| 02 | cpu | cpuMp4H264ActualPtsFrame | EB | PASS |
| 03 | cpu | cpuAviMpeg4ActualPtsFrame | EB | PASS |
| 04 | cpu | cpuCleanupWithoutBindProvesNoWorker | EB | PASS |
| 05 | cpu | cpuFirstFailureSurvivesCleanupFailure | EB | PASS |
| 06 | cpu | cpuActualAggregateAllocationQuotaAndDecode | EB | PASS |
| 07 | cpu | cpuSeekUsesNewEpochAndDecodedTimestamp | EB | PASS |
| 08 | cpu | cpuOversizedDeclarationRejectedBeforeDecoderOpen | EB | PASS |
| 09 | cpu | cpuTruncatedInputRejectsAndReleases | EB | PASS |
| 10 | cpu | cpuValidAviHeaderBadPacketRejects | EB | PASS |
| 11 | cpu | cpuWrongDeclaredFormatRejects | EB | PASS |
| 12 | cpu | cpuCompiledH263DoesNotExpandAcceptedInputCodec | EB | PASS |
| 13 | cpu | cpuForgedFrameRejectedBeforeHostAllocation | EB | PASS |
| 14 | cpu | cpuForgedEpochAndClaimedIdentityRejected | EB | PASS |
| 15 | cpu | cpuUnknownAndEmptyLengthRejectWithActualClose | EB | PASS |
| 16 | cpu | cpuCancelActiveReadRetainsPendingSourceLedger | EB | PASS |
| 17 | cpu | cpuCancelAfterActualFrame | EB | PASS |
| 18 | cpu | cpuHungTaskBoundedStopAndDeath | EB | PASS |
| 19 | cpu | cpuStopAckLossStillRequiresActualDeath | EB | PASS |
| 20 | cpu | cpuStalledStopDoesNotConsumeSecondRpcSlot | EB | PASS |
| 21 | cpu | cpuCancelFromMainThreadDoesNotBlockSecondTask | EB | PASS |
| 22 | cpu | cpuWrongStopEpochRejectedAndTaskContinues | EB | PASS |
| 23 | cpu | cpuOnewayStopRejectedAndTaskContinues | EB | PASS |
| 24 | cpu | cpuRegistrarSynchronousMetadataAndRejects | EB | PASS |
| 25 | cpu | cpuRegistrarLocalHostIdentityRejected | EB | PASS |
| 26 | cpu | cpuRegistrationBadMagicPreservesFirstCause | EB | PASS |
| 27 | cpu | cpuRegistrationTrailingReplyPreservesFirstCause | EB | PASS |
| 28 | cpu | cpuCancelBeforeRegistrationClosesBindingAndRetainsUnknown | EB | PASS |
| 29 | cpu | cpuCancelBeforeBindReturnRevokesLateAcceptance | EB | PASS |
| 30 | cpu | cpuUnbindFailureRequiresExplicitRecovery | EB | PASS |
| 31 | cpu | cpuDuplicateConnectionKeepsOriginalIdentity | EB | PASS |
| 32 | cpu | cpuCancelDuringHelloCannotStartOrRevive | EB | PASS |
| 33 | cpu | cpuRejectedExtraWorkerRetainsSlotAndSecondTask | EB | PASS |
| 34 | cpu | cpuLateWorkerCannotBorrowOriginalDeath | EB | PASS |
| 35 | cpu | cpuExitCollectionRejectsMainThread | EB | PASS |
| 36 | cpu | cpuSelfSigsegvSignalMustBeProven | EB | FAIL |
| 37 | cpu | cpuSecondSlotAndHostSurviveFirstSelfCrash | EB | PASS |
| 38 | host | realEncoderOutput | EB | PASS |
| 39 | host | outputValidationCounterexamples | EB | PASS |
| 40 | host | exportReadyResponseLoss | EB | PASS |
| 41 | host | exportWriteFault | EB | PASS |
| 42 | host | exportFlushFault | EB | PASS |
| 43 | host | exportValidationFault | EB | PASS |
| 44 | host | writingJournalRecovery | EB | PASS |
| 45 | legacy | nativeLeaseSurvivesDuplicateDescriptorClose | EB | PASS |
| 46 | legacy | isolatedActualEncodeAndReadyRecovery | EB | PASS |
| 47 | legacy | cancelAfterActualVideoSample | EB | PASS |
| 48 | legacy | workerExitDuringActualEncoding | EB | PASS |
| 49 | legacy | workerSigsegvDuringActualEncoding | EB | PASS |
| 50 | legacy | secondCodecTaskSurvivesFirstNativeCrash | EB | PASS |
| 51 | legacy | actualHostDeathDuringEncodingAndCrossOwnerAbort | EB | PASS |
| 52 | legacy | actualHostDeathAfterReadyAndSameTaskQuery | EB | PASS |
| 53 | pipeline | pipelineMp4RealFramesVideoOnly | EB | FAIL |
| 54 | pipeline | pipelineAviRealFramesVideoOnly | EB | FAIL |
| 55 | pipeline | pipelineRejectsCrossEpochBeforeCopy | EB | BLOCKED |
| 56 | pipeline | pipelineRejectsLateFrame | EB | BLOCKED |
| 57 | pipeline | pipelineQueueSaturationAborts | EB | BLOCKED |
| 58 | pipeline | pipelineConsumerLostAborts | EB | BLOCKED |
| 59 | pipeline | pipelineEncoderInputRejectedNoReady | EB | BLOCKED |
| 60 | pipeline | pipelineEncoderErrorNoReady | EB | BLOCKED |
| 61 | pipeline | pipelineSinkWriteFailureAborts | EB | BLOCKED |
| 62 | pipeline | pipelineSinkFlushFailureAborts | EB | BLOCKED |
| 63 | pipeline | pipelineCorruptOutputRejectedByIsolatedDecoder | EB | BLOCKED |
| 64 | pipeline | pipelineReadyResponseLossSameToken | EB | BLOCKED |
| 65 | pipeline | pipelineDecodeFailureAborts | EB | BLOCKED |
| 66 | pipeline | pipelineCancelInFlightRetainsFrameLease | EB | BLOCKED |
| 67 | pipeline | pipelineIndependentCpuSurvivesFailure | EB | BLOCKED |
| 68 | pipeline | pipelineRejectsSecondEncoderBeforeCreation | EB | BLOCKED |
| 69 | pipeline | pipelineOwnerRecoveryFencesIncompleteWriting | EB | PASS |

## C13-T01：两正常管线编码配置失败（阻断）

| 正例 | exportId | 进入阶段 | 最终 |
| --- | --- | --- | --- |
| MP4 | 7ad3cdf9-d8d2-4cac-83b4-c0caf03f78e8 | OMX.qcom.video.encoder.avc，MediaCodec.configure抛CodecException | FAIL，期望READY实际ABORTED |
| AVI | d2381e90-8cad-4bd7-a148-7d639024763d | 同一公开AVC配置路径，尚未启动producer | FAIL，期望READY实际ABORTED |

两次PIPE_FAILURE首因链均定位PipelineEncoder.open / MediaCodec.native_configure；本地stage错误为PIPE_ENCODER_OR_VALIDATION_FAILED。原始系统日志有configureCodec error -38、OMX 0x80001001、internalError -2147483648。不能从这些值唯一推断颜色格式、profile/level、权限或设备永久不可编码；host正式双轨通过也不证明本管线ByteBuffer配置兼容。当前错误枚举合并encoder/validation且丢失更精确Codec诊断，是研发排查时应补足的证据，未擅自改成“设备能力不支持即跳过”。

实际PIPE_LEDGER均received=0、encoder_inputs=0、encoded_samples=0、verified=0、queue_peak=0、frame_consumers=0。无PIPE_SOURCE_FRAME/ENCODE_INPUT/SAMPLE、无隔离OUTPUT_FRAME/FULL_EOF、无CONTENT/VISUAL_CHECK或READY成功事实。失败发生在encoder.open()后producer提交之前；没有宿主重新读压缩源、换合成帧或取消验证后放行。**新六帧/PTS/内容/压缩误差接续可行性本轮未证。**

两次最终source/codec/writer/frames/resources_released全true、encoder_output_slots0；post/evidence及失败后ps/services重检无残留。有界codec关闭和未创建producer的资源事实通过，不等于管线业务通过。三个实际pipeline journal（两正例失败＋独立owner恢复）从最终缓存二进制独立解析均ABORTED，READY记录0、残留pipeline MP4为0，见tablet/pipeline-journal-audit.json。

证据：两个pipeline正例attempt内post/host.log、post/evidence.json、原始4-command.log与review.json。保留完整错误日志，未仅凭零帧猜解码/JNI根因。

## C13-T02：self SIGSEGV的App系统signal仍为0（严格FAIL）

本次task=768dd2669dda44448e38a8a658e391cf / epoch7115274094004168125 / generation1 / PID12673 / UID99039，真实帧、ARMED后在cleanup STOP前实际death；外部匹配raw signal11。App历史退出matched=true、reason5、signal0，3次APP_TRACE_ABSENT，trace_signal=-1、trace_sha空、cause UNKNOWN，verdict UNKNOWN_FAIL。保留原始AssertionError，不用注入意图/raw/清理SIG9回填11，不复测求非零status。

该任务首次身份未变，stop_attempts0、actual_death=true、source CLOSED、pending_calls0、stop_pendingfalse、binding_closedtrue、unresolved/global_unproven/slots0、slot_releasedtrue，全部原代次资源有独立终态。资源通过与退出信号失败分开，未重现C10身份混用。

另一个独立双槽方法原系统signal11、reason5且raw11匹配，trace仍APP_TRACE_ABSENT，第二任务与宿主存活断言通过，因此该方法PASS。两方法各一次、不同任务PID；不同结果不能互相覆盖，也不能把C12两项OS11历史结果写为本批self成功。采集器3次读取日志加调用方返回日志不是4次打开流，status0门槛未变。

- cpuSelfSigsegvSignalMustBeProven：App PID12673/UID99039、signal0、APP_TRACE_ABSENT；独立raw=[{"pid": 12673, "uid": 99039, "signal11": true}]。原始证据对应post/host.log和tombstone-pid*.log。
- cpuSecondSlotAndHostSurviveFirstSelfCrash：App PID12815/UID99040、signal11、APP_TRACE_ABSENT；独立raw=[{"pid": 12815, "uid": 99040, "signal11": true}]。原始证据对应post/host.log和tombstone-pid*.log。

## 其他缺陷、覆盖与已证边界

| 编号 | 状态 | 说明 |
| --- | --- | --- |
| C13-ENV01 手机禁用 | ENVIRONMENT_BLOCKED | 69项未调度；不能用平板覆盖手机或绕过用户已确认页面现状 |
| C13-COV01 14项pipeline反例 | BLOCKED | 两正常正例未成立；伪代/迟到帧、队列/失联、encoder拒绝/错误、Sink故障/截断验证、READY丢响应、取消租约、另一任务/第二encoder等均未进行设备验证 |
| C13-LIM01 裸数组/质量/EOF证据 | OPEN | 最终8份1179648B与YUV55296B为事前静态保守限界；实际只到configure，未测到帧数组/队列运行峰值，6帧、luma≤24、源差异≥4/输出≥2、≤1ms映射均未达到 |
| App trace缺失/ordinary UNKNOWN | OPEN/保留历史 | 本轮两个SIGSEGV trace为空；未重跑历史ordinary或降低标准 |

原52项中正常CPU MP4真实RGBA147456B，raw24576、time_base1/12288、pts2000000、best_effort0；AVI为best_effort1的真实PTS（见本轮帧日志），不标成原始PTS。累计配额、输入白名单/坏源/协议、Source取消、STOP/ACK丢失/挂起、同步flags拒绝、两槽、未知绑定/迟到返回、显式解绑恢复和逐代身份均在已通过方法范围有证据。逐事件独立审查未发现身份改写、非主端点媒体、已知代次未死时释放槽；不外推全部系统竞态、OOM或高分辨率长时性能。

host7全部PASS，保留真实H264/AAC双轨/PTS/full decode与READY/abort/reconcile及故障恢复；legacy8全部PASS，仅历史companion实验回归，不替代单APK新管线。pipeline唯一PASS为OwnerRecovery：live owner受锁保护，实际句柄/owner关闭后新owner获得WRITING并幂等ABORT；不是新管线宿主进程SIGKILL实测，也不证明编码或隔离验证成功。

- legacy raw：workerSigsegvDuringActualEncoding PID14233/UID10220，signal11。该指定方法未额外断言App死因分类，不补CPU trace或新管线能力。
- legacy raw：secondCodecTaskSurvivesFirstNativeCrash PID14403/UID10220，signal11。该指定方法未额外断言App死因分类，不补CPU trace或新管线能力。

## 数据保留与预算

| 设备 | 整批新输出字节 | task/journal | 日志/文本字节 | 旧capture |
| --- | ---: | ---: | ---: | --- |
| 手机 | 0 / 8388608 | 0 / 32 | 31700 / 33554432 | 0文件哈希未变 |
| 平板 | 2735580 / 8388608 | 18 / 32 | 1912319 / 33554432 | 8文件哈希未变 |

pipeline专用目录实占363 / 4194304字节、3 / 24个journal，输出MP4为0；单输出2097152B上限及创建前完整2MiB预留、整批8MiB和日志32MiB均在执行/写入前后限界，未事后删旧证据腾额度。新管线失败后删除自己的未READY临时输出是既有abort语义，不是删除历史数据。

cache-before/after-c13.tar、output-budget-final.json、pipeline-budget-final.json、log-budget-final.json和journal-audit留存。平板旧C06/C07 capture8文件哈希不变，手机0文件；未新建capture。新fixtures仅basic.mp4/subtitle.avi，共736803758B，前后完整hash一致：720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9、3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f。源只读、旧fixture/原素材保留，空间符合事前检查；fixture不计输出预算。未上传媒体。

## 原文§29、框架与权利门禁审阅

保留十二项追踪，无一因本机断言或本批局部PASS升级为完整产品验收：

| 项 | 本轮审阅结论/剩余 |
| --- | --- |
| 1 group/artifact/namespace/version | 内部Maven group com.videokit、SDK namespace com.videokit.<module>、App com.videokit.app已有PROJECT_DECISIONS决定；C13矩阵“未定”文字不撤销既有决定。正式artifact/version兼容与交付仍待验证 |
| 2 播放/编辑拆分 | Debug不是独立SDK；core/playback/edit/export及可移除AAR依赖边界OPEN |
| 3 框架/许可 | Media3 1.9.3、FFmpeg8.0.3受限Debug准入沿用；JNI/系统编码、图片及完整危险链与发行OPEN |
| 4 跟踪/模型/最低设备 | YuNet/ViTTrack仅固定文字/LFS身份调查，未集成实权重；权利、真实标签、质量和最低设备OPEN |
| 5 输出预设 | host双轨本轮通过；新六帧无音频AVC/fMP4前置FAIL，不可替代正式预设 |
| 6 remux条件 | 六快照重编码不证明remux；edit-list/旋转/音轨/兼容fallback仍OPEN |
| 7 质量/性能/热 | 本轮无六帧质量/运行峰值；长期内存/速度/热/最低设备分级OPEN |
| 8 UI/engine组合 | 没有Surface或AudioTrack实际显示/听音；View/Compose/Flutter生命周期矩阵OPEN |
| 9 Sink能力 | 指定旧双轨与owner恢复通过；新验证链未运行，宿主FD/随机写能力及跨宿主协议OPEN |
| 10 schema/恢复 | 指定journal/epoch恢复通过；新管线实际宿主死亡、正式schema/迁移/工程恢复OPEN |
| 11 控件/主题/overlay | 产品UI、无障碍/坐标/遮罩API未由本批验证 |
| 12 共享池算法 | 既有进程内CPU2、单encoder/output设计；新在途帧许可竞态因前置BLOCKED，跨宿主全局池与公平/热预算OPEN |

审阅跟踪证据：本批可核验真实标签0帧，annotation-template不是标注；满足十类clip且权利闭合为0套。现有45媒体可作已授权技术测试，不等于人物/训练/离线再分发许可。未下载权重/模型或伪造标注；目录MIT/Apache文字或FaceDetector候选数不代替权重权利和自动跟踪P0。下一有限实验仍须先有权利/实际PTS人工标注与独立复核，不以模板PASS。

正式Flutter＋独立Kit/AAR/C ABI及全部P0保持。本轮Media3封装与公开AVC、受限FFmpeg复用不等于完整权限/故障隔离：宿主仍有MediaCodecList/configure/MediaCodec和AndroidLease JNI，旧双轨验证/字幕/图片/跟踪/显示/PCM危险链仍OPEN；新管线源/输出隔离设计尚未由本轮六帧实测成立。未将同UID分进程、系统服务或ByteBuffer收到数据标为完整安全/真实显示/声音。

五个FFmpeg/allocator库不变、266对象/608依赖/完整对应源/NOTICE/SBOM及既有安全维护证据继承；C13新增JNI验证胶水须继续审计，未声称重跑GPG/上游构建/全面漏洞扫描。仅本地Debug准入，不构成产品外发、商店、专利、替换/再链接或模型素材权利闭合。手机/16KiB、Kit多宿主/R8/移除、真实媒体质量矩阵、跟踪/编辑/全P0与发行均待后续阶段，Apple/Windows不开发、无Browser业务。

## 结束与交付

55个实际instrumentation均完整终态，14个依赖BLOCKED未启动；三次失败均原样留存并有独立资源复核，未把客户端结束当远端停止。平板末尾进程和App/worker服务快照为空；手机未启动C13且末尾无VideoKit进程/服务，仍禁用。当前无在途操作，不清理/降级、不自行换候选或派下一批。

本报告及任务完成事件供负责人接收，不重试已被拒绝的跨窗口通知。C12及更早历史结果保持。D1未通过，不进入M0。
