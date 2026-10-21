# C14 设备附录 V1.0

2026-10-16，仅编译后计划，所有本批设备NOT_RUN。73可调度＋2不重跑的信号门禁，不能把后者当PASS或环境阻断。coder无ADB、不自行交tester；负责人统一安排。

## 调度与依赖

环境只读预检实际App/component/service enabled；手机禁用仍ENVIRONMENT_BLOCKED，UNKNOWN另列，不安装绕过/换包名/卸载清数据/强启。冻结身份和可读旧cache/旧APK由tester按正式要求保留，fixtures/basic.mp4与subtitle.avi只读，不修改原媒体或旧capture。

先环境、公开能力快照、CPU正常MP4/AVI基线，再pipeline MP4/AVI两正例；两正例必须六真实源/六输入/六样本/六独立完整EOF，原时基与相对PTS≤1ms对应，luma≤24、源差异≥4/输出≥2及映射拒绝不改，无音频明确。未成立时后续14个原负例依赖BLOCKED而非编造通过。OwnerRecovery只依赖环境/lease。host7双轨/故障/恢复、legacy8实际编码/Sink/恢复在真实remote终态后回归；不增新crash方法。

Encoder six：PublicCapabilitySnapshot记录实际inventory/四提案上限，没有可用encoder也只证明快照完成；CapabilityDenial人为拒绝能力，预期0 create/0 Source/0 writer/无token且实际资源归还，不是实际设备无能力结论。RejectedConfigurationReleasesBeforeNext在真实configure返回后注入首次拒绝，须先实际release再下一，最终真实六帧READY、attempt2–4、firstAttemptError CONFIGURE仍在；若有限候选不能满足，保留真实FAIL，不无限重跑。AllRejected在每个实际configure后注入拒绝，首CONFIGURE失败、1–4次、无Source/输出writer/READY。

CancelDuringNegotiation在真实configure返回后的owner闸门持有时主线程cancel，pendingOwnerCalls1、单许可保留且无Source/writer，解闸后实际release才ABORTED；这是owner操作闸门，不冒充被卡住的vendor JNI。CloseAckUnproven在实际release正常返回后保守扣住ACK，PENDING/attempt1/codec_released=false/许可1且不重选；只有测试明确确认该实际返回后recover归还。它不制造真实硬件release失败；真实release不确定仍quarantine，不可用测试确认接口绕过未知底层状态。

所有原17 pipeline方法保留：跨代/迟到在复制前拒绝，queue满必须见2帧及blocked offer>500ms，消费者失联/编码输入拒绝/运行错误不READY；Sink write/flush注入命中实际writer，截断只改自己的临时输出并由隔离CPU拒绝，READY丢响应同exportId query/reconcile同token。取消时consumer租约1要立即PENDING，另一真实CPU继续并resume得到帧，第二encoder创建前拒绝。owner-drop恢复不是新管线实际宿主SIGKILL；原legacy真实host death方法仍分开。

## 原始证据与有限预算

保存PIPE_ENCODER_CAPABILITY/PLAN/DIAGNOSTIC/OPEN/OUTPUT_FORMAT及PIPE_SOURCE_FRAME/ENCODE_INPUT/SAMPLE、CPU_OUTPUT_FRAME/FULL_EOF、CONTENT/VISUAL_CHECK和PIPE_LEDGER。每个候选name/canonical/hardware/software/vendor、范围/对齐/color/profile、actual isFormatSupported、配置keys/phase/公开错误码/诊断标识/首错/关闭均核对；支持声明不是配置成功，软件选中不说硬编保证。close未证、creating或owner call未归还必须停止重选/保留PENDING；实际失败不可改为能力skip。

最多128系统info、16 AVC能力、32types、64colors/64profile-level、标识128字符、4提案/创建、12秒协商且总60秒；原生调用超时不强制释放。CPU2、encoder/output1、queue2/consumer1/producer1，8份可达RGBA1179648B＋YUV55296B，codec/Image/转换数组及queue/offers/保留CPU任务分别记账；不是整堆/RSS峰值。六snapshot逐次实际关闭源后推进，Source pending/死亡/绑定/两槽证据独立。

