# D1 C11 集中测试报告 V1.0

报告时间：2026-10-16T10:30:45+08:00。候选 D1-20261016-C11，git_commit=null。正式输入为 D1_PHONE_TEST_EXECUTION_V1.0 顶部 C11 交接、D1_C11_TESTER_REQUIREMENTS_V1.0、C11 交付/设备附录/退出取证设计及冻结 device_plan.json。

## 结论

**D1 未通过，不进入 M0。本批结束，无新增设备方法。** 手机 45 项环境阻断；平板计划45项，实际运行22项：20 PASS、2 FAIL，另23项前置 BLOCKED。正常 MP4、AVI 均在新的注册握手阶段失败，无真实 CPU 帧；依赖该正常前置的代次、额外 worker 和 SIGSEGV/trace 集成路径未执行，不能宣称修复闭合。

| 设备 | CPU30 | host7 | legacy8 | 合计 |
| --- | --- | --- | --- | --- |
| OPPO PDYM20 / U4999DLBNRR89DOR | 30 ENVIRONMENT_BLOCKED | 7 ENVIRONMENT_BLOCKED | 8 ENVIRONMENT_BLOCKED | 45 环境阻断，0次 C11 instrumentation |
| Lenovo TB138FC / HA1Q6WXR | 5 PASS / 2 FAIL / 23 BLOCKED | 7 PASS | 8 PASS | 20 PASS / 2 FAIL / 23 BLOCKED |

手机和平板均 API31、ARM64、4096字节页。手机现场及结束 enabled=2、lastDisabledCaller=com.oplus.athena；未启用、卸载、清数据、更新 C11 或调测试。此前只读查看正确的应用详情页确实没有“启用”按钮，该显示差异不是用户导航错误，独立证据在 PHONE_SETTINGS_20261016；不据“打开”按钮断言已启用。

## 冻结、签名与实际安装身份

独立 verify_c11 校验冻结173源/111证据/5产物 PASS，并独占复制5产物，逐项核验实际字节及 hash。冻结时间2026-10-16 10:19:32。未运行 Gradle、未重建上游、未改冻结件或产品源码。依据是冻结 ZIP，不把当前工作树当旧候选。详见 [freeze-check](D1_C11_EVIDENCE/freeze-check.json)、[admission-check](D1_C11_EVIDENCE/admission-check.json)。

| 对象 | SHA256 |
| --- | --- |
| freeze-summary | bfe33794c0ac606fef0e5fb498672e3a9e33b8390b0e21fe153eb86877306138 |
| source ZIP | 6a1526d20463eef3d9ee8b790af8a8aca41af2e7abdbf5628b5a41fa56fa3a6d |
| app-debug.apk | eb38a952ca1394ef275d52ac890fe265348efec7a143656ee5c02b13ab3f02ec |
| app-debug-androidTest.apk | eda49a21c2d95fd4ec99121031643aa48b47dc4c13275330895b1633f0002c5c |
| worker-debug.apk，仅legacy | 59e99d32b8c0afc98e78ea74114957aee107939173316d4f7bbe719264a5c213 |
| release-unsigned，仅静态对照、未安装 | 71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e |

三个 Debug 包实际签名核验 PASS，证书 SHA256：5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。平板 main/test 更新前备份已知 C10 APK、包状态与可读缓存；更新后回读实际安装 APK，hash 与上述冻结一致。CPU不用companion；host结束后另备份旧worker并同签名保留数据更新，最终回读worker hash一致。手机旧APK及可读缓存亦备份，阻断后未更新。

16个native包条目独立核验库hash、stored布局/偏移与ELF LOAD对齐；五个FFmpeg/allocator库与既有基线逐字节相同，Release hash不变。16KiB静态对齐不等于16KiB页设备运行。交付498 JVM＋28脚本＝526项是本机自检证据，未作为设备PASS计数。

## 执行控制与逐项结果

手机预检阻断后继续平板；逐设备、逐方法串行，冻结列表以外的方法未启动。每方法只有一个独占attempt目录，不覆盖旧证据。两次实际FAIL立即停止外层调度，核查终态/进程/服务及资源，写 review.json 后才继续独立项。没有重试正常前置或重复碰信号，没有按整个JUnit类运行。正常MP4/AVI前置失败后，实际调用start/解码的23项全部按依赖阻断；无绑定清理、构造异常、无效长度及主线程拒绝仍独立执行。故障入口BLOCKED不是本轮再次证明signal0，也不是FAIL改环境阻断。

