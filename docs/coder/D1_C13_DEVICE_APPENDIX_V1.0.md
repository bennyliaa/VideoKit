# C13 设备附录 V1.0

2026-10-16。仅计划与已编译方法，设备NOT_RUN，coder不调用ADB，不自行派tester。37 CPU/7 host/8 legacy沿用C12完整52方法，新pipeline17，共69/合格设备；方法清单由实际源码及DEX核对。两种真实源basic.mp4/subtitle.avi只读，原文件与旧capture保留；外挂SRT存在不构成字幕成功。

## 顺序与依赖

1. 由负责人确认冻结身份及空间/旧证据，tester只读查询实际app/component/service enabled。手机被禁用维持ENVIRONMENT_BLOCKED；未知状态另记UNKNOWN，不换包名/卸载/清数据/强启或要求找已确认不存在的按钮。
2. CPU环境、MP4/AVI真实帧基线及完整52回归。新pipeline依赖对应CPU源基线、实际编码能力及MP4/AVI两正例；正例不成立，编码/输出依赖项标BLOCKED而不拿纯测试补成功。ownerRecovery只依赖环境/lease，不依赖编码成功。
3. 每次只一个方法，独占attempt目录，保留所有日志与失败尝试。已有真实SIGSEGV两项随52回归，不加新故障campaign；ordinary UNKNOWN历史不重跑求理想信号。host7/legacy8在实际remote无在途后回归，不代替单APK管线或完整隔离。
4. 默认run_device_c13.py PLAN_ONLY；执行需serial/method/group=cpu|host|legacy|pipeline、review及docs/tester内独占attempt-dir/log-budget-root。失败、能力阻断、环境阻断和执行UNKNOWN非零退出，外层停止依赖链。客户端超时/结束不证明remote停止，先核查真实在途与负责人决定独立项。

## 新方法预期与原始证据

两正例必须6个真实源帧/编码输入/实际样本/隔离解码输出均为6，READY且同一token、audio=false；源task/epoch/PID/UID/raw timebase/实际PTS/hash逐帧对应。查看PIPE_SOURCE_FRAME、PIPE_ENCODE_INPUT、PIPE_ENCODE_SAMPLE、CPU_OUTPUT_FRAME_VERIFIED、CPU_OUTPUT_FULL_EOF_VERIFIED、PIPE_CONTENT_FRAME、PIPE_VISUAL_CHECK。输出PTS匹配源相对时间≤1ms，luma MAE≤24、源至少两画面差异≥4、输出差异≥2及错误映射拒绝；真实片段不具可区分性应FAIL/未证，不降低阈值或换合成图案。

CrossEpoch在额外复制前PIPE_FRAME_IDENTITY；LateFrame为PIPE_FRAME_ORDER；QueueSaturation实际queue2/blocked offer>500ms触发PIPE_FRAME_QUEUE_FULL；ConsumerLost、encoder-reject/error各保留对应首因。Sink write/flush有实际注入计数，验证反例先写真实输出再截断自己的临时文件，由隔离CPU解析/解码拒绝；所有负例token为空且不READY。ReadyResponse持久READY后故意丢应答，query/reconcile同exportId同token，恢复abort不能撤销READY。

CancelInFlight在真实consumer租约闸门持有时主线程cancel，立即PENDING/consumer1/encoder许可仍1；解闸后实际关闭才ABORTED和全部归还。IndependentCpu在第二真实WAIT_FRAME任务活着时让管线失败，第二任务不得死亡，resume后得到真实结果。RejectsSecondEncoder在第一真实在途时第二许可申请应在codec/输出创建前拒绝。OwnerRecovery验证live owner不可替换、实际关闭后重获WRITING并幂等abort；不是新管线宿主SIGKILL证明，真实host死亡仍看旧8项。

每方法保存PIPE_LEDGER及CPU逐代次death/source/binding/pending/slot账本，资源released须source、codec/Image、writer/FD/共享lease/owner、queue/consumer和callback实际归还。timeout返回PENDING不算已释放；原始错误与cleanup分开，未归还引用保持quarantine，禁止反复新建任务绕预算。source真实hash前后不变；producer后续可能打开句柄前不得移动/删除授权源。

