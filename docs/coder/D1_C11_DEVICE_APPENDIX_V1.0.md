# C11 手机/平板统一设备附录

2026-10-16。coder设备执行NOT_RUN。整批冻结后由负责人一次交tester，不逐功能换包。实际包hash/证书及环境、空间、数据、旧包备份须现场独立核验，不能从连接/安装成功推断Service可用。

## 前置与预算

ARM64/API31+；保存真实API/ABI/页大小与当前serial。历史平板HA1Q6WXR/TB138FC可用，手机U4999DLBNRR89DOR/PDYM20被com.oplus.athena禁用，这些历史不替代当前预检。只读installed/enabled/component/Service检查失败立即停止相关组并记ENVIRONMENT_BLOCKED/UNKNOWN；不enable、卸载、清数据或绕过系统限制。CPU每方法及每start都有App内预检，assumption不能算PASS。

核对冻结main/test APK；CPU不用companion。legacy阶段才核对worker APK，原私有数据/旧包/cache和capture保留。新files/d1_c11_fixtures仅basic.mp4、subtitle.avi，合计736803758字节；源hash见transfer_fixtures，实际传输身份独立核验，不覆盖旧候选目录。保留总fixture＋最大单文件＋256MiB余量。每设备日志总32MiB，legacy新终态输出建议≤32项/8MiB，CPU不落持久帧/READY。

run_device_c11.py默认PLAN_ONLY，只有显式serial/method/group、独占attempt-dir、设备预算根及候选/数据复核才执行单方法；本批只允许device_plan.json的入口。日志读取时硬限额，失败非零退出、停止外层调度。超时/本机子进程结束不证明远端已停或资源释放；必须核查在途和残留，不能自动调下一项。记录每次尝试，不覆盖、不重复相同signal0条件。

## 验证与门槛

每个合格设备45项，CPU 30、host 7、legacy 8。APK另编入的历史ordinary UNKNOWN/播放/模型入口不在本批调度范围；不要按整个JUnit类批跑。正常MP4/AVI及finally资源门禁先过，再按依赖运行独立反例。

新增五项：cpuDuplicateConnectionKeepsOriginalIdentity, cpuCancelDuringHelloCannotStartOrRevive, cpuRejectedExtraWorkerRetainsSlotAndSecondTask, cpuLateWorkerCannotBorrowOriginalDeath, cpuExitCollectionRejectsMainThread。额外worker测试是真实独立隔离进程，只有HELLO/STOP控制，故意挂起STOP；不发送START/broker/source/媒体。须看到旧worker已死而额外worker未死时slot不释放、第三任务被拒、第二任务继续真实解码；finally经认证解除闸门、解绑额外连接并核对所有实际死亡。旧death重放只允许已有真实DeathRecipient的原端点，不能用调试调用制造第一次死亡证明。

保存原始task/epoch、首次PID/UID/process身份、generation注册/HELLO/死亡、每代次STOP attempts/pending/ACK/result、binding_closed、全局unproven/reserved_cpu_slots、Source实际operations/consumers/failedCloses/close、所有pending_calls和最终slot。MAX_WORKERS=4是历史/异常端点记录上限，不是并发CPU许可；溢出/未知/在途保留quarantine。

**严格判失败条件**：首次身份被改写，原帧/旧death归到新代次，终态重新START，未知/额外worker仅凭unbind或旧death释放，binding_closed后新未知进程或登记，仍在途时slot放行。若出现，停止调度、保留原账本与原始进程证据，不能拿末尾ps空补成期限内通过。framework/系统创建竞态未实测，不预写通过。

两个SIGSEGV入口仍需真实帧→ARMED→cleanup前实际death，精确匹配原任务PID/isolated UID/时间/进程的raw单独保存。EXIT_EVIDENCE.signal是原OS status，trace_signal另列；**status0无论trace声明什么都UNKNOWN/FAIL**。不得以STOP的SIGKILL、isolated-not-needed、清理或测试预期替代目标signal11。不因本批读取trace而批准新P0依据。