手机EB=ENVIRONMENT_BLOCKED，统一证据 phone/environment.json、preflight.json、package-at-end.txt。平板每项实际尝试证据为 `D1_C11_EVIDENCE/tablet/attempts/方法名/`，含command/result/post/review；BLOCKED无attempt目录，依赖见 plan.json、results.json。独立汇总见 [execution-audit](D1_C11_EVIDENCE/execution-audit.json)。

| 序号 | 组 | 方法 | 手机 | 平板 |
| --- | --- | --- | --- | --- |
| 01 | cpu | cpuEnvironmentPreflight | EB | PASS |
| 02 | cpu | cpuMp4H264ActualPtsFrame | EB | FAIL |
| 03 | cpu | cpuAviMpeg4ActualPtsFrame | EB | FAIL |
| 04 | cpu | cpuCleanupWithoutBindProvesNoWorker | EB | PASS |
| 05 | cpu | cpuFirstFailureSurvivesCleanupFailure | EB | PASS |
| 06 | cpu | cpuActualAggregateAllocationQuotaAndDecode | EB | BLOCKED |
| 07 | cpu | cpuSeekUsesNewEpochAndDecodedTimestamp | EB | BLOCKED |
| 08 | cpu | cpuOversizedDeclarationRejectedBeforeDecoderOpen | EB | BLOCKED |
| 09 | cpu | cpuTruncatedInputRejectsAndReleases | EB | BLOCKED |
| 10 | cpu | cpuValidAviHeaderBadPacketRejects | EB | BLOCKED |
| 11 | cpu | cpuWrongDeclaredFormatRejects | EB | BLOCKED |
| 12 | cpu | cpuCompiledH263DoesNotExpandAcceptedInputCodec | EB | BLOCKED |
| 13 | cpu | cpuForgedFrameRejectedBeforeHostAllocation | EB | BLOCKED |
| 14 | cpu | cpuForgedEpochAndClaimedIdentityRejected | EB | BLOCKED |
| 15 | cpu | cpuUnknownAndEmptyLengthRejectWithActualClose | EB | PASS |
| 16 | cpu | cpuCancelActiveReadRetainsPendingSourceLedger | EB | BLOCKED |
| 17 | cpu | cpuCancelAfterActualFrame | EB | BLOCKED |
| 18 | cpu | cpuHungTaskBoundedStopAndDeath | EB | BLOCKED |
| 19 | cpu | cpuStopAckLossStillRequiresActualDeath | EB | BLOCKED |
| 20 | cpu | cpuStalledStopDoesNotConsumeSecondRpcSlot | EB | BLOCKED |
| 21 | cpu | cpuCancelFromMainThreadDoesNotBlockSecondTask | EB | BLOCKED |
| 22 | cpu | cpuWrongStopEpochRejectedAndTaskContinues | EB | BLOCKED |
| 23 | cpu | cpuOnewayStopRejectedAndTaskContinues | EB | BLOCKED |
| 24 | cpu | cpuDuplicateConnectionKeepsOriginalIdentity | EB | BLOCKED |
| 25 | cpu | cpuCancelDuringHelloCannotStartOrRevive | EB | BLOCKED |
| 26 | cpu | cpuRejectedExtraWorkerRetainsSlotAndSecondTask | EB | BLOCKED |
| 27 | cpu | cpuLateWorkerCannotBorrowOriginalDeath | EB | BLOCKED |
| 28 | cpu | cpuExitCollectionRejectsMainThread | EB | PASS |
| 29 | cpu | cpuSelfSigsegvSignalMustBeProven | EB | BLOCKED |
| 30 | cpu | cpuSecondSlotAndHostSurviveFirstSelfCrash | EB | BLOCKED |
| 31 | host | realEncoderOutput | EB | PASS |
| 32 | host | outputValidationCounterexamples | EB | PASS |
| 33 | host | exportReadyResponseLoss | EB | PASS |
| 34 | host | exportWriteFault | EB | PASS |
| 35 | host | exportFlushFault | EB | PASS |
| 36 | host | exportValidationFault | EB | PASS |
| 37 | host | writingJournalRecovery | EB | PASS |
| 38 | legacy | nativeLeaseSurvivesDuplicateDescriptorClose | EB | PASS |
| 39 | legacy | isolatedActualEncodeAndReadyRecovery | EB | PASS |
| 40 | legacy | cancelAfterActualVideoSample | EB | PASS |
| 41 | legacy | workerExitDuringActualEncoding | EB | PASS |
| 42 | legacy | workerSigsegvDuringActualEncoding | EB | PASS |
| 43 | legacy | secondCodecTaskSurvivesFirstNativeCrash | EB | PASS |
| 44 | legacy | actualHostDeathDuringEncodingAndCrossOwnerAbort | EB | PASS |
| 45 | legacy | actualHostDeathAfterReadyAndSameTaskQuery | EB | PASS |

