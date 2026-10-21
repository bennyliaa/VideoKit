# C12 手机/平板统一设备附录

2026-10-16。coder设备NOT_RUN；负责人一次整包交tester，逐方法串行，不与构建争用。冻结device_plan.json为唯一调度清单；APK另编入的历史ordinary UNKNOWN/播放/模型入口不自动运行，不按整个JUnit类批跑。

## 前置、数据及停止规则

实际核验serial/API31+/ARM64/页大小、已装包hash/签名/用途、installed/enabled/component/Service及空间；连接/安装成功或历史设备型号不是就绪证明。历史手机U4999DLBNRR89DOR/PDYM20系统禁用，用户正确设置页无启用按钮；环境未变则ENVIRONMENT_BLOCKED，不重复要求找按钮，不enable、卸载、清数据或绕过系统。平板历史HA1Q6WXR/TB138FC需现场重新核验。

CPU只用主/测试APK；legacy阶段才核对worker APK。新files/d1_c12_fixtures仅basic.mp4和subtitle.avi，736803758字节，hash见transfer工具；保留旧包/数据/cache、旧capture及fixture，不覆盖原素材或旧候选目录。空间沿用fixture总量＋最大单文件＋256MiB余量；每设备日志32MiB，legacy新终态建议≤32项/8MiB，CPU不持久落帧或READY。

工具默认PLAN_ONLY，执行需明确serial/method/group、独占attempt目录、设备预算根及候选/数据复核。每次命令读写时限额，失败非零退出、停止外层调度。真实断言FAIL、环境阻断、执行UNKNOWN分开。超时或本机ADB客户端结束不证明远端已停；须核查实际在途/进程/Service并由负责人决定独立项。保留全部尝试，禁止同条件重跑求理想信号。

环境预检后先正常MP4/AVI，必须见REGISTER/HELLO/真实帧及finally完整门禁，再调度解码依赖。无绑定资源/首错、未知空长度、LocalHostIdentity和主线程取证拒绝等独立项可另判；host7/legacy8需实际远端结束后独立回归。原C10/C11未进入的代次/trace在前置恢复后单次验证，不能引用旧PASS/FAIL改写本批。

## 新证据重点

- cpuRegistrarSynchronousMetadataAndRejects：真实isolated→host注册事务，覆盖同步0/metadata组合、oneway组合、code/descriptor/session/endpoint/尾随拒绝；保存接收端真实flags/caller PID/UID/result，不能把发送端参数当接收实测值。重复登记应同一代次，只链接一次死亡，无额外START。
- cpuRegistrarLocalHostIdentityRejected：Android本地Binder的非隔离host身份拒绝，仅为本地负例，不冒充远端kernel身份错误已测。
- BadMagic/TrailingReply：只在Debug测试破坏REGISTER reply，worker须分开记录固定原因并经认证FAILURE回报；host首错为对应CPU_REG_REPLY_*且phase REGISTER，cleanup独立，不得降为generic CONNECT timeout。不得发送START或解码预算。
- CancelBeforeRegistration/BeforeBindReturn：真实注册在途闸门、迟到返回与主线程cancel；解绑不等登记/死亡，须见closed=true时未知/在途/两槽仍保留且第三任务拒绝，另一任务继续完成。解除闸门后晚到端点只撤销，实际death/Source/全部pending回收后才释放。
- UnbindFailureRequiresExplicitRecovery：第一次解绑故意失败，重复cancel不自动重试/放行；显式recover第二次真实解绑，仍需实际death。最多3次，失败保留quarantine。
- 原STOP_STALL/ACK-loss方法增加显式Debug解绑闸门，保留原响应/在途反例窗口，finally必释放；生产cancel没有该闸门。闸门超时不能伪释放。

记录CPU_REGISTRATION_DIAG、worker CPU_REGISTRATION_REPLY/FAILED、CPU_DIAGNOSIS、逐代次ledger，以及CPU_UNBIND_LEDGER issued/accepted/uncertain/in_flight/requested/attempts/pending/closed/result（issued由实际绑定阶段另核对），Source及全部pending/slots/global未知预算。binding_closed、actual_death、no_worker_proven、slot_released四种事实分别审核；未知accepted绑定即使解绑后计数仍≥1。绑定失败/超时/解绑成功/系统finished-inst或末尾ps空不能作未创建或期限内死亡证明。

C11首次Binder/身份、旧death隔离、额外端点无START/source、两CPU槽/MAX_WORKERS异常记录上限继续验证。若binding_closed后出现未知新进程/登记、终态重新START、旧death给新worker释放或unknown借解绑清零，保留FAIL并停调度。

严格SIGSEGV入口仍须真实帧→ARMED→cleanup前death，原任务PID/isolated UID/时间/进程的raw独立保存。EXIT_EVIDENCE.signal是OS原始status，trace_signal另列；signal0无论trace声明什么都UNKNOWN/FAIL。外部raw、STOP的SIG9、测试预期和清理不替代目标11。C11取证器3条流/字节限制及pending/close隔离不变。

host维持真实H264/AAC双轨各自非零、PTS/full decode和READY/abort/reconcile门禁；legacy8仅历史companion回归，不证明CPU trace已通过。整批结束复核无在途/残留、素材hash、旧capture及日志/输出预算，集中报告。D1未通过，不进入M0。

## 单方法清单：52项

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
| 24 | cpu | cpuRegistrarSynchronousMetadataAndRejects |
| 25 | cpu | cpuRegistrarLocalHostIdentityRejected |
| 26 | cpu | cpuRegistrationBadMagicPreservesFirstCause |
| 27 | cpu | cpuRegistrationTrailingReplyPreservesFirstCause |
| 28 | cpu | cpuCancelBeforeRegistrationClosesBindingAndRetainsUnknown |
| 29 | cpu | cpuCancelBeforeBindReturnRevokesLateAcceptance |
| 30 | cpu | cpuUnbindFailureRequiresExplicitRecovery |
| 31 | cpu | cpuDuplicateConnectionKeepsOriginalIdentity |
| 32 | cpu | cpuCancelDuringHelloCannotStartOrRevive |
| 33 | cpu | cpuRejectedExtraWorkerRetainsSlotAndSecondTask |
| 34 | cpu | cpuLateWorkerCannotBorrowOriginalDeath |
| 35 | cpu | cpuExitCollectionRejectsMainThread |
| 36 | cpu | cpuSelfSigsegvSignalMustBeProven |
| 37 | cpu | cpuSecondSlotAndHostSurviveFirstSelfCrash |
| 38 | host | realEncoderOutput |
| 39 | host | outputValidationCounterexamples |
| 40 | host | exportReadyResponseLoss |
| 41 | host | exportWriteFault |
| 42 | host | exportFlushFault |
| 43 | host | exportValidationFault |
| 44 | host | writingJournalRecovery |
| 45 | legacy | nativeLeaseSurvivesDuplicateDescriptorClose |
| 46 | legacy | isolatedActualEncodeAndReadyRecovery |
| 47 | legacy | cancelAfterActualVideoSample |
| 48 | legacy | workerExitDuringActualEncoding |
| 49 | legacy | workerSigsegvDuringActualEncoding |
| 50 | legacy | secondCodecTaskSurvivesFirstNativeCrash |
| 51 | legacy | actualHostDeathDuringEncodingAndCrossOwnerAbort |
| 52 | legacy | actualHostDeathAfterReadyAndSameTaskQuery |