单输出含头≤2MiB，d1_c14_pipeline_outputs最多24 journals/累计4MiB，创建前预留2MiB；host＋pipeline整批新输出≤8MiB且task/journal按正式tester总预算，日志/文本≤32MiB、剩余空间足够。保留历史数据，不删除凑预算；fixture不计新输出，但磁盘需容纳736803758B只读basic/subtitle。新6方法产生自己的失败journal，事前预估73项总量，接近目录24或4MiB时停调度交负责人，不清历史。源/旧capture完整hash前后核对，SRT存在不等字幕时序/显示通过。

run_device_c14.py默认PLAN_ONLY。执行需serial/group/method、review、docs/tester内独占attempt-dir及per-device log-budget-root；每次日志流限额，失败/能力阻断/环境阻断/UNKNOWN非零，停止依赖链。两个不重跑CPU方法会在ADB预检之前被require_planned明确拒绝。客户端超时/退出不证明远端结束，先实际核在途/服务/进程、保留全部尝试和错误，由负责人决定独立项，不重复跑求理想signal。

结束复核真实每方法资源账本、Source/codec/Image/FD/lease/owner/callback/帧、预算和旧数据hash；末尾ps空只证明结束状态。C13-T02原FAIL与trace/ordinary限制不关闭。D1未通过，不进入M0。

## 明确未重跑的两项（编译保留）

| 方法 | C14计划状态 |
|---|---|
| `cpuSelfSigsegvSignalMustBeProven` | NOT_RUN_UNCHANGED_PLATFORM_LIMIT |
| `cpuSecondSlotAndHostSurviveFirstSelfCrash` | NOT_RUN_UNCHANGED_PLATFORM_LIMIT |

两项采集代码/判定没有改变；引用正式C13报告self系统0 FAIL和独立双槽系统11 PASS及各自实际释放事实，不外部raw回填，不将C12历史成功写为C14成功。

## 73个可调度方法