## 集中缺陷及本轮证据

### C11-T01：真实 CPU worker 注册失败，正常解码整体回归失败（阻断）

MP4、AVI各运行一次，均为真实 TEST_FAILED。首个错误 CPU_CONNECT_FAILED / CONNECT / TIMEOUT；finally 的 CPU_CLEANUP_UNPROVEN 作为 suppressed 保留，没有覆盖主错误。不是环境禁用、JNI加载失败或已证解码错误：App/Service预检可见，binding=ACCEPTED，但没有 CPU_GENERATION_REGISTERED、HELLO、START ACK 或CPU帧，native_stage=0。不能从零帧推断FFmpeg本身失败。

| 入口 | task / epoch | 原始worker故障 |
| --- | --- | --- |
| MP4 | d7306e724b8c435880e5e575d65c90fd / 540922591385906161 | CPU_REGISTRATION_REJECTED；系统启动3757、3777、3808三个进程并尝试重建 |
| AVI | c2ffc57769054deaa2a5b401bc2725c5 / 227027542341345547 | CPU_REGISTRATION_REJECTED；系统启动4236、4258、4277三个进程并尝试重建 |


- cpuMp4H264ActualPtsFrame：PID3757/UID99060, PID3777/UID99061, PID3808/UID99062。各PID专属日志直接记录注册拒绝和自身SIG9。
- cpuAviMpeg4ActualPtsFrame：PID4236/UID99063, PID4258/UID99064, PID4277/UID99065。各PID专属日志直接记录注册拒绝和自身SIG9。

这些SIG9是注册失败后的收敛行为，不是要求的SIGSEGV故障命中。具体证据为两attempt的 post/scoped-system.log、unregistered-pid*.log、unregistered-processes.json、host.log和原始command log。CPU_REGISTRATION_REJECTED把注册false/ACK异常合并为相同错误，未记录真实registrar flags/数据大小/ACK分支，根因尚未在设备侧精确区分。

只读冻结源码发现 registrar.onTransact 首行要求flags==0，不同于既有按oneway位判断的同步控制规则。这是需要研发核查的静态线索；本轮未记录该registrar实际flags，因此不将“实际flags=16”写为已证根因，不擅自改包后补跑。

### C11-T02：注册失败后实际进程重建未入代次账本，绑定/槽位不能在App期限内收敛（阻断）

两正常入口最终均记录：pid/uid=-1、identity=false、start_ack=false、actual_death=false、no_worker_proven=false；binding=ACCEPTED、binding_closed=false、unresolved_workers=1、global_unproven_workers=1、reserved_cpu_slots=1；stop_attempts=0、pending_calls=0、source_released=true、source_close=CLOSED、operations/consumers/failed_closes=0、slot_released=false。逐代次账本为空，但系统日志已证明每次三个实际worker创建及退出。

保留未知worker及槽位的保守判定正确；本缺陷是注册失败路径缺少可完成的实际端点登记/绑定撤销/恢复证明，不是“错误放行槽位”。只读源码进一步显示 cancel() 关闭Source并调用sendStop()；remote=null时sendStop直接返回。取消本身没有主动撤销这个已接受但端点未知的绑定；detachAfterDeath依赖已登记代次的真实death，releaseIfProven又先要求workers.allDead()。因此该未知注册失败路径不能主动unbind以收敛重建，期限内账本仍未关闭；这是与握手兼容性分开的取消收敛缺口。unbind仍不可当作未知worker死亡证明。没有把未知计数清零或借旧death制造新进程死亡。MAX_WORKERS=4的异常记录上限、全局2个CPU任务许可、额外端点无START/source及旧death隔离，本轮均未在依赖项中验证，不能因未出现假释放而关闭C10-T02。

远端结束的独立事实：每次 instrumentation 有完整FAIL及终态；ActivityManager明确记录 finished inst 触发系统停止宿主。失败后只读ps无VideoKit进程、dumpsys activity services com.videokit.app为nothing，才继续独立测试。tester未执行force-stop/kill。该框架结束状态只说明允许继续，不追溯证明方法期限内绑定/槽位释放，原FAIL和quarantine账本保持。

### C11-ENV01：手机仍被系统禁用（环境阻断）

45项均为未执行的环境阻断；连接成功/正确设置页显示“打开”不能替代包状态。未绕过系统控制、未重复要求用户启用、未重跑旧C10。需后续实际环境恢复后再按正式候选安排。