主线程取证拒绝测试应返回明确状态且不启动采集。真实采集最多3次打开流，3秒轮询/调用方4秒等待；PENDING/关闭失败要保留采集器隔离，禁止超时清零。legacy共享ExitEvidence和parser变化，坏/冲突trace只能保守失败；原codec abort原因白名单不扩。host仍要求H264/AAC双轨各自非零、真实PTS和full decode，以及ready/abort/reconcile安全门禁。

## 明确单方法清单

| 顺序 | 组 | 方法 |
|---:|---|---|
| 1 | cpu | cpuEnvironmentPreflight |
| 2 | cpu | cpuMp4H264ActualPtsFrame |
| 3 | cpu | cpuAviMpeg4ActualPtsFrame |
| 4 | cpu | cpuCleanupWithoutBindProvesNoWorker |
| 5 | cpu | cpuFirstFailureSurvivesCleanupFailure |
| 6 | cpu | cpuActualAggregateAllocationQuotaAndDecode |
| 7 | cpu | cpuSeekUsesNewEpochAndDecodedTimestamp |
| 8 | cpu | cpuOversizedDeclarationRejectedBeforeDecoderOpen |
| 9 | cpu | cpuTruncatedInputRejectsAndReleases |
| 10 | cpu | cpuValidAviHeaderBadPacketRejects |
| 11 | cpu | cpuWrongDeclaredFormatRejects |
| 12 | cpu | cpuCompiledH263DoesNotExpandAcceptedInputCodec |
| 13 | cpu | cpuForgedFrameRejectedBeforeHostAllocation |
| 14 | cpu | cpuForgedEpochAndClaimedIdentityRejected |
| 15 | cpu | cpuUnknownAndEmptyLengthRejectWithActualClose |
| 16 | cpu | cpuCancelActiveReadRetainsPendingSourceLedger |
| 17 | cpu | cpuCancelAfterActualFrame |
| 18 | cpu | cpuHungTaskBoundedStopAndDeath |
| 19 | cpu | cpuStopAckLossStillRequiresActualDeath |
| 20 | cpu | cpuStalledStopDoesNotConsumeSecondRpcSlot |
| 21 | cpu | cpuCancelFromMainThreadDoesNotBlockSecondTask |
| 22 | cpu | cpuWrongStopEpochRejectedAndTaskContinues |
| 23 | cpu | cpuOnewayStopRejectedAndTaskContinues |
| 24 | cpu | cpuDuplicateConnectionKeepsOriginalIdentity |
| 25 | cpu | cpuCancelDuringHelloCannotStartOrRevive |
| 26 | cpu | cpuRejectedExtraWorkerRetainsSlotAndSecondTask |
| 27 | cpu | cpuLateWorkerCannotBorrowOriginalDeath |
| 28 | cpu | cpuExitCollectionRejectsMainThread |
| 29 | cpu | cpuSelfSigsegvSignalMustBeProven |
| 30 | cpu | cpuSecondSlotAndHostSurviveFirstSelfCrash |
| 31 | host | realEncoderOutput |
| 32 | host | outputValidationCounterexamples |
| 33 | host | exportReadyResponseLoss |
| 34 | host | exportWriteFault |
| 35 | host | exportFlushFault |
| 36 | host | exportValidationFault |
| 37 | host | writingJournalRecovery |
| 38 | legacy | nativeLeaseSurvivesDuplicateDescriptorClose |
| 39 | legacy | isolatedActualEncodeAndReadyRecovery |
| 40 | legacy | cancelAfterActualVideoSample |
| 41 | legacy | workerExitDuringActualEncoding |
| 42 | legacy | workerSigsegvDuringActualEncoding |
| 43 | legacy | secondCodecTaskSurvivesFirstNativeCrash |
| 44 | legacy | actualHostDeathDuringEncodingAndCrossOwnerAbort |
| 45 | legacy | actualHostDeathAfterReadyAndSameTaskQuery |

每设备按实际结果区分PASS、TEST_FAILED、ENVIRONMENT_BLOCKED、PREPARATION_FAILED/UNKNOWN、EXECUTION_UNKNOWN；不能把断言FAIL改为环境阻断，也不能以历史C10 PASS代替C11。方法断言通过之后还需独立审账本/raw。整批结束核查无在途/残留、素材hash和日志/输出预算，提交完整集中报告。D1未通过，不进入M0。