## 预算与终结

CPU进程内2槽、pipeline encoder/output1槽；queue2+consumer1+producer候选1，固定RGBA147456B，保守8个宿主可达数组1179648B（不是RSS上限）与YUV55296B，缩略小记录；无Surface/AudioTrack。原FFmpeg配额/白名单不扩。单输出含容器头≤2MiB；专用d1_c13_pipeline_outputs最多24 journals/累计4MiB，进入前预留完整2MiB。监测host与pipeline合计新输出≤8MiB；旧目录不删除凑预算。每设备日志/文本≤32MiB，工具读写时限额，执行前检查剩余空间；fixtures不计输出预算但须充足磁盘。六快照每次实际释放后下一次，实验deadline60秒，await/cleanup另有有限等待，超时保留PENDING。

结束检查素材/旧capture hash、预算、真实在途/服务/进程与每方法账本；末尾ps空只证明结束快照，不补方法成功。当前两受控SIGSEGV原OS11与trace缺失分栏保留，status0不能借App trace补11；不自动关闭历史ordinary UNKNOWN。编码能力不支持明确CAPABILITY_BLOCKED，新管线不是正式双轨、显示/声音或跟踪P0。D1未通过，不进入M0。

## 69个具体方法

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
| 36 | cpu | `cpuSelfSigsegvSignalMustBeProven` |
| 37 | cpu | `cpuSecondSlotAndHostSurviveFirstSelfCrash` |
| 38 | host | `realEncoderOutput` |
| 39 | host | `outputValidationCounterexamples` |
| 40 | host | `exportReadyResponseLoss` |
| 41 | host | `exportWriteFault` |
| 42 | host | `exportFlushFault` |
| 43 | host | `exportValidationFault` |
| 44 | host | `writingJournalRecovery` |
| 45 | legacy | `nativeLeaseSurvivesDuplicateDescriptorClose` |
| 46 | legacy | `isolatedActualEncodeAndReadyRecovery` |
| 47 | legacy | `cancelAfterActualVideoSample` |
| 48 | legacy | `workerExitDuringActualEncoding` |
| 49 | legacy | `workerSigsegvDuringActualEncoding` |
| 50 | legacy | `secondCodecTaskSurvivesFirstNativeCrash` |
| 51 | legacy | `actualHostDeathDuringEncodingAndCrossOwnerAbort` |
| 52 | legacy | `actualHostDeathAfterReadyAndSameTaskQuery` |
| 53 | pipeline | `pipelineMp4RealFramesVideoOnly` |
| 54 | pipeline | `pipelineAviRealFramesVideoOnly` |
| 55 | pipeline | `pipelineRejectsCrossEpochBeforeCopy` |
| 56 | pipeline | `pipelineRejectsLateFrame` |
| 57 | pipeline | `pipelineQueueSaturationAborts` |
| 58 | pipeline | `pipelineConsumerLostAborts` |
| 59 | pipeline | `pipelineEncoderInputRejectedNoReady` |
| 60 | pipeline | `pipelineEncoderErrorNoReady` |
| 61 | pipeline | `pipelineSinkWriteFailureAborts` |
| 62 | pipeline | `pipelineSinkFlushFailureAborts` |
| 63 | pipeline | `pipelineCorruptOutputRejectedByIsolatedDecoder` |
| 64 | pipeline | `pipelineReadyResponseLossSameToken` |
| 65 | pipeline | `pipelineDecodeFailureAborts` |
| 66 | pipeline | `pipelineCancelInFlightRetainsFrameLease` |
| 67 | pipeline | `pipelineIndependentCpuSurvivesFailure` |
| 68 | pipeline | `pipelineRejectsSecondEncoderBeforeCreation` |
| 69 | pipeline | `pipelineOwnerRecoveryFencesIncompleteWriting` |