| 顺序 | 组 | 方法 |
|---:|---|---|
| 1 | cpu | `cpuEnvironmentPreflight` |
| 2 | cpu | `cpuMp4H264ActualPtsFrame` |
| 3 | cpu | `cpuAviMpeg4ActualPtsFrame` |
| 4 | cpu | `cpuCleanupWithoutBindProvesNoWorker` |
| 5 | cpu | `cpuFirstFailureSurvivesCleanupFailure` |
| 6 | cpu | `cpuActualAggregateAllocationQuotaAndDecode` |
| 7 | cpu | `cpuSeekUsesNewEpochAndDecodedTimestamp` |
| 8 | cpu | `cpuOversizedDeclarationRejectedBeforeDecoderOpen` |
| 9 | cpu | `cpuTruncatedInputRejectsAndReleases` |
| 10 | cpu | `cpuValidAviHeaderBadPacketRejects` |
| 11 | cpu | `cpuWrongDeclaredFormatRejects` |
| 12 | cpu | `cpuCompiledH263DoesNotExpandAcceptedInputCodec` |
| 13 | cpu | `cpuForgedFrameRejectedBeforeHostAllocation` |
| 14 | cpu | `cpuForgedEpochAndClaimedIdentityRejected` |
| 15 | cpu | `cpuUnknownAndEmptyLengthRejectWithActualClose` |
| 16 | cpu | `cpuCancelActiveReadRetainsPendingSourceLedger` |
| 17 | cpu | `cpuCancelAfterActualFrame` |
| 18 | cpu | `cpuHungTaskBoundedStopAndDeath` |
| 19 | cpu | `cpuStopAckLossStillRequiresActualDeath` |
| 20 | cpu | `cpuStalledStopDoesNotConsumeSecondRpcSlot` |
| 21 | cpu | `cpuCancelFromMainThreadDoesNotBlockSecondTask` |
| 22 | cpu | `cpuWrongStopEpochRejectedAndTaskContinues` |
| 23 | cpu | `cpuOnewayStopRejectedAndTaskContinues` |
| 24 | cpu | `cpuRegistrarSynchronousMetadataAndRejects` |
| 25 | cpu | `cpuRegistrarLocalHostIdentityRejected` |
| 26 | cpu | `cpuRegistrationBadMagicPreservesFirstCause` |
| 27 | cpu | `cpuRegistrationTrailingReplyPreservesFirstCause` |
| 28 | cpu | `cpuCancelBeforeRegistrationClosesBindingAndRetainsUnknown` |
| 29 | cpu | `cpuCancelBeforeBindReturnRevokesLateAcceptance` |
| 30 | cpu | `cpuUnbindFailureRequiresExplicitRecovery` |
| 31 | cpu | `cpuDuplicateConnectionKeepsOriginalIdentity` |
| 32 | cpu | `cpuCancelDuringHelloCannotStartOrRevive` |
| 33 | cpu | `cpuRejectedExtraWorkerRetainsSlotAndSecondTask` |
| 34 | cpu | `cpuLateWorkerCannotBorrowOriginalDeath` |
| 35 | cpu | `cpuExitCollectionRejectsMainThread` |
| 36 | host | `realEncoderOutput` |
| 37 | host | `outputValidationCounterexamples` |
| 38 | host | `exportReadyResponseLoss` |
| 39 | host | `exportWriteFault` |
| 40 | host | `exportFlushFault` |
| 41 | host | `exportValidationFault` |
| 42 | host | `writingJournalRecovery` |
| 43 | legacy | `nativeLeaseSurvivesDuplicateDescriptorClose` |
| 44 | legacy | `isolatedActualEncodeAndReadyRecovery` |
| 45 | legacy | `cancelAfterActualVideoSample` |
| 46 | legacy | `workerExitDuringActualEncoding` |
| 47 | legacy | `workerSigsegvDuringActualEncoding` |
| 48 | legacy | `secondCodecTaskSurvivesFirstNativeCrash` |
| 49 | legacy | `actualHostDeathDuringEncodingAndCrossOwnerAbort` |
| 50 | legacy | `actualHostDeathAfterReadyAndSameTaskQuery` |
| 51 | pipeline | `pipelineMp4RealFramesVideoOnly` |
| 52 | pipeline | `pipelineAviRealFramesVideoOnly` |
| 53 | pipeline | `pipelineRejectsCrossEpochBeforeCopy` |
| 54 | pipeline | `pipelineRejectsLateFrame` |
| 55 | pipeline | `pipelineQueueSaturationAborts` |
| 56 | pipeline | `pipelineConsumerLostAborts` |
| 57 | pipeline | `pipelineEncoderInputRejectedNoReady` |
| 58 | pipeline | `pipelineEncoderErrorNoReady` |
| 59 | pipeline | `pipelineSinkWriteFailureAborts` |
| 60 | pipeline | `pipelineSinkFlushFailureAborts` |
| 61 | pipeline | `pipelineCorruptOutputRejectedByIsolatedDecoder` |
| 62 | pipeline | `pipelineReadyResponseLossSameToken` |
| 63 | pipeline | `pipelineDecodeFailureAborts` |
| 64 | pipeline | `pipelineCancelInFlightRetainsFrameLease` |
| 65 | pipeline | `pipelineIndependentCpuSurvivesFailure` |
| 66 | pipeline | `pipelineRejectsSecondEncoderBeforeCreation` |
| 67 | pipeline | `pipelineOwnerRecoveryFencesIncompleteWriting` |
| 68 | encoder | `encoderPublicCapabilitySnapshot` |
| 69 | encoder | `encoderCapabilityDenialCreatesNothing` |
| 70 | encoder | `encoderRejectedConfigurationReleasesBeforeNext` |
| 71 | encoder | `encoderAllRejectedNoSourceWriter` |
| 72 | encoder | `encoderCancelDuringNegotiationRetainsPermit` |
| 73 | encoder | `encoderCloseAckUnprovenStopsSelection` |