## 退出取证、代次与其他回归边界

- C10-T01：status0也读取trace的新版真实路径未到达；两个CPU SIGSEGV入口因正常MP4前置FAIL而BLOCKED。本轮没有新的CPU原始signal/trace成功或缺失结论；不能以C10 raw11或本机模型补C11 PASS。
- 本轮cpuExitCollectionRejectsMainThread PASS，仅证明实际主线程调用返回EXIT_EVIDENCE_MAIN_THREAD_REJECTED。最多三条流、真实pending/close失败隔离及status0/trace分栏仍未有CPU集成设备证据。原OS status0无论trace声明什么都应UNKNOWN/FAIL，准则未变；未采用外部raw或ARMED作App证明。
- C10-T02：新重复连接、HELLO取消、额外worker、迟到worker四项BLOCKED；没有实际额外端点/旧death交错证据，没有把最终ps空算代次验证通过。
- CPU其余独立PASS为环境预检、无绑定清理、首错/cleanup保留、未知/空长度真实关闭。无绑定方法actual_death=false、no_worker_proven=true、Source CLOSED、global_unproven=0、reserved_cpu_slots=0；binding_closed=false不被当作曾绑定已解除。该方法不证明创建过的worker死亡。
- host7项全部PASS，覆盖真实编码/独立输出反例、ready响应丢失、write/flush/validation故障及journal恢复；legacy8项全部PASS，覆盖真实编码/锁、取消、退出、native crash、第二任务与宿主死亡恢复。共享变化的这些指定入口通过，历史未调度ordinary UNKNOWN仍不关闭。

- legacy原始故障：workerSigsegvDuringActualEncoding PID6622/UID10220，worker日志有匹配signal11。该方法没有额外断言App ExitEvidence分类，不能用其PASS声明CPU trace采集或OS status门槛通过。
- legacy原始故障：secondCodecTaskSurvivesFirstNativeCrash PID6819/UID10220，worker日志有匹配signal11。该方法没有额外断言App ExitEvidence分类，不能用其PASS声明CPU trace采集或OS status门槛通过。

## 数据保护、预算与结束状态

| 设备 | 新C11输出字节 | task/journal | 日志/文本字节 | 旧capture文件 |
| --- | ---: | ---: | ---: | --- |
| 手机 | 0 / 8388608 | 0 / 32 | 31699 / 33554432 | 0个哈希未变 |
| 平板 | 2735217 / 8388608 | 15 / 32 | 845575 / 33554432 | 8个哈希未变 |

日志在读取/写入时实施上限，未靠删除历史日志腾预算。最终cache-before/after-c11.tar、output-budget-final.json、log-budget-final.json留存；旧C06/C07 capture平板8文件未变、手机0文件；未产生新capture。CPU无持久帧或READY，原缓存/旧fixture保留。新私有fixture只复制basic.mp4与subtitle.avi，总736803758字节；测试前后hash一致：720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9及3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f。源文件不算新输出；不覆盖原素材，空间前置已核查。

平板22个实际instrumentation均完整结束，其余23无设备调度。结束只读进程快照无VideoKit进程，结束服务快照无VideoKit服务；当前没有在途设备方法。手机未启动C11方法，结束仍禁用且无VideoKit进程。未卸载、清数据、恢复旧版本或修改启用状态；保留包、缓存和证据。最终空进程与历史失败账本分栏，不写为CPU释放门禁PASS。

## 架构、许可与剩余门禁

正式Flutter宿主＋独立Kit/AAR、Media3薄适配方向保持；同APK Debug harness不是正式Kit完成。FFmpeg官方8.0.3及已审H263传递编译/输入拒绝继承，自有实现限AVIO/JNI、协议、资源/代次与取证胶水；无新模型、crash handler或protobuf runtime。许可来源、配置、NOTICE/SBOM/完整对应源及266对象/608依赖证据继承核验；五个上游/allocator库不变。526项本机断言不等于Android并发/退出证明，Debug准入不等于SDK/商店/外发或专利批准。

C11-T01/T02修复及正常解码前置、真实代次/额外端点/全局预算、trace采集、手机覆盖仍待完整后续候选；16KiB页设备、完整产品/Kit/多宿主、系统显示/编码/宿主JNI、全P0与发行条件仍未闭合。C10和更早FAIL/UNKNOWN不回写。用户此前声音/字幕反馈仅属于对应旧候选，本轮不新增人工效果结论。本批结束后等待统一安排，不追加设备方法，不降低signal0门槛。
